/* Reel Room - ai: the calls the page makes to Claude on its own, on your account. */
(function () {
  "use strict";
  var RR = window.RR, S = RR.S;

  var COPY = { not_granted: "Claude is switched off for this page. Allow it from the page's Permissions menu to use this.",
    rate_limited: "Too many requests at once. Give it a minute.", refused: "Claude declined that one. Reword it and try again.",
    invalid_json: "The answer came back garbled. Try again.", cancelled: "", session_expired: "Your session expired. Reload the page.",
    image_rejected: "The frames could not be read. Review skipped.", images_unavailable: "This view cannot send frames to Claude." };
  RR.aiError = function (e) { var c = e && e.code; return c in COPY ? COPY[c] : "Claude could not answer just now (" + (c || "error") + "). Try again."; };

  function voice() {
    var v = S.voice || {};
    return [ "WHO THIS IS FOR", "Nick Jungmarker, a REALTOR with Long & Foster in Baltimore, Maryland. He works with first-time buyers and rowhouse buyers and sellers, in English and Spanish. He films alone on a phone.",
      v.samples ? "HOW HE TALKS (his own words, match this voice):\n" + v.samples : "No voice samples yet: write plainly, short spoken sentences, contractions, nothing he would have to rehearse.",
      v.never ? "WORDS AND TOPICS HE NEVER USES: " + v.never : "" ].filter(Boolean).join("\n");
  }
  var RULES = [ "RULES",
    "- Never invent a number, price, statistic, client or result. Where one is needed and not given, write {{what goes here}} and he fills it in.",
    "- Fair housing: describe places and facts only. Never say who a neighborhood is for, and nothing about schools, safety or the people who live there.",
    "- Spoken lines: 10 words or fewer where possible, one idea per line, the way a person talks. No greeting, no \"in this video\".",
    "- On-screen text: 6 words or fewer, capitals.",
    "- Copy shapes from other creators, never their words." ].join("\n");
  function research() {
    var r = S.research; if (!r) return "";
    return "WHAT IS WORKING (from " + r.n + " short videos across " + r.accounts + " real estate accounts; base rate " + r.base + "% beat their account's median by 3x):\n" +
      (r.shapes || []).map(function (s) { return "- " + s.name + ": " + s.rate + "% (" + s.hit + " of " + s.of + ")"; }).join("\n") + "\n" +
      (r.patterns || []).map(function (p) { return "- " + p.title + ": " + p.detail; }).join("\n");
  }
  function reelText() {
    var r = RR.reel(); if (!r) return "";
    return "THE REEL: " + r.title + " (" + (r.formula || "") + ")\n" + S.beats.map(function (b) {
      return b._id + (b.say ? ' SAY "' + b.say + '"' : " (cutaway only)") + (b.screen ? " | ON SCREEN: " + b.screen : "") + (b.shot ? " | SHOT: " + b.shot : "");
    }).join("\n");
  }

  /* 1. look at a take: three frames against what the shot was supposed to be */
  RR.reviewTake = function (reelId, clipId, beat, kind, frames, checks) {
    var sample = S.cap.sample; if (!sample) return Promise.resolve();
    var path = "reels/" + reelId + "/clips/" + clipId, key = "review" + clipId;
    RR.job(key, "Claude is looking at the take");
    var prompt = [ "You are the director's eye on a solo phone shoot for an Instagram Reel. You are given 3 still frames (start, middle, end) from one take, in order.",
      "THE SHOT THAT WAS ASKED FOR", "Kind: " + (kind === "broll" ? "cutaway with no speech: " + beat.broll : "he speaks this line to camera: \"" + (beat.say || "") + "\""),
      "Action: " + (beat.shot || "n/a"), "Framing: " + (beat.framing || "n/a"), "Angle: " + (beat.angle || "n/a"), "Camera: " + (beat.move || "n/a"), "Location: " + (beat.location || "n/a"),
      beat.screen ? "A text card reading \"" + beat.screen + "\" will be placed across the upper part of the frame, so that band should be free of his face." : "",
      "ALREADY MEASURED FROM THE FILE: " + checks.map(function (c) { return c.label; }).join("; "),
      "Judge only what the frames show: framing against what was asked, headroom for the text card, focus, exposure and backlight, a level horizon, distractions in the background such as another brokerage's sign, a person's face or a licence plate, and whether he is looking at the lens.",
      "You cannot hear the audio or see motion, so say nothing about delivery or sound. Be specific and brief. If it is usable, say keep.",
      "Reply with only JSON: {\"verdict\":\"keep\"|\"retake\",\"note\":\"one or two sentences, what to change if retake\",\"good\":\"one short thing that works\",\"fix\":[\"short imperative, 0 to 3 items\"]}" ].filter(Boolean).join("\n");
    return sample.json(prompt, { images: frames, modelTier: "default", cache: false }).then(function (r) {
      RR.job(key, null);
      if (!r || !r.verdict) return;
      var ai = { verdict: r.verdict === "retake" ? "retake" : "keep", note: String(r.note || "").slice(0, 400), good: String(r.good || "").slice(0, 200), fix: (r.fix || []).slice(0, 3).map(String), at: Date.now() };
      return S.cap.db.doc(path).update({ ai: ai }).then(function () { if (ai.verdict === "retake") RR.toast(beat._id + ": " + ai.note, "bad"); }, function () {});
    }, function (e) { RR.job(key, null); if (e && e.code !== "not_granted" && e.code !== "cancelled") RR.toast(RR.aiError(e), "bad"); });
  };

  /* 2. three other ways to say a line */
  RR.rewriteLine = function (beat, ask) {
    var prompt = [ voice(), RULES, reelText(), "TASK",
      "Rewrite the spoken line for " + beat._id + ": \"" + (beat.say || "") + "\"",
      ask ? "He asked for: " + ask : "Give three options: one shorter, one more conversational, one in Spanish as a Baltimore agent would say it.",
      "Keep the meaning and any {{placeholder}}. It must still lead into the next line.",
      "Reply with only JSON: {\"options\":[{\"label\":\"Shorter\",\"say\":\"...\"}]} with exactly three options." ].join("\n\n");
    return S.cap.sample.json(prompt, { modelTier: "default", cache: false }).then(function (r) { return (r && r.options || []).filter(function (o) { return o && o.say; }).slice(0, 3); });
  };

  /* 3. ideas from something that happened */
  RR.genIdeas = function (seed) {
    var have = S.ideas.map(function (i) { return "- " + i.topic; }).join("\n");
    var prompt = [ voice(), RULES, research(), "ALREADY IN THE QUEUE (do not repeat):\n" + (have || "none"), "TASK",
      seed ? "He wrote: \"" + seed + "\"\nTurn that into four different Reel ideas." : "Give four Reel ideas for this week that fit Baltimore rowhouse buyers and sellers.",
      "Each uses one of the shapes that beat the base rate, is specific to Baltimore, and could be shot alone on one block in under 30 minutes.",
      "Reply with only JSON: {\"ideas\":[{\"topic\":\"what the reel is, one line\",\"formula\":\"shape name\",\"hook\":\"the first spoken line, 10 words or fewer\",\"evidence\":\"which finding above supports it, one line\"}]}" ].join("\n\n");
    return S.cap.sample.json(prompt, { modelTier: "default", cache: false }).then(function (r) { return (r && r.ideas || []).filter(function (i) { return i && i.topic; }).slice(0, 4); });
  };

  /* 4. a full shot list from one idea */
  RR.genScript = function (idea, onText) {
    var prompt = [ voice(), RULES, research(), "TASK",
      "Write a complete Instagram Reel for this idea: \"" + idea.topic + "\"" + (idea.hook ? "\nOpening line to build on: \"" + idea.hook + "\"" : "") + (idea.formula ? "\nShape: " + idea.formula : ""),
      "25 to 35 seconds, 9 to 12 beats. Each beat is one clip he records. The frame must change every beat: a new angle, distance, place or a cutaway. The last line echoes a word from the first so it loops, and there is exactly one ask.",
      "Group the beats into 2 to 4 stops (places he stands) so he shoots everything at one spot before moving.",
      "Reply with only JSON in exactly this shape:",
      '{"title":"short title","formula":"shape name","why":"one sentence on why this should work, citing the finding","hooks":[{"say":"...","screen":"..."}],"beats":[{"say":"spoken line","screen":"TEXT CARD or null","shot":"what he physically does","framing":"Wide | Medium wide (knees up) | Medium (waist up) | Medium close (chest up) | Close (shoulders up)","angle":"Eye level | Low | High, plus anything specific","move":"Locked on tripod | Handheld walking | You move, camera locked","location":"where","broll":"a cutaway to record over this line, or null"}],"stops":[{"name":"place","tip":"one setup tip","beats":[1,2]}],"caption":"first line, short body, one ask. No hashtags, no footer.","keywords":"three search phrases separated by ·","hashtags":"three hashtags","verify":[{"item":"a claim or number he must confirm before recording","from":"who to get it from"}],"spanish_hook":"the opening line in Spanish"}',
      "hooks: three different opening options, the first is the one used in beat 1. stops[].beats are beat numbers starting at 1." ].join("\n\n");
    return S.cap.sample.json(prompt, { modelTier: "complex", cache: false, onText: onText }).then(function (r) {
      if (!r || !Array.isArray(r.beats) || r.beats.length < 4) throw { code: "invalid_json" };
      var pad = function (n) { return "b" + (n < 10 ? "0" : "") + n; }, turn = 0;
      var beats = r.beats.slice(0, 14).map(function (b, i) {
        var cam = /camera|tripod|locked/i.test(b.move || "") && !b.broll;
        return { _id: pad(i + 1), say: String(b.say || ""), screen: b.screen && b.screen !== "null" ? String(b.screen).toUpperCase() : null, shot: String(b.shot || ""),
          framing: String(b.framing || "Medium (waist up)"), angle: String(b.angle || "Eye level"), move: String(b.move || "Locked on tripod"),
          location: String(b.location || ""), broll: b.broll && b.broll !== "null" ? String(b.broll) : null, punch: cam ? (turn++ % 2 === 1) : false };
      });
      var d = new Date(), base = d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2), id = base, n = 1;
      while (S.reels.some(function (x) { return x._id === id; })) id = base + "-" + (++n);
      var caption = [String(r.caption || "").trim(), r.keywords ? String(r.keywords) : "", r.hashtags ? String(r.hashtags) : "", RR.FOOTER].filter(Boolean).join("\n\n");
      var reel = { _id: id, date: base, title: String(r.title || idea.topic).slice(0, 90), formula: String(r.formula || idea.formula || ""), why: String(r.why || ""),
        status: "scripted", status_at: Date.now(), target_seconds: Math.round(beats.reduce(function (s, b) { return s + RR.sayTime(b.say); }, 0)),
        hooks: (r.hooks || []).slice(0, 3), spanish_hook: String(r.spanish_hook || ""), caption: caption, written_by: "app", idea: idea._id || null,
        verify: (r.verify || []).slice(0, 8).map(function (v) { return { item: String(v.item || ""), from: "Get it from: " + String(v.from || "your own records"), done: false }; }),
        stops: (r.stops || []).map(function (s) { return { name: String(s.name || "Stop"), tip: String(s.tip || ""), beats: (s.beats || []).map(function (k) { return pad(+k); }) }; }),
        setup: ["Rear camera, 1x lens, vertical, 1080p at 30. Each clip under 20 MB, so not 4K.", "HDR video off. Lock focus and exposure on your face.", "One clip per line. A second of silence before and after you speak.", "Keep the top fifth of the frame empty above your head for the text card.", "Clip-on or wired mic. Play one clip back before shooting the rest."] };
      return { reel: reel, beats: beats };
    });
  };

  /* 5. ask anything about the reel in front of you */
  RR.ask = function (turns, onText, signal) {
    var lead = [ "You are Nick's co-producer inside his reel production app. Answer in a few plain sentences he can act on while standing on a sidewalk with a phone. If he asks for a line, give the line.",
      voice(), RULES, reelText(), research() ].filter(Boolean).join("\n\n");
    return S.cap.sample([{ role: "user", content: lead }].concat(turns), { cache: false, modelTier: "default", onText: onText, signal: signal });
  };
})();
