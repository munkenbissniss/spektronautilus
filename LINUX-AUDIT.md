# Linux audit, November 2026

What was looked at: the launcher (`linux/spektronautilus.py`), the installer, how the Tools app talks to the local ffmpeg, and which open technology could make the Linux version faster, steadier or lighter.

## Done in this round
| Area | Problem | Change |
|---|---|---|
| Memory (Tools) | Every converted file was read into script memory as a byte array, then copied into a Blob (2 to 3 copies of each result). | `readBlob()`: the browser receives the result as a Blob that it keeps on disk. Used by the main convert path. |
| Graphics card | The earlier freeze came from AI work at full load for hours. | New `/api/gpu` (nvidia-smi: temperature, memory, load). The AI queue waits, up to 5 minutes, while the card is at 80 °C or more, and shows it. |
| Disk | A full /tmp stops ffmpeg half way through. | Uploads that leave less than 500 MB are refused (HTTP 507); free space is shown in `/api/native`; a warning at start below 5 GB. |
| Crash leftovers | A crash left `/tmp/spektronautilus-*` for ever. | Folders older than 6 hours are removed at start; fresh ones (maybe another copy) stay. |
| Hardware encoding | Not used. | Start-up probe encodes a test frame with h264_nvenc, h264_vaapi and h264_qsv; the working ones are reported as `hw`. Not used by the apps yet (see below). |
| Browser | No way to add Chrome options. | `SPEKTRO_CHROME_FLAGS`. |

Tests: `tests_linux.py` (fake nvidia-smi, stale and fresh folders, disk refusal, info fields), plus the full sweep.

## Researched
Checked against sources: Video2X command-line options (docs.video2x.org), NVIDIA VA-API driver and Chrome flags (ubuntuhandbook.org, 2026). The `VaapiOnNvidiaGPUs` feature is marked experimental, so it is documented for experts and not turned on.
From own knowledge, not verified against a source and not tested on real hardware: NVENC/VAAPI/QSV behaviour and the nvidia-smi query fields (the parsing is tested with a fake program).

## Recommendations (not done)
1. **Use the hardware encoder when it works** (opt-in, fall back to libx264 on any error). NVENC is several times faster on an RTX card but a little larger per quality; needs a test on real hardware. M.
2. **Two small ffmpeg jobs in parallel** on machines with 8+ cores. Needs per-item progress. M.
3. **Folder mode**: let the launcher read and write the user's own folders directly, so nothing is copied through the browser. L.
4. **Magic Mixer render with ffmpeg** on Linux (see AUDIT.md item 1). L.
5. **Allow list instead of deny list** for ffmpeg arguments (AUDIT.md item 8). M.
6. Real-world check of Video2X flags and progress output on the RTX 3070.
