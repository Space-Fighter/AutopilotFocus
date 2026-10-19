# AutopilotFocus v1 — Product & Technical Spec

Status: Draft from interview (2026-10-15 to 2026-10-17)
Scope: v1 = standalone Chrome extension + backend. Gymodoro integration, desktop app, and mobile app are later phases.

Legend: **Decided** = chosen by the product owner. **Proposed** = Claude's suggestion, to confirm before or during building.

---

## 1. Problem and core idea

Existing distraction blockers need a manual list of URLs, and they block whole sites. That fails in two ways:

1. **Manual work.** Any distracting site not on the list gets through.
2. **Whole-site blocking is too coarse.** YouTube is useful when you're studying from a lecture and harmful when you're watching cat or gaming videos. Most blockers block YouTube entirely.

**AutopilotFocus** judges the *content* of each page against *what the user is trying to accomplish*, using AI. There's no blocklist to maintain. A biology lecture is allowed during a biology study session, and a gaming video is blocked.

Audience: **public product** (Decided). Onboarding, polish, privacy, and cost control all matter.

---

## 2. Phasing

| Phase | Scope |
|---|---|
| **v1** | Chrome extension (Manifest V3) + Go API + Python AI service. Sign-in required. All four focus modes. |
| Later | Bypass resistance (track extension-off gaps, Incognito access, accountability partner), social features (leaderboards, friends, motivating strangers), custom ML classifier, Firefox and other browsers. Music allowance + 45 s music picking window (parked design: `.plans/architecture/future/music/`). |
| Much later | Gymodoro integration (sync sessions and productivity data; manage focus from Gymodoro). Desktop and mobile apps. |

**Architecture rule (Decided):** focus-mode logic must be separate from any integration. Gymodoro will later be an *integration option* that syncs data. It never decides which modes are available. Keep a clean seam, such as a `SyncProvider` interface with a no-op v1 implementation.

---

## 3. Focus modes (all Decided)

All four modes share the same detection engine.

### Mode 1 — Timed Focus
- The user starts a session and sets a duration.
- Context-aware blocking stays active until the timer ends, then the session ends automatically.
- Pause, resume, and end early.

### Mode 2 — Continuous Focus (Always On)
- No duration. It stays active until the user turns it off.
- It must survive browser restarts and reboots. State is kept in `chrome.storage` and restored on the service worker's `runtime.onStartup` event.
- Temporary pause without turning the mode off. No countdown.

### Mode 3 — Fixed Focus-Break Cycles
- Configurable focus and break lengths (for example 25/5). Alternates automatically.
- **Breaks:** AI blocking is fully off, with a nudge shortly before the break ends.
- **Feed cleanup still applies during breaks** if the user has it turned on (see §6).
- Pause, resume, and stop.

### Mode 4 — Smart Focus
Combines two signals to decide when to start focus:
- **Historical:** time windows when the user usually focuses well (for example 9–11 AM).
- **Real-time:** *topic consistency*, meaning several pages or videos on the same topic within about 15 minutes, measured by embedding similarity. No LLM call is needed for this.

Activation settings (not separate modes):
- **Auto Start (default):** starts focus and notifies the user. The user can dismiss, pause, or override.
- **Suggest First:** shows a notification instead, such as "You usually focus best around this time. Ready to start a focus session?"

Users can set the session length and choose which signals are used (history, real-time, or both).

**Cold start:** onboarding asks for preferred focus hours. Until enough history exists, Smart Focus uses preferred hours and the real-time signal only. Onboarding encourages using the extension during preferred hours so history builds up.

---

## 4. Intent: knowing what the user is trying to do

**Principle (Decided):** goal-setting should feel flexible and conversational, like an agent harness that asks short clarifying questions in context.

- **Profile (onboarding):** who the user is (student, developer, designer, …) and their main topics. This is the baseline.
- **Session goal chat (Decided):** when a session starts, the Chrome side panel opens and asks "What are you working on?" One line is enough. The AI asks a follow-up only if the goal is vague.
- **Goal changes mid-session (Decided):** both of these:
  - The user edits the goal in the side panel at any time, and judging updates immediately.
  - The system detects a topic shift and asks, for example, "Switching to chemistry?"
- **Auto-started sessions (Smart, Continuous):** use the inferred topic from recent activity together with the profile. Show the inferred goal in the side panel so the user can correct it. *(Proposed: this detail wasn't covered in the interview.)*

---

## 5. Detection pipeline

### 5.1 Build philosophy (Decided)
v1 is **AI-first**: the model does the judging, with minimal hardcoded rules. Rule-based shortcuts are added later, and only where they measurably cut cost or improve accuracy.

Deliberate exceptions in v1:
- Sensitive-page filter (§8)
- Default site rules for Instagram, X, and Reddit (§6)
- YouTube metadata parser, used as a fallback (§5.5)

### 5.2 What triggers a check (Decided)
- **Only on navigation:** every URL change, including in-page navigation on single-page sites like YouTube, Reddit, and X. Detect it with the `chrome.webNavigation.onHistoryStateUpdated` event plus a content-script URL watcher.
- No re-check while the user stays on one page. Drifting into comments isn't re-judged; autoplay to a new video changes the URL, so it is re-checked.
- **Active tab only.** Background tabs are checked when they become active.
- Checks run only while a focus period is active (not during breaks or when no session is running).

### 5.3 Latency (Decided)
The page shows normally. If the verdict is "distraction", the block screen covers it. A second or two of exposure is acceptable.

### 5.4 Flow

```
Content script (in page)
  1. Sensitive-page check (§8). If sensitive → stop, allow, send nothing.
  2. Extract page data from the DOM: URL, title, meta description, headings,
     visible text excerpt; on YouTube: title, channel, tags, category,
     description, captions if available.
        │
        ▼
Background service worker → Go API  POST /v1/verdict
        │
Go API:
  3. Auth + daily free-tier check
  4. Personal verdict cache (user + content) → hit: return
        │ miss
        ▼
Python AI service:
  5. Content facts: shared cache lookup (exact content ID, e.g. YouTube video ID
     or normalized URL; then FAISS nearest-neighbor on content embedding).
     Miss → LLM writes a short content description
     ("Minecraft gameplay, entertainment, casual") → stored, shared by all users.
  6. Goal match: embedding similarity between content description and the
     user's current goal + profile.
       - Clearly related → allow
       - Clearly unrelated → distraction
       - Unclear → LLM call with goal + description → verdict
  7. Return verdict + short reason
        │
        ▼
Go API: store verdict in personal cache + history; count the AI check if one was used
        │
        ▼
Extension: allow, or show the block screen (§7)
```

### 5.5 Caching (Decided design)
- **Shared cache of content facts**, not verdicts. The same content can be on-task for one user and a distraction for another (a coding tutorial, social media for a social media manager, lo-fi music). So only *what the content is* gets shared across users. Cost grows with *unique content*, not with *number of users*.
- **Per-user goal match** on top, usually by embedding similarity with no LLM call.
- **Personal verdict cache:** content this user has already judged is never rechecked.
- **Cache hits don't count** toward the free-tier cap.

### 5.6 Model chain (Decided)
- No "smarter model" tier. Same-tier models run **in sequence**: when one provider's quota or rate limit runs out, move to the next.
- **Free-tier APIs first** (for example Gemini Flash, Groq-hosted open models) to keep v1 cost near zero. *(Proposed: the exact list and order go in config, not code.)*
- **Last resort:** when every provider is exhausted, or the user's free cap is used up, offer premium, or a manual blocklist until limits reset.

### 5.7 AI outage or no verdict (Decided)
1. Use a cached verdict if one exists.
2. Otherwise use HTML and metadata tools. On YouTube, a **dedicated parser** checks tags, channel, and category against a predefined set of distracting tags. This matters because YouTube is heavily used for both study and distraction.
3. Otherwise allow the page and re-check when the AI is back. *(Proposed final step.)*
4. A custom ML model is future scope.

### 5.8 Embedding model
**Proposed (choice delegated to Claude):** a small local open model such as `bge-small-en-v1.5`, running on CPU in the Python service. It's free, fast, private, and has no per-call cost. Swap it later if accuracy demands.

---

## 6. Feed cleanup ("Unhook"-style) and default site rules

### YouTube (Decided)
- Hide the **home page feed**, **sidebar "more videos"**, and **Shorts**.
- **Shorts are always blocked**, with no toggle.
- **Do not hide** playlists or comments.
- Feed cleanup is **always on by default**, with per-element toggles in settings. The UI is modeled on Unhook.
- When turned on, hidden elements **stay hidden during breaks too**.

### Instagram, X, Reddit (Decided)
- **Blocked by default during focus sessions** (the whole site).
- A specific page (for example one subreddit) can be allowed only through Convince Me (premium) or the free challenge (§7).
- Feed hiding (Reels and Explore, X "For you" and trending, Reddit home and popular) uses the same toggle UI. *(Proposed, carried over from the interview.)*

Implementation: content scripts with CSS injection plus a `MutationObserver` for elements that load dynamically. Keep selectors in a remotely updatable config, because these sites change their markup often. *(Proposed.)*

---

## 7. Block screen, appeals, and Convince Me

### Block screen (Decided)
A hard block covers the page with a catchy phrase such as **"Caught you slopping."** *(Proposed: rotate a set of phrases that match the selected persona.)*

Two paths out:

| User says | Free users | Premium users | Outcome if successful |
|---|---|---|---|
| **"I wasn't distracted"** | One-line reason, judged by AI. **Uses one AI check from the daily cap.** | Same, not capped | **Pass for that page** (the exact video or URL). Logged as a correction for learning. |
| **"I was, and I want it anyway"** | **Dot challenge:** a dot moves randomly around the screen; click it about 30 times | **Convince Me:** argue with an AI persona | **Timed pass** |

### Convince Me (Decided)
- **Premium only**, because of AI cost.
- The persona is chosen in settings (for example savage, coach, chill).
- **Escalating difficulty:** each win in a day makes the next one harder. *(Proposed: passes also get shorter.)*

### Error handling (Decided)
False blocks and missed distractions count as equally bad, as long as users can correct either in one click and the system learns from it. *(Proposed: a "This was a distraction" button in the popup for missed ones; the appeal flow covers false blocks.)*

---

## 8. Privacy and data

### Sensitive-page filter (Decided: runs in the browser)
Before anything is sent, the content script checks for:
- password or credit-card input fields on the page
- known bank and payment domains *(Proposed: a bundled list that can be updated)*
- checkout and payment URL patterns

If any match, **nothing is sent**, and the page is allowed.

### What the AI may see (Decided)
Everything else on the page: URL, title, metadata, visible text, captions.

### Transparency (Decided)
- An **activity log** showing what was checked and the verdict.
- One-click **"never check this site"**.
- A **privacy pause**.

### Retention (Decided)
- **Raw browsing history is kept for 30 days**, then deleted automatically.
- **Stats are kept indefinitely as aggregates**, so progress stays visible: daily focus minutes, hourly heatmap buckets, streaks, distraction counts per site and topic, and Convince Me tallies.
- *(Proposed: the user can delete all data from settings, which also matters for Chrome Web Store review and GDPR.)*

---

## 9. Accounts and pricing

- **Sign-in required from the start** (Decided). Google and email + password. Gymodoro account later.
- **Free tier (Decided):** a daily cap on *fresh* AI checks (cache hits don't count; appeals do), reset daily. *(Number to decide before launch; Proposed starting point: about 100 per day.)*
- **Premium:** unlimited AI checks and Convince Me. *(Pricing to be decided.)*

---

## 10. Extension UI (Decided)

| Surface | Purpose |
|---|---|
| **Toolbar popup** | Start, stop, and pause a session; timer; current mode; quick "this was a distraction" report |
| **Side panel** | Chat-style goal setting, goal changes, topic-shift prompts, Convince Me chat |
| **Full page** | Analytics, settings, feed-cleanup toggles, activity log, account |
| **Block screen** | Injected overlay (§7) |

### Onboarding (Decided)
1. Sign in
2. Profile: who you are and main topics
3. Preferred focus hours
4. Pick a default mode
5. Try-it demo: open a sample distracting page to see "Caught you slopping" and the appeal flow
6. Encourage focusing during preferred hours to build history

### Analytics in v1 (Decided)
- Focus time and streaks (daily and weekly)
- Distraction breakdown: blocks per day, top distracting sites and topics, peak drift times
- Best focus hours heatmap (also feeds Smart Focus)
- Convince Me record: attempts, wins, reasons

---

## 11. Technical architecture

### Stack (Decided)

| Part | Technology | Responsibility |
|---|---|---|
| Extension | **WXT + React + TypeScript**, Manifest V3, Chrome only | UI, content scripts (DOM extraction, feed cleanup, sensitive filter, block overlay), session state machine |
| API | **Go** (the developer is learning Go through this project) | Auth, users, sessions, history, limits, personal verdict cache, analytics aggregation |
| AI service | **Python** | Content descriptions, embeddings, FAISS search, goal match, LLM model chain, Convince Me and appeal judging |
| Database | **Postgres** | Users, sessions, verdicts, history (30 days), aggregates, content facts |
| Vectors | **FAISS** inside the Python service | Nearest-neighbor search over content and goal embeddings |
| Hosting | **One VPS + Docker Compose** | All services in containers |

Node and Playwright were **dropped**. Content scripts already have the fully rendered page inside the user's real browser. If server-side scraping is ever needed (for example warming the cache with trending videos), use the YouTube Data API or Playwright for Python.

### Proposed details (not covered in the interview)
- **Go ↔ Python:** HTTP/JSON on the internal Docker network. Add a Redis queue later if traffic spikes demand it.
- **FAISS persistence:** Postgres is the source of truth for content facts and their embeddings. The Python service builds the FAISS index from Postgres on startup, adds to it as new content arrives, and saves snapshots to a disk volume. Run one Python worker that owns the index, or rebuild per worker. Avoid several processes writing to one index.
- **Go auth:** JWTs (signed JSON Web Tokens) issued after Google OAuth or an email/password login. Passwords hashed with bcrypt or argon2.
- **Extension session engine:** a state machine (`idle → focus ↔ paused → break → …`) in the background service worker, persisted to `chrome.storage.local`, and timed with `chrome.alarms`, because MV3 service workers can be stopped at any time.
- **Reverse proxy:** Caddy for HTTPS in front of the Go API. Only Go is exposed publicly.

### Main components

```
┌──────────── Chrome extension (WXT/React/TS) ────────────┐
│ popup · side panel · full page · block overlay          │
│ background SW: session state machine, alarms, API client│
│ content scripts: extractor · sensitive filter ·         │
│                  feed cleanup · URL-change watcher      │
└───────────────┬──────────────────────────────────────────┘
                │ HTTPS (JWT)
        ┌───────▼────────┐        ┌────────────────────────┐
        │  Go API        │──HTTP──▶ Python AI service      │
        │ auth, limits,  │        │ embeddings (local),    │
        │ history, stats │        │ FAISS, goal match,     │
        └───────┬────────┘        │ LLM chain (free tiers) │
                │                 └──────────┬─────────────┘
                └──────────► Postgres ◄──────┘
                    (one VPS, Docker Compose)
```

---

## 12. Success metric (Decided)

**Accuracy.** Few verdicts get corrected: a low share of blocks successfully appealed, and few missed distractions reported. *(Proposed target: under 10% of blocks successfully appealed.)* Track per site category and per mode.

---

## 13. Open questions

1. Free-tier daily cap number and premium price.
2. Exact model providers, their order, and the rate limits of each free tier.
3. How auto-started sessions show the inferred goal and let the user correct it.
4. Convince Me escalation curve and timed-pass lengths. Dot-challenge click count and pass length.
5. Whether the predefined YouTube "distracting tags" list is hand-written or generated from verdict data.
6. Sensitive-domain list source and update mechanism.
7. Remote config for feed-cleanup selectors and how often it updates.
8. Data-deletion flow and privacy policy wording for Chrome Web Store review.
9. How Smart Focus learns "productive windows" from history: thresholds and minimum days of data.
