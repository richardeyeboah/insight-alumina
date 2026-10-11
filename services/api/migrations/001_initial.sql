CREATE TABLE IF NOT EXISTS admin_users (
 username text PRIMARY KEY, password_hash text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS admin_sessions (
 token_hash text PRIMARY KEY, username text NOT NULL REFERENCES admin_users(username) ON DELETE CASCADE,
 expires_at timestamptz NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS login_attempts (id bigserial PRIMARY KEY, attempted_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS login_attempts_time ON login_attempts(attempted_at);
CREATE TABLE IF NOT EXISTS webhook_receipts (
 event_hash text PRIMARY KEY, trigger_event text NOT NULL, booking_uid text NOT NULL,
 occurred_at timestamptz NOT NULL, received_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS bookings (
 uid text PRIMARY KEY, event_type_id bigint NOT NULL, starts_at timestamptz NOT NULL,
 ends_at timestamptz NOT NULL, status text NOT NULL CHECK(status IN ('accepted','cancelled','requested','rejected','rescheduled')),
 event_at timestamptz NOT NULL, updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS jobs (
 id bigserial PRIMARY KEY, job_key text UNIQUE NOT NULL,
 kind text NOT NULL CHECK(kind IN ('refresh_metrics','ai_summary')),
 state text NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','running','done','failed')),
 attempts integer NOT NULL DEFAULT 0, available_at timestamptz NOT NULL DEFAULT now(),
 locked_until timestamptz, lease_token text, last_error text,
 created_at timestamptz NOT NULL DEFAULT now(), finished_at timestamptz
);
CREATE INDEX IF NOT EXISTS jobs_ready ON jobs(state, available_at);
CREATE TABLE IF NOT EXISTS metric_snapshots (
 day date PRIMARY KEY, metrics jsonb NOT NULL, updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS ai_summaries (
 job_id bigint PRIMARY KEY REFERENCES jobs(id), summary text NOT NULL,
 model text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS audit_log (
 id bigserial PRIMARY KEY, username text NOT NULL, action text NOT NULL,
 subject text, created_at timestamptz NOT NULL DEFAULT now()
);
