# Infrastructure
Phase 1 deploys only `apps/web` and uses hosted Cal.com. No cloud resources are provisioned by this repository.

Optional local scaffolds:
```sh
docker compose --profile backend up --build
# Separate terminal, only to demonstrate process lifecycle:
docker compose --profile worker up --build
```
The API binds only to localhost on the host machine. These containers are not a production deployment stack. Add reviewed database migrations, secrets, private networking, health/readiness checks, image digests, backups, and deployment automation when phases 2/3 are approved. No PostgreSQL container is started yet because no persistence is implemented.
