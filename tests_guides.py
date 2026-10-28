"""Guides and feedback: every guide exists in all five languages with working links, the apps link to their guide in the chosen
language, and the Feedback form builds a mail to the right address without letting keys reach the mixer.
Run:  python3 build.py && python3 tests_guides.py"""
import functools, http.server, re, threading, urllib.parse
from pathlib import Path
ROOT = Path(__file__).resolve().parent; DOCS = ROOT / "docs"
bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m)
    if not c: bad.append(m)
SLUGS = ["start", "magic-mixer", "video-dj", "vj-mixer", "tools", "queue", "show-check", "offline-linux", "help"]
for lang in ("", "no/", "es/", "de/", "pt/"):
    miss = [s for s in SLUGS if not (DOCS / lang / "guides" / s / "index.html").exists()]
    check(not miss and (DOCS / lang / "guides" / "index.html").exists(), f"/{lang}guides: index and nine guides exist {miss}")
    for s in SLUGS:
        p = DOCS / lang / "guides" / s / "index.html"; h = p.read_text(encoding="utf-8")
        for l in re.findall(r'href="([^"#]*)(#[^"]*)?"', h):
            if not l[0] or l[0].startswith(("http", "mailto")): continue
            t = (p.parent / l[0]).resolve(); t = t / "index.html" if t.is_dir() else t
            if not t.exists(): bad.append(f"{lang}{s}: broken {l[0]}"); print("FAIL broken link", lang, s, l[0])
        ids = set(re.findall(r'id="([^"]+)"', h))
        for l in re.findall(r'href="([^"]*guides/[^"]*)#([\w-]+)"', h):
            t = (p.parent / l[0]).resolve() / "index.html"
            if t.exists() and f'id="{l[1]}"' not in t.read_text(encoding="utf-8"): bad.append(f"{lang}{s}: anchor #{l[1]} missing in {l[0]}"); print("FAIL anchor", lang, s, l)
        for l in re.findall(r'href="(@[^"]*)"', h): bad.append(f"unresolved link {l}")
check(not [b for b in bad if "anchor" in b or "unresolved" in b or "broken" in b], "no broken links, anchors or unresolved @links in any guide")
allhtml = " ".join(p.read_text(encoding="utf-8") for p in DOCS.rglob("*.html") if "vendor" not in p.parts)
check("blog" not in re.sub(r"<(script|style)[\s\S]*?</\1>", "", allhtml).lower().replace("blogging", ""), "no blog left in the pages")
check("tutamail" not in allhtml and "oyvind.dahl" not in allhtml, "the mail address is not written in any page")

from playwright.sync_api import sync_playwright
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(DOCS)))
threading.Thread(target=srv.serve_forever, daemon=True).start(); B = f"http://127.0.0.1:{srv.server_port}"
APPS = [("mixer/", "magic-mixer"), ("mixer-mobile/", "magic-mixer"), ("live-dj/", "video-dj"), ("live-mobile/", "video-dj"), ("vj-pad/", "vj-mixer"), ("vj-mobile/", "vj-mixer"), ("tools/app/", "tools"), ("queue/", "queue")]
with sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for lang, prefix in (("en", ""), ("no", "no/"), ("de", "de/")):
        ctx = b.new_context(viewport={"width": 1100, "height": 800}); ctx.add_init_script(f"localStorage.setItem('spk_lang','{lang}'); localStorage.setItem('spk_desktop','1')")
        for path, g in APPS:
            pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(path + str(e)))
            pg.goto(B + "/" + path + ("?desktop=1" if "mobile" not in path else "")); pg.wait_for_selector("[data-spk-feedback]", timeout=8000)
            a = pg.locator(".spkx a"); href = a.get_attribute("href") if a.count() else ""
            check(href == f"{B}/{prefix}guides/{g}/", f"{lang} {path}: Guide link goes to {prefix}guides/{g}/ ({href})")
            if lang == "en" and path == "mixer/":
                check(pg.locator(".spkx-fix").count() == 0, f"{path}: the links sit in the header, not floating over the app")
            pg.close()
        ctx.close()
    ctx = b.new_context(viewport={"width": 1100, "height": 800}); ctx.add_init_script("localStorage.setItem('spk_lang','no'); localStorage.setItem('spk_desktop','1'); document.addEventListener('click', function(e){var a=e.target.closest && e.target.closest('a[href^=\"mailto:\"]'); if(a){window.__mail=a.href; e.preventDefault();}}, true); window.__keys=0; document.addEventListener('keydown', function(){window.__keys++});")
    pg = ctx.new_page(); pg.goto(B + "/vj-pad/index.html?desktop=1"); pg.wait_for_selector(".pad")
    pg.click("[data-spk-feedback]"); check(pg.locator("#spkx-m").count() == 1 and "Send tilbakemelding" in pg.inner_text("#spkx-m h2"), "Feedback form opens in Norwegian")
    pg.click("[data-x=send]"); check(pg.evaluate("window.__mail") is None and "Skriv en melding" in pg.inner_text("#spkx-m .hint"), "an empty message is not sent")
    pg.fill("#spkx-s", "Hei qwer"); pg.type("#spkx-s", " asdf"); pg.fill("#spkx-r", "meg@example.com")
    check(pg.evaluate("window.__keys") == 0, "typing in the form never reaches the mixer's keyboard handlers")
    pg.select_option("#spkx-k", "1"); pg.click("[data-x=send]")
    mail = pg.evaluate("window.__mail"); u = urllib.parse.urlparse(mail); q = urllib.parse.parse_qs(u.query)
    check(u.path == "oyvind.dahl@tutamail.com" and "Noe er ødelagt" in q["subject"][0], f"mail goes to the right address with a subject ({u.path} {q.get('subject')})")
    body = q["body"][0]; check("Hei qwer asdf" in body and "Reply to: meg@example.com" in body and "/vj-pad/" in body and "Browser:" in body, "mail body has the message, the reply address and the page and browser")
    check(pg.locator("#spkx-m .fail").is_visible() and pg.locator("#spkx-m .fail button").count() == 1, "a copy fallback is shown after sending")
    pg.keyboard.press("Escape"); check(pg.locator("#spkx-m").count() == 0, "Escape closes the form")
    check(not errs, f"no page errors {errs}")
    # the site pages carry the button in the footer
    pg.goto(B + "/no/guides/help/"); pg.wait_for_selector("footer [data-spk-feedback]"); pg.click(".gfb [data-spk-feedback]"); check(pg.locator("#spkx-m").count() == 1, "the feedback box on a guide opens the form")
    # menu: mixers in a dropdown, About and Queue in the footer, queue panel and to-top button
    pg.goto(B + "/"); nav = pg.inner_text("nav.main")
    check("About" not in nav and "Queue" not in nav and pg.locator("nav.main > a").count() == 4, f"main menu is short: {nav!r}")
    check(pg.locator(".dd .ddm").is_hidden(), "the Mixers menu starts closed"); pg.click(".dd .ddb"); check(pg.locator(".dd .ddm a").count() == 3 and pg.locator(".dd .ddm").is_visible(), "the Mixers menu opens with three mixers")
    pg.keyboard.press("Escape"); check(pg.locator(".dd .ddm").is_hidden(), "Escape closes the menu")
    check(pg.locator("footer .fcols a", has_text="About").count() == 1 and pg.locator("footer .fcols a", has_text="Queue").count() == 1, "About and Queue are in the footer")
    pg.goto(B + "/guides/tools/"); check(not pg.locator(".spkdock .up").is_visible(), "no to-top button at the top")
    pg.evaluate("window.scrollTo(0, 1500)"); pg.wait_for_timeout(500); check(pg.locator(".spkdock .up").is_visible(), "to-top button appears after scrolling")
    pg.click(".spkdock .up"); pg.wait_for_function("scrollY < 5", timeout=5000); check(True, "to-top button scrolls up")
    pg.click(".spkdock >> text=Queue"); pg.wait_for_selector("#spkq iframe"); fr = pg.frame_locator("#spkq iframe"); fr.locator("#list").wait_for(timeout=5000)
    check(pg.locator("#spkq").is_visible() and fr.locator("h1").is_hidden(), "Queue opens as a panel at the bottom of any page")
    pg.keyboard.press("Escape"); check(pg.locator("#spkq").is_hidden(), "Escape closes the queue panel")
    pg.goto(B + "/queue/"); check(pg.locator("h1").is_visible(), "the full queue page still exists")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
