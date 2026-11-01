// Package aiclient calls the Python AI service (ai-service, POST /v1/classify).
package aiclient

import (
	"context"
	"errors"
	"net/http"
	"time"

	"github.com/Space-Fighter/AutopilotFocus/api/internal/verdict"
)

// Client talks to one AI service. Create it once in main and reuse it:
// http.Client keeps connections open between requests.
type Client struct {
	baseURL string
	http    *http.Client
}

func New(baseURL string, timeout time.Duration) *Client {
	return &Client{
		baseURL: baseURL,
		http:    &http.Client{Timeout: timeout},
	}
}

// YOU TYPE #3
// Classify sends the request to POST {baseURL}/v1/classify and returns Python's verdict.
// Errors: Python unreachable, timeout, a non-200 status, or a body that isn't a Verdict.
func (c *Client) Classify(ctx context.Context, req verdict.Request) (verdict.Verdict, error) {
	return verdict.Verdict{}, errors.New("YOU TYPE #3: aiclient.Classify")
}
