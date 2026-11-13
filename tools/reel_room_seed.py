#!/usr/bin/env python3
"""
reel_room_seed.py - turn a day's brief into the documents the Reel Room app shows.

Writes one JSON file per document plus batch.json, the `writes` list for the
ArtifactData tool's "batch" action. Claude runs this, then sends the batch.

Usage
  python3 tools/reel_room_seed.py 2026-11-13 --out /tmp/seed [--ideas]
"""
import argparse, json, os, re

def caption_from(md):
    m = re.search(r"## Caption\s+.*?```\n(.*?)```", md, re.S)
    if not m:
        return ""
    paras = m.group(1).strip().split("\n\n")
    # unwrap hard line breaks inside paragraphs; the footer after the dash keeps its lines
    return "\n\n".join(p if p.lstrip().startswith("\u2014") else " ".join(p.split("\n")) for p in paras)

def table_after(md, heading):
    m = re.search(r"## " + re.escape(heading) + r"\s+(.*?)(?=\n## |\Z)", md, re.S)
    rows = []
    for line in (m.group(1) if m else "").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and not set(cells[0]) <= set("-: "):
            rows.append(cells)
    return rows[1:]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("date"); ap.add_argument("--out", required=True)
    ap.add_argument("--ideas", action="store_true", help="also seed ideas from queue.md")
    a = ap.parse_args()
    d = f"output/reels/daily/{a.date}"
    brief = json.load(open(f"{d}/brief.json", encoding="utf-8"))
    md = open(f"{d}/brief.md", encoding="utf-8").read()
    os.makedirs(a.out, exist_ok=True)
    writes = []
    def put(collection, doc_id, data):
        path = os.path.join(a.out, f"{collection.replace('/', '_')}_{doc_id}.json")
        json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        writes.append({"op": "set", "collection": collection, "doc_id": doc_id, "file_path": path})

    verify = [{"item": f"{r[0]} ({r[1]})".replace("`", ""), "from": "Get it from: " + r[2], "done": False}
              for r in table_after(md, "Verify before recording") if len(r) >= 3]
    setup = [
        "Rear camera, 1x lens, vertical, 1080p at 30. Each clip must be under 20 MB, so not 4K.",
        "HDR video off. Lock focus and exposure on your face.",
        "One clip per line. Leave a second of silence before and after you speak.",
        "Leave the top fifth of the frame empty above your head for the text card.",
        "Clip-on or wired mic. Play one clip back with headphones before shooting the rest.",
    ]
    m = re.search(r"## Order to shoot in.*?\n(.*?)(?=\n## )", md, re.S)
    for line in (m.group(1) if m else "").splitlines():
        if re.match(r"\d+\.", line.strip()):
            setup.append("Shoot order " + re.sub(r"[*`]", "", line.strip()))
    put("reels", a.date, {
        "date": a.date, "title": brief["title"], "formula": brief.get("formula", ""),
        "why": brief.get("source", ""), "target_seconds": brief.get("target_seconds", 30),
        "status": "shooting", "caption": caption_from(md), "verify": verify, "setup": setup,
    })
    for b in brief["beats"]:
        put(f"reels/{a.date}/beats", b["id"], {k: b.get(k) for k in
            ("say", "screen", "shot", "framing", "angle", "move", "location", "broll", "punch")})
    put("meta", "current", {"reel": a.date})
    if a.ideas:
        q = open(".claude/instagram/queue.md", encoding="utf-8").read()
        for line in q.splitlines():
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if line.startswith("|") and c[0].isdigit():
                put("ideas", f"q{int(c[0]):02d}", {"n": int(c[0]), "topic": c[1], "formula": c[2],
                    "evidence": re.sub(r"`", "", c[3]), "status": "queued", "from": "claude"})
    json.dump(writes, open(os.path.join(a.out, "batch.json"), "w"), indent=1)
    print(len(writes), "writes ->", os.path.join(a.out, "batch.json"))

if __name__ == "__main__":
    main()
