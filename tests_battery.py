"""Battery saving in the phone mixers (VJ mobile, Video DJ mobile): the picture is only drawn when something moves, and not at all in
the background unless it is sent to another screen. Fades and the sound keep running in the background.
NOT tested here: a real phone's battery (only how often the picture is drawn is counted)."""
import functools, http.server, subprocess, tempfile, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent; T = Path(tempfile.mkdtemp(prefix="spkbat_")); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
def ff(*a): subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *a], check=True)
vids = []
for name, col in (("Red", "ff0000"), ("Blue", "0000ff")):
    p = T / f"{name} - Clip.webm"; ff("-f", "lavfi", "-i", f"color=c=0x{col}:s=320x180:r=25:d=10", "-f", "lavfi", "-i", "sine=frequency=440:duration=10", "-c:v", "libvpx", "-b:v", "200k", "-c:a", "libvorbis", "-shortest", str(p)); vids.append(str(p))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_port}"
VIS = "window.__vis='visible';Object.defineProperty(document,'visibilityState',{get:()=>window.__vis,configurable:true});Object.defineProperty(document,'hidden',{get:()=>window.__vis==='hidden',configurable:true});"
PIX = "() => { const c = document.getElementById('prog'); const d = c.getContext('2d').getImageData(c.width/2|0, c.height/2|0, 1, 1).data; return [d[0], d[1], d[2]]; }"
def close(a, b, t=50): return all(abs(x - y) <= t for x, y in zip(a, b))
def rate(pg, ms=1500):
    a = pg.evaluate("({...SPK.saver.stats, t: SPK.S.lastTick})"); pg.wait_for_timeout(ms); z = pg.evaluate("({...SPK.saver.stats})")
    return (z["drawn"] - a["drawn"]) * 1000 / ms, (z["drawn"] + z["skipped"] - a["drawn"] - a["skipped"]) * 1000 / ms
def hide(pg, h): pg.evaluate(f"window.__vis={'\"hidden\"' if h else '\"visible\"'}; document.dispatchEvent(new Event('visibilitychange'))")
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    for app in ("vj", "dj"):
        ctx = b.new_context(viewport={"width": 390, "height": 800}, has_touch=True, is_mobile=True); ctx.add_init_script(VIS)
        pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(BASE + ("/vj-mobile/index.html" if app == "vj" else "/live-mobile/index.html")); pg.wait_for_selector("#prog")
        pg.wait_for_timeout(800)
        d, t = rate(pg); check(d <= 3 and t >= 20, f"{app}: nothing loaded: {d:.1f} pictures/s drawn (timing runs at {t:.0f}/s)")
        if app == "vj":
            pg.set_input_files("#files", vids); pg.wait_for_function("SPK.S.pads.filter(p=>p&&p.ready).length===2", timeout=15000)
            pg.click(".pad[data-i='0']")
        else:
            pg.set_input_files("#files", vids); pg.click("#bin .li:nth-child(1) [data-a=A]"); pg.click("#bin .li:nth-child(2) [data-a=B]")
            pg.wait_for_function("SPK.S.decks.A.item && SPK.S.decks.B.item && SPK.S.decks.A.el.readyState>=2 && SPK.S.decks.B.el.readyState>=2", timeout=20000)
            pg.click("#plA")
        pg.wait_for_timeout(900)
        d, t = rate(pg); check(d >= 20, f"{app}: a clip plays: every picture drawn ({d:.0f}/s)")
        check(close(pg.evaluate(PIX), [255, 0, 0]), f"{app}: the picture is right (red)")
        # stop: idle again, but a change still shows within a moment
        if app == "vj": pg.evaluate("SPK.S.pads.forEach(p => p && p.v.pause())")
        else: pg.click("#plA")
        pg.wait_for_timeout(1000)
        d, _ = rate(pg); check(d <= 3, f"{app}: paused: {d:.1f} pictures/s")
        pg.evaluate("SPK.setF(1,true)"); pg.wait_for_timeout(700)
        check(close(pg.evaluate(PIX), [0, 0, 0] if app == "vj" else [0, 0, 255]), f"{app}: a change while paused still reaches the picture")
        pg.evaluate("SPK.setF(0,true)"); pg.wait_for_timeout(700)
        # background: nothing drawn, slow timing, but a fade still finishes (the sound follows it)
        if app == "vj": pg.evaluate("SPK.S.pads.forEach(p => p && p.v.play())")
        else: pg.click("#plA")
        pg.wait_for_timeout(500); hide(pg, True); pg.wait_for_timeout(400)
        d, t = rate(pg); check(d == 0 and t <= 12, f"{app}: in the background: nothing drawn, timing slowed to {t:.0f}/s")
        pg.evaluate("SPK.S.auto = { from: 0, to: 1, t0: performance.now(), dur: 1000 }"); pg.wait_for_timeout(1600)
        check(pg.evaluate("SPK.S.f") > .99, f"{app}: a fade still finishes in the background")
        if app == "dj": check(not pg.evaluate("SPK.S.decks.A.el.paused"), "dj: the music keeps playing in the background")
        hide(pg, False); pg.wait_for_timeout(500)
        d, t = rate(pg); check(d >= 20, f"{app}: back on screen: full speed again ({d:.0f}/s)")
        # sending to another screen: keeps drawing in the background
        pg.evaluate("SPK.S.cast = { close() {} }"); hide(pg, True); pg.wait_for_timeout(400)
        d, _ = rate(pg); check(d >= 20, f"{app}: sending to another screen: keeps drawing in the background ({d:.0f}/s)")
        pg.evaluate("SPK.S.cast = null"); hide(pg, False)
        check(not errs, f"{app}: no page errors {errs[:2]}")
        ctx.close()
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
