"""Loop Hospital: the preview makes new frames the fast way (Soft blend), while the saved clip keeps the chosen method (Smooth motion).
The ffmpeg commands are recorded and checked. Real ffmpeg (the computer's own) as the engine."""
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
ff("-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "wide clip.mp4"))
ARGS = []
def host(op, a=None, b=None):
    if op == "exec":
        ARGS.append(" ".join(json.loads(a)))
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
URL = f"http://127.0.0.1:{srv.server_port}/tools/hospital/index.html"
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context().new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(ENGINE_JS); pg.expose_function("host", host)
    pg.goto(URL); pg.wait_for_selector("#picker", state="attached")
    pg.set_input_files("#picker", str(IN / "wide clip.mp4")); pg.wait_for_selector("#facts span:not(.muted)", timeout=60000)
    pg.evaluate("HOSP.R.fps.on = true; HOSP.R.slow.on = true")
    check(pg.evaluate("HOSP.R.fps.engine") == "motion" and pg.evaluate("HOSP.R.slow.engine") == "motion", "Smooth motion is chosen")
    ARGS.clear(); pg.click("#prev"); pg.wait_for_function("document.querySelector('#vafter').src && !document.querySelector('#prev').disabled", timeout=120000)
    prev = " | ".join(ARGS)
    check("minterpolate" not in prev and "framerate=" in prev, "the preview makes new frames with the fast blend")
    check("softer" in pg.inner_text("#msg"), f"and says so: {pg.inner_text('#msg')!r}")
    check(pg.evaluate("HOSP.R.fps.engine") == "motion", "the choice itself is not changed by the preview")
    ARGS.clear(); pg.click("#go"); pg.wait_for_selector("#res a", timeout=300000)
    check("minterpolate" in " | ".join(ARGS), "the saved clip uses Smooth motion (full quality)")
    check(not errs, f"no script errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
