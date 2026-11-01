# AutopilotFocus Go API

Thin relay for the MVP: the extension calls `POST /v1/verdict`, the API forwards it to the
Python AI service (`POST /v1/classify`) and returns the verdict. Sign-in and Postgres come later.

MVP board: frame 1 "Go API", frame 3 steps 2–3 and 6–7, frame 6 step 2.

## Layout

```
api/
  cmd/server/main.go          #1 main: config, routes, start server
  internal/verdict/types.go   request / verdict structs (mirror Python's schemas.py)
  internal/verdict/handler.go #2 POST /v1/verdict
  internal/aiclient/client.go #3 HTTP call to Python
  internal/config/config.go   settings from env
  internal/httpx/cors.go      lets the Chrome extension call the API
```

## Functions to write, in order

| # | File | Function | Concept |
|---|------|----------|---------|
| 1 | `cmd/server/main.go` | `main` | `net/http` server, routing, wiring |
| 2 | `internal/verdict/handler.go` | `Handler.ServeHTTP` | handlers, JSON decode/encode, status codes |
| 3 | `internal/aiclient/client.go` | `Client.Classify` | HTTP client, `context`, timeouts, error wrapping |

## Settings (env)

| Name | Default |
|---|---|
| `PORT` | `8080` |
| `AI_SERVICE_URL` | `http://127.0.0.1:8001` |
| `AI_TIMEOUT` | `45s` |

## Run

```bash
go run ./cmd/server
```
