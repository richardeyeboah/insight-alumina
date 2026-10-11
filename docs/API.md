# API

## Implemented now
Run the API at `http://127.0.0.1:8000` using the service README. These are scaffold operations only:
- `GET /healthz` -> `200 application/json`: `{"status":"ok","service":"api"}`. Liveness only; no database/queue readiness is implied.
- `GET /docs` -> interactive Swagger UI.
- `GET /redoc` -> ReDoc documentation.
- `GET /openapi.json` -> generated OpenAPI schema.

No authentication is needed for liveness. There are no business endpoints, booking creation endpoints, database queries, webhook receivers, or AI calls. Do not expose future admin routes until authentication/authorization is implemented. Disable or protect interactive docs when business endpoints are introduced in production.

## Proposed phase 2 contract (not implemented)
`POST /v1/webhooks/cal`: provider-to-server only. Confirm event names, signature header/algorithm, retry semantics, and payload schemas using current Cal.com documentation before implementation. Verify the signature with the configured secret over exact raw body bytes and compare in constant time; never rely on browser redirects as proof of booking. Enforce HTTPS, payload size limits, schema checks, deduplication, and safe log redaction.

Target semantics: `204` only after durable transactional receipt, including harmless already-persisted duplicates; `400` invalid payload; `401` failed signature; `413` too large; `503` temporary persistence outage. Reconcile missing events with Cal.com. Specify the final deduplication/ordering strategy using actual fixtures before exposing this route.

`GET /v1/admin/metrics` (proposed): authenticated, authorized aggregate reporting. Define date/timezone filters, allowed roles, error structure, rate limits, and retention before implementation. No customer record listing is promised by the scaffold.

## External Cal.com API
Phase 1 uses a hosted booking URL and requires no API credentials. Future server-side integration should use API v2, selected authentication scopes, and required endpoint-specific version headers. Never expose Cal.com keys in `NEXT_PUBLIC_*`, browser code, commits, or logs. OAuth is recommended by Cal.com for integrations; decide the appropriate mechanism for the client-owned account before implementation.

Reference: [Cal.com API v2 introduction](https://cal.com/docs/api-reference/v2/introduction). API availability and privileges depend on provider/account configuration; recheck before phase 2.
