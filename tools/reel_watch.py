#!/usr/bin/env python3
"""
reel_watch.py - turn a video file into something a vision model can "watch".

Claude models do not take video. They take images and text. So watching a reel
means: measure it with ffmpeg (length, cut times, when sound starts), pull the
frames that matter (the first three seconds, then one frame per shot), lay them
out as labelled contact sheets, and add a transcript when a speech-to-text tool
is installed. The watcher agent then reads the sheets and watch.json.

Works on any local video: a reference reel you screen-recorded or saved, your
own raw takes, or a finished edit that needs a QC pass.

Usage
  python3 tools/reel_watch.py video.mp4 --out watch/video
  python3 tools/reel_watch.py final.mp4 --out qc --safe     # draw the IG safe zone

Writes  <out>/watch.json  <out>/hook.jpg  <out>/shots.jpg  (+ transcript.txt)
Needs   ffmpeg, ffprobe, Pillow.  Optional: the `whisper` CLI for a transcript.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

THUMB_W, THUMB_H = 270, 480          # 9:16 thumbnails
SAFE = (230, 1440, 230)              # top y, bottom y, right margin on 1080x1920


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    p = run(["ffprobe", "-v", "error", "-print_format", "json",
             "-show_format", "-show_streams", path])
    d = json.loads(p.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s["codec_type"] == "video"), None)
    a = next((s for s in d.get("streams", []) if s["codec_type"] == "audio"), None)
    if not v:
        sys.exit(f"no video stream in {path}")
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    w, h = int(v["width"]), int(v["height"])
    rot = str((v.get("side_data_list") or [{}])[0].get("rotation", "0"))
    if rot.lstrip("-") in ("90", "270"):
        w, h = h, w
    return {
        "duration": round(float(d["format"]["duration"]), 2),
        "width": w, "height": h,
        "fps": round(float(num) / float(den), 2) if float(den) else None,
        "has_audio": a is not None,
        "vertical_9x16": abs(w / h - 9 / 16) < 0.02,
    }


def cut_times(path, threshold):
    p = run(["ffmpeg", "-hide_banner", "-i", path, "-an",
             "-vf", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"])
    return [round(float(t), 2) for t in re.findall(r"pts_time:([\d.]+)", p.stderr)]


def first_sound(path):
    p = run(["ffmpeg", "-hide_banner", "-i", path, "-vn",
             "-af", "silencedetect=noise=-35dB:d=0.2", "-f", "null", "-"])
    starts = re.findall(r"silence_start: (-?[\d.]+)", p.stderr)
    ends = re.findall(r"silence_end: ([\d.]+)", p.stderr)
    if starts and float(starts[0]) <= 0.05 and ends:
        return round(float(ends[0]), 2)
    return 0.0


def grab(path, t, dest):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.2f}",
         "-i", path, "-frames:v", "1",
         "-vf", f"scale={THUMB_W}:{THUMB_H}:force_original_aspect_ratio=decrease,"
                f"pad={THUMB_W}:{THUMB_H}:(ow-iw)/2:(oh-ih)/2",
         dest])
    return os.path.exists(dest)


def font(size):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/Library/Fonts/Arial Bold.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def sheet(frames, dest, cols, safe):
    """frames: [(label, jpg_path)]"""
    if not frames:
        return
    rows = -(-len(frames) // cols)
    pad, bar = 8, 30
    img = Image.new("RGB", (cols * (THUMB_W + pad) + pad,
                            rows * (THUMB_H + bar + pad) + pad), (18, 18, 18))
    d, f = ImageDraw.Draw(img), font(18)
    for i, (label, jpg) in enumerate(frames):
        x = pad + (i % cols) * (THUMB_W + pad)
        y = pad + (i // cols) * (THUMB_H + bar + pad)
        img.paste(Image.open(jpg).convert("RGB"), (x, y + bar))
        d.text((x + 4, y + 5), label, fill=(255, 255, 255), font=f)
        if safe:
            k = THUMB_H / 1920
            d.rectangle([x, y + bar + SAFE[0] * k,
                         x + THUMB_W - SAFE[2] * k, y + bar + SAFE[1] * k],
                        outline=(0, 255, 120), width=2)
    img.save(dest, quality=88)


def transcript(path, out):
    if not shutil.which("whisper"):
        return None
    run(["whisper", path, "--model", "base", "--output_format", "txt",
         "--output_dir", out, "--fp16", "False"])
    txt = os.path.join(out, os.path.splitext(os.path.basename(path))[0] + ".txt")
    if os.path.exists(txt):
        os.replace(txt, os.path.join(out, "transcript.txt"))
        return open(os.path.join(out, "transcript.txt"), encoding="utf-8").read().strip()
    return None


def main():
    ap = argparse.ArgumentParser(description="Make a video readable by a vision model.")
    ap.add_argument("video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--scene", type=float, default=0.30, help="cut sensitivity, 0-1")
    ap.add_argument("--max-shots", type=int, default=24)
    ap.add_argument("--safe", action="store_true", help="draw the Instagram safe zone")
    a = ap.parse_args()

    os.makedirs(os.path.join(a.out, "frames"), exist_ok=True)
    meta = probe(a.video)
    dur = meta["duration"]
    cuts = [c for c in cut_times(a.video, a.scene) if 0.2 < c < dur - 0.2]
    edges = [0.0] + cuts + [dur]
    shots = [{"n": i + 1, "start": edges[i], "end": edges[i + 1],
              "seconds": round(edges[i + 1] - edges[i], 2)}
             for i in range(len(edges) - 1)]
    lengths = [s["seconds"] for s in shots]

    hook = []
    for i, t in enumerate([0.0, 0.5, 1.0, 1.5, 2.0, 2.5]):
        if t < dur:
            p = os.path.join(a.out, "frames", f"hook_{i}.jpg")
            if grab(a.video, t, p):
                hook.append((f"{t:.1f}s", p))
    sheet(hook, os.path.join(a.out, "hook.jpg"), 6, a.safe)

    step = max(1, -(-len(shots) // a.max_shots))
    picks = []
    for s in shots[::step]:
        p = os.path.join(a.out, "frames", f"shot_{s['n']:03d}.jpg")
        if grab(a.video, (s["start"] + s["end"]) / 2, p):
            picks.append((f"#{s['n']}  {s['start']:.1f}s  ({s['seconds']:.1f}s)", p))
    sheet(picks, os.path.join(a.out, "shots.jpg"), 6, a.safe)

    text = transcript(a.video, a.out) if meta["has_audio"] else None
    report = {
        "file": os.path.basename(a.video), **meta,
        "cuts": len(cuts),
        "shots": len(shots),
        "avg_shot_seconds": round(sum(lengths) / len(lengths), 2),
        "longest_shot_seconds": max(lengths),
        "first_cut_at": cuts[0] if cuts else None,
        "first_sound_at": first_sound(a.video) if meta["has_audio"] else None,
        "shot_list": shots,
        "transcript": text,
        "transcript_note": None if text else
            "no transcript: install the `whisper` CLI (pip install openai-whisper) to get one",
        "sheets": {"hook": "hook.jpg", "shots": "shots.jpg"},
    }
    json.dump(report, open(os.path.join(a.out, "watch.json"), "w"), indent=2)
    print(f"{report['file']}: {dur}s, {meta['width']}x{meta['height']}, "
          f"{len(shots)} shots, avg {report['avg_shot_seconds']}s, "
          f"longest {report['longest_shot_seconds']}s, "
          f"sound starts {report['first_sound_at']}s -> {a.out}/watch.json")


if __name__ == "__main__":
    main()
