package jobs

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

func testDB(t *testing.T) *pgxpool.Pool {
	t.Helper()
	url := os.Getenv("TEST_DATABASE_URL")
	if url == "" {
		t.Skip("TEST_DATABASE_URL required")
	}
	db, err := pgxpool.New(context.Background(), url)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(db.Close)
	if _, err = db.Exec(context.Background(), "TRUNCATE ai_summaries,jobs,metric_snapshots RESTART IDENTITY CASCADE"); err != nil {
		t.Fatal(err)
	}
	return db
}

func TestLeaseRecoveryAndStaleCompletion(t *testing.T) {
	ctx := context.Background()
	db := testDB(t)
	if _, err := db.Exec(ctx, "INSERT INTO jobs(job_key,kind) VALUES ('lease-test','refresh_metrics')"); err != nil {
		t.Fatal(err)
	}
	first, err := Claim(ctx, db)
	if err != nil || first == nil {
		t.Fatal(first, err)
	}
	second, err := Claim(ctx, db)
	if err != nil || second != nil {
		t.Fatal("leased job claimed twice", second, err)
	}
	_, _ = db.Exec(ctx, "UPDATE jobs SET locked_until=now()-interval '1 second'")
	recovered, err := Claim(ctx, db)
	if err != nil || recovered == nil || recovered.Attempts != 2 || recovered.Token == first.Token {
		t.Fatal(recovered, err)
	}
	if err = Complete(ctx, db, first, map[string]int64{"total": 99}, "", ""); err == nil {
		t.Fatal("stale lease overwrote job")
	}
	if err = Complete(ctx, db, recovered, map[string]int64{"total": 2}, "", ""); err != nil {
		t.Fatal(err)
	}
	var state string
	if err = db.QueryRow(ctx, "SELECT state FROM jobs").Scan(&state); err != nil || state != "done" {
		t.Fatal(state, err)
	}
}

func TestFailureRetryAndFinalLeaseExhaustion(t *testing.T) {
	ctx := context.Background()
	db := testDB(t)
	_, _ = db.Exec(ctx, "INSERT INTO jobs(job_key,kind) VALUES ('failure-test','refresh_metrics')")
	j, err := Claim(ctx, db)
	if err != nil {
		t.Fatal(err)
	}
	if err = Fail(ctx, db, j, "safe failure"); err != nil {
		t.Fatal(err)
	}
	var state string
	var available time.Time
	if err = db.QueryRow(ctx, "SELECT state,available_at FROM jobs").Scan(&state, &available); err != nil || state != "pending" || !available.After(time.Now()) {
		t.Fatal(state, available, err)
	}
	_, _ = db.Exec(ctx, "UPDATE jobs SET state='running',attempts=5,locked_until=now()-interval '1 second'")
	if j, err = Claim(ctx, db); err != nil || j != nil {
		t.Fatal(j, err)
	}
	_ = db.QueryRow(ctx, "SELECT state FROM jobs").Scan(&state)
	if state != "failed" {
		t.Fatal("final crashed attempt stuck", state)
	}
}
