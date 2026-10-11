package jobs

import (
	"testing"
	"time"
)

func TestBackoffBounds(t *testing.T) {
	if Backoff(1) != 2*time.Second || Backoff(100) != 32*time.Second {
		t.Fatal("retry backoff must be bounded")
	}
}
