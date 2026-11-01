"""Magic Mixer end to end in the browser: a short song and three loops become a video, and a render that breaks must not freeze the queue."""
import functools, http.server, json, subprocess, tempfile, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent
T = Path(tempfile.mkdtemp(prefix="spkmix_")); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *a], check=True)
ff("-f", "lavfi", "-i", "aevalsrc=0.8*sin(2*PI*60*t)*exp(-8*mod(t\\,0.5))+0.1*sin(2*PI*440*t):s=44100:d=10", str(T / "song.wav"))
for i, c in enumerate(("testsrc2", "smptebars", "mandelbrot")):
    ff("-f", "lavfi", "-i", f"{c}=size=640x360:rate=25", "-t", "2", "-c:v", "libvpx", "-b:v", "500k", str(T / f"loop{i}.webm"))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_port}"
def run(b, path, mobile):
    print('==', path)
    pg = b.new_context(viewport={'width': 1200, 'height': 900}).new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE + path); pg.wait_for_selector("#add")
    if not pg.evaluate("!!window.MediaRecorder && !!MIME"): print("SKIP: this browser cannot record video"); return
    pg.set_input_files("#fA", str(T / "song.wav")); pg.set_input_files("#fV", [str(T / f"loop{i}.webm") for i in range(3)])
    pg.wait_for_function("document.querySelector('#add') && !document.querySelector('#add').disabled", timeout=60000)
    (None if mobile else pg.evaluate("setO('res', '1280x720')"))
    states = lambda: pg.evaluate("jobs.map(j => j.status)")
    pg.click("#add"); pg.wait_for_function("jobs.length >= 1 && ['done','failed','stopped'].includes(jobs[0].status)", timeout=180000)
    j = pg.evaluate("({s: jobs[0].status, err: jobs[0].err || '', size: jobs[0].file ? jobs[0].file.size : 0, pool: pool.filter(p => p.loop >= 0).length, urls: pool.filter(p => p.url).length})")
    check(j["s"] == "done" and j["size"] > 20000, f"the video was made: {j}")
    check(j["pool"] == 0 and j["urls"] == 0, "the hidden video elements are given back when the job is done")
    data = pg.evaluate("""async () => { const u8 = new Uint8Array(await jobs[0].file.arrayBuffer()); let s=''; for (let k=0;k<u8.length;k+=0x8000) s+=String.fromCharCode.apply(null,u8.subarray(k,k+0x8000)); return btoa(s); }""")
    import base64; out = T / ("mix." + pg.evaluate("EXT")); out.write_bytes(base64.b64decode(data))
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)], capture_output=True, text=True).stdout.strip()
    check(d and abs(float(d) - 10) < 2.5, f"the file plays and is about 10 s long: {d}")
    leave = "(() => { const e = new Event('beforeunload', { cancelable: true }); window.dispatchEvent(e); return e.defaultPrevented; })()"
    check(pg.evaluate(leave) is True, "leaving the page asks first while a finished video is not downloaded")
    pg.evaluate("(() => { const a = jobs[0].el.querySelector('a[download]'); a.addEventListener('click', e => e.preventDefault(), { once: true }); a.click(); })()")
    check(pg.evaluate(leave) is False, "after the download there is no question")
    # a recorder that throws: the job must fail with a message, and the queue must go on
    pg.evaluate("window.__MR = MediaRecorder; window.MediaRecorder = class { constructor() { throw new Error('boom'); } }; 0")
    pg.click("#add"); pg.wait_for_function("jobs.length >= 2 && jobs[1].status === 'failed'", timeout=120000)
    check("boom" in pg.evaluate("jobs[1].err"), "a broken render ends as Failed, with the reason: " + pg.evaluate("jobs[1].err"))
    check(pg.evaluate("running === false && cur === null"), "the queue is free again")
    pg.evaluate("window.MediaRecorder = window.__MR; 0")
    pg.click("#add"); pg.wait_for_function("jobs.length >= 3 && ['done','failed'].includes(jobs[2].status)", timeout=180000)
    check(pg.evaluate("jobs[2].status") == "done", "the next job still works after a failure")
    check(not errs, f"no script errors {errs[:2]}")

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    run(b, "/mixer/index.html?desktop=1", False); run(b, "/mixer-mobile/index.html", True)
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
