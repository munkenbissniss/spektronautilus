"""No horizontal scrolling at 320 px (iPhone SE) on any page or app, in every language, and the header language menu works."""
import subprocess, sys, time, json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent; bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
PAGES = ["", "tools/", "packs/", "guides/", "guides/start/", "guides/tools/", "guides/video-dj/", "guides/offline-linux/", "guides/help/", "about/", "queue/",
         "tools/app/", "mixer/", "mixer-mobile/", "live-dj/", "live-mobile/", "vj-pad/", "vj-mobile/"]
LANGS = ["", "no/", "es/", "de/", "pt/"]
sv = subprocess.Popen([sys.executable, "-m", "http.server", "8795", "--directory", str(ROOT / "docs")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
JS = """() => { const W = document.documentElement.clientWidth, out = [];
  for (const el of document.querySelectorAll('body *')) { const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    const cs = getComputedStyle(el); if (cs.position === 'fixed' && r.right <= W + 1 && r.left >= -1) continue;
    let p = el, clipped = false; while ((p = p.parentElement) && p !== document.body) { const o = getComputedStyle(p); if (/(auto|scroll|hidden|clip)/.test(o.overflowX) && p.getBoundingClientRect().right <= W + 1) { clipped = true; break; } }
    if (!clipped && r.right > W + 1) out.push(el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\\s+/).join('.') : '') + ' ' + Math.round(r.right)); }
  return { sw: document.documentElement.scrollWidth, W, out: out.slice(0, 5) }; }"""
try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(); ctx = b.new_context(viewport={"width": 320, "height": 640}, has_touch=True, is_mobile=True, service_workers="block")
        pg = ctx.new_page()
        for lg in LANGS:
            for p in PAGES:
                if p == "queue/" and lg: continue
                url = f"http://127.0.0.1:8795/{lg}{p}"
                try:
                    pg.add_init_script(f"try{{localStorage.setItem('spk_lang','{lg.strip('/') or 'en'}');localStorage.setItem('spk_desktop','1')}}catch(e){{}}")
                    pg.goto(url, wait_until="load"); pg.wait_for_timeout(500)
                except Exception as e: check(False, f"{url} did not load: {e}"); continue
                r = pg.evaluate(JS); check(r["sw"] <= r["W"] and not r["out"], f"{lg or 'en/'}{p}: scrollWidth {r['sw']}/{r['W']} {r['out']}")
        # header menu
        pg.goto("http://127.0.0.1:8795/no/tools/"); pg.wait_for_timeout(300)
        check(pg.locator(".ld .ddm").is_hidden(), "language menu is closed at first")
        box = pg.locator(".ld .ddb").bounding_box(); check(box["x"] + box["width"] > 250, f"language button sits to the right ({box['x']:.0f})")
        pg.click(".ld .ddb"); check(pg.locator(".ld .ddm a").count() == 5 and pg.locator(".ld .ddm").is_visible(), "menu opens with 5 languages")
        r = pg.evaluate(JS); check(r["sw"] <= r["W"], "open menu does not widen the page")
        pg.click(".ld .ddm a[hreflang=de]"); pg.wait_for_url("**/de/tools/"); check(True, "choosing German goes to /de/tools/")
        b.close()
finally: sv.terminate()
print("\nALL OK" if not bad else "\nFAILED: " + "; ".join(bad[:15])); raise SystemExit(1 if bad else 0)
