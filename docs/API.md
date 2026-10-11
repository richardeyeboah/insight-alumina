# API contracts

## Operations
GET /healthz: liveness. GET /readyz: database/schema check. Docs/OpenAPI are disabled with APP_ENV=production.

## Administration
The Next.js `/api/admin/*` server proxy forwards approved routes to server-only API_BASE_URL; the browser never receives backend credentials. API paths:
- POST /v1/admin/login: username/password JSON; Argon2 verification, attempt budget, 8-hour HttpOnly SameSite=strict cookie (Secure in production).
- GET /v1/admin/session: authenticated username and AI availability.
- POST /v1/admin/logout: revoke current session.
- GET /v1/admin/metrics: current booking counts, recent daily appointment counts in UTC, job-state counts, latest worker snapshot, and source limitations.
- GET /v1/admin/bookings: latest 100 minimal records; no attendee details.
- GET /v1/admin/jobs: latest 50 job states/attempts and safe failure messages.
- POST /v1/admin/jobs/{id}/retry: failed jobs only; audited.
- POST /v1/admin/summary: opt-in only; one deduplicated job per UTC day; 202.
- GET /v1/admin/summary: latest generated summary with model and timestamp.

All reads except liveness require a valid server session. Admin POSTs require exact configured APP_ORIGIN. Login failures return generic 401; attempt budget returns 429; unavailable DB 503; disabled AI or invalid retry 409. The frontend proxy caps request bodies at 8 KiB and never caches responses.

## Cal.com webhook
POST /v1/webhooks/cal receives standard versioned BOOKING_CREATED/RESCHEDULED/CANCELLED/REQUESTED/REJECTED payloads. Requires configured event type allowlist and a >=32-character secret. Verifies x-cal-signature-256 HMAC-SHA256 against raw bytes using constant-time comparison before parsing. Payloads are limited to 64 KiB. Unknown versions/events/malformed times fail closed. Extra personal fields are ignored and not persisted.

Receipts, minimal booking state, and jobs commit in one transaction before 204. Normalized event identity deduplicates delivery; event timestamps prevent older events overwriting newer state, with cancellation winning equal timestamps. Reschedule supersedes the previous UID. Financial/payment status is not inferred. Cal.com remains authoritative; lost events or historic bookings require an explicit reconciliation/import procedure, which is not implemented here.

Reference: https://cal.com/docs/developing/guides/automation/webhooks
