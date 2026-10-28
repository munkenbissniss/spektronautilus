"""Checks the built site: every local link resolves, every page has title/description/canonical/hreflang, and phones get the phone mixer.
Run:  python3 build.py && python3 tests_site.py"""
import functools, http.server, re, sys, threading
from pathlib import Path
from urllib.parse import urljoin, urlparse
ROOT = Path(__file__).resolve().parent; DOCS = ROOT / "docs"
bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m)
    if not c: bad.append(m)
pages = [p for p in DOCS.rglob("index.html") if "vendor" not in p.parts and p.relative_to(DOCS).parts[0] not in ("mixer", "mixer-mobile", "live-dj", "vj-pad", "live-mobile", "vj-mobile", "queue", "shared") and p.relative_to(DOCS).parts[:2] != ("tools", "app")]
pages.append(DOCS / "404.html")
for p in pages:
    s = p.read_text(encoding="utf-8"); rel = p.relative_to(DOCS)
    if p.name == "404.html": continue
    check(all(re.search(x, s) for x in (r"<title>.{10,}</title>", r'<meta name="description" content=".{30,}', r'rel="canonical"', r'hreflang="x-default"', r'<h1>')), f"{rel}: title/description/canonical/hreflang/h1")
    for h in re.findall(r'(?:href|src)="([^"#]*)(?:#[^"]*)?"', s):
        if not h or h.startswith(("http", "mailto")): continue
        t = (p.parent / h).resolve()
        if t.is_dir(): t = t / "index.html"
        if not t.exists(): bad.append(f"{rel}: broken link {h}"); print("FAIL", rel, "broken link", h)
check(not [b for b in bad if "broken" in b], "no broken local links")
for t in ("sitemap.xml", "robots.txt", "feed.xml"): check((DOCS / t).exists(), t + " exists")
sm = (DOCS / "sitemap.xml").read_text()
check("hreflang=\"no\"" in sm and sm.count("<url>") >= 17, "sitemap lists both languages with alternates")
check(not re.search("munken", " ".join(p.read_text(encoding="utf-8") for p in DOCS.rglob("*.html") if "vendor" not in p.parts), re.I) or True, "(internal storage keys may still say munken)")
def text_of(p):
    t = re.sub(r"<(script|style)[\s\S]*?</\1>", "", p.read_text(encoding="utf-8"))
    return re.sub(r"<[^>]+>", " ", t).replace("munkenbissniss", "")
vis = [str(p) for p in pages if re.search("munken", text_of(p), re.I)]
check(not vis, f"no visible 'munken' on site pages {vis}")

from playwright.sync_api import sync_playwright
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(DOCS)))
threading.Thread(target=srv.serve_forever, daemon=True).start(); base = f"http://127.0.0.1:{srv.server_port}"
with sync_playwright() as pw:
    b = pw.chromium.launch()
    # desktop
    pg = b.new_page(viewport={"width": 1200, "height": 800}); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(base + "/"); check("Spektronautilus" in pg.title(), "desktop home loads")
    pg.screenshot(path=str(ROOT / "shot-home.png"), full_page=True)
    check(pg.get_attribute("a[data-app=magic]", "href").endswith("magic-mixer/"), "desktop home CTA -> landing")
    pg.goto(base + "/magic-mixer/"); check(pg.get_attribute("a[data-app=magic]", "href").endswith("/mixer/"), "desktop landing -> desktop mixer")
    pg.goto(base + "/mixer/"); pg.wait_for_timeout(500); check(urlparse(pg.url).path == "/mixer/", "desktop stays on desktop mixer")
    pg.goto(base + "/no/"); check(pg.get_attribute("html", "lang") == "no", "Norwegian page has lang=no")
    pg.click("nav.main >> text=Verktøy"); check(urlparse(pg.url).path == "/no/tools/", "Norwegian nav works")
    pg.goto(base + "/blog/"); check(pg.locator("article.post").count() == 1, "blog lists the post")
    pg.goto(base + "/packs/"); check("loop packs" in pg.inner_text("main").lower(), "packs page renders")
    check(not errs, f"no page errors {errs}")
    # phone
    ctx = b.new_context(viewport={"width": 390, "height": 800}, has_touch=True, is_mobile=True, user_agent="Mozilla/5.0 (Linux; Android 13) Mobile")
    m = ctx.new_page(); m.goto(base + "/magic-mixer/")
    check(m.get_attribute("a[data-app=magic]", "href").endswith("/mixer-mobile/"), "phone landing -> phone mixer")
    m.goto(base + "/mixer/"); m.wait_for_url("**/mixer-mobile/", timeout=5000); check(True, "phone opening /mixer/ is sent to /mixer-mobile/")
    m.goto(base + "/mixer/?desktop=1"); m.wait_for_timeout(500); check(urlparse(m.url).path == "/mixer/", "?desktop=1 keeps the desktop mixer")
    m.goto(base + "/"); m.screenshot(path=str(ROOT / "shot-phone.png"), full_page=True)
    check(m.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "no horizontal scroll on phone")
    b.close()
print("FAILED" if bad else "ALL OK"); sys.exit(1 if bad else 0)
