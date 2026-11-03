"""Browser test of the sound sources of the VJ mixer: choosing an input, an audio file played in the mixer (the beat follows it), shared tab sound
(only the failure path: a real shared tab needs a person), and sound in the recording. NOT tested: a real microphone, a real PipeWire/Pulse monitor input."""
import functools, http.server, subprocess, tempfile, threading, math, struct, wave
from pathlib import Path
ROOT = Path(__file__).resolve().parent; DOCS = ROOT / "docs"; T = Path(tempfile.mkdtemp(prefix="spkvjsnd_")); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
# a 16 s "kick drum" at 100 BPM: a 60 Hz burst every 0.6 s
def kick_wav(path, bpm, secs):
    sr = 22050; n = sr * secs; per = int(sr * 60 / bpm); out = bytearray()
    for i in range(n):
        k = i % per; v = math.sin(2 * math.pi * 60 * k / sr) * math.exp(-k / (sr * 0.08)) * 0.9 if k < sr * 0.4 else 0
        out += struct.pack("<h", int(v * 30000))
    with wave.open(str(path), "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(out))
kick_wav(T / "Kick 100.wav", 100, 16); kick_wav(T / "Second.wav", 100, 3)
loop = T / "Red Loop.webm"; subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=0xff0000:s=320x180:r=25:d=2", "-c:v", "libvpx", "-b:v", "200k", str(loop)], check=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(DOCS))); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{srv.server_port}/vj-pad/index.html"
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required", "--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream"])
    ctx = b.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True, permissions=["microphone"]); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: d.accept())
    pg.goto(URL); pg.wait_for_selector("#pads .pad")
    check(len(pg.locator("#bsrc option").all()) == 4 and not pg.is_visible("#audioRow"), "four beat sources; the sound row is hidden until a source needs it")
    # --- input device list
    pg.select_option("#bsrc", "audio"); pg.wait_for_function("SPK.S.mic && SPK.S.mic.st", timeout=10000)
    pg.wait_for_function("document.querySelectorAll('#adev option').length>1", timeout=10000)
    n = pg.locator("#adev option").count(); check(pg.is_visible("#adev") and n >= 2, f"microphone: an input list appears ({n} entries)")
    dev = pg.evaluate("[...document.querySelectorAll('#adev option')].map(o=>o.value).filter(Boolean)[0]")
    pg.select_option("#adev", dev); pg.wait_for_function("SPK.S.mic && SPK.S.mic.st && SPK.S.mic.st.getAudioTracks()[0].getSettings().deviceId", timeout=10000)
    check(pg.evaluate("SPK.cfg.adev") == dev and pg.evaluate("SPK.S.mic.st.getAudioTracks()[0].getSettings().deviceId") == dev, "choosing an input switches to it and remembers it")
    # --- audio file
    pg.select_option("#bsrc", "file"); pg.wait_for_selector("#afileRow", state="visible")
    check(pg.is_visible("#aPlay") and not pg.is_visible("#adev"), "audio file: player shown, input list hidden")
    pg.set_input_files("#aFiles", [str(T / "Kick 100.wav"), str(T / "Second.wav")]); pg.wait_for_function("SPK.S.mic && document.querySelector('#aInfo').textContent.includes('Track 1 of 2')", timeout=10000)
    check("Kick 100.wav" in pg.inner_text("#aInfo"), "two files are queued: " + pg.inner_text("#aInfo"))
    pg.click("#aPlay"); pg.wait_for_function("document.querySelector('#aPlay').textContent==='Pause'", timeout=10000)
    pg.evaluate("SPK.setBpm(140)"); pg.wait_for_timeout(11000)
    bpm = pg.evaluate("SPK.S.bpm"); cnt = pg.evaluate("SPK.S.kick.count")
    check(cnt >= 8 and 90 <= bpm <= 110, f"the beat follows the file: {cnt} kicks, tempo {bpm} (file is 100 BPM, it started at 140)")
    check("0:" in pg.inner_text("#aInfo") and "/" in pg.inner_text("#aInfo"), "time is shown: " + pg.inner_text("#aInfo"))
    pg.click("#aNext"); pg.wait_for_timeout(600); check("Track 2 of 2" in pg.inner_text("#aInfo"), "Next track works")
    pg.click("#aPrev"); pg.wait_for_timeout(600); check("Track 1 of 2" in pg.inner_text("#aInfo"), "Previous track works")
    pg.click("#aPlay"); pg.wait_for_timeout(300); check(pg.inner_text("#aPlay") == "Play", "Pause works")
    # --- recording with sound
    pg.click("#advBtn"); pg.set_input_files("#files", [str(loop)]); pg.wait_for_function("SPK.S.pads.filter(p=>p&&p.ready).length==1", timeout=10000)
    pg.click("#pads .pad >> nth=0"); pg.click("#aPlay"); pg.check("#recAudio")
    pg.click("#recBtn"); pg.wait_for_timeout(3000); pg.click("#recBtn"); pg.wait_for_function("SPK.S.recFile", timeout=15000)
    with pg.expect_download() as d: pg.click("#recSave")
    f = T / d.value.suggested_filename; d.value.save_as(f)
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout.split()
    check("audio" in pr and "video" in pr, f"the recording has picture and sound {pr}")
    pg.uncheck("#recAudio"); pg.click("#recBtn"); pg.wait_for_timeout(1500); pg.click("#recBtn"); pg.wait_for_function("!SPK.S.rec && SPK.S.recFile.name", timeout=15000)
    with pg.expect_download() as d: pg.click("#recSave")
    f2 = T / ("b_" + d.value.suggested_filename); d.value.save_as(f2)
    pr2 = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(f2)], capture_output=True, text=True).stdout.split()
    check("audio" not in pr2, f"without the tick the recording has no sound {pr2}")
    # recording with the tick but no source: a clear note
    pg.select_option("#bsrc", "clock"); pg.wait_for_timeout(300); pg.check("#recAudio"); pg.click("#recBtn"); pg.wait_for_timeout(300)
    check("no sound" in pg.inner_text("#toast"), "tick but no sound source: it says so"); pg.click("#recBtn"); pg.wait_for_function("!SPK.S.rec", timeout=10000)
    # --- shared tab sound: in the test browser nothing with sound can be shared, so the failure must be clear and harmless
    pg.evaluate("navigator.mediaDevices.getDisplayMedia = async () => { const c = document.createElement('canvas'); c.width = 8; c.height = 8; return c.captureStream(5); }")
    pg.select_option("#bsrc", "share"); pg.wait_for_function("document.querySelector('#bnote').textContent.includes('No sound')", timeout=10000)
    check("No sound was shared" in pg.inner_text("#bnote") and pg.input_value("#bsrc") == "clock", "sharing without sound falls back to tap tempo with an explanation")
    pg.evaluate("navigator.mediaDevices.getDisplayMedia = async () => { const ac = new AudioContext(); const d = ac.createMediaStreamDestination(); const o = ac.createOscillator(); o.connect(d); o.start(); const c = document.createElement('canvas'); c.width = 8; c.height = 8; const v = c.captureStream(5); d.stream.getAudioTracks().forEach(t => v.addTrack(t)); return v; }")
    pg.select_option("#bsrc", "share"); pg.wait_for_timeout(800)
    check(pg.evaluate("SPK.cfg.bsrc") == "share" and pg.evaluate("!!SPK.S.mic") and "Sharing sound" in pg.inner_text("#bnote"), "shared sound with an audio track is taken in (simulated share)")
    pg.select_option("#bsrc", "clock"); pg.wait_for_timeout(300); check(pg.evaluate("SPK.S.mic") is None, "back to tap tempo releases the sound")
    check(not errs, f"no script errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
