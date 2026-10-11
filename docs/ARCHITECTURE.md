# Architecture

The monorepo has three independently runnable services. The public Next.js site embeds Cal.com; `/admin` and a same-origin server API proxy provide the private operations UI. FastAPI authenticates requests and owns PostgreSQL booking ingestion. Go consumes durable jobs from the same PostgreSQL database; no separate queue service is required.

```text
Visitor -> Next.js -> inline Cal.com scheduling
Cal.com -> signed HTTPS webhook -> FastAPI -> PostgreSQL transaction
                                            receipts + bookings + jobs
Admin -> HttpOnly server session -> Next.js proxy -> FastAPI metrics/jobs
Go worker -> leased PostgreSQL jobs -> snapshots / optional Ollama summary
```

All business records start from received verified events. We store UIDs, event-type IDs, appointment timestamps/status, receipt metadata, and audited administration; no names, emails, reading notes, or card details are copied. Cal.com controls availability, booking, reschedule, cancellation, and provider confirmation. Prices/revenue are not fabricated or inferred.

PostgreSQL's transaction combines receipts, projections, and pending jobs. The database queue acts as a transactional outbox and durable job store. Workers claim with FOR UPDATE SKIP LOCKED, validate lease tokens at completion, retry with jitter, and mark exhausted jobs failed. Admins can inspect and retry. Model calls are at least once under crash recovery; resulting summaries are deduplicated. A self-hosted Ollama server receives only numeric aggregates when explicitly enabled.

Admin passwords are Argon2-hashed; sessions use random tokens with only hashes persisted, expire after eight hours, and are revoked at logout. Login attempts are globally bounded in PostgreSQL; admin writes require exact Origin. Production cookies require HTTPS. Caddy terminates TLS and keeps database/API/model services behind the network boundary. Separate database roles restrict application/worker writes. There is no MFA or multi-role authorization yet; all provisioned admins are trusted operators.

The existing Vercel frontend remains usable for public booking. Production API/database/worker infrastructure must be launched on the prepared Docker server and connected before admin is live. Historical import and provider reconciliation are still operational gaps; never claim this reporting store is a complete calendar/payment ledger.
