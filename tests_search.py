"""Find loops: short clips, no government footage, loops and GIFs first, GIF sources. Uses a fake archive.org / Commons on localhost
(real ffmpeg through the Linux server, so the downloaded GIF is really converted to mp4). Needs ffmpeg + playwright."""
import json, subprocess, sys, tempfile, threading, time, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
ROOT = Path(__file__).resolve().parent; T = Path(tempfile.mkdtemp(prefix="spksearch_")); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=10:duration=2", "-pix_fmt", "yuv420p", str(T / "a.mp4")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=101x61:rate=10:duration=1", "-vf", "format=pal8", str(T / "a.gif")], check=True)
MV = {   # id: (title, creator, runtime, length of the file, has file)
  "army1": ("Army training film", "U.S. Army Signal Corps", "", 20, True), "neon": ("Neon city loop", "Someone", "00:00:10", 10, True),
  "long": ("Long documentary about a city", "Someone", "", 1800, True), "dance": ("Vintage dancing 1950", "Prelinger", "", 25, True), "nofile": ("City without a video", "X", "", 0, False)}
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, body, ct="application/json"):
        self.send_response(200); self.send_header("Content-Type", ct); self.send_header("Access-Control-Allow-Origin", "*"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        if u.path == "/advancedsearch.php":
            qq = q["q"][0]
            if "Animated GIF" in qq: docs = [{"identifier": "spin", "title": "Spinning thing", "creator": "Gifmaker", "licenseurl": "https://creativecommons.org/publicdomain/zero/1.0/"}]
            else: docs = [{"identifier": k, "title": v[0], "creator": v[1], "runtime": v[2], "licenseurl": "https://creativecommons.org/publicdomain/zero/1.0/"} for k, v in MV.items()]
            return self.send(json.dumps({"response": {"docs": docs}}).encode())
        if u.path.startswith("/metadata/"):
            i = u.path.split("/")[-1]
            if i == "spin": return self.send(json.dumps({"files": [{"name": "spin.gif", "source": "original", "size": "1000"}], "metadata": {}}).encode())
            t, c, rt, ln, has = MV[i]
            return self.send(json.dumps({"files": [{"name": i + ".mp4", "source": "derivative", "size": "100", "length": str(ln)}] if has else [{"name": "x.txt", "source": "original"}], "metadata": {"licenseurl": "https://creativecommons.org/publicdomain/zero/1.0/"}}).encode())
        if u.path.startswith("/download/"):
            f = u.path.split("/")[-1]; return self.send((T / ("a.gif" if f.endswith(".gif") else "a.mp4")).read_bytes(), "image/gif" if f.endswith(".gif") else "video/mp4")
        if u.path == "/w/api.php":
            return self.send(json.dumps({"query": {"pages": {"1": {"pageid": 1, "index": 1, "title": "File:Fire.gif", "imageinfo": [{"url": f"http://127.0.0.1:{self.server.server_port}/download/c/fire.gif", "width": 101, "height": 61, "mime": "image/gif", "descriptionurl": "http://x/f", "extmetadata": {"Artist": {"value": "Me"}, "LicenseShortName": {"value": "CC0"}}}]},
                "2": {"pageid": 2, "index": 2, "title": "File:Photo.jpg", "imageinfo": [{"url": "http://x/p.jpg", "width": 10, "height": 10, "mime": "image/jpeg"}]}}}}).encode())
        self.send_response(404); self.end_headers()
mock = ThreadingHTTPServer(("127.0.0.1", 0), H); threading.Thread(target=mock.serve_forever, daemon=True).start(); M = f"http://127.0.0.1:{mock.server_port}"
srv = subprocess.Popen([sys.executable, str(ROOT / "linux/spektronautilus.py"), "--no-browser", "--port", "8797", "--docs", str(ROOT / "docs")], stdout=subprocess.PIPE, text=True); srv.stdout.readline(); srv.stdout.readline()
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); ctx = b.new_context(viewport={"width": 1200, "height": 900}); ctx.add_init_script(f"window.VJ_BASES={{archive:'{M}',prelinger:'{M}',commons:'{M}/w/api.php'}}; try{{localStorage.setItem('spk_lang','en')}}catch(e){{}}")
        pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("http://127.0.0.1:8797/tools/app/index.html"); pg.click("#tabs [data-t=search]"); pg.wait_for_selector("#srcs input")
        names = pg.eval_on_selector_all("#srcs input", "e=>e.map(x=>[x.dataset.s,x.checked])"); d = dict(names)
        check(d["nasa"] is False and d["archive"] and d["prelinger"] and d["commonsgif"] and d["archivegif"], f"default sources: NASA off, GIF sources on {d}")
        check(pg.is_checked("#short") and pg.is_checked("#hidegov") and pg.is_checked("#loopsfirst"), "short / no government / loops first are on by default")
        def only(*on):
            for n in d:
                if pg.is_checked(f"#srcs input[data-s={n}]") != (n in on): pg.click(f"#srcs input[data-s={n}]", force=True)
        def titles(): return pg.eval_on_selector_all("#results .rc .t", "e=>e.map(x=>x.textContent)")
        only("archive"); pg.fill("#q", "city"); pg.click("#dosearch"); pg.wait_for_selector("#results .rc"); pg.wait_for_function("!document.querySelector('#dosearch').disabled")
        t = titles(); print("     ", t)
        check(set(t) == {"Neon city loop", "Vintage dancing 1950"}, "government film, the 30-minute film and the item without video are hidden")
        check(t[0] == "Neon city loop", "the item that says 'loop' comes first")
        check("hidden by your filters" in pg.inner_text("#smsg"), "the message says how many were hidden: " + pg.inner_text("#smsg"))
        check(pg.locator("#results .loopb").count() == 1, "one loops badge")
        dur = pg.eval_on_selector_all("#results .rc", "e=>e.map(x=>x.querySelectorAll('.muted')[0].textContent)"); check(all(" s" in x for x in dur) and "10 s" in dur[0], f"lengths come from the archive metadata: {dur}")
        pg.uncheck("#short"); pg.uncheck("#hidegov"); pg.click("#dosearch"); pg.wait_for_function("document.querySelectorAll('#results .rc').length>2")
        t = titles(); check("Army training film" in t and "Long documentary about a city" in t, f"with the filters off the rest appears {t}")
        # GIF sources
        only("archivegif", "commonsgif"); pg.check("#short"); pg.check("#hidegov"); pg.click("#dosearch"); pg.wait_for_function("document.querySelector('#results')&&document.querySelector('#results').textContent.includes('Fire')")
        t = titles(); check(sorted(t) == ["Fire", "Spinning thing"], f"GIF results from Archive and Commons (the jpg is skipped) {t}")
        check(pg.locator("#results .loopb").count() == 2 and "GIF" in pg.inner_text("#results"), "GIFs are marked as loops")
        pg.click("#results .rc >> nth=0"); pg.click("#results .rc >> nth=1"); pg.select_option("#o_preset", "ultrafast") if pg.locator("#o_preset").count() else None
        pg.click("#go"); pg.wait_for_function("VJ.JOBS.length && VJ.JOBS[0].status!=='running' && VJ.JOBS[0].status!=='queued'", timeout=90000)
        j = pg.evaluate("({s: VJ.JOBS[0].status, f: VJ.JOBS[0].failed, n: VJ.JOBS[0].results.map(r=>r.name)})"); print("     ", j)
        check(j["s"] == "done" and j["f"] == 0 and sum(1 for n in j["n"] if n.endswith(".mp4")) == 2, "downloaded GIFs are converted to mp4 (odd sizes too)")
        check(not errs, "no page errors " + "; ".join(errs[:2])); b.close()
finally:
    srv.terminate(); mock.shutdown()
print("\nALL OK" if not bad else "\nFAILED: " + "; ".join(bad)); raise SystemExit(1 if bad else 0)
