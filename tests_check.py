"""Tests the 'Ready for the show?' check on the desktop mixers and the phone mixers, and the test card."""
import functools, http.server, threading
from pathlib import Path
ROOT = Path(__file__).resolve().parent; bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f"http://127.0.0.1:{srv.server_port}"
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for path, sel, kind in (("live-dj/index.html?desktop=1", "#decks .deck", "desktop"), ("vj-pad/index.html?desktop=1", ".pad", "desktop"), ("live-mobile/", ".deck", "phone"), ("vj-mobile/", ".pad", "phone")):
        ctx = b.new_context(viewport={"width": 1200, "height": 900} if kind == "desktop" else {"width": 390, "height": 800}, locale="en-US", **({} if kind == "desktop" else {"is_mobile": True, "has_touch": True}))
        pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"{B}/{path}"); pg.wait_for_selector(sel, state="attached")
        check(pg.locator("#spk-chk-open").count() == 1, f"{path.split('/')[0]}: the 'Ready for the show?' button is there")
        pg.click("#spk-chk-open"); pg.wait_for_selector("#spk-chk li", timeout=8000); pg.wait_for_function("document.querySelector('#spk-chk .sum').textContent.indexOf('Checking')<0", timeout=8000)
        rows = pg.locator("#spk-chk li").count(); names = pg.locator("#spk-chk li b").all_inner_texts()
        check(rows >= (8 if kind == "desktop" else 5), f"{path.split('/')[0]}: {rows} checks listed ({', '.join(names[:5])}…)")
        check("Video format" in names and "Speed" in names, "video format and speed are checked")
        check(("Output window" in names) == (kind == "desktop"), "the output window row exists on the desktop mixers only")
        txt = pg.evaluate("SPK_CHECK.report()"); check("[" in txt and "Spektronautilus" in txt and "Video format" in txt, "the report is plain text")
        pg.click("#spk-chk button:has-text('Run the check again')"); pg.wait_for_function("document.querySelector('#spk-chk .sum').textContent.indexOf('Checking')<0", timeout=8000); check(pg.locator("#spk-chk li").count() == rows, "run again works")
        if kind == "desktop":
            with ctx.expect_page() as np:
                pg.click("#spk-chk button:has-text('Show test card')")
            tc = np.value; tc.wait_for_load_state(); tc.wait_for_selector("canvas")
            check("testcard.html" in tc.url and tc.evaluate("document.getElementById('c').width") > 100, "the test card opens in its own window")
            tc.close()
        else:
            pg.click("#spk-chk button:has-text('Show test card')"); pg.wait_for_selector("#spk-card iframe")
            fr = pg.frame_locator("#spk-card iframe"); fr.locator("canvas").wait_for(); pg.wait_for_timeout(300)
            fr.locator("canvas").click(); pg.wait_for_selector("#spk-card", state="detached", timeout=3000); check(True, "phone: the test card closes with a tap")
        pg.keyboard.press("Escape"); check(pg.locator("#spk-chk").count() == 0, "Esc closes the check")
        check(not errs, f"no script errors {errs[:1]}"); ctx.close()
    # translated
    ctx = b.new_context(locale="en-US"); pg = ctx.new_page(); pg.goto(f"{B}/vj-pad/index.html?desktop=1&lang=no"); pg.wait_for_selector(".pad")
    check(pg.inner_text("#spk-chk-open") == "Klar for showet?", "the button is translated")
    pg.click("#spk-chk-open"); pg.wait_for_function("document.querySelector('#spk-chk .sum').textContent.indexOf('Sjekker')<0 && document.querySelector('#spk-chk .sum').textContent.length>3", timeout=8000); pg.wait_for_timeout(300)
    t = pg.inner_text("#spk-chk"); check("Videoformat" in t and "Ingen loops ennå" in t, "the whole dialog is in Norwegian"); print(t[:400])
    ctx.close(); b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
