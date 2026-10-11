# Docker deployment

## What is prepared
A PostgreSQL database, one-shot schema migration service, FastAPI service, Go worker, optional Ollama service, standalone Next.js server, and Caddy HTTPS gateway. Only Caddy exposes production ports. Separate application/worker database roles have no schema or role management privileges. Fresh database initialization creates roles, and migration grants the relevant table access.

Docker and a server are not installed/provisioned by this change. Use Docker Engine with Compose 2.24+ (the production override uses `!reset`). Allocate server resources to the expected load; model serving can require considerably more memory/CPU or GPU than the booking services.

## Initial production setup
1. Clone the repository to a server and point a domain's DNS to it. Permit inbound TCP 80/443 for HTTPS; SSH access should be restricted. Do not expose PostgreSQL or the API directly.
2. Copy `.env.example` to `.env` and restrict permissions with `chmod 600 .env`. Generate three **distinct** database passwords using `openssl rand -hex 32` for `DATABASE_PASSWORD` (migration/admin database owner), `APP_DATABASE_PASSWORD`, and `WORKER_DATABASE_PASSWORD`. Generate another distinct value for `CAL_WEBHOOK_SECRET` (minimum 32 characters). Never commit/share these values.
3. Set `SITE_DOMAIN` to the server domain, `APP_ORIGIN=https://<SITE_DOMAIN>`, and `CAL_EVENT_TYPE_IDS` to the actual numeric event type IDs from Cal.com. Leave AI disabled initially.
4. Start the stack:
```sh
docker compose -f docker-compose.yml -f docker-compose.production.yml up --build -d
```
5. Create the first account with a securely prompted password:
```sh
docker compose -f docker-compose.yml -f docker-compose.production.yml run --rm migrate python -m app.manage create-admin --username owner
```
6. Open `https://<SITE_DOMAIN>/admin`. Verify login/logout, HTTPS-only cookies, initial empty data, and failed anonymous requests. No default account exists. Review the compiled website and Cal.com flow before replacing the public domain.
7. Configure Cal.com webhook intake and run an approved test booking. Check that the record and worker snapshot appear. Do not assume previously made appointments are automatically imported.

The server-hosted website proxies admin traffic to the internal API. If keeping **Vercel as the frontend**, configure a separate protected HTTPS API ingress with `/v1/admin/*` reachable by Vercel, set API `APP_ORIGIN=https://insight-alumina.vercel.app`, and add server-only `API_BASE_URL=https://<api-host>` in Vercel. The provided Caddy configuration intentionally exposes only web routes and webhook intake; it must be explicitly adapted for that split deployment. Deploying the frontend alone does not provision database/API/worker services.

## Cal.com
Set subscriber URL `https://<SITE_DOMAIN>/v1/webhooks/cal`, the same secret as the API, and enable BOOKING_CREATED, BOOKING_RESCHEDULED, BOOKING_CANCELLED, BOOKING_REQUESTED, and BOOKING_REJECTED. Standard payloads with version `2021-10-20` or `2026-07-27` are supported. Custom payloads and seated events need separate validation before use. The API validates event IDs and acknowledges only committed events. It stores a minimal booking projection and queues analytics atomically.

## Optional AI with Ollama
Choose a model suitable for the server and its license; model weights are not included. Set `OLLAMA_MODEL` to that model, enable `AI_ANALYTICS_ENABLED=true`, start the AI profile, and explicitly pull the selected weights:
```sh
docker compose -f docker-compose.yml -f docker-compose.production.yml --profile ai up --build -d
docker compose exec ollama ollama pull <model>
```
Recreate API/worker after environment changes. Ollama remains internal, with no public port. Request a summary from Admin → Insights; refresh after the worker finishes. Each request uses only aggregate numeric counts, nonstreaming mode, a maximum 220 generated tokens, a 60-second HTTP timeout, and one new job per UTC day. A failed attempt can retry up to five times, and operator retry can cause additional inference. Use infrastructure spending/resource controls too; daily job deduplication is not a billing guarantee. Model availability was not live-tested during implementation.

## Backups and restore
Back up the database to an encrypted, access-controlled off-server destination. Example database dump (do not commit backups):
```sh
docker compose exec -T db pg_dump -U insight -d insight -Fc > insight-backup.dump
```
Restore into a separate empty database and validate records, admin access, migrations, and queue state before relying on backups:
```sh
cat insight-backup.dump | docker compose exec -T db pg_restore -U insight -d <empty-restore-database> --no-owner
```
Establish retention with the client; delete expired sessions routinely, and define a retention period for receipt/audit/booking history. Volume persistence is not a backup. Changing password environment variables on an existing PostgreSQL volume does not rotate database roles; explicitly alter role passwords, update service secrets, and recreate affected services.

## Operations and rollback
`/healthz` is liveness; `/readyz` checks database/schema availability. Inspect redacted worker logs and Admin → Jobs. Jobs that exhaust five attempts appear failed; correct the cause before retry. Shutdown stops new claims and gives active jobs up to 80 seconds to complete; Compose allows 90 seconds. Expired leases recover on another worker.

Use immutable reviewed images/digests for production releases. Source image tags in this preparation are mutable and need your release pinning/scanning process. Back up before schema changes. Migration files are versioned and transactional; never rewrite an already-applied migration. Restore the previous application image for rollback only when schema remains compatible. Monitor failed/pending jobs, database capacity, backup failures, API errors, sign-in denial, and server/model resource use.
