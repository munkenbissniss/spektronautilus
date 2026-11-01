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
    check("Fake GPU" in req("/api/v2x-gpus")[1].decode(), "GPU list works (the new --list-devices spelling was detected)")
    check(info["v2x"].get("dev") == "-d" and info["v2x"].get("rife") is True, f"capabilities read from --help: {info['v2x']}")
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
        pg.goto(B + "/tools/app/index.html"); pg.wait_for_selector("#groups details"); pg.click("#tabs [data-t=ai]"); pg.select_option("#o_upEngine", "ai")
        pg.set_input_files("#picker", [str(T / "c.mp4")]); pg.wait_for_selector("#files .vt")
        check(pg.locator("#ainote").is_visible() and "Video2X found" in pg.inner_text("#ainote"), "note says Video2X found")
        pg.click("#go"); pg.wait_for_function("VJ.JOBS.length && VJ.JOBS[0].status!=='running' && VJ.JOBS[0].status!=='queued'", timeout=60000)
        j = pg.evaluate("({s: VJ.JOBS[0].status, f: VJ.JOBS[0].failed, n: VJ.JOBS[0].results.map(r=>r.name)})")
        check(j["s"] == "done" and j["f"] == 0 and len(j["n"]) == 1, f"UI job done: {j}"); print("     name:", j["n"])
        pg.fill("#o_aiGpu", "1"); n0 = pg.evaluate("VJ.JOBS.length"); pg.click("#go"); pg.wait_for_function(f"VJ.JOBS.length>{n0} && VJ.JOBS[0].status!=='running' && VJ.JOBS[0].status!=='queued'", timeout=60000); print("     ", pg.evaluate("({s: VJ.JOBS[0].status, l: VJ.JOBS[0].log})"))
        check("-d 1" in (FAKE.parent / "video2x.log").read_text(), "the graphics card is passed with the flag this Video2X understands (-d)")
        for mode, want in (("slow", ("20", "2.0")), ("smooth", ("20", "1.0"))):
            pg.click("#tabs [data-t=slowmo]"); pg.select_option("#o_slowEngine", "ai"); pg.set_input_files("#picker", [str(T / "c.mp4")]); pg.wait_for_selector("#files .vt")
            check(pg.locator("#ainote").is_visible() and "Video2X found" in pg.inner_text("#ainote"), "slow motion shows the Video2X note")
            pg.select_option("#o_slowMode", mode); pg.select_option("#o_slowFactor", "2"); pg.click("#go")
            n = pg.evaluate("VJ.JOBS.length"); pg.wait_for_function(f"VJ.JOBS.length>={n} && VJ.JOBS[0].status!=='running' && VJ.JOBS[0].status!=='queued'", timeout=60000)
            j = pg.evaluate("({s: VJ.JOBS[0].status, f: VJ.JOBS[0].failed, n: VJ.JOBS[0].results.map(r=>r.name)})"); print("     ", mode, j)
            check(j["s"] == "done" and j["f"] == 0 and any(x.endswith(".mp4") for x in j["n"]), f"slow motion job ({mode}) done")
            with pg.expect_download() as dl: pg.click("#jobs .job:first-child [data-a=zip]")
            zz = zipfile.ZipFile(dl.value.path()); nm = [x for x in zz.namelist() if x.endswith(".mp4")][0]; (T / "sm.mp4").write_bytes(zz.read(nm))
            pr = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames,r_frame_rate:format=duration", "-of", "json", str(T / "sm.mp4")], capture_output=True, text=True).stdout
            q = json.loads(pr); fr = q["streams"][0]["nb_read_frames"]; dur = float(q["format"]["duration"]); fps = q["streams"][0]["r_frame_rate"]
            print("      frames", fr, "duration", round(dur, 2), "fps", fps, "name", nm)
            check(fr == want[0] and abs(dur - float(want[1])) < 0.15, f"{mode}: {fr} frames over {dur:.2f} s ({fps})")
        pg.click("#tabs [data-t=ai]"); pg.set_input_files("#picker", [str(T / "c.mp4")]); pg.wait_for_selector("#files .vt")
        pg.click("#aigpu"); pg.wait_for_function("document.querySelector('#aigpus').textContent.includes('Fake GPU')", timeout=10000); check(True, "Check my graphics card shows GPUs")
        check(not errs, "no page errors " + "; ".join(errs[:2])); br.close()
        # wasm mode: plain static server, no local engine
        sv = subprocess.Popen([sys.executable, "-m", "http.server", "8794", "--directory", str(ROOT / "docs")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
        try:
            br = pw.chromium.launch(); pg = br.new_page(); pg.goto("http://127.0.0.1:8794/tools/app/index.html"); pg.wait_for_selector("#groups details"); pg.click("#tabs [data-t=ai]"); pg.select_option("#o_upEngine", "ai")
            pg.set_input_files("#picker", [str(T / "c.mp4")]); pg.wait_for_selector("#files .vt"); pg.wait_for_timeout(800)
            check(pg.locator("#ainote").is_visible() and "Linux" in pg.inner_text("#ainote"), "web version explains it needs Linux: " + pg.inner_text("#ainote")[:60]); br.close()
        finally: sv.terminate()
finally: srv.terminate()
print("\nALL OK" if not bad else "\nFAILED: " + "; ".join(bad)); raise SystemExit(1 if bad else 0)
