#!/usr/bin/env bash
# One command after you add or change a migration. Run from anywhere:
#   ./scripts/db-update.sh
#
#   1. start Postgres (docker compose) and wait until it's healthy
#   2. apply every migration in db/migrations/ that hasn't run yet (tracked in schema_migrations)
#   3. regenerate the Python models (sqlacodegen -> ai-service/src/ai_service/db_models.py)
#   4. regenerate the Go code       (sqlc       -> api/internal/db/)
#
# Then review the generated changes with `git diff` and commit them with the migration.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Database name and user come from the repo-root .env (same values docker compose uses).
set -a; source .env; set +a
psql_in_db() { docker compose exec -T db psql -q -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 "$@"; }

echo "== 1/4 Postgres"
docker compose up -d db >/dev/null
for _ in $(seq 1 30); do
  [ "$(docker inspect -f '{{.State.Health.Status}}' "$(docker compose ps -q db)")" = healthy ] && break
  sleep 2
done
echo "   healthy"

echo "== 2/4 migrations"
# Remembers which files have run, so each migration runs exactly once.
psql_in_db -c "CREATE TABLE IF NOT EXISTS schema_migrations (
                 version    text PRIMARY KEY,
                 applied_at timestamptz NOT NULL DEFAULT now());"
applied=0
for file in db/migrations/*.sql; do
  version="$(basename "$file" .sql)"
  if [ -n "$(psql_in_db -tA -c "SELECT 1 FROM schema_migrations WHERE version = '$version'")" ]; then
    continue
  fi
  echo "   applying $version"
  # The file and its bookkeeping row run in ONE transaction: either both happen or neither.
  { echo "SET client_min_messages TO warning;"; cat "$file"; echo
    echo "INSERT INTO schema_migrations (version) VALUES ('$version');"; } \
    | psql_in_db --single-transaction -f -
  applied=$((applied + 1))
done
echo "   $applied new migration(s) applied"

echo "== 3/4 Python models (sqlacodegen)"
(cd ai-service && uv run python scripts/gen_models.py)

echo "== 4/4 Go code (sqlc)"
# Git Bash on Windows needs a Windows-style path for docker volume mounts.
if HOST_ROOT="$(pwd -W 2>/dev/null)"; then export MSYS_NO_PATHCONV=1; else HOST_ROOT="$ROOT"; fi
docker run --rm -v "$HOST_ROOT:/src" -w /src/api sqlc/sqlc:1.30.0 generate
echo "   wrote api/internal/db/"

echo "Done. Review with: git diff -- ai-service/src/ai_service/db_models.py api/internal/db"
