"""Tests of the Linux version (linux/spektronautilus.py): the local server, its safety rules, and the tools app running on the
real ffmpeg through it (no bridge, no mock). Needs ffmpeg + playwright."""
import json, subprocess, sys, tempfile, time, urllib.request, urllib.error, zipfile, io, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent; T = Path(tempfile.mkdtemp(prefix="spklin_")); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
srv = subprocess.Popen([sys.executable, str(ROOT / "linux/spektronautilus.py"), "--no-browser", "--port", "8791", "--docs", str(ROOT / "docs")], stdout=subprocess.PIPE, text=True)
try:
    line = srv.stdout.readline(); check("8791" in line, "server starts: " + line.strip())
    srv.stdout.readline()
    B = "http://127.0.0.1:8791"
    def req(path, method="GET", data=None, headers=None, host=None):
        h = {"X-Spk": "1", **(headers or {})}
        if host: h["Host"] = host
        r = urllib.request.Request(B + path, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(r, timeout=60) as x: return x.status, x.read()
        except urllib.error.HTTPError as e: return e.code, e.read()
    s, b = req("/api/native"); info = json.loads(b); check(s == 200 and info["ok"] and info["cores"] >= 1, f"native engine reported {info.get('version')}")
    check(req("/")[0] == 200 and req("/tools/app/index.html")[0] == 200 and req("/live-dj/")[0] == 200, "the website is served")
    check(req("/api/native", headers={"X-Spk": "0"})[0] == 403, "API without the header is refused")
    check(req("/api/native", host="evil.example:8791")[0] == 403 and req("/", host="evil.example")[0] == 403, "wrong Host header (DNS rebinding) is refused")
    check(req("/api/fs/../../etc/passwd")[0] in (400, 403, 404) and req("/api/fs/%2e%2e/%2e%2e/etc/passwd")[0] == 400, "path traversal is refused")
    check(req("/api/exec", "POST", json.dumps(["-i", "/etc/passwd", "o.mp4"]).encode())[0] == 400, "absolute paths in ffmpeg arguments are refused")
    check(req("/api/exec", "POST", json.dumps(["-i", "file:/etc/passwd", "o.mp4"]).encode())[0] == 400, "file: urls are refused")
    check(req("/api/exec", "POST", json.dumps(["-f", "lavfi", "-i", "movie=/etc/passwd", "o.mp4"]).encode())[0] == 400, "movie= with a path is refused")
    # file round trip + exec with progress
    s, _ = req("/api/fs/a/in.bin", "PUT", b"x" * 3_000_000); check(s == 200, "upload 3 MB")
    s, b = req("/api/fs/a/in.bin"); check(s == 200 and len(b) == 3_000_000, "download it again")
    req("/api/fs/a", "DELETE"); check(req("/api/fs/a/in.bin")[0] == 404, "delete a folder")
    args = ["-y", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=25:duration=3", "-c:v", "libx264", "-pix_fmt", "yuv420p", "t/out.mp4"]
    r = urllib.request.Request(B + "/api/exec", data=json.dumps(args).encode(), method="POST", headers={"X-Spk": "1"}); lines = []
    with urllib.request.urlopen(r, timeout=60) as x:
        for l in x: lines.append(json.loads(l))
    # the file must be written into a folder that exists
    check(lines and lines[-1].get("code") != 0, "ffmpeg errors come back with a log (missing folder)")
    req("/api/fs/t/x", "PUT", b"1"); lines = []
    with urllib.request.urlopen(urllib.request.Request(B + "/api/exec", data=json.dumps(args).encode(), method="POST", headers={"X-Spk": "1"}), timeout=60) as x:
        for l in x: lines.append(json.loads(l))
    check(lines[-1]["code"] == 0 and any("Stream #0" in l for l in lines[-1]["log"]), "exec runs ffmpeg and returns the log")
    s, b = req("/api/fs/t/out.mp4"); (T / "o.mp4").write_bytes(b)
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width", "-of", "csv=p=0", str(T / "o.mp4")], capture_output=True, text=True).stdout
    check("h264,320" in pr, "output is valid H.264 " + pr.strip())
    # kill
    import threading
    out = []
    def long():
        a2 = ["-y", "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=30:duration=600", "-c:v", "libx264", "-preset", "veryslow", "t/long.mp4"]
        try:
            with urllib.request.urlopen(urllib.request.Request(B + "/api/exec", data=json.dumps(a2).encode(), method="POST", headers={"X-Spk": "1"}), timeout=60) as x:
                for l in x: out.append(json.loads(l))
        except Exception as e: out.append({"err": str(e)})
    th = threading.Thread(target=long); th.start(); time.sleep(2.5); t0 = time.time(); req("/api/kill", "POST"); th.join(20)
    check(not th.is_alive() and time.time() - t0 < 10, "Stop kills a running ffmpeg quickly")
    time.sleep(1); check(subprocess.run(["pgrep", "-x", "ffmpeg"], capture_output=True).returncode != 0, "no ffmpeg left running")

    # ---------------- the real tools app on top of the local server
    from playwright.sync_api import sync_playwright
    IN = T / "in"; IN.mkdir()
    def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *a], check=True)
    ff("-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=30:duration=3", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "Mitt Klipp.mov"))
    ff("-f", "lavfi", "-i", "testsrc2=size=200x120:rate=10:duration=2", "-vf", "format=pal8", str(IN / "gif one.gif"))
    ff("-f", "lavfi", "-i", "testsrc2=size=1920x1080:rate=30:duration=120", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(T / "big.mov"))
    with sync_playwright() as pw:
        b = pw.chromium.launch(); ctx = b.new_context(accept_downloads=True, viewport={"width": 1200, "height": 900}); pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(B + "/tools/app/index.html"); pg.wait_for_selector("#groups details")
        pg.set_input_files("#picker", [str(f) for f in sorted(IN.iterdir())]); pg.wait_for_selector("#files .vt")
        check(pg.input_value("#o_preset") == "fast", "fast mode picks a better default preset")
        pg.fill("#o_template", "vj_{n3}_{name}"); pg.select_option("#o_preset", "ultrafast"); pg.click("#go")
        pg.wait_for_function("VJ.JOBS.length && VJ.JOBS[0].status!=='running' && VJ.JOBS[0].status!=='queued'", timeout=90000)
        j = pg.evaluate("({s: VJ.JOBS[0].status, f: VJ.JOBS[0].failed, n: VJ.JOBS[0].results.map(r=>r.name)})")
        check(j["s"] == "done" and j["f"] == 0 and len(j["n"]) == 2, f"convert on the real ffmpeg: {j}")
        check("Fast mode" in pg.inner_text("#ekind"), "the page says it is in fast mode: " + pg.inner_text("#ekind"))
        with pg.expect_download() as d: pg.click("#jobs [data-a=zip]")
        z = zipfile.ZipFile(d.value.path()); names = z.namelist(); check(z.testzip() is None and len(names) == 2, f"zip {names}")
        for n in names:
            (T / n).write_bytes(z.read(n)); pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name,pix_fmt,width", "-of", "csv=p=0", str(T / n)], capture_output=True, text=True).stdout.strip()
            check(pr.startswith("h264,") and "yuv420p" in pr, f"{n}: {pr}")
        # filters through the same path
        pg.click("#tabs [data-t=filters]"); pg.set_input_files("#picker", [str(IN / "Mitt Klipp.mov")]); pg.wait_for_selector("#files .vt")
        pg.wait_for_selector("#fgrid .ft"); pg.click("#fgrid .ft:nth-child(1)"); pg.click("#fgrid .ft:nth-child(3)"); pg.select_option("#o_preset", "ultrafast"); pg.click("#go")
        pg.wait_for_function("VJ.JOBS.length>1 && VJ.JOBS[0].status!=='running' && VJ.JOBS[0].status!=='queued'", timeout=120000)
        j = pg.evaluate("({s: VJ.JOBS[0].status, f: VJ.JOBS[0].failed, n: VJ.JOBS[0].results.length})"); check(j == {"s": "done", "f": 0, "n": 2}, f"filters on the real ffmpeg {j}")
        # HAP / ProRes need the real ffmpeg: this is the only place they can run
        pg.click("#tabs [data-t=pro]"); pg.set_input_files("#picker", [str(IN / "Mitt Klipp.mov")]); pg.wait_for_selector("#files .vt"); check(not pg.locator("#pronote").is_visible(), "HAP / ProRes: no warning with the local engine")
        pg.select_option("#o_proFormat", "hapq"); pg.click("#go"); pg.wait_for_function("VJ.JOBS.length>2 && VJ.JOBS[0].status!=='running' && VJ.JOBS[0].status!=='queued'", timeout=120000)
        j = pg.evaluate("({s: VJ.JOBS[0].status, f: VJ.JOBS[0].failed, n: VJ.JOBS[0].results.map(r=>r.name)})"); check(j["s"] == "done" and j["n"] == ["vj_001_Mitt_Klipp.mov"], f"HAP Q on the real ffmpeg: {j}")
        pg.wait_for_selector("#jobs .job:first-child .res a:has-text('.mov')")
        with pg.expect_download() as d2: pg.click("#jobs .job:first-child [data-a=zip]")
        zz = zipfile.ZipFile(d2.value.path()); (T / "hq.mov").write_bytes(zz.read(zz.namelist()[0]))
        pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name,width,height", "-of", "csv=p=0", str(T / "hq.mov")], capture_output=True, text=True).stdout.strip()
        check(pr.startswith("hap,1280,720"), "HAP Q file is valid: " + pr)
        # stop
        pg.click("#tabs [data-t=convert]"); pg.set_input_files("#picker", [str(T / "big.mov")]); pg.wait_for_selector("#files .vt"); pg.select_option("#o_preset", "medium")
        pg.click("#go"); pg.wait_for_function("VJ.JOBS[0].status==='running'", timeout=20000); pg.wait_for_timeout(1500); pg.click("#jobs [data-a=cancel]")
        pg.wait_for_function("VJ.JOBS[0].status==='cancelled'", timeout=15000); check(True, "Stop works against the local engine")
        time.sleep(1); check(subprocess.run(["pgrep", "-x", "ffmpeg"], capture_output=True).returncode != 0, "and ffmpeg is gone")
        check(not errs, "no page errors " + "; ".join(errs[:2])); b.close()
finally:
    srv.terminate()
    try: srv.wait(10)
    except Exception: srv.kill()
print("\nALL OK" if not bad else "\nFAILED: " + "; ".join(bad)); raise SystemExit(1 if bad else 0)
