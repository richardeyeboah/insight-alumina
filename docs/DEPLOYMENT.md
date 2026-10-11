# Deployment and operating cost

## Current state
The booking frontend is deployed at https://insight-alumina.vercel.app/. The PostgreSQL/API/worker/admin integration is implemented and prepared for Docker deployment; it has not been provisioned on a production server. Frontend deployment alone does not run these services.

Follow [Docker deployment](DOCKER_DEPLOYMENT.md) for the full stack, HTTPS, first admin creation, Cal.com webhooks, optional Ollama, backups, and operations. The deployment includes a standalone Next.js container. Keeping Vercel for the frontend requires the separately documented protected API ingress and server-only API_BASE_URL configuration.

## Frontend hosting
For Vercel, use apps/web as root, Next.js preset, Node 22, npm ci, and npm run build. Set NEXT_PUBLIC_CAL_BOOKING_URL to the approved profile/event URL and redeploy after changes. Verify mobile booking, calendar conflicts, confirmation, cancellation, and rescheduling using approved test appointments. Custom domain/DNS and client account setup remain operator tasks.

**Vercel Hobby is intended for noncommercial use.** Before commercial operation, choose a commercially permitted plan or host. No subscription upgrade or purchase is performed by this code. See [Vercel Hobby terms](https://vercel.com/docs/plans/hobby).

## Costs and release controls
Budget for server/domain/scheduling services, database storage and off-server backups, monitoring, bandwidth, and any payment-provider fees. Optional model serving adds memory/CPU/GPU requirements. No fixed prices or zero-cost commercial hosting claims are made; check vendor quotes and licenses before purchasing. Set spending alerts and resource limits.

Require reviewed CI and least-privilege access. Keep staging separate from production, test backup restoration, record a known-good release, and use backward-compatible migrations. See the Docker guide for rollback and secret rotation. The example images use mutable tags; pin reviewed digests and scan them for production releases.
