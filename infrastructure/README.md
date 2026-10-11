# Infrastructure

`docker-compose.yml` starts PostgreSQL, a one-shot migration service, FastAPI and the Go worker. `docker-compose.production.yml` adds Next.js and Caddy HTTPS, removes the local API port, and sets production session security. Optional AI profile adds internal Ollama; weights require an explicit pull.

Read [Docker deployment](../docs/DOCKER_DEPLOYMENT.md) before starting. Set distinct hexadecimal database secrets, webhook secret, real event IDs, and server domain. There are no default production credentials. PostgreSQL initialization scripts run only for a fresh volume; rotation needs SQL plus service recreation. Backups are required separately from volume persistence.
