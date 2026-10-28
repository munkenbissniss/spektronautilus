"""Browser test of the phone VJ mixer (docs/vj-mobile) in an emulated phone, incl. sending the picture to the receiver page over WebRTC.
NOT tested: a real phone, real casting, AirPlay, Wi-Fi between two devices, 1080p speed on a weak phone. Test videos are webm (the test browser has no H.264)."""
import functools, http.server, subprocess, tempfile, threading
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parent; DOCS = ROOT / "docs"; T = Path(tempfile.mkdtemp(prefix="spkvm_")); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
files = {}
for name, col in (("Red Loop", "ff0000"), ("Blue Loop", "0000ff"), ("Green Loop", "00ff00")):
    p = T / f"{name}.webm"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x{col}:s=640x360:r=25:d=6", "-c:v", "libvpx", "-b:v", "300k", str(p)], check=True); files[name] = p
Image.new("RGBA", (200, 100), (255, 255, 0, 255)).save(T / "logo.png")
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(DOCS))); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_port}"
PIX = "([x,y]) => { const c = document.getElementById('prog'); const d = c.getContext('2d').getImageData(Math.round(c.width*x), Math.round(c.height*y), 1, 1).data; return [d[0], d[1], d[2]]; }"
def close(a, b, t=50): return all(abs(x - y) <= t for x, y in zip(a, b))
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    ctx = b.new_context(viewport={"width": 390, "height": 800}, has_touch=True, is_mobile=True, user_agent="Mozilla/5.0 (Linux; Android 13) Mobile")
    pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept())
    pg.goto(BASE + "/vj-pad/index.html"); pg.wait_for_url("**/vj-mobile/**", timeout=5000); check(True, "phone opening the desktop VJ mixer is sent to the phone version")
    pg.goto(BASE + "/vj-pad/index.html?desktop=1"); pg.wait_for_timeout(500); check("/vj-pad/" in pg.url, "?desktop=1 keeps the desktop version")
    pg.evaluate("localStorage.removeItem('spk_desktop')")
    pg.goto(BASE + "/vj-mobile/index.html"); pg.wait_for_selector(".pad")
    check(pg.locator(".pad").count() == 8 and pg.locator(".lay").count() == 4, "8 pads and 4 layers")
    check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no sideways scrolling on a phone")
    pg.set_input_files("#files", list(files.values())); pg.wait_for_function("SPK.S.pads.filter(p=>p&&p.ready).length===3", timeout=15000)
    check(pg.locator(".pad:not(.empty)").count() == 3, "three videos fill pads 1-3")
    check("Red Loop" in pg.inner_text("#pads"), "pad shows the clip name")
    # pad onto layer A1 (selected by default), then B1
    pg.click(".pad[data-i='0']"); pg.wait_for_timeout(700); check(close(pg.evaluate(PIX, [.5, .5]), [255, 0, 0]), "tap pad 1 -> red on channel A")
    check(pg.locator(".pad[data-i='0']").evaluate("e=>e.classList.contains('live')"), "live pad is highlighted")
    pg.click(".lay[data-n='2']"); pg.click(".pad[data-i='1']"); pg.wait_for_timeout(500)
    check(close(pg.evaluate(PIX, [.5, .5]), [255, 0, 0]), "channel B is hidden while the crossfader is at A")
    pg.evaluate("SPK.setF(1,true)"); pg.wait_for_timeout(500); check(close(pg.evaluate(PIX, [.5, .5]), [0, 0, 255]), "crossfader at B -> blue")
    pg.evaluate("SPK.setF(.5,true)"); pg.wait_for_timeout(500); check(close(pg.evaluate(PIX, [.5, .5]), [128, 0, 128], 40), "half way is a dissolve")
    pg.evaluate("SPK.setF(0,true)"); pg.select_option("#fadeSec", "2"); pg.click("#mix"); pg.wait_for_function("SPK.S.f>.99 && !SPK.S.auto", timeout=6000)
    check(pg.inner_text("#mix") == "Mix → A", "Mix fades to B and offers the way back")
    # layers: opacity, off, blend, second layer on same channel
    pg.evaluate("SPK.setF(0,true)"); pg.click(".lay[data-n='1']"); pg.click(".pad[data-i='2']"); pg.wait_for_timeout(500)
    check(close(pg.evaluate(PIX, [.5, .5]), [0, 255, 0]), "layer A2 (green) covers A1")
    pg.evaluate("document.querySelector('#op').value=50; document.querySelector('#op').dispatchEvent(new Event('input'))"); pg.wait_for_timeout(400)
    check(close(pg.evaluate(PIX, [.5, .5]), [128, 128, 0], 40), "50% opacity blends green over red")
    pg.click("#lon"); pg.wait_for_timeout(400); check(close(pg.evaluate(PIX, [.5, .5]), [255, 0, 0]) and pg.inner_text("#lon") == "Off", "layer Off shows the layer below")
    pg.click("#lclr"); check(pg.evaluate("SPK.S.layers[1].pad") == -1, "Clear empties the layer")
    # beat
    for _ in range(4): pg.click("#tap"); pg.wait_for_timeout(500)
    bpm = float(pg.input_value("#bpm")); check(95 <= bpm <= 130, f"tap tempo about 120 BPM ({bpm})")
    pg.fill("#bpm", "100"); pg.dispatch_event("#bpm", "change"); pg.click("#dbl"); check(pg.input_value("#bpm") == "200", "×2 doubles the tempo")
    pg.click("#half"); pg.click("#half"); check(pg.input_value("#bpm") == "50", "÷2 halves it")
    pg.fill("#bpm", "60"); pg.dispatch_event("#bpm", "change")
    # effects
    pg.click("#fx button:has-text('Flash')"); pg.click("#beat1"); pg.wait_for_timeout(120)
    px = pg.evaluate(PIX, [.5, .5]); check(px[0] > 200 and px[1] > 60, f"Flash lights the picture on the beat {px}")
    pg.wait_for_timeout(900); pg.click("#fx button:has-text('Flash')")
    pg.click("#fx button:has-text('Invert')"); pg.click("#beat1"); pg.wait_for_timeout(120)
    px = pg.evaluate(PIX, [.5, .5]); check(px[0] < 100 and px[1] > 150, f"Invert flips the colours on the beat {px}")
    pg.click("#fx button:has-text('Invert')")
    # poster + logo
    pg.click("summary:text('Poster')"); pg.fill("#pl1", "TEST ARTIST"); pg.fill("#pl2", "Live now"); pg.click("#colors button:nth-child(2)"); pg.click("#pshow"); pg.wait_for_timeout(1400)
    seen = False
    for x in (.06, .1, .15, .2, .25, .3):
        for y in (.84, .88, .92):
            r, g_, bl = pg.evaluate(PIX, [x, y])
            if (r, g_, bl) != (255, 0, 0) and max(abs(r - 255), g_, bl) > 80: seen = True
    check(seen, "poster is drawn over the picture")
    pg.click("#phide"); pg.wait_for_timeout(1600); check(pg.evaluate("SPK.S.shown") is None, "poster slides away again")
    pg.click("summary:text('Logo')"); pg.set_input_files("#logoFile", str(T / "logo.png")); pg.wait_for_function("SPK.S.logo.img", timeout=4000); pg.wait_for_timeout(300)
    yel = False
    for x in (.9, .92, .94):
        for y in (.08, .1, .12):
            r, g_, bl = pg.evaluate(PIX, [x, y]); yel = yel or (r > 200 and g_ > 200 and bl < 80)
    check(yel, "logo shows upper right")
    # remove, settings
    pg.click(".pad[data-i='2'] [data-x]"); check(pg.locator(".pad:not(.empty)").count() == 2, "✕ removes a loop")
    pg.click("summary:text('Settings')"); pg.select_option("#res", "640x360"); check(pg.evaluate("document.getElementById('prog').width") == 640, "picture size can be changed")
    pg.select_option("#res", "960x540")
    # cast
    pg.click("details:has(summary:text('Send to another screen')) summary"); pg.click("#castStart"); pg.wait_for_selector("#castStep2", state="visible", timeout=15000)
    offer = pg.input_value("#offerBox"); check(len(offer) > 200, f"offer code made ({len(offer)} characters)")
    pg.click(".pad[data-i='0']"); pg.evaluate("SPK.setF(0,true)")
    link = pg.evaluate("new URL('../live-mobile/receiver.html', location.href).href + '#o=' + encodeURIComponent(document.getElementById('offerBox').value)")
    rx = ctx.new_page(); rx.on("pageerror", lambda e: errs.append("rx: " + str(e))); rx.goto(link); rx.wait_for_function("document.getElementById('answer').value.length > 100", timeout=15000)
    pg.fill("#answerBox", rx.input_value("#answer")); pg.click("#castConnect")
    rx.wait_for_function("document.body.classList.contains('live') && __rx.video.videoWidth > 0", timeout=25000); check(True, "receiver connected and got video")
    PX_RX = "() => { const v=__rx.video; const c=document.createElement('canvas'); c.width=v.videoWidth; c.height=v.videoHeight; const x=c.getContext('2d'); x.drawImage(v,0,0); const d=x.getImageData(c.width/2,c.height/2,1,1).data; return [d[0],d[1],d[2]]; }"
    rx.wait_for_timeout(600); px = rx.evaluate(PX_RX); check(px[0] > 150 and px[2] < 120, f"receiver shows the phone's picture (red) {px}")
    pg.evaluate("SPK.setF(1,true)"); rx.wait_for_timeout(1200); px = rx.evaluate(PX_RX); check(px[2] > 150 and px[0] < 120, f"receiver follows the crossfader (blue) {px}")
    pg.fill("#answerBox", "garbage"); pg.click("#castConnect"); check("does not look right" in pg.inner_text("#toast"), "a wrong code gives a clear message")
    pg.click("#castStop")
    # full screen button exists and survives a reload with settings kept
    pg.reload(); pg.wait_for_selector(".pad"); check(pg.evaluate("SPK.cfg.res") == "960x540" and pg.input_value("#bpm") == "60", "settings and tempo are remembered")
    check(not errs, "no page errors: " + "; ".join(errs[:3])); b.close()
print("\nALL OK" if not bad else "\nFAILED: " + "; ".join(bad)); raise SystemExit(1 if bad else 0)
