"""Browser test of the VJ mixer (docs/vj-mixer). Needs ffmpeg, playwright, Pillow. Test loops are webm (the test browser has no H.264).
NOT tested here: real MIDI hardware, a real projector, real music through a microphone, 1080p performance on weak computers."""
import functools, http.server, subprocess, sys, tempfile, threading
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parent; DOCS = ROOT / "docs"; T = Path(tempfile.mkdtemp(prefix="spkvj_"))
bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
files = []
for name, col in (("Red Loop", "ff0000"), ("Blue Loop", "0000ff"), ("Green Loop", "00ff00")):
    p = T / f"{name}.webm"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x{col}:s=640x360:r=25:d=2", "-c:v", "libvpx", "-b:v", "300k", str(p)], check=True); files.append(str(p))
(T / "Broken Loop.webm").write_bytes(b"nope"); Image.new("RGBA", (200, 100), (255, 255, 0, 255)).save(T / "logo.png")
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(DOCS))); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{srv.server_port}/vj-pad/index.html"
FAKE_MIDI = """window.__mi=[];navigator.requestMIDIAccess=async()=>{const i={name:'Fake Pads',onmidimessage:null};window.__mi.push(i);const m=new Map([['1',i]]);return{inputs:m,onstatechange:null}};window.__send=d=>window.__mi.forEach(i=>i.onmidimessage&&i.onmidimessage({data:new Uint8Array(d)}));"""
PIX = "([id,x,y]) => { const c = document.getElementById(id); const d = c.getContext('2d').getImageData(Math.round(c.width*x), Math.round(c.height*y), 1, 1).data; return [d[0], d[1], d[2]]; }"
def close(a, b, t=45): return all(abs(x - y) <= t for x, y in zip(a, b))
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required", "--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream"])
    ctx = b.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True, permissions=["microphone"]); ctx.add_init_script(FAKE_MIDI)
    pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept())
    pg.goto(URL); pg.wait_for_selector("#pads .pad")
    check(pg.locator("#pads .pad").count() == 20, "20 pads on the grid")
    pg.set_input_files("#files", files); pg.wait_for_function("SPK.S.pads.filter(p=>p&&p.ready).length==3", timeout=15000)
    check(pg.locator("#pads .pad.has").count() == 3, "3 loops loaded into pads with thumbnails")
    # layer A1 <- pad 1 (red)
    pg.evaluate("SPK.selectLayer(0)"); pg.click("#pads .pad >> nth=0"); pg.wait_for_timeout(500)
    check(close(pg.evaluate(PIX, ["cvA", .5, .5]), [255, 0, 0]), "pad click plays red on layer A1")
    check(close(pg.evaluate(PIX, ["prog", .5, .5]), [255, 0, 0]), "output shows channel A")
    check(close(pg.evaluate(PIX, ["cvB", .5, .5]), [0, 0, 0]), "channel B is black")
    # A2 <- pad 2 (blue) with Add -> magenta
    pg.keyboard.press("KeyX"); pg.keyboard.press("Digit2"); pg.wait_for_timeout(300)
    check(close(pg.evaluate(PIX, ["cvA", .5, .5]), [0, 0, 255]), "keys: X selects layer A2, 2 plays pad 2 (blue covers red)")
    pg.select_option(".lay[data-n='1'] select", "lighter"); pg.wait_for_timeout(300)
    check(close(pg.evaluate(PIX, ["cvA", .5, .5]), [255, 0, 255]), "Add blend: red + blue = magenta")
    pg.select_option(".lay[data-n='1'] select", "source-over")
    pg.evaluate("document.querySelector(\".lay[data-n='1'] input[type=range]\").value=50; document.querySelector(\".lay[data-n='1'] input[type=range]\").dispatchEvent(new Event('input',{bubbles:true}))"); pg.wait_for_timeout(300)
    check(close(pg.evaluate(PIX, ["cvA", .5, .5]), [128, 0, 128], 30), "layer opacity 50 % blends the layers")
    pg.click(".lay[data-n='1'] button[data-a=on]"); pg.wait_for_timeout(250)
    check(close(pg.evaluate(PIX, ["cvA", .5, .5]), [255, 0, 0]), "layer off hides it")
    # channel B + crossfader
    pg.keyboard.press("KeyV"); pg.keyboard.press("Digit3"); pg.wait_for_timeout(300)
    check(close(pg.evaluate(PIX, ["cvB", .5, .5]), [0, 255, 0]), "channel B plays green")
    pg.evaluate("SPK.setF(1,true)"); pg.wait_for_timeout(300); check(close(pg.evaluate(PIX, ["prog", .5, .5]), [0, 255, 0]), "crossfader at B shows green")
    pg.evaluate("SPK.setF(.5,true)"); pg.wait_for_timeout(300); check(close(pg.evaluate(PIX, ["prog", .5, .5]), [128, 128, 0], 35), "half way is a dissolve")
    pg.evaluate("SPK.setF(0,true)")
    pg.fill("#fadeSec", "0.5"); pg.dispatch_event("#fadeSec", "input"); pg.click("#mix"); pg.wait_for_function("SPK.S.f>.99", timeout=4000); check(True, "auto fade reaches B")
    pg.evaluate("SPK.setF(0,true)")
    # tap tempo
    for _ in range(5): pg.keyboard.press("Backquote"); pg.wait_for_timeout(500)
    bpm = pg.evaluate("SPK.S.bpm"); check(110 <= bpm <= 130, f"tap tempo finds about 120 BPM ({bpm})")
    # effects (on the beat, right after 'Beat 1 now')
    pg.evaluate("SPK.setBpm(60)"); pg.evaluate("document.getElementById('fxAmt').value=100; document.getElementById('fxAmt').dispatchEvent(new Event('input'))")
    pg.keyboard.press("KeyD"); pg.click("#beat1"); pg.wait_for_timeout(60)
    px = pg.evaluate(PIX, ["prog", .5, .5]); check(px[1] > 150 and px[2] > 150, f"Flash brightens the picture on the beat {px}")
    pg.wait_for_timeout(1850); px = pg.evaluate(PIX, ["prog", .5, .5]); pg.keyboard.press("KeyD")
    check(close(px, [255, 0, 0], 60), f"flash fades away between beats {px}")
    pg.keyboard.press("KeyG"); pg.click("#beat1"); pg.wait_for_timeout(60); px = pg.evaluate(PIX, ["prog", .5, .5]); pg.keyboard.press("KeyG")
    check(px[0] < 120 and px[1] > 150 and px[2] > 150, f"Invert turns red into cyan on the beat {px}")
    # poster + logo
    pg.fill("#pl1", "VJ Test"); pg.click("#colors button[data-id=gold]"); pg.keyboard.press("Escape"); pg.click("#pshow"); pg.wait_for_timeout(1300)
    px = pg.evaluate(PIX, ["prog", .05, .9]); check(px[0] > 200 and px[1] > 150 and px[2] < 120, f"poster drawn {px}")
    pg.click("#phide"); pg.wait_for_timeout(1700)
    pg.click("details:has(summary:text('Logo')) summary"); pg.set_input_files("#logoFile", str(T / "logo.png")); pg.wait_for_function("SPK.S.logo.img", timeout=5000); pg.wait_for_timeout(300)
    px = pg.evaluate(PIX, ["prog", .93, .08]); check(px[0] > 200 and px[1] > 200 and px[2] < 80, f"logo upper right {px}")
    # output window
    with ctx.expect_page() as pop: pg.click("#openOut")
    o = pop.value; o.wait_for_function("document.getElementById('v').videoWidth > 0", timeout=8000)
    px = o.evaluate("() => { const v=document.getElementById('v'); const c=document.createElement('canvas'); c.width=v.videoWidth; c.height=v.videoHeight; const x=c.getContext('2d'); x.drawImage(v,0,0); const d=x.getImageData(c.width*.5,c.height*.5,1,1).data; return [d[0],d[1],d[2],v.videoWidth]; }")
    check(px[3] == 1280 and px[0] > 150, f"output window shows the picture {px}"); o.close()
    # MIDI
    pg.click("details:has(summary:text('MIDI')) summary"); pg.click("#midiOn"); pg.wait_for_function("document.getElementById('midiStatus').textContent.includes('Fake Pads')")
    pg.click("button[data-l=pad3]"); pg.evaluate("__send([0x99,38,100])")
    pg.evaluate("SPK.selectLayer(0)"); pg.evaluate("__send([0x99,38,100])"); pg.wait_for_timeout(300)
    check(pg.evaluate("SPK.S.layers[0].pad") == 2, "MIDI pad triggers pad 3 on the selected layer")
    pg.click("button[data-l=xfade]"); pg.evaluate("__send([0xb0,7,5])"); pg.evaluate("__send([0xb0,7,127])"); check(pg.evaluate("SPK.S.f") > .99, "MIDI fader moves the crossfader"); pg.evaluate("SPK.setF(0,true)")
    # audio kick input
    pg.evaluate("SPK.setBeatSource('audio')"); pg.wait_for_function("SPK.S.mic", timeout=5000); pg.wait_for_timeout(4500)
    k = pg.evaluate("SPK.S.kick.count"); check(pg.evaluate("!!SPK.S.mic"), f"audio input connected (kicks heard from the test tone: {k})")
    pg.evaluate("SPK.setBeatSource('clock')"); check(pg.evaluate("SPK.S.mic") is None, "audio input released when switching back")
    # 20 pads, broken file, remember
    pg.evaluate("for(let i=0;i<20;i++) SPK.freePad(i)"); pg.set_input_files("#files", files * 7)
    pg.wait_for_function("SPK.S.pads.filter(Boolean).length==20", timeout=20000); check(True, "20 loops fill every pad")
    pg.set_input_files("#files", files[:1]); check("full" in pg.inner_text("#toast"), "a 21st loop gives a clear message")
    pg.evaluate("SPK.freePad(0)")
    with pg.expect_file_chooser() as fc: pg.click("#pads .pad >> nth=0")
    fc.value.set_files(str(T / "Broken Loop.webm")); pg.wait_for_timeout(2500)
    check(pg.evaluate("SPK.S.pads[0]") is None and "can't play" in pg.inner_text("#toast"), "broken loop: clear message, pad freed")
    pg.evaluate("for(let i=3;i<20;i++) SPK.freePad(i)")
    pg.click("details:has(summary:text('Advanced')) summary"); pg.check("#remember"); pg.wait_for_timeout(1200)
    pg.reload(); pg.wait_for_selector("#pads .pad"); pg.wait_for_function("SPK.S.pads.filter(Boolean).length>=2", timeout=10000)
    check(pg.evaluate("SPK.S.pads.filter(Boolean).length") == 2, f"remembered loops come back after a reload ({pg.evaluate('SPK.S.pads.filter(Boolean).length')})")
    check(not [e for e in pg.evaluate("SPK.S.log") if e.startswith("ERR")], "no internal errors logged"); check(not errs, f"no page errors {errs}")
    pg.screenshot(path=str(ROOT / "shot-vj.png"), full_page=True)
    b.close()
print("FAILED" if bad else "ALL OK"); sys.exit(1 if bad else 0)
