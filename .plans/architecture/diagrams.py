"""AutopilotFocus architecture drawing set (Excalidraw).

Source of truth for docs/architecture/autopilot-focus.excalidraw.
Regenerate:  python docs/architecture/diagrams.py
Previews:    python .claude/skills/excalidraw-architecture/scripts/render.py docs/architecture/autopilot-focus.excalidraw

Content follows .plans/autopilot-focus-v1-spec.md. Components the spec marks
"Proposed" are drawn dashed with "(proposed)".
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "excalidraw-architecture", "scripts"))
from excal import Sheet, MUTED  # noqa: E402

S = Sheet()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "autopilot-focus.excalidraw")


# ------------------------------------------------------------------------ 1
with S.frame("overview", "System overview", 2040, 1020,
             "v1 = standalone Chrome extension + backend on one VPS. Gymodoro sync is a later phase."):
    S.box("student", 40, 470, 130, 80, "Student", "gray", shape="ellipse")

    S.zone("ext", 210, 190, 400, 690, "Chrome extension (WXT · React · TS)", "blue")
    S.box("cs", 250, 240, 320, 110, "Content scripts\nextract · sensitive filter\nfeed cleanup · overlay")
    S.box("sw", 250, 470, 320, 90, "Service worker\nsessions · alarms · API")
    S.box("ui", 250, 690, 320, 100, "Popup · Side panel\nDashboard")

    S.zone("vps", 690, 190, 930, 690, "VPS · Docker Compose", "cyan")
    S.proposed("caddy", 730, 240, 260, 100, "Caddy · HTTPS", "cyan")
    S.box("api", 730, 470, 260, 90, "Go API\nauth · limits · history", "cyan")
    S.box("ai", 1110, 470, 290, 90, "Python AI service\nembed · match · LLM chain", "yellow")
    S.cylinder("pg", 740, 670, 240, 150, "Postgres\nusers · verdicts\naggregates")
    S.cylinder("fx", 1130, 670, 250, 150, "FAISS index\nin-memory", "yellow")
    S.box("vol", 1440, 700, 160, 90, "Docker\nvolume", "gray")

    S.zone("llm", 1710, 290, 290, 460, "LLM providers (free tiers)", "gray")
    S.box("la", 1745, 340, 220, 70, "1 · Provider A", "gray")
    S.box("lb", 1745, 480, 220, 70, "2 · Provider B", "gray")
    S.box("lc", 1745, 620, 220, 70, "3 · Provider C", "gray")
    S.box("gym", 1710, 830, 290, 80, "Gymodoro\n(much later)", "gray", style="dashed")

    S.arrow("student", "ui", "starts focus")
    S.arrow("cs", "sw", "page data")
    S.arrow("sw", "ui", "state", both=True)
    S.arrow("sw", "caddy", "HTTPS + JWT")
    S.arrow("caddy", "api", "proxy")
    S.arrow("api", "ai", "HTTP/JSON")
    S.arrow("api", "pg", "SQL", both=True)
    S.arrow("ai", "fx", "k-NN", both=True)
    S.arrow("ai", "pg", "content facts", style="dashed")
    S.arrow("fx", "vol", "snapshot")
    S.arrow("ai", "la", "fallback chain", style="dashed")
    S.arrow("la", "lb", "quota hit")
    S.arrow("lb", "lc", "quota hit")
    S.arrow("api", "gym", "sync (later)", style="dashed", via=[(1055, 600), (1055, 935)])
    S.text(40, 950, "Legend: solid = runtime request · dashed arrow = background/fallback · dashed box = proposed or later · cylinder = data store",
           16, color=MUTED)


# ------------------------------------------------------------------------ 2
with S.frame("ext", "Chrome extension internals", 2320, 1420,
             "Manifest V3. Content scripts run inside each page; the service worker is the brain and may be stopped by Chrome at any time."):
    S.zone("page", 40, 200, 620, 1100, "Inside the web page (content scripts)", "blue")
    S.box("url", 80, 250, 250, 90, "URL-change watcher\nincl. SPA navigation", size=16)
    S.box("sens", 80, 420, 250, 100, "Sensitive-page filter\npw / card fields\nbank & checkout", "red", size=16)
    S.box("extract", 380, 420, 240, 100, "Page extractor\ntitle · meta · headings\nvisible text", size=16)
    S.box("ytp", 380, 600, 240, 100, "YouTube parser\ntags · channel\ncategory · captions", size=16)
    S.box("feed", 80, 780, 540, 110, "Feed cleanup (Unhook-style)\nYT Shorts (always) · home · sidebar\nInstagram · X · Reddit feeds", size=16)
    S.proposed("selectors", 80, 930, 540, 80, "Remote selector config", size=15)
    S.box("overlay", 80, 1100, 540, 110, "Block overlay\n\"Caught you slopping\" · appeal box\ndot challenge · Convince Me link", "red", size=16)

    S.zone("bg", 760, 200, 720, 1100, "Background service worker", "blue")
    S.box("router", 800, 250, 640, 90, "Message router (chrome.runtime)")
    S.box("sm", 800, 440, 300, 100, "Session state machine\n4 focus modes")
    S.box("alarms", 1140, 440, 300, 100, "chrome.alarms\nfocus / break timers")
    S.box("smart", 800, 640, 300, 100, "Smart Focus\nsignal collector")
    S.box("notif", 1140, 640, 300, 100, "chrome.notifications\nauto-start · suggest")
    S.cylinder("store", 800, 860, 300, 160, "chrome.storage.local\nsession · settings")
    S.box("vcache", 1140, 880, 300, 100, "Local verdict cache\n(per page key)")
    S.box("client", 1140, 1110, 300, 100, "API client\nJWT · retries", "cyan")

    S.zone("uiz", 1580, 200, 700, 1100, "Extension UI (React)", "blue")
    S.box("popup", 1620, 250, 300, 110, "Toolbar popup\nstart · pause · timer\n\"this was a distraction\"", size=16)
    S.box("onb", 1950, 250, 300, 110, "Onboarding\nsign-in · profile\nhours · mode · demo", "pink", size=16)
    S.box("side", 1620, 460, 300, 120, "Side panel\ngoal chat · topic-shift\nConvince Me chat", size=16)
    S.box("dash", 1620, 680, 300, 130, "Dashboard page\nanalytics · settings\nactivity log\nfeed toggles", size=16)
    S.box("backend", 1950, 1115, 300, 90, "Go API (VPS)", "cyan")

    S.arrow("url", "sens", "navigation")
    S.arrow("sens", "extract", "safe page")
    S.arrow("extract", "ytp", "youtube.com")
    S.arrow("extract", "router", "page data")
    S.arrow("ytp", "router", "metadata", via=[(690, 650), (690, 320)])
    S.arrow("router", "sm", "commands", both=True)
    S.arrow("sm", "alarms", "schedule", both=True)
    S.arrow("smart", "sm", "start / suggest")
    S.arrow("sm", "notif", "notify")
    S.arrow("sm", "store", "", via=[(780, 490), (780, 940)])
    S.arrow("router", "client", "verdict request", via=[(1465, 295), (1465, 1160)])
    S.arrow("client", "vcache", "cache", both=True)
    S.arrow("router", "overlay", "show block", color="red", via=[(735, 295), (735, 1155)])
    S.arrow("client", "backend", "HTTPS + JWT")
    S.arrow("popup", "router", "chrome.runtime messages")
    S.arrow("side", "router", "", via=[(1560, 520), (1560, 320)])
    S.arrow("dash", "router", "", via=[(1590, 745), (1590, 330)])
    S.arrow("selectors", "feed", "update", style="dashed")


# ------------------------------------------------------------------------ 3
with S.frame("backend", "Backend services", 2340, 1560,
             "Only Caddy is public. Go owns users, limits and history; Python owns everything AI."):
    S.box("ext", 40, 620, 220, 90, "Extension", "blue")
    S.proposed("caddy", 330, 610, 230, 110, "Caddy\nTLS · reverse proxy", "cyan", size=16)

    S.zone("go", 650, 200, 660, 1000, "Go API", "cyan")
    S.box("mw", 690, 250, 280, 110, "HTTP router\nJWT middleware", "cyan", size=16)
    S.box("verdict", 1000, 250, 280, 110, "POST /v1/verdict\nquota · personal cache", "cyan", size=16)
    S.box("auth", 690, 440, 280, 110, "Auth\nGoogle OAuth · email/pw\nJWT (proposed)", "cyan", size=16)
    S.box("appeal", 1000, 440, 280, 110, "POST /v1/appeal\nPOST /v1/convince", "cyan", size=16)
    S.box("meter", 690, 620, 280, 110, "Limits & metering\ndaily free AI-check cap\npremium flag", "cyan", size=16)
    S.box("sessions", 1000, 620, 280, 110, "Sessions & goals\n/v1/sessions", "cyan", size=16)
    S.box("agg", 690, 820, 280, 100, "Nightly aggregation\nraw → daily_stats", "cyan", size=16)
    S.box("purge", 1000, 820, 280, 100, "Retention job\ndelete raw > 30 days", "red", size=16)
    S.box("stats", 690, 1020, 280, 100, "Stats & activity log\n/v1/stats · /v1/log", "cyan", size=16)
    S.proposed("delete", 1000, 1020, 280, 100, "Delete-my-data\nendpoint", "cyan", size=16)

    S.zone("py", 1400, 200, 620, 1000, "Python AI service", "yellow")
    S.box("desc", 1440, 250, 260, 100, "Content describer\nLLM → short facts", "yellow", size=16)
    S.proposed("embed", 1730, 250, 260, 100, "Embedder\nbge-small, CPU", "yellow", size=16)
    S.box("fmgr", 1440, 440, 260, 100, "FAISS manager\nsearch · add", "yellow", size=16)
    S.box("match", 1730, 440, 260, 100, "Goal matcher\nsimilarity thresholds", "yellow", size=16)
    S.box("judge", 1440, 620, 260, 120, "Judges\nverdict · appeal\nConvince Me personas", "yellow", size=16)
    S.box("topic", 1730, 620, 260, 120, "Topic signals\ntopic shift · Smart\nconsistency", "yellow", size=16)
    S.box("chain", 1440, 830, 550, 100, "LLM provider chain (used by describer & judges)\nA → B → C when a quota runs out", "yellow", size=16)
    S.proposed("snap", 1440, 1020, 550, 100, "Index rebuild from Postgres on boot + disk snapshots", "yellow", size=16)

    S.cylinder("pg", 800, 1310, 300, 170, "Postgres")
    S.cylinder("fvol", 1560, 1310, 300, 170, "faiss volume", "gray")
    S.box("prov", 2090, 830, 220, 100, "LLM provider\nAPIs", "gray", shape="ellipse")

    S.arrow("ext", "caddy", "HTTPS")
    S.arrow("caddy", "mw", "/v1/*")
    S.arrow("mw", "verdict", "route")
    S.arrow("mw", "auth", "login")
    S.arrow("verdict", "match", "HTTP/JSON", via=[(1350, 305), (1350, 395), (1860, 395)])
    S.arrow("appeal", "judge", "HTTP/JSON", via=[(1370, 495), (1370, 680)])
    S.arrow("sessions", "topic", "goal text", via=[(1340, 675), (1340, 785), (1860, 785)])
    S.arrow("match", "fmgr", "k-NN")
    S.arrow("desc", "embed", "embed")
    S.arrow("match", "judge", "unclear", via=[(1860, 585), (1570, 585)])
    S.arrow("judge", "chain")
    S.arrow("chain", "prov", "API calls")
    S.arrow("fmgr", "snap", "", style="dashed", via=[(1420, 490), (1420, 1070)])
    S.arrow("snap", "fvol", "write")
    S.arrow("snap", "pg", "read facts", style="dashed", via=[(1480, 1250), (1100, 1250)])
    S.arrow("agg", "pg", "SQL", via=[(670, 870), (670, 1395)])
    S.arrow("purge", "pg", "DELETE", via=[(1295, 870), (1295, 1395)])
    S.arrow("stats", "pg", "")
    S.arrow("delete", "pg", "", style="dashed")


# ------------------------------------------------------------------------ 4
with S.frame("seq", "Verdict request — sequence", 2320, 1260,
             "Cache miss path. The page is already visible; the block screen appears when the verdict returns."):
    cols = {}
    for i, (k, label, col) in enumerate([("cs", "Content script", "blue"), ("sw", "Service worker", "blue"),
                                          ("go", "Go API", "cyan"), ("pg", "Postgres", "violet"),
                                          ("py", "Python AI", "yellow"), ("llm", "LLM provider", "gray")]):
        cols[k] = S.lifeline(k, 80 + i * 370, 160, 260, 1000, label, col)
    msgs = [
        ("cs", "sw", "page data (sensitive check passed)", "solid"),
        ("sw", "go", "POST /v1/verdict + JWT", "solid"),
        ("go", "pg", "quota left? personal cache?", "solid"),
        ("pg", "go", "ok · miss", "dashed"),
        ("go", "py", "classify(content, goal)", "solid"),
        ("py", "pg", "content_facts by key / FAISS", "solid"),
        ("pg", "py", "miss", "dashed"),
        ("py", "llm", "describe content", "solid"),
        ("llm", "py", "short description", "dashed"),
        ("py", "pg", "store content_facts (shared)", "solid"),
        ("py", "go", "verdict + reason", "dashed"),
        ("go", "pg", "store verdict · count AI check", "solid"),
        ("go", "sw", "verdict", "dashed"),
        ("sw", "cs", "show block overlay (if distraction)", "solid"),
    ]
    y = 320
    for i, (a, b, label, style) in enumerate(msgs):
        S.message(cols[a], cols[b], y, f"{i + 1}. {label}", style=style,
                  color="red" if i == len(msgs) - 1 else "ink", key=f"m{i}")
        y += 60
        if i == 9:
            S.note("matchnote", cols["py"] - 150, y - 20, 300, 80,
                   "embedding match vs goal\nLLM judge only if unclear", "yellow", size=15)
            y += 90


# ------------------------------------------------------------------------ 5
with S.frame("pipe", "AI agent — verdict pipeline", 2060, 1640,
             "Runs on every navigation in the active tab while a focus period is active."):
    M = 560
    S.box("n0", M - 20, 130, 300, 70, "URL changes in active tab", "gray", shape="ellipse", size=16)
    S.box("d1", M, 240, 260, 130, "Focus period\nactive?", "blue", shape="diamond", size=16)
    S.box("x1", 80, 270, 240, 70, "Do nothing", "gray", shape="ellipse")
    S.box("d2", M, 420, 260, 130, "Sensitive page?\npw / card / bank", "red", shape="diamond", size=15)
    S.box("a1", 80, 450, 240, 70, "Allow · send nothing", "green", size=16)
    S.box("d3", M, 600, 260, 130, "Personal verdict\ncached?", "blue", shape="diamond", size=15)
    S.box("r1", 80, 630, 240, 70, "Apply cached verdict", "green", size=16)
    S.box("d4", M, 780, 260, 130, "Free cap\nleft?", "blue", shape="diamond", size=16)
    S.box("up", 60, 810, 280, 70, "Basic mode (frame 15)\n+ premium offer", "yellow", size=16)
    S.box("d5", M, 960, 260, 130, "Content facts\ncached?", "blue", shape="diamond", size=15)
    S.box("gen", M + 380, 990, 280, 70, "LLM writes content\ndescription → shared", "yellow", size=16)
    S.box("d6", M, 1140, 260, 130, "Embedding match\nvs goal", "violet", shape="diamond", size=15)
    S.box("ok", 80, 1170, 240, 70, "Allow", "green")
    S.box("jj", M - 10, 1330, 280, 70, "LLM judges\ngoal + description", "yellow", size=16)
    S.box("bl", M + 380, 1320, 300, 90, "BLOCK\n\"Caught you slopping\"", "red", size=18)
    S.box("ap", M + 760, 1200, 320, 80, "Appeal: one-line reason\n(free: uses 1 check)", "gray", size=16)
    S.box("cm", M + 760, 1440, 320, 80, "Dot challenge (free)\nConvince Me (premium)", "gray", size=16)
    S.box("d7", M + 760, 960, 260, 130, "All providers\ndown?", "red", shape="diamond", size=15)
    S.box("tag", M + 380, 1150, 260, 70, "Basic mode (frame 15)\nno LLM", "yellow", size=15)
    S.box("allow2", M + 1100, 990, 260, 70, "Allow · recheck later", "green", size=16)

    for a, b, l in [("n0", "d1", ""), ("d1", "x1", "no"), ("d1", "d2", "yes"), ("d2", "a1", "yes"),
                    ("d2", "d3", "no"), ("d3", "r1", "yes"), ("d3", "d4", "no"), ("d4", "up", "no"),
                    ("d4", "d5", "yes"), ("d5", "gen", "no"), ("d5", "d6", "yes"), ("gen", "d6", ""),
                    ("d6", "ok", "related"), ("d6", "bl", "unrelated"), ("d6", "jj", "unclear"),
                    ("jj", "ok", "on-task"), ("jj", "bl", "distraction"),
                    ("bl", "ap", "wasn't distracted"), ("bl", "cm", "want it anyway"),
                    ("d7", "tag", "yes"), ("d7", "allow2", "no")]:
        S.arrow(a, b, l)
    S.arrow("gen", "d7", "error", style="dashed", color="red")


# ------------------------------------------------------------------------ 6
with S.frame("block", "Block screen — appeal & Convince Me", 2160, 1180,
             "Every outcome is logged: successful appeals are the v1 accuracy metric."):
    S.box("bl", 60, 520, 300, 110, "BLOCK screen\n\"Caught you slopping\"", "red", size=18)
    S.box("says", 450, 505, 260, 140, "User says?", "pink", shape="diamond")

    S.box("reason", 820, 230, 300, 100, "One-line reason\n\"how does this help?\"", "gray", size=16)
    S.box("judge", 1200, 200, 280, 160, "AI judge:\nconvincing?\n(free: 1 check)", "yellow", shape="diamond", size=15)
    S.box("pass", 1600, 160, 300, 100, "Pass for this page\n+ logged correction", "green", size=16)
    S.box("stay1", 1600, 330, 300, 80, "Stays blocked", "red")

    S.box("plan", 820, 790, 260, 140, "Plan?", "blue", shape="diamond")
    S.box("dot", 1200, 680, 300, 110, "Dot challenge\nclick moving dot ~30×", "gray", size=16)
    S.box("cm", 1200, 900, 300, 120, "Convince Me\npersona chat\nsavage · coach · chill", "violet", size=16)
    S.box("cmj", 1580, 880, 300, 160, "Convinced?\nharder after each\nwin today", "yellow", shape="diamond", size=15)
    S.box("timed", 1600, 690, 300, 90, "Timed pass", "green")
    S.box("stay2", 1940, 925, 190, 80, "Stays\nblocked", "red", size=16)

    S.arrow("bl", "says")
    S.arrow("says", "reason", "wasn't distracted")
    S.arrow("reason", "judge")
    S.arrow("judge", "pass", "yes")
    S.arrow("judge", "stay1", "no")
    S.arrow("says", "plan", "want it anyway")
    S.arrow("plan", "dot", "free")
    S.arrow("plan", "cm", "premium")
    S.arrow("dot", "timed", "done")
    S.arrow("cm", "cmj")
    S.arrow("cmj", "timed", "yes")
    S.arrow("cmj", "stay2", "no")
    S.note("rules", 60, 820, 600, 260,
           "Rules\n• Appeal win → pass for that exact page/video\n• Want-it-anyway win → timed pass\n"
           "• Convince Me is premium only (AI cost)\n• Free appeals count toward the daily cap\n"
           "• Instagram / X / Reddit pages unlock the same way", "yellow", size=16)


# ------------------------------------------------------------------------ 7
with S.frame("modes", "Focus modes & session state machine", 2100, 1180,
             "Same detection engine in every mode. State lives in chrome.storage; timers use chrome.alarms."):
    S.box("idle", 80, 420, 200, 100, "Idle", "gray", shape="ellipse", size=22)
    S.box("sugg", 80, 760, 220, 100, "Suggested\n(Smart)", "violet", shape="ellipse")
    S.box("focus", 620, 420, 220, 100, "Focus\nblocking on", "blue", shape="ellipse")
    S.box("paused", 620, 760, 220, 100, "Paused", "yellow", shape="ellipse", size=22)
    S.box("brk", 1120, 420, 220, 100, "Break\nblocking off", "green", shape="ellipse")
    S.arrow("idle", "focus", "start", offset=-26)
    S.arrow("focus", "idle", "timer ends / stop", offset=-26)
    S.arrow("idle", "sugg", "Smart: Suggest First")
    S.arrow("sugg", "focus", "accept")
    S.arrow("sugg", "idle", "dismiss", via=[(30, 810), (30, 470)])
    S.arrow("focus", "paused", "pause", offset=-40)
    S.arrow("paused", "focus", "resume", offset=-40)
    S.arrow("focus", "brk", "focus timer (Cycles)", offset=-26)
    S.arrow("brk", "focus", "break timer", offset=-26)
    S.text(80, 200, "start = manual start in Timed / Continuous / Cycles, or Smart Auto Start (notifies user).\n"
           "Break: AI blocking off, feed cleanup stays on, nudge shortly before break ends.", 18, color=MUTED)

    S.note("m1", 1480, 200, 580, 150, "1 · Timed\nuser sets duration → auto-ends\npause · resume · end early", "blue")
    S.note("m2", 1480, 380, 580, 170, "2 · Continuous (Always On)\nno timer · survives restarts/reboots\ntemporary pause without disabling", "blue")
    S.note("m3", 1480, 580, 580, 150, "3 · Fixed Focus-Break Cycles\ne.g. 25 / 5 · customizable\npause · resume · stop", "blue")
    S.note("m4", 1480, 760, 580, 170, "4 · Smart Focus\nhistory + real-time topic signal\nAuto Start (default) / Suggest First", "violet")


# ------------------------------------------------------------------------ 8
with S.frame("smart", "Smart Focus engine", 2260, 1060,
             "Decides when to start focus. Cold start uses onboarding hours until history builds up."):
    S.box("hours", 60, 230, 320, 100, "Preferred hours\n(onboarding)", "pink")
    S.cylinder("hist", 60, 400, 320, 160, "daily_stats\nhourly heatmap")
    S.box("rt", 60, 650, 320, 120, "Real-time topic consistency\nseveral pages, same topic\nwithin ~15 min", "yellow", size=16)
    S.box("enough", 470, 330, 280, 150, "Enough\nhistory?", "blue", shape="diamond")
    S.box("window", 900, 330, 280, 150, "Productive\nwindow now?", "blue", shape="diamond")
    S.box("combine", 1230, 520, 320, 110, "Combine signals\n(user chooses which)", "yellow")
    S.box("setting", 1640, 500, 280, 150, "Activation\nsetting?", "violet", shape="diamond")
    S.box("auto", 1980, 330, 250, 110, "Auto Start\nnotify · dismiss\npause · override", "blue", size=16)
    S.box("suggest", 1980, 700, 250, 110, "Suggest First\nnotification\naccept · dismiss", "violet", size=16)
    S.box("session", 1640, 860, 280, 90, "Focus session", "blue", shape="ellipse")
    S.arrow("hours", "enough", "cold start")
    S.arrow("hist", "enough")
    S.arrow("enough", "window", "check")
    S.arrow("window", "combine", "time signal")
    S.arrow("rt", "combine", "activity signal", via=[(1390, 710)])
    S.arrow("combine", "setting", "go")
    S.arrow("setting", "auto", "default")
    S.arrow("setting", "suggest")
    S.arrow("auto", "session")
    S.arrow("suggest", "session", "accept")
    S.arrow("session", "hist", "learns", style="dashed", via=[(1780, 995), (25, 995), (25, 480)])


# ------------------------------------------------------------------------ 9
with S.frame("goal", "Goal & intent capture", 1960, 900,
             "Conversational, like an agent harness: ask only when needed."):
    S.box("start", 60, 270, 260, 90, "Session starts", "gray", shape="ellipse")
    S.box("manual", 410, 245, 260, 140, "Started\nmanually?", "blue", shape="diamond")
    S.box("ask", 770, 130, 340, 110, "Side panel asks\n\"What are you\nworking on?\"", "pink", size=16)
    S.box("vague", 1200, 115, 260, 140, "Goal vague?", "blue", shape="diamond")
    S.box("follow", 1560, 140, 330, 90, "One follow-up question", "pink", size=16)
    S.box("infer", 770, 420, 340, 110, "Infer goal from recent\ntopics + profile;\nshow it in side panel", "yellow", size=16)
    S.box("goal", 1200, 430, 300, 110, "Current goal\ntext + embedding", "violet")
    S.box("edit", 1580, 440, 300, 90, "User edits goal\nanytime", "pink", size=16)
    S.box("shift", 770, 700, 340, 100, "Topic-shift detector\n(embeddings)", "yellow", size=16)
    S.box("confirm", 1200, 700, 300, 100, "\"Switching to\nchemistry?\"", "pink", size=16)
    S.box("pipe", 1580, 700, 300, 80, "→ verdict pipeline", "gray")
    S.arrow("start", "manual")
    S.arrow("manual", "ask", "yes")
    S.arrow("manual", "infer", "no (Smart /\nContinuous)")
    S.arrow("ask", "vague")
    S.arrow("vague", "follow", "yes")
    S.arrow("follow", "vague", "", via=[(1725, 280), (1330, 280)])
    S.arrow("vague", "goal", "no")
    S.arrow("infer", "goal")
    S.arrow("edit", "goal")
    S.arrow("goal", "shift", "watch")
    S.arrow("shift", "confirm")
    S.arrow("confirm", "goal", "yes → update")
    S.arrow("goal", "pipe", "used by")


# ----------------------------------------------------------------------- 10
with S.frame("db", "Database schema (Postgres)", 1460, 1280,
             "Raw history 30 days; aggregates forever; content facts shared by all users."):
    S.table("users", 60, 180, "users", ["id           uuid  PK", "email        text  UQ", "auth_provider text",
                                         "plan         text", "profile      jsonb", "focus_hours  jsonb",
                                         "created_at   ts"])
    S.table("daily", 60, 620, "daily_stats", ["user_id      uuid  PK FK", "day          date  PK",
                                              "focus_min    int", "blocks       int",
                                              "heatmap      int[24]", "top_sites    jsonb",
                                              "convince_wins int"])
    S.table("sess", 500, 180, "sessions", ["id         uuid PK", "user_id    uuid FK", "mode       text",
                                           "goal       text", "started_at ts", "ended_at   ts"])
    S.table("verd", 500, 580, "verdicts", ["id         uuid PK", "user_id    uuid FK", "session_id uuid FK",
                                           "content_id uuid FK", "verdict    text", "reason     text",
                                           "source     text", "page_vec   vector (later)",
                                           "goal_vec   vector (later)", "created_at ts"])
    S.table("appl", 500, 1060, "appeals", ["id         uuid PK", "verdict_id uuid FK", "kind  text  won bool"])
    S.table("facts", 940, 620, "content_facts", ["id          uuid PK", "content_key text UQ",
                                                 "description text", "embedding   bytea",
                                                 "created_at  ts"], color="yellow")
    S.note("ret", 940, 180, 460, 260,
           "Retention\n• verdicts, appeals: deleted after 30 days\n  (so basic mode remembers 30 days)\n• daily_stats: kept forever\n"
           "• content_facts: shared, not per user\n• FAISS index is rebuilt from\n  content_facts.embedding", "yellow", size=16)
    S.arrow("sess", "users", "user_id")
    S.arrow("verd", "users", "user_id")
    S.arrow("verd", "sess", "session_id")
    S.arrow("verd", "facts", "content_id")
    S.arrow("appl", "verd", "verdict_id")
    S.arrow("daily", "users", "user_id")


# ----------------------------------------------------------------------- 11
with S.frame("privacy", "Privacy & data lifecycle", 2160, 960,
             "Sensitive pages never leave the browser. Users can see what was sent and pause checks."):
    S.box("page", 60, 330, 240, 90, "Page opened", "gray", shape="ellipse")
    S.box("sens", 380, 300, 260, 150, "Sensitive?\nor \"never check\"\nor privacy pause", "red", shape="diamond", size=15)
    S.box("none", 380, 580, 260, 90, "Nothing sent\npage allowed", "green", size=16)
    S.box("send", 740, 330, 260, 90, "Send page data\nHTTPS + JWT", "blue", size=16)
    S.cylinder("raw", 1090, 290, 280, 170, "Raw history\nverdicts · appeals")
    S.box("agg", 1460, 330, 260, 90, "Nightly aggregation", "cyan", size=16)
    S.cylinder("daily", 1810, 290, 300, 170, "daily_stats\nkept forever")
    S.box("purge", 1090, 590, 280, 90, "Deleted after 30 days", "red", size=16)
    S.box("log", 740, 590, 260, 90, "Activity log\nuser sees what was sent", "gray", size=15)
    S.proposed("del", 1460, 590, 300, 100, "Delete my data\n(settings)", "red", size=16)
    S.arrow("page", "sens")
    S.arrow("sens", "none", "yes")
    S.arrow("sens", "send", "no")
    S.arrow("send", "raw")
    S.arrow("raw", "agg")
    S.arrow("agg", "daily")
    S.arrow("raw", "purge", "30 days")
    S.arrow("raw", "log", "read", style="dashed")
    S.arrow("del", "raw", "", style="dashed")
    S.text(60, 800, "Filter runs in the content script before any request. Payment, banking and password pages are detected by\n"
           "card/password fields, a bank & payment domain list (proposed: bundled + updatable) and checkout URL patterns.", 17, color=MUTED)


# ----------------------------------------------------------------------- 12
with S.frame("deploy", "Deployment — one VPS", 1960, 1000,
             "Docker Compose. Only port 443 is public; services talk over the internal Docker network."):
    S.box("net", 60, 440, 220, 100, "Internet", "gray", shape="ellipse")
    S.zone("vps", 380, 190, 1160, 740, "VPS · docker-compose.yml", "cyan")
    S.proposed("caddy", 430, 430, 240, 110, "caddy\n:443 public", "cyan", size=16)
    S.box("go", 780, 300, 260, 110, "go-api\n:8080 internal\n+ cron jobs", "cyan", size=16)
    S.box("py", 780, 600, 260, 110, "py-ai\n:8000 internal\nembed model on CPU", "yellow", size=16)
    S.cylinder("pg", 1160, 260, 300, 170, "postgres\nvolume: pgdata")
    S.cylinder("fv", 1160, 580, 300, 170, "volume: faiss\nindex snapshots", "gray")
    S.box("llm", 1650, 600, 260, 110, "LLM provider\nAPIs (HTTPS)", "gray", shape="ellipse")
    S.arrow("net", "caddy", "HTTPS")
    S.arrow("caddy", "go", "reverse proxy")
    S.arrow("go", "py", "HTTP")
    S.arrow("go", "pg", "SQL")
    S.arrow("py", "pg", "SQL", style="dashed")
    S.arrow("py", "fv", "read / write")
    S.arrow("py", "llm", "outbound HTTPS", via=[(910, 860), (1780, 860)])


# ----------------------------------------------------------------------- 13
with S.frame("roadmap", "Roadmap & phases", 2160, 600,
             "Gymodoro is an integration option, never a focus mode. Keep a SyncProvider seam (no-op in v1)."):
    S.note("v1n", 60, 180, 640, 340,
           "v1 — now\n• Chrome extension (MV3, WXT + React)\n• 4 focus modes\n• AI content-aware blocking\n"
           "• Shared content-facts cache + FAISS\n• Free-tier LLM provider chain\n• Block screen, appeal, dot challenge\n"
           "• Convince Me (premium)\n• Feed cleanup: YT · IG · X · Reddit\n• Analytics + activity log\n"
           "• Sign-in required (Google, email)", "blue", size=18)
    S.note("latern", 760, 180, 640, 340,
           "Later\n• Track extension-off gaps\n• Incognito access prompt\n• Accountability partner\n"
           "• Leaderboards & friends\n• Rule layers where they cut cost\n• Custom ML classifier\n"
           "• Firefox & other browsers", "gray", size=18)
    S.note("muchn", 1460, 180, 640, 340,
           "Much later\n• Gymodoro integration\n  sync sessions & productivity data\n  manage focus from Gymodoro\n"
           "• Desktop app\n• Mobile app", "gray", size=18)
    S.arrow("v1n", "latern", "")
    S.arrow("latern", "muchn", "")


# ----------------------------------------------------------------------- 14
with S.frame("pyflow", "Python AI service — page to verdict", 2320, 2980,
             "Step by step, with the file for each step. Dashed = later (content cache). LLMs get TEXT; vectors are only for lookup and comparison."):
    S.box("ext", 100, 190, 300, 90, "1. Extension reads page\ntitle · tags · text", "blue", size=16)
    S.box("go", 520, 190, 360, 90, "Go API\n→ POST /v1/classify (api.py)", "cyan", size=16)

    S.zone("py", 80, 340, 1560, 1560, "Python AI service  (ai-service/src/ai_service/)", "yellow")
    S.box("s2", 520, 420, 360, 90, "2. Embedder\npage TEXT → page vector\n(later)", "yellow", style="dashed", size=16)
    S.box("s3", 560, 610, 280, 160, "3. FAISS:\nclose stored\nvector? (later)", "blue", shape="diamond", style="dashed", size=15)
    S.box("s4a", 140, 860, 340, 100, "4a. Postgres\nget saved summary\n(later)", "violet", style="dashed", size=16)
    S.box("s4b", 860, 860, 340, 100, "4b. Describer\nsend page TEXT to LLM\n→ summary TEXT", "yellow", size=16)
    S.box("s5", 1260, 860, 340, 100, "5. Save summary → Postgres\n+ page vector → FAISS\n(later)", "violet", style="dashed", size=15)
    S.box("s6", 500, 1120, 400, 100, "6. Embedder\nsummary TEXT → summary vector\ngoal TEXT → goal vector", "yellow", size=16)
    S.box("s7", 560, 1330, 280, 160, "7. Goal matcher\ncompare vectors\n→ score", "violet", shape="diamond", size=15)
    S.box("allow", 140, 1590, 240, 90, "ALLOW", "green", size=20)
    S.box("judge", 540, 1580, 320, 110, "8. LLM judge (unclear only)\nsummary TEXT + goal TEXT\ndetail below ↓", "yellow", size=16)
    S.box("block", 1020, 1590, 240, 90, "BLOCK", "red", size=20)

    S.box("prov", 1760, 1110, 280, 110, "LLM provider APIs\n(llm.py chain)", "gray", shape="ellipse", size=16)

    S.arrow("ext", "go", "page data")
    S.arrow("go", "s2", "")
    S.arrow("go", "s4b", "page TEXT (kept)", via=[(1030, 235)])
    S.arrow("s2", "s3", "page vector")
    S.arrow("s3", "s4a", "found", style="dashed")
    S.arrow("s3", "s4b", "not found", style="dashed")
    S.arrow("s4b", "s5", "", style="dashed")
    S.arrow("s4a", "s6", "saved summary", style="dashed")
    S.arrow("s4b", "s6", "summary TEXT")
    S.arrow("s6", "s7", "two vectors")
    S.arrow("s7", "allow", "related ≥ 0.75")
    S.arrow("s7", "judge", "unclear 0.55–0.75")
    S.arrow("s7", "block", "unrelated ≤ 0.55")
    S.arrow("judge", "allow", "on-task")
    S.arrow("judge", "block", "distraction")
    S.arrow("s4b", "prov", "TEXT", style="dashed")
    S.arrow("judge", "prov", "TEXT", style="dashed", via=[(700, 1800), (1900, 1800)])

    S.note("files", 1720, 340, 560, 330,
           "Files (ai-service/src/ai_service/)\n"
           "1  extension (not Python)\n"
           "2  embedder.py · later\n"
           "3  — · later (FAISS or pgvector)\n"
           "4a — · later (Postgres)\n"
           "4b describer.py #4 + llm.py #3\n"
           "5  — · later\n"
           "6  embedder.py #1 + matcher.py #2\n"
           "7  matcher.py #2\n"
           "8  judge.py #5 + llm.py #3\n"
           "glue 4b→8: pipeline.py #6\n"
           "basic mode: describer.py + pipeline.py\n"
           "HTTP in/out: api.py (done)", "yellow", size=17)
    S.note("now", 1720, 730, 560, 230,
           "Building now (Step 0)\n1 → 4b → 6 → 7 → 8\n\nLater (content cache)\n2 → 3 → 4a, and 5\n\nFAISS remembers what a page IS,\nnever whether it distracts.", "gray", size=17)
    S.text(100, 1920, "Verdict (allow / block + reason) returns to the Go API, then the extension shows the block overlay.", 17, color=MUTED)

    # Step 8 in detail: what happens when the score is unclear.
    Y0 = 2040
    S.zone("detail", 80, Y0, 2160, 880, "Step 8 in detail — unclear score (0.55–0.75)", "yellow")
    S.box("u_in", 120, Y0 + 95, 240, 90, "From step 8\nscore 0.55–0.75", "violet", shape="ellipse", size=15)
    S.box("u_prompt", 450, Y0 + 75, 380, 130,
          "8.1 Build prompt (judge.py)\nsystem: judge rules\nuser: goal · profile · summary\ntopics · kind (score not sent)", "yellow", size=15)
    S.box("u_try", 950, Y0 + 85, 300, 110, "8.2 complete_json (llm.py)\ntry provider 1 (Groq)", "yellow", size=15)
    S.box("u_ok", 1370, Y0 + 65, 280, 150, "Valid JSON\n{decision,\nreason}?", "blue", shape="diamond", size=15)
    S.box("u_more", 1840, Y0 + 65, 280, 150, "More providers\nleft?", "blue", shape="diamond", size=15)
    S.box("u_verdict", 1360, Y0 + 320, 300, 110, "8.3 Verdict (judge.py)\ndecision · reason\nsource = llm", "yellow", size=15)
    S.box("u_exh", 1840, Y0 + 330, 280, 90, "AllProvidersExhausted\n(llm.py)", "red", size=15)
    S.box("u_yt", 1800, Y0 + 520, 320, 110, "Basic mode → frame 15\nextracted summary · match\n(describer.py · pipeline.py)", "yellow", size=15)
    S.box("u_out", 900, Y0 + 520, 380, 120, "Return Verdict → Go API\nallow / block + reason\n(Go counts 1 AI check)", "cyan", size=15)
    S.note("u_notes", 120, Y0 + 520, 700, 290,
           "Notes\n"
           "• The same chain + fallback also guards the describer (4b).\n"
           "• Go checks its cached verdict before calling Python,\n"
           "  so there is no cache step here.\n"
           "• Bad JSON counts as a provider failure → next provider.\n"
           "• Free cap used up: Go sends use_llm = false,\n"
           "  so Python goes straight to basic mode.", "gray", size=15)

    S.arrow("u_in", "u_prompt", "")
    S.arrow("u_prompt", "u_try", "TEXT")
    S.arrow("u_try", "u_ok", "")
    S.arrow("u_ok", "u_verdict", "yes")
    S.arrow("u_ok", "u_more", "no: rate limit ·\ntimeout · bad JSON")
    S.arrow("u_more", "u_try", "yes: next provider (Gemini …)", via=[(1980, Y0 + 40), (1100, Y0 + 40)])
    S.arrow("u_more", "u_exh", "no")
    S.arrow("u_exh", "u_yt", "")
    S.arrow("u_yt", "u_out", "")
    S.arrow("u_verdict", "u_out", "")


# ----------------------------------------------------------------------- 15
with S.frame("basic", "Basic mode — judging without an LLM", 2200, 1300,
             "Runs when a free user's daily AI cap is used up, or when every LLM provider is down. Cost ≈ 0: local embeddings only."):
    S.box("in1", 80, 200, 300, 90, "Free cap used up\n(Go sends use_llm = false)", "cyan", shape="ellipse", size=15)
    S.box("in2", 80, 420, 300, 90, "All LLM providers\ndown", "red", shape="ellipse", size=15)
    S.box("ex", 520, 300, 380, 120, "1. Extracted summary (describer.py)\ntitle · meta · headings\nYT channel · category · tags", "yellow", size=15)
    S.box("m", 560, 540, 300, 160, "2. Embedding match\nvs goal\n(basic thresholds)", "violet", shape="diamond", size=15)
    S.box("ok", 80, 580, 240, 80, "ALLOW", "green", size=18)
    S.box("bl", 1060, 580, 240, 80, "BLOCK", "red", size=18)
    S.box("nn", 560, 820, 300, 170, "3. Closest past case?\nsame user · similar page\n+ similar goal ≥ 0.9\n(later)", "blue", shape="diamond", style="dashed", size=14)
    S.box("copy", 1060, 860, 280, 90, "Copy its verdict\nsource = nearest\n(later)", "gray", style="dashed", size=15)
    S.box("re", 80, 870, 280, 90, "4. Allow ·\nrecheck later", "green", size=16)

    S.arrow("in1", "ex", "")
    S.arrow("in2", "ex", "")
    S.arrow("ex", "m", "summary TEXT")
    S.arrow("m", "ok", "related")
    S.arrow("m", "bl", "unrelated")
    S.arrow("m", "nn", "unclear")
    S.arrow("nn", "copy", "yes", style="dashed")
    S.arrow("nn", "re", "no (or not built yet)")

    S.note("why", 1460, 180, 680, 300,
           "Why basic mode\n• Protection never stops: no uninstalls\n  or \"stopped working\" reviews\n"
           "• Free users still see the premium offer\n• Premium = unlimited AI checks, so it\n  only reaches basic mode in outages", "yellow")
    S.note("rules", 1460, 540, 680, 360,
           "Rules\n• No LLM calls; source = extracted\n• May need its own thresholds (eval)\n"
           "• Closest case uses only THIS user's\n  verdicts: verdicts depend on the goal\n"
           "• Prefer LLM-judged + corrected cases\n• Open: extracted summary first for\n  everyone? Decided by the eval", "gray")
    S.note("lev", 1460, 960, 680, 260,
           "Upgrade levers (proposed)\n• Popup: \"Basic mode: less accurate\n  until midnight\"\n"
           "• Upgrade prompt when basic mode\n  allows an unclear page\n• Track retention · upgrades · appeals", "gray")


S.save(OUT)
