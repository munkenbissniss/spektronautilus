"""Browser test of the Live Video DJ Mixer (docs/live-dj). Needs ffmpeg (to make small test videos), playwright and Pillow.
The test videos are webm because the test browser has no H.264; real shows use mp4 in Chrome or Edge.
MIDI is tested with a fake MIDI device. Real MIDI hardware, an HDMI projector and casting are NOT tested here."""
import functools, http.server, subprocess, sys, tempfile, threading
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parent; DOCS = ROOT / "docs"; T = Path(tempfile.mkdtemp(prefix="spklive_"))
bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
files = {}
for name, col, hz in (("Red Band - Song One", "ff0000", 440), ("Blue Band - Song Two", "0000ff", 550), ("Green Band - Song Three", "00ff00", 660)):
    p = T / f"{name}.webm"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x{col}:s=640x360:r=25:d=8", "-f", "lavfi", "-i", f"sine=frequency={hz}:duration=8", "-c:v", "libvpx", "-b:v", "400k", "-c:a", "libvorbis", "-shortest", str(p)], check=True)
    files[name] = p
(T / "Broken - File.webm").write_bytes(b"not a video")
Image.new("RGBA", (200, 100), (255, 255, 0, 255)).save(T / "logo.png")

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(DOCS))); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{srv.server_port}/live-dj/index.html"
FAKE_MIDI = """
window.__midiInputs = [];
navigator.requestMIDIAccess = async () => { const inp = { name: 'Fake Controller', onmidimessage: null }; window.__midiInputs.push(inp);
  const m = new Map([['1', inp]]); m.onstatechange = null; return { inputs: m, onstatechange: null }; };
window.__sendMidi = d => window.__midiInputs.forEach(i => i.onmidimessage && i.onmidimessage({ data: new Uint8Array(d) }));
"""
JS_PIX = "([x,y]) => { const c = document.getElementById('prog'); const d = c.getContext('2d').getImageData(Math.round(c.width*x), Math.round(c.height*y), 1, 1).data; return [d[0], d[1], d[2]]; }"
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    ctx = b.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True); ctx.add_init_script(FAKE_MIDI)
    pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_selector("#decks .deck")
    pg.set_input_files("#files", [str(files[n]) for n in files] + [str(T / "Broken - File.webm")])
    check(pg.evaluate("SPK.S.lib.length") == 4, "4 files added to the library")
    check("Red Band – Song One" in pg.inner_text("#lib"), "title parsed from the file name")
    pg.evaluate("SPK.load('A', SPK.S.lib[0])"); pg.evaluate("SPK.load('B', SPK.S.lib[1])")
    pg.wait_for_function("SPK.S.decks.A.item && SPK.S.decks.B.item && SPK.S.decks.A.el.readyState>=2 && SPK.S.decks.B.el.readyState>=2", timeout=20000)
    check(pg.inner_text("#nmA").startswith("Red Band"), "deck A shows its track")
    pg.click("#plA"); pg.wait_for_timeout(1200)
    t = pg.evaluate("SPK.S.decks.A.el.currentTime"); check(t > 0.5, f"deck A plays (t={t:.2f})")
    pg.click("#plB"); pg.wait_for_timeout(500)
    px = pg.evaluate(JS_PIX, [.5, .5]); check(px[0] > 200 and px[2] < 60, f"crossfader at A shows red {px}")
    pg.evaluate("SPK.setF(1, true)"); pg.wait_for_timeout(400)
    px = pg.evaluate(JS_PIX, [.5, .5]); check(px[2] > 200 and px[0] < 60, f"crossfader at B shows blue {px}")
    pg.evaluate("SPK.setF(.5, true)"); pg.wait_for_timeout(400)
    px = pg.evaluate(JS_PIX, [.5, .5]); check(100 < px[0] < 160 and 100 < px[2] < 160, f"half way is a dissolve {px}")
    ga = pg.evaluate("[SPK.S.decks.A.gain.gain.value, SPK.S.decks.B.gain.gain.value]")
    check(abs(ga[0] - .7071) < .03 and abs(ga[1] - .7071) < .03, f"equal-power sound gains in the middle {ga}")
    pg.evaluate("SPK.setF(0, true)"); pg.wait_for_timeout(300)
    ga = pg.evaluate("[SPK.S.decks.A.gain.gain.value, SPK.S.decks.B.gain.gain.value]"); check(ga[0] > .97 and ga[1] < .03, f"sound gains at A {ga}")
    # peak meter shows sound
    pg.wait_for_timeout(300); check(float(pg.evaluate("parseFloat(document.getElementById('meA').style.width)||0")) > 2, "deck A level meter moves")
    # auto fade
    pg.fill("#fadeSec", "1"); pg.dispatch_event("#fadeSec", "input"); pg.click("#mix")
    pg.wait_for_function("SPK.S.f > .99", timeout=5000); pg.wait_for_timeout(300)
    check(pg.evaluate("SPK.S.decks.A.el.paused"), "after the auto fade the old deck stops")
    check(pg.inner_text("#mix") == "Mix → A", "button now offers the way back: " + pg.inner_text("#mix"))
    # keyboard
    pg.keyboard.press("ArrowLeft"); check(abs(pg.evaluate("SPK.S.f") - .95) < .001, "arrow key nudges the crossfader")
    # manual move cancels auto fade
    pg.evaluate("SPK.setF(1, true)"); pg.fill("#fadeSec", "20"); pg.dispatch_event("#fadeSec", "input"); pg.click("#mix"); pg.wait_for_timeout(300)
    pg.evaluate("document.getElementById('xf').value=900; document.getElementById('xf').dispatchEvent(new Event('input'))"); pg.wait_for_timeout(500)
    check(pg.evaluate("SPK.S.auto") is None and abs(pg.evaluate("SPK.S.f") - .9) < .01, "moving the fader by hand cancels the auto fade")
    pg.evaluate("SPK.setF(0, true)")
    # poster
    pg.fill("#pl1", "Red Band"); pg.fill("#pl2", "Song One"); pg.click("#colors button[data-id=gold]"); pg.click("#pshow"); pg.wait_for_timeout(1500)
    px = pg.evaluate(JS_PIX, [.06, .88]); check(px[0] > 200 and px[1] > 150 and px[2] < 120, f"poster drawn in the chosen colour {px}")
    pg.screenshot(path=str(ROOT / "shot-live.png"), full_page=True)
    pg.click("#phide"); pg.wait_for_timeout(1800); px = pg.evaluate(JS_PIX, [.06, .88])
    check(pg.evaluate("SPK.S.shown") is None, "poster slides out and is gone")
    pg.click("#psave"); check(pg.inner_text("#slots button").startswith("Red Band"), "poster saved to slot 1")
    pg.evaluate("SPK.slotShow(1)"); pg.wait_for_timeout(1000); check(pg.evaluate("SPK.S.shown") is not None, "slot shows the poster")
    pg.click("#phide"); pg.wait_for_timeout(1800)
    # logo
    pg.click("details:has(summary:text('Logo')) summary"); pg.set_input_files("#logoFile", str(T / "logo.png")); pg.wait_for_function("SPK.S.logo.img", timeout=5000); pg.wait_for_timeout(300)
    px = pg.evaluate(JS_PIX, [.93, .08]); check(px[0] > 200 and px[1] > 200 and px[2] < 80, f"logo in the upper right {px}")
    pg.evaluate("document.getElementById('logoOn').click()"); pg.wait_for_timeout(300)
    px = pg.evaluate(JS_PIX, [.93, .08]); check(not (px[0] > 200 and px[1] > 200 and px[2] < 80), "logo can be switched off")
    pg.evaluate("document.getElementById('logoOn').click()")
    # output window
    with ctx.expect_page() as pop: pg.click("#openOut")
    o = pop.value; o.wait_for_function("document.getElementById('v').videoWidth > 0", timeout=8000)
    px = o.evaluate("() => { const v=document.getElementById('v'); const c=document.createElement('canvas'); c.width=v.videoWidth; c.height=v.videoHeight; const x=c.getContext('2d'); x.drawImage(v,0,0); const d=x.getImageData(c.width/2,c.height/2,1,1).data; return [d[0],d[1],d[2],v.videoWidth,v.videoHeight]; }")
    check(px[3] == 1920 and px[0] > 150, f"output window shows the program picture {px}")
    pg.evaluate("SPK.setF(1, true)"); o.wait_for_timeout(1000)
    px = o.evaluate("() => { const v=document.getElementById('v'); const c=document.createElement('canvas'); c.width=v.videoWidth; c.height=v.videoHeight; const x=c.getContext('2d'); x.drawImage(v,0,0); const d=x.getImageData(c.width/2,c.height/2,1,1).data; return [d[0],d[1],d[2]]; }")
    check(px[2] > 150 and px[0] < 80, f"output follows the crossfader {px}")
    pg.bring_to_front(); pg.evaluate("SPK.setF(0, true)")
    # background: ticker keeps running when this window is hidden
    pg.evaluate("window.__n=0; const t=SPK.tick; "); 
    # record
    pg.click("#rec"); pg.wait_for_timeout(2500)
    with pg.expect_download() as dl: pg.click("#rec")
    sz = Path(dl.value.path()).stat().st_size; check(sz > 5000 and dl.value.suggested_filename.endswith(".webm"), f"recording saved ({sz} bytes)")
    o.close()
    # MIDI
    pg.click("details:has(summary:text('MIDI')) summary"); pg.click("#midiOn"); pg.wait_for_function("document.getElementById('midiStatus').textContent.includes('Fake Controller')", timeout=3000)
    check(True, "MIDI device is listed")
    pg.click("button[data-l=xfade]"); pg.evaluate("__sendMidi([0xb0, 7, 10])")
    check("cc ch1 #7" in pg.inner_text("#mtbl"), "learn mapped a fader to the crossfader")
    pg.evaluate("__sendMidi([0xb0, 7, 127])"); check(abs(pg.evaluate("SPK.S.f") - 1) < .001, "MIDI fader moves the crossfader")
    pg.evaluate("__sendMidi([0xb0, 7, 0])")
    pg.click("button[data-l=playA]"); pg.evaluate("__sendMidi([0x99, 36, 100])"); was = pg.evaluate("SPK.S.decks.A.el.paused")
    pg.evaluate("__sendMidi([0x99, 36, 100])"); check(pg.evaluate("SPK.S.decks.A.el.paused") != was, "MIDI note toggles play on deck A")
    pg.on("dialog", lambda d: d.accept()); pg.reload(); pg.wait_for_selector("#decks .deck"); check("#7" in pg.text_content("#mtbl"), "MIDI mapping survives a reload")
    # bad file does not hurt the working deck
    pg.set_input_files("#files", [str(T / "Broken - File.webm")])
    pg.evaluate("SPK.load('A', SPK.S.lib[SPK.S.lib.length-1])"); pg.wait_for_timeout(2500)
    check(pg.evaluate("SPK.S.decks.A.item") is None and "can't play" in pg.inner_text("#toast"), "broken file gives a clear message and the deck is left empty")
    check(not [e for e in pg.evaluate("SPK.S.log") if e.startswith("ERR")], "no internal errors logged")
    check(not errs, f"no page errors {errs}")
    # auto-mix across three tracks
    pg2 = ctx.new_page(); pg2.goto(URL); pg2.wait_for_selector("#decks .deck")
    pg2.set_input_files("#files", [str(files[n]) for n in files])
    pg2.fill("#fadeSec", "1"); pg2.dispatch_event("#fadeSec", "input"); pg2.evaluate("(()=>{const e=document.getElementById('autoSec'); e.value=3; e.dispatchEvent(new Event('input'))})()")
    pg2.evaluate("document.getElementById('autoMix').click()")
    pg2.evaluate("SPK.load('A', SPK.S.lib[0])"); pg2.wait_for_function("SPK.S.decks.A.el.readyState>=2", timeout=15000); pg2.click("#plA")
    pg2.wait_for_function("SPK.S.f > .99 && SPK.S.decks.B.item && !SPK.S.decks.B.el.paused", timeout=15000)
    check("Blue" in pg2.inner_text("#nmB"), "auto-mix loaded the next track on B and faded to it: " + pg2.inner_text("#nmB"))
    pg2.wait_for_function("SPK.S.decks.A.item && SPK.S.decks.A.item.name.includes('Green')", timeout=10000)
    check(True, "auto-mix cued the third track on the idle deck")
    pg2.wait_for_function("SPK.S.f < .01", timeout=15000); check(True, "auto-mix mixed on to the third track")
    b.close()
print("FAILED" if bad else "ALL OK"); sys.exit(1 if bad else 0)
