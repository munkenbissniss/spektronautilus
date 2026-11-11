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
| `docs/tools/hospital/` | Loop Hospital: examine one clip and treat it step by step (cut, crop, slow motion, upscale, resize, look, loop fix), with before/after preview |
| `docs/tools/app/` | The loop tools (convert, GIF→MP4, make loops, filters, find loops, crop & trim, sizes, HAP/ProRes, upscale and slow motion (sharp/blend/motion methods everywhere; AI methods in the Linux and Windows versions + your own Video2X), catalogue, loop pack). Needs the engine files, see below. |
| `docs/shared/` | Shared scripts: queue, offline (service worker registration), language (`i18n.js` + `lang/`, generated), the "Ready for the show?" check (`check.js`, `testcard.html`) |
| `src/i18n-app/` | The texts of the apps and their translations (`en.txt` is the master, one string per line; `t*.txt` hold `ID ¦ no ¦ es ¦ de ¦ pt`). `build_i18n.py` turns them into `docs/shared/lang/*.js` and checks that nothing is missing. |
| `build.py`, `i18n/`, `home_text.py`, `content/`, `data/`, `src/` | Generator for the pages around the apps (home, landing pages, guides, packs, sitemap). The front page texts are in `home_text.py` (all languages side by side) |
| `make_logos.py` | Draws the logo proposals into `docs/logos/` (a page for choosing, not linked from the site) |
| `tools-source/` | Desktop/CLI version of the tools (`python3 vj ui`), and the tests for the tools |
| `tests_site.py` | Checks the built site (links, SEO tags, phone redirect) |

## Daily work

```
python3 build.py        # rebuilds docs/ from the texts, guides and packs
python3 tests_site.py   # checks links, SEO tags and the phone redirect
python3 tests_live.py   # browser test of the Video DJ (needs ffmpeg, playwright, Pillow)
python3 tests_vj.py     # browser test of the VJ mixer
python3 tests_vj_adv.py # the advanced view of the VJ mixer: banks, auto mix, recording
python3 tests_vj_sound.py # sound sources of the VJ mixer: input list, audio file, shared tab, sound in the recording
python3 tests_live_mobile.py   # phone live mixer, incl. sending the picture to a receiver page over WebRTC
python3 tests_vj_mobile.py     # phone VJ mixer
python3 tests_queue.py         # shared queue page
python3 tests_offline.py       # offline mode and updates
python3 tests_i18n.py          # every app in every language: nothing left in English, language button
python3 tests_check.py         # the "Ready for the show?" check and the test card
python3 tests_hospital.py      # Slow motion and Upscale (ffmpeg methods), and the Loop Hospital (rotate, several looks)
python3 tests_upload.py        # the Vimeo upload dialog (against a pretend server)
python3 tests_progress.py       # progress bars: never backwards, alive, pause/resume, clock, Queue page
python3 tests_longnames.py      # very long file names on a 320 px phone screen
python3 tests_ios_fastpath.py   # iPhone app: Tools converts with the phone video chips (stand-in for the app)
python3 tests_home.py          # the front page in five languages: every link works, fits a phone
python3 tests_mixer_render.py  # Magic Mixer (desktop and phone) makes a real video in the browser; a broken render must not freeze the queue
python3 tests_v2x.py           # AI upscale with Video2X, tested with a stand-in program (real Video2X needs a Vulkan GPU)
python3 tests_newtools.py      # crop & trim, sizes, HAP/ProRes, catalogue, loop pack (real ffmpeg)
node --test tests_filters.mjs   # runs all twenty filters with the computer's own ffmpeg
node --test tests_life.mjs        # Loop Hospital "Bring it to life": real ffmpeg, seamless loop, still pictures move, 16 s
node tests_fps.mjs              # "Frame rate": 60 fps without stutter, loop seam and length kept, stepping fixed, AI (stand-in) path
node tests_smooth.mjs           # "Smooth out": stray frames found, a lurch is evened out, works after Cut
node tests_loops.mjs            # "Make it loop": back-and-forth keeps its tempo, eases at the turnaround, no jump at the seam
python3 tests_hospital_ai.py       # Loop Hospital: AI slow motion + AI upscale (stand-in Video2X), disabled in the browser version, preview stays light
python3 tests_hospital_preview.py, tests_hospital_reset.py, tests_mpd218.py, tests_battery.py  # Loop Hospital on a phone: the preview video sits right above the preview button
python3 tests_gif.py             # Loop Hospital: Convert GIF to MP4 above the video window, then treat the mp4
python3 tests_cuts.py            # Magic Mixer cuts & sync: build-up rush, hard cuts, real render (desktop and phone)
python3 tests_aiprogress.py     # true progress when the result is longer than the input, graphics card choice for AI
python3 tests_life_ui.py         # the same step in the page: suggestion, styles, Advanced, a real 16 s result
node --test tests_vjrate.mjs      # exports stay under the data-rate ceiling (default 3 MB/s) even on 1080p noise
node --test tests_live_core.mjs tests_vj_core.mjs tests_engine.mjs
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
- Available: Magic Video Mixer (desktop and phone), Video DJ (desktop and phone), VJ Mixer (desktop and phone), tools (crop & trim, sizes, HAP/ProRes (Linux version), AI upscale and AI slow motion (Linux and Windows versions, needs Video2X installed by the user, never bundled), catalogue and loop pack on top of the first five), a "Ready for the show?" check in the live mixers, offline mode (installable), five languages, a shared queue page (`/queue/`) that shows jobs from the tools and both Magic Mixers.
- Not yet set up: loop packs (waiting for the Jottacloud links), donations.


## Windows version (installer)
The same launcher (`linux/spektronautilus.py`) runs on Windows. `windows/` and `.github/workflows/windows.yml` build `Spektronautilus-Setup.exe` on GitHub (PyInstaller + Inno Setup, ffmpeg bundled, no admin rights needed).
- Build: GitHub > Actions > "Windows installer" > Run workflow (or push a tag like `v1.0.0` to also publish a release). Download `Spektronautilus-Setup` from the run.
- Not code-signed, so Windows SmartScreen shows "More info > Run anyway". Signing needs a paid certificate.
- The bundled ffmpeg is a separate GPL build (BtbN). Its licence is installed next to it.
- AI upscaling and AI slow motion (RIFE) run through Video2X, which you install yourself (never bundled: separate programme and licence). It is found in PATH, in `SPEKTRO_VIDEO2X`, in a one-line `video2x.txt` in the settings folder, or in the usual install places. The launcher reads `video2x --help` to learn the flag spelling of that version (`-g`/`--list-gpus` or `-d`/`--list-devices`) and whether it has RIFE.
- Not yet tested on a real Windows machine: the workflow has a smoke test (starts the exe, checks the site and ffmpeg), but please try the installer once yourself.
