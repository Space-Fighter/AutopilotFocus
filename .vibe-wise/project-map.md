# Project Map

## Purpose
AutopilotFocus: a distraction blocker that judges page *content* rather than whole sites, so the user never maintains a manual blocklist. Example: a YouTube lecture is allowed; cat or gaming videos are not.

## Requirements
- No manual URL blocklist (core differentiator vs existing blockers)
- Judge relevance at content level (e.g. per YouTube video), not per domain
- Platform: browser extension first; desktop and mobile apps in later stages
- Audience: public product (onboarding and polish matter)
- Main failure mode addressed: distracting sites/apps, including ones not on any list
- Must work standalone (no account) AND optionally connected to Gymodoro (user's existing productivity + fitness platform)
- Standalone vs Gymodoro-connected are integration options, NOT focus modes; all four modes available in both
- Gymodoro connection syncs focus sessions and relevant productivity data; Gymodoro can manage the focus experience; Gymodoro enhances but never gates modes
- Shared AI-powered, context-aware detection that understands what the user is trying to accomplish (not productive/distracting site labels)
- Focus modes:
  1. Timed Focus: user sets duration; auto-ends; pause/resume/end early
  2. Continuous (Always On): no duration; persists across browser restarts/reboots (within extension limits); temporary pause without disabling
  3. Fixed Focus-Break Cycles: configurable focus/break intervals (e.g. 25/5); blocking relaxed during breaks; pause/resume/stop
  4. Smart Focus: combines historical patterns (e.g. strong focus 9-11 AM) with real-time sustained productive activity (e.g. 15 min biology study) to start sessions; keeps learning
     - Activation setting: Auto Start (default; notifies; dismiss/pause/override) or Suggest First (notification to accept/dismiss)
     - User configures session duration and which detection signals are used
- Architecture must separate focus-mode logic from Gymodoro integration
- Intent capture: should feel flexible and conversational, like an agent harness (e.g. Claude Code asking clarifying questions in context). Exact mechanism not yet defined.
- On distraction: hard block with a catchy phrase (e.g. "Caught you slopping")
  - If not actually distracted: user answers a few questions to justify and get through
  - If distracted and still wants it: user must persuade an AI in a feature named "Convince Me"
- Error tolerance: false blocks and missed distractions weighted equally, provided users can correct in one click and the system learns from it
- Breaks (Fixed cycles): blocking fully off, plus a nudge near break end to wrap up
- "Convince Me" outcome: if it was genuinely not a distraction -> pass for that page; if it was a distraction and user convinces -> timed pass
- Data the AI may see: everything on the page EXCEPT payment pages and banking/credential pages (exclusion mechanism not yet defined)
- v1 browser: Chrome only (Manifest V3)
- Build philosophy: v1 is AI-agent-first (the model does the judging, minimal hardcoded rules). Rule-based layers get added later only where they measurably cut cost or improve results.
- Cost idea from user: reuse earlier LLM verdicts via vector embeddings / FAISS / RAG (semantic cache)
- Cache design (chosen after explanation): shared cache of content FACTS (AI-written description per unique content); per-user goal match via embedding similarity, AI call only when the match is unclear; optional personal verdict cache
- Model chain: no "smarter model" tier. Same-tier models used in sequence; when one model's quota/limit is exhausted, move to the next. Last resort = premium upsell or manual blocklist until free limits reset.
- Accounts: sign-in required from the start
- AI outage: use cached verdict if it exists; otherwise fall back to HTML/metadata tools. YouTube gets a dedicated parser (video tags, channel, category) checked against a predefined set of distracting tags, because YouTube is heavily used for both study and distraction. Custom ML model = future scope.
- Latency: page shows normally; block screen appears once the verdict says distraction (brief exposure accepted)
- Bypass resistance (LATER, not v1): track extension-off gaps in analytics, request Incognito access, accountability partner notifications. Social later: focus-time leaderboards, friends and strangers motivating each other.
- YouTube "Unhook"-style cleanup: hide Shorts entirely, home page feed, and sidebar "more videos"; do NOT hide playlists or comments
- Re-checks: only on navigation (each URL change, including in-page navigation on YouTube etc.); no re-check while staying on a page
- Scope: active tab only; background tabs ignored until focused
- Feed cleanup is always on by default, with per-part toggles in settings
- Instagram, X, Reddit: blocked by default during focus sessions (whole site); a specific subreddit/page allowed only by winning "Convince Me". (A deliberate default site rule, separate from AI page judging.)
- Feed cleanup UI modeled on Unhook (per-element toggles). YouTube Shorts always blocked (no toggle). If feed cleanup is on, hidden elements stay hidden during breaks too.
- Appeal ("I wasn't distracted"): one-line reason, judged by AI
- "Convince Me" persona: user picks in settings (e.g. savage, coach, chill)
- Smart Focus cold start: onboarding asks preferred focus hours + use real-time activity only, until enough history accumulates
- Browsing history and focus patterns stored on the server with the account
- v1 analytics: focus time & streaks; distraction breakdown (blocks/day, top sites/topics, peak drift times); best focus hours heatmap; Convince Me record
- Backend stack (chosen): Go API (auth, DB, limits, history, cache lookup) + Python AI service (descriptions, embeddings, goal match, model chain). Node dropped; page data is extracted in the extension via content scripts. Playwright (Python) only if server scraping is ever needed.
- Learner is new to Go and wants to learn it through this project
- Database: Postgres for relational data; FAISS (inside the Python service) for vectors. FAISS persistence/reload must be designed.
- Hosting: one VPS running all services with Docker Compose
- Sign-in: Google + email/password (Gymodoro account later)
- Extension UI surfaces: toolbar popup (quick actions/timer) + Chrome side panel (chat-style goal setting, Convince Me) + full page (analytics, settings)
- Extension UI: WXT + React + TypeScript
- Model chain providers: free-tier APIs first (e.g. Gemini Flash, Groq-hosted open models); specific list TBD
- Free tier: daily cap on fresh AI checks (cache hits don't count); resets daily; number TBD
- Embedding model: learner delegated choice (proposed: small local open model on CPU, e.g. bge-small)
- Onboarding: profile ("who are you", main topics), preferred focus hours, default mode, try-it demo. Since there's no focus data at first, encourage use during preferred hours to build history.
- Goal chat: side panel opens on session start ("What are you working on?"), follow-up only if vague
- Goal change mid-session: manual edit in side panel anytime + auto-detected topic shift prompt ("Switching to chemistry?")
- Convince Me is PREMIUM ONLY (AI cost); escalating difficulty per win per day. Free users instead get a friction challenge: click a randomly moving dot ~30 times to get a timed pass.
- Free appeal: allowed for free users; each appeal uses one AI check from the daily cap
- Smart Focus real-time signal: topic consistency (several pages on the same topic within ~15 min, via embeddings)
- Retention: raw history deleted after 30 days; stats (focus time, heatmap, streaks, breakdowns) kept as aggregates indefinitely so progress stays visible
- v1 success metric: accuracy (low rate of successful appeals/corrections)
- Sensitive pages filtered IN THE BROWSER before sending: password/card fields, bank/payment domains, checkout URLs -> nothing sent, page allowed
- Transparency: activity log (what was checked + verdict), one-click "never check this site", privacy pause
- Phasing: Gymodoro integration is a much later phase. v1 = standalone extension only; keep a clean seam for later sync.

## Components
No application code yet. Architecture drawings (planned design, not implementation): docs/architecture/ (Excalidraw board generated by diagrams.py; skill in .claude/skills/excalidraw-architecture/).

## Main Flow
Unknown.

## Data and Trust Boundaries
Unknown.

## Build and Deployment
None.

## Unknowns
- Exact free-tier cap number, provider list, embedding model (proposed in spec)
- FAISS persistence and multi-process design
- Go<->Python transport (proposed HTTP/JSON in spec)
- Spec: ../.plans/autopilot-focus-v1-spec.md
