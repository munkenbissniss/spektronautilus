# Ideas and improvements (October 2026 review)

Sorted by how much they would help, with a rough size: S = hours, M = a day or two, L = several days.

## 1. Stability at a real gig
- ✅ **Done: works offline in the browser (installable web app).** A service worker stores the whole site on the first visit, so the mixers start with no venue Wi-Fi; a bar asks before a new version replaces a running one.
- ✅ **Done: "Ready for the show?"** in the four live mixers: H.264, offline-ready, screen stays awake, pop-ups, second screen, full screen, MIDI, sound, battery, speed test, free space, output window and loaded loops/tracks, with a test card for the projector and a copyable report.
- **Render faster than real time in Magic Mixer** with WebCodecs, L. **Not done, on purpose.** Today a 4-minute song takes 4 minutes. A faster renderer needs its own MP4 reader (to get video samples out of the loops), a decoder with seeking, an encoder and an MP4 writer, and the H.264 parts can only be verified in a normal Chrome (the test browser used for development has no H.264). A renderer that cannot be tested end to end could produce broken files, which is worse than a slow one. Next step, when you can test in Chrome: build it as an "Experimental fast export" switch that falls back to today's real-time render on any error. On the Linux version a better route exists: let ffmpeg compose the planned shots (no browser limits).
- **Error log + "Copy debug info" button**, S. One global handler that collects errors and browser info, so a bug report is one paste.
- **Restore after a crash or accidental reload** in Video DJ and VJ mixer (decks, pads, layers, effects), M. Pads already have "remember loops".
- **Photosensitivity safety**, S–M. A "limit flashing" switch that caps flash/strobe/invert to 3 per second (default on for public events), and a clear warning near those effects.

## 2. Speed
- **Linux version (built now):** real ffmpeg, no memory limit. Next steps for it: hardware encoders (NVENC, VAAPI) as an option, 2 jobs in parallel for small clips, a "watch folder" that converts anything dropped into it, and reading/writing the real folders directly instead of copying through the browser (the local server can do that).
- **Mixers on the GPU (WebGL)**, L. Blend modes and effects as shaders instead of Canvas 2D filters. Large gain on weak laptops and 1080p, and enables better effects (RGB split, glitch, kaleidoscope, feedback).
- **Heavy-clip warning**, S. When a pad gets a 4K or HEVC clip, say so and offer "make a light copy" with the Tools.
- **Frame-rate meter** with automatic quality drop (lower picture size when the frame rate falls), S–M.
- **Draw hidden channels less often**, done in the VJ mixer desktop version (every 3rd frame when the channel is not heard). Same trick for the Video DJ and phone mixers: S.

## 3. Using it (UX)
- **First-run tour** (3 short steps) per mixer and a **"?" shortcut sheet**, S.
- **Sets**: save and load a whole setup (pads, layers, effects, posters, MIDI) as a small file, M.
- **Show mode**: big-button layout without settings, locked against accidental clicks, M.
- **MIDI presets** for common controllers (Launchpad, APC mini, LPD8, nanoKONTROL) with LED feedback, M.
- **Queue**: sound and title-bar progress when a job finishes, "Retry failed", S.
- **Undo** for removing a pad or clearing a layer; drag to reorder pads; pad colours, S–M.

## 4. Language and communication
- ✅ **Done: the apps and the whole site speak English, Norwegian, Spanish, German and Portuguese.** The 🌐 button in each app switches language; the site pages are separate, search-visible pages per language. Next: French, and a way for volunteers to correct wording (the lists are in `src/i18n-app/`).
- **Help / FAQ page**: "my video will not play", "which format", "how do I get the picture on the projector", "why is it slow", with screenshots, S–M.
- **Changelog page** and a visible version number, S.
- **Honest browser notes**: a short banner on Safari and Firefox about what is limited there, S.
- **Sample content** so a new visitor can try the mixers in 10 seconds (3 tiny CC0 loops built in), S.

## 5. New tools
- ✅ **Done: Crop & trim** (16:9, 9:16, 1:1, 4:3, 21:9, start and length).
- ✅ **Done: Sizes** (480p proxy, 720p, 1080p, 1440p, 4K; sizes bigger than the clip are skipped).
- ✅ **Done: HAP, HAP Q, HAP Alpha, ProRes 422 (4 levels), ProRes 4444** in the Linux version. DXV is not possible with ffmpeg (closed format).
- **Alpha loops** (transparent overlays) end to end, M.
- **Speed and retime**: half speed, double speed, smooth slow-motion, S–M.
- **Colour looks / LUT** in bulk, S.
- ✅ **Done: Catalogue** (HTML page with pictures, sorting and search, plus CSV).
- ✅ **Done: Loop pack builder** (zip with the untouched loops, README, pack.json, catalogue page, contact-sheet picture and licence). A preview GIF is not included; the contact sheet picture does that job.
- **Audio tools for Magic Mixer songs**: BPM and key detection, loudness normalising, MP3 trimming, M.
- **Duplicate finder** for big loop folders, S.

## 6. New mixer features
- **Video DJ**: playlist and setlist, BPM detection with beat-matched auto-mix, countdown and clock, "now playing" text from file names, QR code overlay for social links.
- **VJ mixer**: scenes (save a combination of layers and effects, recall with one key), audio-reactive effects from the microphone spectrum, video echo/feedback effects, record the program output.
- **Output to other software**: on Linux, a virtual camera (v4l2loopback) so OBS, Zoom or Resolume can take the mixer picture. NDI is possible with the Linux version but needs extra software.

## 7. Site and growth
- Loop pack pages with video previews, search and filter, per-pack licence (waiting for the Jottacloud links).
- Share cards (Open Graph images) per page, JSON-LD "SoftwareApplication" for the mixers, S.
- Privacy-friendly visitor statistics (GoatCounter or Plausible), S, when you are ready to share the site.
- A GitHub Release with the Linux package, and a "Run it on your computer" section on the About page, S.
- Donation (waiting until you say go).
