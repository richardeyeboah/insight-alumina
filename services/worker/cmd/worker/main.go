package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"strconv"
	"sync"
	"syscall"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/richardeyeboah/insight-alumina/services/worker/internal/jobs"
)

func main() {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	config, err := pgxpool.ParseConfig(os.Getenv("DATABASE_URL"))
	if err != nil || os.Getenv("DATABASE_URL") == "" {
		slog.Error("DATABASE_URL is required")
		os.Exit(1)
	}
	config.MaxConns = 6
	db, err := pgxpool.NewWithConfig(ctx, config)
	if err != nil {
		slog.Error("database configuration failed")
		os.Exit(1)
	}
	defer db.Close()
	if err = db.Ping(ctx); err != nil {
		slog.Error("database unavailable")
		os.Exit(1)
	}
	concurrency, _ := strconv.Atoi(os.Getenv("WORKER_CONCURRENCY"))
	if concurrency < 1 {
		concurrency = 2
	}
	if concurrency > 4 {
		concurrency = 4
	}
	var wg sync.WaitGroup
	for i := 0; i < concurrency; i++ {
		wg.Add(1)
		go func() { defer wg.Done(); run(ctx, db) }()
	}
	slog.Info("worker started", "concurrency", concurrency)
	wg.Wait()
	slog.Info("worker drained and stopped")
}

func run(ctx context.Context, db *pgxpool.Pool) {
	for ctx.Err() == nil {
		claimCtx, cancel := context.WithTimeout(ctx, 10*time.Second)
		j, err := jobs.Claim(claimCtx, db)
		cancel()
		if err != nil || j == nil {
			if err != nil {
				slog.Warn("job claim failed")
			}
			select {
			case <-ctx.Done():
				return
			case <-time.After(time.Second):
			}
			continue
		}
		// Shutdown stops claims; current work has a bounded window to finish.
		workCtx, done := context.WithTimeout(context.Background(), 80*time.Second)
		counts, e := jobs.Metrics(workCtx, db)
		summary := ""
		model := os.Getenv("OLLAMA_MODEL")
		if e == nil && j.Kind == "ai_summary" {
			if os.Getenv("AI_ANALYTICS_ENABLED") != "true" || model == "" {
				e = &disabledError{}
			} else {
				summary, e = jobs.Summarize(workCtx, os.Getenv("OLLAMA_URL"), model, counts)
			}
		}
		if e == nil {
			e = jobs.Complete(workCtx, db, j, counts, summary, model)
		}
		done()
		if e != nil {
			failureCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			if err := jobs.Fail(failureCtx, db, j, "Processing failed; check worker/model availability"); err != nil {
				slog.Warn("job failure update failed", "job_id", j.ID)
			}
			cancel()
			slog.Warn("job attempt failed", "job_id", j.ID, "attempt", j.Attempts)
		} else {
			slog.Info("job complete", "job_id", j.ID, "kind", j.Kind)
		}
	}
}

type disabledError struct{}

func (*disabledError) Error() string { return "AI disabled or model not configured" }
