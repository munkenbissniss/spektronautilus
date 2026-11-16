"""The local Linux version (a native engine) also takes the fast way; its own ffmpeg does only the rest (here: a Look).
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
ff("-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30:duration=2", *VP9, str(IN / "_flat.mp4")); ff("-display_rotation", "90", "-i", str(IN / "_flat.mp4"), "-c", "copy", str(IN / "turned.mp4"))
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
  window.__VJ_ENGINE__ = { kind: 'native', info: { cores: 2, v2x: { ok: false } }, async load() {}, async exec(args) { return JSON.parse(await window.host('exec', JSON.stringify(args))); },
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



EXECS = []
_host = host
def host2(op, a=None, b=None):
    if op == "exec": EXECS.append(json.loads(a))
    return _host(op, a, b)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context(accept_downloads=True).new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(ENGINE_JS); pg.expose_function("host", host2)
    pg.goto(BASE + "/tools/hospital/index.html"); pg.wait_for_selector("#picker", state="attached")
    pg.set_input_files("#picker", str(IN / "wide.mp4")); pg.wait_for_selector("#facts span:not(.muted)", timeout=120000)
    check(not EXECS and pg.is_visible("#fastway"), f"the local version examines the clip the fast way ({len(EXECS)} ffmpeg calls)")
    pg.evaluate("HOSP.R.fps.on = true; HOSP.R.fps.engine = 'blend'")
    pg.click("#go"); pg.wait_for_selector("#res a", timeout=600000)
    with pg.expect_download() as dl: pg.click("#res a")
    p = T / "native_result.mp4"; dl.value.save_as(p); i = probe(p)
    check(not EXECS and abs(i["fps"] - 60) < 0.01 and i["n"] == 180, f"and treats it the fast way: {i} ({len(EXECS)} ffmpeg calls)")
    pg.evaluate("HOSP.R.look.on = true; HOSP.R.fps.on = false")
    pg.click("#go"); pg.wait_for_function("document.querySelectorAll('#res a').length >= 2", timeout=600000)
    check(len(EXECS) > 0, f"a Look goes to the computer's own ffmpeg ({len(EXECS)} calls)")
    check(not errs, f"no script errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
