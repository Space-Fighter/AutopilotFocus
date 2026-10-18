---
name: excalidraw-architecture
description: Create, update and store the project's architecture diagrams and planned schematics as one Excalidraw drawing sheet (docs/architecture/autopilot-focus.excalidraw). Use when the user asks for architecture diagrams, schematics, system/subsystem/module visuals, data flows, sequence diagrams, database schema pictures, state machines, or the AI agent's decision logic and conditionals; and whenever the spec or architecture changes so the diagrams need to follow. Also use to show, render or explain an existing diagram.
---

# Excalidraw architecture sheet

All architecture diagrams live on **one Excalidraw canvas** (a "drawing sheet")
with one **frame per subsystem or view**, laid out left→right in rows. The board is
generated from Python so it stays in sync with the spec, and anything a person
draws by hand on the board is preserved across regenerations.

## Files

| Path | What it is |
|---|---|
| `docs/architecture/diagrams.py` | **Source of truth.** One `with S.frame(...)` block per frame. |
| `docs/architecture/autopilot-focus.excalidraw` | Generated board. Open in VS Code (Excalidraw extension) or excalidraw.com. |
| `docs/architecture/previews/NN-*.png` | Rendered previews, one per frame, plus `00-sheet.png`. |
| `.claude/skills/excalidraw-architecture/scripts/excal.py` | Drawing library (`Sheet`). |
| `.claude/skills/excalidraw-architecture/scripts/render.py` | PNG renderer / local viewer. |
| `.claude/skills/excalidraw-architecture/assets/viewer.html` | Excalidraw viewer used by the renderer. |
| `.plans/*-spec.md` | The spec the diagrams must reflect. |

## Workflow

1. **Read** the relevant spec section and `docs/architecture/diagrams.py`. Diagrams
   must reflect decided facts; anything the spec marks *Proposed* is drawn with
   `S.proposed(...)` (dashed, "(proposed)"). Never invent components.
2. **Edit** `diagrams.py` with the Edit tool:
   - changing a subsystem → edit its frame block;
   - a new subsystem/module/flow → add a new `with S.frame(...)` block **at the end**
     (frame numbers come from order; appending keeps existing numbers stable).
3. **Regenerate:** `python docs/architecture/diagrams.py`
4. **Render:** `python .claude/skills/excalidraw-architecture/scripts/render.py docs/architecture/autopilot-focus.excalidraw [--frames 3,14]`
   (needs Edge or Chrome and internet; ~2 s per frame).
5. **Look at every changed preview** with the Read tool. Fix overlaps, arrows
   crossing boxes, labels sitting on lines, boxes spilling outside the frame.
   Iterate until clean — do not report a diagram you have not looked at.
6. **Report** which frames changed and link the previews. Mention any spec gap you
   found (something the diagram needed that the spec does not decide).

To let the user browse interactively: `render.py BOARD --serve` prints a local URL
(edits there are not saved). For editing, recommend the VS Code extension
"Excalidraw" (pomdtr.excalidraw-editor) or excalidraw.com.

## Library cheat-sheet (`excal.py`)

Coordinates inside a frame are **local** (0,0 = frame top-left). Keys are short
names unique within the frame; arrows refer to keys (`"api"`) or, across frames,
`"frame.key"`.

```python
with S.frame("backend", "Backend services", 2340, 1560, "one-line subtitle"):
    S.zone("go", x, y, w, h, "Go API", "cyan")            # dashed group outline + title
    S.box("api", x, y, w, h, "Go API\nauth · limits", "cyan")      # rectangle
    S.box("d1", x, y, 260, 130, "Cache hit?", "blue", shape="diamond")
    S.box("s", x, y, 200, 90, "Idle", "gray", shape="ellipse")
    S.proposed("caddy", x, y, w, h, "Caddy", "cyan")      # dashed + "(proposed)"
    S.cylinder("pg", x, y, 260, 160, "Postgres")          # data store
    S.table("users", x, y, "users", ["id  uuid PK", ...])  # SQL table
    S.note("n", x, y, w, h, "Title\n• bullet", "yellow")  # sticky note
    S.lifeline("go", x, y, 260, 1000, "Go API", "cyan")   # sequence participant → returns center x
    S.message(x1, x2, y, "1. call", style="dashed")        # sequence message
    S.text(x, y, "free text", 18)
    S.arrow("a", "b", "label", style="dashed", both=True, offset=-24, via=[(x, y), ...])
S.save(OUT)
```

## Conventions

- **Colors mean something** (same across all frames): blue = Chrome extension,
  cyan = Go API / infra, yellow = Python AI / LLM work, violet = data stores,
  gray = external / neutral, red = block / security / errors, green = allow /
  success, pink = user-facing prompts.
- Every frame has a title and a one-line subtitle saying what the view is for.
- Shapes: diamond = decision, ellipse = start/end or state, cylinder = store,
  dashed box = proposed or later phase, dashed arrow = background / fallback.

## Layout rules (learned the hard way)

- Leave **≥ 120 px** between boxes joined by a labelled arrow; labels need room.
- Two opposite arrows between the same pair: `offset=-24` on both (state machines);
  vertical pairs with labels: `offset=-40`.
- Route long arrows with `via` waypoints through **empty corridors** (gaps between
  columns/rows). Never let two routed arrows share a corridor; keep ≥ 30 px apart.
- An arrow's label sits on its **longest segment** — if two routes' long segments
  are near each other, drop one label (``""``) rather than overlap.
- Keep frames ≤ ~2400 px wide; split a crowded view into two frames instead.
- Edit `diagrams.py` with the Edit tool or a Python script file. Do **not** pipe
  replacement code through shell heredocs: they turn `\n` escapes into real
  newlines and break the string literals.

## Hand-drawn edits

Generated elements carry `customData.generated = true`. On save, elements without
that flag (drawn by a person in Excalidraw) are kept. Moving or retyping a
*generated* element by hand is overwritten on the next regeneration — tell the
user to request the change (so it goes into `diagrams.py`) or to draw additions as
new elements.
