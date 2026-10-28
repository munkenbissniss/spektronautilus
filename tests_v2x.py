"""Video2X integration, tested with a stand-in program (the real Video2X needs a Vulkan GPU). Needs ffmpeg + playwright."""
import json, os, subprocess, sys, tempfile, time, urllib.request, urllib.error, zipfile, threading
from pathlib import Path
ROOT = Path(__file__).resolve().parent; T = Path(tempfile.mkdtemp(prefix="spkv2x_")); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
FAKE = T / "video2x"
FAKE.write_text('''#!/usr/bin/env python3
import sys, subprocess, time
a = sys.argv[1:]
if a == ["--version"]: print("video2x 6.0.0-standin"); sys.exit(0)
if a == ["--list-gpus"]: print("0. Fake GPU (Vulkan)"); sys.exit(0)
OK = {"-i","-o","-p","-s","-c","-e","-g","--realesrgan-model","--libplacebo-shader","-w","-h"}
d = {}
for i in range(0, len(a), 2):
    if a[i] not in OK: print("unknown option", a[i]); sys.exit(2)
    d[a[i]] = a[i+1]
s = int(d.get("-s", 2))
if d.get("-p") == "libplacebo": vf = "scale=%s:%s" % (d["-w"], d["-h"])
else: vf = "scale=iw*%d:ih*%d" % (s, s)
if "SLOW" in d["-i"]:
    for i in range(1, 600): print("Processing frame %d/600" % i, flush=True); time.sleep(0.1)
for i in range(1, 11): print("Processing frame %d/10" % i, flush=True); time.sleep(0.05)
r = subprocess.run(["ffmpeg","-v","error","-y","-nostdin","-i",d["-i"],"-vf",vf,"-c:v","libx264","-pix_fmt","yuv420p",d["-o"]])
sys.exit(r.returncode)
''')
FAKE.chmod(0o755)
def start(port, env):
    p = subprocess.Popen([sys.executable, str(ROOT / "linux/spektronautilus.py"), "--no-browser", "--port", str(port), "--docs", str(ROOT / "docs")], stdout=subprocess.PIPE, text=True, env={**os.environ, **env})
    p.stdout.readline(); p.stdout.readline(); return p
def mk(B):
    def req(path, method="GET", data=None):
        r = urllib.request.Request(B + path, data=data, method=method, headers={"X-Spk": "1"})
        try:
            with urllib.request.urlopen(r, timeout=60) as x: return x.status, x.read()
        except urllib.error.HTTPError as e: return e.code, e.read()
    return req
def run(B, args):
    out = []
    with urllib.request.urlopen(urllib.request.Request(B + "/api/v2x-exec", data=json.dumps(args).encode(), method="POST", headers={"X-Spk": "1"}), timeout=60) as x:
        for l in x: out.append(json.loads(l))
    return out
# 1. no Video2X
srv0 = start(8792, {"SPEKTRO_VIDEO2X": str(T / "nope"), "PATH": "/usr/bin:/bin", "HOME": str(T)})
try:
    r0 = mk("http://127.0.0.1:8792"); info = json.loads(r0("/api/native")[1])
    check(info["v2x"]["ok"] is False, "no Video2X: reported as missing")
    check(r0("/api/v2x-exec", "POST", json.dumps(["-i", "a.mp4", "-o", "b.mp4"]).encode())[0] == 503, "no Video2X: exec gives 503")
finally: srv0.terminate()
srv = start(8793, {"SPEKTRO_VIDEO2X": str(FAKE)}); B = "http://127.0.0.1:8793"; req = mk(B)
try:
    info = json.loads(req("/api/native")[1]); check(info["v2x"]["ok"] and "standin" in info["v2x"]["version"], f"Video2X found: {info['v2x']}")
    check("Fake GPU" in req("/api/v2x-gpus")[1].decode(), "GPU list works")
    for bad_args, why in [(["-i", "a.mp4", "-o", "b.mp4", "--evil", "x"], "unknown flag"), (["-i", "/etc/passwd", "-o", "b.mp4"], "absolute path"), (["-i", "../a.mp4", "-o", "b.mp4"], ".. path"),
                          (["-i", "a.mp4", "-o", "b.mp4", "--libplacebo-shader", "/etc/x"], "path as shader"), (["-i", "a.mp4"], "no output"), (["-i", "a.mp4", "-o", "b.mp4", "-s", "9"], "scale 9")]:
        check(req("/api/v2x-exec", "POST", json.dumps(bad_args).encode())[0] == 400, f"rejected: {why}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=10:duration=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(T / "c.mp4")], check=True)
    req("/api/fs/w/c.mp4", "PUT", (T / "c.mp4").read_bytes())
    o = run(B, ["-i", "w/c.mp4", "-o", "w/o.mp4", "-p", "realesrgan", "--realesrgan-model", "realesr-animevideov3", "-s", "2", "-c", "libx264", "-e", "crf=17"])
    check(o[-1]["code"] == 0 and any("p" in x for x in o[:-1]), "progress streamed, exit 0")
    (T / "o.mp4").write_bytes(req("/api/fs/w/o.mp4")[1])
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(T / "o.mp4")], capture_output=True, text=True).stdout.strip()
    check(pr == "640,360", "output doubled: " + pr)
    # kill
    req("/api/fs/w/SLOW.mp4", "PUT", (T / "c.mp4").read_bytes()); res = []
    th = threading.Thread(target=lambda: res.append(run(B, ["-i", "w/SLOW.mp4", "-o", "w/s.mp4"]))); th.start(); time.sleep(1.5); t0 = time.time(); req("/api/kill", "POST"); th.join(15)
    check(not th.is_alive() and time.time() - t0 < 10, "Stop kills Video2X")
    # UI
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch(); pg = br.new_page(viewport={"width": 1200, "height": 900}); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(B + "/tools/app/index.html"); pg.wait_for_selector("#groups details"); pg.click("#tabs [data-t=ai]")
        pg.set_input_files("#picker", [str(T / "c.mp4")]); pg.wait_for_selector("#files .vt")
        check(pg.locator("#ainote").is_visible() and "Video2X found" in pg.inner_text("#ainote"), "note says Video2X found")
        pg.click("#go"); pg.wait_for_function("VJ.JOBS.length && VJ.JOBS[0].status!=='running' && VJ.JOBS[0].status!=='queued'", timeout=60000)
        j = pg.evaluate("({s: VJ.JOBS[0].status, f: VJ.JOBS[0].failed, n: VJ.JOBS[0].results.map(r=>r.name)})")
        check(j["s"] == "done" and j["f"] == 0 and len(j["n"]) == 1, f"UI job done: {j}"); print("     name:", j["n"])
        pg.click("#aigpu"); pg.wait_for_function("document.querySelector('#aigpus').textContent.includes('Fake GPU')", timeout=10000); check(True, "Check my graphics card shows GPUs")
        check(not errs, "no page errors " + "; ".join(errs[:2])); br.close()
        # wasm mode: plain static server, no local engine
        sv = subprocess.Popen([sys.executable, "-m", "http.server", "8794", "--directory", str(ROOT / "docs")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
        try:
            br = pw.chromium.launch(); pg = br.new_page(); pg.goto("http://127.0.0.1:8794/tools/app/index.html"); pg.wait_for_selector("#groups details"); pg.click("#tabs [data-t=ai]")
            pg.set_input_files("#picker", [str(T / "c.mp4")]); pg.wait_for_selector("#files .vt"); pg.wait_for_timeout(800)
            check(pg.locator("#ainote").is_visible() and "Linux" in pg.inner_text("#ainote"), "web version explains it needs Linux: " + pg.inner_text("#ainote")[:60]); br.close()
        finally: sv.terminate()
finally: srv.terminate()
print("\nALL OK" if not bad else "\nFAILED: " + "; ".join(bad)); raise SystemExit(1 if bad else 0)
