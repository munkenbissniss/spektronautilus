# Spektronautilus – the magic video mixer

Free browser tools for VJs, visual artists and music lovers. Everything runs in the browser and files never leave the device.

The site is static (GitHub Pages: publish the `docs/` folder). English is at the root, Norwegian in `/no/`.

## What is in the repo

| Path | What |
|---|---|
| `docs/` | The finished site. This is what you publish. |
| `docs/mixer/`, `docs/mixer-mobile/` | Magic Video Mixer (desktop and phone). Phones that open `/mixer/` are sent to the phone version (`?desktop=1` turns that off). |
| `docs/live-dj/` | Live Video DJ Mixer (`index.html` control window, `output.html` projector window, `app.js`, pure logic in `core.js`) |
| `docs/live-mobile/` | Phone live mixer (`index.html`) and the receiver page for sending the picture to another screen (`receiver.html`, `cast.js`) |
| `docs/vj-pad/` | VJ Mixer (same layout as the Live DJ mixer; shares `../live-dj/core.js`) |
| `docs/tools/app/` | The loop tools (convert, GIF→MP4, make loops, find loops). Needs the engine files, see below. |
| `build.py`, `i18n/`, `content/`, `data/`, `src/` | Generator for the pages around the apps (home, landing pages, blog, packs, sitemap) |
| `tools-source/` | Desktop/CLI version of the tools (`python3 vj ui`), and the tests for the tools |
| `tests_site.py` | Checks the built site (links, SEO tags, phone redirect) |

## Daily work

```
python3 build.py        # rebuilds docs/ from the texts, blog posts and packs
python3 tests_site.py   # checks links, SEO tags and the phone redirect
python3 tests_live.py   # browser test of the Live DJ mixer (needs ffmpeg, playwright, Pillow)
python3 tests_vj.py     # browser test of the VJ mixer
python3 tests_live_mobile.py   # phone live mixer, incl. sending the picture to a receiver page over WebRTC
node --test tests_filters.mjs   # runs all ten filters with the computer's own ffmpeg
node --test tests_live_core.mjs tests_vj_core.mjs
```

### One-time: the video engine for the browser tools
```
python3 get-ffmpeg.py   # downloads ffmpeg.wasm (~31 MB) into docs/tools/app/vendor/
```
Commit `docs/tools/app/vendor/` together with the rest.

### Loop packs
Edit `data/packs.json`: one entry per pack with `title`, `url` (the Jottacloud share link), and optionally `desc`, `desc_no`, `clips`, `size`. Run `python3 build.py`.

### Blog
Add `content/blog/YYYY-MM-DD-name.en.md` (and `.no.md`) with a front matter block:
```
---
title: My post
date: 2026-11-01
---
Text. **bold**, *italic*, [links](https://example.com), "## headings" and "- lists".
```

### Another language
Copy `i18n/en.py` to `i18n/<code>.py`, translate the texts, run `python3 build.py`. The language switcher, hreflang links and sitemap update by themselves. The app screens (mixers and tools) are still English only.

### SEO
Every page has its own title and description, a canonical URL, `hreflang` links between languages (plus `x-default`), Open Graph tags and JSON-LD. `sitemap.xml`, `robots.txt` and `feed.xml` are written by the build. Set the real address in `site.json` before you publish; if you later get your own domain, change it there and rebuild.

## Status
- Available: Magic Video Mixer (desktop and phone), Live Video DJ Mixer (desktop and phone), VJ Mixer (desktop and phone), tools (all 5), a shared queue page (`/queue/`) that shows jobs from the tools and both Magic Mixers.
- Not yet set up: loop packs (waiting for the Jottacloud links), donations.
