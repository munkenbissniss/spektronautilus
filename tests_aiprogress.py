"""True progress (the result is longer than the input) and the graphics card choice for AI. Stand-in ffmpeg, no real video needed."""
import json, os, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent; T = Path(tempfile.mkdtemp(prefix="spkprog_")); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
BIN = T / "bin"; BIN.mkdir()
(BIN / "ffmpeg").write_text('''#!/usr/bin/env python3
import sys, time
a = sys.argv[1:]
if "-version" in a: print("ffmpeg version 6.0-standin"); sys.exit(0)
if "-encoders" in a: print(" V....D libx264              libx264 H.264"); sys.exit(0)
e = sys.stderr
e.write("  Duration: 00:00:02.00, start: 0.000000, bitrate: 500 kb/s\\n"); e.flush()
for t in (1, 2, 4, 6, 8):
    time.sleep(0.15); e.write("frame=  10 fps=25 q=28.0 size=  10kB time=00:00:%02d.00 bitrate=100kbits/s speed=1x\\r" % t); e.flush()
e.write("video:10kB audio:0kB\\n"); sys.exit(0)
''')
(BIN / "ffmpeg").chmod(0o755)
port = 8794
env = {**os.environ, "PATH": f"{BIN}:/usr/bin:/bin", "HOME": str(T), "SPEKTRO_VIDEO2X": str(T / "nope")}
srv = subprocess.Popen([sys.executable, str(ROOT / "linux/spektronautilus.py"), "--no-browser", "--port", str(port), "--docs", str(ROOT / "docs")], stdout=subprocess.PIPE, text=True, env=env)
srv.stdout.readline(); srv.stdout.readline()
def prog(expect):
    h = {"X-Spk": "1", "Content-Type": "application/json"}
    if expect: h["X-Spk-Expect"] = str(expect)
    ps = []
    with urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{port}/api/exec", data=json.dumps(["-i", "a.mp4", "o.mp4"]).encode(), method="POST", headers=h), timeout=30) as x:
        for l in x:
            m = json.loads(l)
            if "p" in m: ps.append(m["p"])
    return ps
try:
    old = prog(0); new = prog(8)
    check(old and old[-1] == 1.0 and sum(1 for p in old if p >= 1.0) >= 1 and old.index(1.0) <= 2, f"without the expected length the bar is full early: {old}")
    check(new and new[0] < .2 and 1.0 not in new[:-1] and new == sorted(new) and new[-1] == 1.0, f"with the expected length the bar follows the real work: {new}")
finally: srv.terminate()
# the page side: expected length on the arguments, graphics card choice
js = r"""
import { encodeArgs, aiDevice, defaultProfile } from './docs/tools/app/core.js';
const out = [], ok = (c, m) => out.push((c ? 'ok   ' : 'FAIL ') + m);
const prof = { ...defaultProfile(), fps: 25 };
let a = encodeArgs('i.mp4', 'o.mp4', prof, { width: 640, height: 360, duration: 4, fps: 25 }, { repeat: 4 });
ok(a.expect === 16 && JSON.stringify(a).indexOf('expect') < 0, 'a clip repeated 4 times is expected to be 16 s, and the number is not sent to ffmpeg');
a = encodeArgs('i.mp4', 'o.mp4', prof, { width: 640, height: 360, duration: 8, fps: 25 }, { limit: 3 });
ok(a.expect === 3, 'a cut of 3 s is expected to be 3 s');
a = encodeArgs('i.mp4', 'o.mp4', prof, { width: 640, height: 360, duration: 8, fps: 25 }, { trimFrames: 50 });
ok(Math.abs(a.expect - 2) < .01, 'a trim to 50 frames at 25 fps is expected to be 2 s');
const eng = lines => ({ info: { v2x: { ok: true, dev: '-d' } }, async v2xGpus() { return { ok: true, lines }; } });
let d = await aiDevice(eng(['0. llvmpipe (LLVM 15.0.7, 256 bits)', '1. Intel(R) UHD Graphics 620 (KBL GT2)', '2. NVIDIA GeForce MX150']));
ok(d.args.join(' ') === '-d 2', 'a discrete card is chosen over the software driver and the Intel one: ' + d.args.join(' ') + ' ' + d.name);
d = await aiDevice(eng(['0: llvmpipe (LLVM 15)', '1: Intel(R) UHD Graphics 620']));
ok(d.args.join(' ') === '-d 1' && !d.soft, 'without a discrete card the Intel one is used, not llvmpipe');
d = await aiDevice(eng(['0. llvmpipe (LLVM 15)']));
ok(d.soft && d.args.length === 0, 'only a software driver: it is reported, and nothing is forced');
d = await aiDevice(eng([]));
ok(d.args.length === 0 && !d.soft, 'no list: Video2X chooses');
d = await aiDevice(eng(['0. llvmpipe']), 3);
ok(d.args.join(' ') === '-d 3', 'a number typed by the user wins');
console.log(out.join('\n'));
"""
(T / "u.mjs").write_text(js.replace("'./docs/", f"'{ROOT}/docs/"))
r = subprocess.run(["node", str(T / "u.mjs")], capture_output=True, text=True, cwd=str(T)); print(r.stdout, r.stderr[-400:])
bad += [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
print("\nALL OK" if not bad and "ok" in r.stdout else f"\n{len(bad)} FAILED"); sys.exit(1 if bad or not r.stdout else 0)
