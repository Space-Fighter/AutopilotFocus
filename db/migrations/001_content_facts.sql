-- 001: shared summary cache (full board frame 10 "content_facts"; frame 14 steps 4a and 5).
-- Owned by these SQL migrations. The Python and Go ORMs only map to it; they never create or alter it.

-- Turns on pgvector (adds the "vector" column type).
CREATE EXTENSION IF NOT EXISTS vector;

-- One row per described page. Shared by all users: it says what a page IS, never a verdict.
CREATE TABLE IF NOT EXISTS content_facts (
    id           bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- 64-bit: doubles as the FAISS ID
    content_key  text        NOT NULL UNIQUE,     -- "youtube:<video id>" or the normalized URL
    summary      text        NOT NULL,            -- ContentFacts.summary (written by the LLM)
    topics       text[]      NOT NULL DEFAULT '{}',
    kind         text        NOT NULL,
    page_vec     vector(384) NOT NULL,            -- embedding of the page's own text: what FAISS searches
    summary_vec  vector(384) NOT NULL,            -- embedding of the summary: reused on a cache hit
    created_at   timestamptz NOT NULL DEFAULT now()
);
