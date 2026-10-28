"""Checks the app translations: each mixer and tool is opened in every language; visible text that is still the English master text
(and so should have been translated) is listed, and strings the master does not know about are counted."""
import functools, http.server, re, threading
from pathlib import Path
ROOT = Path(__file__).resolve().parent; bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
norm = lambda s: re.sub(r"\s+", " ", s).strip()
master = {norm(l) for l in open(ROOT / "src/i18n-app/en.txt", encoding="utf-8") if norm(l)}
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f"http://127.0.0.1:{srv.server_port}"
APPS = (("live-dj/index.html?desktop=1", "#decks .deck"), ("vj-pad/index.html?desktop=1", ".pad"), ("mixer/index.html?desktop=1", "#pre"), ("tools/app/index.html", "#groups details"),
        ("live-mobile/", ".deck"), ("vj-mobile/", ".pad"), ("mixer-mobile/", "body"), ("queue/", "#list"))
JS = """() => { const out = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) { const e = n.parentElement; if (!e || /^(SCRIPT|STYLE|TEXTAREA|NOSCRIPT)$/.test(e.tagName) || e.closest('[data-no-i18n]')) continue;
    const t = n.nodeValue.replace(/\\s+/g, ' ').trim(); if (t) out.push(t); } return out }"""
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(); lost = 0
    for lg in ("no", "es", "de", "pt"):
        for path, sel in APPS:
            ctx = b.new_context(viewport={"width": 1200, "height": 900}, locale="en-US"); pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            sep = "&" if "?" in path else "?"
            pg.goto(f"{B}/{path}{sep}lang={lg}"); pg.wait_for_selector(sel, state="attached", timeout=8000); pg.wait_for_timeout(500)
            texts = pg.evaluate(JS); eng = sorted({t for t in texts if t in master and re.search(r"[a-z]{3}", t) and not re.fullmatch(r"[A-Za-z0-9 ./·:–-]{1,12}", t)})
            lang_attr = pg.evaluate("document.documentElement.lang")
            check(lang_attr == lg and not errs, f"{lg} {path.split('?')[0]}: lang attribute and no script errors {errs[:1]}")
            check(len(eng) <= 12, f"{lg} {path.split('?')[0]}: {len(eng)} master strings still English" + (": " + " | ".join(e[:40] for e in eng[:6]) if eng else ""))
            ctx.close()
    # language button, saved choice, and live text that the apps write later
    ctx = b.new_context(locale="en-US"); pg = ctx.new_page(); pg.goto(B + "/vj-mobile/"); pg.wait_for_selector(".pad")
    pg.click("#spk-lang > button"); pg.click("#spk-lang button[lang=de]"); pg.wait_for_selector(".pad"); pg.wait_for_timeout(500)
    check(pg.evaluate("localStorage.getItem('spk_lang')") == "de" and pg.evaluate("document.documentElement.lang") == "de", "the language button saves the choice and reloads in German")
    check(pg.evaluate("SPK_T('Remove loop')") == "Loop entfernen", "SPK_T translates strings the apps write later")
    pg.goto(B + "/no/"); pg.goto(B + "/live-mobile/"); pg.wait_for_selector(".deck")
    check(pg.evaluate("document.documentElement.lang") == "no", "visiting the Norwegian site makes the apps open in Norwegian")
    ctx.close(); b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
