package jobs

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Job struct {
	ID       int64
	Kind     string
	Token    string
	Attempts int
}

const MaxAttempts = 5

func Claim(ctx context.Context, db *pgxpool.Pool) (*Job, error) {
	tokenBytes := make([]byte, 16)
	if _, err := rand.Read(tokenBytes); err != nil {
		return nil, err
	}
	token := hex.EncodeToString(tokenBytes)
	// A crashed final attempt becomes visible as a failed job rather than staying stuck.
	if _, err := db.Exec(ctx, `UPDATE jobs SET state='failed',last_error='Lease expired after final attempt',lease_token=NULL,locked_until=NULL WHERE state='running' AND locked_until<now() AND attempts>=$1`, MaxAttempts); err != nil {
		return nil, err
	}
	row := db.QueryRow(ctx, `WITH candidate AS (
 SELECT id FROM jobs WHERE attempts<$1 AND ((state='pending' AND available_at<=now()) OR (state='running' AND locked_until<now()))
 ORDER BY available_at,id FOR UPDATE SKIP LOCKED LIMIT 1)
 UPDATE jobs j SET state='running',attempts=attempts+1,lease_token=$2,locked_until=now()+interval '120 seconds'
 FROM candidate c WHERE j.id=c.id RETURNING j.id,j.kind,j.attempts`, MaxAttempts, token)
	j := &Job{Token: token}
	err := row.Scan(&j.ID, &j.Kind, &j.Attempts)
	if errors.Is(err, pgx.ErrNoRows) {
		return nil, nil
	}
	return j, err
}

func Backoff(attempt int) time.Duration {
	if attempt < 1 {
		attempt = 1
	}
	if attempt > MaxAttempts {
		attempt = MaxAttempts
	}
	return time.Duration(1<<uint(attempt)) * time.Second
}

func Fail(ctx context.Context, db *pgxpool.Pool, j *Job, message string) error {
	state := "pending"
	if j.Attempts >= MaxAttempts {
		state = "failed"
	}
	var b [1]byte
	_, _ = rand.Read(b[:])
	delay := Backoff(j.Attempts) + time.Duration(b[0])*time.Millisecond*10
	_, err := db.Exec(ctx, `UPDATE jobs SET state=$1,last_error=$2,available_at=now()+$3::interval,locked_until=NULL,lease_token=NULL WHERE id=$4 AND lease_token=$5 AND state='running'`, state, message, fmt.Sprintf("%f seconds", delay.Seconds()), j.ID, j.Token)
	return err
}

func Metrics(ctx context.Context, db *pgxpool.Pool) (map[string]int64, error) {
	m := map[string]int64{}
	var total, active, cancelled, requested, upcoming int64
	err := db.QueryRow(ctx, `SELECT count(*) FILTER(WHERE status!='rescheduled'),count(*) FILTER(WHERE status='accepted'),count(*) FILTER(WHERE status='cancelled'),count(*) FILTER(WHERE status='requested'),count(*) FILTER(WHERE status='accepted' AND starts_at>=now()) FROM bookings`).Scan(&total, &active, &cancelled, &requested, &upcoming)
	m["total"] = total
	m["active"] = active
	m["cancelled"] = cancelled
	m["requested"] = requested
	m["upcoming"] = upcoming
	return m, err
}

func Complete(ctx context.Context, db *pgxpool.Pool, j *Job, metrics map[string]int64, summary, model string) error {
	tx, err := db.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)
	var id int64
	if err = tx.QueryRow(ctx, `UPDATE jobs SET state='done',finished_at=now(),locked_until=NULL,lease_token=NULL,last_error=NULL WHERE id=$1 AND lease_token=$2 AND state='running' RETURNING id`, j.ID, j.Token).Scan(&id); err != nil {
		return err
	}
	raw, err := json.Marshal(metrics)
	if err != nil {
		return err
	}
	if _, err = tx.Exec(ctx, `INSERT INTO metric_snapshots(day,metrics) VALUES ((now() AT TIME ZONE 'UTC')::date,$1) ON CONFLICT(day) DO UPDATE SET metrics=excluded.metrics,updated_at=now()`, raw); err != nil {
		return err
	}
	if j.Kind == "ai_summary" {
		if _, err = tx.Exec(ctx, `INSERT INTO ai_summaries(job_id,summary,model) VALUES ($1,$2,$3) ON CONFLICT(job_id) DO NOTHING`, j.ID, summary, model); err != nil {
			return err
		}
	}
	return tx.Commit(ctx)
}
