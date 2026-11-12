#!/usr/bin/env python3
"""
shorts_pull.py - build captured.tsv for swipe.py from public YouTube Shorts tabs.

Instagram shows nothing without a login, and the skill never logs in. Most
realtors cross-post the same vertical video to Shorts, where the view counts
are public. This reads the Shorts tab listing for each handle (one request per
channel, newest 40), takes that channel's own median as the baseline, and
writes one row per Short. Run it monthly, on a short list. It is not a crawler.

The `hook` column is the Short's TITLE, in the creator's words. It is a proxy
for the spoken first line, not the line itself. Say so when you report.

Usage
  pip install yt-dlp
  python3 shorts_pull.py accounts.txt --out captured.tsv
  python3 swipe.py captured.tsv --out ../../instagram/swipe.md
"""
import argparse, json, re, statistics, subprocess, sys

def pull(handle, n):
    p = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist",
                        "--playlist-end", str(n), "-J",
                        f"https://www.youtube.com/@{handle}/shorts"],
                       capture_output=True, text=True)
    try:
        return json.loads(p.stdout)
    except ValueError:
        return None

def clean(title):
    t = re.sub(r"#\w+", "", title or "")
    t = re.sub(r"[^\x00-\x7FáéíóúñüÁÉÍÓÚÑ¿¡]", "", t)
    return re.sub(r"\s+", " ", t).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("accounts", help="text file, one YouTube handle per line, # for comments")
    ap.add_argument("--out", default="captured.tsv")
    ap.add_argument("--per-channel", type=int, default=40)
    ap.add_argument("--min-shorts", type=int, default=15)
    a = ap.parse_args()
    handles = [l.split("#")[0].strip().lstrip("@") for l in open(a.accounts)]
    rows = []
    for h in filter(None, handles):
        d = pull(h, a.per_channel)
        es = [e for e in (d or {}).get("entries", []) if e and e.get("view_count")]
        if len(es) < a.min_shorts:
            print(f"skip  {h}: {len(es)} shorts readable", file=sys.stderr)
            continue
        med = int(statistics.median(e["view_count"] for e in es))
        print(f"ok    {h}: {len(es)} shorts, median {med:,}", file=sys.stderr)
        for e in es:
            t = clean(e.get("title"))
            if len(t.split()) >= 3:
                rows.append((f"@{h}", d.get("channel_follower_count") or "", med,
                             e["view_count"], t, e["id"]))
    with open(a.out, "w", encoding="utf-8") as o:
        o.write("account\tfollowers\tmedian\tviews\thook\tid\n")
        for r in rows:
            o.write("\t".join(map(str, r)) + "\n")
    print(f"{len(rows)} rows, {len({r[0] for r in rows})} accounts -> {a.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
