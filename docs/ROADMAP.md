# Rollout status

## Implemented and locally verified
- Editorial booking website with inline Cal.com scheduling.
- PostgreSQL schema/versioned migration runner and restricted service roles.
- Signed, allowlisted webhook intake with transactional receipt/booking/job storage.
- Password-protected admin dashboard, session/logout, CSRF Origin checks, and sign-in attempt limits.
- Aggregate booking reports, recent minimal records, job monitoring/retry.
- Go durable jobs, lease recovery, concurrency bounds, retries and failure state.
- Optional Ollama summaries (disabled by default; adapter tested with a controlled mock).
- Docker services and HTTPS production configuration.

## Deployment/configuration still required
- Install Docker on the selected server, set DNS, real secrets/event IDs, run migrations, and provision an admin account.
- Configure Cal.com webhooks and verify a real approved booking lifecycle.
- Connect the frontend API_BASE_URL or use the included server-hosted frontend.
- Choose/pull an Ollama model and verify model execution if AI is wanted.
- Build/scan/pin production container images, configure backups/restore drills and monitoring.

## Later improvements
Provider reconciliation/historical import, MFA and account recovery, explicit retention tooling, richer period/cohort analytics, payment/revenue reconciliation from verified payment data, and measured-load tuning. These are not claimed as implemented.

Client content, actual service configuration, cancellation/privacy policies, custom domain selection, and full booking verification remain separate client launch tasks.
