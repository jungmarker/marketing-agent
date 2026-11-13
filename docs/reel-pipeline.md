# Reel pipeline

A daily loop that turns what is working in real estate short-form into one
Reel a day for Nick to shoot, then edits what he records.

```
            every morning (cloud, scheduled)                     when you have footage (your computer)
 ┌─────────┐   ┌──────────┐   ┌───────────┐   ┌────────┐         ┌─────────┐   ┌────────┐
 │  scout  │──▶│ watcher  │──▶│   lead    │──▶│ writer │──▶ you ─▶│ editor  │──▶│   qc   │──▶ you post
 │ (Haiku) │   │ (Sonnet) │   │ (session) │   │ (Opus) │  shoot   │ (Sonnet)│   │(Sonnet)│
 └─────────┘   └──────────┘   └───────────┘   └────────┘         └─────────┘   └────────┘
  view data     reference       ranks, picks    brief.md           final.mp4     POST / FIX /
  refresh       breakdowns      today's reel    brief.json         edit.json     RESHOOT
```

## Who does what, and on which model

| Agent | Model | Job | Why that model |
|---|---|---|---|
| `reel-scout` | Haiku 5.5 | Pulls public Shorts listings for about six accounts a day, merges them, lists new outliers, finds new accounts on Mondays | Mechanical: run a script, compare numbers. Cheapest model, runs daily |
| `reel-watcher` | Sonnet 5.5 | Reads contact sheets of a video and writes the shot-by-shot breakdown | Needs vision over many frames. Sonnet reads images well at a fraction of the top model's cost |
| lead (the scheduled session) | the session's model | Ranks, decides today's topic and formula, checks the brief, reports | The one judgement call per day; it also holds the context |
| `reel-writer` | Opus 5.5 | Hooks, spoken script, shot directions, caption | Writing you have to say out loud is where quality shows. One call a day, so cost is small |
| `reel-editor` | Sonnet 5.5 | Watches your takes, picks one per beat, sets trims, renders, checks its render | Vision plus tool use, many frames |
| `reel-qc` | Sonnet 5.5 | Independent pass on the finished cut and caption | A second reader that did not make the edit |

Definitions are in `.claude/agents/`. Change `model:` in a file to move an
agent up or down.

### What "watching" means here

Claude models take images and text, not video. `tools/reel_watch.py` measures
a video with ffmpeg (length, cut times, when sound starts), pulls a frame every
half second for the first 2.5 seconds and one frame per shot after that, and
lays them out as labelled sheets, with a transcript if the `whisper` CLI is
installed. The agent reads those. Limits: a frame every half second can miss a
fast cut, motion is inferred from stills, and it cannot judge audio quality or
delivery. Without `whisper` there is no spoken-line check at all.

### What gets watched

- **Other creators, at scale:** numbers only. View counts and titles from
  public YouTube Shorts listings, ranked against each account's own median.
  No video is downloaded and Instagram is never opened or logged into.
- **Other creators, in detail:** only files you put in `inbox/reference/`
  (a screen recording of a reel you saved). The watcher breaks those down.
- **Your own footage and finished edits:** everything in `footage/<date>/`.

## The daily run

Instructions: `.claude/commands/reel-daily.md`. Scheduled for 5:43 AM Eastern.

1. Sync the repo, install `yt-dlp`.
2. Scout refreshes a fifth of `accounts.txt` (every account each five days).
3. Watcher breaks down anything new in `inbox/reference/`.
4. Lead picks from `queue.md`, never the same formula three briefs running;
   full re-rank of `swipe.md` on Mondays or on a new 5x outlier.
5. Writer produces `output/reels/daily/<date>/brief.md` and `brief.json`.
6. Lead checks it, logs it in `log.md`, commits, pushes.
7. Report: the reel, the clip list, the b-roll list, what to verify.

The original skill says to research monthly because formulas last a season.
The daily run respects that: it refreshes a small slice of data each day and
writes one brief; it does not redo the whole study daily.

## What a brief contains

`brief.md`: why this reel (evidence with numbers), three scored hooks, shot
list (line, on-screen text, action, framing, angle, camera, location per
clip), b-roll list with seconds, shoot order, gear and phone settings,
caption with compliance footer, Spanish hook, verify-before-recording table,
editor hand-off, scores.

`brief.json`: the same beats in a form the editor reads.

## Shooting

One clip per beat, named `b01.mp4`, `b02.mp4`... Cutaways `b05_broll.mp4`.
Extra takes `b01_take2.mp4`. A second of silence either side of each line.
HDR off. Put them in `footage/<date>/`.

## Editing

`/reel-edit <date>` in Claude Code on the computer that holds the footage
(needs `ffmpeg` and `pip install pillow`).

`tools/reel_edit.py` does: trim silence off each clip, lay cutaways over the
spoken audio, reframe to 1080x1920 at 30 fps with an alternating 8% punch-in,
join the beats, burn the hook card (brand red), text cards and three-word
captions inside Instagram's safe zone, level audio to -14 LUFS, export
H.264/AAC. It writes `final.mp4` and `final.edit.json`.

The editor agent adds the judgement: which take, where a false start is, when
a card covers your face. QC then returns POST, FIX or RESHOOT by beat id.

It does not: add music or sound effects, colour grade, tone-map HDR, time
captions to individual words (they are spread evenly across each beat), or
post anything. It refuses a postable render while a `{{placeholder}}` remains.

## Files

| Path | What |
|---|---|
| `.claude/instagram/accounts.txt` | Accounts being tracked |
| `.claude/instagram/captured.tsv` | Raw rows: account, median, views, title |
| `.claude/instagram/swipe.md` | Findings and top outliers |
| `.claude/instagram/queue.md` | Next reels, in order. Edit freely |
| `.claude/instagram/log.md` | What was briefed, shot, posted, and how it did |
| `.claude/instagram/voice.md` | How you talk. Samples still missing |
| `output/reels/daily/<date>/` | Brief, edit map, final cut, QC |
| `footage/<date>/`, `inbox/reference/` | Your clips and reference reels (not in git) |

## Known gaps

- View data is YouTube Shorts, used as a stand-in for Instagram.
- Hooks in the data are titles, not spoken first lines.
- The editor has been run on generated test clips only, not real phone footage.
- Briefs are in a generic voice until `voice.md` has three samples of yours.
- Nothing is checked against Long & Foster's advertising rules.
