/* Reel Room - media: look at a clip on the phone before and after it uploads. */
(function () {
  "use strict";
  var RR = window.RR, S = RR.S, LIMIT = 20 * 1024 * 1024;

  function once(el, ev, ms) {
    return new Promise(function (res, rej) {
      var t = setTimeout(function () { el.removeEventListener(ev, ok); rej(new Error("timeout " + ev)); }, ms);
      function ok() { clearTimeout(t); el.removeEventListener(ev, ok); res(); }
      el.addEventListener(ev, ok);
    });
  }

  /* size, length and three frames, read from the file itself */
  function readVideo(file) {
    var url = URL.createObjectURL(file), v = document.createElement("video");
    v.muted = true; v.playsInline = true; v.preload = "auto"; v.src = url;
    var out = { dur: 0, w: 0, h: 0, frames: [] };
    return once(v, "loadedmetadata", 8000).then(function () {
      out.dur = isFinite(v.duration) ? v.duration : 0; out.w = v.videoWidth; out.h = v.videoHeight;
      var times = [Math.min(0.5, out.dur * 0.15), out.dur / 2, Math.max(out.dur - 0.6, out.dur * 0.85)];
      var cw = 360, ch = Math.round(cw * (out.h || 16) / (out.w || 9)), c = document.createElement("canvas");
      c.width = cw; c.height = ch;
      return times.reduce(function (p, t) {
        return p.then(function () {
          v.currentTime = t;
          return once(v, "seeked", 3500).then(function () {
            c.getContext("2d").drawImage(v, 0, 0, cw, ch);
            return new Promise(function (r) { c.toBlob(function (b) { if (b) out.frames.push(b); r(); }, "image/jpeg", 0.72); });
          });
        });
      }, Promise.resolve());
    }).then(function () { return out; }, function () { return out; }).then(function (o) { URL.revokeObjectURL(url); return o; });
  }

  /* where the talking starts and stops, how loud it is, and a small waveform */
  function readAudio(file) {
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return Promise.resolve(null);
    var ctx;
    return file.arrayBuffer().then(function (buf) {
      ctx = new AC();
      return new Promise(function (res, rej) { var p = ctx.decodeAudioData(buf, res, rej); if (p && p.catch) p.catch(rej); });
    }).then(function (a) {
      var d = a.getChannelData(0), sr = a.sampleRate, win = Math.floor(sr * 0.02), n = Math.floor(d.length / win), rms = new Float32Array(n), peak = 0, i, j;
      for (i = 0; i < n; i++) { var s = 0; for (j = 0; j < win; j++) { var x = d[i * win + j]; s += x * x; var ax = x < 0 ? -x : x; if (ax > peak) peak = ax; } rms[i] = Math.sqrt(s / win); }
      var top = 0; for (i = 0; i < n; i++) if (rms[i] > top) top = rms[i];
      var th = Math.max(0.012, top * 0.14), first = -1, last = -1;
      for (i = 0; i < n - 2; i++) if (rms[i] > th && rms[i + 1] > th && rms[i + 2] > th) { first = i; break; }
      for (i = n - 1; i > 1; i--) if (rms[i] > th && rms[i - 1] > th) { last = i; break; }
      var bins = 64, peaks = [];
      for (i = 0; i < bins; i++) { var m = 0, a0 = Math.floor(i * n / bins), a1 = Math.floor((i + 1) * n / bins); for (j = a0; j < a1; j++) if (rms[j] > m) m = rms[j]; peaks.push(top ? Math.round(100 * m / top) : 0); }
      var dur = a.duration;
      return { dur: dur, peak: peak, loud: top, peaks: peaks, silent: first < 0,
        in: first < 0 ? 0 : Math.max(0, first * 0.02 - 0.08), out: last < 0 ? dur : Math.min(dur, (last + 1) * 0.02 + 0.15) };
    }).then(function (r) { try { ctx.close(); } catch (_) {} return r; }, function () { try { ctx && ctx.close(); } catch (_) {} return null; });
  }

  /* instant checks, no network: these are facts about the file */
  RR.checks = function (beat, kind, v, a, size) {
    var out = [], target = RR.sayTime(beat.say), spoken = a ? a.out - a.in : 0;
    if (v.w && v.h) {
      out.push(v.h > v.w ? { level: "ok", label: "Vertical", detail: v.w + "×" + v.h }
        : { level: "bad", label: "Shot sideways", detail: "Hold the phone upright. A sideways clip gets cropped to a thin slice." });
      if (Math.min(v.w, v.h) < 720) out.push({ level: "warn", label: "Low resolution", detail: v.w + "×" + v.h + ". Set the camera to 1080p." });
    }
    if (kind === "aroll" && beat.say) {
      if (!a) out.push({ level: "warn", label: "Could not read the audio", detail: "Play it back once to make sure you can hear yourself." });
      else if (a.silent || a.loud < 0.01) out.push({ level: "bad", label: "No voice picked up", detail: "The clip is silent. Check the mic, then record it again." });
      else {
        if (a.loud < 0.045) out.push({ level: "warn", label: "Voice is quiet", detail: "Move the mic closer or step out of the wind." });
        else if (a.peak > 0.985) out.push({ level: "warn", label: "Audio is clipping", detail: "Too loud for the mic. Move it a little further away." });
        else out.push({ level: "ok", label: "Voice level good", detail: "" });
        if (spoken < target * 0.55) out.push({ level: "bad", label: "Sounds cut off", detail: RR.sec(spoken) + " of talking for a line that takes about " + RR.sec(target) + "." });
        else if (spoken > target * 1.7 + 0.8) out.push({ level: "warn", label: "Runs long", detail: RR.sec(spoken) + " against about " + RR.sec(target) + ". Fine if you restarted mid-clip; trim it in Cut." });
        else out.push({ level: "ok", label: "Length " + RR.sec(spoken), detail: "target about " + RR.sec(target) });
        if (a.in < 0.15) out.push({ level: "warn", label: "No pause before you speak", detail: "Leave a beat of silence first so the cut is clean." });
      }
    } else if (v.dur) {
      out.push(v.dur >= 2.5 ? { level: "ok", label: "Length " + RR.sec(v.dur), detail: "" } : { level: "warn", label: "Short cutaway", detail: RR.sec(v.dur) + ". Hold cutaways for 4 seconds or more." });
    }
    out.push({ level: "ok", label: RR.mb(size), detail: "" });
    return out;
  };

  function toMp4(file) {
    /* phones record QuickTime .mov; same container family as MP4, so relabel the brand */
    return file.slice(0, 12).arrayBuffer().then(function (buf) {
      var b = new Uint8Array(buf);
      if (b.length === 12 && b[4] === 0x66 && b[5] === 0x74 && b[6] === 0x79 && b[7] === 0x70 && b[8] === 0x71 && b[9] === 0x74) { b[8] = 0x6d; b[9] = 0x70; b[10] = 0x34; b[11] = 0x32; }
      return new Blob([b, file.slice(12)], { type: "video/mp4" });
    });
  }
  var COPY = { too_large: "That clip is over the 20 MB limit. Record it shorter, or at 1080p instead of 4K.",
    unsupported_type: "That file type was refused. Use the phone's normal camera.", quota_or_state: "Storage is full. Remove old takes on the Board tab, or ask Claude to clear finished reels.",
    not_granted: "This view is not allowed to upload.", rate_limited: "Too many uploads at once. Wait a moment and try again." };

  /* the whole path for one take: check it, store it, then let Claude look at it */
  RR.addTake = function (beat, kind, file) {
    if (!file || !S.cap.assets) return Promise.resolve(null);
    var key = beat._id + kind;
    if (file.size > LIMIT) { RR.toast("That clip is " + RR.mb(file.size) + ". The limit is 20 MB: set the camera to 1080p at 30 and keep each clip under about 10 seconds.", "bad"); return Promise.resolve(null); }
    RR.job(key, "Checking the take");
    var reelId = S.viewId, v, a;
    return Promise.all([readVideo(file), kind === "aroll" ? readAudio(file) : Promise.resolve(null)]).then(function (r) {
      v = r[0]; a = r[1];
      RR.job(key, "Uploading " + RR.mb(file.size));
      var isWebm = /webm/.test(file.type);
      return (isWebm ? Promise.resolve(file) : toMp4(file)).then(function (blob) { return S.cap.assets.upload(blob, { type: isWebm ? "video/webm" : "video/mp4" }); });
    }).then(function (up) {
      var dur = v.dur || (a && a.dur) || 0;
      var doc = { beat: beat._id, kind: kind, asset: up.id, size: up.sizeBytes, at: Date.now(), status: "new",
        dur: dur, w: v.w, h: v.h, in: a ? a.in : 0, out: a ? a.out : dur, peaks: a ? a.peaks : null,
        checks: RR.checks(beat, kind, v, a, up.sizeBytes) };
      return S.cap.db.collection("reels/" + reelId + "/clips").add(doc).then(function (ref) {
        RR.job(key, null); RR.refreshUsage();
        var patch = {}; patch[kind === "broll" ? "take_broll" : "take"] = ref.id;
        S.cap.db.doc("reels/" + reelId + "/beats/" + beat._id).update(patch).catch(function () {});
        var bad = doc.checks.filter(function (c) { return c.level === "bad"; })[0];
        RR.toast(bad ? bad.label + ". " + bad.detail : "Take saved.", bad ? "bad" : "good");
        if (S.cap.sample && v.frames.length && RR.ls.get("autoReview", true) && !bad) RR.reviewTake(reelId, ref.id, beat, kind, v.frames, doc.checks);
        return ref.id;
      });
    }).catch(function (e) {
      RR.job(key, null);
      RR.toast(COPY[e && e.code] || "Upload failed (" + ((e && e.code) || "connection") + "). Try again.", "bad");
      return null;
    });
  };

  /* frames from a clip that is already stored, for a review on demand */
  RR.framesOf = function (clip) {
    return fetch("/_blob/" + clip.asset).then(function (r) { return r.blob(); }).then(readVideo).then(function (v) { return v.frames; }, function () { return []; });
  };

  RR.wake = function () {
    var lock = null;
    try { if (navigator.wakeLock) navigator.wakeLock.request("screen").then(function (l) { lock = l; }, function () {}); } catch (_) {}
    return function () { try { lock && lock.release(); } catch (_) {} };
  };
})();
