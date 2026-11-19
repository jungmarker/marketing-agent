/* Reel Room - Cut tab: watch the reel assemble from your takes, choose and trim, review the final. */
(function () {
  "use strict";
  var RR = window.RR, S = RR.S, html = RR.html, ui = RR.ui;

  function sequence() {
    var t = 0;
    return S.beats.map(function (b, i) {
      var c = RR.chosen(b), br = b.use_broll === false ? null : RR.chosen(b, "broll"), len = RR.beatLen(b);
      var it = { beat: b, i: i, clip: c, broll: br, in: c ? c.in || 0 : 0, len: len, start: t };
      t += len; return it;
    });
  }
  function chunks(line) { var w = (line || "").split(/\s+/).filter(Boolean), out = []; for (var i = 0; i < w.length; i += 3) out.push(w.slice(i, i + 3).join(" ")); return out; }
  function captionAt(line, frac) {
    var g = chunks(line); if (!g.length) return "";
    var total = g.reduce(function (n, x) { return n + x.length; }, 0), acc = 0;
    for (var i = 0; i < g.length; i++) { acc += g[i].length / total; if (frac <= acc) return g[i]; }
    return g[g.length - 1];
  }

  /* plays the chosen takes back to back with the text card and captions on top.
     Beats with no take yet play as a slide for as long as the line takes to say. */
  ui.Player = function (p) {
    var seq = p.seq, st = RR.useState({ i: 0, t: 0, playing: false }), pos = st[0], setPos = st[1];
    var chrome = RR.useState(RR.ls.get("chrome", true)), showUi = chrome[0], setShowUi = chrome[1];
    var a = RR.useRef(null), b = RR.useRef(null), br = RR.useRef(null), eng = RR.useRef({ active: 0, i: 0, playing: false, slideT0: 0, raf: 0 });
    var seqRef = RR.useRef(seq); seqRef.current = seq;
    var els = function () { return [a.current, b.current]; };
    function seekTo(el, t) {
      if (el.readyState >= 1) { try { el.currentTime = t; } catch (_) {} return; }
      var f = function () { el.removeEventListener("loadedmetadata", f); try { el.currentTime = t; } catch (_) {} };
      el.addEventListener("loadedmetadata", f);
    }
    function load(el, it) { if (!el) return; if (it && it.clip) { var src = "/_blob/" + it.clip.asset; if (el.dataset.src !== src) { el.dataset.src = src; el.src = src; } seekTo(el, it.in); } }
    function show(i) {
      var e = eng.current, it = seqRef.current[i], cur = els()[e.active], nxt = els()[1 - e.active];
      e.i = i; e.slideT0 = performance.now();
      if (cur) cur.pause();
      if (it && it.clip) { e.active = 1 - e.active; load(nxt, it); nxt.style.opacity = 1; if (cur) cur.style.opacity = 0; if (e.playing) { var pr = nxt.play(); if (pr && pr.catch) pr.catch(function () {}); } }
      else { if (cur) cur.style.opacity = 0; if (nxt) nxt.style.opacity = 0; }
      var v = br.current;
      if (v) { if (it && it.broll) { var s2 = "/_blob/" + it.broll.asset; if (v.dataset.src !== s2) { v.dataset.src = s2; v.src = s2; } seekTo(v, 0); v.style.opacity = 1; if (e.playing) { var p2 = v.play(); if (p2 && p2.catch) p2.catch(function () {}); } } else { v.pause(); v.style.opacity = 0; } }
      var after = seqRef.current[i + 1]; if (after && after.clip) load(els()[1 - e.active], after);
      setPos({ i: i, t: 0, playing: e.playing });
    }
    function stop(reset) { var e = eng.current; e.playing = false; cancelAnimationFrame(e.raf); els().forEach(function (x) { x && x.pause(); }); br.current && br.current.pause(); if (reset) show(0); else setPos(function (s) { return { i: s.i, t: s.t, playing: false }; }); }
    function tick() {
      var e = eng.current, it = seqRef.current[e.i]; if (!e.playing) return;
      if (!it) return stop(true);
      var el = els()[e.active], t = it.clip && el ? Math.max(0, el.currentTime - it.in) : (performance.now() - e.slideT0) / 1000;
      if (t >= it.len || (it.clip && el && el.ended)) { if (e.i + 1 >= seqRef.current.length) return stop(true); show(e.i + 1); }
      else setPos({ i: e.i, t: t, playing: true });
      e.raf = requestAnimationFrame(tick);
    }
    function play() {
      var e = eng.current;
      /* a tap unlocks both players on phones, so the cut between takes does not stall */
      els().concat([br.current]).forEach(function (x) { if (x && x.dataset.src && x.paused) { var pr = x.play(); if (pr && pr.then) pr.then(function () { if (x !== els()[e.active] && x !== br.current) x.pause(); }, function () {}); } });
      e.playing = true; e.slideT0 = performance.now() - pos.t * 1000;
      var it = seqRef.current[e.i], el = els()[e.active];
      if (it && it.clip && el) { var pr = el.play(); if (pr && pr.catch) pr.catch(function () {}); }
      if (it && it.broll && br.current) { var p2 = br.current.play(); if (p2 && p2.catch) p2.catch(function () {}); }
      cancelAnimationFrame(e.raf); e.raf = requestAnimationFrame(tick); setPos({ i: e.i, t: pos.t, playing: true });
    }
    RR.useEffect(function () { show(0); return function () { stop(false); }; }, [p.sig]);
    RR.useEffect(function () { if (p.jump != null && p.jump.i < seq.length) show(p.jump.i); }, [p.jump]);
    var it = seq[pos.i] || {}, beat = it.beat || {}, frac = it.len ? Math.min(1, pos.t / it.len) : 0, total = seq.reduce(function (n, x) { return n + x.len; }, 0), at = (it.start || 0) + pos.t;
    return html`<div class="player">
      <div class="stage">
        <video ref=${a} playsinline preload="auto" class="layer"></video>
        <video ref=${b} playsinline preload="auto" class="layer"></video>
        <video ref=${br} playsinline muted preload="auto" class="layer"></video>
        ${!it.clip && html`<div class="slide"><span class="mono">${beat._id}</span><p>${beat.say || beat.shot || beat.broll}</p><small>Not shot yet. Timed from the script.</small></div>`}
        ${beat.cues ? beat.cues.filter(function (c) { return pos.t >= c.at && pos.t < c.end; }).map(function (c) { return html`<div class=${RR.cls("ov-cue", "pos-" + c.pos, c === beat.cues[0] && "card-hook")}>${c.text}</div>`; })
          : beat.screen && html`<div class=${RR.cls("ov-card", pos.i === 0 && "card-hook")}>${beat.screen}</div>`}
        ${beat.say && html`<div class="ov-cap">${captionAt(beat.say, frac)}</div>`}
        ${showUi && html`<div class="ov-ui" aria-hidden="true"><i></i><i></i><i></i><i></i><b></b><b></b></div>`}
        <button class=${RR.cls("play", pos.playing && "is-playing")} aria-label=${pos.playing ? "Pause" : "Play"} onClick=${function () { pos.playing ? stop(false) : play(); }}>${pos.playing ? "" : "▶"}</button>
      </div>
      <div class="transport"><span class="mono">${RR.tc(at)} / ${RR.tc(total)}</span>
        <label class="switch"><input type="checkbox" id="chrome-toggle" checked=${showUi} onChange=${function (e) { setShowUi(e.target.checked); RR.ls.set("chrome", e.target.checked); }} />Show where Instagram covers the frame</label></div>
      <div class="timeline" role="list">${seq.map(function (x) { var state = x.clip ? RR.beatState(x.beat) : "todo";
        return html`<button role="listitem" class=${RR.cls("tl", "tl-" + state, x.i === pos.i && "tl-on", x.len > 4.5 && "tl-long")} style=${"flex:" + Math.max(0.6, x.len) + " 1 0"} title=${x.beat._id + " " + RR.sec(x.len)} onClick=${function () { show(x.i); p.onSelect && p.onSelect(x.beat._id); }}>
          ${x.i === pos.i && html`<i style=${"width:" + Math.round(frac * 100) + "%"}></i>`}<span>${x.beat._id.replace("b", "")}</span></button>`; })}</div>
    </div>`;
  };

  /* choose the take, set where it starts and ends, change the words */
  ui.Wave = function (p) {
    var c = p.clip, pk = c.peaks || [], d = c.dur || 1, a = (p.in / d) * 100, b = (p.out / d) * 100;
    return html`<div class="wave"><div class="wave-bars">${pk.length ? pk.map(function (v) { return html`<i style=${"height:" + Math.max(4, v) + "%"}></i>`; }) : html`<span class="dim">No waveform for this clip</span>`}</div>
      <div class="wave-cut" style=${"left:0;width:" + a + "%"}></div><div class="wave-cut" style=${"left:" + b + "%;right:0"}></div></div>`;
  };
  ui.BeatEditor = function (p) {
    var b = S.beats.filter(function (x) { return x._id === p.id; })[0] || { _id: p.id, gone: true };
    var takes = RR.takes(b._id), cuts = RR.takes(b._id, "broll"), c = RR.chosen(b), cb = RR.chosen(b, "broll");
    var tr = RR.useState(null), trim = tr[0], setTrim = tr[1], sc = RR.useState(b.screen || ""), screen = sc[0], setScreen = sc[1];
    RR.useEffect(function () { setTrim(c ? { in: c.in || 0, out: c.out != null ? c.out : c.dur } : null); }, [c && c._id, c && c.in, c && c.out]);
    RR.useEffect(function () { setScreen(b.screen || ""); }, [b._id, b.screen]);
    var vid = RR.useRef(null);
    var seek = function (t) { if (vid.current) { try { vid.current.currentTime = t; } catch (_) {} } };
    var saveTrim = function () { if (c && trim) RR.act.clip(c._id, { in: +trim.in.toFixed(2), out: +trim.out.toFixed(2), trimmed_by: "nick" }); };
    var audition = function () { var v = vid.current; if (!v || !trim) return; v.currentTime = trim.in; v.play(); var stopAt = function () { if (v.currentTime >= trim.out) { v.pause(); v.removeEventListener("timeupdate", stopAt); } }; v.addEventListener("timeupdate", stopAt); };
    var changed = c && trim && (Math.abs(trim.in - (c.in || 0)) > 0.01 || Math.abs(trim.out - (c.out != null ? c.out : c.dur)) > 0.01);
    var first = S.beats[0] && S.beats[0]._id === b._id;
    if (b.gone) return null;
    return html`<section class="panel editor" id=${"edit-" + b._id}>
      <div class="panel-head"><span class="mono id">${b._id}</span><div class="grow"><p class="ed-line">${b.say ? "“" + b.say + "”" : "No talking: " + (b.shot || "")}</p></div>
        <button class="btn sm ghost" onClick=${function () { RR.set({ sheet: { type: "rewrite", beat: b._id } }); }}>Change line</button></div>
      ${!takes.length && html`<div class="empty sm"><p>No take for this line yet.</p><${ui.Record} beat=${b} kind="aroll" label="Record this line" /></div>`}
      ${c && trim && html`<div class="trim">
        <video ref=${vid} class="trim-video" controls playsinline preload="metadata" src=${"/_blob/" + c.asset + "#t=" + (c.in || 0).toFixed(2)}></video>
        <${ui.Wave} clip=${c} in=${trim.in} out=${trim.out} />
        <label class="range"><span>Start <b class="mono">${RR.sec(trim.in)}</b></span><input type="range" id=${"in-" + b._id} min="0" max=${c.dur} step="0.05" value=${trim.in} onInput=${function (e) { var v = Math.min(+e.target.value, trim.out - 0.3); setTrim({ in: v, out: trim.out }); seek(v); }} /></label>
        <label class="range"><span>End <b class="mono">${RR.sec(trim.out)}</b></span><input type="range" id=${"out-" + b._id} min="0" max=${c.dur} step="0.05" value=${trim.out} onInput=${function (e) { var v = Math.max(+e.target.value, trim.in + 0.3); setTrim({ in: trim.in, out: v }); seek(v); }} /></label>
        <div class="row"><span class="mono">${RR.sec(trim.out - trim.in)} in the cut${trim.out - trim.in > 4.5 ? " · long, add a cutaway or tighten" : ""}</span>
          <button class="btn sm" onClick=${audition}>Play the trim</button><button class="btn sm primary" disabled=${!changed} onClick=${saveTrim}>Save trim</button></div>
        <${ui.Checks} clip=${c} />
        ${S.cap.sample && !c.ai && !S.jobs["review" + c._id] && html`<button class="btn sm" onClick=${function () { RR.job("review" + c._id, "Pulling frames"); RR.framesOf(c).then(function (f) { if (f.length) RR.reviewTake(S.viewId, c._id, b, "aroll", f, c.checks || []); else { RR.job("review" + c._id, null); RR.toast("Could not read frames from that clip.", "bad"); } }); }}>Have Claude look at this take</button>`}
      </div>`}
      ${takes.length > 1 && html`<div class="take-strip"><small>${takes.length} takes</small>${takes.map(function (t, n) { return html`<button class=${RR.cls("take-pill", c && c._id === t._id && "on", "v-" + RR.verdict(t))} onClick=${function () { RR.act.beat(b._id, { take: t._id }); }}>Take ${n + 1} · ${RR.sec(RR.clipLen(t))}</button>`; })}</div>`}
      ${takes.length ? html`<div class="row"><${ui.Record} beat=${b} kind="aroll" label="Record another take" />${c && S.cap.assets && html`<button class="btn sm ghost" onClick=${function () { RR.act.removeClip(c); }}>Delete this take</button>`}</div>` : null}
      <label class="field"><span>Text on screen ${first ? "(the hook card)" : ""}</span>
        <div class="row"><input type="text" id=${"screen-" + b._id} value=${screen} maxlength="160" placeholder="No text on this beat" onInput=${function (e) { setScreen(e.target.value); }} />
        <button class="btn sm" disabled=${screen.trim() === (b.screen || "")} onClick=${function () { RR.act.beat(b._id, { screen: screen.trim() ? screen.trim().toUpperCase() : null }); }}>Save</button></div>
        ${RR.words(screen) > 6 && screen.indexOf("\n") < 0 && html`<small class="fix fix-warn">Over six words. It will not be read in time.</small>`}</label>
      ${b.broll && html`<div class="cutaway"><small>Cutaway</small><p>${b.broll}</p>
        ${cb ? html`<video class="trim-video" controls playsinline muted preload="metadata" src=${"/_blob/" + cb.asset}></video>
          <label class="switch"><input type="checkbox" id=${"use-" + b._id} checked=${b.use_broll !== false} onChange=${function (e) { RR.act.beat(b._id, { use_broll: e.target.checked }); }} />Show the cutaway over this line</label>` : null}
        <${ui.Record} beat=${b} kind="broll" label=${cuts.length ? "Record it again" : "Record cutaway"} /></div>`}
      <${ui.BeatNotes} beat=${b._id} />
    </section>`;
  };
  ui.Msg = function (p) { var n = p.n; return html`<div class=${"msg msg-" + (n.from === "claude" ? "claude" : "nick")}><small>${n.from === "claude" ? "Claude (editor)" : "You"}${n.beat ? " · " + n.beat : ""} · ${RR.when(n.at)}</small>${n.text}</div>`; };
  ui.BeatNotes = function (p) {
    var st = RR.useState(""), v = st[0], set = st[1], mine = S.notes.filter(function (n) { return n.beat === p.beat; });
    return html`<div class="notes">${mine.map(function (n) { return html`<${ui.Msg} n=${n} />`; })}
      <div class="row"><input type="text" id=${"note-" + p.beat} value=${v} placeholder="Note for the edit on this beat" onInput=${function (e) { set(e.target.value); }} /><button class="btn sm" disabled=${!v.trim()} onClick=${function () { RR.act.note(v, p.beat); set(""); }}>Send</button></div></div>`;
  };

  ui.Cut = function () {
    var r = RR.reel(), sel = RR.useState(null), selId = sel[0], setSel = sel[1], jm = RR.useState(null), jump = jm[0], setJump = jm[1], nt = RR.useState(""), note = nt[0], setNote = nt[1], cp = RR.useState("Copy caption"), copyLabel = cp[0], setCopy = cp[1];
    if (!r) return html`<div class="empty">Nothing to cut yet. Start from Today or Ideas.</div>`;
    var seq = sequence(), total = RR.total(), target = r.target_seconds || 30, shot = seq.filter(function (x) { return x.clip; }).length;
    var sig = S.viewId + "|" + seq.map(function (x) { return (x.clip ? x.clip._id + ":" + x.in + ":" + x.len.toFixed(2) : "-") + (x.broll ? "+" + x.broll._id : ""); }).join(",");
    var long = seq.filter(function (x) { return x.len > 4.5 && !x.broll; }), holes = /\{\{/.test(S.beats.map(function (b) { return (b.say || "") + (b.screen || ""); }).join(" "));
    var ready = r.status === "ready_to_edit", open = (r.verify || []).filter(function (v) { return !v.done; }).length;
    var copy = function () { try { navigator.clipboard.writeText(r.caption).then(function () { setCopy("Copied"); setTimeout(function () { setCopy("Copy caption"); }, 1500); }, function () { setCopy("Press and hold the text to copy"); }); } catch (_) { setCopy("Press and hold the text to copy"); } };
    return html`<div class="stack">
      <section class="panel flush">
        <${ui.Player} seq=${seq} sig=${sig} jump=${jump} onSelect=${setSel} />
        <div class="cut-facts">
          <span class=${Math.abs(total - target) > 6 ? "bad" : ""}><b class="mono">${RR.sec(total)}</b> long, target ${target}s</span>
          <span><b class="mono">${shot}/${seq.length}</b> lines shot</span>
          ${long.length ? html`<span class="bad">${long.map(function (x) { return x.beat._id; }).join(", ")} run past 4.5s on one shot</span>` : null}
          ${holes ? html`<span class="bad">A {{placeholder}} is still in the script</span>` : null}
        </div>
        <p class="dim pad">This is a preview built in your browser from the takes you picked. Tap a block to work on that beat. The finished file, with burned-in text and levelled audio, is rendered by Claude.</p>
      </section>

      ${r.final && r.final.asset ? html`<section class="panel"><h2>Finished cut from Claude</h2>
        <video class="final" controls playsinline preload="metadata" src=${"/_blob/" + r.final.asset}></video>
        ${r.final.note && html`<p>${r.final.note}</p>`}
        ${r.qc && r.qc.verdict && html`<p class="slate-chip">Check: ${r.qc.verdict}</p>`}
        ${(r.qc && r.qc.flags || []).map(function (f) { return html`<p class="fix fix-warn">${f}</p>`; })}
        <div class="row"><button class="btn primary grow" onClick=${function () { RR.act.status("approved"); }}>${r.status === "approved" || r.status === "posted" ? "Approved" : "Approve this cut"}</button>
          <button class="btn" onClick=${function () { RR.act.status("changes"); var el = document.getElementById("note-all"); if (el) el.focus(); }}>Ask for changes</button></div>
      </section>` : html`<section class="panel"><h2>Send it to be finished</h2>
        <p class="dim">${ready ? "Marked ready. Claude renders it on the next check: every morning, or sooner if you say so in the chat." : "When the preview above looks right, hand it over. Your take choices, trims and text go with it."}</p>
        <button class=${RR.cls("btn xl", !ready && "primary")} disabled=${!shot} onClick=${function () { RR.act.status(ready ? "shooting" : "ready_to_edit"); }}>${ready ? "Take it back, I'm still working" : "Ready for the final render"}</button></section>`}

      ${selId ? html`<${ui.BeatEditor} id=${selId} />` : null}
      <section class="panel"><h2>Every beat</h2>${seq.map(function (x) { var state = x.clip ? RR.beatState(x.beat) : "todo";
        return html`<button class=${RR.cls("shot-row", selId === x.beat._id && "row-on")} onClick=${function () { setSel(x.beat._id); setJump({ i: x.i, n: Date.now() }); setTimeout(function () { var el = document.getElementById("edit-" + x.beat._id); if (el) el.scrollIntoView({ behavior: "smooth", block: "start" }); }, 60); }}>
          <span class="mono id">${x.beat._id}</span><span class="shot-text">${x.beat.say || x.beat.screen || x.beat.broll}</span>
          <span class="mono dim">${RR.sec(x.len)}${RR.takes(x.beat._id).length > 1 ? " · " + RR.takes(x.beat._id).length + " takes" : ""}</span><${ui.Dot} s=${state} /></button>`; })}</section>

      ${r.verify && r.verify.length ? html`<section class="panel"><h2>Confirm before it goes out${open ? " · " + open + " open" : ""}</h2>${r.verify.map(function (v, i) { return html`<label class="check"><input type="checkbox" id=${"verify-" + i} checked=${!!v.done} onChange=${function () { RR.act.verify(i); }} /><span>${v.item}<small>${v.from}</small></span></label>`; })}</section>` : null}
      ${r.caption && html`<section class="panel"><h2>Caption</h2><pre class="caption">${r.caption}</pre><button class="btn" onClick=${copy}>${copyLabel}</button></section>`}
      <section class="panel"><h2>Notes with your editor</h2>
        <p class="dim">These go to Claude in the chat session, which does the final render. It reads them on its next check.</p>
        ${S.notes.filter(function (n) { return !n.beat; }).map(function (n) { return html`<${ui.Msg} n=${n} />`; })}
        <textarea id="note-all" value=${note} placeholder="What to change in the edit: pace, order, a card, the ending" onInput=${function (e) { setNote(e.target.value); }}></textarea>
        <button class="btn primary" disabled=${!note.trim()} onClick=${function () { RR.act.note(note); setNote(""); }}>Send note</button></section>
    </div>`;
  };
})();
