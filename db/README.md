# Database (Postgres + pgvector)

One schema shared by the Python AI service and the Go API. **These SQL files own the schema**:
the Python and Go ORMs only map to the tables; they never create or alter them.

Board: full board frame 10 "Database schema".

## Start Postgres locally

From the repo root (needs Docker Desktop running and `.env`, see `docker-compose.yml`):

```bash
docker compose up -d
docker compose ps        # wait for (healthy)
```

## Apply migrations

Run every file in order. They use `IF NOT EXISTS`, so running them again is safe.

```bash
for f in db/migrations/*.sql; do docker compose exec -T db psql -U autopilot -d autopilot -v ON_ERROR_STOP=1 -f - < "$f"; done
```

## Regenerate the code (after every migration)

Nobody hand-writes table classes: both languages generate them from the schema.

```bash
# Python (sqlacodegen, reads the live database) -> ai-service/src/ai_service/db_models.py
cd ai-service && uv run python scripts/gen_models.py

# Go (sqlc, reads db/migrations + api/internal/db/queries) -> api/internal/db/*.go
cd api && MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd -W)/..:/src" -w /src/api sqlc/sqlc:1.30.0 generate
```

(`pwd -W` and `MSYS_NO_PATHCONV` are for Git Bash on Windows; on macOS/Linux use `"$PWD/..:/src"`.)

## Changing a table

1. Add the next migration file (`003_…sql`). Never edit one that has already run.
2. Apply it (above).
3. Regenerate the code (above). Python: add the table to `TABLES` in `gen_models.py` if it needs it.
   Go: add queries in `api/internal/db/queries/*.sql` for anything new.
4. Fix whatever no longer compiles or type-checks: that's the drift, caught for you.

## Rules

- Plain Postgres + pgvector only, so the same files run on Neon or AWS RDS later.
- Generated files (`db_models.py`, `api/internal/db/*.go`) are never edited by hand.

| File | Creates |
|---|---|
| `001_content_facts.sql` | pgvector extension, `content_facts` (shared summary cache) |
| `002_core_tables.sql` | `users`, `goals`, `sessions`, `verdicts`, `appeals`, `daily_stats` |
