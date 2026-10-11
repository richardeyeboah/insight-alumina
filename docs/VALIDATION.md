# Initial validation

Local checks on 2026-10-11:
- Website: ESLint, TypeScript, and production build passed.
- API: Ruff lint/format and two health/future-route tests passed.
- Worker: gofmt, go vet, go test (no tests yet), and compilation passed.
- Production-only npm audit: zero vulnerabilities. Full development audit has a documented advisory; see SECURITY.md.

Hosted CI results should be read from GitHub Actions after the scaffold commit. Docker images have not been built locally. No production hosting, Cal.com account, real booking, payment flow, database, or job queue has been tested or provisioned.
