#!/usr/bin/env python3
"""
reel_edit.py - cut a Reel from the day's brief and the clips you recorded.

You record one clip per beat. The brief (brief.json) says what each beat says
and what text goes on screen. This script does the mechanical edit:

  1. finds the clip for each beat           b01.mp4, b02.mov ... in the footage folder
  2. trims the dead air off both ends       (or uses in/out from an edit map)
  3. swaps in a cutaway if you shot one     b05_broll.mp4 plays over b05's audio
  4. reframes everything to 1080x1920, 30fps, with an optional punch-in
  5. joins the beats in order
  6. burns in the hook card, text cards and captions, inside Instagram's safe zone
  7. levels the audio to -14 LUFS and exports H.264/AAC

It does not choose takes or judge performance. The reel-editor agent does that
by watching the clips (tools/reel_watch.py) and writing an edit map; this
script then renders exactly what the map says.

File naming in the footage folder
  b01.mp4            you saying beat 1 (any video extension)
  b01_take2.mp4      another take; the newest file wins unless the map names one
  b05_broll.mp4      cutaway for beat 5, shown over the b05 audio
  A beat with only a _broll clip plays silent for `seconds` (default 3).

Edit map (optional, --map edit.json), written by the reel-editor agent
  {"b01": {"file": "b01_take2.mp4", "in": 0.42, "out": 3.10},
   "b05": {"broll": "b05_broll.mp4", "broll_in": 1.0}}

Usage
  python3 tools/reel_edit.py output/reels/daily/2026-11-13/brief.json \
      footage/2026-11-13 --out output/reels/daily/2026-11-13/final.mp4

Needs ffmpeg and ffprobe. Shoot with HDR off; HDR clips come out washed.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

W, H, FPS = 1080, 1920, 30
VIDEO_EXT = (".mp4", ".mov", ".m4v", ".mkv", ".webm")
PUNCH = 1.08
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
       "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]

# Safe zone on 1080x1920: keep text between y=230 and y=1440, off the right 230px.
ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,{font},84,&H00FFFFFF,&H00FFFFFF,&H003C16D4,&H003C16D4,-1,0,0,0,100,100,0,0,3,16,0,8,60,250,270,1
Style: Card,{font},70,&H00FFFFFF,&H00FFFFFF,&H000A0A0A,&H000A0A0A,-1,0,0,0,100,100,0,0,3,14,0,8,60,250,270,1
Style: Cap,{font},60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,260,520,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def run(cmd, check=True):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if check and p.returncode:
        sys.exit("ffmpeg failed:\n  " + " ".join(cmd) + "\n" + p.stderr[-1500:])
    return p


def probe(path):
    d = json.loads(run(["ffprobe", "-v", "error", "-print_format", "json",
                        "-show_format", "-show_streams", path]).stdout)
    return {"duration": float(d["format"]["duration"]),
            "audio": any(s["codec_type"] == "audio" for s in d["streams"])}


def find_clips(folder):
    """{'b01': {'aroll': path, 'broll': path}}, newest file wins per slot."""
    clips = {}
    files = [f for f in os.listdir(folder) if f.lower().endswith(VIDEO_EXT)]
    for f in sorted(files, key=lambda f: os.path.getmtime(os.path.join(folder, f))):
        m = re.match(r"(b\d{2})(.*)\.\w+$", f, re.IGNORECASE)
        if m:
            slot = "broll" if "broll" in m.group(2).lower() else "aroll"
            clips.setdefault(m.group(1).lower(), {})[slot] = os.path.join(folder, f)
    return clips


def speech_bounds(path, dur):
    """Trim silence at the head and tail. Returns (in, out)."""
    p = run(["ffmpeg", "-hide_banner", "-i", path, "-vn",
             "-af", "silencedetect=noise=-35dB:d=0.25", "-f", "null", "-"], check=False)
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    t_in, t_out = 0.0, dur
    if starts and starts[0] <= 0.05 and ends:
        t_in = max(0.0, ends[0] - 0.08)
    if starts and len(starts) > len(ends):                  # silence runs to the end
        t_out = min(dur, starts[-1] + 0.12)
    elif starts and ends and abs(ends[-1] - dur) < 0.1 and starts[-1] > t_in:
        t_out = min(dur, starts[-1] + 0.12)
    return (t_in, t_out) if t_out - t_in > 0.4 else (0.0, dur)


def vf(punch):
    z = PUNCH if punch else 1.0
    sw, sh = int(W * z) // 2 * 2, int(H * z) // 2 * 2
    return (f"scale={sw}:{sh}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},fps={FPS},setsar=1,format=yuv420p")


def render_beat(beat, clip, emap, dest):
    aroll = os.path.join(emap["_dir"], emap["file"]) if emap.get("file") else clip.get("aroll")
    broll = os.path.join(emap["_dir"], emap["broll"]) if emap.get("broll") else clip.get("broll")
    punch = bool(beat.get("punch"))
    if aroll:
        info = probe(aroll)
        if not beat.get("say"):                                # silent shot: hold for its set time
            auto_in, auto_out = 0.0, min(info["duration"], float(beat.get("seconds", 3)))
        elif info["audio"]:
            auto_in, auto_out = speech_bounds(aroll, info["duration"])
        else:
            auto_in, auto_out = 0.0, info["duration"]
        t_in, t_out = float(emap.get("in", auto_in)), float(emap.get("out", auto_out))
        dur = t_out - t_in
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
               "-ss", f"{t_in:.3f}", "-t", f"{dur:.3f}", "-i", aroll]
        if broll:
            cmd += ["-ss", f"{float(emap.get('broll_in', 0)):.3f}", "-i", broll]
            vsrc, vfilter = "1:v", vf(False) + f",tpad=stop_mode=clone:stop_duration={dur:.3f}"
        else:
            vsrc, vfilter = "0:v", vf(punch)
        if info["audio"]:
            asrc = ["-map", "0:a"]
        else:
            cmd += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
            asrc = ["-map", f"{2 if broll else 1}:a"]
        cmd += ["-map", vsrc, *asrc, "-vf", vfilter, "-t", f"{dur:.3f}", *ENC, dest]
        source = os.path.basename(broll or aroll) + (" over " + os.path.basename(aroll) if broll else "")
    else:                                                    # cutaway only, no speech
        dur = min(probe(broll)["duration"], float(beat.get("seconds", 3)))
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
               "-ss", f"{float(emap.get('broll_in', 0)):.3f}", "-i", broll,
               "-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
               "-map", "0:v", "-map", "1:a", "-vf", vf(punch), "-t", f"{dur:.3f}", *ENC, dest]
        source = os.path.basename(broll) + " (silent)"
    run(cmd)
    return probe(dest)["duration"], source


def ts(t):
    h, rem = divmod(max(t, 0), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def clean(text):
    return text.replace("{", "(").replace("}", ")").replace("\n", " ").strip()


def wrap(text, width):
    if "\n" in text:                                         # stacked card: keep the author's lines
        return r"\N".join(wrap(part, width + 12) for part in text.split("\n") if part.strip())
    lines, cur = [], ""
    for w in clean(text).split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return r"\N".join(lines + [cur])


def caption_chunks(line, start, dur, words_per=3):
    words = clean(line).split()
    groups = [" ".join(words[i:i + words_per]) for i in range(0, len(words), words_per)]
    total = sum(len(g) for g in groups) or 1
    t, out = start, []
    for g in groups:
        d = dur * len(g) / total
        out.append((t, t + d, g))
        t += d
    return out


def build_ass(timeline, font, captions):
    rows = []
    for i, (beat, start, dur) in enumerate(timeline):
        if beat.get("screen"):
            style = "Hook" if i == 0 else "Card"
            rows.append(f"Dialogue: 1,{ts(start)},{ts(start + dur)},{style},,0,0,0,,"
                        + wrap(beat["screen"], 16))
        if captions and beat.get("say"):
            for a, b, text in caption_chunks(beat["say"], start, dur):
                rows.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{text}")
    return ASS_HEAD.format(font=font) + "\n".join(rows) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Cut a Reel from a brief and a folder of clips.")
    ap.add_argument("brief", help="brief.json")
    ap.add_argument("footage", help="folder of clips named b01.mp4, b05_broll.mp4 ...")
    ap.add_argument("--out", required=True)
    ap.add_argument("--map", help="edit map json from the reel-editor agent")
    ap.add_argument("--font", default="Inter")
    ap.add_argument("--no-captions", action="store_true")
    ap.add_argument("--keep", action="store_true", help="keep the work folder")
    ap.add_argument("--draft", action="store_true",
                    help="render even if {{placeholders}} are still in the brief")
    a = ap.parse_args()

    brief = json.load(open(a.brief, encoding="utf-8"))
    holes = [b["id"] for b in brief["beats"]
             if "{{" in (b.get("say") or "") + (b.get("screen") or "")]
    if holes and not a.draft:
        sys.exit("unfilled {{placeholders}} in: " + ", ".join(holes)
                 + "\nput the real figures in brief.json, or pass --draft for a rough cut")
    emap = json.load(open(a.map, encoding="utf-8")) if a.map else {}
    clips = find_clips(a.footage)
    missing = [b["id"] for b in brief["beats"]
               if not clips.get(b["id"]) and not (emap.get(b["id"], {}).get("file")
                                                  or emap.get(b["id"], {}).get("broll"))]
    if missing:
        sys.exit("no clip for: " + ", ".join(missing)
                 + f"\nrecord them as e.g. {missing[0]}.mp4 into {a.footage}")

    work = tempfile.mkdtemp(prefix="reel_")
    timeline, report, t = [], [], 0.0
    for beat in brief["beats"]:
        seg = os.path.join(work, beat["id"] + ".mp4")
        dur, source = render_beat(beat, clips.get(beat["id"], {}),
                                  {**emap.get(beat["id"], {}), "_dir": a.footage}, seg)
        timeline.append((beat, t, dur))
        report.append({"beat": beat["id"], "start": round(t, 2), "seconds": round(dur, 2),
                       "source": source, "flag": "over 4.5s, tighten or add a cutaway"
                       if dur > 4.5 else None})
        t += dur

    lst = os.path.join(work, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{os.path.join(work, b['id'] + '.mp4')}'\n" for b in brief["beats"])
    joined = os.path.join(work, "joined.mp4")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", joined])

    ass = os.path.join(work, "text.ass")
    open(ass, "w", encoding="utf-8").write(build_ass(timeline, a.font, not a.no_captions))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    esc = ass.replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", joined,
         "-vf", f"ass='{esc}'", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
         *ENC, "-movflags", "+faststart", a.out])

    target = float(brief.get("target_seconds", 30))
    summary = {"out": a.out, "seconds": round(t, 2), "target_seconds": target,
               "length_flag": None if abs(t - target) <= 5 else
               f"{t - target:+.1f}s against target", "beats": report}
    rep = os.path.splitext(a.out)[0] + ".edit.json"
    json.dump(summary, open(rep, "w"), indent=2)
    if not a.keep:
        shutil.rmtree(work, ignore_errors=True)
    flags = [r for r in report if r["flag"]]
    print(f"{a.out}: {t:.1f}s across {len(report)} beats (target {target:.0f}s), "
          f"{len(flags)} beat flag(s). Report: {rep}")
    for r in flags:
        print(f"  {r['beat']}: {r['seconds']}s - {r['flag']}")


if __name__ == "__main__":
    main()
