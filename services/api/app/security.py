import hashlib
import os
import secrets
from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from fastapi import HTTPException, Request

from app.db import database

hasher = PasswordHasher()
dummy_hash = hasher.hash(secrets.token_urlsafe(32))
COOKIE = "ia_admin_session"


def check_origin(request: Request):
    allowed = os.environ.get("APP_ORIGIN", "http://localhost:3000").rstrip("/")
    if request.headers.get("origin", "").rstrip("/") != allowed:
        raise HTTPException(403, "Request origin is not allowed")


def current_admin(request: Request) -> str:
    token = request.cookies.get(COOKIE, "")
    if len(token) < 32 or len(token) > 128:
        raise HTTPException(401, "Sign in required")
    digest = hashlib.sha256(token.encode()).hexdigest()
    with database() as db:
        session = db.execute(
            "SELECT username FROM admin_sessions WHERE token_hash=%s AND expires_at>now()",
            (digest,),
        ).fetchone()
    if not session:
        raise HTTPException(401, "Session expired")
    return session["username"]


def login(username: str, password: str) -> str:
    with database() as db:
        # Serialize this small login budget to avoid a race between concurrent attempts.
        db.execute("SELECT pg_advisory_xact_lock(617205)")
        db.execute(
            "DELETE FROM login_attempts WHERE attempted_at < now() - interval '15 minutes'"
        )
        count = db.execute("SELECT count(*) AS n FROM login_attempts").fetchone()["n"]
        if count >= 10:
            raise HTTPException(
                429, "Too many sign-in attempts; try again in 15 minutes"
            )
        db.execute("INSERT INTO login_attempts DEFAULT VALUES")
        user = db.execute(
            "SELECT password_hash FROM admin_users WHERE username=%s", (username,)
        ).fetchone()
        valid = False
        try:
            valid = (
                hasher.verify(user["password_hash"] if user else dummy_hash, password)
                and user is not None
            )
        except VerificationError:
            pass
        if not valid:
            # Commit failed attempt before returning an error.
            db.commit()
            raise HTTPException(401, "Invalid sign-in details")
        token = secrets.token_urlsafe(32)
        db.execute("DELETE FROM admin_sessions WHERE expires_at <= now()")
        db.execute(
            "INSERT INTO admin_sessions(token_hash,username,expires_at) VALUES (%s,%s,%s)",
            (
                hashlib.sha256(token.encode()).hexdigest(),
                username,
                datetime.now(UTC) + timedelta(hours=8),
            ),
        )
        db.execute(
            "INSERT INTO audit_log(username,action) VALUES (%s,'login')", (username,)
        )
        return token
