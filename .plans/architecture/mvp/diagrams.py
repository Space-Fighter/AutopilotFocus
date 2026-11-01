"""AutopilotFocus v1 MVP board (Excalidraw).

The smallest product a student can use: an On/Off switch, a typed goal, AI blocking, one appeal button.
Everything else is parked (see ../diagrams.py for the full design).

Regenerate:  python .plans/architecture/mvp/diagrams.py
Previews:    python .claude/skills/excalidraw-architecture/scripts/render.py .plans/architecture/mvp/autopilot-focus-mvp.excalidraw
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "excalidraw-architecture", "scripts"))
from excal import Sheet, MUTED  # noqa: E402

S = Sheet()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "autopilot-focus-mvp.excalidraw")


# ------------------------------------------------------------------------ 1
with S.frame("overview", "MVP — system overview", 2000, 1000,
             "Three parts, one job: while blocking is On, block pages that don't fit the goal. Dashed = later in v1."):
    S.box("student", 40, 450, 140, 80, "Student", "gray", shape="ellipse")

    S.zone("ext", 230, 190, 420, 640, "Chrome extension (WXT · React · TS)", "blue")
    S.box("popup", 270, 240, 340, 110, "Popup\nOn / Off switch\nOn → type goal", size=16)
    S.box("sw", 270, 450, 340, 100, "Service worker\nOn/Off state · API calls", size=16)
    S.box("cs", 270, 660, 340, 120, "Content script\nextract page · block overlay\n\"I wasn't distracted\"", size=16)

    S.zone("vps", 740, 190, 760, 640, "VPS · Docker Compose", "cyan")
    S.box("go", 790, 450, 280, 100, "Go API\nPOST /v1/verdict", "cyan", size=16)
    S.box("py", 1170, 450, 290, 100, "Python AI service\nPOST /v1/classify", "yellow", size=16)
    S.proposed("auth", 790, 650, 280, 110, "Sign-in + Postgres\n(later in v1)", "cyan", size=15)

    S.zone("llm", 1600, 300, 340, 380, "LLM providers", "gray")
    S.box("prov", 1640, 380, 260, 220, "providers.toml\nGroq → Gemini\n→ OpenAI", "gray", size=16)

    S.arrow("student", "popup", "")
    S.arrow("popup", "sw", "start · goal")
    S.arrow("cs", "sw", "page data", both=True)
    S.arrow("sw", "go", "HTTPS")
    S.arrow("go", "py", "HTTP/JSON")
    S.arrow("py", "prov", "")
    S.arrow("go", "auth", "", style="dashed")
    S.text(40, 900, "Not in the MVP: other focus modes, Smart Focus, Convince Me, dot challenge, feed cleanup, analytics, "
           "music, goal lists, closest-case search, FAISS / pgvector.", 16, color=MUTED)


# ------------------------------------------------------------------------ 2
with S.frame("ext", "MVP — Chrome extension", 2100, 1180,
             "Only what the On/Off switch needs. The service worker can be stopped by Chrome, so On/Off and the goal live in chrome.storage (they survive restarts)."):
    S.zone("page", 40, 180, 640, 920, "Inside the page (content script)", "blue")
    S.box("url", 80, 240, 260, 90, "URL-change watcher\nincl. YouTube navigation", size=15)
    S.box("sens", 80, 420, 260, 100, "Sensitive-page filter\npw / card fields\nbank & checkout", "red", size=15)
    S.box("extract", 400, 420, 240, 100, "Page extractor\ntitle · meta · headings\n+ YouTube fields", size=15)
    S.box("overlay", 80, 660, 560, 130, "Block overlay\n\"Caught you slopping\"\nreason + goal · [I wasn't distracted]", "red", size=16)
    S.box("allowed", 80, 920, 560, 100, "Allowed pages until turned Off\n(appeal = allow this exact page)", "green", size=15)

    S.zone("bg", 780, 180, 620, 920, "Service worker", "blue")
    S.box("sm", 820, 240, 540, 100, "Blocking: Off / On\ngoal (set when turned On)", size=16)
    S.cylinder("store", 960, 410, 250, 140, "chrome.storage\non/off · goal · allowed")
    S.box("client", 820, 660, 540, 110, "API client\nonly while blocking is On\nonly for the active tab", "cyan", size=15)

    S.zone("ui", 1500, 180, 560, 920, "Popup (React)", "blue")
    S.box("pop", 1540, 240, 480, 160, "On / Off switch\nturning On asks \"What are\nyou working on?\" · edit goal", size=16)
    S.box("api", 1540, 660, 480, 110, "Go API (VPS)", "cyan", size=16)

    S.arrow("url", "sens", "navigation")
    S.arrow("sens", "extract", "")
    S.arrow("extract", "client", "page data (safe pages only)", via=[(720, 470), (720, 600), (1090, 600)])
    S.arrow("client", "overlay", "block + reason", color="red")
    S.arrow("overlay", "allowed", "appeal")
    S.arrow("pop", "sm", "on / off")
    S.arrow("sm", "store", "", both=True)
    S.arrow("client", "api", "HTTPS")


# ------------------------------------------------------------------------ 3
with S.frame("seq", "MVP — one page, start to finish", 2300, 1140,
             "What happens when the student opens a page while blocking is On. The page shows at once; the overlay appears if it's blocked."):
    xs = {}
    for key, x, label, color in [("cs", 120, "Content script", "blue"), ("sw", 520, "Service worker", "blue"),
                                 ("go", 920, "Go API", "cyan"), ("py", 1320, "Python AI", "yellow"),
                                 ("llm", 1720, "LLM provider", "gray")]:
        xs[key] = S.lifeline(key, x, 160, 300, 900, label, color)
    S.message(xs["cs"], xs["sw"], 300, "1. page data (sensitive check passed)")
    S.message(xs["sw"], xs["go"], 380, "2. POST /v1/verdict  {page, goal}")
    S.message(xs["go"], xs["py"], 460, "3. POST /v1/classify  {page, goal}")
    S.message(xs["py"], xs["llm"], 540, "4. describe page → summary")
    S.message(xs["llm"], xs["py"], 620, "5. summary", style="dashed")
    S.box("pnote", xs["py"] - 170, 680, 340, 110, "embedding match vs goal\njudge (LLM) only if unclear\nLLM fails → allow + recheck", "yellow", size=15)
    S.message(xs["py"], xs["go"], 840, "6. verdict + reason", style="dashed")
    S.message(xs["go"], xs["sw"], 920, "7. verdict", style="dashed")
    S.message(xs["sw"], xs["cs"], 1000, "8. block → show overlay", style="dashed")


# ------------------------------------------------------------------------ 4
with S.frame("py", "MVP — Python AI service (built)", 2320, 1000,
             "Already working in ai-service/. Dashed = later: the FAISS summary cache (saves LLM calls) and the no-LLM fallback."):
    S.box("in", 60, 220, 240, 90, "page + goal", "gray", shape="ellipse", size=16)
    S.box("fs", 400, 180, 280, 170, "Similar page\nalready described?\nFAISS (later)", "blue", shape="diamond", style="dashed", size=14)
    S.box("reuse", 400, 450, 280, 100, "Reuse its saved\nsummary\n(Postgres, later)", "violet", style="dashed", size=15)
    S.box("desc", 820, 210, 340, 110, "Describer (LLM)\npage → summary\ndescriber.py", "yellow", size=15)
    S.box("m1", 860, 440, 280, 160, "Embedding match\nvs goal\nmatcher.py", "violet", shape="diamond", size=15)
    S.box("ok1", 1320, 420, 220, 80, "ALLOW", "green", size=18)
    S.box("bl1", 1320, 560, 220, 80, "BLOCK", "red", size=18)
    S.box("judge", 840, 740, 320, 100, "LLM judge (unclear only)\njudge.py", "yellow", size=15)
    S.box("jout", 1320, 750, 220, 80, "ALLOW / BLOCK", "gray", size=16)
    S.box("fail", 1320, 220, 300, 90, "No LLM answered →\nallow + recheck later", "green", style="dashed", size=15)

    S.arrow("in", "fs")
    S.arrow("fs", "desc", "not found\n(MVP: always)")
    S.arrow("fs", "reuse", "found", style="dashed")
    S.arrow("reuse", "m1", "", style="dashed")
    S.arrow("desc", "m1", "summary")
    S.arrow("desc", "fail", "fails", style="dashed", color="red")
    S.arrow("m1", "ok1", "related")
    S.arrow("m1", "bl1", "unrelated")
    S.arrow("m1", "judge", "unclear")
    S.arrow("judge", "jout", "")
    S.note("files", 1700, 400, 560, 360,
           "Files (ai-service/)\n• pipeline.py: the flow\n• describer.py\n• matcher.py + embedder.py\n"
           "• judge.py + llm.py (Groq → Gemini → OpenAI)\n• api.py: HTTP for Go\n• eval/: accuracy test\n\n"
           "Later: FAISS summary cache (full board\nframe 14, steps 2–5) · basic mode", "yellow", size=16)


# ------------------------------------------------------------------------ 5
with S.frame("plan", "MVP — build order", 2200, 760,
             "Get one real page blocked end to end first, then make it nicer. Each step ends with something you can try."):
    steps = [
        ("s1", "1. Python service\n✓ done", "green"),
        ("s2", "2. Go API\nPOST /v1/verdict\n→ Python", "cyan"),
        ("s3", "3. Extension\nextract → API →\noverlay", "blue"),
        ("s4", "4. On/Off switch\npopup + goal", "blue"),
        ("s5", "5. Appeal button\n+ sensitive filter", "blue"),
        ("s6", "6. Sign-in +\nPostgres\n+ deploy to VPS", "cyan"),
    ]
    x = 60
    for i, (key, label, color) in enumerate(steps):
        S.box(key, x, 220, 280, 140, label, color, size=16)
        if i:
            S.arrow(steps[i - 1][0], key, "")
        x += 350
    S.note("try", 60, 470, 1000, 220,
           "Milestone after step 3: open a YouTube gaming video with goal\n\"studying biology\" and see \"Caught you slopping\".\n"
           "Milestone after step 6: a friend installs it and uses it for a real study session.", "yellow", size=17)
    S.note("parked", 1160, 470, 980, 220,
           "Parked (designs kept in .plans/):\nother focus modes · Smart Focus · Convince Me · dot challenge\n"
           "feed cleanup · analytics · music · goal lists + goal checks\nclosest-case search · floating prompt · FAISS · pgvector", "gray", size=17)

# ------------------------------------------------------------------------ 6
with S.frame("goal", "MVP — goal handling", 2200, 900,
             "One goal while blocking is On, typed by the student. No goal list, no goal checks yet."):
    S.box("pop", 60, 220, 360, 120, "Popup: turn blocking On\n→ \"What are you\nworking on?\" (required)", "pink", size=16)
    S.box("store", 540, 220, 360, 120, "Current goal\nchrome.storage\n(until turned Off)", "violet", size=16)
    S.box("req", 1020, 220, 360, 120, "Sent with every\nverdict request\n{page, goal}", "cyan", size=16)
    S.box("py", 1500, 220, 360, 120, "Python: embedding match\n+ LLM judge use this goal", "yellow", size=16)
    S.box("edit", 540, 500, 360, 110, "Edit goal in the popup\nany time → next pages\nuse the new goal", "pink", size=16)
    S.box("ov", 1020, 500, 360, 110, "Block overlay shows it:\n\"… isn't part of: <goal>\"", "red", size=16)

    S.arrow("pop", "store", "")
    S.arrow("store", "req", "")
    S.arrow("req", "py", "")
    S.arrow("edit", "store", "")
    S.arrow("py", "ov", "block + reason", via=[(1680, 555)])
    S.note("later", 60, 700, 1300, 140,
           "Later (full board frame 9): saved goal list · onboarding goals · general goal (safe categories)\n"
           "LLM goal check · inferred goals for auto-started sessions · topic-shift prompt · edit goal from the block screen", "gray", size=16)


S.save(OUT)
