"""Beat-synced cutting in the Magic Mixer (Cuts & sync): build-up rush, hard cuts, and a real render with the cut options on (desktop and phone)."""
import functools, http.server, subprocess, tempfile, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent
T = Path(tempfile.mkdtemp(prefix="spkcuts_")); bad = []
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
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    pg = b.new_context().new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/mixer/index.html?desktop=1"); pg.wait_for_selector("#add")
    PLAN = """() => { const nb = 256, bt = Array.from({ length: nb + 1 }, (_, i) => i * .5), rnd = mkrng(5);
      const A = { dur: nb * .5, tempo: 120, bt, nb, energy: Array.from({ length: nb }, (_, i) => .5 + .3 * Math.sin(i / 9)), phase: 0, sections: [[0, 128], [128, 256]], cluster: [0, 1], breaks: [], drops: [128], buildup: new Array(nb).fill(false), kicks: [], kstr: [], feel: {} };
      const L = Array.from({ length: 5 }, (_, i) => ({ v: Array.from({ length: 15 }, (_, d) => Math.sin(i * 3 + d)), mm: i / 5, name: 'l' + i })), S = normLoops(L, 0);
      const run = (over) => { const o = { ...getO(), fade: 8, accent: true, ...over }; const P = plan(A, L, S, o, mkrng(5)); return P.slots.map(s => ({ len: s.i1 - s.i0, i0: s.i0, xf: s.xf, kind: s.kind })); };
      return { base: run({ hardCuts: 0, rush: 0 }), rush: run({ hardCuts: 0, rush: 1 }), half: run({ hardCuts: 0, rush: .5 }), hard: run({ hardCuts: 1, rush: 0 }) }; }"""
    r2 = pg.evaluate(PLAN)
    before = [s for s in r2["rush"] if s["i0"] < 128 and s["i0"] >= 128 - 16]
    check(sum(s["len"] for s in before) == 16 and before[-1]["len"] == 1 and before[0]["len"] > before[-1]["len"], f"build-up rush: the last 4 bars before the drop get shorter and shorter {[s['len'] for s in before]}")
    check(all(before[i]["len"] >= before[i + 1]["len"] for i in range(len(before) - 1)), "the shots never get longer on the way into the drop")
    check(any(s["i0"] == 128 for s in r2["rush"]), "a shot starts exactly on the drop")
    halfb = [s["len"] for s in r2["half"] if 128 - 16 <= s["i0"] < 128]; check(min(halfb) >= 2, f"rush 0.5 stops at 2 beats {halfb}")
    check(min(s["len"] for s in r2["base"] if s["i0"] < 128 - 16) >= 4, "without rush the shots are not cut short")
    hard = [s for s in r2["hard"][1:] if s["xf"] == 0]; soft = [s for s in r2["base"][1:] if s["xf"] > 0]
    check(len(hard) >= len(r2["hard"]) * .6 and len(soft) == len(r2["base"]) - 1, f"hard cuts: {len(hard)} of {len(r2['hard']) - 1} changes are cuts; without it {len(soft)} fades")
    check("Demo" not in pg.inner_text("#pre") and not pg.evaluate("!!window.SPKDemo"), "the Demo mood and its overlay effects are gone")
    check(pg.locator("#o_dPlasma").count() == 0 and pg.locator("#o_dFlash").count() == 0, "no demo overlay options are left")
    pg.evaluate("setO('hardCuts', .8); setO('rush', 1); setO('cutStart', true); setO('tempoLock', true); setO('punch', .4); setO('res', '1280x720')")
    pg.set_input_files("#fA", str(T / "song.wav")); pg.set_input_files("#fV", [str(T / f"loop{i}.webm") for i in range(3)])
    pg.wait_for_function("document.querySelector('#add') && !document.querySelector('#add').disabled", timeout=60000)
    pg.click("#add"); pg.wait_for_function("jobs.length >= 1 && ['done','failed','stopped'].includes(jobs[0].status)", timeout=240000)
    j = pg.evaluate("({s: jobs[0].status, err: jobs[0].err || '', size: jobs[0].file ? jobs[0].file.size : 0})")
    check(j["s"] == "done" and j["size"] > 20000, f"desktop: a video with the cut options on was made: {j}")
    check(not errs, f"no script errors {errs[:2]}")
    # phone version
    pm = b.new_context(viewport={"width": 400, "height": 800}).new_page(); errs2 = []; pm.on("pageerror", lambda e: errs2.append(str(e)))
    pm.goto(BASE + "/mixer-mobile/index.html"); pm.wait_for_selector("#add")
    check(pm.locator("[data-k=mood] [data-v=Demo]").count() == 0, "phone: no Demo mood")
    if pm.evaluate("!!window.MediaRecorder && !!MIME"):
        pm.set_input_files("#fA", str(T / "song.wav")); pm.set_input_files("#fV", [str(T / f"loop{i}.webm") for i in range(3)])
        pm.wait_for_function("document.querySelector('#add') && !document.querySelector('#add').disabled", timeout=60000)
        pm.click("#add"); pm.wait_for_function("jobs.length >= 1 && ['done','failed','stopped'].includes(jobs[0].status)", timeout=240000)
        j = pm.evaluate("({s: jobs[0].status, err: jobs[0].err || '', size: jobs[0].file ? jobs[0].file.size : 0})")
        check(j["s"] == "done" and j["size"] > 10000, f"phone: a video was made: {j}")
    check(not errs2, f"phone: no script errors {errs2[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
