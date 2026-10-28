"""Browser test of the phone live mixer (docs/live-mobile) in an emulated phone, including sending the picture to a second page
(the receiver) over WebRTC with hand-copied codes. Needs ffmpeg, playwright, Pillow.
NOT tested: a real phone, real casting to a TV or projector computer, AirPlay, Wi-Fi between two devices (here both pages share one browser)."""
import functools, http.server, subprocess, sys, tempfile, threading
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parent; DOCS = ROOT / "docs"; T = Path(tempfile.mkdtemp(prefix="spklm_"))
bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
files = {}
for name, col, hz in (("Red Band - One", "ff0000", 440), ("Blue Band - Two", "0000ff", 550)):
    p = T / f"{name}.webm"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x{col}:s=640x360:r=25:d=10", "-f", "lavfi", "-i", f"sine=frequency={hz}:duration=10", "-c:v", "libvpx", "-b:v", "300k", "-c:a", "libvorbis", "-shortest", str(p)], check=True); files[name] = str(p)
Image.new("RGBA", (200, 100), (255, 255, 0, 255)).save(T / "logo.png")
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(DOCS))); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_port}"
PIX = "([id,x,y]) => { const c = document.getElementById(id); const d = c.getContext('2d').getImageData(Math.round(c.width*x), Math.round(c.height*y), 1, 1).data; return [d[0], d[1], d[2]]; }"
def close(a, b, t=50): return all(abs(x - y) <= t for x, y in zip(a, b))
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    ctx = b.new_context(viewport={"width": 390, "height": 800}, has_touch=True, is_mobile=True, user_agent="Mozilla/5.0 (Linux; Android 13) Mobile")
    # the desktop address sends phones here
    pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept())
    pg.goto(BASE + "/live-dj/index.html"); pg.wait_for_url("**/live-mobile/**", timeout=5000); check(True, "phone opening the desktop live mixer is sent to the phone version")
    pg.goto(BASE + "/live-dj/index.html?desktop=1"); pg.wait_for_timeout(500); check("/live-dj/" in pg.url, "?desktop=1 keeps the desktop version")
    pg.goto(BASE + "/live-mobile/index.html"); pg.wait_for_selector(".deck")
    check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no sideways scrolling on a phone")
    pg.set_input_files("#files", list(files.values())); check(pg.locator("#bin .li").count() == 2, "two videos in the clip list")
    pg.click("#bin .li:nth-child(1) [data-a=A]"); pg.click("#bin .li:nth-child(2) [data-a=B]")
    pg.wait_for_function("SPK.S.decks.A.item && SPK.S.decks.B.item && SPK.S.decks.A.el.readyState>=2 && SPK.S.decks.B.el.readyState>=2", timeout=20000)
    pg.click("#plA"); pg.click("#plB"); pg.wait_for_timeout(900)
    check(close(pg.evaluate(PIX, ["prog", .5, .5]), [255, 0, 0]), "deck A on air shows red")
    pg.evaluate("SPK.setF(1,true)"); pg.wait_for_timeout(400); check(close(pg.evaluate(PIX, ["prog", .5, .5]), [0, 0, 255]), "crossfader at B shows blue")
    pg.evaluate("SPK.setF(.5,true)"); pg.wait_for_timeout(400); check(close(pg.evaluate(PIX, ["prog", .5, .5]), [128, 0, 128], 35), "half way is a dissolve")
    ga = pg.evaluate("[SPK.S.decks.A.gain.gain.value, SPK.S.decks.B.gain.gain.value]"); check(abs(ga[0] - .7071) < .04, f"equal-power sound in the middle {ga}")
    pg.evaluate("SPK.setF(0,true)")
    pg.select_option("#fadeSec", "2"); pg.click("#mix"); pg.wait_for_function("SPK.S.f>.99", timeout=6000); pg.wait_for_timeout(300)
    check(pg.evaluate("SPK.S.decks.A.el.paused") and "Mix → A" == pg.inner_text("#mix"), "mix fades to B, stops A and offers the way back")
    pg.evaluate("SPK.setF(0,true)"); pg.click("#lpA"); check(pg.evaluate("SPK.S.decks.A.el.loop"), "loop button repeats the video")
    # hold effects with the finger
    box = pg.locator("#fx [data-i='0']").bounding_box()
    pg.mouse.move(box["x"] + 10, box["y"] + 10); pg.mouse.down(); pg.wait_for_timeout(120); px = pg.evaluate(PIX, ["prog", .5, .5]); check(px[1] > 150 and px[2] > 150, f"holding Flash brightens the picture {px}")
    pg.mouse.up(); pg.wait_for_timeout(300); check(close(pg.evaluate(PIX, ["prog", .5, .5]), [255, 0, 0]), "letting go ends the effect")
    pg.evaluate("SPK.fxSet(2,true)"); pg.wait_for_timeout(200); px = pg.evaluate(PIX, ["prog", .5, .5]); pg.evaluate("SPK.fxSet(2,false)"); check(px[0] < 90 and px[1] > 160, f"Invert turns red into cyan {px}")
    # poster and logo
    pg.click("details:has(summary:text('Poster')) summary"); pg.fill("#pl1", "Phone Test"); pg.click("#colors [data-id=gold]"); pg.click("#pshow"); pg.wait_for_timeout(1300)
    pxs = [pg.evaluate(PIX, ["prog", x / 100, .9]) for x in range(5, 30, 2)]; px = next((q for q in pxs if q[0] > 200 and q[1] > 150 and q[2] < 120), pxs[0]); check(px[0] > 200 and px[1] > 150 and px[2] < 120, f"poster drawn in gold {px}")
    pg.click("#phide"); pg.wait_for_timeout(1500)
    pg.click("details:has(summary:text('Logo')) summary"); pg.set_input_files("#logoFile", str(T / "logo.png")); pg.wait_for_function("SPK.S.logo.img", timeout=5000); pg.wait_for_timeout(300)
    px = pg.evaluate(PIX, ["prog", .93, .09]); check(px[0] > 200 and px[1] > 200 and px[2] < 90, f"logo in the upper right {px}")
    # sending to another screen
    pg.click("details:has(summary:text('Send to another screen')) summary"); pg.click("#castStart"); pg.wait_for_selector("#castStep2", state="visible", timeout=15000)
    offer = pg.input_value("#offerBox"); check(len(offer) > 200 and offer[0] in "zp", f"offer code made ({len(offer)} characters)")
    link = pg.evaluate("new URL('receiver.html', location.href).href + '#o=' + encodeURIComponent(document.getElementById('offerBox').value)")
    rx = ctx.new_page(); rx.on("pageerror", lambda e: errs.append("rx: " + str(e)))
    rx.goto(link); rx.wait_for_function("document.getElementById('answer').value.length > 100", timeout=15000)
    ans = rx.input_value("#answer"); check(len(ans) > 100, f"answer code made on the receiver ({len(ans)} characters)")
    pg.fill("#answerBox", ans); pg.click("#castConnect")
    rx.wait_for_function("document.body.classList.contains('live') && __rx.video.videoWidth > 0", timeout=25000); check(True, "receiver connected and got video")
    PX_RX = "() => { const v=__rx.video; const c=document.createElement('canvas'); c.width=v.videoWidth; c.height=v.videoHeight; const x=c.getContext('2d'); x.drawImage(v,0,0); const d=x.getImageData(c.width/2,c.height/2,1,1).data; return [d[0],d[1],d[2]]; }"
    rx.wait_for_timeout(500); px = rx.evaluate(PX_RX); check(px[0] > 150 and px[2] < 120, f"receiver shows the phone's picture (red) {px}")
    pg.evaluate("SPK.setF(1,true)"); rx.wait_for_timeout(1200); px = rx.evaluate(PX_RX); check(px[2] > 150 and px[0] < 120, f"receiver follows the crossfader (blue) {px}")
    check(rx.evaluate("__rx.video.srcObject.getAudioTracks().length") == 1, "sound is sent too")
    pg.select_option("#castSound", "other"); check(pg.evaluate("SPK.S.audio.local.gain.value") == 0, "sound can be moved to the other screen only")
    pg.select_option("#castSound", "both"); check(pg.evaluate("SPK.S.audio.local.gain.value") == 1, "and back to both")
    pg.fill("#answerBox", "garbage"); pg.click("#castConnect"); check("does not look right" in pg.inner_text("#toast"), "a wrong code gives a clear message")
    pg.click("#castStop")
    # broken file
    (T / "Broken.webm").write_bytes(b"nope"); pg.set_input_files("#files", [str(T / "Broken.webm")]); pg.click("#bin .li:last-child [data-a=B]"); pg.wait_for_timeout(2500)
    check(pg.evaluate("SPK.S.decks.B.item") is None and "can't play" in pg.inner_text("#toast"), "a broken video gives a clear message")
    check(not [e for e in pg.evaluate("SPK.S.log") if e.startswith("ERR")], "no internal errors logged"); check(not errs, f"no page errors {errs}")
    pg.screenshot(path=str(ROOT / "shot-lm.png"), full_page=True)
    b.close()
print("FAILED" if bad else "ALL OK"); sys.exit(1 if bad else 0)
