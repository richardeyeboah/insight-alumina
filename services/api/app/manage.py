import argparse
import getpass
from pathlib import Path

from argon2 import PasswordHasher
from psycopg import sql

from app.db import database


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["migrate", "create-admin"])
    parser.add_argument("--username")
    args = parser.parse_args()
    with database() as db:
        if args.command == "migrate":
            db.execute("SELECT pg_advisory_xact_lock(617204)")
            db.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations (version text PRIMARY KEY, applied_at timestamptz DEFAULT now())"
            )
            for file in sorted(
                (Path(__file__).parent.parent / "migrations").glob("*.sql")
            ):
                if not db.execute(
                    "SELECT 1 FROM schema_migrations WHERE version=%s", (file.name,)
                ).fetchone():
                    db.execute(file.read_text())
                    db.execute(
                        "INSERT INTO schema_migrations(version) VALUES (%s)",
                        (file.name,),
                    )
            # Application roles cannot create/drop schema objects or manage users.
            roles = {
                "insight_api": [
                    "admin_users",
                    "admin_sessions",
                    "login_attempts",
                    "webhook_receipts",
                    "bookings",
                    "jobs",
                    "audit_log",
                ],
                "insight_worker": ["jobs", "metric_snapshots", "ai_summaries"],
            }
            for role, tables in roles.items():
                if db.execute(
                    "SELECT 1 FROM pg_roles WHERE rolname=%s", (role,)
                ).fetchone():
                    db.execute(
                        sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(
                            sql.Identifier(role)
                        )
                    )
                    for table in tables:
                        db.execute(
                            sql.SQL(
                                "GRANT SELECT,INSERT,UPDATE,DELETE ON {} TO {}"
                            ).format(sql.Identifier(table), sql.Identifier(role))
                        )
                    for table in (
                        ["metric_snapshots", "ai_summaries", "schema_migrations"]
                        if role == "insight_api"
                        else ["bookings", "schema_migrations"]
                    ):
                        db.execute(
                            sql.SQL("GRANT SELECT ON {} TO {}").format(
                                sql.Identifier(table), sql.Identifier(role)
                            )
                        )
                    db.execute(
                        sql.SQL(
                            "GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO {}"
                        ).format(sql.Identifier(role))
                    )
            print("Migrations applied")
        else:
            if not args.username or len(args.username) > 100:
                parser.error("--username is required (maximum 100 characters)")
            password = getpass.getpass("New admin password (at least 16 characters): ")
            if len(password) < 16 or password != getpass.getpass("Confirm password: "):
                parser.error("Password must match and contain at least 16 characters")
            db.execute(
                "INSERT INTO admin_users(username,password_hash) VALUES (%s,%s)",
                (args.username, PasswordHasher().hash(password)),
            )
            print("Admin created")


if __name__ == "__main__":
    main()
