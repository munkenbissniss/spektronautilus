"""Loop Hospital on a phone: the preview video appears right above the preview button (no scrolling up); on a wide screen it stays next to Before."""
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
ff("-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=30:duration=3", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "wide clip.mp4"))
def host(op, a=None, b=None):
    if op == "exec":
        r = subprocess.run(["ffmpeg", "-nostdin", *json.loads(a)], cwd=FS, capture_output=True)
        return json.dumps({"code": r.returncode, "log": [l for l in re.split(r"[\r\n]+", r.stderr.decode("utf-8", "replace")) if l]})
    if op == "write": p = FS / a; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(base64.b64decode(b)); return ""
    if op == "read": return base64.b64encode((FS / a).read_bytes()).decode()
    if op == "remove": (FS / a).unlink(missing_ok=True); return ""
    if op == "rmdir": shutil.rmtree(FS / a, ignore_errors=True); return ""
    raise ValueError(op)
ENGINE_JS = r"""(() => { const b64 = u8 => { let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); };
  const un64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0)); let n = 0;
  window.__VJ_ENGINE__ = { kind: 'wasm', async load() {}, async exec(args) { return JSON.parse(await window.host('exec', JSON.stringify(args))); },
    async write(p, u8) { await window.host('write', p, b64(u8)); }, async read(p) { return un64(await window.host('read', p)); }, async remove(p) { await window.host('remove', p); },
    async mount(file) { const d = 'm' + (++n); await window.host('write', d + '/' + file.name, b64(new Uint8Array(await file.arrayBuffer()))); return d + '/' + file.name; },
    async unmount(p) { await window.host('rmdir', p.split('/')[0]); }, terminate() {} }; })();"""
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{srv.server_port}/tools/app/index.html"
URL = f"http://127.0.0.1:{srv.server_port}/tools/hospital/index.html"
def run(width, height):
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_context(viewport={"width": width, "height": height}).new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.add_init_script(ENGINE_JS); pg.expose_function("host", host); pg.goto(URL); pg.wait_for_selector("#picker", state="attached")
        pg.set_input_files("#picker", str(IN / "wide clip.mp4")); pg.wait_for_selector("#facts span:not(.muted)", timeout=60000)
        pg.click("#prev"); pg.wait_for_function("document.querySelector('#vafter').src && !document.querySelector('#fafter').classList.contains('hide')", timeout=120000); pg.wait_for_timeout(800)
        r = pg.evaluate("""() => { const f = document.querySelector('#fafter'), c4 = document.querySelector('#c4'), run = c4.querySelector('.run'), rect = f.getBoundingClientRect(), rr = run.getBoundingClientRect();
          return { inC4: f.parentElement === c4, above: f.compareDocumentPosition(document.querySelector('#prev')) & 4, gap: rr.top - rect.bottom, inView: rect.top >= 0 && rect.bottom <= innerHeight, btnInView: rr.top >= 0 && rr.bottom <= innerHeight, playing: !document.querySelector('#vafter').paused, state: { prev: document.querySelector('#prev').disabled, go: document.querySelector('#go').disabled, stopHidden: document.querySelector('#stop').classList.contains('hide'), cur: document.querySelector('#cur').textContent }, idle: !document.querySelector('#prev').disabled && !document.querySelector('#go').disabled && document.querySelector('#stop').classList.contains('hide'), overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth }; }""")
        b.close(); return r, errs
r, e = run(390, 800)
check(r["idle"], f"phone: after the preview the buttons are free again and Stop is hidden: {r['state']}")
check(r["inC4"] and r["above"], "phone: the After video is in the preview card, above the preview button")
check(0 <= r["gap"] < 40, f"phone: it sits right above the button (gap {r['gap']:.0f}px)")
check(r["inView"] and r["btnInView"], "phone: the preview and the button are both on screen after the preview is made")
check(not r["overflow"] and not e, f"phone: nothing overflows, no errors {e[:2]}")   # playback itself cannot be tested: the test browser has no H.264
with sync_playwright() as pw:   # a long file name (a hash) in the status line must wrap, not run off the screen
    b = pw.chromium.launch(); pg = b.new_context(viewport={"width": 390, "height": 800}).new_page()
    pg.add_init_script(ENGINE_JS); pg.expose_function("host", host); pg.goto(URL); pg.wait_for_selector("#picker", state="attached")
    pg.set_input_files("#picker", str(IN / "wide clip.mp4")); pg.wait_for_selector("#facts span:not(.muted)", timeout=60000)
    pg.evaluate("document.querySelector('#cur').textContent = '35fc02248182d16e846336df9b52c2b6a1d7e9f0c3b4a5968778695a4b3c2d1e0f · 50% · 1:00'")
    check(pg.evaluate("document.querySelector('#cur').scrollWidth <= document.querySelector('#cur').clientWidth + 1 && document.documentElement.scrollWidth <= document.documentElement.clientWidth"), "phone: a long file name in the status line wraps instead of running off the screen")
    b.close()
r, e = run(1200, 900)
check(not r["inC4"], "wide screen: the After video stays next to Before")
check(not e, f"wide screen: no errors {e[:2]}")
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
