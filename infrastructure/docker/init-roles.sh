#!/bin/sh
set -eu
case "$APP_DATABASE_PASSWORD" in *[!a-fA-F0-9]*|"") echo "Use a hexadecimal APP_DATABASE_PASSWORD" >&2; exit 1;; esac
case "$WORKER_DATABASE_PASSWORD" in *[!a-fA-F0-9]*|"") echo "Use a hexadecimal WORKER_DATABASE_PASSWORD" >&2; exit 1;; esac
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --set=api_password="$APP_DATABASE_PASSWORD" --set=worker_password="$WORKER_DATABASE_PASSWORD" <<'SQL'
CREATE ROLE insight_api LOGIN PASSWORD :'api_password';
CREATE ROLE insight_worker LOGIN PASSWORD :'worker_password';
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
SQL
