"""Tests the Vimeo upload dialog (against a pretend server) and that every app that makes a video offers it."""
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
ff("-f", "lavfi", "-i", "testsrc2=size=360x640:rate=25:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "tall.mp4"))
ff("-f", "lavfi", "-i", "color=c=black:s=320x180:r=25:d=4,geq=r='128+100*sin(2*PI*(X/80+T/4))':g='128+100*sin(2*PI*(Y/60+T/4))':b='128+100*sin(2*PI*T/4)'", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "isloop.mp4"))
ff("-f", "lavfi", "-i", "testsrc2=size=320x180:rate=25:duration=4", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "nonloop.mp4"))
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
def probe(path):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,pix_fmt:format=duration", "-of", "json", str(path)], capture_output=True, text=True).stdout)
    return j["streams"][0], float(j["format"]["duration"])
def results(pg, idx=0):
    d = T / f"res{len(os.listdir(T))}"; d.mkdir()
    data = pg.evaluate("""async (i) => { const out = {}; for (const r of VJ.JOBS[i].results) if (r.blob) { const u8 = new Uint8Array(await r.blob.arrayBuffer()); let s=''; for (let k=0;k<u8.length;k+=0x8000) s+=String.fromCharCode.apply(null,u8.subarray(k,k+0x8000)); out[r.name]=btoa(s);} return out; }""", idx)
    paths = {}
    for n, b in data.items(): (d / n).write_bytes(base64.b64decode(b)); paths[n] = d / n
    return paths
def wait_job(pg, n): pg.wait_for_function(f"VJ.JOBS.filter(j => ['done','failed','cancelled'].includes(j.status)).length >= {n}", timeout=240000)
def newest(pg):   # the newest job is first in the list
    return pg.evaluate("({s: VJ.JOBS[0].status, f: VJ.JOBS[0].failed, n: VJ.JOBS[0].results.length, e: VJ.JOBS[0].error || '', log: VJ.JOBS[0].log.slice(-4)})")



ff("-f", "lavfi", "-i", "testsrc2=size=320x180:rate=12:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "tiny.mp4"))
H = f"http://127.0.0.1:{srv.server_port}/tools/hospital/index.html"
CORS = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Expose-Headers": "Location, Range, Upload-Offset"}
seen = []
def vm_start(route, req):
    if req.method == "OPTIONS": route.fulfill(status=204, headers=CORS); return
    seen.append(("vimeo-start", req.headers, req.post_data)); route.fulfill(status=200, headers=CORS, body=json.dumps({"upload": {"upload_link": "https://tus.mock/u1"}, "link": "https://vimeo.com/999", "uri": "/videos/999"}))
def vm_patch(route, req):
    if req.method == "OPTIONS": route.fulfill(status=204, headers=CORS); return
    off = int(req.headers.get("upload-offset", "0")); n = len(req.post_data_buffer or b""); seen.append(("vimeo-patch", off, n)); route.fulfill(status=204, headers={**CORS, "Upload-Offset": str(off + n)})
BIG = "(() => { const f = new File([new Uint8Array(20e6)], 'mix.mp4', { type: 'video/mp4' }); SPK_UP.open(f, { title: 'My <mix>', name: 'mix.mp4' }); })()"
with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={"width": 1180, "height": 900}); ctx.add_init_script(ENGINE_JS)
    pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.expose_function("host", host)
    pg.route("https://api.vimeo.com/me/videos", vm_start); pg.route("https://tus.mock/**", vm_patch)
    pg.goto(H); pg.wait_for_selector("#drop"); pg.wait_for_function("window.SPK_UP")
    pg.evaluate(BIG); pg.wait_for_selector("#spk-up")
    check("YouTube" not in pg.inner_text("#spk-up") and pg.locator("#u-vtok").is_visible(), "the dialog is for Vimeo only")
    pg.select_option("#u-priv", "unlisted"); pg.fill("#u-vtok", "vtok"); pg.click("#u-go"); pg.wait_for_selector("#spk-up .ok a", timeout=20000)
    vs = next(s for s in seen if s[0] == "vimeo-start"); vb = json.loads(vs[2]); patches = [(s[1], s[2]) for s in seen if s[0] == "vimeo-patch"]
    check(vs[1].get("authorization") == "bearer vtok" and vb["privacy"]["view"] == "unlisted" and vb["upload"]["size"] == 20000000 and vb["name"] == "My mix", f"Vimeo: token, privacy, size and a cleaned title {vb}")
    check(patches == [(0, 4194304), (4194304, 4194304), (8388608, 4194304), (12582912, 4194304), (16777216, 3222784)], f"Vimeo: 4 MB tus parts so the bar moves often {patches}")
    check(pg.locator("#spk-up .ok a").get_attribute("href") == "https://vimeo.com/999", "Vimeo: link to the new video")
    check(json.loads(pg.evaluate("localStorage.getItem('munken_vimeo')"))["token"] == "vtok", "the token is kept where the Magic Mixer keeps it")
    pg.click("#u-close"); pg.wait_for_selector("#spk-up", state="detached")
    # a refused start tells you why
    pg.unroute("https://api.vimeo.com/me/videos"); pg.route("https://api.vimeo.com/me/videos", lambda r, q: r.fulfill(status=401, headers=CORS, body=json.dumps({"error": "bad token"})) if q.method != "OPTIONS" else r.fulfill(status=204, headers=CORS))
    pg.evaluate(BIG); pg.click("#u-go"); pg.wait_for_selector("#spk-up .er", timeout=10000); check("scopes" in pg.inner_text("#u-st"), "Vimeo: a refused token is explained: " + pg.inner_text("#u-st")[:90]); pg.click("#u-close")
    # the apps offer it
    pg.set_input_files("#picker", str(IN / "tiny.mp4")); pg.wait_for_selector("#findings li", timeout=60000); pg.click("#go"); pg.wait_for_selector("#res [data-up]", timeout=240000)
    pg.click("#res [data-up]"); pg.wait_for_selector("#spk-up"); check(pg.input_value("#u-title") == "tiny", "Loop Hospital: Upload… opens the dialog with the clip name"); pg.click("#u-close")
    pg.goto(f"http://127.0.0.1:{srv.server_port}/tools/app/index.html"); pg.wait_for_selector("#tabs button"); pg.click("#tabs button[data-t=convert]"); pg.set_input_files("#picker", [str(IN / "tiny.mp4")]); pg.wait_for_selector("#files .vt"); pg.click("#go")
    pg.wait_for_selector("#jobs [data-a=up]", timeout=240000); pg.click("#jobs [data-a=up]"); pg.wait_for_selector("#spk-up"); check(True, "Tools: every finished video has an Upload… button"); pg.click("#u-close")
    pg.goto(f"http://127.0.0.1:{srv.server_port}/live-dj/index.html?desktop=1"); pg.wait_for_selector("#recUp", state="attached"); pg.wait_for_function("window.SPK_UP"); check(True, "Video DJ: upload dialog is loaded")
    for f in ("mixer/index.html", "mixer-mobile/index.html"):
        t = (ROOT / "docs" / f).read_text(encoding="utf-8"); check("Upload to Vimeo" in t and "youtube" not in t.lower(), f"{f}: has its Vimeo upload and nothing about YouTube")
    check(not errs, f"no script errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
