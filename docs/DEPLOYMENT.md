# Deployment and operating cost

## Local development
Node.js 22 LTS/npm for the website, Python 3.11+ for the optional API, Go 1.24+ for the optional worker, Docker Compose for container demonstrations. Follow component READMEs; no cloud account or database is required to run the scaffold. Copy `.env.example` to the location expected by each tool; root `.env` is not read automatically by Next.js.

## Phase 1 production: web only
1. Confirm client-owned GitHub/hosting/Cal.com/domain accounts and a commercially permitted hosting plan. **Vercel Hobby is noncommercial and unsuitable for this client business website.** Use Vercel Pro or evaluate another commercially permitted Next.js host. [Official restriction](https://vercel.com/docs/plans/hobby).
2. Import this GitHub repository into Vercel, set root directory to `apps/web`, use the Next.js preset, Node 22, `npm ci` install, and `npm run build`. Do not deploy the repository root as a Next.js project.
3. Set `NEXT_PUBLIC_CAL_BOOKING_URL` to the client's confirmed event URL in the production environment. It is public and baked into the build; redeploy after changes. Give previews separate test booking URLs or leave them unset.
4. Configure the client domain and DNS, verify TLS, and check the published site from desktop/mobile. Confirm actual bookings, notifications, rescheduling, cancellation, and calendar conflicts.
5. Restrict preview access when unpublished client content is present. Establish least-privilege team roles and billing alerts. Configure branch protections to require CI and review; these settings are not created by the scaffold.
6. Record the known-good deployment and rollback through the host's deployment history. Roll back both deployment and relevant public booking configuration if necessary.

No production deployment, subscription purchase, domain registration, Cal account setup, or branch protections are performed by this repository.

For another Node host, build in `apps/web`, run `npm start` behind HTTPS with the host's provided port and environment. Confirm current platform requirements and commercial terms. The Docker files here cover optional backend services, not the web app.

## Phase 2 production (future)
Deploy FastAPI as an independently managed service behind HTTPS, and use managed PostgreSQL with private connectivity where supported. Add schema migrations as a controlled release step, authenticated admin access, connection pooling, DB readiness, rate/body limits, signature verification, and backup/restore drills. Store secrets in provider secret management, rotate them, and separate staging from production. Protect API documentation after business endpoints are added. CORS, if required, should allow only known web origins; it is not authorization.

## Phase 3 production (future)
Deploy Go to a long-running container/worker host appropriate for queue consumption. Do not assume a request-based web function can run an indefinite worker. Use durable jobs, bounded resources, graceful shutdown, health/readiness checks, immutable image digests, logs/metrics/alerts, dead-letter handling, and staged releases. Database migrations must remain backward compatible during rollout and rollback.

## Cost controls
Phase 1 pays only for necessary hosting/domain/scheduling and any configured payment fees. Confirm plan limits and per-seat/usage billing, custom domain renewal, Cal feature availability, tax, and payment fees using current vendor quotes. No fixed or zero-cost commercial budget is asserted.

Phase 2 adds API/database compute, storage, backups, network egress, and optional analytics/provider usage. Phase 3 may add queue/worker/monitoring costs. Set monthly budgets and alerts, cap AI requests/tokens, monitor GitHub Actions minutes for private repos, and avoid provisioning idle services before their acceptance gates. Recheck pricing at purchase time.
