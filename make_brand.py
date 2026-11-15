"""Draws the Spektronautilus logo (the prism: one ray in, three rays out) and every icon made from it.
Run:  python3 make_brand.py      (needs Playwright's Chromium for the PNG icons)

Writes src/logo.svg (header), src/favicon.svg (tab), linux/spektronautilus.svg (app menu), docs/mixer-mobile/icon.svg,
src/icon-192.png, src/icon-512.png, src/apple-touch-icon.png and, when the iOS repository sits next to this one, its 1024 px app icon."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PURPLE, DEEP, WHITE = "#5a2496", "#3d0e7e", "#ffffff"


def mark(fill=PURPLE):
    """The prism and its rays inside a 64 x 64 box, centred on 32,32, drawn in the brand purple."""
    return (f'<path d="M30.7 21.5 L17.3 41 L44.1 41 Z" fill="{fill}"/>'
            f'<g fill="{fill}"><rect x="6.5" y="31.1" width="17" height="1.9"/>'
            f'<rect x="36.4" y="27.3" width="18.8" height="1.9"/><rect x="39.2" y="31.1" width="16" height="1.9"/>'
            f'<rect x="42" y="34.9" width="13.2" height="1.9"/></g>')


def badge():
    """Purple ring, white disc, purple prism: reads on light and dark backgrounds alike."""
    return f'<circle cx="32" cy="32" r="32" fill="{PURPLE}"/><circle cx="32" cy="32" r="27" fill="{WHITE}"/>' + mark()


def svg(body, box=64):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {box} {box}">{body}</svg>\n'


def tile(size=64, scale=0.78):
    """A square app icon: deep purple glow with the white disc and prism in the middle (inside the maskable safe zone)."""
    s = size * scale / 54          # the white disc is 54 units wide
    o = (size - 64 * s) / 2
    return (f'<defs><radialGradient id="g" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="{PURPLE}"/>'
            f'<stop offset="1" stop-color="{DEEP}"/></radialGradient></defs><rect width="{size}" height="{size}" fill="url(#g)"/>'
            f'<g transform="translate({o:.2f} {o:.2f}) scale({s:.4f})"><circle cx="32" cy="32" r="27" fill="{WHITE}"/>{mark()}</g>')


def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    print("wrote", p.relative_to(ROOT.parent))


def main():
    write(ROOT / "src" / "logo.svg", svg(badge()))
    write(ROOT / "src" / "favicon.svg", svg(badge()))
    write(ROOT / "linux" / "spektronautilus.svg", svg(badge()))
    write(ROOT / "docs" / "mixer-mobile" / "icon.svg", svg(tile(512), 512))
    pngs = [(ROOT / "src" / "icon-192.png", 192), (ROOT / "src" / "icon-512.png", 512), (ROOT / "src" / "apple-touch-icon.png", 180)]
    ios = ROOT.parent / "spektronautilus-ios" / "App" / "Resources" / "Assets.xcassets" / "AppIcon.appiconset" / "icon-1024.png"
    if ios.exists():
        pngs.append((ios, 1024))
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for path, n in pngs:
            pg = b.new_page(viewport={"width": n, "height": n})
            pg.set_content(f'<style>html,body{{margin:0}}svg{{display:block;width:{n}px;height:{n}px}}</style>' + svg(tile(n), n))
            pg.screenshot(path=str(path), omit_background=False)
            pg.close()
            print("wrote", path.relative_to(ROOT.parent), f"{n}x{n}")
        b.close()


if __name__ == "__main__":
    main()
