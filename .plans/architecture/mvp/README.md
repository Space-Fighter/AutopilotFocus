# v1 MVP board

The smallest AutopilotFocus a student can use: a **timed focus session** with a **typed goal**,
AI blocking of pages that don't fit the goal, and one **"I wasn't distracted"** button.

- **Board:** [autopilot-focus-mvp.excalidraw](autopilot-focus-mvp.excalidraw)
- **Previews:** [previews/](previews/)
- **Source:** [diagrams.py](diagrams.py). Regenerate with `python .plans/architecture/mvp/diagrams.py`.

| # | Frame |
|---|---|
| 1 | MVP — system overview |
| 2 | MVP — Chrome extension |
| 3 | MVP — one page, start to finish |
| 4 | MVP — Python AI service (built) |
| 5 | MVP — build order |

## In the MVP

- **Extension:** popup to start a timed session and type a goal; URL watcher; sensitive-page filter;
  page extractor (+ YouTube fields); block overlay with reason and goal; appeal = allow this exact page
  for the rest of the session.
- **Go API:** `POST /v1/verdict`, forwarding to Python. Sign-in + Postgres come at the end of v1.
- **Python AI service:** already built: LLM summary → embedding match → LLM judge for unclear pages.
  If no LLM answers, the page is allowed and rechecked later.

## Parked (designs kept)

Other focus modes, Smart Focus, Convince Me, dot challenge, feed cleanup, analytics, music,
goal lists and goal checks, closest-case search, floating prompt, FAISS, pgvector,
basic mode (no-LLM fallback, code saved in [../future/basic-mode/](../future/basic-mode/)).
The full design is in [../diagrams.py](../diagrams.py) and the specs in `.plans/`.
