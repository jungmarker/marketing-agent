/* Reel Room - core: store, data wiring, helpers, actions. Everything hangs off window.RR. */
(function () {
  "use strict";
  var RR = (window.RR = {});
  var P = window.preact, H = window.preactHooks;
  RR.h = P.h; RR.render = P.render; RR.html = window.htm.bind(P.h);
  RR.useState = H.useState; RR.useEffect = H.useEffect; RR.useRef = H.useRef; RR.useMemo = H.useMemo;

  RR.FOOTER = "—\nNick Jungmarker | REALTOR® | Long & Foster Real Estate\n(301) 875-7182 | jungmarker.com\nEqual Housing Opportunity 🏠";
  RR.STAGES = ["scripted", "shooting", "ready_to_edit", "review", "approved", "posted"];
  RR.STAGE_LABEL = { scripted: "Script", shooting: "Shoot", ready_to_edit: "Cut", changes: "Cut", review: "Review", approved: "Approved", posted: "Posted" };

  /* ---------- store ---------- */
  var S = (RR.S = {
    cap: { db: null, assets: null, sample: null }, booted: false, failed: null,
    currentId: null, viewId: null, reels: [], beats: [], clips: [], notes: [], ideas: [],
    research: null, voice: null, bank: [], jobs: {}, toasts: [], tab: "today", shoot: null, sheet: null,
    loadedView: false, usage: null,
  });
  var subs = [];
  RR.set = function (patch) { Object.assign(S, patch); subs.forEach(function (f) { f(); }); };
  RR.useStore = function () {
    var st = RR.useState(0), force = st[1];
    RR.useEffect(function () { var f = function () { force(function (n) { return n + 1; }); }; subs.push(f); return function () { subs.splice(subs.indexOf(f), 1); }; }, []);
    return S;
  };
  RR.toast = function (text, kind) {
    var t = { id: Date.now() + Math.random(), text: text, kind: kind || "info" };
    RR.set({ toasts: S.toasts.concat([t]) });
    setTimeout(function () { RR.set({ toasts: S.toasts.filter(function (x) { return x.id !== t.id; }) }); }, kind === "bad" ? 7000 : 3500);
  };
  RR.job = function (key, label) { var j = Object.assign({}, S.jobs); if (label) j[key] = label; else delete j[key]; RR.set({ jobs: j }); };

  /* ---------- helpers ---------- */
  RR.words = function (t) { return ((t || "").match(/[A-Za-z0-9$%'’À-ſ-]+/g) || []).length; };
  RR.sayTime = function (t) { return RR.words(t) * 60 / 165; };
  RR.sec = function (n) { return (Math.round((n || 0) * 10) / 10).toFixed(1) + "s"; };
  RR.tc = function (n) { n = Math.max(0, n || 0); var m = Math.floor(n / 60), s = n - m * 60; return m + ":" + (s < 10 ? "0" : "") + s.toFixed(1); };
  RR.mb = function (n) { return ((n || 0) / 1048576).toFixed(1) + " MB"; };
  RR.when = function (ms) { try { return new Date(ms).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }); } catch (_) { return ""; } };
  RR.cls = function () { return Array.prototype.filter.call(arguments, Boolean).join(" "); };
  RR.ls = { get: function (k, d) { try { var v = localStorage.getItem("rr." + k); return v == null ? d : JSON.parse(v); } catch (_) { return d; } },
            set: function (k, v) { try { localStorage.setItem("rr." + k, JSON.stringify(v)); } catch (_) {} } };
  function rows(q) { return q.docs.map(function (d) { var o = d.data() || {}; o._id = d.id; return o; }); }

  /* ---------- derived ---------- */
  RR.reel = function () { return S.reels.filter(function (r) { return r._id === S.viewId; })[0] || null; };
  RR.takes = function (beatId, kind) { return S.clips.filter(function (c) { return c.beat === beatId && c.kind === (kind || "aroll"); }); };
  RR.verdict = function (c) { return c.status === "keep" || c.status === "retake" ? c.status : (c.ai && c.ai.verdict) || (c.checks && c.checks.some(function (k) { return k.level === "bad"; }) ? "retake" : "new"); };
  RR.chosen = function (beat, kind) {
    var t = RR.takes(beat._id, kind), pick = kind === "broll" ? beat.take_broll : beat.take;
    if (!t.length) return null;
    var hit = t.filter(function (c) { return c._id === pick; })[0];
    if (hit) return hit;
    var good = t.filter(function (c) { return RR.verdict(c) === "keep"; });
    return (good.length ? good : t)[(good.length ? good : t).length - 1];
  };
  RR.beatState = function (beat) {
    var t = RR.takes(beat._id);
    if (!t.length) return "todo";
    var c = RR.chosen(beat), v = RR.verdict(c);
    return v === "keep" ? "good" : v === "retake" ? "retake" : "sent";
  };
  RR.clipLen = function (c) { return c ? Math.max(0.2, (c.out != null ? c.out : c.dur || 0) - (c.in || 0)) : 0; };
  RR.beatLen = function (beat) {
    var c = RR.chosen(beat);
    if (!beat.say) return c ? Math.min(RR.clipLen(c), beat.seconds || 3) : (beat.seconds || 3);   /* a silent shot holds for its set time */
    return c ? RR.clipLen(c) : RR.sayTime(beat.say);
  };
  RR.total = function () { return S.beats.reduce(function (n, b) { return n + RR.beatLen(b); }, 0); };
  /* shots in the order you would shoot them: by stop, cutaways after the lines at that stop */
  RR.shotList = function () {
    var r = RR.reel(), byId = {}, out = [], seen = {};
    S.beats.forEach(function (b) { byId[b._id] = b; });
    var stops = (r && r.stops && r.stops.length) ? r.stops : [{ name: "Shots", beats: S.beats.map(function (b) { return b._id; }) }];
    stops.forEach(function (st, si) {
      (st.beats || []).forEach(function (id) { if (byId[id] && !seen[id]) { seen[id] = 1; out.push({ beat: byId[id], kind: "aroll", stop: st.name, tip: st.tip, si: si }); } });
      (st.beats || []).forEach(function (id) { if (byId[id] && byId[id].broll) out.push({ beat: byId[id], kind: "broll", stop: st.name, tip: st.tip, si: si }); });
    });
    S.beats.forEach(function (b) { if (!seen[b._id]) { out.push({ beat: b, kind: "aroll", stop: "Other", si: 99 }); if (b.broll) out.push({ beat: b, kind: "broll", stop: "Other", si: 99 }); } });
    return out;
  };
  RR.progress = function () {
    var list = RR.shotList(), done = list.filter(function (s) { return RR.takes(s.beat._id, s.kind).length; }).length;
    return { done: done, of: list.length, pct: list.length ? Math.round(100 * done / list.length) : 0 };
  };

  /* ---------- data ---------- */
  var viewUnsub = [];
  function fail(e) { if (!S.booted) RR.set({ failed: (e && e.code) || "unavailable", booted: true }); }
  RR.view = function (id) {
    if (id === S.viewId && viewUnsub.length) return;
    viewUnsub.forEach(function (u) { try { u(); } catch (_) {} });
    viewUnsub = [];
    RR.set({ viewId: id, beats: [], clips: [], notes: [], loadedView: false });
    if (!id || !S.cap.db) return;
    var db = S.cap.db, base = "reels/" + id;
    viewUnsub.push(db.collection(base + "/beats").onSnapshot(function (q) { RR.set({ beats: rows(q).sort(function (a, b) { return a._id < b._id ? -1 : 1; }), loadedView: true }); }, fail));
    viewUnsub.push(db.collection(base + "/clips").onSnapshot(function (q) { RR.set({ clips: rows(q).sort(function (a, b) { return (a.at || 0) - (b.at || 0); }) }); }, fail));
    viewUnsub.push(db.collection(base + "/notes").onSnapshot(function (q) { RR.set({ notes: rows(q).sort(function (a, b) { return (a.at || 0) - (b.at || 0); }) }); }, fail));
  };
  RR.boot = function (cap) {
    S.cap = cap;
    if (!cap.db) return RR.set({ booted: true, failed: "signed_out" });
    var db = cap.db, timer = setTimeout(function () { if (!S.booted) RR.set({ booted: true, failed: "timeout" }); }, 10000);
    db.doc("meta/current").onSnapshot(function (d) {
      clearTimeout(timer);
      var id = d.exists ? (d.data() || {}).reel : null;
      var first = !S.booted || S.viewId === S.currentId;
      RR.set({ currentId: id, booted: true, failed: null });
      if (first) RR.view(id);
    }, fail);
    db.collection("reels").onSnapshot(function (q) { RR.set({ reels: rows(q).sort(function (a, b) { return a._id < b._id ? 1 : -1; }) }); }, function () {});
    db.collection("ideas").onSnapshot(function (q) { RR.set({ ideas: rows(q) }); }, function () {});
    db.collection("bank").onSnapshot(function (q) { var all = []; rows(q).forEach(function (d) { (d.videos || []).forEach(function (v) { all.push(v); }); }); RR.set({ bank: all }); }, function () {});
    db.doc("research/current").onSnapshot(function (d) { RR.set({ research: d.exists ? d.data() : null }); }, function () {});
    db.doc("profile/voice").onSnapshot(function (d) { RR.set({ voice: d.exists ? d.data() : null }); }, function () {});
    RR.refreshUsage();
  };
  RR.refreshUsage = function () { if (S.cap.assets) S.cap.assets.list().then(function (r) { RR.set({ usage: r.usage }); }, function () {}); };

  /* ---------- actions ---------- */
  function base() { return "reels/" + S.viewId; }
  function quiet(p) { return p.then(function (x) { return x; }, function (e) { RR.toast("That did not save (" + ((e && e.code) || "error") + "). Try again.", "bad"); }); }
  RR.act = {
    reel: function (patch) { return quiet(S.cap.db.doc(base()).update(patch)); },
    status: function (s) { return RR.act.reel({ status: s, status_at: Date.now() }); },
    beat: function (id, patch) { return quiet(S.cap.db.doc(base() + "/beats/" + id).update(patch)); },
    clip: function (id, patch) { return quiet(S.cap.db.doc(base() + "/clips/" + id).update(patch)); },
    removeClip: function (c) {
      return quiet(S.cap.db.doc(base() + "/clips/" + c._id).delete()).then(function () {
        if (S.cap.assets && c.asset) S.cap.assets.delete(c.asset).then(RR.refreshUsage, function () {});
      });
    },
    note: function (text, beat) {
      text = (text || "").trim(); if (!text) return Promise.resolve();
      var doc = { from: "nick", text: text.slice(0, 4000), at: Date.now() }; if (beat) doc.beat = beat;
      return quiet(S.cap.db.collection(base() + "/notes").add(doc));
    },
    line: function (beat, text) {
      text = (text || "").trim(); if (!text || text === beat.say) return Promise.resolve();
      return RR.act.beat(beat._id, { say: text, say_before: beat.say || "", edited_by: "nick", edited_at: Date.now() });
    },
    makeCurrent: function (id) { return quiet(S.cap.db.doc("meta/current").set({ reel: id, at: Date.now() })).then(function () { RR.view(id); }); },
    verify: function (i) {
      var r = RR.reel(), v = (r.verify || []).map(function (x) { return Object.assign({}, x); });
      v[i].done = !v[i].done; return RR.act.reel({ verify: v });
    },
    idea: function (id, patch) { return quiet(S.cap.db.doc("ideas/" + id).update(patch)); },
    addIdea: function (doc) { return quiet(S.cap.db.collection("ideas").add(Object.assign({ status: "queued", from: "nick", at: Date.now(), n: 0 }, doc))); },
    removeIdea: function (id) { return quiet(S.cap.db.doc("ideas/" + id).delete()); },
    nextIdea: function (idea) {
      S.ideas.forEach(function (i) { if (i.status === "next" && i._id !== idea._id) RR.act.idea(i._id, { status: "queued" }); });
      return RR.act.idea(idea._id, { status: idea.status === "next" ? "queued" : "next", picked_at: Date.now() });
    },
    voice: function (doc) { return quiet(S.cap.db.doc("profile/voice").set(Object.assign({ at: Date.now() }, doc))); },
    results: function (id, res) { return quiet(S.cap.db.doc("reels/" + id).update({ results: res, status: "posted", status_at: Date.now() })); },
    /* put a ready-made script from the bank on the slate */
    fromBank: function (v) {
      var d = new Date(), day = d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2), id = day + "-" + v.id;
      if (S.reels.some(function (r) { return r._id === id; })) return RR.act.makeCurrent(id);
      var where = (v.beats[0] && v.beats[0].location) || "One spot";
      var reel = { _id: id, date: day, title: v.title, formula: v.shape, why: "Answers a question people search: \u201C" + v.question + "\u201D", status: "scripted", status_at: Date.now(),
        target_seconds: v.seconds, caption: v.caption, verify: v.verify || [], kind: v.kind, bank_id: v.id, written_by: "bank",
        setup_detail: v.setup || null,
        stops: [{ name: where, tip: v.kind === "talk" ? "One clip per line. Move a step or turn between lines so the background changes." : v.kind === "point" ? "No talking. One continuous take: follow the moves on the next screen in order. Add the music in Instagram." : "One clip, no talking. The text is added on top. Add the music in Instagram.", beats: v.beats.map(function (b) { return b.id; }) }],
        setup: ["Rear camera, 1x lens, vertical, 1080p at 30. Each clip under 20 MB, so not 4K.", "HDR video off. Lock focus and exposure.", v.kind === "talk" ? "A second of silence before and after you speak." : "No audio needed. Leave empty space in the frame where the text goes.", "Keep the top fifth of the frame clear for the text card."] };
      var beats = v.beats.map(function (b) { var o = Object.assign({}, b); o._id = b.id; delete o.id; return o; });
      return RR.act.createReel(reel, beats).then(function () { return RR.act.makeCurrent(id); });
    },
    /* create a whole reel from a generated script */
    createReel: function (reel, beats) {
      var db = S.cap.db, id = reel._id;
      return quiet(db.doc("reels/" + id).set(reel).then(function () {
        return beats.reduce(function (p, b) { return p.then(function () { var d = Object.assign({}, b); delete d._id; return db.doc("reels/" + id + "/beats/" + b._id).set(d); }); }, Promise.resolve());
      })).then(function () { RR.view(id); });
    },
  };
  RR.go = function (tab) { if (location.hash !== "#" + tab) location.hash = tab; else RR.set({ tab: tab }); };
  function fromHash() { var h = (location.hash || "").replace("#", ""); return ["today", "cut", "ideas", "board"].indexOf(h) >= 0 ? h : "today"; }
  window.addEventListener("hashchange", function () { RR.set({ tab: fromHash() }); window.scrollTo(0, 0); });
  S.tab = fromHash();
})();
