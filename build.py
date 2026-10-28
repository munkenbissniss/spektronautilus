#!/usr/bin/env python3
"""Builds the Spektronautilus site into docs/.

Pages are generated from i18n/<lang>.py (texts), content/guides/<lang>.md (the guides) and data/packs.json (loop packs).
English lives at the root, other languages in /<lang>/. Every page gets hreflang links, a canonical URL,
Open Graph tags and structured data, and the build writes sitemap.xml, robots.txt and 404.html.
To add a language: copy i18n/en.py to i18n/<code>.py, translate it, run  python3 build.py.
"""
import html, importlib.util, json, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = json.loads((ROOT / "site.json").read_text())["url"].rstrip("/") + "/"
SLUGS = {"home": "", "magic": "magic-mixer/", "live": "live-mixer/", "vj": "vj-mixer/", "tools": "tools/", "packs": "packs/", "docs": "guides/", "about": "about/"}
MIXERS = ["magic", "live", "vj"]
NAV = ["home", "magic", "live", "vj", "tools", "packs", "docs", "about"]
# the guides: (slug, group, icon, tool) ; tool = (desktop path, phone path or None) of the app the guide is about
GUIDES = [("start", "start", "🧭", None),
          ("magic-mixer", "mixers", "🪄", ("mixer/", "mixer-mobile/")),
          ("video-dj", "mixers", "🎛️", ("live-dj/", "live-mobile/")),
          ("vj-mixer", "mixers", "🎚️", ("vj-pad/", "vj-mobile/")),
          ("tools", "tools", "🧰", ("tools/app/", None)),
          ("queue", "more", "📋", ("queue/", None)),
          ("show-check", "more", "✅", None),
          ("offline-linux", "more", "📲", None),
          ("help", "more", "🛟", None)]
GROUPS = ["start", "mixers", "tools", "more"]
GUIDE_OF = {"magic": "magic-mixer", "live": "video-dj", "vj": "vj-mixer", "tools": "tools"}
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


def slugify(t):
    t = re.sub(r"<[^>]+>", "", t).lower()
    t = t.replace("æ", "ae").replace("ø", "o").replace("å", "a").replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "ss")
    t = "".join(c for c in __import__("unicodedata").normalize("NFKD", t) if not __import__("unicodedata").combining(c))
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


_UI = {}
def ui_label(lang, text):
    """the guides name buttons and settings of the apps with [[English label]]; show them as the app shows them in this language"""
    if not _UI:
        sd = ROOT / "src" / "i18n-app"
        en = [l.rstrip("\n") for l in (sd / "en.txt").read_text(encoding="utf-8").splitlines()]
        tr = {}
        for f in sorted(sd.glob("t*.txt")):
            for l in f.read_text(encoding="utf-8").splitlines():
                parts = l.split(" ¦ ")
                if len(parts) == 5 and parts[0].strip().isdigit(): tr[int(parts[0])] = [x.strip() for x in parts[1:]]
        _UI["en"] = set(en)
        for k, lg in enumerate(["no", "es", "de", "pt"]):
            _UI[lg] = {en[i - 1]: v[k] for i, v in tr.items() if i <= len(en)}
    if text not in _UI["en"]: sys.exit(f"a guide mentions an app label that does not exist: [[{text}]]")
    return text if lang == "en" else _UI[lang].get(text, text)


def md(text):
    """tiny markdown: ## / ### headings (## Title {#id} sets the anchor), - lists, 1. lists, > tips, **bold**, *italic*, `code`,
    links [x](https://..), [x](@page/) = a page in the same language, [x](@@app/) = something at the site root (apps)"""
    out, para, ul, ol = [], [], [], []
    toc = []
    def inline(s):
        keep = []
        def hold(m):
            keep.append(f'<span class="ui">{e(ui_label(md.lang, m.group(1)))}</span>'); return f"\x00{len(keep) - 1}\x00"
        s = re.sub(r"\[\[(.+?)\]\]", hold, s)
        s = e(s)
        s = re.sub(r"\{\{(.+?)\}\}", r"<kbd>\1</kbd>", s)
        s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
        s = re.sub(r"\[(.+?)\]\((https?://[^)\s]+|/[^)\s]*|@@?[\w./#-]+|[\w./#-]+)\)", r'<a href="\2">\1</a>', s)
        return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], s)
    def flush():
        nonlocal para, ul, ol
        if para: out.append("<p>" + inline(" ".join(para)) + "</p>"); para = []
        if ul: out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in ul) + "</ul>"); ul = []
        if ol: out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in ol) + "</ol>"); ol = []
    for line in text.splitlines():
        if not line.strip(): flush()
        elif line.startswith("## ") or line.startswith("### "):
            flush()
            lvl = 2 if line.startswith("## ") else 3
            t = line[lvl + 1:].strip()
            m = re.search(r"\s*\{#([\w-]+)\}$", t)
            hid = m.group(1) if m else slugify(t)
            if m: t = t[:m.start()]
            if lvl == 2: toc.append((hid, t))
            out.append(f'<h{lvl} id="{hid}">{inline(t)}</h{lvl}>')
        elif line.startswith("> "):
            flush(); out.append(f'<p class="tip">{inline(line[2:])}</p>')
        elif line.startswith("- "):
            if para or ol: flush()
            ul.append(line[2:])
        elif re.match(r"\d+\. ", line):
            if para or ul: flush()
            ol.append(re.sub(r"^\d+\. ", "", line))
        else:
            if ul or ol: flush()
            para.append(line.strip())
    flush()
    md.toc = toc
    return "\n".join(out)


def guides(lang):
    """content/guides/<lang>.md holds all guides of a language, each starting with  === slug  and a few  key: value  lines"""
    f = ROOT / "content" / "guides" / f"{lang}.md"
    res = {}
    md.lang = lang
    if not f.exists(): return res
    for chunk in re.split(r"^=== ", f.read_text(encoding="utf-8"), flags=re.M)[1:]:
        slug, rest = chunk.split("\n", 1)
        head, body = rest.split("\n\n", 1)
        meta = dict(l.split(": ", 1) for l in head.splitlines() if ": " in l)
        html_ = md(body)
        res[slug.strip()] = {**meta, "html": html_, "toc": md.toc, "text": re.sub(r"\s+", " ", body).strip()}
    return res


STYLE = (ROOT / "src" / "style.css").read_text()
LOGO = (ROOT / "src" / "logo.svg").read_text().strip()
LOGO = re.sub(r"<metadata>.*?</metadata>", "", LOGO, flags=re.S).replace(' xmlns:c2pa="http://c2pa.org/manifest"', "")      # the file carries a large hidden metadata block; no need to ship it on every page
# Phones are sent to the phone version of an app. ?desktop=1 turns that off.
MOBILE_JS = """(function(){try{var q=location.search.indexOf('desktop=1')>-1;if(q)localStorage.setItem('spk_desktop','1');
var m=!localStorage.getItem('spk_desktop')&&matchMedia('(pointer:coarse) and (max-width:900px)').matches;if(!m)return;
var map=[[/(^|\\/)mixer\\/$/,'$1mixer-mobile/'],[/(^|\\/)live-dj\\/$/,'$1live-mobile/'],[/(^|\\/)vj-pad\\/$/,'$1vj-mobile/']];
document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll('a[data-app]').forEach(function(a){map.forEach(function(r){a.href=a.href.replace(r[0],r[1])})})})}catch(e){}})();"""


# shows how many jobs are running in the Queue link (the tools and mixers write the count to localStorage)
DD_JS = """document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll('.dd,.ld').forEach(function(d){var b=d.querySelector('.ddb'),m=d.querySelector('.ddm');function set(o){m.hidden=!o;b.setAttribute('aria-expanded',o?'true':'false')}b.addEventListener('click',function(e){e.stopPropagation();var o=m.hidden;document.querySelectorAll('.ddm').forEach(function(x){x.hidden=true});set(o)});document.addEventListener('click',function(e){if(!d.contains(e.target))set(false)});document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!m.hidden){set(false);b.focus()}});d.addEventListener('focusout',function(e){if(!d.contains(e.relatedTarget))set(false)})})});"""
QBADGE_JS = """document.addEventListener('DOMContentLoaded',function(){function u(){try{var o=JSON.parse(localStorage.getItem('spk_q')||'{}'),n=Date.now()-(o.t||0)<30000?o.n||0:0;document.querySelectorAll('.qn').forEach(function(b){b.hidden=!n;b.textContent=n})}catch(e){}}u();addEventListener('storage',u);setInterval(u,4000)});"""


def render(lang, L, key, body_html, title, desc, extra_ld=None, path=None, alt=None, og_type="website", noindex=False):
    path = SLUGS[key] if path is None else path
    r = depth_root(lang, path)
    rl = r + prefix(lang)                       # root of this language
    def link(k): return f'<a href="{rl}{SLUGS[k]}"{" aria-current=page" if k == key else ""}>{e(L["nav"][k])}</a>'
    mix = "".join(link(k) for k in MIXERS)
    nav = link("home") + (f'<div class="dd"><button type="button" class="ddb" aria-expanded="false" aria-haspopup="true"{" data-current" if key in MIXERS else ""}>{e(L["nav"]["mixers"])} <span aria-hidden="true">▾</span></button>'
                          f'<div class="ddm" hidden>{mix}</div></div>') + link("tools") + link("packs") + link("docs")
    foot = (f'<div class="wrap fcols"><div><div class="dgt">{e(L["nav"]["mixers"])}</div>{mix}</div>'
            f'<div><div class="dgt">Spektronautilus</div>{link("home")}{link("tools")}{link("packs")}{link("docs")}</div>'
            f'<div><div class="dgt">{e(L["ui"]["f_more"])}</div>{link("about")}<a href="{r}queue/">{e(L["nav"]["queue"])}<span class="qn" hidden></span></a></div></div>')
    alts = alt if alt is not None else {lg: path for lg in LANGS}
    sw = "".join(f'<a href="{r}{prefix(lg)}{p}" hreflang="{lg}" lang="{lg}"{" aria-current=true" if lg == lang else ""}>{e(LANGS[lg]["label"])}</a>' for lg, p in alts.items()) if len(alts) > 1 else ""
    lang_dd = (f'<div class="ld" role="navigation" aria-label="{e(L["ui"]["lang"])}"><button type="button" class="ddb" aria-expanded="false" aria-haspopup="true" aria-label="{e(L["ui"]["lang"])}">🌐 {lang.upper()} <span aria-hidden="true">▾</span></button>'
               f'<div class="ddm" hidden>{sw}</div></div>') if sw else ""
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
<link rel="manifest" href="{r}manifest.webmanifest">
<style>{STYLE}</style>
<script type="application/ld+json">{ld}</script>
<script>{MOBILE_JS}</script>
<script>{DD_JS}</script>
<script>{QBADGE_JS}try{{localStorage.setItem('spk_lang','{lang}')}}catch(e){{}}</script>
<script src="{r}shared/sw-register.js" defer></script>
<script src="{r}shared/extras.js" data-dock="1" defer></script>
</head>
<body>
<a href="#main" class="sr" style="position:absolute;left:-999px">{e(L['ui']['skip'])}</a>
<header class="top"><div class="wrap">
<a class="brand" href="{rl}">{LOGO}<span>Spektronautilus</span></a>
<nav class="main" aria-label="Main">{nav}</nav>
{lang_dd}
</div></header>
<main id="main"><div class="wrap">
{body_html}
</div></main>
<footer>{foot}<div class="wrap fbase"><span>{e(L['ui']['footer'])}</span><span data-spk-feedback-slot></span><span>© Spektronautilus · MIT</span></div></footer>
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
    body = re.sub(r"\{r\}(magic-mixer|live-mixer|vj-mixer|packs|guides|about)/", lambda m: rl + m.group(1) + "/", P["body"])
    body = re.sub(r"\{r\}tools/(?!app)", lambda m: rl + "tools/", body)
    body = body.replace("{r}", r).replace("{devnote}", e(ui["devnote"]))
    if key in GUIDE_OF:                       # a button to the guide next to the buttons that open the tool
        body = body.replace("</div>", f'<a class="btn" href="{rl}guides/{GUIDE_OF[key]}/">📖 {e(ui["g_guide"])}</a></div>', 1)
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


def write_offline():
    """service worker + manifest + icons: the whole site is stored in the browser on the first visit"""
    import hashlib, shutil
    for n in ("icon-192.png", "icon-512.png"): shutil.copy2(ROOT / "src" / n, DOCS / n)
    skip = {"sw.js", "sitemap.xml", "robots.txt"}
    files, h = [], hashlib.sha1()
    for p in sorted(DOCS.rglob("*")):
        rel = p.relative_to(DOCS).as_posix()
        if not p.is_file() or rel in skip or rel.startswith("tools/app/vendor/") or "__pycache__" in rel or rel.endswith((".png~", ".map")) or rel.startswith("shot-"): continue
        h.update(rel.encode()); h.update(p.read_bytes()); files.append(rel)
        if rel.endswith("/index.html") or rel == "index.html": files.append(rel[:-10] or "./")
    tpl = (ROOT / "src" / "sw.template.js").read_text()
    (DOCS / "sw.js").write_text(tpl.replace("__VERSION__", h.hexdigest()[:12]).replace("__FILES__", json.dumps(sorted(set(files)))), encoding="utf-8")


def guide_nav(L, allg, cur, rl):
    ui = L["ui"]
    groups = ""
    for g in GROUPS:
        items = [(sl, ic) for sl, gr, ic, _ in GUIDES if gr == g and sl in allg]
        if items:
            groups += f'<div class="dg"><div class="dgt">{e(ui["g_grp_" + g])}</div>' + "".join(
                f'<a href="{rl}guides/{sl}/"{" aria-current=page" if sl == cur else ""}><span>{ic}</span> {e(allg[sl]["name"])}</a>' for sl, ic in items) + "</div>"
    return (f'<nav class="dnav" aria-label="{e(ui["g_all"])}"><details><summary>{e(ui["g_all"])}</summary>{groups}</details></nav>'
            "<script>(function(){var d=document.querySelector('.dnav details');if(d&&matchMedia('(min-width:900px)').matches)d.open=true})()</script>")


def feedback_box(L):
    ui = L["ui"]
    return f'<div class="note gfb"><strong>{e(ui["g_fb_t"])}</strong> {e(ui["g_fb_b"])} <button class="btn" type="button" data-spk-feedback>💬 {e(ui["g_fb_btn"])}</button></div>'


def guide_body(L, slug, allg, r, rl):
    G, ui = allg[slug], L["ui"]
    order = [sl for sl, _, _, _ in GUIDES if sl in allg]
    i = order.index(slug)
    tool = next(t for sl, _, _, t in GUIDES if sl == slug)
    cta = ""
    if tool:
        cta = (f'<div class="cta"><a class="btn main"{" data-app=1" if tool[1] else ""} href="{r}{tool[0]}">{e(ui["g_open"])}</a>'
               + (f'<a class="btn" href="{r}{tool[1]}">{e(ui["g_phone"])}</a>' if tool[1] else "") + "</div>")
    toc = ""
    if len(G["toc"]) >= 3:
        toc = f'<nav class="toc" aria-label="{e(ui["g_on"])}"><div class="dgt">{e(ui["g_on"])}</div>' + "".join(f'<a href="#{h}">{e(t)}</a>' for h, t in G["toc"]) + "</nav>"
    html_ = G["html"].replace('href="@@', 'href="' + r).replace('href="@', 'href="' + rl)
    pager = ""
    if i > 0:
        pv = allg[order[i - 1]]
        pager += f'<a class="pg prev" href="{rl}guides/{order[i - 1]}/"><small>← {e(ui["g_prev"])}</small>{e(pv["name"])}</a>'
    else:
        pager += "<span></span>"
    if i < len(order) - 1:
        nx = allg[order[i + 1]]
        pager += f'<a class="pg next" href="{rl}guides/{order[i + 1]}/"><small>{e(ui["g_next"])} →</small>{e(nx["name"])}</a>'
    icon = next(ic for sl, _, ic, _ in GUIDES if sl == slug)
    return (f'<div class="docs">{guide_nav(L, allg, slug, rl)}<article class="doc">'
            f'<p class="crumb"><a href="{rl}guides/">{e(L["nav"]["docs"])}</a> › {e(G["name"])}</p>'
            f'<h1><span class="gi">{icon}</span> {e(G["title"])}</h1><p class="lead">{e(G["desc"])}</p>{cta}{toc}'
            f'<div class="body">{html_}</div>{feedback_box(L)}<div class="pager">{pager}</div></article></div>')


def guides_index(L, P, allg, rl):
    ui = L["ui"]
    icon = {sl: ic for sl, _, ic, _ in GUIDES}
    out = f'<h2>{e(ui["g_tasks"])}</h2><div class="tasks">' + "".join(f'<a class="task" href="{rl}guides/{sl}/"><span>{icon[sl]}</span>{e(txt)}</a>' for txt, sl in P["tasks"] if sl in allg) + "</div>"
    for g in GROUPS:
        items = [sl for sl, gr, _, _ in GUIDES if gr == g and sl in allg]
        if items:
            out += f'<h2>{e(ui["g_grp_" + g])}</h2><div class="cards">' + "".join(
                f'<a class="card gcard" href="{rl}guides/{sl}/"><div class="gi">{icon[sl]}</div><h3>{e(allg[sl]["name"])}</h3><p>{e(allg[sl]["summary"])}</p><span class="more">{e(ui["g_read"])} →</span></a>' for sl in items) + "</div>"
    return out + feedback_box(L)


def main():
    global LANGS
    LANGS = load_langs()
    G = {lang: guides(lang) for lang in LANGS}
    for lang in LANGS:                                  # every language must have every guide the English one has
        miss = [sl for sl in G["en"] if sl not in G[lang]]
        if miss: sys.exit(f"content/guides/{lang}.md is missing: {', '.join(miss)}")
    sitemap = []
    for lang, L in LANGS.items():
        rl0 = prefix(lang)
        for key in NAV:
            P = L["pages"][key]
            path = SLUGS[key]
            r = depth_root(lang, path)
            body = page_body(L, key, r, P)
            ld = []
            if key == "magic":
                ld.append({"@context": "https://schema.org", "@type": "WebApplication", "name": "Magic Video Mixer", "applicationCategory": "MultimediaApplication", "operatingSystem": "Any (modern browser)",
                           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "description": P["desc"], "inLanguage": lang, "url": url(lang, path)})
            if key == "docs":
                body += guides_index(L, P, G[lang], r + rl0)
            write(prefix(lang) + path + "index.html", render(lang, L, key, body, P["title"], P["desc"], ld))
            sitemap.append(path)
        for sl, g in G[lang].items():
            path = f"guides/{sl}/"
            r = depth_root(lang, path)
            ld = [{"@context": "https://schema.org", "@type": "TechArticle", "headline": g["title"], "description": g["desc"], "inLanguage": lang, "url": url(lang, path),
                   "publisher": {"@type": "Organization", "name": "Spektronautilus"}}]
            write(prefix(lang) + path + "index.html", render(lang, L, "docs", guide_body(L, sl, G[lang], r, r + rl0), g["title"] + " | Spektronautilus", g["desc"], ld, path=path))
    # sitemap with language alternates
    urls = []
    def entry(loc, alts):
        a = "".join(f'<xhtml:link rel="alternate" hreflang="{lg}" href="{u}"/>' for lg, u in alts.items())
        if "en" in alts: a += f'<xhtml:link rel="alternate" hreflang="x-default" href="{alts["en"]}"/>'
        return f"<url><loc>{loc}</loc><lastmod>{date.today().isoformat()}</lastmod>{a}</url>"
    for key in NAV:
        alts = {lg: url(lg, SLUGS[key]) for lg in LANGS}
        urls += [entry(alts[lg], alts) for lg in LANGS]
    for sl in G["en"]:
        alts = {lg: url(lg, f"guides/{sl}/") for lg in LANGS}
        urls += [entry(u, alts) for u in alts.values()]
    for extra in ("mixer/", "mixer-mobile/", "tools/app/", "live-dj/", "vj-pad/", "live-mobile/", "vj-mobile/"):
        urls.append(f"<url><loc>{SITE}{extra}</loc></url>")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
    write("favicon.svg", LOGO + "\n")
    L = LANGS["en"]
    write("404.html", render("en", L, "home", '<h1>Page not found</h1><p class="lead">That page does not exist. Try the <a href="./">home page</a>.</p>', "Not found | Spektronautilus", "Page not found", path="", alt={"en": ""}, noindex=True).replace('href="../favicon', 'href="favicon'))
    import build_i18n; build_i18n.build()
    write_offline()
    write(".nojekyll", "")
    print("built", len(LANGS), "languages:", ", ".join(LANGS))


if __name__ == "__main__":
    main()
