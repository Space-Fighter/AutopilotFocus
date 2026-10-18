# Architecture diagrams

One Excalidraw drawing sheet with every AutopilotFocus schematic, one frame per view.

- **Board:** [autopilot-focus.excalidraw](autopilot-focus.excalidraw). Open it with the VS Code
  "Excalidraw" extension (pomdtr.excalidraw-editor) or drag it onto excalidraw.com.
- **Previews:** [previews/](previews/) has one PNG per frame.
- **Source:** [diagrams.py](diagrams.py) generates the board from code. Run `python docs/architecture/diagrams.py`.
- **Skill:** `.claude/skills/excalidraw-architecture/` holds the drawing library, the renderer, and the agent instructions.

| # | Frame |
|---|---|
| 1 | System overview |
| 2 | Chrome extension internals |
| 3 | Backend services |
| 4 | Verdict request — sequence |
| 5 | AI agent — verdict pipeline |
| 6 | Block screen — appeal & Convince Me |
| 7 | Focus modes & session state machine |
| 8 | Smart Focus engine |
| 9 | Goal & intent capture |
| 10 | Database schema (Postgres) |
| 11 | Privacy & data lifecycle |
| 12 | Deployment — one VPS |
| 13 | Roadmap & phases |
| 14 | Python AI service — page to verdict |

Dashed boxes are components the spec still marks as *Proposed*, or ones planned for later phases.
Anything you draw by hand on the board is kept when the board is regenerated. Changes to the generated
shapes belong in `diagrams.py`.
