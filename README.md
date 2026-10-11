# Insight Alumina

Tarot booking website and business administration monorepo.

**Public website:** https://insight-alumina.vercel.app — Next.js/TypeScript/Tailwind editorial design with inline Cal.com booking. Client-owned session configuration remains in Cal.com. No prices, testimonials, or reading services are invented.

**Backend implementation:** PostgreSQL migrations, signed booking webhooks, password-protected administration with server sessions, booking analytics, a durable Go worker, and opt-in Ollama business summaries. Backend services are prepared for Docker deployment; they are not provisioned on a production server by this repository. The Vercel website needs a reachable `API_BASE_URL` before its `/admin` area can connect.

## Structure
```text
apps/web/                  Booking site, /admin dashboard, server-only API proxy
services/api/              FastAPI, authentication, analytics, webhooks, migrations
services/worker/           Go queue consumer and optional AI adapter
infrastructure/docker/    Containers, PostgreSQL roles, Caddy HTTPS configuration
.github/workflows/ci.yml   Web checks and PostgreSQL-backed API/worker tests
docs/                     Architecture, API, operations, security, rollout
```

## Website
Node 22/npm:
```sh
cd apps/web
npm ci
cp .env.example .env.local
npm run dev
```
The public Cal.com profile is configured in the example. `API_BASE_URL` is server-only, normally `http://127.0.0.1:8000` for local development. Real `.env` files are ignored. Open http://localhost:3000; administration is at `/admin`.

## Full local backend
Install Docker with Compose v2.24+; from repository root:
```sh
cp .env.example .env
# Set three independent random hexadecimal database passwords,
# a random webhook secret of at least 32 characters, and real event type IDs.
docker compose up --build -d
docker compose run --rm migrate python -m app.manage create-admin --username owner
```
The account creation command securely prompts for a password of at least 16 characters. No default admin account/password exists. The database stays internal; the local API binds to 127.0.0.1:8000. Use Next.js locally with its API_BASE_URL configured.

**Production Docker instructions:** [Docker deployment](docs/DOCKER_DEPLOYMENT.md). The Go worker drains on shutdown, claims jobs with PostgreSQL leases, retries failures with bounded backoff/jitter, and exposes exhausted jobs for admin retry.

**Optional AI:** disabled by default. A self-hosted Ollama model can summarize numeric aggregate counts only, with one new summary job per UTC day and a token/time limit. No customer identifiers, notes, reading content, prices, or API secrets go to the model. Outputs are advisory and labeled. Actual model weights are not bundled or pulled automatically.

## Documentation
- [Architecture](docs/ARCHITECTURE.md)
- [API contracts](docs/API.md)
- [Cal.com integration](docs/BOOKING.md)
- [Docker deployment, backups, and rollout](docs/DOCKER_DEPLOYMENT.md)
- [Website deployment and cost considerations](docs/DEPLOYMENT.md)
- [Security](docs/SECURITY.md)
- [Roadmap](docs/ROADMAP.md)
- [Validation](docs/VALIDATION.md)

## Operating costs and ownership
Domain/web hosting plus Cal.com are the initial footprint. Backend adds a server, PostgreSQL storage/backups, and optional model compute; no budget or zero-cost promise is fabricated. Keep accounts client-owned, set spending alerts, and configure backups before relying on analytics. Vercel Hobby permits only personal noncommercial use: [official terms](https://vercel.com/docs/plans/hobby).

The repository is public at the owner's request. Keep secrets and customer information out of Git/issues/logs. A development dependency advisory is documented in SECURITY.md. No open-source license is granted; establish ownership/licensing separately.
