# Parked feature: music allowance + music picking window

Designed on 2026-10-19, then parked for a later phase. Nothing here is live: the main board,
spec and code were reverted to the version without music.

## The feature

- **Music is always allowed.** The content describer labels listening content (songs, albums,
  playlists, streams, any genre, with or without lyrics) as kind `music`. The pipeline allows it
  before the goal match, because music always scores "unrelated" against a study goal.
  Videos *about* music (reactions, reviews) stay `entertainment` and are judged normally.
- **45-second picking window.** Spotify and YouTube Music are music by site rule; on YouTube a page
  is music when the verdict's kind is `music`. The timer runs once per music-site visit (clicking
  more songs doesn't restart it). When time is up, an overlay ("Music's on — back to work") covers
  the page while audio keeps playing.

## Tier (Decided 2026-10-19)

| Free | Premium |
|---|---|
| Music allowed (Spotify, YouTube Music, YouTube music videos); music pages stay open | The **music picking window** (timer, then overlay while audio keeps playing), with an adjustable length (e.g. 30 s / 45 s / 2 min) |

Why: blocking music would make the free product feel broken, while the picking window is a
"focus strength" feature. Rule: gate what costs money or adds power, never what makes free feel broken.

## Files here

| File | What it is |
|---|---|
| `autopilot-focus-music.excalidraw` | The board with the music changes (frames 2, 5, 14), kept in sync with the live board (includes basic mode, frame 15) |
| `diagrams.py` | Source for that board. Run `python diagrams.py` from this folder to regenerate it |
| `previews/` | PNGs of the three changed frames |
| `spec-music.patch` | Spec text (§5.1 exception + §6 "Music picking window") |
| `code-music.patch` | The `music` kind in schemas.py, describer prompt lines, judge rubric |

## Bringing it back

From the repo root:

```bash
git apply .plans/architecture/future/music/spec-music.patch
git apply .plans/architecture/future/music/code-music.patch
```

Then copy the music edits for frames 2, 5 and 14 from this `diagrams.py` into
`.plans/architecture/diagrams.py` (not the whole file: other frames may have changed since),
and add the rule to `pipeline.classify`: `if facts.kind == "music": return allow` before `match`.
The `Verdict` also needs a `kind` field so the extension can start the timer.
