"""Loop Hospital: Convert GIF to MP4 at the top of the patient, then the converted clip can be treated (computer's own ffmpeg as the engine)."""
import base64, functools, http.server, json, os, re, shutil, subprocess, tempfile, threading, zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent
T = Path(tempfile.mkdtemp(prefix="spknew_")); IN, FS = T / "in", T / "fs"; IN.mkdir(); FS.mkdir()
bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *a], check=True)
ff("-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=30:duration=3", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "wide clip.mp4"))
def host(op, a=None, b=None):
    if op == "exec":
        r = subprocess.run(["ffmpeg", "-nostdin", *json.loads(a)], cwd=FS, capture_output=True)
        return json.dumps({"code": r.returncode, "log": [l for l in re.split(r"[\r\n]+", r.stderr.decode("utf-8", "replace")) if l]})
    if op == "write": p = FS / a; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(base64.b64decode(b)); return ""
    if op == "read": return base64.b64encode((FS / a).read_bytes()).decode()
    if op == "remove": (FS / a).unlink(missing_ok=True); return ""
    if op == "rmdir": shutil.rmtree(FS / a, ignore_errors=True); return ""
    raise ValueError(op)
ENGINE_JS = r"""(() => { const b64 = u8 => { let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); };
  const un64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0)); let n = 0;
  window.__VJ_ENGINE__ = { kind: 'wasm', async load() {}, async exec(args) { return JSON.parse(await window.host('exec', JSON.stringify(args))); },
    async write(p, u8) { await window.host('write', p, b64(u8)); }, async read(p) { return un64(await window.host('read', p)); }, async remove(p) { await window.host('remove', p); },
    async mount(file) { const d = 'm' + (++n); await window.host('write', d + '/' + file.name, b64(new Uint8Array(await file.arrayBuffer()))); return d + '/' + file.name; },
    async unmount(p) { await window.host('rmdir', p.split('/')[0]); }, terminate() {} }; })();"""
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{srv.server_port}/tools/app/index.html"
ff("-f", "lavfi", "-i", "testsrc2=size=240x136:rate=10:duration=2", "-vf", "split[a][b];[a]palettegen[p];[b][p]paletteuse", str(IN / "spin.gif"))
URL = f"http://127.0.0.1:{srv.server_port}/tools/hospital/index.html"
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context().new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(ENGINE_JS); pg.expose_function("host", host)
    pg.goto(URL); pg.wait_for_selector("#picker", state="attached")
    check(pg.locator("#gifbar").count() == 1 and "hide" in (pg.get_attribute("#gifbar", "class") or ""), "the convert bar is hidden before a clip is chosen")
    pg.set_input_files("#picker", str(IN / "wide clip.mp4"))
    pg.wait_for_selector("#facts span:not(.muted)", timeout=60000)
    check(pg.is_hidden("#gifbar"), "an mp4 gets no convert button")
    pg.set_input_files("#picker", str(IN / "spin.gif"))
    pg.wait_for_selector("#gifbar:not(.hide)", timeout=60000)
    check(pg.is_visible("#gif2mp4"), "a GIF shows the Convert GIF to MP4 button")
    check(pg.evaluate("document.querySelector('#gifbar').compareDocumentPosition(document.querySelector('.pv')) & 4") > 0, "the button sits above the video window")
    pg.click("#gif2mp4")
    pg.wait_for_function("document.querySelector('#gifdone') && !document.querySelector('#gifdone').classList.contains('hide')", timeout=120000)
    check(pg.is_hidden("#gifbar"), "after converting the button is gone (the patient is an mp4 now)")
    href = pg.evaluate("document.querySelector('#gifdl').href"); name = pg.get_attribute("#gifdl", "download")
    check(name == "spin.mp4", f"download is named {name}")
    data = pg.evaluate("async () => { const r = await fetch(document.querySelector('#gifdl').href); const u8 = new Uint8Array(await r.arrayBuffer()); let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); }")
    out = T / "spin_out.mp4"; out.write_bytes(base64.b64decode(data))
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,pix_fmt:format=duration", "-of", "json", str(out)], capture_output=True, text=True).stdout)
    st = j["streams"][0]
    check(st["codec_name"] == "h264" and st["pix_fmt"] == "yuv420p" and st["width"] == 240 and abs(float(j["format"]["duration"]) - 2) < 0.3, f"a real h264 mp4 of the same size and length: {st['codec_name']} {st['width']}x{st['height']} {j['format']['duration']}s")
    facts = pg.inner_text("#facts"); check("h264" in facts and "240" in facts, f"the patient is now the mp4: {facts!r}")
    pg.click("#prev"); pg.wait_for_function("document.querySelector('#vafter').src", timeout=120000)
    check(True, "the converted clip can be treated (preview made)")
    check(not errs, f"no script errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
