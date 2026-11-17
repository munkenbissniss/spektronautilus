"""The real Linux launcher with the fast way: the picture work happens in the browser (graphics card), and the finished frames are
sent to the launcher, where the computer's own ffmpeg (x264, all cores) writes the video. Checks the result against the ffmpeg way
for a few recipes. The browser here cannot read H.264, so the clips are VP9 and the in-between passes are written as VP9 too
(SPK_WC_TEST); the final file is H.264 from x264, as on a real computer. Needs ffmpeg + playwright."""
import json, os, re, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent; T = Path(tempfile.mkdtemp(prefix="spkwcl_")); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *a], check=True)
VP9 = ["-c:v", "libvpx-vp9", "-b:v", "3M", "-deadline", "realtime", "-cpu-used", "8", "-pix_fmt", "yuv420p", "-g", "30"]
ff("-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30:duration=2", *VP9, str(T / "wide.mp4"))
ff("-f", "lavfi", "-i", "testsrc2=size=618x348:rate=25:duration=1", *VP9, str(T / "odd.mp4"))
def probe(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames,codec_name,has_b_frames", "-of", "json", str(p)], capture_output=True, text=True).stdout)["streams"][0]
    a, b = map(int, j["r_frame_rate"].split("/")); return {"w": j["width"], "h": j["height"], "fps": a / b, "n": int(j["nb_read_frames"]), "codec": j["codec_name"], "b": j.get("has_b_frames", 0)}
def psnr(a, b):
    r = subprocess.run(["ffmpeg", "-nostdin", "-i", str(a), "-i", str(b), "-lavfi", "[0:v][1:v]psnr", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"average:([\d.]+|inf)", r); return float(m.group(1)) if m and m.group(1) != "inf" else 99.0
PORT = 8795
srv = subprocess.Popen([sys.executable, str(ROOT / "linux/spektronautilus.py"), "--no-browser", "--port", str(PORT), "--docs", str(ROOT / "docs")], stdout=subprocess.PIPE, text=True, env={**os.environ, "SPEKTRO_VIDEO2X": "/nonexistent"})
INIT = """window.SPK_WC_TEST = { codec: 'vp09.00.40.08', nativeArgs: inter => inter ? ['-c:v', 'libvpx-vp9', '-deadline', 'realtime', '-cpu-used', '8', '-crf', '14', '-b:v', '0', '-g', '8', '-pix_fmt', 'yuv420p'] : null };"""
RUN = r"""async ([bytes, name, patch, tag]) => {
  const WC = await import('/tools/app/wc.js'), ST = await import('/tools/app/steps.js'), L = await import('/tools/app/loops.js'), C = await import('/tools/app/core.js');
  const u8 = Uint8Array.from(atob(bytes), c => c.charCodeAt(0)), file = new File([u8], name, { type: 'video/mp4' }), e = HOSP.engine;
  await e.pick(); const h = await WC.open(file); if (!h) return { error: 'not opened' };
  const R = ST.defaultRecipe(); for (const [k, v] of Object.entries(patch)) R[k] = { ...R[k], ...v };
  const base = { ...C.defaultProfile(), preset: 'fast', maxFps: 60 };
  const t0 = performance.now(), r = await WC.run(h, R, base, { native: e.canEncode ? e : null }), ms = performance.now() - t0;
  await e.write('res_' + tag + '_wc.mp4', r.data);
  const path = await e.mount(file), info = await L.probe(e, path, name);
  const r2 = await ST.runRecipe(e, L, path, 'res_' + tag + '_ff.mp4', info, R, base, {});
  const b64 = async p => { const d = await e.read(p); let s = ''; for (let i = 0; i < d.length; i += 0x8000) s += String.fromCharCode.apply(null, d.subarray(i, i + 0x8000)); return btoa(s); };
  return { note: r.note, ffnote: r2.note, ms, canEncode: !!e.canEncode, wc: await b64('res_' + tag + '_wc.mp4'), ff: await b64('res_' + tag + '_ff.mp4') };
}"""
CASES = [
    ("plain", "wide.mp4", {}),
    ("odd width", "odd.mp4", {}),
    ("60 fps blend + back and forth (two in-between passes)", "wide.mp4", {"fps": {"on": True, "engine": "blend"}, "loop": {"on": True, "mode": "pingpong"}}),
    ("repeat to 7 s (copies, with B-frames)", "wide.mp4", {"out": {"minSeconds": 7}}),
    ("Ken Burns to 6 s", "wide.mp4", {"kb": {"on": True, "minSeconds": 6}}),
]
import base64
try:
    line = srv.stdout.readline(); check(str(PORT) in line, "the launcher starts: " + line.strip())
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_context(accept_downloads=True).new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.add_init_script(INIT)
        pg.goto(f"http://127.0.0.1:{PORT}/tools/hospital/index.html"); pg.wait_for_selector("#picker", state="attached")
        for i, (label, name, patch) in enumerate(CASES):
            tag = f"c{i}"
            try: r = pg.evaluate(RUN, [base64.b64encode((T / name).read_bytes()).decode(), name, patch, tag])
            except Exception as e: check(False, f"{label}: {str(e)[:300]}"); continue
            if r.get("error"): check(False, f"{label}: {r['error']}"); continue
            (T / f"{tag}_wc.mp4").write_bytes(base64.b64decode(r["wc"])); (T / f"{tag}_ff.mp4").write_bytes(base64.b64decode(r["ff"]))
            a, f = probe(T / f"{tag}_wc.mp4"), probe(T / f"{tag}_ff.mp4")
            raw = (T / f"{tag}_wc.mp4").read_bytes()
            check(r["canEncode"] and a["codec"] == "h264" and b"x264" in raw[:200000], f"{label}: written by the computer's own x264 ({a['codec']}, B-frames: {a['b']})")
            same = a["w"] == f["w"] and a["h"] == f["h"] and abs(a["fps"] - f["fps"]) < 0.02 and abs(a["n"] - f["n"]) <= max(2, round(0.02 * f["n"]))
            p = psnr(T / f"{tag}_wc.mp4", T / f"{tag}_ff.mp4")
            check(same, f"{label}: {a['w']}x{a['h']} {a['fps']:.2f} fps {a['n']} frames (ffmpeg way: {f['w']}x{f['h']} {f['fps']:.2f} fps {f['n']} frames), {r['ms']/1000:.1f} s | {r['note'][-70:]}")
            check(p >= (27 if "in-between" in label else 30), f"{label}: picture close to the ffmpeg way (PSNR {p:.1f} dB)")   # the test writes its in-between passes as quick VP9, which costs a little
        # the page itself: examined with the computer's ffmpeg, treated the fast way, written by x264
        pg.set_input_files("#picker", str(T / "wide.mp4")); pg.wait_for_selector("#facts span:not(.muted)", timeout=120000)
        check(pg.is_visible("#fastway") and "loops" in pg.inner_text("#facts").lower() or "jump" in pg.inner_text("#facts").lower(), f"the page examines the clip: {pg.inner_text('#facts')!r}")
        check(pg.evaluate("!!(HOSP.engine && HOSP.engine.kind === 'native')"), "the page runs on the local engine")
        pg.evaluate("HOSP.R.fps.on = true; HOSP.R.fps.engine = 'blend'")
        pg.click("#go"); pg.wait_for_selector("#res a", timeout=600000)
        with pg.expect_download() as dl: pg.click("#res a")
        out = T / "page.mp4"; dl.value.save_as(out); i = probe(out)
        check(i["codec"] == "h264" and abs(i["fps"] - 60) < 0.01 and i["n"] == 120, f"the page's result: {i}")
        check("time:" in pg.inner_text("#res"), f"the result says where the time went: {pg.inner_text('#res')[-120:]!r}")
        left = json.loads(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}/api/native", headers={"X-Spk": "1"})).read())
        check(left.get("enc") is True, "the launcher offers its encoder")
        check(not errs, f"no script errors {errs[:2]}")
        b.close()
finally:
    srv.terminate()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
