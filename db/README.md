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

## Rules

- Never edit a migration that has already run anywhere; add the next number (`003_…`).
- Changing a table means updating three places: the new migration, the Python mapping, the Go struct.
- Plain Postgres + pgvector only, so the same files run on Neon or AWS RDS later.

| File | Creates |
|---|---|
| `001_content_facts.sql` | pgvector extension, `content_facts` (shared summary cache) |
| `002_core_tables.sql` | `users`, `goals`, `sessions`, `verdicts`, `appeals`, `daily_stats` |
