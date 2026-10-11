# Architecture

## Decision: one monorepo, incremental runtime complexity
The web, API, worker, infrastructure, and documentation share a repository to keep contracts and delivery changes reviewable together. They remain independent deployment units. Next.js/TypeScript supports a maintainable frontend; Tailwind supplies styling. FastAPI offers typed request validation and OpenAPI when a backend is justified. PostgreSQL is the planned transactional store. Go is reserved for durable asynchronous processing where concurrency and operational reliability become useful.

## Phase 1: hosted scheduling
```text
Customer -> Next.js website -> Cal.com event page -> calendar/confirmation
                         (no custom backend or database)
```
The implemented CTA is a normal link, which avoids loading third-party embed scripts and works without client-side JavaScript. Cal.com owns availability, conflict checks, timezone selection, booking, rescheduling, and cancellation. Confirmation on the scheduling provider is authoritative; a website click does not mean a booking completed. Payments, if required and supported by the selected Cal.com plan, are configured there rather than handled by this scaffold.

## Phase 2: reliable booking ingestion (planned)
```text
Cal.com -> HTTPS webhook -> FastAPI -> PostgreSQL transaction
Admin -> authenticated API -> aggregate reporting
```
Cal.com remains the scheduling source of truth. Verify webhook signatures over raw bytes before parsing, validate payloads, enforce a body-size limit, and persist deduplicated events durably before acknowledging success. Use a unique event key or stable provider identifier plus event type/version; define ordering and reschedule/cancellation semantics from actual provider payloads. Reconciliation against the provider handles missing/out-of-order delivery. Keep a minimum booking projection, event receipt metadata, and audited admin access. Add migrations and least-privilege DB roles. Do not store reading content or unnecessary sensitive intake answers.

An admin interface and auth are not scaffolded. Select an identity provider; enforce authorization on every admin route. AI business summaries, if approved, receive aggregate/de-identified metrics only, use deterministic analytics as the source of truth, carry confidence/limitations, and have strict token/spending limits. No model provider is selected or called here.

## Phase 3: durable processing (planned)
```text
Webhook transaction -> booking projection + transactional outbox
Outbox relay -> durable queue -> Go workers -> reporting/integrations
                       failed jobs -> dead-letter queue -> operator
```
Use the outbox pattern to avoid losing jobs between DB commit and queue publication. Delivery is at least once; consumers must be idempotent. Bound concurrency, implement exponential backoff with jitter, cap retries, distinguish permanent failures, and provide dead-letter replay tooling. Choose a queue based on measured volume, hosting, operating cost, and team familiarity; no queue vendor is committed yet. Consider PostgreSQL-backed jobs before adding another managed service.

## Boundaries and tradeoffs
The web has only a public scheduling URL, never database or API credentials. Server-only secrets stay with API/worker deployments. Phase 1 avoids distributed operations but depends on the scheduling provider. Later phases add reporting control and recoverability at the cost of databases, migrations, backups, auth, monitoring, and on-call responsibility. Do not deploy architecture solely to demonstrate technology; use phase acceptance gates in the roadmap.
