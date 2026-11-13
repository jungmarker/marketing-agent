---
description: The daily reel run - refresh the data, pick today's reel, write the full shoot brief, report
---

This is the daily reel run for Nick Jungmarker (Baltimore REALTOR, Long &
Foster). It runs unattended every morning. Work in `/home/user/marketing-agent`.
Use the date in America/New_York (`TZ=America/New_York date +%F`) as `<date>`.
$ARGUMENTS

## 0. Get the repo into shape

- `git fetch origin claude/dreamy-allen-ihb240 && git checkout claude/dreamy-allen-ihb240 && git pull`
  (skip quietly if already there and clean).
- `python3 -m yt_dlp --version || pip install -q yt-dlp`.
- `mkdir -p ~/.claude/instagram && cp .claude/instagram/*.md ~/.claude/instagram/`
  (the ig-* skills read from there; the repo copy is the one that persists).
- If `output/reels/daily/<date>/brief.md` already exists, report that and stop.

## 0.5 Check the Reel Room first

Read `.claude/commands/reel-room.md` and do its "Each time this runs" steps:
answer Nick's notes, pull and review new clips, cut if he marked it ready.

Then decide whether today gets a new brief:
- The app's current reel has clips and is not `approved`: he is mid-shoot. Do
  not replace it. Skip steps 4 to 6, still do steps 1 to 3, and report.
- Otherwise write today's brief as below. If an idea in the app has
  `status: "next"`, that is today's topic.

## 1. Scout (reel-scout agent, Haiku)

Read `.claude/instagram/accounts.txt`. Take today's slice: sort the handles,
and pull the ones whose index modulo 5 equals the day of the year modulo 5
(about six channels a day, so every account is refreshed each five days).
On Mondays also ask the scout for up to three new accounts.

If the scout agent type is not available, use a general-purpose agent with
`model: haiku` and give it the text of `.claude/agents/reel-scout.md`.

If YouTube is blocked or every pull fails, do not stop: note it and carry on
from the existing swipe file.

## 2. Watch (reel-watcher agent, Sonnet) - only if there is something to watch

Look in `inbox/reference/` for video files with no `breakdown.md` beside them
(reels Nick saved or screen-recorded). Run one watcher per file, at most four.
Their breakdowns feed step 3. An empty inbox is normal; skip the step.

## 3. Analyse and pick (you, the lead)

- On Mondays, or when the scout found a new outlier at 5x or more, rerun
  `python3 .claude/skills/ig-viral/swipe.py .claude/instagram/captured.tsv`
  and update the findings section of `.claude/instagram/swipe.md` by hand.
  Other days, append new outliers to its table and leave the findings alone.
- Read `.claude/instagram/queue.md` and `.claude/instagram/log.md`. Pick
  today's reel: the top queue item whose formula was not used in the last two
  briefs. Prefer an idea tied to a new outlier from step 1 or a breakdown from
  step 2. If the queue has fewer than five items, add ideas until it has ten,
  each with topic, formula id and the evidence row it comes from.
- Check `output/reels/daily/` for a previous day with footage notes or an
  audit, and `log.md` for results Nick reported. What he says worked outranks
  the swipe file.

## 4. Write (reel-writer agent, Opus)

Give the writer the topic, formula, evidence and `<date>`. It writes
`output/reels/daily/<date>/brief.md` and `brief.json` in the exact format of
the newest existing brief: hook options with scores, shot list with framing,
angle, camera move and location per clip, b-roll list with seconds, shoot
order, gear, caption with compliance footer, Spanish hook, verify list,
editor hand-off, scores.

Fallback: general-purpose agent with `model: opus` and the text of
`.claude/agents/reel-writer.md`.

## 5. Check the brief yourself

- `python3 -c "import json;json.load(open('output/reels/daily/<date>/brief.json'))"`.
- Every beat has `id`, `say`, `shot`, `framing`, `angle`, `move`, `location`.
- No number without a source or a `{{placeholder}}`. No line about who a
  neighborhood is for. Caption ends with the footer from `config.py`.
- Fix small problems directly. Send it back to the writer once for big ones.

## 6. Record it

- Move the idea from `queue.md` to `log.md` with the date, formula and hook.
- `git add -A && git commit` with a one-line message, then
  `git push -u origin claude/dreamy-allen-ihb240`. Never commit video files.

## 6.5 Post it to the Reel Room

`python3 tools/reel_room_seed.py <date> --out <scratch dir>` and send its
`batch.json` as one `ArtifactData` batch to
https://claude.ai/artifact/3D41X8Zzymk61zSMCMAc1K, then add a note from
`claude` saying the shot list is up. Nick works from the app, not from files.

## 7. Report to Nick

Short, in this order: today's reel in one line with the spoken hook; how long
the shoot takes and where; the clip list (ids and lines) and b-roll list; what
he must verify before recording; anything new in the data (new outliers,
accounts added); anything that failed. Then the Reel Room link.

## Never

Post, schedule a post, follow, like, comment or message. Log into Instagram.
Invent a number, a client or a result. Download other creators' videos.
