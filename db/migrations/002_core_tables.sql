-- 002: users, goals, sessions, verdicts, appeals, daily stats (full board frame 10).
-- Owned by these SQL migrations. The Python and Go ORMs only map to them.
--
-- Deleting a user deletes all their rows (ON DELETE CASCADE): "delete my data" must
-- remove everything (spec §6.2 of goals-and-basic-mode-nearest-case-spec.md).

-- Accounts. One row per person.
CREATE TABLE IF NOT EXISTS users (
    id             uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    email          text        NOT NULL UNIQUE,
    auth_provider  text        NOT NULL CHECK (auth_provider IN ('google', 'email')),
    password_hash  text,                         -- only for auth_provider = 'email'
    plan           text        NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'premium')),
    profile        jsonb       NOT NULL DEFAULT '{}',   -- role, main topics
    focus_hours    jsonb       NOT NULL DEFAULT '{}',   -- preferred focus hours
    created_at     timestamptz NOT NULL DEFAULT now()
);

-- Goals: saved list, session-only, or inferred. Embedded once; the vector is reused.
CREATE TABLE IF NOT EXISTS goals (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     uuid        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    text        text        NOT NULL,
    vec         vector(384),
    kind        text        NOT NULL CHECK (kind IN ('saved', 'session', 'inferred')),
    status      text        NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'pending', 'rejected')),
    created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS goals_user_id_idx ON goals (user_id);

-- Focus sessions. In the MVP one session = one period with blocking switched On.
CREATE TABLE IF NOT EXISTS sessions (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     uuid        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    mode        text        NOT NULL DEFAULT 'on_off',
    goal_id     uuid        REFERENCES goals (id) ON DELETE SET NULL,
    started_at  timestamptz NOT NULL DEFAULT now(),
    ended_at    timestamptz                       -- NULL while the session is running
);
CREATE INDEX IF NOT EXISTS sessions_user_id_idx ON sessions (user_id);

-- Decisions. One row per user + page + goal; repeat visits bump visit_count.
CREATE TABLE IF NOT EXISTS verdicts (
    id            uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       uuid        NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    session_id    uuid        REFERENCES sessions (id) ON DELETE SET NULL,
    content_id    bigint      REFERENCES content_facts (id) ON DELETE SET NULL, -- NULL on fallback
    goal_id       uuid        REFERENCES goals (id) ON DELETE SET NULL,
    decision      text        NOT NULL CHECK (decision IN ('allow', 'block')),
    reason        text        NOT NULL,
    source        text        NOT NULL,           -- embedding | llm | fallback (more later)
    weight        real        NOT NULL DEFAULT 0, -- vote weight for the closest-case search
    confirmed     boolean     NOT NULL DEFAULT false,
    user_reason   text,                           -- optional reason from the floating prompt
    page_vec      vector(384),                    -- extracted-summary vector (closest-case search)
    goal_vec      vector(384),
    combined_vec  vector(768),                    -- [page_vec, goal_vec]
    visit_count   integer     NOT NULL DEFAULT 1,
    first_seen    timestamptz NOT NULL DEFAULT now(),
    last_seen     timestamptz NOT NULL DEFAULT now(),
    UNIQUE (user_id, content_id, goal_id)
);
CREATE INDEX IF NOT EXISTS verdicts_session_id_idx ON verdicts (session_id);
-- HNSW = graph index for fast nearest-neighbour search on the combined vector.
-- vector_ip_ops = inner product, which equals cosine for unit-length vectors.
CREATE INDEX IF NOT EXISTS verdicts_combined_vec_idx ON verdicts USING hnsw (combined_vec vector_ip_ops);

-- Appeals: "I wasn't distracted" and "want it anyway" outcomes.
CREATE TABLE IF NOT EXISTS appeals (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    verdict_id  uuid        NOT NULL REFERENCES verdicts (id) ON DELETE CASCADE,
    kind        text        NOT NULL CHECK (kind IN ('not_distracted', 'want_anyway')),
    won         boolean     NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS appeals_verdict_id_idx ON appeals (verdict_id);

-- Per-day aggregates, kept forever (focus time, blocks, heatmap, ...).
CREATE TABLE IF NOT EXISTS daily_stats (
    user_id        uuid      NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    day            date      NOT NULL,
    focus_min      integer   NOT NULL DEFAULT 0,
    blocks         integer   NOT NULL DEFAULT 0,
    heatmap        integer[] NOT NULL DEFAULT array_fill(0, ARRAY[24]),  -- 24 hourly buckets
    top_sites      jsonb     NOT NULL DEFAULT '{}',
    convince_wins  integer   NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, day)
);
