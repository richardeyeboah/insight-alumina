import hashlib
import hmac
import json
import os
import re
from datetime import UTC, datetime
from typing import Literal

import psycopg
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from app.db import database
from app.security import COOKIE, check_origin, current_admin, login

app = FastAPI(
    title="Insight Alumina API",
    version="0.2.0",
    docs_url=None if os.getenv("APP_ENV") == "production" else "/docs",
    redoc_url=None if os.getenv("APP_ENV") == "production" else "/redoc",
    openapi_url=None if os.getenv("APP_ENV") == "production" else "/openapi.json",
)


@app.exception_handler(psycopg.Error)
def database_error(request: Request, error: Exception):
    return JSONResponse(
        status_code=503, content={"detail": "Database temporarily unavailable"}
    )


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/healthz")
def health():
    return {"status": "ok", "service": "api"}


@app.get("/readyz")
def ready():
    with database() as db:
        db.execute("SELECT 1 FROM schema_migrations LIMIT 1")
    return {"status": "ready"}


class Credentials(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=1024)


@app.post("/v1/admin/login", dependencies=[Depends(check_origin)])
def sign_in(body: Credentials, response: Response):
    token = login(body.username, body.password)
    response.set_cookie(
        COOKIE,
        token,
        max_age=8 * 3600,
        httponly=True,
        secure=os.getenv("APP_ENV") == "production",
        samesite="strict",
        path="/",
    )
    return {"ok": True}


@app.get("/v1/admin/session")
def session(username: str = Depends(current_admin)):
    return {
        "username": username,
        "ai_enabled": os.getenv("AI_ANALYTICS_ENABLED", "false").lower() == "true",
    }


@app.post("/v1/admin/logout", dependencies=[Depends(check_origin)])
def logout(
    request: Request, response: Response, username: str = Depends(current_admin)
):
    with database() as db:
        db.execute(
            "DELETE FROM admin_sessions WHERE token_hash=%s",
            (hashlib.sha256(request.cookies[COOKIE].encode()).hexdigest(),),
        )
        db.execute(
            "INSERT INTO audit_log(username,action) VALUES (%s,'logout')", (username,)
        )
    response.delete_cookie(
        COOKIE,
        path="/",
        secure=os.getenv("APP_ENV") == "production",
        httponly=True,
        samesite="strict",
    )
    return {"ok": True}


@app.get("/v1/admin/metrics")
def metrics(username: str = Depends(current_admin)):
    with database() as db:
        totals = db.execute(
            "SELECT count(*) FILTER(WHERE status!='rescheduled') AS total, count(*) FILTER(WHERE status='accepted') AS active, count(*) FILTER(WHERE status='cancelled') AS cancelled, count(*) FILTER(WHERE status='requested') AS requested, count(*) FILTER(WHERE status='accepted' AND starts_at>=now()) AS upcoming FROM bookings"
        ).fetchone()
        daily = db.execute(
            "SELECT starts_at::date::text AS day, count(*) AS bookings FROM bookings WHERE status!='rescheduled' AND starts_at>=now()-interval '30 days' AND starts_at<now() GROUP BY 1 ORDER BY 1"
        ).fetchall()
        worker = db.execute(
            "SELECT state,count(*) AS count FROM jobs GROUP BY state"
        ).fetchall()
        last = db.execute(
            "SELECT day,metrics,updated_at FROM metric_snapshots ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()
        return {
            "totals": totals,
            "daily": daily,
            "jobs": worker,
            "last_snapshot": last,
            "timezone": "UTC",
            "source": "Verified webhook events received by this system; not a full historical Cal.com import",
        }


@app.get("/v1/admin/bookings")
def bookings(username: str = Depends(current_admin)):
    with database() as db:
        return {
            "bookings": db.execute(
                "SELECT uid,event_type_id,starts_at,ends_at,status FROM bookings ORDER BY starts_at DESC LIMIT 100"
            ).fetchall()
        }


@app.get("/v1/admin/jobs")
def jobs(username: str = Depends(current_admin)):
    with database() as db:
        return {
            "jobs": db.execute(
                "SELECT id,kind,state,attempts,last_error,created_at,finished_at FROM jobs ORDER BY id DESC LIMIT 50"
            ).fetchall()
        }


@app.post("/v1/admin/jobs/{job_id}/retry", dependencies=[Depends(check_origin)])
def retry(job_id: int, username: str = Depends(current_admin)):
    with database() as db:
        row = db.execute(
            "UPDATE jobs SET state='pending',attempts=0,available_at=now(),lease_token=NULL,locked_until=NULL,last_error=NULL WHERE id=%s AND state='failed' RETURNING id",
            (job_id,),
        ).fetchone()
        if not row:
            raise HTTPException(409, "Only failed jobs can be retried")
        db.execute(
            "INSERT INTO audit_log(username,action,subject) VALUES (%s,'retry_job',%s)",
            (username, str(job_id)),
        )
    return {"ok": True}


@app.post("/v1/admin/summary", status_code=202, dependencies=[Depends(check_origin)])
def request_summary(username: str = Depends(current_admin)):
    if os.getenv("AI_ANALYTICS_ENABLED", "false").lower() != "true":
        raise HTTPException(409, "Optional AI is disabled")
    # One job per UTC day. Repeated clicks do not create additional model calls.
    key = "ai:" + datetime.now(UTC).date().isoformat()
    with database() as db:
        row = db.execute(
            "INSERT INTO jobs(job_key,kind) VALUES (%s,'ai_summary') ON CONFLICT(job_key) DO UPDATE SET job_key=excluded.job_key RETURNING id,state",
            (key,),
        ).fetchone()
        db.execute(
            "INSERT INTO audit_log(username,action,subject) VALUES (%s,'request_summary',%s)",
            (username, str(row["id"])),
        )
    return row


@app.get("/v1/admin/summary")
def summary(username: str = Depends(current_admin)):
    with database() as db:
        return {
            "summary": db.execute(
                "SELECT summary,model,created_at FROM ai_summaries ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
        }


class BookingPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")
    uid: str = Field(min_length=1, max_length=200)
    eventTypeId: int = Field(ge=1)
    startTime: datetime
    endTime: datetime
    rescheduleUid: str | None = Field(default=None, max_length=200)
    status: str | None = None

    @model_validator(mode="after")
    def valid_times(self):
        if (
            self.startTime.tzinfo is None
            or self.endTime.tzinfo is None
            or self.endTime <= self.startTime
        ):
            raise ValueError("Timezone-aware start/end are required")
        return self


class BookingEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    triggerEvent: Literal[
        "BOOKING_CREATED",
        "BOOKING_RESCHEDULED",
        "BOOKING_CANCELLED",
        "BOOKING_REQUESTED",
        "BOOKING_REJECTED",
    ]
    createdAt: datetime
    payload: BookingPayload

    @model_validator(mode="after")
    def aware(self):
        if self.createdAt.tzinfo is None:
            raise ValueError("Timezone-aware event time required")
        return self


@app.post("/v1/webhooks/cal", status_code=204)
async def webhook(request: Request):
    secret = os.getenv("CAL_WEBHOOK_SECRET", "")
    allowed = {
        int(x.strip())
        for x in os.getenv("CAL_EVENT_TYPE_IDS", "").split(",")
        if x.strip().isdigit()
    }
    if len(secret) < 32 or not allowed:
        raise HTTPException(503, "Webhook configuration is incomplete")
    raw = bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw) > 65536:
            raise HTTPException(413, "Payload too large")
    signature = request.headers.get("x-cal-signature-256", "")
    expected = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    if not re.fullmatch(r"[a-fA-F0-9]{64}", signature) or not hmac.compare_digest(
        signature.lower(), expected
    ):
        raise HTTPException(401, "Invalid webhook signature")
    version = request.headers.get("x-cal-webhook-version", "2021-10-20")
    if version not in {"2021-10-20", "2026-07-27"}:
        raise HTTPException(400, "Unsupported webhook version")
    try:
        event = BookingEvent.model_validate_json(raw)
    except ValidationError:
        raise HTTPException(400, "Invalid booking event") from None
    p = event.payload
    if p.eventTypeId not in allowed:
        raise HTTPException(403, "Event type not permitted")
    # Hash normalized minimal event data. Raw attendee details never reach the DB/logs.
    identity = json.dumps(
        {
            "event": event.triggerEvent,
            "created": event.createdAt.isoformat(),
            "uid": p.uid,
            "start": p.startTime.isoformat(),
            "end": p.endTime.isoformat(),
            "previous": p.rescheduleUid,
        },
        sort_keys=True,
    )
    digest = hashlib.sha256(identity.encode()).hexdigest()
    status = {
        "BOOKING_CANCELLED": "cancelled",
        "BOOKING_REJECTED": "rejected",
        "BOOKING_REQUESTED": "requested",
    }.get(event.triggerEvent, "requested" if p.status == "PENDING" else "accepted")
    with database() as db:
        inserted = db.execute(
            "INSERT INTO webhook_receipts(event_hash,trigger_event,booking_uid,occurred_at) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING event_hash",
            (digest, event.triggerEvent, p.uid, event.createdAt),
        ).fetchone()
        if not inserted:
            return Response(status_code=204)
        # Cancellation wins ties. Older events cannot overwrite newer booking state.
        db.execute(
            """INSERT INTO bookings(uid,event_type_id,starts_at,ends_at,status,event_at) VALUES (%s,%s,%s,%s,%s,%s)
        ON CONFLICT(uid) DO UPDATE SET event_type_id=excluded.event_type_id,starts_at=excluded.starts_at,ends_at=excluded.ends_at,status=excluded.status,event_at=excluded.event_at,updated_at=now()
        WHERE excluded.event_at>bookings.event_at OR (excluded.event_at=bookings.event_at AND excluded.status='cancelled')""",
            (p.uid, p.eventTypeId, p.startTime, p.endTime, status, event.createdAt),
        )
        if (
            event.triggerEvent == "BOOKING_RESCHEDULED"
            and p.rescheduleUid
            and p.rescheduleUid != p.uid
        ):
            db.execute(
                """INSERT INTO bookings(uid,event_type_id,starts_at,ends_at,status,event_at) VALUES (%s,%s,%s,%s,'rescheduled',%s) ON CONFLICT(uid) DO UPDATE SET status='rescheduled',event_at=excluded.event_at,updated_at=now() WHERE bookings.event_at<=excluded.event_at""",
                (
                    p.rescheduleUid,
                    p.eventTypeId,
                    p.startTime,
                    p.endTime,
                    event.createdAt,
                ),
            )
        db.execute(
            "INSERT INTO jobs(job_key,kind) VALUES (%s,'refresh_metrics') ON CONFLICT DO NOTHING",
            ("event:" + digest,),
        )
    return Response(status_code=204)
