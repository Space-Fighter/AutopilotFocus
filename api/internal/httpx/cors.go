// Package httpx holds small HTTP helpers shared by the handlers.
package httpx

import (
	"net/http"
	"strings"
)

// CORS lets the Chrome extension call this API. Requests from an extension carry an
// Origin like "chrome-extension://<id>". MVP: allow any extension; pin the real
// extension ID before launch.
func CORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if origin := r.Header.Get("Origin"); strings.HasPrefix(origin, "chrome-extension://") {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}
		if r.Method == http.MethodOptions { // the browser's preflight check
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next.ServeHTTP(w, r)
	})
}
