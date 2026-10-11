# Security and privacy

## Current scaffold
No customer data is collected by the custom app; visitors who follow the booking link use Cal.com. No credentials are present in example files. The backend exposes only liveness and generated docs; the worker does no work. Public frontend variables must contain public configuration only. Dependency updates and CI are configured, but security scanning, branch protections, and production controls need configuration and verification.

## Launch controls
- This repository is public at the owner’s request. Publish only approved source/documentation; use least-privilege collaborators, MFA, and client-owned accounts.
- Never commit `.env` files, secrets, booking payloads, payment details, or reading notes. Rotate any exposed secret immediately rather than merely deleting the file.
- Use HTTPS and verify the real Cal.com destination. Confirm privacy notice and cancellation/refund terms with the client; minimize intake fields and avoid sensitive reading content.
- Protect previews, review accessibility, and patch dependencies. Review dependency and container scans before deployment. Pin CI actions to reviewed commit SHAs and images to digests before production hardening.
- Do not collect card details in this application. If payments are configured, use the scheduling/payment provider's supported hosted flow and reconcile paid/refunded status separately from booking existence.

## Phase 2/3 controls before enabling services
Authenticate admins with an identity provider; check roles on every route and audit sensitive actions. Enforce least-privilege database/queue credentials, secret management, signature verification before JSON parsing, body limits, idempotency, safe error handling, rate limits, and input validation. Browser CORS rules do not secure server-to-server endpoints. Logs should contain request/event identifiers, not raw payloads, tokens, or attendee details.

Define data inventory, access, retention, deletion/export, encryption, backups, and a tested restore process. Do not send identifiable booking data or reading content to an AI provider; use aggregate/de-identified metrics only after client approval and a provider/data-handling review. Optional AI remains disabled and unimplemented.

For an incident, revoke/rotate affected credentials, contain access, preserve redacted evidence, restore/reconcile provider state, assess affected records, and determine required notifications with the responsible client. Report vulnerabilities privately to the repository owner; do not include secrets or customer details in issues.

## Initial dependency audit (2026-10-11)
The generated Next.js development lint toolchain includes the braces stack-exhaustion advisory GHSA-vfj7-8cjw-p6xm through micromatch/fast-glob. The registry’s latest braces version is 3.0.3 and remains affected. The full npm audit reports five high-severity entries in this development dependency chain; no patched braces release was available during setup. The production-only npm audit reported zero vulnerabilities during setup. Recheck and update the toolchain when a compatible fix is available; avoid untrusted glob patterns in development tooling. This repository does not claim a clean full dependency audit.
