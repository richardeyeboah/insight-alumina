package jobs

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestSummarySendsOnlyAggregateCounts(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var body map[string]any
		if json.NewDecoder(r.Body).Decode(&body) != nil {
			t.Fatal("bad body")
		}
		if body["stream"] != false || !strings.Contains(body["prompt"].(string), `"total":2`) {
			t.Error("missing bounded aggregate prompt")
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"response":"Two bookings recorded.","done":true}`))
	}))
	defer server.Close()
	result, err := Summarize(context.Background(), server.URL, "test-model", map[string]int64{"total": 2})
	if err != nil || result != "Two bookings recorded." {
		t.Fatal(result, err)
	}
}
func TestSummaryRejectsProviderFailure(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { w.WriteHeader(500) }))
	defer server.Close()
	if _, err := Summarize(context.Background(), server.URL, "test", map[string]int64{}); err == nil {
		t.Fatal("provider failure accepted")
	}
}
