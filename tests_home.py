"""Front page: every card and link leads somewhere that exists, in all five languages, and the page fits a phone."""
import functools, http.server, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent; bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f"http://127.0.0.1:{srv.server_port}"
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context(viewport={"width": 1100, "height": 900}).new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    for lang in ("", "no/", "es/", "de/", "pt/"):
        pg.goto(f"{B}/{lang}"); pg.wait_for_selector("h1")
        hrefs = pg.eval_on_selector_all("main a[href]", "els => els.map(a => a.href)")
        goals = pg.locator("a.goal").count(); kit = pg.locator("a.kit").count(); flow = pg.locator("ol.flow li").count()
        check(goals == 6 and kit == 12 and flow == 4, f"/{lang}: 6 goals, 12 tools, 4 steps ({goals}/{kit}/{flow})")
        dead = []
        for h in sorted(set(x.split("#")[0] for x in hrefs if x.startswith(B))):
            r = pg.request.get(h)
            if r.status != 200: dead.append((h, r.status))
        check(not dead, f"/{lang}: every link works {dead[:3]}")
        check(pg.locator("main a[href*='tools/hospital']").count() >= 2, f"/{lang}: the Loop Hospital can be reached")
        check(pg.evaluate("document.documentElement.lang") == (lang.strip("/") or "en"), f"/{lang}: language set")
    ph = b.new_context(viewport={"width": 320, "height": 640}).new_page()
    for lang in ("", "de/", "no/"):
        ph.goto(f"{B}/{lang}"); check(ph.evaluate("document.documentElement.scrollWidth - innerWidth") <= 0, f"/{lang} fits 320 px")
    check(not errs, f"no script errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
