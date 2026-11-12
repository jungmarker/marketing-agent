---
description: Run the reel research team - find what is over-performing in real estate short-form, break it down, and write my versions
---

Run a research team for my Instagram Reels and report back with things I can
shoot this week. $ARGUMENTS

## Who this is for

I'm Nick Jungmarker, a REALTOR with Long & Foster in Baltimore. I work mostly
with first-time buyers and rowhouse buyers and sellers, in English and Spanish.
My account is small, so what works for a 2M-follower account is not evidence
for me. Brand details and the compliance footer are in `config.py`. My voice
is in `.claude/instagram/voice.md`; if it is still blank, ask me for three of
my own reels before writing scripts, and write drafts in a plain voice
meanwhile, labelled as such.

## What "successful" means

Rank by how far a video beat its own account's median, not by raw views. 3x or
more is a signal. Under 1.5x is that account's normal day. I care about formats
a solo agent with a phone can repeat, and about reels that bring buyer and
seller conversations in Baltimore, more than about views from people who will
never move here.

## The team

Use the `ig-viral` skill as the method and split the work across agents:

1. **Scouts (2 to 3, in parallel).** Find and verify accounts: local agents in
   rowhouse cities (Baltimore, DC, Philadelphia), consumer-facing agents
   elsewhere within about 10x of my size, Spanish-language agents and lenders,
   adjacent creators with my audience (lenders, inspectors), and a few very
   large accounts for format only. Start from `.claude/instagram/accounts.txt`
   and add to it.
2. **Collector.** Instagram cannot be read without my login, and you never log
   in for me or ask for a password. Use public YouTube Shorts from the same
   creators (`.claude/skills/ig-viral/shorts_pull.py`), and ask me for my Saved
   collection or screenshots if you want Instagram numbers. Read at human
   volume. No scraping service, no background loop.
3. **Breakdown.** For the top outliers, capture the first spoken line, the
   on-screen text, length, shot type, cut pace and the ask. If you could only
   get titles, say so. Read published breakdowns for production detail and
   mark those as self-reported.
4. **Analyst.** Run `swipe.py`. Tell me which shapes beat the base rate, with
   counts, what the top third share that the bottom third lack, and what the
   classifier could not name. State the sample size and how much to trust it.
5. **Writer.** Turn the top three shapes into my versions with `ig-reel`: three
   scored hook options, a spoken script, a separate on-screen text list, a
   timed shot list, and a Spanish hook where it fits. Run `beats.py` and the
   humanizer and show me the scores, including the bad ones.

## Rules

- Copy the shape, never the video. Credit every row to the account it came from.
- Never invent a number, a client or a result under my name. Use
  `{{placeholder}}` and tell me where to get the real figure.
- Fair housing: describe places and facts, never who an area is for.
- Do not post, follow, like, comment or message anything.
- If a source is blocked, tell me what you could not see and carry on. Do not
  fill the gap with guesses.

## What I want back

1. The ranked findings in a short table, with the caveats up top.
2. The setup: framing, text placement, length, cuts, sound, the ask, each
   marked by how good the evidence is.
3. Three ready-to-shoot reels as beat tables.
4. What to stop making.
5. `.claude/instagram/swipe.md` and `accounts.txt` updated, and the playbook
   saved under `output/reels/` with today's date.
6. One line on how this prompt should change next time, based on what got in
   your way.
