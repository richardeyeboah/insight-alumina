# Insight Alumina

Public monorepo for a tarot-reading client booking website, designed to launch with a small operating footprint and grow only when business needs justify it.

**Status: initial scaffold, not a launched client product.** The web app renders a responsive starter page and links to a configured Cal.com event. The API exposes a health endpoint. The Go process demonstrates graceful shutdown. Service prices, durations, client biography, availability, payment rules, and testimonials have not been supplied or invented. PostgreSQL, administration, webhook processing, AI analytics, and background jobs are planned, not completed.

## Repository layout
```text
apps/web/                   Next.js, TypeScript, Tailwind, ESLint
services/api/               Python FastAPI scaffold and contract tests
services/worker/            Go process scaffold
infrastructure/docker/     Optional development container definitions
.github/workflows/          CI for all three components
.github/dependabot.yml      Dependency update configuration
docs/                      Architecture, API, roadmap, deployment, security, booking
```

## Quick start: website only
Prerequisites: Node.js 22 LTS and npm. The generated npm lockfile is committed.
```sh
git clone https://github.com/richardeyeboah/insight-alumina.git
cd insight-alumina/apps/web
cp .env.example .env.local
# Set NEXT_PUBLIC_CAL_BOOKING_URL to the client's actual Cal.com event URL.
npm ci
npm run dev
```
Open http://localhost:3000. An unset or invalid URL displays a booking preparation message; the app accepts HTTPS `cal.com` URLs with an owner and event path. Restart the dev server after changing environment variables. Production changes require a rebuild. No Cal.com API key is needed for the phase 1 link.

```sh
npm run lint
npm run typecheck
npm run build
npm start
```
For Python 3.11+ setup, see [API setup](services/api/README.md). For Go 1.24+ setup, see [worker setup](services/worker/README.md). Optional Docker commands are in [infrastructure](infrastructure/README.md). These components are unnecessary for phase 1.

## Phased delivery
1. **Booking website:** approved content, service information, Cal.com availability and booking, responsive/accessibility review, domain, and commercial hosting. Launch only after end-to-end booking checks.
2. **Backend and analytics:** FastAPI, PostgreSQL, authenticated administration, verified booking webhooks, reliable persistence, and aggregate business reporting. AI summaries are optional and disabled until implemented with privacy and spending controls.
3. **Systems engineering:** Go worker, durable jobs, bounded concurrency, retries, deduplication, failure recovery, observability, Docker hardening, and controlled deployment pipelines.

## Documentation
- [Architecture and data flow](docs/ARCHITECTURE.md)
- [Roadmap and acceptance criteria](docs/ROADMAP.md)
- [Local and production deployment, costs, rollback](docs/DEPLOYMENT.md)
- [Implemented API and future contracts](docs/API.md)
- [Cal.com setup and integration](docs/BOOKING.md)
- [Security and privacy](docs/SECURITY.md)

## Cost and ownership
Phase 1 needs only web hosting, a domain, and the client's scheduling account. Confirm Cal.com plan eligibility and integration requirements; do not assume paid features are free. Avoid idle API/database/worker resources until needed. Set provider spending alerts and keep production accounts under client ownership.

**Vercel Hobby is restricted to personal, noncommercial use. A commercial client booking website needs Vercel Pro or another host whose terms permit commercial use.** See [Vercel Hobby documentation](https://vercel.com/docs/plans/hobby). No exact hosting budget is promised; verify current plan, seat, usage, domain, payment, and tax costs before launch.

## Contributions
Keep secrets and customer data out of commits, issues, CI logs, and previews. Use focused pull requests and require passing CI before merging once branch protections are configured. CI is defined here; branch protection and hosting integrations are not automatically provisioned. No open-source license is granted by this scaffold; establish client ownership and licensing separately.
