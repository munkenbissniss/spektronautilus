"""The fast path (WebCodecs + graphics card) of the Loop Hospital, against the ffmpeg way, recipe by recipe.
The browser here has no H.264, so the tests use VP9 in MP4 both ways in (SPK_WC_TEST); the steps are the same. Each result is compared
with what the ffmpeg way makes from the same clip and recipe: same size, same frame rate, same length (to a frame or two), and a picture
that is close (PSNR). Real ffmpeg (the computer's own) is the ffmpeg engine."""
import base64, functools, http.server, json, os, re, shutil, subprocess, sys, tempfile, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent
T = Path(tempfile.mkdtemp(prefix="spkwc_")); IN, FS = T / "in", T / "fs"; IN.mkdir(); FS.mkdir()
bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *a], check=True)
VP9 = ["-c:v", "libvpx-vp9", "-b:v", "3M", "-deadline", "realtime", "-cpu-used", "8", "-pix_fmt", "yuv420p", "-g", "30"]
ff("-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30:duration=3", *VP9, str(IN / "wide.mp4"))
ff("-f", "lavfi", "-i", "testsrc2=size=360x640:rate=25:duration=2", *VP9, str(IN / "tall.mp4"))
ff("-f", "lavfi", "-i", "testsrc2=size=180x320:rate=25:duration=2", *VP9, str(IN / "tallsmall.mp4"))
ff("-f", "lavfi", "-i", "testsrc2=size=618x348:rate=25:duration=1", *VP9, str(IN / "odd.mp4"))   # a width that is not a multiple of 8
ff("-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30:duration=2", *VP9, str(IN / "_flat.mp4")); ff("-display_rotation", "90", "-i", str(IN / "_flat.mp4"), "-c", "copy", str(IN / "turned.mp4"))
# a moving picture with a "logo" that stays in the bottom right corner (a small, sharp test picture), and the same as a phone clip
ff("-f", "lavfi", "-i", "mandelbrot=size=640x360:rate=30", "-f", "lavfi", "-i", "testsrc=size=120x80:rate=30", "-t", "2", "-filter_complex", "[1:v]trim=end_frame=1,loop=-1:1:0[l];[0:v][l]overlay=500:262:shortest=1", *VP9, str(IN / "logo.mp4"))
ff("-display_rotation", "90", "-i", str(IN / "logo.mp4"), "-c", "copy", str(IN / "turned_logo.mp4"))
# a real moving loop (fast movement), and a short one that does not loop
src = "/mnt/user-data/uploads/matrix-abstract-big-green-135-1920x1080-60.mp4"
if os.path.exists(src): ff("-ss", "2", "-t", "1.5", "-i", src, "-vf", "scale=320:180,fps=30", *VP9, str(IN / "real.mp4"))
else: ff("-f", "lavfi", "-i", "mandelbrot=size=320x180:rate=30", "-t", "1.5", *VP9, str(IN / "real.mp4"))

def probe(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames,codec_name", "-of", "json", str(p)], capture_output=True, text=True).stdout)["streams"][0]
    a, b = map(int, j["r_frame_rate"].split("/")); return {"w": j["width"], "h": j["height"], "fps": a / b, "n": int(j["nb_read_frames"]), "codec": j["codec_name"]}
def psnr(a, b):
    r = subprocess.run(["ffmpeg", "-nostdin", "-i", str(a), "-i", str(b), "-lavfi", "[0:v][1:v]scale2ref=flags=bicubic[x][y];[x][y]psnr", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"average:([\d.]+|inf)", r); return float(m.group(1)) if m and m.group(1) != "inf" else 99.0

def psnr_box(a, b, box):   # the same part (x, y, w, h as parts of the picture) of two clips
    cr = f"crop=iw*{box[2]}:ih*{box[3]}:iw*{box[0]}:ih*{box[1]}"
    r = subprocess.run(["ffmpeg", "-nostdin", "-i", str(a), "-i", str(b), "-lavfi", f"[0:v]{cr}[x];[1:v]{cr}[y];[x][y]psnr", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"average:([\d.]+|inf)", r); return float(m.group(1)) if m and m.group(1) != "inf" else 99.0

def host(op, a=None, b=None):
    if op == "exec":
        r = subprocess.run(["ffmpeg", "-nostdin", *json.loads(a)], cwd=FS, capture_output=True)
        return json.dumps({"code": r.returncode, "log": [l for l in re.split(r"[\r\n]+", r.stderr.decode("utf-8", "replace")) if l]})
    if op == "write": p = FS / a; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(base64.b64decode(b)); return ""
    if op == "read": return base64.b64encode((FS / a).read_bytes()).decode()
    if op == "remove": (FS / a).unlink(missing_ok=True); return ""
    if op == "rmdir": shutil.rmtree(FS / a, ignore_errors=True); return ""
    if op == "save": (T / a).write_bytes(base64.b64decode(b)); return ""
    raise ValueError(op)
ENGINE_JS = r"""(() => { const b64 = u8 => { let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); };
  window.b64 = b64; const un64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0)); let n = 0;
  window.SPK_WC_TEST = { codec: 'vp09.00.40.08' };
  window.__VJ_ENGINE__ = { kind: 'wasm', async load() {}, async exec(args) { return JSON.parse(await window.host('exec', JSON.stringify(args))); },
    async write(p, u8) { await window.host('write', p, b64(u8)); }, async read(p) { return un64(await window.host('read', p)); }, async remove(p) { await window.host('remove', p); },
    async mount(file) { const d = 'm' + (++n); await window.host('write', d + '/' + file.name, b64(new Uint8Array(await file.arrayBuffer()))); return d + '/' + file.name; },
    async unmount(p) { await window.host('rmdir', p.split('/')[0]); }, terminate() {} }; })();"""
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def translate_path(self, p):
        p = p.split("?")[0]
        if p.startswith("/in/"): return str(IN / p[4:])
        return str(ROOT / "docs" / p.lstrip("/"))
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_port}"

# one recipe both ways: returns (fast result info, ffmpeg result info, psnr, note)
RUN = r"""async ([name, patch, tag]) => {
  const WC = await import('/tools/app/wc.js'), ST = await import('/tools/app/steps.js'), L = await import('/tools/app/loops.js'), C = await import('/tools/app/core.js');
  const file = new File([await (await fetch('/in/' + name)).blob()], name, { type: 'video/mp4' });
  const h = await WC.open(file); if (!h) return { error: 'not opened' };
  const R = ST.defaultRecipe(); for (const [k, v] of Object.entries(patch)) R[k] = { ...R[k], ...v };
  const base = { ...C.defaultProfile(), preset: 'veryfast', maxFps: 60 };
  const t0 = performance.now(); let prog = [];
  const r = await WC.run(h, R, base, { onProgress: x => prog.push(x) }); const ms = performance.now() - t0;
  await window.host('save', tag + '_wc.mp4', b64(r.data));
  // the ffmpeg way
  const e = window.__VJ_ENGINE__, path = await e.mount(file), info = await L.probe(e, path, name);
  const t1 = performance.now(); const r2 = await ST.runRecipe(e, L, path, 'out_' + tag + '.mp4', info, R, base, {}); const ms2 = performance.now() - t1;
  await window.host('save', tag + '_ff.mp4', b64(await e.read('out_' + tag + '.mp4')));
  const mono = prog.every((x, i) => !i || x >= prog[i - 1] - 1e-9);
  return { note: r.note, ffnote: r2.note, ms, ms2, prog: [prog.length, prog[prog.length - 1], mono] };
}"""
CASES = [
    ("logo removed", "logo.mp4", {"clean": {"on": True, "boxes": [[0.77, 0.71, 0.21, 0.26]]}}, {"psnr": 30, "box": [0.77, 0.71, 0.21, 0.26]}),
    ("logo removed, phone clip (stored turned)", "turned_logo.mp4", {"clean": {"on": True, "boxes": [[0.7, 0.02, 0.28, 0.21]]}}, {"psnr": 30, "box": [0.7, 0.02, 0.28, 0.21]}),
    ("logo removed + crop + motion frame rate", "logo.mp4", {"clean": {"on": True, "boxes": [[0.77, 0.71, 0.21, 0.26]]}, "crop": {"on": True, "shape": "11"}, "fps": {"on": True, "engine": "blend"}}, {"psnr": 26}),
    ("plain", "wide.mp4", {}, {}),
    ("odd width (rows packed tight)", "odd.mp4", {}, {}),
    ("fps60 motion", "real.mp4", {"fps": {"on": True, "engine": "motion"}}, {"psnr": 24}),
    ("fps60 blend", "wide.mp4", {"fps": {"on": True, "engine": "blend"}}, {"psnr": 24}),
    ("slow2 motion", "real.mp4", {"slow": {"on": True, "factor": 2, "engine": "motion"}}, {"psnr": 24}),
    ("slow smooth", "wide.mp4", {"slow": {"on": True, "factor": 2, "mode": "smooth", "engine": "blend"}}, {}),
    ("turn+crop", "tall.mp4", {"rotate": {"on": True, "turn": "90"}, "crop": {"on": True, "shape": "169"}}, {}),
    ("display matrix", "turned.mp4", {}, {}),
    ("cut", "wide.mp4", {"cut": {"on": True, "start": 0.5, "len": 1.5}}, {}),
    ("size fit letterbox", "tall.mp4", {"size": {"on": True, "box": "1280x720", "fit": "fit", "upscale": True}}, {}),
    ("size fill", "tall.mp4", {"size": {"on": True, "box": "1280x720", "fit": "fill", "upscale": True}}, {}),
    ("upscale sharp", "wide.mp4", {"up": {"on": True, "scale": 2, "sharp": 50}}, {}),
    ("life calm 6 s", "real.mp4", {"life": {"on": True, "minSeconds": 6}}, {"psnr": 22}),
    ("life dream (trails, glow)", "real.mp4", {"life": {"on": True, "style": "dream", "ease": 50, "breathe": 35, "drift": 35, "sway": 20, "glow": 30, "trails": True, "minSeconds": 4}}, {"psnr": 20}),
    ("ken burns", "wide.mp4", {"kb": {"on": True, "mode": "drift", "amount": 60, "minSeconds": 8}}, {"psnr": 22}),
    ("repeat to 10 s", "wide.mp4", {"out": {"minSeconds": 10}}, {}),
    ("loop pingpong", "real.mp4", {"loop": {"on": True, "mode": "pingpong"}}, {"psnr": 22}),
    ("loop crossfade", "real.mp4", {"loop": {"on": True, "mode": "crossfade", "fade": 0.4}}, {"psnr": 22}),
    ("loop auto + 6 s", "wide.mp4", {"loop": {"on": True, "mode": "auto"}, "out": {"minSeconds": 6}}, {}),
    ("smooth out", "real.mp4", {"smooth": {"on": True, "strength": 70}}, {"psnr": 22}),
    ("all at once", "tallsmall.mp4", {"rotate": {"on": True, "turn": "90"}, "crop": {"on": True, "shape": "169"}, "fps": {"on": True, "engine": "motion"}, "life": {"on": True, "minSeconds": 4}, "loop": {"on": True, "mode": "auto"}}, {"psnr": 20}),
]
SYNC = "--sync" in sys.argv          # the plain way of reading pictures back (what Safari and iPhones use), instead of the one that does not wait
only = [a for a in sys.argv[1:] if not a.startswith("--")]
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context().new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(ENGINE_JS); pg.expose_function("host", host)
    if SYNC: pg.add_init_script("window.SPK_WC_TEST.syncRead = true")
    pg.goto(BASE + "/tools/hospital/index.html"); pg.wait_for_selector("#picker", state="attached")
    check(pg.evaluate("import('/tools/app/wc.js').then(m => m.supported())"), "the fast path is available in this browser (VP9 for the test)" + (", reading pictures back the plain way" if SYNC else ""))
    for i, (label, name, patch, opt) in enumerate(CASES):
        if only and not any(o in label for o in only): continue
        tag = f"c{i}"
        try: r = pg.evaluate(RUN, [name, patch, tag])
        except Exception as e: check(False, f"{label}: {str(e)[:300]}"); continue
        if r.get("error"): check(False, f"{label}: {r['error']}"); continue
        a, f = probe(T / f"{tag}_wc.mp4"), probe(T / f"{tag}_ff.mp4")
        same = a["w"] == f["w"] and a["h"] == f["h"] and abs(a["fps"] - f["fps"]) < 0.02 and abs(a["n"] - f["n"]) <= max(2, round(0.02 * f["n"]))
        p = psnr(T / f"{tag}_wc.mp4", T / f"{tag}_ff.mp4")
        check(same, f"{label}: {a['w']}x{a['h']} {a['fps']:.2f} fps {a['n']} frames (ffmpeg way: {f['w']}x{f['h']} {f['fps']:.2f} fps {f['n']} frames), {r['ms']/1000:.1f} s vs {r['ms2']/1000:.1f} s" + ("" if same else f" | fast: {r['note']} | ffmpeg: {r['ffnote']}"))
        check(p >= opt.get("psnr", 28), f"{label}: picture close to the ffmpeg way (PSNR {p:.1f} dB)")
        if opt.get("box"):
            pb = psnr_box(T / f"{tag}_wc.mp4", T / f"{tag}_ff.mp4", opt["box"]); po = psnr_box(T / f"{tag}_wc.mp4", IN / name, opt["box"])
            check(pb >= 26 and po < 22, f"{label}: the box is filled in like the ffmpeg way does it (PSNR {pb:.1f} dB there; against the clip with the logo {po:.1f} dB)")
        check(r["prog"][0] > 0 and r["prog"][1] > 0.97 and r["prog"][2], f"{label}: progress goes up to the end {r['prog']}")
    check(not errs, f"no script errors {errs[:2]}")
    b.close()
print(f"\nresults in {T}")
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
