# Validation

Local checks on 2026-10-11:
- Website: ESLint, TypeScript, and production build passed. Admin login, overview, bookings, jobs, optional AI disabled state, and logout were checked through the browser against a local API/database.
- API: Ruff lint/format and ten tests passed, including real PostgreSQL integration tests for authentication, origin protection, expiration, rate limits, webhook signatures/body limits/event allowlist, deduplication, event ordering/reschedule tombstones, and job controls.
- Worker: five Go tests passed with the race detector, including real PostgreSQL lease recovery/stale completion and exhausted retries, plus mock model adapter tests; go vet passed.
- End-to-end: an actual signed HTTP webhook was persisted to a temporary PostgreSQL database, consumed by the running Go worker, and produced a persisted metrics snapshot visible in the dashboard. Test data was isolated and is not client booking history.
- Production-only npm audit previously reported zero vulnerabilities; the development dependency advisory is documented in SECURITY.md.

Docker is unavailable on this computer. Container images and the complete Compose/HTTPS stack have **not** been built/run locally. PostgreSQL integration checks used a temporary PostgreSQL 18 instance; deployment selects PostgreSQL 17 and still needs server acceptance testing. Optional AI was tested with a mock response, not a downloaded/live model.

No production database/API/worker, model, admin account, backup destination, or webhook is provisioned. No real appointment/payment was created as part of these checks. GitHub-hosted CI must be checked separately; validation reported here was run locally. Validate the stack, restore procedure, provider webhook payloads, and an approved test booking on the target server before relying on it.
