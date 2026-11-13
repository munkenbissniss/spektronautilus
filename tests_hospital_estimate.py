"""Loop Hospital: the time estimate. Two short trial runs of the real recipe predict the whole job, so the estimate is not too low when the
heavy steps come last. Real ffmpeg (the computer's own) as the engine; it reports no progress until a pass ends, which is the hardest
case for the old guess from the bar. NOT tested: a phone, Video2X (AI)."""
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
ff("-f", "lavfi", "-i", "testsrc2=size=320x180:rate=25:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "short.mp4"))
ff("-f", "lavfi", "-i", "testsrc2=size=640x640:rate=25:duration=3.5", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "square.mp4"))
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
  window.__VJ_ENGINE__ = { kind: 'wasm', async load() {}, async exec(args) { const k = await window.host('start', JSON.stringify(args)); for (;;) { const r = await window.host('poll', k); if (r) return JSON.parse(r); await new Promise(z => setTimeout(z, 150)); } },
    async write(p, u8) { await window.host('write', p, b64(u8)); }, async read(p) { return un64(await window.host('read', p)); }, async remove(p) { await window.host('remove', p); },
    async mount(file) { const d = 'm' + (++n); await window.host('write', d + '/' + file.name, b64(new Uint8Array(await file.arrayBuffer()))); return d + '/' + file.name; },
    async unmount(p) { await window.host('rmdir', p.split('/')[0]); }, terminate() {} }; })();"""
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()

URL = f"http://127.0.0.1:{srv.server_port}/tools/hospital/index.html"
import time
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context().new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(ENGINE_JS); pg.expose_function("host", host)
    pg.goto(URL); pg.wait_for_selector("#picker", state="attached")
    pg.set_input_files("#picker", str(IN / "long clip.mp4")); pg.wait_for_selector("#facts span:not(.muted)", timeout=60000)
    # heavy work late in the job: 24 -> 60 fps with motion interpolation, then make it loop (crossfade)
    pg.evaluate("Object.assign(HOSP.R.fps, { on: true, target: 60, engine: 'motion' }); Object.assign(HOSP.R.loop, { on: true, mode: 'crossfade', fade: 1.5 }); Object.assign(HOSP.R.size, { on: true, box: '640x360', fit: 'keep' })")
    t0 = time.time(); pg.click("#go"); seen = []; measuring = False
    while time.time() - t0 < 600:
        txt = pg.inner_text("#cur") if pg.locator("#cur").count() else ""
        if "Measuring" in txt: measuring = True
        import re
        m = re.search(r"(?:(\d+)% · )?(\d+):(\d\d) · about (?:(\d+):)?(\d+):(\d\d) left", txt)
        if m:
            pct, el = int(m.group(1) or 0), int(m.group(2)) * 60 + int(m.group(3))
            left = int(m.group(4) or 0) * 3600 + int(m.group(5)) * 60 + int(m.group(6)); seen.append((time.time() - t0, pct, el, left))
        if pg.locator("#res a").count(): break
        pg.wait_for_timeout(1000)
    total = time.time() - t0
    check(pg.locator("#res a").count() == 1, f"the job finished in {total:.0f} s")
    check(measuring, "it says it is measuring first")
    msg = pg.inner_text("#msg"); check("estimated" in msg, f"the result says how long it took and what was estimated: {msg!r}")
    # every shown estimate (time so far + time left) against the real total
    pred = [(t, pct, t + left) for t, pct, el, left in seen]
    early = [p for t, pct, p in pred if t < total * 0.5]
    print("  shown:", [(round(t), pct, round(p)) for t, pct, p in pred][:40])
    check(len(early) >= 3, f"an estimate is shown early ({len(early)} times in the first half)")
    lo = min(p for _, _, p in pred) if pred else 0
    check(lo >= total * 0.7, f"never too low: the lowest predicted total was {lo:.0f} s, the real total {total:.0f} s")
    hi = max(p for _, _, p in pred) if pred else 0
    check(hi <= total * 1.8, f"not wildly too high either: highest {hi:.0f} s")
    # like the clips from a phone: short and square, cropped to 16:9, 60 fps with Smooth motion, 2x slower, brought to life and repeated
    # to 16 s. The heavy steps work on the short clip only; the repeat is light. (This was estimated 1.4 to 3.7 times too high.)
    pg.click("#reset")
    with pg.expect_navigation(): pg.click("#reset")
    pg.wait_for_selector("#picker", state="attached"); pg.set_input_files("#picker", str(IN / "square.mp4")); pg.wait_for_selector("#facts span:not(.muted)", timeout=60000)
    pg.evaluate("""Object.assign(HOSP.R.crop, { on: true, shape: '169' }); Object.assign(HOSP.R.fps, { on: true, target: 60, engine: 'motion' });
      Object.assign(HOSP.R.slow, { on: true, factor: 2, engine: 'motion' }); HOSP.R.life.on = true; HOSP.R.life.minSeconds = 16; Object.assign(HOSP.R.size, { on: true, box: '640x360', fit: 'keep' })""")
    t0 = time.time(); pg.click("#go"); pg.wait_for_selector("#res a", timeout=600000)
    msg = pg.inner_text("#msg"); m = re.search(r"Done in (\d+):(\d\d) \(estimated (\d+):(\d\d)\)", msg)
    real, est = (int(m.group(1)) * 60 + int(m.group(2)), int(m.group(3)) * 60 + int(m.group(4))) if m else (0, 0)
    check(m and 0.75 * real <= est <= 1.4 * real, f"short clip repeated to 16 s: estimated {est} s, took {real} s ({msg!r})")
    # a short job is not measured
    pg.click("#reset"); 
    with pg.expect_navigation(): pg.click("#reset")
    pg.wait_for_selector("#picker", state="attached"); pg.set_input_files("#picker", str(IN / "short.mp4")); pg.wait_for_selector("#facts span:not(.muted)", timeout=60000)
    pg.click("#go"); saw = False
    for _ in range(120):
        if "Measuring" in (pg.inner_text("#cur") or ""): saw = True
        if pg.locator("#res a").count(): break
        pg.wait_for_timeout(250)
    check(pg.locator("#res a").count() == 1 and "estimated" not in pg.inner_text("#msg"), "a short job is not measured first (it would cost more than it saves)")
    check(not errs, f"no script errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
