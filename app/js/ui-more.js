/* Reel Room - Ideas, Board, the Ask sheet, and the app shell. */
(function () {
  "use strict";
  var RR = window.RR, S = RR.S, html = RR.html, ui = RR.ui;

  /* ---------- Ideas ---------- */
  function writeScript(idea) {
    if (S.jobs.script) return;
    RR.job("script", "Writing the script");
    RR.genScript(idea, function (x) { RR.job("script", "Writing the script · " + RR.words(x.text) + " words"); }).then(function (out) {
      return RR.act.createReel(out.reel, out.beats).then(function () {
        if (idea._id) RR.act.idea(idea._id, { status: "scripted", reel: out.reel._id });
        RR.job("script", null); RR.toast("Script is ready. Read it through before you shoot.", "good"); RR.go("today");
      });
    }, function (e) { RR.job("script", null); RR.toast(RR.aiError(e), "bad"); });
  }
  var KIND = { talk: "Talk", point: "No talking · point", text: "No talking · one clip" };
  ui.BankDetail = function (p) {
    var v = p.v, b = v.beats;
    if (v.kind === "talk") return html`<ol class="plain bank-lines">${b.map(function (x) { return html`<li>${x.say}${x.screen ? html` <span class="card sm-card">${x.screen}</span>` : null}</li>`; })}</ol>`;
    var c = b[0].cues || [], st = v.setup || {};
    return html`<div class="bank-lines">${st.where && html`<p><b>Where:</b> ${st.where}</p>`}${st.clip && html`<p><b>The clip:</b> ${st.clip}</p>`}
      <ol class="cues compact">${c.map(function (q) { return html`<li><span class="mono cue-t">${q.at.toFixed(1)}s</span><div class="cue-body"><span class="card sm-card">${q.text}</span><p>${q.do}</p></div></li>`; })}</ol></div>`;
  };
  ui.Bank = function (p) {
    var st = RR.useState(RR.ls.get("bankFilter", "point")), f = st[0], setF = st[1], mr = RR.useState(p.top ? 4 : 8), more = mr[0], setMore = mr[1];
    var op = RR.useState(null), open = op[0], setOpen = op[1], hd = RR.useState(RR.ls.get("bankHidden", false)), hidden = hd[0], setHidden = hd[1];
    if (!S.bank.length) return p.top ? html`<div class="empty sm">Loading the video list\u2026</div>` : null;
    var done = {}; S.reels.forEach(function (r) { if (r.bank_id) done[r.bank_id] = r; });
    var list = S.bank.filter(function (v) { return f === "all" || v.kind === f; });
    var chip = function (k, label) { return html`<button class=${RR.cls("take-pill", f === k && "on")} onClick=${function () { setF(k); setMore(8); RR.ls.set("bankFilter", k); }}>${label} · ${k === "all" ? S.bank.length : S.bank.filter(function (v) { return v.kind === k; }).length}</button>`; };
    if (p.top && hidden) return html`<button class="btn" onClick=${function () { setHidden(false); RR.ls.set("bankHidden", false); }}>Show the ${S.bank.length} videos ready to shoot</button>`;
    return html`<section class="stack tight bank"><div class="row"><h2 class="sec grow">${S.bank.length} videos ready to shoot</h2>
        ${p.top && html`<button class="btn sm ghost" onClick=${function () { setHidden(true); RR.ls.set("bankHidden", true); }}>Hide</button>`}</div>
      <p class="dim">Each one answers a question people search about buying or selling in Baltimore. Open one to see every shot, then tap Shoot this.</p>
      <div class="take-strip">${chip("point", "No talking: point at text")}${chip("text", "No talking: one clip")}${chip("talk", "Talk to camera")}${chip("all", "All")}</div>
      ${list.slice(0, more).map(function (v) { var r = done[v.id], hook = (v.beats[0] && (v.beats[0].say || v.beats[0].screen.split("\n")[0])) || "";
        return html`<article class="idea">
          <div class="idea-top"><span class="slate-chip">${KIND[v.kind]}</span><span class="mono dim">${v.kind === "talk" ? v.beats.length + " lines" : "one take"} · ${v.seconds}s</span></div>
          <h3>${v.title}</h3><p class="idea-hook">“${hook}”</p><p class="dim">Answers: ${v.question}${v.verify && v.verify.length ? " · " + v.verify.length + " to confirm first" : ""}</p>
          ${open === v.id && html`<${ui.BankDetail} v=${v} />`}
          <div class="row wrap">${r ? html`<button class="btn sm" onClick=${function () { RR.view(r._id); RR.go("today"); window.scrollTo(0, 0); }}>Open · ${RR.STAGE_LABEL[r.status] || r.status}</button>`
            : html`<button class="btn primary sm" onClick=${function () { RR.act.fromBank(v).then(function () { RR.go("today"); RR.toast("On the slate. Tap Start shooting.", "good"); var el = document.querySelector(".slate-head"); if (el) el.scrollIntoView({ behavior: "smooth" }); }); }}>Shoot this</button>`}
            <button class="btn sm ghost" onClick=${function () { setOpen(open === v.id ? null : v.id); }}>${open === v.id ? "Hide the shots" : "See every shot"}</button></div></article>`; })}
      ${list.length > more && html`<button class="btn" onClick=${function () { setMore(more + 12); }}>Show more (${list.length - more} left)</button>`}
    </section>`;
  };
  ui.Research = function () {
    var r = S.research; if (!r) return null;
    var max = Math.max.apply(null, (r.shapes || []).map(function (s) { return s.rate; }).concat([r.base, 1]));
    return html`<section class="panel"><h2>What is working right now</h2>
      <p class="dim">${r.n.toLocaleString()} short videos from ${r.accounts} real estate accounts, each measured against that account's own typical video. ${r.base}% beat it by three times or more. ${r.caveat || ""}</p>
      <div class="bars">${(r.shapes || []).map(function (s) { return html`<div class="bar-row"><span class="bar-name">${s.name}</span>
        <div class="bar-track"><i class=${s.rate >= r.base ? "up" : "down"} style=${"width:" + Math.round(100 * s.rate / max) + "%"}></i><em style=${"left:" + Math.round(100 * r.base / max) + "%"}></em></div>
        <span class="mono">${s.rate}%</span></div>`; })}
        <p class="bar-key"><em></em>the line is the ${r.base}% average</p></div>
      ${(r.patterns || []).map(function (p) { return html`<div class="pattern"><b>${p.title}</b><p>${p.detail}</p></div>`; })}
      ${r.outliers && r.outliers.length ? html`<details><summary>The videos behind this</summary><ul class="outliers">${r.outliers.map(function (o) { return html`<li><b class="mono">${o.x}×</b><span>${o.title}<small>${o.account} · ${Number(o.views).toLocaleString()} views</small></span></li>`; })}</ul></details>` : null}
      <small class="dim">Updated ${r.updated || ""}</small></section>`;
  };
  ui.Ideas = function () {
    var st = RR.useState(""), seed = st[0], setSeed = st[1], sg = RR.useState({ loading: false, list: [], err: "" }), sug = sg[0], setSug = sg[1];
    var gen = function () { setSug({ loading: true, list: [], err: "" }); RR.genIdeas(seed).then(function (l) { setSug({ loading: false, list: l, err: l.length ? "" : "Nothing came back. Try again." }); }, function (e) { setSug({ loading: false, list: [], err: RR.aiError(e) }); }); };
    var queue = S.ideas.filter(function (i) { return i.status !== "done" && i.status !== "scripted"; }).sort(function (a, b) { return (b.status === "next") - (a.status === "next") || (b.from === "nick") - (a.from === "nick") || (a.n || 0) - (b.n || 0); });
    var ai = !!S.cap.sample, busy = !!S.jobs.script;
    var card = function (i, fresh) { return html`<article class="idea">
      <div class="idea-top"><span class="slate-chip">${i.formula || (i.from === "nick" ? "Yours" : "Idea")}</span>${i.status === "next" && html`<span class="state state-good">Up next</span>`}</div>
      <h3>${i.topic}</h3>${i.hook && html`<p class="idea-hook">“${i.hook}”</p>`}${i.evidence && html`<p class="dim">${i.evidence}</p>`}
      <div class="row wrap">
        ${ai && html`<button class="btn primary sm" disabled=${busy} onClick=${function () { writeScript(i); }}>Write the script</button>`}
        ${fresh ? html`<button class="btn sm" onClick=${function () { RR.act.addIdea({ topic: i.topic, formula: i.formula || "", hook: i.hook || "", evidence: i.evidence || "", from: "claude" }); setSug({ loading: false, err: "", list: sug.list.filter(function (x) { return x !== i; }) }); }}>Save for later</button>`
          : html`<button class="btn sm" onClick=${function () { RR.act.nextIdea(i); }}>${i.status === "next" ? "Not next" : "Make it tomorrow's"}</button><button class="btn sm ghost" onClick=${function () { RR.act.removeIdea(i._id); }}>Remove</button>`}
      </div></article>`; };
    return html`<div class="stack">
      <${ui.Bank} />
      <section class="panel"><h2>Start from something real</h2>
        <textarea id="idea-seed" value=${seed} placeholder="A question a buyer asked this week. A listing you just took. Something on your block that annoyed you." onInput=${function (e) { setSeed(e.target.value); }}></textarea>
        <div class="row wrap">
          ${ai && html`<button class="btn primary" disabled=${sug.loading} onClick=${gen}>${sug.loading ? html`<span class="spin"></span>Thinking` : seed.trim() ? "Turn it into reel ideas" : "Give me four ideas"}</button>`}
          <button class="btn" disabled=${!seed.trim()} onClick=${function () { RR.act.addIdea({ topic: seed.trim().slice(0, 300) }); setSeed(""); }}>Save as my own idea</button></div>
        ${!ai && html`<p class="dim">Instant ideas and scripts need Claude allowed for this page. Your saved ideas still reach Claude in chat each morning.</p>`}
        ${sug.err && html`<p class="fix fix-bad">${sug.err}</p>`}
        ${busy && html`<p class="thinking"><span class="spin"></span>${S.jobs.script}. This takes about a minute.</p>`}
      </section>
      ${sug.list.length ? html`<section class="stack tight"><h2 class="sec">Fresh ideas</h2>${sug.list.map(function (i) { return card(i, true); })}</section>` : null}
      <section class="stack tight"><h2 class="sec">Queue · ${queue.length}</h2>
        ${queue.length ? queue.map(function (i) { return card(i, false); }) : html`<div class="empty sm">Nothing queued. Add an idea above.</div>`}</section>
      <${ui.Research} />
    </div>`;
  };

  /* ---------- Board ---------- */
  ui.Results = function (p) {
    var r = p.reel, st = RR.useState(Object.assign({ views: "", sends: "", saves: "", comments: "", leads: "" }, r.results || {})), v = st[0], set = st[1];
    var f = function (k, label) { return html`<label class="num"><span>${label}</span><input type="number" inputmode="numeric" min="0" id=${"res-" + r._id + k} value=${v[k]} onInput=${function (e) { var n = Object.assign({}, v); n[k] = e.target.value; set(n); }} /></label>`; };
    return html`<div class="results"><div class="num-grid">${f("views", "Views")}${f("sends", "Sends")}${f("saves", "Saves")}${f("comments", "Comments")}${f("leads", "Leads")}</div>
      <button class="btn sm primary" onClick=${function () { var out = {}; Object.keys(v).forEach(function (k) { out[k] = v[k] === "" ? null : +v[k]; }); out.at = Date.now(); RR.act.results(r._id, out).then(function () { RR.toast("Saved. Tomorrow's pick will weigh it.", "good"); }); }}>Save results</button></div>`;
  };
  ui.Board = function () {
    var op = RR.useState(null), openId = op[0], setOpen = op[1], vo = S.voice || {}, sv = RR.useState(null), draft = sv[0], setDraft = sv[1];
    var d = draft || { samples: vo.samples || "", never: vo.never || "" };
    var au = RR.useState(RR.ls.get("autoReview", true)), auto = au[0], setAuto = au[1];
    var posted = S.reels.filter(function (r) { return r.results && r.results.views != null; }).slice().reverse();
    var vals = posted.map(function (r) { return r.results.views; }).sort(function (a, b) { return a - b; }), median = vals.length ? vals[Math.floor((vals.length - 1) / 2)] : 0, top = Math.max.apply(null, vals.concat([1]));
    var u = S.usage;
    return html`<div class="stack">
      <section class="panel"><h2>Scoreboard</h2>
        ${posted.length ? html`<div class="bars">${posted.map(function (r) { var x = median ? r.results.views / median : 0;
            return html`<div class="bar-row"><span class="bar-name">${r.title}</span><div class="bar-track"><i class=${x >= 1 ? "up" : "down"} style=${"width:" + Math.max(2, Math.round(100 * r.results.views / top)) + "%"}></i><em style=${"left:" + Math.round(100 * median / top) + "%"}></em></div><span class="mono">${Number(r.results.views).toLocaleString()}</span></div>`; })}
            <p class="bar-key"><em></em>your median, ${median.toLocaleString()} views${posted.length < 5 ? ". Too few reels to call a pattern yet." : ""}</p></div>`
          : html`<div class="empty sm">Post a reel and put its numbers in below. This fills in as a chart of each reel against your own median, which is the only comparison that tells you what to make more of.</div>`}
      </section>
      <section class="panel"><h2>Every reel</h2>
        ${S.reels.length ? S.reels.map(function (r) { var isOpen = openId === r._id;
          return html`<div class=${RR.cls("reel-row", r._id === S.currentId && "reel-current")}>
            <button class="reel-main" onClick=${function () { setOpen(isOpen ? null : r._id); }}>
              <span class="mono dim">${r._id}</span><b>${r.title}</b>
              <span class="row"><span class=${"stage-chip st-" + r.status}>${RR.STAGE_LABEL[r.status] || r.status}</span>${r._id === S.currentId && html`<span class="tag-on">On the slate</span>`}${r.results && r.results.views != null && html`<span class="mono dim">${Number(r.results.views).toLocaleString()} views</span>`}</span></button>
            ${isOpen && html`<div class="reel-open"><div class="row wrap">
                <button class="btn sm" onClick=${function () { RR.view(r._id); RR.go("today"); }}>Open</button>
                ${r._id !== S.currentId && html`<button class="btn sm" onClick=${function () { RR.act.makeCurrent(r._id); RR.go("today"); }}>Put on today's slate</button>`}</div>
              <p class="dim">After it has been up 48 hours, enter what Instagram shows under Insights.</p><${ui.Results} reel=${r} /></div>`}
          </div>`; }) : html`<div class="empty sm">No reels yet.</div>`}
      </section>
      <section class="panel"><h2>Your voice</h2>
        <p class="dim">Every script and rewrite is written to sound like this. Paste three captions or reels of yours, word for word.</p>
        <label class="field"><span>How I actually talk</span><textarea id="voice-samples" value=${d.samples} placeholder="Paste your own captions or what you said in a reel that sounded most like you." onInput=${function (e) { setDraft({ samples: e.target.value, never: d.never }); }}></textarea></label>
        <label class="field"><span>Words and topics I never use</span><input type="text" id="voice-never" value=${d.never} placeholder="dream home, nestled, hustle…" onInput=${function (e) { setDraft({ samples: d.samples, never: e.target.value }); }} /></label>
        <button class="btn primary" disabled=${!draft} onClick=${function () { RR.act.voice({ samples: d.samples.slice(0, 6000), never: d.never.slice(0, 500) }).then(function () { setDraft(null); RR.toast("Voice saved.", "good"); }); }}>Save my voice</button>
      </section>
      <section class="panel"><h2>Set-up</h2>
        <label class="switch"><input type="checkbox" id="auto-review" checked=${auto} onChange=${function (e) { setAuto(e.target.checked); RR.ls.set("autoReview", e.target.checked); }} />Have Claude look at every take as soon as it uploads</label>
        ${u && html`<div class="meter"><div class="meter-bar"><i style=${"width:" + Math.min(100, Math.round(100 * u.bytes / (u.maxBytes || 1))) + "%"}></i></div><span class="mono">${RR.mb(u.bytes)} of ${RR.mb(u.maxBytes)} used</span></div>`}
        <p class="dim">Clips are capped at 20 MB each. Finished reels are cleared from here by Claude after you approve them.</p>
      </section>
    </div>`;
  };

  /* ---------- Ask ---------- */
  var chat = { turns: [], ctl: null };
  ui.Ask = function (p) {
    var st = RR.useState({ text: "", live: "", busy: false, err: "", n: 0 }), s = st[0], set = st[1], end = RR.useRef(null);
    RR.useEffect(function () { if (end.current) end.current.scrollIntoView({ block: "end" }); }, [s.live, s.n]);
    var send = function (q) {
      q = (q || s.text).trim(); if (!q || s.busy) return;
      chat.turns.push({ role: "user", content: q }); chat.ctl = new AbortController();
      set({ text: "", live: "", busy: true, err: "", n: s.n + 1 });
      RR.ask(chat.turns.slice(-12), function (x) { set(function (o) { return Object.assign({}, o, { live: x.text }); }); }, chat.ctl.signal).then(function (r) {
        chat.turns.push({ role: "assistant", content: r.text }); set(function (o) { return { text: o.text, live: "", busy: false, err: "", n: o.n + 1 }; });
      }, function (e) { if (e && e.text) chat.turns.push({ role: "assistant", content: e.text }); else chat.turns.pop(); set(function (o) { return { text: o.text || q, live: "", busy: false, err: e && e.code === "cancelled" ? "" : RR.aiError(e), n: o.n + 1 }; }); });
    };
    var starters = ["It started raining. What do I change?", "Give me a stronger last line.", "Is this too long? What would you cut?", "Write the Spanish version of line one."];
    return html`<${ui.Sheet} title="Ask Claude" onClose=${p.onClose}>
      <p class="dim">Answers on the spot, knowing today's script and what is working. It cannot see your clips from here.</p>
      <div class="chat">
        ${!chat.turns.length && !s.busy && html`<div class="starters">${starters.map(function (q) { return html`<button class="option" onClick=${function () { send(q); }}>${q}</button>`; })}</div>`}
        ${chat.turns.map(function (t) { return html`<div class=${"msg msg-" + (t.role === "user" ? "nick" : "claude")}>${t.content}</div>`; })}
        ${s.busy && html`<div class="msg msg-claude">${s.live || html`<span class="thinking"><span class="spin"></span>Thinking</span>`}</div>`}
        ${s.err && html`<p class="fix fix-bad">${s.err}</p>`}<div ref=${end}></div>
      </div>
      <div class="row ask-row"><input type="text" id="ask-input" value=${s.text} placeholder="Ask about this reel" onInput=${function (e) { set(Object.assign({}, s, { text: e.target.value })); }} onKeyDown=${function (e) { if (e.key === "Enter") send(); }} />
        ${s.busy ? html`<button class="btn" onClick=${function () { chat.ctl && chat.ctl.abort(); }}>Stop</button>` : html`<button class="btn primary" disabled=${!s.text.trim()} onClick=${function () { send(); }}>Ask</button>`}</div>
    <//>`;
  };

  /* ---------- shell ---------- */
  var TABS = [["today", "Today"], ["cut", "Cut"], ["ideas", "Ideas"], ["board", "Board"]];
  ui.App = function () {
    RR.useStore();
    var r = RR.reel(), sheet = S.sheet, close = function () { RR.set({ sheet: null }); };
    var View = { today: ui.Today, cut: ui.Cut, ideas: ui.Ideas, board: ui.Board }[S.tab];
    var rb = sheet && sheet.type === "rewrite" ? S.beats.filter(function (b) { return b._id === sheet.beat; })[0] : null;
    return html`<div class="app">
      <header class="top"><div class="stripe" aria-hidden="true"></div>
        <div class="top-row"><div class="brand"><b>REEL ROOM</b><span class="mono dim">v6 \u00B7 ${S.bank.length} videos</span></div>
          ${S.cap.sample && html`<button class="btn sm ask-btn" onClick=${function () { RR.set({ sheet: { type: "ask" } }); }}>Ask Claude</button>`}</div>
      </header>
      <main class="wrap"><${View} /></main>
      <nav class="tabbar" aria-label="Sections">${TABS.map(function (t) { return html`<a href=${"#" + t[0]} aria-current=${S.tab === t[0] ? "page" : null}>${t[1]}</a>`; })}</nav>
      ${S.shoot && html`<${ui.ShootMode} />`}
      ${S.practice && html`<${ui.Practice} />`}
      ${rb && html`<${ui.Rewrite} beat=${rb} onClose=${close} />`}
      ${sheet && sheet.type === "ask" && html`<${ui.Ask} onClose=${close} />`}
      <div class="toasts" aria-live="polite">${S.toasts.map(function (t) { return html`<div class=${"toast toast-" + t.kind}>${t.text}</div>`; })}</div>
    </div>`;
  };

  var root = document.getElementById("app");
  root.textContent = "";
  RR.render(html`<${ui.App} />`, root);
  var use = window.claude && window.claude.use;
  if (!use) RR.set({ booted: true, failed: "signed_out" });
  else Promise.all(["db", "assets", "sample"].map(function (n) { return window.claude.use(n).catch(function () { return null; }); }))
    .then(function (c) { RR.boot({ db: c[0], assets: c[1], sample: c[2] }); });
})();
