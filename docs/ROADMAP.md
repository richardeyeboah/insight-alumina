# Roadmap

All boxes below represent future work; this repository is an initial scaffold.

## Phase 1 — low-cost functional booking website
- [ ] Client approves brand, copy, real services, durations, prices, cancellation/refund policy, contact route, and privacy notice.
- [ ] Configure client-owned Cal.com account, real event types, calendar conflict checking, timezone, buffers, booking limits, and conferencing/location.
- [ ] Set the actual booking URL; optionally add an accessible embed with a direct-link fallback after checking current official embed guidance.
- [ ] Review mobile/desktop layout, keyboard navigation, contrast, metadata, and page performance.
- [ ] Test actual availability, confirmation delivery, cancellation, rescheduling, timezone changes, and calendar conflicts; test payments if separately configured.
- [ ] Configure commercial hosting, custom domain/TLS, provider access, spending alerts, and rollback process.

Acceptance: customers can complete a test booking and receive accurate confirmation; the client can manage it in Cal.com; all published service terms and content are approved. No custom API, PostgreSQL, or Go deployment is needed.

## Phase 2 — backend, PostgreSQL, optional analytics
- [ ] Validate a reporting/admin need and obtain a running-cost budget.
- [ ] Choose managed PostgreSQL and identity provider; add migrations, roles, backup/restore drill, connection limits, and retention rules.
- [ ] Implement raw-body webhook verification, schema validation, deduplication, transactional persistence, reconciliation, and integration tests using real provider fixtures with personal data removed.
- [ ] Implement authenticated administration and aggregate booking/cancellation reporting with explicit access controls.
- [ ] Optional AI: approve provider/data use, aggregate or de-identify inputs, set a spend cap, label generated summaries, and validate against deterministic metrics.

Acceptance: forged/replayed events cannot mutate data incorrectly; retries and out-of-order events produce correct state; authorized admins can view reports; restore and deletion procedures work. AI is a separate opt-in milestone.

## Phase 3 — Go worker and systems engineering
- [ ] Implement transactional outbox and durable job storage/queue.
- [ ] Add idempotent handlers, bounded concurrency, graceful draining, timeouts, retries with jitter, dead-letter handling, and replay controls.
- [ ] Test duplicate delivery, crash recovery, queue outage, permanent failures, load, and shutdown during work.
- [ ] Add structured redacted logs, metrics, alerts, container scans, immutable releases, readiness checks, and staged deployment/rollback.

Acceptance: committed jobs survive failures, duplicate delivery is safe, concurrency is controlled, and operators can diagnose/replay failures. CI/CD should deploy only approved services and environments.

## Current deliverables
Starter Next.js page with configurable Cal.com link; FastAPI health endpoint and tests; idle Go process with graceful stop; optional Docker scaffolds; CI and dependency update configuration; project documentation. Nothing is marked as launched or business-complete.
