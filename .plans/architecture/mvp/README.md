# v1 MVP board

The smallest AutopilotFocus a student can use: a **blocking On/Off switch**. Turning it On asks
for a **goal**; while On, pages that don't fit the goal are blocked, with one **"I wasn't distracted"** button.

- **Board:** [autopilot-focus-mvp.excalidraw](autopilot-focus-mvp.excalidraw)
- **Previews:** [previews/](previews/)
- **Source:** [diagrams.py](diagrams.py). Regenerate with `python .plans/architecture/mvp/diagrams.py`.

| # | Frame |
|---|---|
| 1 | MVP — system overview |
| 2 | MVP — Chrome extension |
| 3 | MVP — one page, start to finish |
| 4 | MVP — Python AI service (built) |
| 5 | MVP — goal handling |
| 6 | MVP — build order |

## In the MVP

- **Extension:** popup with an On/Off switch (On asks "What are you working on?"; the goal can be
  edited any time); state kept in chrome.storage, so it survives browser restarts. URL watcher;
  sensitive-page filter; page extractor (+ YouTube fields); block overlay with reason and goal;
  appeal = allow this exact page until blocking is turned Off. No timer.
- **Go API:** `POST /v1/verdict`, forwarding to Python. Sign-in + Postgres come at the end of v1.
- **Python AI service:** already built: LLM summary → embedding match → LLM judge for unclear pages.
  If no LLM answers, the page is allowed and rechecked later.

## Parked (designs kept)

Focus modes (Timed, Continuous, Cycles), Smart Focus, Convince Me, dot challenge, feed cleanup, analytics, music,
goal lists and goal checks, closest-case search, floating prompt, FAISS, pgvector,
basic mode (no-LLM fallback, code saved in [../future/basic-mode/](../future/basic-mode/)).
The full design is in [../diagrams.py](../diagrams.py) and the specs in `.plans/`.
