# Audit, November 2026

A read-through of the whole project: errors, risks, memory, CPU/GPU, stability, usability and structure. Three groups: what was fixed in this round, what was found and is left as a recommendation (with a rough size: S = hours, M = a day or two, L = several days), and what was checked and is fine. Earlier ideas are in `IDEAS.md`.

## Fixed in this round

| Where | Problem | Fix |
|---|---|---|
| Magic Mixer (desktop and phone) | If setting up a render threw an error (no recorder, no storage, a broken loop), the promise never finished: the job stayed on "Preparing" for ever and **the whole queue stopped**. An error in the frame loop froze the render silently. | The render is wrapped: a setup error makes the job *Failed* with the reason, an error while drawing stops the render and keeps what was made, and a failure while finishing the file ends the job. The next job in the queue runs. Tested with a recorder that throws. |
| Magic Mixer (desktop) | Ten hidden video elements stayed loaded after a job (decoders and blob files in memory) and unused ones were kept during a render. | Videos not needed for 6 s are released during the render, and all are released when the job ends (the phone version already released unused ones; it now also releases all at the end). |
| Magic Mixer | A finished video that was not downloaded was deleted when you reloaded or left the page, without a warning (the warning only came during rendering). | Leaving the page asks first while a finished video is not downloaded or sent to Vimeo. |
| VJ Mixer (desktop) | Removing a pad read the video address after it had been cleared, so the blob URL was never freed: every removed pad kept its video in memory until the page closed. | The address is read first, then revoked (the phone version was already right). |
| Video DJ (desktop) | Each deck copied up to 1.5 GB into memory regardless of the computer. | The limit follows `navigator.deviceMemory` (300 MB to 1.5 GB). Bigger files are streamed from disk, as before. |
| Loop Hospital | The result list's blob URLs were never revoked when you chose another clip. | They are revoked. |
| AI tools (Upscale, Slow motion) | 100 clips on the graphics card once froze the computer. Nothing warned, nothing rested. | With more than 3 clips the first press only explains and suggests a test with one clip; the second press runs. New setting *Rest between clips* (0, 10, 30, 60 s) lets the card cool down. The warning also recommends saving straight into a folder so results are not kept in memory. |
| Launcher | The ffmpeg argument filter is a deny list. `subfile,,start,…:/path` was not caught. | `subfile` is denied. (Only same-origin requests with the `X-Spk` header reach it, so this was low risk.) |
| Tests | The Magic Mixer had no end-to-end test. | `tests_mixer_render.py` makes a real video from a song and loops in both mixers, checks the file, the freed videos, the leave warning, a failing recorder and that the queue goes on. `tests_engine.mjs` covers Stop in the browser engine. |

## Found, not changed (recommendations)

1. **Magic Mixer renders in real time** (a 4-minute song takes 4 minutes, and the tab must stay open). On the Linux/Windows version, let ffmpeg compose the planned shots: no browser limits, several times faster than real time. L. See `IDEAS.md`.
2. **Browser tools are single-threaded ffmpeg.wasm**, about 5 to 10 times slower than the local engine. GitHub Pages cannot send the headers that multi-threaded wasm needs; a small service-worker shim can add them. The upside is 2 to 4 times faster conversion. M, and needs a test on Safari and Firefox before it ships.
3. **Effects use Canvas 2D filters** (`ctx.filter` blur and hue-rotate in the VJ mixer). On weak laptops and above 1080p this is the first thing that drops frames. WebGL shaders would fix it and allow better effects. L.
4. **Pool size in the desktop Magic Mixer is fixed at 10 videos.** With 4K or HEVC loops this is a lot of decoding. Make it depend on the loop resolution and `deviceMemory`, and warn about heavy loops before the render starts. S.
5. **Results stay in memory in the Tools** unless *Save each file straight into a folder* is on (Chrome and Edge only). Large batches in Safari or Firefox can run out of memory. A "download as you go" mode or a zip per 500 MB would help. M.
6. **Mobile Magic Mixer keeps the finished file in memory when storage in the browser is not available** (a browser without write access to its private file area). A long video can then use a lot of memory. A limit and a message before starting would help. S.
7. **Real-world checks still missing:** the Windows installer, the real Video2X flags and progress output on a Vulkan GPU, and Vimeo upload against the real service (only a pretend server is tested). Test list for the coming week is in the reply to this audit.
8. **Launcher ffmpeg filter** is a deny list. Moving to an allow list of the options the apps really use would be sturdier. M.
9. **Console noise on the static site:** the Tools probe `/api/native` returns a 404 on GitHub Pages, shown as a red line in the console. Harmless. Skip the probe when the page is not served from 127.0.0.1. S.
10. **Repository tidy-up:** `shot-*.png` and `__pycache__` sit in the root (git-ignored, but they end up in the zip). Move screenshots to a folder outside the repo. S.

## Checked and fine

- All 3,350 links and sources in the built pages resolve. No duplicate ids (other than a template string in the Magic Mixer).
- Every button, field and image on the front page, the three mixers (desktop and phone), the Tools, the Loop Hospital and the Queue has an accessible name; each page has one `h1` and the right `lang`. No script errors on load.
- The local launcher only answers to 127.0.0.1, checks the Host header (DNS rebinding), needs a custom header for any write or run, keeps file paths inside its work folder and checks Video2X arguments against a list of flags.
- Memory: object URLs are revoked in the Video DJ, phone mixers, Tools and Hospital. The tick worker restarts if it stalls.
- Offline mode: the whole site is cached on the first visit; the updates bar asks before replacing a running version.
