import hashlib
import hmac
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.db import database
from app.main import app
from app.security import COOKIE, hasher

pytestmark = pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="Set TEST_DATABASE_URL to an isolated PostgreSQL database",
)


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", os.environ.get("TEST_DATABASE_URL", ""))
    monkeypatch.setenv("CAL_WEBHOOK_SECRET", "test-secret-only-" * 3)
    monkeypatch.setenv("CAL_EVENT_TYPE_IDS", "123")
    monkeypatch.setenv("APP_ORIGIN", "http://localhost:3000")
    monkeypatch.setenv("AI_ANALYTICS_ENABLED", "false")
    with database() as db:
        db.execute(
            "DROP TABLE IF EXISTS admin_sessions,admin_users,login_attempts,webhook_receipts,bookings,ai_summaries,jobs,metric_snapshots,audit_log CASCADE"
        )
        db.execute(
            (Path(__file__).parent.parent / "migrations/001_initial.sql").read_text()
        )
        db.execute(
            "TRUNCATE admin_sessions,admin_users,login_attempts,webhook_receipts,bookings,ai_summaries,jobs,metric_snapshots,audit_log RESTART IDENTITY CASCADE"
        )
        db.execute(
            "INSERT INTO admin_users(username,password_hash) VALUES ('owner',%s)",
            (hasher.hash("test-only-password-long"),),
        )


def event(kind="BOOKING_CREATED", uid="test-booking", at="2026-10-11T12:00:00Z"):
    return {
        "triggerEvent": kind,
        "createdAt": at,
        "payload": {
            "uid": uid,
            "eventTypeId": 123,
            "startTime": "2026-10-20T12:00:00Z",
            "endTime": "2026-10-20T12:30:00Z",
            "attendees": [{"name": "PRIVATE", "email": "private@example.com"}],
            "additionalNotes": "PRIVATE READING",
        },
    }


def send(client, body):
    raw = json.dumps(body).encode()
    signature = hmac.new(
        os.environ["CAL_WEBHOOK_SECRET"].encode(), raw, hashlib.sha256
    ).hexdigest()
    return client.post(
        "/v1/webhooks/cal", content=raw, headers={"x-cal-signature-256": signature}
    )


def sign_in(client):
    return client.post(
        "/v1/admin/login",
        json={"username": "owner", "password": "test-only-password-long"},
        headers={"origin": "http://localhost:3000"},
    )


def test_signature_deduplication_and_minimal_storage():
    with TestClient(app) as client:
        assert client.post("/v1/webhooks/cal", json=event()).status_code == 401
        assert send(client, event()).status_code == 204
        assert send(client, event()).status_code == 204
    with database() as db:
        assert (
            db.execute("SELECT count(*) AS n FROM webhook_receipts").fetchone()["n"]
            == 1
        )
        assert db.execute("SELECT count(*) AS n FROM jobs").fetchone()["n"] == 1
        assert "PRIVATE" not in str(db.execute("SELECT * FROM bookings").fetchall())


def test_out_of_order_and_reschedule():
    with TestClient(app) as client:
        assert (
            send(
                client, event("BOOKING_CANCELLED", at="2026-10-11T14:00:00Z")
            ).status_code
            == 204
        )
        assert send(client, event()).status_code == 204
        with database() as db:
            assert (
                db.execute("SELECT status FROM bookings").fetchone()["status"]
                == "cancelled"
            )
        body = event("BOOKING_RESCHEDULED", "replacement", "2026-10-11T15:00:00Z")
        body["payload"]["rescheduleUid"] = "test-booking"
        assert send(client, body).status_code == 204
    with database() as db:
        assert (
            db.execute(
                "SELECT status FROM bookings WHERE uid='replacement'"
            ).fetchone()["status"]
            == "accepted"
        )


def test_reschedule_before_original_creation_keeps_original_retired():
    with TestClient(app) as client:
        body = event("BOOKING_RESCHEDULED", "replacement", "2026-10-11T15:00:00Z")
        body["payload"]["rescheduleUid"] = "original"
        assert send(client, body).status_code == 204
        assert send(client, event(uid="original")).status_code == 204
        assert sign_in(client).status_code == 200
        assert client.get("/v1/admin/metrics").json()["totals"]["total"] == 1
    with database() as db:
        assert (
            db.execute("SELECT status FROM bookings WHERE uid='original'").fetchone()[
                "status"
            ]
            == "rescheduled"
        )


def test_event_allowlist_and_body_limits():
    with TestClient(app) as client:
        body = event()
        body["payload"]["eventTypeId"] = 999
        assert send(client, body).status_code == 403
        assert client.post("/v1/webhooks/cal", content=b"x" * 65537).status_code == 413


def test_admin_auth_csrf_logout_and_expiration():
    with TestClient(app) as client:
        assert client.get("/v1/admin/metrics").status_code == 401
        assert (
            client.post(
                "/v1/admin/login",
                json={"username": "owner", "password": "test-only-password-long"},
            ).status_code
            == 403
        )
        response = sign_in(client)
        assert response.status_code == 200
        assert (
            "HttpOnly" in response.headers["set-cookie"]
            and "SameSite=strict" in response.headers["set-cookie"]
        )
        assert client.get("/v1/admin/metrics").status_code == 200
        assert (
            client.post(
                "/v1/admin/logout", headers={"origin": "https://evil.example"}
            ).status_code
            == 403
        )
        assert (
            client.post(
                "/v1/admin/logout", headers={"origin": "http://localhost:3000"}
            ).status_code
            == 200
        )
        assert client.get("/v1/admin/session").status_code == 401
        sign_in(client)
        with database() as db:
            db.execute("UPDATE admin_sessions SET expires_at=now()-interval '1 second'")
        assert client.get("/v1/admin/session").status_code == 401


def test_login_rate_limit_and_invalid_credentials():
    with TestClient(app) as client:
        for _ in range(10):
            assert (
                client.post(
                    "/v1/admin/login",
                    json={"username": "owner", "password": "incorrect"},
                    headers={"origin": "http://localhost:3000"},
                ).status_code
                == 401
            )
        assert sign_in(client).status_code == 429


def test_summary_opt_in_daily_deduplication_and_failed_retry(monkeypatch):
    with TestClient(app) as client:
        assert sign_in(client).status_code == 200
        headers = {"origin": "http://localhost:3000"}
        assert client.post("/v1/admin/summary", headers=headers).status_code == 409
        monkeypatch.setenv("AI_ANALYTICS_ENABLED", "true")
        first = client.post("/v1/admin/summary", headers=headers)
        second = client.post("/v1/admin/summary", headers=headers)
        assert first.status_code == 202 and first.json()["id"] == second.json()["id"]
        job_id = first.json()["id"]
        assert (
            client.post(f"/v1/admin/jobs/{job_id}/retry", headers=headers).status_code
            == 409
        )
        with database() as db:
            db.execute(
                "UPDATE jobs SET state='failed',attempts=5 WHERE id=%s", (job_id,)
            )
        assert (
            client.post(f"/v1/admin/jobs/{job_id}/retry", headers=headers).status_code
            == 200
        )


def test_production_cookie(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    with TestClient(app) as client:
        response = sign_in(client)
        assert "Secure" in response.headers["set-cookie"]
        assert COOKIE in response.headers["set-cookie"]
