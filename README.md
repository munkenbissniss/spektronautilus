# Spektronautilus – the magic video mixer

Free browser tools for VJs, visual artists and music lovers. Everything runs in the browser and files never leave the device.

The site is static (GitHub Pages: publish the `docs/` folder). English is at the root; Norwegian, Spanish, German and Portuguese are in `/no/`, `/es/`, `/de/`, `/pt/`.

## What is in the repo

| Path | What |
|---|---|
| `docs/` | The finished site. This is what you publish. |
| `docs/mixer/`, `docs/mixer-mobile/` | Magic Video Mixer (desktop and phone). Phones that open `/mixer/` are sent to the phone version (`?desktop=1` turns that off). |
| `docs/live-dj/` | Video DJ (`index.html` control window, `output.html` projector window, `app.js`, pure logic in `core.js`) |
| `docs/live-mobile/` | Phone Video DJ (`index.html`) and the receiver page for sending the picture to another screen (`receiver.html`, `cast.js`) |
| `docs/vj-pad/` | VJ Mixer (same layout as the Video DJ; shares `../live-dj/core.js`) |
| `docs/tools/app/` | The loop tools (convert, GIF→MP4, make loops, filters, find loops, crop & trim, sizes, HAP/ProRes, AI upscale (Linux version + your own Video2X), catalogue, loop pack). Needs the engine files, see below. |
| `docs/shared/` | Shared scripts: queue, offline (service worker registration), language (`i18n.js` + `lang/`, generated), the "Ready for the show?" check (`check.js`, `testcard.html`) |
| `src/i18n-app/` | The texts of the apps and their translations (`en.txt` is the master, one string per line; `t*.txt` hold `ID ¦ no ¦ es ¦ de ¦ pt`). `build_i18n.py` turns them into `docs/shared/lang/*.js` and checks that nothing is missing. |
| `build.py`, `i18n/`, `content/`, `data/`, `src/` | Generator for the pages around the apps (home, landing pages, guides, packs, sitemap) |
| `tools-source/` | Desktop/CLI version of the tools (`python3 vj ui`), and the tests for the tools |
| `tests_site.py` | Checks the built site (links, SEO tags, phone redirect) |

## Daily work

```
python3 build.py        # rebuilds docs/ from the texts, guides and packs
python3 tests_site.py   # checks links, SEO tags and the phone redirect
python3 tests_live.py   # browser test of the Video DJ (needs ffmpeg, playwright, Pillow)
python3 tests_vj.py     # browser test of the VJ mixer
python3 tests_live_mobile.py   # phone live mixer, incl. sending the picture to a receiver page over WebRTC
python3 tests_vj_mobile.py     # phone VJ mixer
python3 tests_queue.py         # shared queue page
python3 tests_offline.py       # offline mode and updates
python3 tests_i18n.py          # every app in every language: nothing left in English, language button
python3 tests_check.py         # the "Ready for the show?" check and the test card
python3 tests_v2x.py           # AI upscale with Video2X, tested with a stand-in program (real Video2X needs a Vulkan GPU)
python3 tests_newtools.py      # crop & trim, sizes, HAP/ProRes, catalogue, loop pack (real ffmpeg)
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

### Guides
`content/guides/<lang>.md` holds all nine guides of a language (menu item *Guides*, address `/guides/…`). Each guide starts with `=== slug`, then `name:`, `title:`, `desc:` and `summary:` lines, a blank line and the text.
- Headings: `## Title {#anchor}` (the anchors are the same in every language, other guides link to them). `> text` makes a tip box.
- Links: `[text](@guides/video-dj/)` to a page in the same language, `[text](@@tools/app/#loop)` to an app at the site root.
- Buttons and settings of the apps are written `[[English label]]` and are shown as the app shows them in that language. The build stops if a label does not exist in `src/i18n-app/en.txt`. Keys are written `{{F}}`.
- Every language needs every guide. To add a guide: add it to `GUIDES` in `build.py` and to all five files.
- Apps link to their guide and have the Feedback button through `docs/shared/extras.js` (`<script src="../shared/extras.js" data-guide="video-dj" defer>`). The form opens the visitor's mail program (mailto), because a static site cannot send mail. The address is set at the top of that file.
- Test: `python3 tests_guides.py`.

### Another language
Pages: copy `i18n/en.py` to `i18n/<code>.py` and translate, run `python3 build.py`. The language switcher, hreflang links and sitemap update by themselves.
Apps (mixers and tools): add a column to the `src/i18n-app/t*.txt` lines and the language code to `LANGS` in `build_i18n.py` and `docs/shared/i18n.js`. Changed or new English text in an app: add the line to the end of `src/i18n-app/en.txt` and its translations in a new `t*.txt`; `python3 build.py` stops with a list if something is missing or a `{placeholder}` differs.

### SEO
Every page has its own title and description, a canonical URL, `hreflang` links between languages (plus `x-default`), Open Graph tags and JSON-LD. `sitemap.xml` and `robots.txt` are written by the build. Set the real address in `site.json` before you publish; if you later get your own domain, change it there and rebuild.

## Linux version (runs locally)
`linux/` contains a launcher that serves the whole site on your own computer (127.0.0.1 only) and opens it in Chrome/Chromium in its own window, started with settings for live visuals. If `ffmpeg` is installed, the tools use it instead of the slower WebAssembly engine (the page says "Fast mode"). Nothing needs to be downloaded or installed with pip.

- Try it from the repository: `python3 linux/spektronautilus.py`
- Make a package: `python3 linux/build_linux.py` gives `dist/spektronautilus-linux.tar.gz` (unpack, run `./install.sh`; it adds a menu entry and a `spektronautilus` command; `uninstall.sh` removes it).
- Tests: `python3 tests_linux.py` (server, safety rules, tools on the real ffmpeg) and `python3 tests_linux_install.py` (package, install, launcher, uninstall).
- Safety: the server refuses other Host names and requests without its custom header (stops other websites from using it), only lets ffmpeg touch its own temporary folder, and deletes that folder on exit.

## Status
- Available: Magic Video Mixer (desktop and phone), Video DJ (desktop and phone), VJ Mixer (desktop and phone), tools (crop & trim, sizes, HAP/ProRes (Linux version), AI upscale (Linux version, needs Video2X installed by the user, never bundled), catalogue and loop pack on top of the first five), a "Ready for the show?" check in the live mixers, offline mode (installable), five languages, a shared queue page (`/queue/`) that shows jobs from the tools and both Magic Mixers.
- Not yet set up: loop packs (waiting for the Jottacloud links), donations.
