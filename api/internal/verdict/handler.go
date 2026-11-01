package verdict

import (
	"context"
	"net/http"
)

// Classifier is anything that can turn a Request into a Verdict. aiclient.Client is one.
// Defining the interface here (where it's used) means this package doesn't import
// aiclient, and tests can pass a fake.
type Classifier interface {
	Classify(ctx context.Context, req Request) (Verdict, error)
}

// Handler serves POST /v1/verdict.
type Handler struct {
	AI Classifier
}

// YOU TYPE #2
// ServeHTTP reads the JSON body, checks it, asks the AI service, and writes the verdict as JSON.
//   - bad JSON, or missing page.url / goal.text  -> 400 Bad Request
//   - AI service fails                           -> 502 Bad Gateway
//   - success                                    -> 200 + Verdict JSON
func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	http.Error(w, "YOU TYPE #2: verdict.Handler.ServeHTTP", http.StatusNotImplemented)
}
