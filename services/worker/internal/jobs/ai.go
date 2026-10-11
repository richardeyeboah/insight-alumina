package jobs

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// Only numeric aggregate counts are sent to the model, never customer records.
func Summarize(ctx context.Context, endpoint, model string, counts map[string]int64) (string, error) {
	u, err := url.Parse(endpoint)
	if err != nil || u.Host == "" || (u.Scheme != "http" && u.Scheme != "https") || u.User != nil {
		return "", errors.New("invalid model endpoint")
	}
	metrics, _ := json.Marshal(counts)
	body, _ := json.Marshal(map[string]any{"model": model, "stream": false, "prompt": "Summarize these tarot booking business counts in at most 120 words. Do not invent revenue, prices, customers, causes, trends, or forecasts. These are current counts, not a historical series. Suggest one cautious operational check. Metrics: " + string(metrics), "options": map[string]any{"num_predict": 220, "temperature": 0.2}})
	req, err := http.NewRequestWithContext(ctx, "POST", strings.TrimRight(endpoint, "/")+"/api/generate", bytes.NewReader(body))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")
	client := &http.Client{Timeout: 60 * time.Second, CheckRedirect: func(req *http.Request, via []*http.Request) error { return http.ErrUseLastResponse }}
	res, err := client.Do(req)
	if err != nil {
		return "", errors.New("model request failed")
	}
	defer res.Body.Close()
	if res.StatusCode != 200 {
		return "", fmt.Errorf("model returned HTTP %d", res.StatusCode)
	}
	raw, err := io.ReadAll(io.LimitReader(res.Body, 65537))
	if err != nil || len(raw) > 65536 {
		return "", errors.New("invalid model response")
	}
	var result struct {
		Response string `json:"response"`
		Done     bool   `json:"done"`
	}
	if json.Unmarshal(raw, &result) != nil || !result.Done || strings.TrimSpace(result.Response) == "" || len(result.Response) > 4000 {
		return "", errors.New("invalid model response")
	}
	return result.Response, nil
}
