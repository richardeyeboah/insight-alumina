# FastAPI backend

Python 3.11+, PostgreSQL. Implements signed Cal.com intake, minimal booking persistence, admin login/session/logout, aggregate metrics, job inspection/retry, and optional AI summary scheduling.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
# Set DATABASE_URL to an isolated database before migrating.
python -m app.manage migrate
python -m app.manage create-admin --username owner
uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Set APP_ORIGIN, CAL_WEBHOOK_SECRET, CAL_EVENT_TYPE_IDS and DATABASE_URL. APP_ENV=production enforces Secure session cookies and disables API docs. Authentication uses Argon2 password hashes and eight-hour, opaque HttpOnly/SameSite cookies backed by hashed server sessions. State changes require exact Origin. Login attempts have a database-backed global 10-attempt/15-minute budget. There is no public account creation or default password.

`ruff check .`, `ruff format --check .`, `pytest -q`; set `TEST_DATABASE_URL` to an **isolated test database**, as integration tests drop/recreate application tables. Without it, integration tests explicitly skip. Migration needs database owner permissions; production services use separate restricted roles.

See docs/API.md and docs/DOCKER_DEPLOYMENT.md. No Cal.com historical import, payment/revenue reporting, MFA, role hierarchy, or external reconciliation scheduler is implemented. Cal.com remains the source of truth for appointment management.
