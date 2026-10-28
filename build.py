#!/usr/bin/env python3
"""Builds the Spektronautilus site into docs/.

Pages are generated from i18n/<lang>.py (texts), content/blog/*.md (posts) and data/packs.json (loop packs).
English lives at the root, other languages in /<lang>/. Every page gets hreflang links, a canonical URL,
Open Graph tags and structured data, and the build writes sitemap.xml, robots.txt, feed.xml and 404.html.
To add a language: copy i18n/en.py to i18n/<code>.py, translate it, run  python3 build.py.
"""
import html, importlib.util, json, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = json.loads((ROOT / "site.json").read_text())["url"].rstrip("/") + "/"
SLUGS = {"home": "", "magic": "magic-mixer/", "live": "live-mixer/", "vj": "vj-mixer/", "tools": "tools/", "packs": "packs/", "blog": "blog/", "about": "about/"}
NAV = ["home", "magic", "live", "vj", "tools", "packs", "blog", "about"]
e = html.escape


def load_langs():
    langs = {}
    for f in sorted((ROOT / "i18n").glob("*.py")):
        spec = importlib.util.spec_from_file_location("t_" + f.stem, f)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        langs[m.T["lang"]] = m.T
    if "en" not in langs:
        sys.exit("i18n/en.py is required")
    return dict(sorted(langs.items(), key=lambda kv: kv[0] != "en"))


def prefix(lang):
    return "" if lang == "en" else lang + "/"


def depth_root(lang, path):      # relative path from a page back to docs/
    n = (0 if lang == "en" else 1) + path.strip("/").count("/") + (1 if path.strip("/") else 0)
    return "../" * n


def url(lang, path):
    return SITE + prefix(lang) + path


def md(text):
    out, para, ul = [], [], []
    def inline(s):
        s = e(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
        return re.sub(r"\[(.+?)\]\((https?://[^)\s]+|/[^)\s]*|[\w./#-]+)\)", r'<a href="\2">\1</a>', s)
    def flush():
        nonlocal para, ul
        if para: out.append("<p>" + inline(" ".join(para)) + "</p>"); para = []
        if ul: out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in ul) + "</ul>"); ul = []
    for line in text.splitlines():
        if not line.strip(): flush()
        elif line.startswith("## "): flush(); out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("- "): 
            if para: flush()
            ul.append(line[2:])
        else:
            if ul: flush()
            para.append(line.strip())
    flush()
    return "\n".join(out)


def posts():
    res = []
    for f in sorted((ROOT / "content" / "blog").glob("*.md"), reverse=True):
        m = re.match(r"(.+)\.(\w\w)$", f.stem)
        if not m: continue
        slug, lang = m.groups()
        raw = f.read_text(encoding="utf-8")
        fm, body = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S).groups()
        meta = dict(l.split(": ", 1) for l in fm.splitlines() if ": " in l)
        res.append({"slug": slug, "lang": lang, "title": meta["title"], "date": meta["date"], "html": md(body), "text": re.sub(r"\s+", " ", body).strip()})
    return res


STYLE = (ROOT / "src" / "style.css").read_text()
LOGO = (ROOT / "src" / "logo.svg").read_text().strip()
# Phones are sent to the phone version of an app. ?desktop=1 turns that off.
MOBILE_JS = """(function(){try{var q=location.search.indexOf('desktop=1')>-1;if(q)localStorage.setItem('spk_desktop','1');
var m=!localStorage.getItem('spk_desktop')&&matchMedia('(pointer:coarse) and (max-width:900px)').matches;if(!m)return;
var map=[[/(^|\\/)mixer\\/$/,'$1mixer-mobile/'],[/(^|\\/)live-dj\\/$/,'$1live-mobile/'],[/(^|\\/)vj-pad\\/$/,'$1vj-mobile/']];
document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll('a[data-app]').forEach(function(a){map.forEach(function(r){a.href=a.href.replace(r[0],r[1])})})})}catch(e){}})();"""


# shows how many jobs are running in the Queue link (the tools and mixers write the count to localStorage)
QBADGE_JS = """document.addEventListener('DOMContentLoaded',function(){function u(){try{var o=JSON.parse(localStorage.getItem('spk_q')||'{}'),n=Date.now()-(o.t||0)<30000?o.n||0:0;document.querySelectorAll('.qn').forEach(function(b){b.hidden=!n;b.textContent=n})}catch(e){}}u();addEventListener('storage',u);setInterval(u,4000)});"""


def render(lang, L, key, body_html, title, desc, extra_ld=None, path=None, alt=None, og_type="website", noindex=False):
    path = SLUGS[key] if path is None else path
    r = depth_root(lang, path)
    rl = r + prefix(lang)                       # root of this language
    nav = "".join(f'<a href="{rl}{SLUGS[k]}"{" aria-current=page" if k == key else ""}>{e(L["nav"][k])}</a>' for k in NAV)
    nav += f'<a href="{r}queue/" class="qlink">{e(L["nav"]["queue"])}<span class="qn" hidden></span></a>'
    alts = alt if alt is not None else {lg: path for lg in LANGS}
    sw = "".join(f'<a href="{r}{prefix(lg)}{p}" hreflang="{lg}" lang="{lg}"{" aria-current=true" if lg == lang else ""}>{e(LANGS[lg]["label"])}</a>' for lg, p in alts.items()) if len(alts) > 1 else ""
    hre = "".join(f'<link rel="alternate" hreflang="{lg}" href="{url(lg, p)}">' for lg, p in alts.items())
    if "en" in alts: hre += f'<link rel="alternate" hreflang="x-default" href="{url("en", alts["en"])}">'
    canon = url(lang, path)
    ld = json.dumps([{"@context": "https://schema.org", "@type": "WebSite", "name": "Spektronautilus", "url": SITE, "inLanguage": lang}] + (extra_ld or []), ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="canonical" href="{canon}">
{hre}
<meta property="og:site_name" content="Spektronautilus"><meta property="og:type" content="{og_type}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canon}"><meta property="og:locale" content="{L['locale']}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#14182b">
<link rel="icon" href="{r}favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="Spektronautilus blog" href="{SITE}feed.xml">
<style>{STYLE}</style>
<script type="application/ld+json">{ld}</script>
<script>{MOBILE_JS}</script>
<script>{QBADGE_JS}</script>
</head>
<body>
<a href="#main" class="sr" style="position:absolute;left:-999px">{e(L['ui']['skip'])}</a>
<header class="top"><div class="wrap">
<a class="brand" href="{rl}">{LOGO}<span>Spektronautilus</span></a>
<nav class="main" aria-label="Main">{nav}</nav>
<div class="lang" role="navigation" aria-label="{e(L['ui']['lang'])}">{sw}</div>
</div></header>
<main id="main"><div class="wrap">
{body_html}
</div></main>
<footer><div class="wrap"><span>{e(L['ui']['footer'])}</span><span>© Spektronautilus · MIT</span></div></footer>
</body></html>
"""


def write(rel, text):
    p = DOCS / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def page_body(L, key, r, P):
    ui = L["ui"]
    head = ""
    if key == "home":
        head = f'<section class="hero"><div class="tag">{e(P["tag"])}</div><h1>{e(P["h1"])}</h1><p class="lead">{e(P["lead"])}</p></section>'
    else:
        head = f'<h1>{e(P["h1"])}</h1><p class="lead">{e(P["lead"])}</p>'
    rl = r + prefix(L["lang"])
    body = re.sub(r"\{r\}(magic-mixer|live-mixer|vj-mixer|packs|blog|about)/", lambda m: rl + m.group(1) + "/", P["body"])
    body = re.sub(r"\{r\}tools/(?!app)", lambda m: rl + "tools/", body)
    body = body.replace("{r}", r).replace("{devnote}", e(ui["devnote"]))
    if key == "packs":
        data = json.loads((ROOT / "data" / "packs.json").read_text(encoding="utf-8"))["packs"]
        if not data: body = f'<p class="note">{e(ui["nopacks"])}</p>'
        else:
            cards = []
            for p in data:
                d = p.get("desc_" + L["lang"]) or p.get("desc", "")
                meta = " · ".join(x for x in (p.get("clips") and f'{p["clips"]} clips', p.get("size")) if x)
                cards.append(f'<div class="card pack"><div><h3>{e(p["title"])}</h3><p>{e(d)}</p><p class="mute">{e(meta)}</p></div><a class="btn main" href="{e(p["url"])}" rel="noopener">{e(ui["download"])}</a></div>')
            body = '<div class="cards" style="grid-template-columns:1fr">' + "".join(cards) + "</div>"
    return head + body


def main():
    global LANGS
    LANGS = load_langs()
    ps = posts()
    sitemap = []
    for lang, L in LANGS.items():
        for key in NAV:
            P = L["pages"][key]
            path = SLUGS[key]
            r = depth_root(lang, path)
            body = page_body(L, key, r, P)
            ld = []
            if key == "magic":
                ld.append({"@context": "https://schema.org", "@type": "WebApplication", "name": "Magic Video Mixer", "applicationCategory": "MultimediaApplication", "operatingSystem": "Any (modern browser)",
                           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "description": P["desc"], "inLanguage": lang, "url": url(lang, path)})
            if key == "blog":
                mine = [p for p in ps if p["lang"] == lang]
                items = "".join(f'<article class="card post" style="margin:10px 0"><h3><a href="{r}{prefix(lang)}blog/{p["slug"]}/">{e(p["title"])}</a></h3><time datetime="{p["date"]}">{p["date"]}</time><p>{e(p["text"][:200])}…</p></article>' for p in mine)
                body += items or f'<p class="note">{e(L["ui"]["noposts"])}</p>'
            write(prefix(lang) + path + "index.html", render(lang, L, key, body, P["title"], P["desc"], ld))
            sitemap.append(path)
        # blog posts
        for p in [p for p in ps if p["lang"] == lang]:
            path = f"blog/{p['slug']}/"
            r = depth_root(lang, path)
            alt = {p2["lang"]: path for p2 in ps if p2["slug"] == p["slug"]}
            body = f'<article class="post"><h1>{e(p["title"])}</h1><time datetime="{p["date"]}">{p["date"]}</time><div class="body">{p["html"]}</div><p><a href="{r}{prefix(lang)}blog/">← {e(L["nav"]["blog"])}</a></p></article>'
            ld = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "datePublished": p["date"], "inLanguage": lang, "author": {"@type": "Person", "name": "Spektronautilus"}}]
            write(prefix(lang) + path + "index.html", render(lang, L, "blog", body, p["title"] + " | Spektronautilus", p["text"][:155], ld, path=path, alt=alt, og_type="article"))
    # sitemap with language alternates
    urls = []
    def entry(loc, alts):
        a = "".join(f'<xhtml:link rel="alternate" hreflang="{lg}" href="{u}"/>' for lg, u in alts.items())
        if "en" in alts: a += f'<xhtml:link rel="alternate" hreflang="x-default" href="{alts["en"]}"/>'
        return f"<url><loc>{loc}</loc><lastmod>{date.today().isoformat()}</lastmod>{a}</url>"
    for key in NAV:
        alts = {lg: url(lg, SLUGS[key]) for lg in LANGS}
        urls += [entry(alts[lg], alts) for lg in LANGS]
    for p in ps:
        alts = {p2["lang"]: url(p2["lang"], f"blog/{p['slug']}/") for p2 in ps if p2["slug"] == p["slug"]}
        urls += [entry(u, alts) for u in alts.values()]
    for extra in ("mixer/", "mixer-mobile/", "tools/app/", "live-dj/", "vj-pad/", "live-mobile/", "vj-mobile/"):
        urls.append(f"<url><loc>{SITE}{extra}</loc></url>")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
    items = "".join(f'<item><title>{e(p["title"])}</title><link>{url(p["lang"], "blog/" + p["slug"] + "/")}</link><guid>{url(p["lang"], "blog/" + p["slug"] + "/")}</guid><pubDate>{p["date"]}</pubDate><description>{e(p["text"][:300])}</description></item>' for p in ps if p["lang"] == "en")
    write("feed.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Spektronautilus</title><link>{SITE}</link><description>News and tips from Spektronautilus</description>{items}</channel></rss>\n')
    write("favicon.svg", LOGO + "\n")
    L = LANGS["en"]
    write("404.html", render("en", L, "home", '<h1>Page not found</h1><p class="lead">That page does not exist. Try the <a href="./">home page</a>.</p>', "Not found | Spektronautilus", "Page not found", path="", alt={"en": ""}, noindex=True).replace('href="../favicon', 'href="favicon'))
    write(".nojekyll", "")
    print("built", len(LANGS), "languages:", ", ".join(LANGS))


if __name__ == "__main__":
    main()
