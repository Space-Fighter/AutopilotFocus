// Command server runs the AutopilotFocus Go API.
//
// Run from api/:  go run ./cmd/server
// Needs the Python AI service running (see ai-service/README.md).
package main

import (
	"log"
)

// YOU TYPE #1
// main wires everything together and starts the HTTP server:
//  1. load config
//  2. create the AI client
//  3. register routes: GET /health and POST /v1/verdict
//  4. wrap the router in httpx.CORS and listen on cfg.Port
func main() {
	log.Fatal("YOU TYPE #1: main")
}
