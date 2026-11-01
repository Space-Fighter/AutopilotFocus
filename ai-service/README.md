# AutopilotFocus AI service (Python)

Judges whether a page serves the user's current goal. Board frame 3 (orange box) and the
bottom half of frame 5.

```
PageData --describe_content--> ContentFacts --match--> related / unrelated / unclear
                                                            |                  |
                                                         Verdict      judge (LLM) -> Verdict
```

## Setup

```bash
uv sync
cp .env.example .env   # then add at least one API key
```

## Functions to write, in order

| # | File | Function | Concept |
|---|------|----------|---------|
| 1 | `embedder.py` | `embed`, `cosine` | Embeddings and similarity |
| 2 | `matcher.py` | `facts_text`, `goal_text`, `match` | Thresholds: the cheap first pass |
| 3 | `llm.py` | `ProviderChain.complete_json` | Calling an LLM, JSON output, fallback chain |
| 4 | `describer.py` | prompt, `build_describe_prompt`, `describe_content` | Prompting for structured output |
| 5 | `judge.py` | prompt, `judge` | LLM as a judge |
| 6 | `pipeline.py` | `classify` | Workflow: code decides the steps |
| 7 | `page_identity.py` | `content_key` | Exact identity of a page (cache key) |
| 8 | `summary_index.py` | `SummaryIndex.add`, `search` | FAISS: vector search with your own IDs |
| 9 | `facts_cache.py` | `get_facts` | Cache-aside: exact key → FAISS → LLM → save |
| 10 | `matcher.py` | `GoalVectors.get` | Memoizing: embed a goal once |

Needs Postgres for the cache: from the repo root, `docker compose up -d`, then run the
migrations (see `db/README.md`).

## Run

```bash
uv run python eval/run_eval.py                    # Step 0: accuracy test
uv run uvicorn ai_service.api:app --port 8001     # Step 1: HTTP service for the Go API
```

Not built yet (later steps): content-facts cache, FAISS / pgvector, appeal and Convince Me judges,
topic signals for Smart Focus.
