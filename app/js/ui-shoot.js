/* Reel Room - Today tab and the on-set shoot mode. */
(function () {
  "use strict";
  var RR = window.RR, S = RR.S, html = RR.html, ui = (RR.ui = {});

  ui.Sheet = function (p) {
    return html`<div class="scrim" onClick=${function (e) { if (e.target === e.currentTarget) p.onClose(); }}>
      <div class="sheet" role="dialog" aria-label=${p.title}>
        <div class="sheet-head"><h2>${p.title}</h2><button class="icon-btn" aria-label="Close" onClick=${p.onClose}>✕</button></div>
        <div class="sheet-body">${p.children}</div>
      </div></div>`;
  };
  ui.Dot = function (p) { return html`<span class=${"dot dot-" + p.s} aria-hidden="true"></span>`; };
  var STATE = { todo: "To shoot", sent: "Sent", good: "Good", retake: "Retake" };
  ui.State = function (p) { return html`<span class=${"state state-" + p.s}><${ui.Dot} s=${p.s} />${STATE[p.s]}</span>`; };

  /* what was measured, what Claude saw, what the editor said */
  ui.Checks = function (p) {
    var c = p.clip, job = S.jobs["review" + c._id];
    return html`<div class="checks">
      <div class="chips">${(c.checks || []).map(function (k) { return html`<span class=${"chip chip-" + k.level} title=${k.detail}>${k.label}</span>`; })}</div>
      ${(c.checks || []).filter(function (k) { return k.level !== "ok" && k.detail; }).map(function (k) { return html`<p class=${"fix fix-" + k.level}>${k.detail}</p>`; })}
      ${job && html`<p class="thinking"><span class="spin"></span>${job}</p>`}
      ${c.ai && html`<div class=${"verdict verdict-" + c.ai.verdict}>
        <b>${c.ai.verdict === "retake" ? "Claude: shoot it again" : "Claude: keep it"}</b>
        <p>${c.ai.note}</p>
        ${c.ai.fix && c.ai.fix.length ? html`<ul>${c.ai.fix.map(function (f) { return html`<li>${f}</li>`; })}</ul>` : null}
        <small>From three still frames. It cannot hear you or see movement.</small></div>`}
      ${c.note && html`<div class=${"verdict verdict-" + (c.status === "retake" ? "retake" : "keep")}><b>Editor's note</b><p>${c.note}</p></div>`}
    </div>`;
  };
  ui.Take = function (p) {
    var c = p.clip, picked = p.picked;
    return html`<div class=${RR.cls("take", picked && "take-picked")}>
      <video controls preload="metadata" playsinline src=${"/_blob/" + c.asset + "#t=" + (c.in || 0).toFixed(2)}></video>
      <div class="take-meta"><span class="mono">${RR.sec(RR.clipLen(c))}</span><span class="mono dim">${RR.when(c.at)}</span>
        ${picked ? html`<span class="tag-on">In the cut</span>` : p.onPick && html`<button class="btn sm" onClick=${p.onPick}>Use this take</button>`}
        ${S.cap.assets && html`<button class="btn sm ghost" onClick=${function () { RR.act.removeClip(c); }}>Delete</button>`}</div>
      <${ui.Checks} clip=${c} />
    </div>`;
  };
  ui.Record = function (p) {
    var key = p.beat._id + p.kind, job = S.jobs[key];
    if (!S.cap.assets) return html`<p class="dim">Recording is available to the page's owner, signed in.</p>`;
    if (job) return html`<div class="recording"><span class="spin"></span>${job}…</div>`;
    var pick = function (e) { var f = e.target.files && e.target.files[0]; e.target.value = ""; RR.addTake(p.beat, p.kind, f).then(function (id) { if (id && p.onDone) p.onDone(); }); };
    return html`<div class="rec-row">
      <label class="btn rec"><span class="rec-dot"></span>${p.label}<input type="file" accept="video/*" capture="environment" onChange=${pick} /></label>
      <label class="btn ghost">Library<input type="file" accept="video/*" onChange=${pick} /></label></div>`;
  };

  /* a drawing of the frame you are trying to get */
  var FRAMES = [ [/close.*shoulder|^close/i, { r: 13.5, cy: 66, w: 50, yb: 170 }], [/medium close|chest/i, { r: 10, cy: 60, w: 38, yb: 170 }],
    [/medium wide|knees/i, { r: 5.2, cy: 50, w: 18, yb: 170 }], [/wide/i, { r: 3.8, cy: 62, w: 12, yb: 122 }], [/./, { r: 7.6, cy: 56, w: 27, yb: 170 }] ];
  ui.FrameGuide = function (p) {
    var b = p.beat, cut = p.kind === "broll", f = FRAMES.filter(function (x) { return x[0].test(b.framing || ""); })[0][1];
    var cx = /left third/i.test(b.framing || "") ? 33 : /right third/i.test(b.framing || "") ? 57 : 45;
    var moves = /walk|climb|you move|out of frame/i.test((b.move || "") + (b.shot || ""));
    var low = /low/i.test(b.angle || ""), top = f.cy + f.r + 2;
    return html`<svg class="guide" viewBox="0 0 90 160" role="img" aria-label=${cut ? "Cutaway framing" : "Framing guide: " + (b.framing || "medium")}>
      <defs><clipPath id=${"clip-" + b._id + p.kind}><rect x="1" y="1" width="88" height="158" rx="6" /></clipPath></defs>
      <rect class="g-frame" x="1" y="1" width="88" height="158" rx="6" />
      <g clip-path=${"url(#clip-" + b._id + p.kind + ")"}>
        <line class="g-third" x1="30" y1="1" x2="30" y2="159" /><line class="g-third" x1="60" y1="1" x2="60" y2="159" />
        <line class="g-third" x1="1" y1="53" x2="89" y2="53" /><line class="g-third" x1="1" y1="107" x2="89" y2="107" />
        ${cut ? html`<g><rect class="g-subject" x="20" y="52" width="50" height="56" rx="3" /><line class="g-cross" x1="45" y1="72" x2="45" y2="88" /><line class="g-cross" x1="37" y1="80" x2="53" y2="80" /></g>`
          : html`<g><rect class="g-body" x=${cx - f.w / 2} y=${top} width=${f.w} height=${f.yb - top} rx=${f.w * 0.32} /><circle class="g-head" cx=${cx} cy=${f.cy} r=${f.r} /></g>`}
        ${moves && !cut && html`<path class="g-move" d=${"M " + (cx - 24) + " 138 L " + (cx + 16) + " 138 m -5 -4 l 5 4 l -5 4"} />`}
      </g>
      <rect class="g-safe" x="4" y="19" width="67" height="101" rx="2" />
      ${b.screen && html`<g><rect class=${"g-card" + (p.first ? " g-hook" : "")} x="9" y="23" width="56" height="11" rx="1" /><text class="g-label" x="37" y="30.6" text-anchor="middle">TEXT</text></g>`}
      ${b.say && html`<rect class="g-cap" x="16" y="106" width="42" height="6" rx="1" />`}
      <circle class="g-ui" cx="80" cy="96" r="3" /><circle class="g-ui" cx="80" cy="108" r="3" /><circle class="g-ui" cx="80" cy="120" r="3" />
      <rect class="g-ui" x="6" y="134" width="40" height="4" rx="2" /><rect class="g-ui" x="6" y="142" width="58" height="3" rx="1.5" />
      ${low && html`<text class="g-note" x="45" y="154" text-anchor="middle">PHONE LOW, TILT UP</text>`}
    </svg>`;
  };

  /* say it against the clock before you record it */
  ui.Rehearse = function (p) {
    var st = RR.useState(null), t0 = st[0], setT0 = st[1], el = RR.useState(0), ms = el[0], setMs = el[1];
    RR.useEffect(function () { if (t0 == null) return; var id = setInterval(function () { setMs(performance.now() - t0); }, 50); return function () { clearInterval(id); }; }, [t0]);
    RR.useEffect(function () { setT0(null); setMs(0); }, [p.id]);
    var s = ms / 1000, tgt = p.target, state = !ms ? "" : s > tgt * 1.3 ? "over" : s < tgt * 0.7 && t0 == null ? "under" : "ok";
    return html`<button class=${"rehearse rehearse-" + state} onClick=${function () { if (t0 == null) { setMs(0); setT0(performance.now()); } else setT0(null); }}>
      <span class="mono big">${s.toFixed(1)}</span><span class="mono dim">/ ${tgt.toFixed(1)}s</span>
      <span class="rehearse-label">${t0 != null ? "Tap when you finish the line" : ms ? (state === "over" ? "Long. Tighten it" : state === "under" ? "Rushed. Slow down" : "On pace") : "Rehearse against the clock"}</span></button>`;
  };

  ui.Rewrite = function (p) {
    var beat = p.beat, st = RR.useState({ loading: false, options: null, err: "" }), s = st[0], set = st[1], dr = RR.useState(beat.say || ""), draft = dr[0], setDraft = dr[1], ak = RR.useState(""), ask = ak[0], setAsk = ak[1];
    var run = function () { set({ loading: true, options: null, err: "" }); RR.rewriteLine(beat, ask).then(function (o) { set({ loading: false, options: o, err: o.length ? "" : "Nothing came back. Try again." }); }, function (e) { set({ loading: false, options: null, err: RR.aiError(e) }); }); };
    var save = function (t) { RR.act.line(beat, t).then(p.onClose); };
    return html`<${ui.Sheet} title=${"Line " + beat._id} onClose=${p.onClose}>
      <label class="field"><span>Your line</span><textarea id=${"line-" + beat._id} value=${draft} onInput=${function (e) { setDraft(e.target.value); }}></textarea></label>
      <div class="row"><span class="mono dim">about ${RR.sec(RR.sayTime(draft))} · ${RR.words(draft)} words</span><button class="btn primary" disabled=${!draft.trim() || draft.trim() === beat.say} onClick=${function () { save(draft); }}>Save line</button></div>
      ${S.cap.sample && html`<div class="ai-box">
        <label class="field"><span>Ask Claude for other ways to say it</span><input type="text" id=${"ask-" + beat._id} placeholder="shorter, funnier, in Spanish, less salesy…" value=${ask} onInput=${function (e) { setAsk(e.target.value); }} /></label>
        <button class="btn" disabled=${s.loading} onClick=${run}>${s.loading ? html`<span class="spin"></span>Writing` : "Give me three options"}</button>
        ${s.err && html`<p class="fix fix-bad">${s.err}</p>`}
        ${s.options && s.options.map(function (o) { return html`<button class="option" onClick=${function () { save(o.say); }}><small>${o.label || "Option"} · ${RR.sec(RR.sayTime(o.say))}</small>${o.say}</button>`; })}
      </div>`}
    <//>`;
  };

  /* ---------- shoot mode: one shot at a time, in the order you would shoot ---------- */
  ui.ShootMode = function () {
    var list = RR.shotList(), i = Math.min(S.shoot.i, list.length - 1), shot = list[i];
    RR.useEffect(function () { return RR.wake(); }, []);
    RR.useEffect(function () { var el = document.querySelector(".shoot-scroll"); if (el) el.scrollTop = 0; }, [i]);
    if (!shot) return null;
    var b = shot.beat, cut = shot.kind === "broll", takes = RR.takes(b._id, shot.kind).slice().reverse(), chosen = RR.chosen(b, shot.kind);
    var go = function (n) { RR.set({ shoot: { i: Math.max(0, Math.min(list.length - 1, n)) } }); };
    var nextTodo = function () { for (var k = 1; k <= list.length; k++) { var j = (i + k) % list.length; if (!RR.takes(list[j].beat._id, list[j].kind).length) return j; } return -1; };
    var nt = nextTodo(), firstBeat = S.beats[0] && S.beats[0]._id === b._id;
    var newStop = i === 0 || list[i - 1].stop !== shot.stop;
    return html`<div class="shoot">
      <div class="shoot-top">
        <button class="icon-btn" aria-label="Leave shoot mode" onClick=${function () { RR.set({ shoot: null }); }}>✕</button>
        <div class="shoot-where"><b>${shot.stop}</b><span class="mono dim">shot ${i + 1} of ${list.length}</span></div>
        <div class="pips">${list.map(function (s, k) { return html`<button aria-label=${"Shot " + (k + 1)} class=${RR.cls("pip", "pip-" + (RR.takes(s.beat._id, s.kind).length ? RR.beatState(s.beat) : "todo"), k === i && "pip-on")} onClick=${function () { go(k); }}></button>`; })}</div>
      </div>
      <div class="shoot-scroll">
        ${newStop && shot.tip && html`<div class="stop-tip"><b>New spot: ${shot.stop}.</b> ${shot.tip}</div>`}
        <div class="shoot-main">
          <${ui.FrameGuide} beat=${b} kind=${shot.kind} first=${firstBeat} />
          <dl class="dir">
            <dt>Clip</dt><dd class="mono">${b._id}${cut ? " cutaway" : ""}</dd>
            ${!cut && html`<dt>Framing</dt><dd>${b.framing}</dd><dt>Angle</dt><dd>${b.angle}</dd><dt>Camera</dt><dd>${b.move}</dd>`}
            <dt>Where</dt><dd>${b.location}</dd>
          </dl>
        </div>
        ${cut ? html`<div class="prompter"><small>Cutaway, no talking</small><p class="cut-desc">${b.broll}</p><small>Plays over: “${b.say}”</small></div>`
          : !b.say ? html`<div class="prompter"><small>No talking. Text goes on screen</small>
              <span class=${RR.cls("card card-lg", firstBeat && "card-hook")}>${b.screen}</span>
              <p class="cut-desc">${b.shot}</p><small>Hold it for ${RR.sec(b.seconds || 3)}. Leave room in the frame for the text.</small></div>`
          : html`<div class="prompter">
              <small>Say</small><p class="line">${b.say}</p>
              ${b.screen && html`<span class=${RR.cls("card", firstBeat && "card-hook")}>${b.screen}</span>`}
              <p class="do">${b.shot}</p>
              <div class="row"><${ui.Rehearse} id=${b._id} target=${RR.sayTime(b.say)} /><button class="btn ghost" onClick=${function () { RR.set({ sheet: { type: "rewrite", beat: b._id } }); }}>Change line</button></div>
            </div>`}
        <${ui.Record} beat=${b} kind=${shot.kind} label=${takes.length ? "Record another take" : cut ? "Record cutaway" : b.say ? "Record this line" : "Record this shot"} />
        ${takes.map(function (c) { return html`<${ui.Take} key=${c._id} clip=${c} picked=${chosen && chosen._id === c._id} onPick=${function () { var pch = {}; pch[cut ? "take_broll" : "take"] = c._id; RR.act.beat(b._id, pch); }} />`; })}
      </div>
      <div class="shoot-nav">
        <button class="btn ghost" disabled=${i === 0} onClick=${function () { go(i - 1); }}>Back</button>
        ${nt < 0 ? html`<button class="btn primary grow" onClick=${function () { RR.set({ shoot: null }); RR.go("cut"); }}>Everything is shot. Open the cut</button>`
          : html`<button class=${RR.cls("btn grow", takes.length && "primary")} onClick=${function () { go(takes.length ? nt : i + 1 < list.length ? i + 1 : nt); }}>${takes.length ? "Next to shoot: " + list[nt].beat._id + (list[nt].kind === "broll" ? " cutaway" : "") : "Skip for now"}</button>`}
      </div>
    </div>`;
  };

  /* ---------- Today ---------- */
  ui.Stepper = function (p) {
    var at = Math.max(0, RR.STAGES.indexOf(p.status === "changes" ? "ready_to_edit" : p.status));
    var steps = ["Script", "Shoot", "Cut", "Review", "Approved", "Posted"];
    return html`<ol class="stepper">${steps.map(function (s, k) { return html`<li class=${k < at ? "done" : k === at ? "on" : ""}>${s}</li>`; })}</ol>`;
  };
  ui.Today = function () {
    var r = RR.reel();
    if (!S.booted) return html`<div class="empty"><span class="spin"></span>Loading your reel…</div>`;
    if (S.failed && !r) return html`<div class="empty">${S.failed === "signed_out" ? "Sign in to Claude to open your reels." : "This did not load. Reopen the page to try again."}</div>`;
    if (!r) return html`<div class="empty"><b>No reel on the slate yet.</b><p>Pick an idea and have the script written, or wait for the morning shot list.</p><button class="btn primary" onClick=${function () { RR.go("ideas"); }}>Go to ideas</button></div>`;
    var list = RR.shotList(), prog = RR.progress(), open = (r.verify || []).filter(function (v) { return !v.done; }).length;
    var firstTodo = -1; list.some(function (s, k) { if (!RR.takes(s.beat._id, s.kind).length) { firstTodo = k; return true; } });
    var retakes = list.filter(function (s) { return s.kind === "aroll" && RR.beatState(s.beat) === "retake"; });
    var stops = []; list.forEach(function (s, k) { var last = stops[stops.length - 1]; if (!last || last.name !== s.stop) stops.push(last = { name: s.stop, tip: s.tip, shots: [] }); last.shots.push({ s: s, k: k }); });
    var start = function (k) { if (r.status === "scripted") RR.act.status("shooting"); RR.set({ shoot: { i: k } }); };
    return html`<div class="stack">
      ${S.viewId !== S.currentId && html`<div class="banner">You are looking at a reel that is not on today's slate.<button class="btn sm" onClick=${function () { RR.act.makeCurrent(S.viewId); }}>Make it today's reel</button></div>`}
      <section class="hero">
        <${ui.Stepper} status=${r.status} />
        <h1>${r.title}</h1>
        <div class="hero-meta"><span class="slate-chip">${r.formula || "Reel"}</span><span class="mono dim">${S.beats.length} ${r.kind && r.kind !== "talk" ? "shots" : "lines"} · about ${Math.round(RR.total())}s · ${stops.length} spots</span></div>
        ${r.why && html`<p class="why">${r.why}</p>`}
        <div class="meter"><div class="meter-bar"><i style=${"width:" + prog.pct + "%"}></i></div><span class="mono">${prog.done}/${prog.of} shot</span></div>
        ${!S.loadedView ? null : firstTodo >= 0
          ? html`<button class="btn primary xl" onClick=${function () { start(firstTodo); }}>${prog.done ? "Keep shooting: " + list[firstTodo].beat._id + " is next" : "Start shooting"}</button>`
          : html`<button class="btn primary xl" onClick=${function () { RR.go("cut"); }}>Everything is shot. Open the cut</button>`}
        ${retakes.length ? html`<p class="fix fix-warn">${retakes.length} to shoot again: ${retakes.map(function (s) { return s.beat._id; }).join(", ")}</p>` : null}
        ${open ? html`<button class="notice" onClick=${function () { RR.go("cut"); }}><b>${open} thing${open > 1 ? "s" : ""} to confirm before you record.</b> Numbers and legal lines that need a real source. Tap to see them.</button>` : null}
      </section>

      ${stops.map(function (st, n) { return html`<section class="panel">
        <div class="panel-head"><span class="stop-n">${n + 1}</span><div><h2>${st.name}</h2>${st.tip && html`<p class="dim">${st.tip}</p>`}</div></div>
        ${st.shots.map(function (x) { var b = x.s.beat, cut = x.s.kind === "broll", state = RR.takes(b._id, x.s.kind).length ? (cut ? "good" : RR.beatState(b)) : "todo";
          return html`<button class="shot-row" onClick=${function () { start(x.k); }}>
            <span class="mono id">${b._id}</span>
            <span class="shot-text">${cut ? html`<i>Cutaway:</i> ${b.broll}` : b.say || html`<i>Text:</i> ${b.screen}`}</span>
            <span class="mono dim">${cut ? "4s+" : RR.sec(b.say ? RR.sayTime(b.say) : b.seconds || 3)}</span><${ui.Dot} s=${state} /></button>`; })}
      </section>`; })}

      ${r.hooks && r.hooks.length > 1 && html`<details class="panel"><summary>Other ways to open it</summary>${r.hooks.map(function (h) { return html`<p class="alt-hook">“${h.say}” ${h.screen && html`<span class="card sm-card">${h.screen}</span>`}</p>`; })}${r.spanish_hook && html`<p class="alt-hook"><small>Spanish:</small> “${r.spanish_hook}”</p>`}</details>`}
      ${r.setup && r.setup.length ? html`<details class="panel"><summary>Phone settings before you start</summary><ul class="plain">${r.setup.map(function (t) { return html`<li>${t}</li>`; })}</ul></details>` : null}
    </div>`;
  };
})();
