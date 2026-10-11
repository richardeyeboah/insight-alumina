from fastapi.testclient import TestClient

from app.main import app


def test_health_contract():
    response = TestClient(app).get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api"}


def test_webhook_fails_closed_without_configuration():
    assert TestClient(app).post("/v1/webhooks/cal", json={}).status_code == 503
