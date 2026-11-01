"""Draws the four logo proposals as SVG files plus an overview page: docs/logos/.
Run:  python3 make_logos.py      (the page is for choosing a logo, it is not part of the site menu)"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "docs" / "logos"
SPEC = ["#7a3cff", "#2b3af0", "#19c3e6", "#2fd39a", "#ffd23f", "#ff8a3d", "#ff3d81"]   # violet blue cyan green yellow orange pink
INK = "#14182b"
f = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")


def path(points, close=False):
    return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in points) + (" Z" if close else "")


def spiral(cx, cy, a, b, t0, t1, n=60, rot=0.0):
    pts = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        r = a * math.exp(b * t)
        pts.append((cx + r * math.cos(t + rot), cy + r * math.sin(t + rot)))
    return pts


# ------------------------------------------------------------------ A: Aperture. Seven spiral blades in spectrum colours, like a camera iris that is also a shell.
def logo_a():
    out = ['<defs></defs>']
    for i, c in enumerate(SPEC):
        rot = i * 2 * math.pi / 7
        pts = spiral(32, 32, 7.5, 0.5, 0.0, 2.45, 40, rot)
        out.append(f'<path d="{path(pts)}" fill="none" stroke="{c}" stroke-width="5.2" stroke-linecap="round"/>')
    return "".join(out)


# ------------------------------------------------------------------ B: Frames. Golden rectangles are video frames, each in a colour of the spectrum; a white arc runs through them like the shell.
def logo_b():
    sq = [(5, 0, 0, 0), (3, 5, 0, 1), (2, 6, 3, 2), (1, 5, 4, 3), (1, 5, 3, 4)]       # size, x, y, colour index
    S, ox, oy, gap = 6.6, 5.6, 15.2, 0.16
    o = []
    for s, x, y, c in sq:
        o.append(f'<rect x="{f(ox + (x + gap) * S)}" y="{f(oy + (y + gap) * S)}" width="{f((s - 2 * gap) * S)}" height="{f((s - 2 * gap) * S)}" rx="{f(S * .28)}" fill="{SPEC[[1, 2, 4, 5, 6][c]]}"/>')
    P = lambda x, y: (ox + x * S, oy + y * S)
    arcs = [((0, 5), (5, 0), 5, (5, 5)), ((5, 0), (8, 3), 3, (5, 3)), ((8, 3), (6, 5), 2, (6, 3)), ((6, 5), (5, 4), 1, (6, 4)), ((5, 4), (6, 3), 1, (6, 4))]
    d = ""
    for k, (a, b, r, c) in enumerate(arcs):
        (x1, y1), (x2, y2) = P(*a), P(*b)
        d += (f"M{f(x1)} {f(y1)} " if k == 0 else "") + f"A{f(r * S)} {f(r * S)} 0 0 1 {f(x2)} {f(y2)} "
    o.append(f'<path d="{d.strip()}" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" opacity=".95"/>')
    return "".join(o)


# ------------------------------------------------------------------ C: Pearls. Dots grow along a shell spiral and run through the colours of the spectrum.
def logo_c():
    n, dots = 22, []
    for i in range(n):
        t = 0.5 + i * 0.62
        r = 2.4 * math.exp(0.15 * t)
        dots.append((r * math.cos(t + 3.6), r * math.sin(t + 3.6), 0.255 * r + 0.4, SPEC[int(round(i / (n - 1) * (len(SPEC) - 1)))]))
    x0, x1 = min(x - r for x, y, r, c in dots), max(x + r for x, y, r, c in dots)
    y0, y1 = min(y - r for x, y, r, c in dots), max(y + r for x, y, r, c in dots)
    k = 54 / max(x1 - x0, y1 - y0); mx, my = 32 - k * (x0 + x1) / 2, 32 - k * (y0 + y1) / 2
    return "".join(f'<circle cx="{f(mx + k * x)}" cy="{f(my + k * y)}" r="{f(k * r)}" fill="{c}"/>' for x, y, r, c in dots)


# ------------------------------------------------------------------ D: Soundwave shell. A sound wave wound up into a nautilus. Blue to pink.
def logo_d():
    pts, n = [], 520
    for i in range(n + 1):
        t = 2.2 + 11.0 * i / n
        r = 3.0 * math.exp(0.13 * t) * (1 + 0.075 * math.sin(t * 9.0) * min(1, i / 120))
        pts.append((r * math.cos(t + 2.4), r * math.sin(t + 2.4)))
    x0, x1, y0, y1 = min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)
    k = 52 / max(x1 - x0, y1 - y0); mx, my = 32 - k * (x0 + x1) / 2, 32 - k * (y0 + y1) / 2
    pts = [(mx + k * x, my + k * y) for x, y in pts]
    return (f'<defs><linearGradient id="gd" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{SPEC[1]}"/><stop offset=".55" stop-color="{SPEC[0]}"/><stop offset="1" stop-color="{SPEC[6]}"/></linearGradient></defs>'
            f'<path d="{path(pts)}" fill="none" stroke="url(#gd)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')


LOGOS = [
    ("a", "Blenderen", "Sju spiralblader i spekterets farger. Det er både en kameraåpning (blenderen i et kamera) og et nautilusskall. Mest «Spektro».", logo_a),
    ("b", "Rammene", "Gyllent snitt bygd av videorammer, hver i en farge fra spekteret, med en hvit spiral gjennom. Mest «video».", logo_b),
    ("c", "Perlene", "Prikker som vokser langs et skall og går gjennom alle regnbuens farger. Rolig, enkelt og lett å kjenne igjen i liten størrelse.", logo_c),
    ("d", "Lydskallet", "En lydbølge som er surret opp til et nautilusskall, fra blått til rosa. Mest «musikk», og nærmest dagens logo.", logo_d),
]
CURRENT = ('<defs><linearGradient id="gc" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2b3af0"/><stop offset="1" stop-color="#ff3d81"/></linearGradient></defs>'
           '<path d="M32 8a24 24 0 1 1-24 24c0-13 10-20 21-20 10 0 17 7 17 16 0 8-6 13-13 13-6 0-10-4-10-9 0-4 3-7 7-7 3 0 5 2 5 4" fill="none" stroke="url(#gc)" stroke-width="5" stroke-linecap="round"/>')


def svg(inner, tile=False, size=None):
    wh = f' width="{size}" height="{size}"' if size else ""
    bg = f'<rect width="64" height="64" rx="14" fill="{INK}"/>' if tile else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"{wh}>{bg}{inner}</svg>'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for key, name, _, fn in LOGOS:
        (OUT / f"logo-{key}.svg").write_text(svg(fn()), encoding="utf-8")
        (OUT / f"logo-{key}-tile.svg").write_text(svg(fn(), tile=True), encoding="utf-8")
    cards = []
    for key, name, why, fn in [("0", "Dagens logo", "For sammenligning: én spiral med blå-rosa gradient.", lambda: CURRENT)] + LOGOS:
        inner = fn()
        # every inline copy needs its own gradient ids, so the copies do not share (or lose) a gradient
        def sv(extra, tile=False, size=None):
            s = svg(inner, tile, size)
            return s.replace('id="gd"', f'id="gd{extra}"').replace('url(#gd)', f'url(#gd{extra})').replace('id="gc"', f'id="gc{extra}"').replace('url(#gc)', f'url(#gc{extra})')
        label = "" if key == "0" else f'<span class="k">{key.upper()}</span>'
        cards.append(f'''<section class="opt{' cur' if key == '0' else ''}"><h2>{label}{name}</h2><p class="why">{why}</p>
<div class="row"><div class="pane light">{sv(key + "l", size=150)}</div><div class="pane dark">{sv(key + "d", size=150)}</div><div class="pane tile">{sv(key + "t", tile=True, size=150)}</div></div>
<div class="row small"><div class="lock light">{sv(key + "w", size=40)}<b>Spektronautilus</b></div><div class="lock dark">{sv(key + "x", size=40)}<b>Spektronautilus</b></div>
<div class="fav"><span>{sv(key + "f", tile=True, size=32)}</span><span>{sv(key + "g", tile=True, size=16)}</span><small>32 og 16 px (fanen i nettleseren)</small></div></div></section>''')
    page = f'''<!DOCTYPE html>
<html lang="nb"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Logoforslag – Spektronautilus</title>
<style>
:root{{--bg:#f3f4f8;--ink:#14182b;--mute:#5a607a;--line:#d5d8e6;--panel:#fff;--b:#ff3d81;color-scheme:light}}
@media (prefers-color-scheme:dark){{:root{{--bg:#10122a;--ink:#eceefb;--mute:#a0a6c8;--line:#2a2e57;--panel:#171a3a;--b:#ff6fa3;color-scheme:dark}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
.wrap{{max-width:1000px;margin:0 auto;padding:24px 16px 60px}}h1{{margin:0 0 4px;font-size:2rem;letter-spacing:-.03em}}.lead{{color:var(--mute);margin:0 0 22px;max-width:46em}}
.opt{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;margin:0 0 18px}}.opt.cur{{opacity:.85}}
h2{{margin:0 0 2px;font-size:1.2rem;display:flex;gap:10px;align-items:center}}.k{{display:inline-grid;place-items:center;width:30px;height:30px;border-radius:50%;background:var(--ink);color:var(--bg);font-weight:800}}
.why{{margin:0 0 12px;color:var(--mute)}}.row{{display:flex;flex-wrap:wrap;gap:12px;align-items:center}}.row.small{{margin-top:12px}}
.pane{{display:grid;place-items:center;padding:14px;border-radius:12px;border:1px solid var(--line)}}.light{{background:#fff;color:#14182b}}.dark{{background:#10122a;color:#eceefb}}.tile{{background:#e9ebf3}}
.lock{{display:flex;gap:10px;align-items:center;padding:8px 16px;border-radius:12px;border:1px solid var(--line)}}.lock b{{font-size:1.25rem;letter-spacing:-.02em}}
.fav{{display:flex;gap:10px;align-items:center}}.fav small{{color:var(--mute)}}.fav span{{display:inline-block;line-height:0}}
.how{{color:var(--mute);font-size:.93rem}}
</style></head><body><div class="wrap">
<h1>Fire logoforslag</h1>
<p class="lead">Alle tar utgangspunkt i navnet: <b>spekter</b> (fargene) og <b>nautilus</b> (skallet, spiralen). Hvert forslag vises på lys og mørk bunn, som app-ikon, ved siden av navnet og i fanestørrelse. Gi beskjed om hvilken du liker best, eller hva du vil blande.</p>
{"".join(cards)}
<p class="how">Filene ligger i <code>docs/logos/</code> som <code>logo-a.svg</code> til <code>logo-d.svg</code>, og <code>-tile.svg</code> for versjonen med mørk, avrundet bunn (app-ikon og favicon).</p>
</div></body></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
