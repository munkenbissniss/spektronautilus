"""Browser test of the VJ mixer's advanced view: five banks (100 loops, only the visible bank keeps videos loaded), auto mix and recording to a file.
The simple view must stay as it was. Test loops are webm (the test browser has no H.264)."""
import functools, http.server, subprocess, tempfile, threading
from pathlib import Path
ROOT = Path(__file__).resolve().parent; DOCS = ROOT / "docs"; T = Path(tempfile.mkdtemp(prefix="spkvjadv_")); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
files = []
for name, col in (("Red Loop", "ff0000"), ("Blue Loop", "0000ff"), ("Green Loop", "00ff00")):
    p = T / f"{name}.webm"; subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x{col}:s=320x180:r=25:d=2", "-c:v", "libvpx", "-b:v", "200k", str(p)], check=True); files.append(str(p))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(DOCS))); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{srv.server_port}/vj-pad/index.html"
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    ctx = b.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True); pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept())
    pg.goto(URL); pg.wait_for_selector("#pads .pad")
    check(not pg.is_visible("#banks") and not pg.is_visible("#apCard") and not pg.is_visible("#recCard"), "simple view: no banks, auto mix or recording on screen")
    check(pg.inner_text("#advBtn") == "Advanced view", "the switch says Advanced view")
    pg.click("#advBtn"); pg.wait_for_selector("#banks button")
    check(pg.locator("#banks button").count() == 5 and pg.is_visible("#apCard") and pg.is_visible("#recCard"), "advanced view: 5 banks, auto mix and recording")
    check(pg.inner_text("#advBtn") == "Simple view" and pg.evaluate("SPK.cfg.adv"), "the switch now says Simple view and is remembered")
    # 30 loops: 20 fill bank 1, 10 go to bank 2
    pg.set_input_files("#files", files * 10); pg.wait_for_function("SPK.S.pads.filter(Boolean).length==30", timeout=20000)
    pg.wait_for_function("SPK.S.pads.filter(p=>p&&p.loaded).length==20", timeout=20000)
    check(pg.evaluate("SPK.S.pads.slice(20,30).every(p=>p && !p.loaded)"), "loops in other banks keep no video in memory")
    px = pg.evaluate("(()=>{const c=SPK.S.pads[20].thumb;const d=c.getContext('2d').getImageData(80,45,1,1).data;return [d[0],d[1],d[2]]})()")
    check(sum(px) > 100, f"but they still have a picture {px}")
    check("Bank 1 · 20" in pg.inner_text("#banks") and "Bank 2 · 10" in pg.inner_text("#banks"), "bank buttons show how many loops each has")
    pg.click("#banks button >> nth=1"); pg.wait_for_function("SPK.S.pads.slice(20,30).every(p=>p.loaded)", timeout=10000)
    pg.wait_for_function("SPK.S.pads.slice(0,20).every(p=>!p.loaded)", timeout=10000)
    check(pg.locator("#pads .pad.has").count() == 10 and pg.locator("#pads .pad").first.get_attribute("data-i") == "20", "bank 2 shows its own pads, bank 1 videos are let go")
    pg.keyboard.press("1"); pg.wait_for_timeout(300)
    check(pg.evaluate("SPK.S.layers[SPK.S.sel].pad") == 20, "key 1 plays the first pad of the bank you are in (pad 21)")
    pg.keyboard.press("]"); check(pg.evaluate("SPK.S.bank") == 2, "] goes to the next bank"); pg.keyboard.press("["); pg.keyboard.press("[")
    check(pg.evaluate("SPK.S.bank") == 0, "[ goes back"); pg.wait_for_function("SPK.S.pads[20].loaded", timeout=5000)
    check(pg.evaluate("SPK.S.pads[20].loaded"), "a loop that is playing stays loaded when you leave its bank")
    # auto mix
    pg.evaluate("SPK.cfg.fadeSec=0.5; SPK.cfg.apEvery=3; SPK.cfg.apFrom='all'; SPK.cfg.apStack=2"); pg.evaluate("SPK.setBank(0)")
    pg.click("#apGo"); check(pg.evaluate("SPK.AP.on") and "Stop" in pg.inner_text("#apGo"), "auto mix starts")
    pg.wait_for_function("SPK.AP.scene>=3", timeout=30000); check(True, "it changes scene on its own (scene %s)" % pg.evaluate("SPK.AP.scene"))
    check("Scene" in pg.inner_text("#apStat"), "the status shows the scene and time: " + pg.inner_text("#apStat"))
    used = pg.evaluate("SPK.S.layers.filter(l=>l.pad>=0).length"); check(used >= 2, f"it fills layers with loops ({used})")
    pg.click("#apGo"); check(not pg.evaluate("SPK.AP.on"), "auto mix stops")
    # a mix with a set length ends itself
    pg.evaluate("SPK.cfg.apLen=0.07"); pg.click("#apGo"); pg.wait_for_function("!SPK.AP.on", timeout=30000)
    check("finished" in pg.inner_text("#toast"), "a mix with a length ends by itself")
    # recording
    pg.evaluate("SPK.cfg.apLen=0; SPK.cfg.apRec=true"); pg.click("#apGo"); pg.wait_for_timeout(3500)
    check(pg.evaluate("!!SPK.S.rec") and "Recording" in pg.inner_text("#recStat"), "auto mix can record: " + pg.inner_text("#recStat"))
    pg.click("#apGo"); pg.wait_for_function("SPK.S.recFile", timeout=15000)
    sz = pg.evaluate("SPK.S.recFile.size"); check(sz > 2000 and pg.is_visible("#recSave"), f"the recording is ready to save ({sz} bytes)")
    with pg.expect_download() as d: pg.click("#recSave")
    check(d.value.suggested_filename.startswith("vj-mix-"), "saved as " + d.value.suggested_filename)
    pg.evaluate("SPK.cfg.apRec=false"); pg.click("#recBtn"); pg.wait_for_timeout(1500); check(pg.evaluate("!!SPK.S.rec") and "Stop" in pg.inner_text("#recBtn"), "Record button starts a recording")
    pg.click("#recBtn"); pg.wait_for_function("!SPK.S.rec", timeout=10000); check(True, "and stops it")
    # back to the simple view: nothing is lost
    pg.click("#advBtn"); check(pg.evaluate("SPK.S.pads.filter(Boolean).length") == 30 and pg.locator("#pads .pad").count() == 20 and not pg.is_visible("#banks"), "simple view again: 20 pads, the other loops are kept")
    check("kept" in pg.inner_text("#toast"), "and it says so"); pg.click("#advBtn")
    # 100 loops
    pg.evaluate("for(let i=0;i<100;i++) SPK.freePad(i)"); pg.set_input_files("#files", files * 35)
    pg.wait_for_function("SPK.S.pads.filter(Boolean).length==100", timeout=40000); check(True, "100 loops fit")
    pg.wait_for_function("SPK.S.pads.filter(p=>p&&p.loaded).length<=20", timeout=60000)
    check(pg.evaluate("SPK.S.pads.filter(p=>p&&p.loaded).length") <= 20 and "100 pads are full" in pg.inner_text("#toast"), "only 20 videos are loaded, and the 101st loop gets a clear message")
    check(not errs, f"no script errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
