"""Loop Hospital on a phone: switching to another app freezes the page. The work then waits, goes on when you come back, says so, and
the time away is not counted as working time. (The engine side, that the stall limit ignores time away, is in tests_engine.mjs.)
The freeze is simulated: the page is marked hidden and the engine stops answering until it is visible again. NOT tested: a real phone."""
import base64, functools, http.server, json, os, re, shutil, subprocess, tempfile, threading, zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent
T = Path(tempfile.mkdtemp(prefix="spknew_")); IN, FS = T / "in", T / "fs"; IN.mkdir(); FS.mkdir()
bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *a], check=True)
ff("-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=24:duration=12", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "long clip.mp4"))
PROCS = {}
def host(op, a=None, b=None):
    if op == "start":   # ffmpeg runs on its own, so the test can read the page while it works
        k = str(len(PROCS)); PROCS[k] = subprocess.Popen(["ffmpeg", "-nostdin", *json.loads(a)], cwd=FS, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE); return k
    if op == "poll":
        p = PROCS[a]
        if p.poll() is None: return ""
        err = p.stderr.read().decode("utf-8", "replace"); return json.dumps({"code": p.returncode, "log": [l for l in re.split(r"[\r\n]+", err) if l]})
    if op == "write": p = FS / a; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(base64.b64decode(b)); return ""
    if op == "read": return base64.b64encode((FS / a).read_bytes()).decode()
    if op == "remove": (FS / a).unlink(missing_ok=True); return ""
    if op == "rmdir": shutil.rmtree(FS / a, ignore_errors=True); return ""
    raise ValueError(op)
ENGINE_JS = r"""(() => { const b64 = u8 => { let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); };
  const un64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0)); let n = 0;
  window.__VJ_ENGINE__ = { kind: 'wasm', async load() {}, async exec(args) { const k = await window.host('start', JSON.stringify(args)); for (;;) { if (window.__frozen) { await new Promise(z => setTimeout(z, 100)); continue; } const r = await window.host('poll', k); if (r) return JSON.parse(r); await new Promise(z => setTimeout(z, 150)); } },
    async write(p, u8) { await window.host('write', p, b64(u8)); }, async read(p) { return un64(await window.host('read', p)); }, async remove(p) { await window.host('remove', p); },
    async mount(file) { const d = 'm' + (++n); await window.host('write', d + '/' + file.name, b64(new Uint8Array(await file.arrayBuffer()))); return d + '/' + file.name; },
    async unmount(p) { await window.host('rmdir', p.split('/')[0]); }, terminate() {} }; })();"""
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()

VIS = "window.__vis='visible';Object.defineProperty(document,'visibilityState',{get:()=>window.__vis,configurable:true});Object.defineProperty(document,'hidden',{get:()=>window.__vis==='hidden',configurable:true});"
URL = f"http://127.0.0.1:{srv.server_port}/tools/hospital/index.html"
import re, time
def away(pg, on):
    pg.evaluate(f"window.__frozen = {'true' if on else 'false'}; window.__vis = '{'hidden' if on else 'visible'}'; document.dispatchEvent(new Event('visibilitychange'))")
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context(viewport={"width": 390, "height": 800}, is_mobile=True, has_touch=True).new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(ENGINE_JS); pg.add_init_script(VIS); pg.expose_function("host", host)
    pg.goto(URL); pg.wait_for_selector("#picker", state="attached")
    pg.set_input_files("#picker", str(IN / "long clip.mp4")); pg.wait_for_selector("#facts span:not(.muted)", timeout=60000)
    pg.evaluate("Object.assign(HOSP.R.size, { on: true, box: '640x360', fit: 'keep' }); Object.assign(HOSP.R.loop, { on: true, mode: 'crossfade', fade: 1 })")
    pg.click("#go"); pg.wait_for_timeout(2500)
    clock = lambda: (lambda m: int(m.group(1)) * 60 + int(m.group(2)) if m else None)(re.search(r"(\d+):(\d\d)(?! left)", pg.inner_text("#cur")))
    c0 = clock(); away(pg, True); pg.wait_for_timeout(12000); away(pg, False); pg.wait_for_timeout(1200)
    check(pg.is_visible("#stop") and "Welcome back" in pg.inner_text("#msg"), f"after 12 s in the background: still working, and it says so: {pg.inner_text('#msg')!r}")
    c1 = clock(); check(c0 is not None and c1 is not None and c1 - c0 <= 5, f"the time away is not counted as working time (clock {c0} -> {c1} s over 14 s, 12 of them away)")
    pg.wait_for_selector("#res a", timeout=300000)
    check(pg.locator("#res a").count() == 1 and "stopped responding" not in pg.inner_text("#msg"), "the clip is finished from where it was, without an error")
    check(not errs, f"no script errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
