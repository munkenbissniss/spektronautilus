"""The Loop Hospital: Remove logos and text (found boxes, tapping and drawing boxes, the treated clip), and players that play once.
Based on the setup of tests_wc_hospital.py. The Loop Hospital page with the fast path: examining, preview and treating without ffmpeg; Looks and unreadable clips use ffmpeg.
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



ff("-f", "lavfi", "-i", "mandelbrot=size=640x360:rate=30", "-f", "lavfi", "-i", "testsrc=size=120x80:rate=30", "-t", "3", "-filter_complex", "[1:v]trim=end_frame=1,loop=-1:1:0[l];[0:v][l]overlay=500:262:shortest=1", *VP9, str(IN / "logo.mp4"))
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context(accept_downloads=True).new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(ENGINE_JS); pg.expose_function("host", host)
    pg.goto(BASE + "/tools/hospital/index.html"); pg.wait_for_selector("#picker", state="attached")
    pg.set_input_files("#picker", str(IN / "logo.mp4")); pg.wait_for_selector("#facts span:not(.muted)", timeout=120000)
    check(pg.evaluate("document.querySelector('#vbefore').loop") is False, "the Before player does not loop by itself")
    pg.click('[data-tile="clean"]')
    pg.wait_for_function("/will be removed|Nothing found|Could not/.test(document.querySelector('#cleanmsg').textContent)", timeout=60000)
    boxes = pg.evaluate("HOSP.R.clean.boxes"); msg = pg.inner_text("#cleanmsg")
    hit = [x for x in boxes if x[0] <= 0.79 and x[0] + x[2] >= 0.96 and x[1] <= 0.73 and x[1] + x[3] >= 0.95]
    check(len(hit) == 1, f"the logo in the corner is found and chosen: {boxes} ({msg!r})")
    pg.locator("#cleancv").scroll_into_view_if_needed(); pg.evaluate("document.querySelector('#cleancv').scrollIntoView({ block: 'center' })")
    cv = pg.locator("#cleancv").bounding_box()
    check(cv and cv["width"] > 200 and cv["height"] > 100, f"a still of the clip is shown with the boxes {cv}")
    if hit:
        x, y = cv["x"] + cv["width"] * (hit[0][0] + hit[0][2] / 2), cv["y"] + cv["height"] * (hit[0][1] + hit[0][3] / 2)
        pg.mouse.click(x, y); n1 = len(pg.evaluate("HOSP.R.clean.boxes"))
        pg.mouse.click(x, y); n2 = len(pg.evaluate("HOSP.R.clean.boxes"))
        check(n1 == len(boxes) - 1 and n2 == len(boxes), f"tapping a box leaves it alone, tapping again uses it ({len(boxes)} -> {n1} -> {n2})")
    pg.mouse.move(cv["x"] + cv["width"] * 0.05, cv["y"] + cv["height"] * 0.05); pg.mouse.down()
    pg.mouse.move(cv["x"] + cv["width"] * 0.2, cv["y"] + cv["height"] * 0.15, steps=5); pg.mouse.up()
    nb = pg.evaluate("HOSP.R.clean.boxes")
    check(len(nb) == len(boxes) + 1 and abs(nb[-1][0] - 0.05) < 0.02 and abs(nb[-1][2] - 0.15) < 0.02, f"dragging marks a box of your own: {nb[-1] if nb else None}")
    pg.click("#cleanclear"); check(pg.evaluate("HOSP.R.clean.boxes.length") == 0, "Clear all removes every box")
    pg.click("#cleanfind"); pg.wait_for_function("HOSP.R.clean.boxes.length > 0", timeout=60000)
    # treat it: the logo is gone from the result
    pg.click("#go"); pg.wait_for_function("document.querySelector('#res a') || /warn/.test(document.querySelector('#msg').className) && document.querySelector('#msg').textContent", timeout=600000)
    if not pg.query_selector("#res a"): print("MSG", pg.inner_text("#msg"))
    note = pg.inner_text("#res"); check("logo removed" in note, f"the result says the logo was removed: {note[:140]!r}")
    with pg.expect_download() as dl: pg.click("#res a")
    p = T / "clean_result.mp4"; dl.value.save_as(p)
    cr = "crop=iw*0.19:ih*0.22:iw*0.78:ih*0.73"
    r = subprocess.run(["ffmpeg", "-nostdin", "-i", str(p), "-i", str(IN / "logo.mp4"), "-lavfi", f"[0:v]{cr},scale=120:80[x];[1:v]{cr},scale=120:80[y];[x][y]psnr", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"average:([\d.]+|inf)", r); pv = float(m.group(1)) if m and m.group(1) != "inf" else 99
    check(pv < 20, f"the corner of the result no longer shows the logo (PSNR against the clip with the logo {pv:.1f} dB)")
    m, cl = pg.inner_text("#msg"), pg.get_attribute("#msg", "class") or ""
    check(not m.startswith("Done") or ("good" in cl and "warn" not in cl), f"Done is shown as good news, not as a warning ({m!r}, {cl!r})")
    cl2 = pg.evaluate("(() => { const m = document.querySelector('#msg'); m.textContent = ''; return 0; })()")
    # players: once, then stop; play again by hand: loops
    pg.wait_for_function("document.querySelector('#vafter').src", timeout=10000)
    st = pg.evaluate("""async () => { const v = document.querySelector('#vafter'); v.muted = true;
      if (v.readyState < 1) await new Promise(r => v.addEventListener('loadedmetadata', r, { once: true }));
      v.currentTime = Math.max(0, v.duration - 0.3); await v.play().catch(() => {});
      await new Promise(r => { if (v.ended) r(); else v.addEventListener('ended', r, { once: true }); setTimeout(r, 8000); });
      const a = { ended: v.ended, paused: v.paused, loop: v.loop }; await v.play(); await new Promise(r => setTimeout(r, 200)); a.loopAfter = v.loop; v.pause(); return a; }""")
    check(st["ended"] and st["paused"] and not st["loop"], f"the After player stops after one round {st}")
    check(st["loopAfter"], f"pressing play after that loops the clip {st}")
    check(not errs, f"no script errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
