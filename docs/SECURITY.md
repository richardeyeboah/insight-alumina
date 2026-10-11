# Security and privacy

## Implemented controls
Administration uses Argon2 password hashes and opaque eight-hour sessions stored hashed in PostgreSQL. Cookies are HttpOnly/SameSite strict and Secure in production. Mutations require an exact configured Origin. A database-backed global sign-in budget limits attempts, and login/logout/job retry/AI requests are audited. There is no public registration or default admin password. The frontend proxies admin requests through its server; database credentials never enter browser bundles.

Webhook ingestion checks raw-body HMAC signatures before parsing, limits bodies, allowlists event type IDs, rejects unsupported payloads, and handles duplicates/out-of-order events transactionally. Stored bookings contain identifiers, times, and status only; attendee names, email addresses, reading notes, and raw payloads are discarded. Separate database roles restrict application and worker access. Production API documentation and access logs are disabled. Worker leases prevent stale workers committing results; failed jobs are visible and manually retryable.

Optional Ollama summaries receive aggregate numeric counts only and are disabled by default. Generated summaries may be inaccurate and require review. No payment or revenue reporting is inferred from bookings.

## Launch and ongoing operations
This repository is public. Never commit secrets, environment files, dumps, customer details, or reading notes. Use client-owned accounts, least-privilege access, MFA on hosting/GitHub, HTTPS, private database/model networking, reviewed image digests, dependency updates, and off-server encrypted backups. Test restoration before relying on backups. Rotate exposed credentials immediately.

Single-role administration is intended for trusted operators. Admin MFA, password recovery, automated Cal.com reconciliation, formal retention/deletion tooling, and historical import are not implemented. Set retention periods with the client and remove old receipt/audit/session records under that policy. A sign-in attempt budget can deny legitimate access during abuse; monitor it. Review the privacy notice, third-party booking disclosure, and cancellation terms with the client. Never collect card details in this app.

For incidents, contain access, rotate affected credentials, preserve redacted evidence, restore/reconcile provider state, and assess notification obligations with the client. Report vulnerabilities privately to the repository owner, without customer data or secrets.

## Initial dependency audit (2026-10-11)
The generated Next.js development lint toolchain includes the braces stack-exhaustion advisory GHSA-vfj7-8cjw-p6xm through micromatch/fast-glob. The registry’s latest braces version is 3.0.3 and remains affected. The full npm audit reports five high-severity entries in this development dependency chain; no patched braces release was available during setup. The production-only npm audit reported zero vulnerabilities during setup. Recheck and update the toolchain when a compatible fix is available; avoid untrusted glob patterns in development tooling. This repository does not claim a clean full dependency audit.
