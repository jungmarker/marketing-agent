#!/usr/bin/env python3
"""Build app/reel-room.html: one self-contained file. Inlines the UI libraries, every
script in app/js/, and the 40-video bank, so the page needs nothing else to show the list.
Run after changing app/shell.html, app/js/*.js or content/video-bank.json."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor")
shell = open(os.path.join(HERE, "shell.html"), encoding="utf-8").read()
def safe(js): return js.replace("</script", "<\\/script")
libs = ["preact.umd.js", "hooks.umd.js", "htm.umd.js"]
order = ["core.js", "media.js", "ai.js", "ui-shoot.js", "ui-cut.js", "ui-more.js"]
bank = json.load(open(os.path.join(HERE, "..", "content", "video-bank.json"), encoding="utf-8"))
guard = """<script>
(function () {
  function show(msg) {
    var a = document.getElementById("app"); if (!a) return;
    var d = document.createElement("div"); d.className = "boot-err";
    d.textContent = "Something broke while loading. Tell Claude this exact message: " + msg;
    a.insertBefore(d, a.firstChild);
  }
  window.addEventListener("error", function (e) { show((e.message || "error") + (e.filename ? " @ " + e.filename.split("/").pop() + ":" + e.lineno : "")); });
  window.addEventListener("unhandledrejection", function (e) { var r = e.reason || {}; show("promise: " + (r.code || r.message || String(r))); });
  setTimeout(function () { var a = document.getElementById("app"); if (a && /Loading Reel Room/.test(a.textContent)) show("still on the loading screen after 12 seconds"); }, 12000);
})();
</script>"""
parts = [guard]
parts += ["<script>/* %s */\n%s\n</script>" % (n, safe(open(os.path.join(VENDOR, n), encoding="utf-8").read())) for n in libs]
parts.append("<script>window.RR_BANK = %s;</script>" % safe(json.dumps(bank, ensure_ascii=False, separators=(",", ":"))))
parts += ["<script>/* %s */\n%s\n</script>" % (n, safe(open(os.path.join(HERE, "js", n), encoding="utf-8").read())) for n in order]
out = re.sub(r'<script src="[^"]+"></script>\s*', "", shell).rstrip() + "\n" + "\n".join(parts) + "\n"
open(os.path.join(HERE, "reel-room.html"), "w", encoding="utf-8").write(out)
print("app/reel-room.html", round(len(out.encode()) / 1024), "KB")
