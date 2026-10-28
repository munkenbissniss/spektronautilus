=== start
name: Start here
title: Start here: which tool is right for you?
desc: A two-minute overview of Spektronautilus: what each tool does, which one to pick, and what to know before you begin.
summary: A two-minute overview of everything, and which tool to pick.

## What is Spektronautilus {#what}
Spektronautilus is a set of free tools for VJs, visual artists and music lovers. Everything runs in your web browser. Your videos and music stay on your own device and are never uploaded.

## Which tool do I need? {#which}
- You have **a song and some video loops** and want a finished video: [Magic Video Mixer](@guides/magic-mixer/).
- You want to **play music videos at a party or event**, mixing two videos like a DJ: [Video DJ](@guides/video-dj/).
- You want to **play loops live** with pads, layers and beat effects: [VJ Mixer](@guides/vj-mixer/).
- Your loops are in the **wrong format, too big or not seamless**: [Tools](@guides/tools/).
- You started several long jobs and want to follow them: [Queue](@guides/queue/).

## The basics {#basics}
- **Browser.** A recent Chrome or Edge on a computer works best. The mixers also work in other modern browsers, but some features (MIDI, choosing the sound device) need Chrome or Edge.
- **Phone or tablet.** You are sent to a simpler phone version of each mixer automatically. It has fewer features so it runs smoothly.
- [[Video format]]. Use mp4 with H.264. It plays everywhere. If you have other formats, convert them with the [Tools](@guides/tools/).
- **Language.** The website has a language menu in the top right. Inside the mixers and tools, use the 🌐 button.
- **Light or dark.** The mixers and tools have a button to switch the theme.
- **Advanced.** Every tool starts with a few simple choices. The technical settings are folded away under [[Advanced]]. You can ignore them until you need them.

## Before your first show {#show}
Run the [Ready for the show?](@guides/show-check/) check on the computer you will use. It tells you in a minute if the video format, second screen, sound and speed are in order. Then read how to make the site [work without internet](@guides/offline-linux/).

> Keep your tools tested and a backup plan ready. These tools are new, so try everything at home first.

## Stuck? {#stuck}
Look in [Help and troubleshooting](@guides/help/). You can also press the **Feedback** button at the bottom of every page and tell what happened.

=== magic-mixer
name: Magic Video Mixer
title: Magic Video Mixer: turn a song and loops into a video
desc: Add a song and your video loops. The mixer listens to the music, finds the beat and the mood, and cuts the loops together into a finished video.
summary: Add a song and some loops, and get a finished video that follows the music.

## How it works {#how}
You give the mixer one music track and a folder of video loops. It analyses the music (tempo, beat, drops, quiet and loud parts) and your loops (colour, brightness, movement). Then it cuts the loops together so that changes land on the beat and similar loops are used for similar parts of the song.

## Make your first video {#first}
1. **Music.** Drop one audio file (mp3 works best), or press [[choose file]]. The mixer analyses the music and then shows the tempo.
2. **Video loops.** Drop videos or a whole folder. The desktop version takes up to 100 loops. Seamless loops of the same size work best. If your clips do not loop smoothly, fix them first with [[Make loops]] in the [Tools](@guides/tools/).
3. **Mix settings.** Press [[Recommended]]. The mixer looks at the music and your loops and suggests a mood. You can also pick a mood yourself, for example [[Chill]], [[Ambient]] or [[Groove]]. You can still change everything afterwards.
4. **Export.** Press [[Add to export queue]]. The video is made while the page is open.

> The export runs in real time. A 10-minute track takes about 10 minutes. Keep the tab open, and do not expect sound while it works.

## Settings worth knowing {#settings}
Most people never need these. They are under [[Advanced]] sections.
- [[Typical shot length (bars)]] is how long a clip stays on screen, counted in bars. 4 bars is relaxed, 8 bars is slow, 16 to 32 bars is very slow and ambient.
- [[Crossfade length (beats)]] sets how softly one clip melts into the next. 0 is a hard cut.
- [[Loops per section]] is how many loops share one part of the song. 2 gives a calm A-B-A-B.
- [[Style match]] makes the next clip look like the one before, so the mix flows.
- [[Layers & looks]] blend a second clip on top, add a colour tint per section and let the picture breathe with the music.
- [[Motion & effects]] add beat zoom, shake, brightness pulse and echo trails. All are gentle by default.
- [[Use every loop]] tries to show all your loops at least once.
- [[Use CLIP (AI image understanding)]] lets an AI model (CLIP) look at your loops. It downloads about 100 to 150 MB the first time, so use Wi-Fi. It works offline after that.
- [[Seed (empty = random)]]. The same seed and the same settings give the same mix. Use [[Versions]] to make several different mixes at once.

## Export and share {#export}
- **Format.** MP4 (H.264). Choose the size (960×540, 1280×720 or 1920×1080), the frame rate and the quality. 8 Mbit/s is about 600 MB for 10 minutes.
- **Where the video is.** Finished videos stay inside the page until you download or remove them. [[Storage in this browser]] shows how much space they use, and [[Delete all stored videos]] clears it.
- [[Upload to Vimeo (optional)]]. Paste your own Vimeo access token. It is kept only in your browser and sent only to Vimeo. Videos are private by default.
- **Follow the jobs** on the [Queue](@guides/queue/) page.

## The phone version {#phone}
The phone version is made for a phone. Choose a track and some videos, pick a mood and a shape (landscape or portrait), and press [[Make video]].
- Keep the page open and the screen on while the video is made. On an iPhone, turn off Low Power Mode first, because it stops videos from playing.
- If the phone struggles or the page reloads, choose 30 or 24 frames per second, a smaller size, fewer loops or a shorter track.
- [[Smarter matching (AI)]] is heavy for a phone. Turn it off if the page reloads by itself.
- If something is interrupted, the page offers to download what was saved ([[Download recovered video]]).

## Tips {#tips}
- Use loops of the same size and frame rate. Mixed sizes work, but it is calmer when they match.
- Start with 720p. Go higher only when you need it.
- Not happy with the result? Press [[Recommended]] again, change the mood, or use another seed.
- Something wrong? See [Help and troubleshooting](@guides/help/).

=== video-dj
name: Video DJ
title: Video DJ: mix music videos on two decks
desc: Mix complete music videos like a DJ, with two decks, a crossfader, a preview, a logo, text posters, MIDI and a clean output window for your projector.
summary: Mix music videos on two decks with a crossfader, made for events.

## What it is {#what}
Video DJ has two decks for music videos (mp4, mov, webm). Picture and sound mix together. You see a preview of both decks next to the output, and a separate output window goes to the projector or TV.

> The tool is made for a computer with Chrome or Edge. On a phone you get a simpler version with two decks, a crossfader, effects, posters and a way to send the picture to another screen.

## Your first mix {#first}
1. **Add videos.** Drop music videos on the page, or press [[Add files…]]. Names like “Artist - Title.mp4” turn into poster text. Drop a video straight onto a deck to load it at once.
2. **Load the decks.** Put a video on deck A and one on deck B. Press play on each.
3. **Open the output window.** Press [[Open output window]], drag the new window to the projector and press {{F}} for full screen. Keep the control window open during the show.
4. **Mix.** Move the crossfader by hand, or press [[Mix to other deck (auto fade)]] for a smooth fade. [[Fade time]] sets how long it takes.

## Auto-mix {#automix}
Switch on [[Auto-mix to the next track]] and the mixer starts the next track on the idle deck for you, a number of seconds before the current one ends. You set that number. Use it for long sets, or to take a break.

## Sound {#sound}
- [[Sound follows the crossfader]] fades the sound together with the picture.
- [[Smooth (equal power)]] or [[Linear]] sets the curve of the sound fade.
- A soft limiter on the master stops two loud tracks from clipping when they overlap.
- [[Sound output]] lets you pick another sound device (Chrome or Edge).

## Logo and posters {#posters}
- **Logo.** Add a PNG with transparency (it works best). The logo sits in the upper right corner of the picture. Choose its size, and switch it on and off with one button.
- **Posters.** A poster is sliding text with a big line and a small line. Choose a colour preset, where it slides in from and how long it stays. Save posters in slots and show them with one click or key.
- **Track name.** Switch on [[Show the track name when a track mixes in]] and the poster appears by itself.

## MIDI controller {#midi}
Plug in your controller, press [[Enable MIDI]] (Chrome or Edge on a computer), then press [[Learn]] next to a function and move the control you want to use.

## Record and stream {#record}
- [[● Record]] saves the mix, picture and sound, to a file.
- To stream, capture the output window in OBS (Window Capture), or use Chrome’s “Cast…” and choose the output window. The mixer does not send video over the internet by itself.

## Built to not crash {#safe}
- Tracks are loaded fully into memory before they play (files over 1.5 GB are streamed instead), so the disk cannot interrupt a track.
- A problem with one file shows a message and never stops the other deck.
- The picture keeps running when the control window is in the background, and closing the window by mistake asks first.
- Run the [Ready for the show?](@guides/show-check/) check before every event.

## The phone version {#phone}
Two decks, a crossfader, effects (Zoom, Flash, Strobe, Invert, Mirror), posters and full screen. To show the picture on another screen, open [[Send to another screen]]: make a code, open the link on the other screen (a laptop, a TV browser or a projector computer on the same Wi-Fi), and paste the answer code. Nothing goes through a server.

> Flashing effects can trigger seizures in some people. Keep them slow at public events.

=== vj-mixer
name: VJ Mixer
title: VJ Mixer: play loops live with pads and layers
desc: Play your loops live. Two channels with three layers each, 20 loop pads, a crossfader and beat effects that follow the tempo.
summary: Play loops live on 20 pads with layers, a crossfader and beat effects.

## What it is {#what}
The VJ Mixer is for playing short video loops live. You have 20 pads, two channels (A and B) with three layers each, a crossfader, and simple effects that follow the beat. Loops play without sound.

> It is made for a computer with Chrome or Edge. On a phone you get a smaller version with 8 pads and 2 layers per channel.

## Fill the pads {#pads}
Drop loop files on the pad grid, or press [[Add loops…]]. They fill the empty pads. Use mp4 (H.264) loops for the smoothest playback. To reuse them next time, switch on [[Remember my loops on this computer]]. They are stored in this browser only.

## Play {#play}
1. **Pick a layer.** Each channel has three layers. Select the layer you want to play on.
2. **Press a pad** (or its key on the keyboard). The loop starts on the selected layer at once.
3. **Mix the layers.** Each layer has its own opacity and a blend mode: normal, add, screen or multiply.
4. **Mix the channels.** Use the crossfader, or [[Mix to other channel (auto fade)]]. [[Clear layer]] empties a layer.

## The beat {#beat}
The effects follow a beat. You can set it in three ways:
- **Tap** the tempo button a few times, or type the **BPM**.
- Let the mixer **listen to the kick drum** through an audio input ([[Audio input (kick drum)]]). Use [[Sensitivity]] to tune it.
- Press [[Set beat 1 (downbeat)]] on the moment that should count as the first beat of a bar.

## Beat effects {#effects}
Zoom, Shake, Flash, Strobe, Invert, Mirror, Colour spin and Blur. Switch each one on, choose how often it pulses (every beat, 2 beats or 4 beats) and how strong it is.

> Flash, Strobe and Invert at a fast tempo can trigger seizures in some people. Keep it slow at public events.

## Logo, posters, MIDI and output {#more}
These work like in the [Video DJ](@guides/video-dj/#posters): a logo, sliding text posters, MIDI control with [[Learn]], and an output window for the projector (press {{F}} for full screen). To stream, capture the output window in OBS or use Chrome’s “Cast…”.

## The phone version {#phone}
8 pads, two layers per channel, a crossfader and effects, with the same beat tools. It also plays loops without sound.

## Loops too heavy? {#heavy}
Use mp4 (H.264) at 720p or 1080p. Convert other formats and shrink big files with the [Tools](@guides/tools/). Run the [Ready for the show?](@guides/show-check/) check to see how smooth your computer is.

=== tools
name: Loop tools
title: Loop tools: convert, fix, filter and organise your loops
desc: Free browser tools for VJ loops: convert GIFs and videos, make seamless loops, crop, resize, add looks, find free loops and bundle packs.
summary: Convert, loop, crop, filter, find and pack your video loops.

## How the tools work {#how}
Open the tools and pick one from the list. Every tool follows the same pattern:
1. **Add files.** Drop files or a folder, or press [[choose files]].
2. **Settings.** A few simple choices. The technical settings are under [[Advanced]].
3. **Start.** The work becomes jobs in a job list. You can queue many files and let it run. See the [Queue](@guides/queue/).
4. **Download.** Results are plain mp4 files you can use in any VJ software.

Everything runs inside your browser and your files never leave your computer. Big files are fine, they are read straight from the disk. In Chrome or Edge you can also pick a folder and save each result straight into it ([[Save each file straight into a folder I choose]]).

> The browser version is slower than a desktop program (about 5 to 10 times). For many large 4K files use the [Linux version](@guides/offline-linux/#linux), which uses the fast engine on your own computer.

## GIF to MP4 {#gif2mp4}
Converts many GIFs to smooth mp4 at once, also GIFs with transparency. For transparent GIFs, choose a background colour (black, white or #rrggbb). [[Keep shape, only shrink]] keeps small GIFs small. [Open this tool](@@tools/app/#gif2mp4).

## Make loops {#loop}
Checks whether a clip already loops. If it does, it is left alone. If not, it can trim the clip to the best loop point, play it forward and then backward, or crossfade the end into the start. [[Auto: keep good loops, otherwise fix them]] picks for you: keep good loops, fix the others. You can also set a minimum length, because the Magic Video Mixer likes loops of 16 seconds or more. [Open this tool](@@tools/app/#loop).

## Convert {#convert}
Turns mov, webm, mkv, gif and other formats into VJ-friendly mp4. Choose size, frame rate and quality, and use a [[Name template]] to rename in bulk. The template understands tokens such as `{name}`, `{n}`, `{n2}` (a number with two digits), `{w}`, `{h}`, `{res}`, `{fps}`, `{dur}` and `{date}`. You can also remove spaces, switch to lowercase and replace æøå. [Open this tool](@@tools/app/#convert).

## Find loops {#search}
Search free sources for loops, then download and convert them in one go. Internet Archive, Wikimedia Commons, NASA and the Prelinger Archives work without an account. Pexels and Pixabay have many ready-made loops, but need a free key, which takes a minute. The key is stored only in your browser and is sent only to that site.
- The author and licence of every download are saved in a file called `credits.csv`. Licences differ per clip, so check them before you use a clip in public.
- Some sites do not let a web page download their files. Then use [[Open page]], download the clip yourself and drop it into [[Convert]].
- Only download things you have the right to use.

[Open this tool](@@tools/app/#search).

## Filters {#filters}
Adds VJ-style looks to a whole folder of loops: glow, glitch, mirror, kaleidoscope, VHS, duotone, pixelate, trails and more. Press [[Preview on first clip]] to see each look before you apply them. Every file gets one new clip per look you pick. [Open this tool](@@tools/app/#filters).

## Crop & trim {#crop}
Cuts clips to widescreen, vertical or square, and trims the start and the end, for a whole folder at once. Choose how to fit: crop to exactly the box, or letterbox with bars. [Open this tool](@@tools/app/#crop).

## Sizes {#sizes}
Makes a small proxy, 720p, 1080p and 4K of every clip in one go. Sizes larger than the original are skipped. [Open this tool](@@tools/app/#sizes).

## HAP / ProRes {#pro}
Makes professional formats for Resolume, VDMX, Millumin and video editors. This needs the local [Linux version](@guides/offline-linux/#linux), because it uses ffmpeg on your own computer. [Open this tool](@@tools/app/#pro).

## AI upscale {#ai}
Makes video clips sharper and larger with AI, using the free program Video2X. It works only in the local [Linux version](@guides/offline-linux/#linux) and needs a graphics card with Vulkan support. Your files never leave your computer.

How to use it:
1. Install Video2X yourself (an AppImage, the AUR package, or your own build). Spektronautilus finds it by itself. If it does not, set the path in the `SPEKTRO_VIDEO2X` variable and start Spektronautilus again.
2. Open the tool and add your clips. The note above the settings says whether Video2X was found.
3. Choose [[Kind of picture]] and [[Make it this much bigger]], then press [[Upscale]].

Good to know:
- It is slow. A short clip can take many minutes, so use the [Queue](@guides/queue/) and let it run.
- Photos and real film are always made 4× bigger. The result may not be larger than 8K.
- Have more than one graphics card? Press [[Check my graphics card]] and set [[Graphics card number]].

## Catalogue {#catalog}
Makes a web page and a spreadsheet file with a picture, the length, the size and the loop quality of every loop. Good for big collections. [Open this tool](@@tools/app/#catalog).

## Loop pack {#pack}
Bundles loops into a zip you can share, with a preview picture, an information file and a licence. [Open this tool](@@tools/app/#pack).

## Good to know {#know}
- Loops normally have no sound. [[Keep sound]] is off by default.
- Short loops give smooth scrubbing and looping in VJ software.
- If something fails, the job shows the reason. See [Help and troubleshooting](@guides/help/).

=== queue
name: Queue
title: Queue: follow all your jobs in one place
desc: The Queue page shows all jobs from the tools and the Magic Video Mixers in one list, so you can follow long exports and download the results.
summary: All jobs from the tools and mixers in one list.

## What the Queue is {#what}
Every long task, such as converting 200 files or exporting a 10-minute video, becomes a job. The Queue page shows all the jobs from the tools and from both Magic Video Mixers in one place, with their status: waiting, running, done or failed.

## How to use it {#use}
1. Start jobs in a tool or in the Magic Video Mixer.
2. Open the [Queue](@@queue/) from the top menu. A small number next to [[Queue]] tells you how many jobs are running right now.
3. Download finished files from the list when they are done.
4. Press [[Clear finished]] to tidy up.

> Jobs run in the page that started them. **Keep that page open** until it says done. The Queue page is a window onto the jobs, it does not run them.

## Where do the files go? {#files}
Finished files from the tools are kept in this browser, up to about 600 MB per job, so you can download them later. The Magic Video Mixer keeps its own videos on its own page, so use [[Open page]] from the Queue to download those. Nothing leaves your computer.

If a file is no longer stored, the Queue says so, and you can run the job again.

=== show-check
name: Ready for the show?
title: Ready for the show? Check your device before you go live
desc: A one-minute check of your computer and browser before an event: video format, second screen, sound, battery, speed and more.
summary: A one-minute check of your device before you go live.

## What it is {#what}
Inside Video DJ, the VJ Mixer and their phone versions you find [[Ready for the show?]]. It checks your device and browser in a minute and tells you what to fix before the audience arrives. Nothing is sent anywhere.

## How to use it {#use}
1. Open the mixer on the computer you will use at the event, with the projector connected.
2. Open [[Ready for the show?]] and read the list. Each line is [[OK]], [[Check]], [[Problem]] or [[Info]].
3. Fix what needs fixing, and press [[Run the check again]].
4. Press [[Show test card]] to see that the picture fits the projector.

## What each line means {#lines}
- [[Video format]]. Whether the browser plays mp4 (H.264), which the mixers like best. If not, use Chrome, Edge or Safari, or convert your videos with the [Tools](@guides/tools/).
- [[Works without internet]]. Whether the site is saved for offline use. See [Offline and Linux](@guides/offline-linux/).
- [[Screen stays awake]]. Whether the browser can stop the screen from going to sleep. If not, turn off the screen saver and sleep in your system settings.
- [[Pop-up windows]]. The output window is a pop-up. If the browser blocks pop-ups, the output window cannot open.
- [[Second screen]]. Whether a second screen is found. Connect the projector first.
- [[Full screen]] and [[MIDI controller]]. Whether they are available, and whether a controller is connected.
- [[Sound]]. Whether sound is ready.
- [[Battery]]. Warns if the battery is low. Plug in before the show.
- [[Speed]]. A short test of how many frames per second the screen can draw. If it is slow, close other tabs and programs and use a smaller picture size.
- [[Free space]]. Warns when there is little disk space for recording.
- [[Output window]], loops and tracks. Whether the output window is open and whether anything is loaded.

## The test card {#card}
[[Show test card]] opens a picture made for projectors. If you see a round circle, all four corners and the pink frame, the picture fits the screen. Press {{F}} for full screen and {{Esc}} or click to close it.

## Ask for help with a report {#report}
[[Copy report]] copies a short plain-text summary of your device. Paste it in a message when you ask for help with the [Feedback](@guides/help/#feedback) button.

=== offline-linux
name: Offline and Linux
title: Use Spektronautilus offline, install it and run it on Linux
desc: How to make the site work without internet at the venue, install it like an app, and run the whole site locally on Linux for more speed and stability.
summary: Work without internet, install the site like an app, or run it locally on Linux.

## Work without internet {#offline}
Spektronautilus saves itself in your browser, so it also works without Wi-Fi at the venue.
1. Open the site once while you are online.
2. Wait a minute. The pages and the mixers are being saved.
3. Run [Ready for the show?](@guides/show-check/) and check the line [[Works without internet]].

You can also **install** the site as an app: use “Install” or “Add to home screen” in your browser menu. It then opens in its own window.

> The Tools load their video engine (about 30 MB) the first time you use them. Use each tool once while you are online. The Linux version does not need that engine.

## Updates {#updates}
When a new version is ready, a small bar says [[A new version is ready.]] with the buttons [[Update now]] and “Later”. It never updates by itself while the page is open, so a running show is never disturbed. Update before the event, not during it.

## Linux version {#linux}
There is a version that runs the whole site on your own Linux computer. It is only reachable from your computer (address 127.0.0.1), and it opens in Chrome or Chromium in its own window, started with settings made for live visuals.

Why use it:
- **Speed.** If `ffmpeg` is installed, the tools use it instead of the slower browser engine. The page then says “Fast mode”.
- **No memory limit** for big files, and no internet is needed (only [[Find loops]] needs it).
- **HAP and ProRes.** The [HAP / ProRes tool](@guides/tools/#pro) works in the Linux version.
- **AI upscaling.** The [AI upscale tool](@guides/tools/#ai) uses Video2X, if you have installed it.

How to install:
1. Download the Linux package (`spektronautilus-linux.tar.gz`) and unpack it: `tar xzf spektronautilus-linux.tar.gz`.
2. Go into the folder and run `./install.sh`. It needs no root rights. It adds a menu entry and a `spektronautilus` command, with shortcuts to Video DJ, VJ Mixer and the loop tools.
3. To try it without installing, run `./spektronautilus.py` in the unpacked folder.
4. `./uninstall.sh` removes it again.

You need Python 3.8 or newer and, for the mixers, Chrome or Chromium. To get ffmpeg on Debian or Ubuntu, run `sudo apt install ffmpeg`.

## Safe by design {#safe}
The local server accepts only requests from your own computer, refuses other website names, and only lets ffmpeg touch its own temporary folder, which it deletes when you close it.

=== help
name: Help and troubleshooting
title: Help and troubleshooting: when something does not work
desc: Answers to common problems: videos that will not play, the output window, stutter, a phone that reloads, MIDI, lost files and how to get in touch.
summary: Answers to common problems, and how to get in touch.

## A video will not play {#play}
Almost always a format problem. The mixers like **mp4 with H.264**. Convert the file with [[Convert]] in the [Tools](@guides/tools/). iPhone videos in HEVC, some mov files and webm files can be a problem in some browsers.

## There is no sound {#sound}
- Loops in the VJ Mixer play without sound on purpose.
- In Video DJ, check the volume of the deck, the master and [[Sound follows the crossfader]].
- The browser may need a click on the page before it plays sound. Click once on the page.
- Check [[Sound output]] if you use more than one sound device.

## The output window does not open {#output}
The browser blocked the pop-up. Allow pop-ups for the site and try again. The [Ready for the show?](@guides/show-check/) check tests this.

## The picture stutters {#stutter}
- Choose a smaller picture size (the output size) and use 720p loops.
- Close other tabs and programs.
- Use a recent Chrome or Edge, and plug the computer in.
- Run the speed test in [Ready for the show?](@guides/show-check/).
- On a laptop, make sure the browser uses the strong graphics card.

## My phone reloads the page {#phone}
The phone ran out of memory or the screen locked. Use a smaller size, 30 or 24 frames per second, fewer or shorter loops, and keep the screen on. On an iPhone, turn off Low Power Mode. In the Magic Video Mixer, switch off [[Smarter matching (AI)]].

## The export stopped or is very slow {#export}
Exports run in real time, so a 10-minute track needs about 10 minutes. Keep the tab open and visible, and do not let the computer sleep. If it was interrupted, the Magic Video Mixer offers to recover what was saved.

## MIDI does not find my controller {#midi}
Use Chrome or Edge on a computer. Plug in the controller first, then press [[Enable MIDI]] and allow it in the browser. Other programs that use the controller can block it, so close them.

## Where are my files? {#files}
In your browser, on your computer. Finished tool results and Magic Mixer videos are listed on the [Queue](@guides/queue/) page. If you clear the site data of your browser, they are gone, so download what you want to keep.

## Privacy {#privacy}
No accounts and no tracking. Videos and music are processed on your device. Searching for loops contacts the video sources you pick, and the optional Vimeo upload contacts Vimeo.

## Get in touch {#feedback}
Press the **Feedback** button, at the bottom of every page, and write what happened. It opens your email program with the message filled in. Add what browser you use and what you were doing. For a problem on a show computer, add the report from [Ready for the show?](@guides/show-check/#report). You can also write to us on [GitHub](https://github.com/munkenbissniss/spektronautilus/issues).
