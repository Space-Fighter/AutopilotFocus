# Goals model + basic-mode nearest-case search — Spec

Status: Decided in interview, 2026-10-31 to 2026-11-01
Extends: `.plans/autopilot-focus-v1-spec.md` (§4 Intent, §5.9 Basic mode, §8 Privacy, §10 UI).
Audience: students and working professionals with ordinary jobs. Rare roles are not design drivers.

---

## 1. Summary

1. Every user has a **goal model**: always-on general rules, a **saved goal list**, and an optional **session goal**.
2. When a page is blocked, the block screen shows **why** and **which goal** was used, and lets the user **edit the goal**. Every new goal is checked by the LLM so a goal can't be "the distraction itself".
3. In **basic mode** (no LLM: free cap used up, or all providers down), an unclear page is decided by the **closest past cases from all users**, like a doctor who compares a new patient with the most similar earlier cases.
4. If there's too little evidence, the page stays allowed and a small floating prompt asks: **"Is this a distraction?"** The answer becomes the strongest kind of evidence.
5. Decision search runs in **Postgres (pgvector)**. Summary search stays in **FAISS**. Both sit behind small interfaces so either can be swapped later.

---

## 2. Goal model

### 2.1 Layers
| Layer | What it is | Where it comes from |
|---|---|---|
| **General goal** | Not an embedded goal. Two parts: the judge's rules (rubric) and a list of **always-allowed categories** (docs, email, calendar, search, dev and office tools, study and work sites) | Built in |
| **Saved goal list** | The user's standing subjects or work tasks, e.g. "cell biology", "monthly accounts in Excel" | Onboarding (optional), side panel, dashboard, block screen |
| **Session goal** | What the user works on right now, typed at session start | Side panel "What are you working on?" |
| **Inferred goal** | A guess from recent pages + saved list, for sessions that start without a typed goal (Smart, Continuous) | Computed |

If the user gives no goals at onboarding, only the general goal applies until they add some.

### 2.2 Which goals are active
- **Session goal set:** only the session goal + the general goal. Other saved goals do **not** allow pages. (Biology session → chemistry pages can be blocked.)
- **No session goal:** the whole saved list + the general goal.
- **Auto-started session without a typed goal:** the inferred goal + the general goal.

### 2.3 Matching against several goals
The page is compared with **each active goal separately**; the **highest score wins**. Goals are never glued into one text, because that dilutes each one. Each goal is embedded once when saved and its vector is reused.

### 2.4 Saved goal list rules
- **Size:** free users up to **5** saved goals; premium **unlimited**.
- **Session goal lifetime:** at session start the user chooses **"Add to my goals"** or **"Just for this session"** (temporary, dropped when the session ends).
- **Managed in:** onboarding walkthrough, side panel, dashboard settings, block screen.

### 2.5 Goal check (stops "the goal is the distraction")
- **Every goal added to the saved list**, and every **edit made from the block screen**, is checked once by the LLM: does it describe a real task with an outcome, or just consuming content?
  - "Revise cell biology for Friday's exam" passes. "Watch Minecraft videos" is rejected.
  - Work-like goals pass even if they involve a usually distracting site (making or managing something, not consuming it).
- The check uses one AI check. In basic mode (no LLM available), a new goal is saved as **pending** and checked when AI is available; until then it does not allow pages.
- **Goal text is untrusted**, like page text: it is quoted inside the judge prompt with the instruction to ignore any instructions in it, and capped in length (~200 characters).

---

## 3. Block screen

- Shows: the phrase ("Caught you slopping"), the **reason**, and the **goal that was used**, e.g. *"Minecraft gameplay isn't part of: Revise cell biology"*.
- Buttons: **Edit goal**, **I wasn't distracted** (appeal), **I want it anyway** (dot challenge / Convince Me).
- **Edit goal flow:** user edits → goal check (§2.5) → if it passes, the blocked page is **re-checked with the new goal** and unblocked only if it fits. The user also chooses "add to list" or "just this session".

---

## 4. Basic mode: closest-case search (spec §5.9 step 3)

Runs only in basic mode, only for pages whose embedding match is **unclear**.

### 4.1 What is searched
- **One search over everyone's stored decisions.** Closest cases decide, whoever made them. No "own history first", no extra weight for the user's own decisions. *(Kept as a later option: switch to own-history-first if the eval shows it's better.)*
- A case is close when **both** match: similar page **and** similar goal.

### 4.2 How (one combined vector)
1. Every stored decision has a **combined vector** = `[extracted-page vector (384) , goal vector (384)]`, both unit length.
   - The page part always uses the **extracted summary** (title, meta, headings, YouTube channel/category/tags), even when the decision itself was made with an LLM summary. Basic mode only has extracted text, so both sides must be the same kind.
2. For the unclear page, build `[p , g]` the same way. With several active goals, run the search once per goal and keep the best results.
3. **pgvector** returns the **top 20** nearest by combined distance (HNSW index). Because both halves have length 1, the dot product = page similarity + goal similarity.
4. Keep only candidates with **page similarity ≥ 0.9 and goal similarity ≥ 0.9** (starting values, in config, tuned by the eval).
5. **Weighted vote** over the closest remaining cases (up to 5): vote = source weight × combined similarity.

### 4.3 Source weights (starting values, tuned by the eval)
| Decision source | Weight |
|---|---|
| Confirmed by a user (floating-prompt answer, appeal outcome, "this was a distraction" report) | 3 |
| LLM judge (`llm`) | 2 |
| Embedding match on an LLM summary (`embedding`) | 1.5 |
| Basic mode (`extracted`) | 0.5 |
| Copied from neighbours (`nearest`) | 0 — never votes, so guesses can't copy guesses |
| Fallback allow (`fallback`) | 0 |

- **No fading by age.** Every stored decision counts fully.
- **Repeats:** one row per user + page + goal, with a **visit count** and last-seen time. Repeat visits don't add votes.
- **Minimum evidence:** a cross-user copy needs votes from **at least 2 different people**; otherwise it's "too little evidence" (§5). A user's own confirmed decision for the same page + goal decides for them alone.
- The result is saved with `source = "nearest"`.

---

## 5. Floating prompt: "Is this a distraction?"

### 5.1 When it appears
All of these must be true:
1. Basic mode is active.
2. The embedding match is **unclear**.
3. The closest-case search finds **too little evidence**.

It never appears in normal mode (the LLM judge handles unclear pages there). Asking is also a feature: it makes users notice their own drifting.

### 5.2 Look and behaviour
- A small floating window at the **side of the page**, not prominent, visible for **15 seconds**.
- **No daily cap.** (A page + goal that was answered once has evidence afterwards, so it isn't asked again.)
- Buttons: **Yes** / **No**.
  - **Yes (distraction):** the page is blocked; saved as a **confirmed block** (weight 3).
  - **No (not a distraction):** the page stays allowed; saved as a **confirmed allow** (weight 3), with an **optional one-line reason**.
  - **Ignored for 15 s:** the page stays allowed; **nothing is saved**.
- Answers are shared with other users through the closest-case search (subject to the 2-people rule).

### 5.3 Reasons
Stored privately with the decision. Used for analytics and for building the eval dataset. Never shown to other users.

---

## 6. Data and storage

### 6.1 Tools
| Search | Tool | Notes |
|---|---|---|
| **Decisions** (basic mode, §4) | **pgvector** in Postgres | Vectors in the same row as decision, source, user, time: one query returns everything the vote needs |
| **Summaries** (normal mode content-facts cache) | **FAISS** in the Python service | Chosen so the developer learns both tools. **Vectors are also stored in Postgres**, so FAISS can be rebuilt any time |

Each search sits behind a small interface (`SummaryIndex`, `DecisionIndex` with `search(vector, k)` / `add(...)`), so switching either one to the other tool changes one file.

### 6.2 Collection and consent
- Decision data is **collected for everyone, on by default, no opt-out**, stated in the privacy statement as being used for reliability.
- **Delete-my-data must remove every row of that user** (decisions, goals, reasons) — required by GDPR and India's DPDP Act even without an opt-out.

### 6.3 Retention (changes main spec §8)
- Decisions are **kept with the user ID** (no 30-day deletion). Stated purposes:
  1. The user's own **decision history in the dashboard**.
  2. **Personalised search** later (e.g. switching to own-history-first).
- Users can delete single entries and all their history from the dashboard.

### 6.4 Schema changes (Postgres)
**`verdicts`** (one row per user + page + goal):
`id, user_id, session_id, content_key, goal_id, decision, reason_shown, source, weight, confirmed bool, user_reason text NULL, page_vec_extracted vector(384), goal_vec vector(384), combined_vec vector(768) [HNSW index], visit_count int, first_seen ts, last_seen ts`

**`goals`** (new):
`id, user_id, text, vec vector(384), kind (saved | session | inferred), status (active | pending | rejected), created_at`

**`content_facts`**: unchanged, plus `page_vec vector(384)` (source for the FAISS index).

---

## 7. Eval (how the numbers get set)

The eval (`ai-service/eval/run_eval.py` + `dataset.jsonl`) is a test with known answers: pages + goals labelled allow/block by hand. The script runs each case through the real pipeline and reports accuracy, how often each path decided, and speed.

To tune a number (e.g. the 0.9 closeness), run the eval with several values and keep the one with the best accuracy. Numbers to tune with it:
- normal and basic match thresholds (0.75 / 0.55)
- closest-case closeness (0.9 page, 0.9 goal)
- source weights (3 / 2 / 1.5 / 0.5)
- minimum evidence (2 people)

The dataset needs ~50 real labelled cases (currently 6), plus multi-user cases to test the closest-case search.

---

## 8. Risks and open points

1. **Legal review before launch.** Keeping decisions with user IDs indefinitely needs the stated purposes (§6.3) in the privacy statement and working deletion. A short review by a lawyer is advised.
2. **Storage growth.** No deletion means the `verdicts` table and its HNSW index grow without end. Watch disk and RAM; options later: half-precision vectors, indexing only rows with weight > 0, archiving old rows out of the index.
3. **Prompt fatigue.** No daily cap: watch dismissal rates; add a cap if users ignore most prompts.
4. **Unlimited premium goals.** A very long saved list makes "closest goal wins" allow almost everything when no session goal is set. Watch the appeal and missed-distraction rates for premium users.
5. **Cold start.** Before enough decisions exist, most unclear basic-mode pages end in the floating prompt.
6. **Pending goals in basic mode.** A goal added while no LLM is available doesn't allow pages until it's checked.

---

## 9. Changes needed in the main spec and board

| Where | Change |
|---|---|
| Main spec §4 Intent | Replace with the goal model (§2) and the block-screen goal edit (§3) |
| Main spec §5.9 Basic mode | Step 3 becomes the closest-case search (§4); add the floating prompt (§5) |
| Main spec §8 Retention | Decisions kept with user ID for stated purposes (§6.3) |
| Main spec §9 Pricing | Free: 5 saved goals; premium: unlimited |
| Main spec §11 / §13 | pgvector for decisions, FAISS for summaries (§6.1) |
| Board frame 7 / 9 (goals) | Goal layers, goal check, add-to-list vs session-only |
| Board frame 6 (block screen) | Goal shown + Edit goal + recheck |
| Board frame 10 (schema) | New `goals` table; `verdicts` columns (§6.4) |
| Board frame 15 (basic mode) | Closest-case search across everyone, weights, floating prompt |
