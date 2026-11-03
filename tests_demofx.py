"""Demoscene-style effects of the Magic Mixer: every effect changes the picture, all at 0 changes nothing, and a real job renders with them (desktop and phone)."""
import functools, http.server, subprocess, tempfile, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent
T = Path(tempfile.mkdtemp(prefix="spkdemo_")); bad = []
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
UNIT = """() => { const W = 320, H = 180, cv = document.createElement('canvas'); cv.width = W; cv.height = H; const g = cv.getContext('2d', { alpha: false }), res = {};
  const base = () => { g.fillStyle = '#203050'; g.fillRect(0, 0, W, H); g.fillStyle = '#e8d9b0'; g.beginPath(); g.arc(160, 90, 40, 0, 7); g.fill(); g.fillStyle = '#000'; g.fillRect(20, 120, 280, 20); };
  const sum = () => { const d = g.getImageData(0, 0, W, H).data; let s = 0; for (let i = 0; i < d.length; i += 4) s = (s * 31 + d[i] + d[i + 1] * 3 + d[i + 2] * 7) % 1000003; return s; };
  base(); const ref = sum(); res.ref = ref;
  const run = (o) => { const fx = SPKDemo.create(W, H, 3); base(); for (let f = 0; f < 6; f++) { base(); fx.apply(g, cv, { dVar: 0, dText: '', dTextSpeed: 8, ...o }, { m: 2 + f / 25, kk: 1, hue: 120, ci: 0, pci: 0, fx: 1, cut: 1 }); } return sum(); };
  res.none = run({}); for (const k of SPKDemo.NAMES) res[k] = run(k === 'dText' ? { dText: 'GREETZ' } : { [k]: 1 });
  res.off = run({ dPlasma: 0, dBars: 0, dStars: 0, dScan: 0 });
  // 'change per section': with variation 1 some section masks are off, so the picture differs between sections
  res.secA = run({ dBars: 1, dVar: 1, dPlasma: 1 }); return res; }"""
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    pg = b.new_context().new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/mixer/index.html?desktop=1"); pg.wait_for_selector("#add")
    r = pg.evaluate(UNIT)
    check(r["none"] == r["ref"] and r["off"] == r["ref"], "all effects at 0: the picture is untouched")
    for k in ("dPlasma", "dBars", "dFeedback", "dWobble", "dMosaic", "dChroma", "dStars", "dScan", "dText", "dBloom", "dGrain", "dFlash", "dBox"):
        check(r[k] != r["ref"], f"{k} changes the picture")

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
    check("Demo" in pg.inner_text("#pre"), "the Demo mood exists")
    pg.click("#pre [data-p=Demo]")
    v = pg.evaluate("({h: +document.querySelector('#o_hardCuts').value, r: +document.querySelector('#o_rush').value, c: document.querySelector('#o_cutStart').checked, t: document.querySelector('#o_tempoLock').checked, pl: +document.querySelector('#o_dPlasma').value, s: +document.querySelector('#o_shotBars').value})")
    check(v["h"] > 0 and v["r"] > 0 and v["c"] and v["t"] and v["s"] == 2, f"the Demo mood turns on the beat cutting: {v}")
    check(v["pl"] == 0, "the Demo mood does not add overlay effects")
    pg.click("#pre [data-p=Chill]")
    check(pg.evaluate("+document.querySelector('#o_hardCuts').value") == 0 and not pg.evaluate("document.querySelector('#o_cutStart').checked"), "another mood switches the beat cutting off again")
    pg.click("#pre [data-p=Demo]")
    pg.evaluate("setO('res', '1280x720'); setO('dText', 'MAGIC MIXER GREETZ')")
    pg.set_input_files("#fA", str(T / "song.wav")); pg.set_input_files("#fV", [str(T / f"loop{i}.webm") for i in range(3)])
    pg.wait_for_function("document.querySelector('#add') && !document.querySelector('#add').disabled", timeout=60000)
    pg.click("#add"); pg.wait_for_function("jobs.length >= 1 && ['done','failed','stopped'].includes(jobs[0].status)", timeout=240000)
    j = pg.evaluate("({s: jobs[0].status, err: jobs[0].err || '', size: jobs[0].file ? jobs[0].file.size : 0})")
    check(j["s"] == "done" and j["size"] > 20000, f"desktop: a video with demo effects was made: {j}")
    check(not errs, f"no script errors {errs[:2]}")
    # phone version
    pm = b.new_context(viewport={"width": 400, "height": 800}).new_page(); errs2 = []; pm.on("pageerror", lambda e: errs2.append(str(e)))
    pm.goto(BASE + "/mixer-mobile/index.html"); pm.wait_for_selector("#add")
    if pm.evaluate("!!window.MediaRecorder && !!MIME"):
        pm.set_input_files("#fA", str(T / "song.wav")); pm.set_input_files("#fV", [str(T / f"loop{i}.webm") for i in range(3)])
        pm.wait_for_function("document.querySelector('#add') && !document.querySelector('#add').disabled", timeout=60000)
        pm.click("[data-k=mood] [data-v=Demo]"); check(pm.evaluate("opts().hardCuts") > 0 and pm.evaluate("opts().rush") > 0, "phone: the Demo mood turns on the beat cutting")
        pm.click("#add"); pm.wait_for_function("jobs.length >= 1 && ['done','failed','stopped'].includes(jobs[0].status)", timeout=240000)
        j = pm.evaluate("({s: jobs[0].status, err: jobs[0].err || '', size: jobs[0].file ? jobs[0].file.size : 0})")
        check(j["s"] == "done" and j["size"] > 10000, f"phone: a video with demo effects was made: {j}")
    check(not errs2, f"phone: no script errors {errs2[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
