"""Very long file names must not break the layout on a phone (320 px): file lists, job cards, the Queue page, the Loop Hospital."""
import base64, functools, http.server, json, re, shutil, subprocess, tempfile, threading, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent
T = Path(tempfile.mkdtemp(prefix="spklong_")); IN, FS = T / "in", T / "fs"; IN.mkdir(); FS.mkdir()
bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
LONG1 = "MyVeryLongFileNameWithoutAnySpaces_final_FINAL_v2_export_2026-10-21_1080p_h264_masterfile_versionTwo_reallyTheLastOne"
LONG2 = "A clip with a very long name that has spaces in it and goes on and on and on for quite a while longer than any phone screen"
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *a], check=True)
ff("-f", "lavfi", "-i", "sine=frequency=440:duration=3", str(IN / (LONG1 + ".wav")))
for n in (LONG1, LONG2): ff("-f", "lavfi", "-i", "testsrc2=size=320x180:rate=25:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / (n + ".mp4")))
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
BASE = f"http://127.0.0.1:{srv.server_port}"
JS = """() => { const W = document.documentElement.clientWidth, out = [];
  for (const el of document.querySelectorAll('body *')) { const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    const cs = getComputedStyle(el); if (cs.position === 'fixed' && r.right <= W + 1 && r.left >= -1) continue;
    let p = el, clipped = false; while ((p = p.parentElement) && p !== document.body) { const o = getComputedStyle(p); if (/(auto|scroll|hidden|clip)/.test(o.overflowX) && p.getBoundingClientRect().right <= W + 1) { clipped = true; break; } }
    if (!clipped && (r.right > W + 1 || r.left < -1)) out.push(el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\\s+/).join('.') : '') + ' ' + Math.round(r.left) + '..' + Math.round(r.right)); }
  return { sw: document.documentElement.scrollWidth, W, out: out.slice(0, 6) }; }"""
def fits(pg, what): r = pg.evaluate(JS); check(r["sw"] <= r["W"] and not r["out"], f"{what}: scrollWidth {r['sw']}/{r['W']} {r['out']}")
with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={"width": 320, "height": 640}, has_touch=True, is_mobile=True, service_workers="block")
    ctx.add_init_script("try{localStorage.setItem('spk_desktop','1')}catch(e){}")
    pg = ctx.new_page(); pg.expose_function("host", host); ctx.add_init_script(ENGINE_JS)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    # Tools: file list and a finished job
    pg.goto(BASE + "/tools/app/index.html"); pg.wait_for_selector("#tabs button"); pg.click("#tabs button[data-t=convert]")
    pg.set_input_files("#picker", [str(IN / (LONG1 + ".mp4")), str(IN / (LONG2 + ".mp4"))]); pg.wait_for_selector("#files .vt", timeout=60000)
    SH = lambda n: __import__("os").environ.get("SHOTS") and pg.screenshot(path=f"/tmp/{n}.png", full_page=True)
    SH("s1"); fits(pg, "Tools: file list with long names")
    pg.click("#go"); pg.wait_for_function("VJ.JOBS.length && VJ.JOBS[0].status==='running'", timeout=30000); fits(pg, "Tools: running job card")
    pg.wait_for_function("['done','failed'].includes(VJ.JOBS[0].status)", timeout=120000); pg.wait_for_timeout(600); SH("s2"); fits(pg, "Tools: finished job card with long result names")
    # Queue page with fake long jobs
    pg.goto(BASE + "/queue/index.html"); pg.wait_for_function("window.__queue")
    pg.evaluate("""([a,b]) => { const J = window.__queue.JOBS, now = Date.now();
      J.set('t:x:1', {key:'t:x:1', app:'tools', appLabel:'Convert', id:1, title:a+', '+b, status:'running', created:now, updated:now, progress:.4, done:1, total:2, current:b, canCancel:true, url:'/tools/app/', results:[]});
      J.set('t:x:2', {key:'t:x:2', app:'tools', appLabel:'Convert', id:2, title:a, status:'done', created:now-1, updated:now, progress:1, done:2, total:2, results:[{name:a+'.mp4',size:123456},{name:b+'.mp4',size:99}], url:'/tools/app/'});
      window.__queue.draw(); }""", [LONG1, LONG2]); pg.wait_for_timeout(300); SH("s3"); fits(pg, "Queue: long titles, current file and results")
    # Loop Hospital
    pg.goto(BASE + "/tools/hospital/index.html"); pg.wait_for_selector("input[type=file]", state="attached")
    pg.set_input_files("input[type=file]", str(IN / (LONG1 + ".mp4"))); pg.wait_for_timeout(2500); SH("s4"); fits(pg, "Loop Hospital: long file name")
    V = [str(IN / (LONG1 + ".mp4")), str(IN / (LONG2 + ".mp4"))]; A = str(IN / (LONG1 + ".wav"))
    for page, sels in [("mixer/index.html", [("#fA", [A]), ("#fV", V)]), ("mixer-mobile/index.html", [("#fA", [A]), ("#fV", V)]),
                       ("vj-pad/index.html", [("#files", V), ("#aFiles", [A])]), ("live-dj/index.html", [("#files", V)]), ("live-mobile/index.html", [("#files", V)])]:
        pg.goto(BASE + "/" + page); pg.wait_for_timeout(500)
        for sel, fl in sels:
            pg.set_input_files(sel, fl); pg.wait_for_timeout(1800)
        if page.startswith("vj-pad"): pg.evaluate("document.body.classList.add('adv')")
        SH(page.split("/")[0]); fits(pg, page + ": long file names")
    check(not errs, f"no page errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else "\nFAILED: " + "; ".join(bad[:15])); sys.exit(1 if bad else 0)
