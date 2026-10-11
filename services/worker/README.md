# Worker scaffold
Go 1.24+ process with structured lifecycle logs and graceful SIGINT/SIGTERM shutdown. No queue, job execution, retries, concurrency pool, or database connection is implemented.

```sh
go run ./cmd/worker
# Ctrl+C stops the process
go test ./...
go vet ./...
```
See the phase 3 roadmap before enabling a production worker.
