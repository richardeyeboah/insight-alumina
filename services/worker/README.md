# Go background worker

PostgreSQL-backed durable queue; bounded concurrency (default 2, maximum 4), atomic SKIP LOCKED claims, 120-second leases, up to five attempts, exponential backoff with jitter, lease recovery, dead-letter state, and graceful drain.

Jobs: refresh aggregate metric snapshots; optional Ollama summaries from numeric counts only. Results and job completion commit atomically with lease-token validation; stale workers cannot overwrite a reclaimed job. Queue execution is at least once: a crash can repeat model inference, though stored results are deduplicated by job ID.

```sh
go test ./...
go vet ./...
# After API migrations; set DATABASE_URL to the worker role connection.
go run ./cmd/worker
```

For PostgreSQL integration tests set TEST_DATABASE_URL to an isolated migrated database. Tests truncate job/snapshot tables. See docs/DOCKER_DEPLOYMENT.md for environment, optional model setup, and production process hosting. This worker requires a long-running server/container, not a Vercel request function.
