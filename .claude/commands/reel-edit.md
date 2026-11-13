---
description: Edit a day's Reel from the clips in footage/<date>/ and QC the result
argument-hint: <date, e.g. 2026-11-13>
---

Edit the reel for `$ARGUMENTS` (if blank, the newest folder under `footage/`).

Run this where the footage is. Raw clips are too big to send to a cloud
session, so this is normally Claude Code on Nick's own computer, in this repo,
with `ffmpeg` installed (`brew install ffmpeg`) and `pip install pillow`.

1. Check `output/reels/daily/<date>/brief.json` and `footage/<date>/` exist.
   If the footage folder is missing or empty, say exactly where to put the
   clips and how to name them, and stop.
2. Hand the job to the **reel-editor** agent (Sonnet): watch the takes, pick
   one per beat, write `edit.json`, render `final.mp4`, check its own render.
   Fallback: general-purpose agent with `model: sonnet` and the text of
   `.claude/agents/reel-editor.md`.
3. Hand the result to the **reel-qc** agent (Sonnet), which did not make the
   edit: PASS or FAIL per check, then POST, FIX or RESHOOT.
4. If the verdict is FIX and the fix is in the edit (trim, take choice, text),
   send it back to the editor once, then QC again.
5. Report: verdict, path to `final.mp4`, length, takes chosen, flags left,
   beats to reshoot. Do not post it. Do not commit video files.
