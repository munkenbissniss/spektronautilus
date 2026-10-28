"""Tests the offline support: after one visit the whole site (pages, mixers, tools) opens with the network cut, and a new version
waits for the visitor's OK instead of replacing a running page. Service workers are off on localhost, so the test turns them on with ?sw=1."""
import functools, http.server, shutil, tempfile, threading, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent; T = Path(tempfile.mkdtemp(prefix="spkoff_")); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
site = T / "site"; shutil.copytree(ROOT / "docs", site)
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def end_headers(self): self.send_header("Cache-Control", "no-store"); super().end_headers()
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=str(site))); threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f"http://127.0.0.1:{srv.server_port}"
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={"width": 1200, "height": 900}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(B + "/index.html"); pg.wait_for_timeout(800); check(pg.evaluate("!!navigator.serviceWorker.controller") is False, "no service worker on plain localhost (the Linux version and other tests stay unaffected)")
    pg.goto(B + "/index.html?sw=1"); pg.wait_for_function("localStorage.getItem('spk_offline')==='1'", timeout=20000); check(True, "service worker installed and marked ready")
    pg.reload(); pg.wait_for_function("!!navigator.serviceWorker.controller", timeout=10000); check(True, "page is controlled by the service worker after a reload")
    n = pg.evaluate("caches.keys().then(async k => { const c = await caches.open(k[0]); return (await c.keys()).length })"); check(n > 60, f"{n} files stored")
    check(pg.evaluate("fetch('/manifest.webmanifest').then(r=>r.json()).then(j=>j.icons.length)") == 3, "web app manifest is served")
    ctx.set_offline(True)
    for path, sel, what in (("/live-dj/index.html?desktop=1", "#decks .deck", "Video DJ"), ("/vj-pad/index.html?desktop=1", ".pad", "VJ Mixer"), ("/mixer/index.html?desktop=1", "#pre", "Magic Mixer"),
                            ("/tools/app/index.html", "#groups details", "Tools"), ("/live-mobile/", ".deck", "phone live mixer"), ("/vj-mobile/", ".pad", "phone VJ mixer"),
                            ("/queue/", "#list", "Queue"), ("/no/", "h1", "Norwegian home"), ("/guides/video-dj/", "h1", "a guide")):
        p = ctx.new_page(); p.on("pageerror", lambda e: errs.append(path + " " + str(e)))
        try: p.goto(B + path); p.wait_for_selector(sel, timeout=8000); check(True, f"offline: {what} opens")
        except Exception as e: check(False, f"offline: {what} opens ({str(e)[:80]})")
        p.close()
    p = ctx.new_page(); p.goto(B + "/live-mobile/"); p.wait_for_selector(".deck")
    pg2 = ctx.new_page(); pg2.goto(B + "/no/tools/"); check("Verktøy" in pg2.inner_text("h1") or len(pg2.inner_text("h1")) > 0, "offline: another language page opens"); pg2.close()
    ctx.set_offline(False)
    # ---- a new version waits for the visitor
    sw = site / "sw.js"; sw.write_text(re.sub(r"VERSION = '[0-9a-f]+'", "VERSION = 'newversion1'", sw.read_text()))
    ab = site / "about/index.html"; ab.write_text(ab.read_text().replace("</main>", "<p id='newbit'>NEW VERSION TEXT</p></main>", 1))
    pg.evaluate("navigator.serviceWorker.getRegistration().then(r => r.update())")
    pg.wait_for_selector("#spk-upd", timeout=15000); check("new version" in pg.inner_text("#spk-upd").lower(), "a bar offers the new version")
    pg.goto(B + "/about/index.html?sw=1"); check(pg.locator("#newbit").count() == 0, "the open site still shows the old version until the visitor accepts")
    pg.wait_for_selector("#spk-upd", timeout=8000)
    with pg.expect_navigation(timeout=15000): pg.click("#spk-upd button:first-of-type")
    pg.wait_for_selector("#newbit", timeout=8000); check(True, "after 'Update now' the page reloads with the new version")
    keys = pg.evaluate("caches.keys()"); check(keys == ["spk-newversion1"], f"old cache removed {keys}")
    check(not errs, "no page errors: " + "; ".join(errs[:3])); b.close()
print("\nALL OK" if not bad else "\nFAILED: " + "; ".join(bad)); raise SystemExit(1 if bad else 0)
