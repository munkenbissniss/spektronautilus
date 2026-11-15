# Spektronautilus Output

A native Linux player for the projector, written in Rust. The mixers in the browser will become its remote control; Output decodes
on the graphics card, mixes the layers there and shows the picture in step with the projector's refresh.

**Now: phase 0, a measuring player.** It plays one clip (or a test pattern) full screen with vsync and counts every refresh it
missed. That answers one question before anything else is built: does the picture stutter when the browser is not in the way?

> Status: written without a Rust build here (no access to crates.io in the environment it was written in). GitHub Actions builds
> and tests it on every push (`.github/workflows/output.yml`): without a screen, with software Vulkan, a test pattern and a clip.
> The first run may need small compile fixes. Not tested on a real screen, graphics card or projector.

## Get it

- **Without building:** open the latest run of *Spektronautilus Output (Rust)* under the repository's Actions tab and download
  *spektronautilus-output-linux-x86_64* (Artifacts). Unzip, then `chmod +x spektronautilus-output`.
- **Or build it** (Ubuntu / Pop!_OS):

  ```bash
  sudo apt install build-essential libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev gstreamer1.0-plugins-bad gstreamer1.0-libav
  curl https://sh.rustup.rs -sSf | sh        # Rust, once
  cd output && cargo build --release         # -> target/release/spektronautilus-output
  ```

Hardware decoding: on Intel (X1 Carbon) GStreamer's VA-API decoders come with `gstreamer1.0-plugins-bad` (plus
`intel-media-va-driver-non-free`); on NVIDIA its NVDEC decoders come with the same package and the NVIDIA driver. The report says
which decoder was used.

## Measure (phase 0)

Connect the projector, then:

```bash
./spektronautilus-output --pattern --seconds 120      # 1. the screen alone: a white bar moving 16 pixels per refresh
./spektronautilus-output myloop.mp4 --seconds 600     # 2. one of your loops, looped, for 10 minutes
```

It uses the second screen (the projector) when there is one; `--monitor N` picks another (the list is printed at the start).
`--windowed` runs in a window. Esc or Q stops early. Every 5 seconds a line shows the numbers, and at the end:

- `RESULT: smooth` = no refresh missed, no frame dropped.
- `missed refreshes` = times the picture was not ready for a refresh (shows as a jump). Above 0 with the test pattern means the
  stutter is below any player: driver, power saving, HDMI sound or the projector.
- `refreshes per frame` = how many refreshes each video frame stayed. A 30 fps clip on 60 Hz should show every frame exactly 2;
  a mix of 1 and 3 is judder from the clip's frame rate against the screen's (a 60 fps loop avoids it).
- The full report is saved as `spektronautilus-output-report.json`. Please send it back: it decides phase 1.

Run it on X11 and on Wayland if you can (choose at the login screen), and on both computers.
