"""Loop Hospital: AI upscale and AI slow motion (Video2X, stand-in program). Needs ffmpeg + playwright."""
import base64, functools, http.server, json, re, shutil, subprocess, tempfile, threading, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent
T = Path(tempfile.mkdtemp(prefix="spkhai_")); IN, FS = T / "in", T / "fs"; IN.mkdir(); FS.mkdir()
bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
FAKE = T / "video2x"
FAKE.write_text(r'''#!/usr/bin/env python3
import sys, subprocess, time
a = sys.argv[1:]
if a == ["--version"]: print("video2x 6.0.0-standin"); sys.exit(0)
if a == ["--help"]: print("usage: video2x -i IN -o OUT -p {libplacebo,realesrgan,rife}  --device N  --list-devices  -m MUL --rife-model M"); sys.exit(0)
if a == ["--list-devices"]: print("0. Fake GPU (Vulkan)"); sys.exit(0)
open(__file__ + ".log", "a").write(" ".join(a) + chr(10))
OK = {"-i","-o","-p","-s","-c","-e","-d","-m","--rife-model","--realesrgan-model","--libplacebo-shader","-w","-h"}
d = {}
for i in range(0, len(a), 2):
    if a[i] not in OK: print("unknown option", a[i]); sys.exit(2)
    d[a[i]] = a[i+1]
s = int(d.get("-s", 2))
if d.get("-p") == "rife":
    m = int(d["-m"]); fr = subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=r_frame_rate","-of","csv=p=0",d["-i"]],capture_output=True,text=True).stdout.strip().split("/")
    fps = int(fr[0]) / int(fr[1] if len(fr) > 1 else 1)
    for i in range(1, 6): print("Processing frame %d/5" % i, flush=True); time.sleep(0.05)
    r = subprocess.run(["ffmpeg","-v","error","-y","-nostdin","-i",d["-i"],"-vf","fps=%g" % (fps * m),"-c:v","libx264","-pix_fmt","yuv420p",d["-o"]]); sys.exit(r.returncode)
if d.get("-p") == "libplacebo": vf = "scale=%s:%s" % (d["-w"], d["-h"])
else: vf = "scale=iw*%d:ih*%d" % (s, s)
if "SLOW" in d["-i"]:
    for i in range(1, 600): print("Processing frame %d/600" % i, flush=True); time.sleep(0.1)
for i in range(1, 11): print("Processing frame %d/10" % i, flush=True); time.sleep(0.05)
r = subprocess.run(["ffmpeg","-v","error","-y","-nostdin","-i",d["-i"],"-vf",vf,"-c:v","libx264","-pix_fmt","yuv420p",d["-o"]])
sys.exit(r.returncode)
''')
FAKE.chmod(0o755)
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *a], check=True)
ff("-f", "lavfi", "-i", "color=c=black:s=320x180:r=25:d=4,geq=lum='150+80*sin(2*PI*(X/80+T/4))':cb=128:cr=128", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "clip4.mp4"))
def host(op, a=None, b=None):
    if op == "exec":
        r = subprocess.run(["ffmpeg", "-nostdin", *json.loads(a)], cwd=FS, capture_output=True)
        return json.dumps({"code": r.returncode, "log": [l for l in re.split(r"[\r\n]+", r.stderr.decode("utf-8", "replace")) if l]})
    if op == "v2x":
        r = subprocess.run([str(FAKE), *json.loads(a)], cwd=FS, capture_output=True, text=True)
        return json.dumps({"code": r.returncode, "log": [l for l in re.split(r"[\r\n]+", r.stdout + r.stderr) if l]})
    if op == "write": p = FS / a; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(base64.b64decode(b)); return ""
    if op == "read": d = (FS / a).read_bytes(); (T / "last.mp4").write_bytes(d); return base64.b64encode(d).decode()
    if op == "remove": (FS / a).unlink(missing_ok=True); return ""
    if op == "rmdir": shutil.rmtree(FS / a, ignore_errors=True); return ""
    raise ValueError(op)
def engine_js(kind):
    return r"""(() => { const b64 = u8 => { let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); };
  const un64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0)); let n = 0;
  window.__VJ_ENGINE__ = { kind: '%s', info: { v2x: { ok: %s, mul: '-m', rife: true } }, async load() {}, async exec(args) { return JSON.parse(await window.host('exec', JSON.stringify(args))); },
    async v2x(args, o) { const r = JSON.parse(await window.host('v2x', JSON.stringify(args))); if (o && o.onProgress) o.onProgress(1); return r; },
    async write(p, u8) { await window.host('write', p, b64(u8)); }, async read(p) { return un64(await window.host('read', p)); }, async remove(p) { await window.host('remove', p); },
    async mount(file) { const d = 'm' + (++n); await window.host('write', d + '/' + file.name, b64(new Uint8Array(await file.arrayBuffer()))); return d + '/' + file.name; },
    async unmount(p) { await window.host('rmdir', p.split('/')[0]); }, terminate() {} }; })();""" % (kind, "true" if kind == "native" else "false")
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_port}"
def probe(f):
    j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration", "-of", "json", str(f)]))
    return j["streams"][0]["width"], j["streams"][0]["height"], float(j["format"]["duration"])

with sync_playwright() as pw:
    b = pw.chromium.launch()
    def page(kind):
        ctx = b.new_context(viewport={"width": 1000, "height": 900}, service_workers="block")
        ctx.add_init_script("try{localStorage.setItem('spk_desktop','1')}catch(e){}"); ctx.add_init_script(engine_js(kind))
        pg = ctx.new_page(); pg.expose_function("host", host); pg.errs = []; pg.on("pageerror", lambda e: pg.errs.append(str(e)))
        pg.goto(BASE + "/tools/hospital/index.html"); pg.wait_for_selector("#picker", state="attached")
        pg.set_input_files("#picker", str(IN / "clip4.mp4")); pg.wait_for_selector("#findings li", timeout=60000)
        pg.click("[data-tile=slow]"); pg.click("[data-tile=up]"); return pg
    # 1. browser engine: the AI choices are there but switched off
    pg = page("wasm")
    check(pg.locator("[data-s=slow][data-k=engine][value=ai]").is_disabled() and pg.locator("[data-s=up][data-k=engine][value=ai]").is_disabled(), "browser version: AI choices are disabled")
    # 2. local engine: AI slow motion 2x then AI upscale 2x, then the normal pass
    pg = page("native")
    check(not pg.locator("[data-s=slow][data-k=engine][value=ai]").is_disabled(), "local version: AI choices are enabled")
    pg.locator("[data-s=slow][data-k=engine][value=ai]").check(force=True); pg.locator("[data-s=up][data-k=engine][value=ai]").check(force=True)
    pg.locator("[data-s=slow][data-k=factor][value=\"2\"]").check(force=True); pg.locator("[data-s=up][data-k=scale][value=\"2\"]").check(force=True)
    pg.click("#go"); pg.wait_for_selector("#res .rr", timeout=240000)
    w, h, d = probe(T / "last.mp4")
    check(abs(d - 8) < 0.4, f"AI slow motion 2x: 4 s became 8 s ({d})")
    check(w >= 640 and h >= 360, f"AI upscale 2x: the picture is bigger than the 320x180 original ({w}x{h})")
    log = (FS.parent / "video2x.log").read_text() if (FS.parent / "video2x.log").exists() else ""
    flog = "".join(p.read_text() for p in T.glob("video2x.log")) + "".join(p.read_text() for p in FS.glob("*.log"))
    check("-p rife" in flog and "-p realesrgan" in flog, "Video2X was asked for RIFE and Real-ESRGAN")
    check(not list(FS.glob("hosp_*_ai*")), "no temporary AI files are left behind")
    check(not pg.errs, f"no page errors {pg.errs[:2]}")
    # 3. the preview never runs the AI
    n0 = flog.count("\n"); pg.click("#prev"); pg.wait_for_function("document.querySelector('#msg').textContent.includes('Preview done')", timeout=240000)
    flog2 = "".join(p.read_text() for p in T.glob("video2x.log")) + "".join(p.read_text() for p in FS.glob("*.log"))
    check(flog2.count("\n") == n0, "the preview does not start Video2X")
    b.close()
print("ALL OK" if not bad else "FAILED: " + str(bad)); sys.exit(1 if bad else 0)
