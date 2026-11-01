"""Tests Slow motion and Upscale (ffmpeg methods) in the Tools page and the Loop Hospital, in the browser, with the computer's own ffmpeg as the engine."""
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
with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={"width": 1180, "height": 900}); ctx.add_init_script(ENGINE_JS)
    pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.expose_function("host", host)
    pg.goto(URL); pg.wait_for_selector("#tabs button")
    groups = pg.locator("#tabs .tg small").evaluate_all("els => els.map(e => e.textContent)")
    check(groups == ["Find", "Fix up", "Look", "Share and export", "New"], f"the tools are grouped: {groups}")
    tabs = pg.locator("#tabs button").all_inner_texts()
    check("Slow motion" in tabs and "Upscale" in tabs and "AI upscale" not in tabs, f"Slow motion and Upscale are tools: {tabs}")
    check(pg.locator("#tabs a.hosp").get_attribute("href") == "../hospital/", "link to the Loop Hospital")
    # ---- sharp upscale
    pg.click("#tabs button[data-t=ai]"); pg.set_input_files("#picker", [str(IN / "tiny.mp4")]); pg.wait_for_selector("#files .vt")
    check(pg.locator("#o_aiModel").is_hidden() and pg.locator("#o_upSharp").is_visible() and pg.locator("#ainote").is_hidden(), "sharp method: AI choices and AI note are hidden")
    pg.select_option("#o_aiScale", "3"); pg.click("#go"); wait_job(pg, 1); st = newest(pg)
    check(st["s"] == "done" and st["f"] == 0, f"sharp upscale done {st}")
    r = results(pg, 0); f = next(iter(r.values())); s, d = probe(f); check((s["width"], s["height"]) == (960, 540) and r and "tiny_up3x.mp4" in r, f"3x sharp: {s['width']}x{s['height']} {list(r)}")
    # ---- AI chosen in the web version: clear message, no job
    pg.select_option("#o_upEngine", "ai"); check(pg.locator("#o_aiModel").is_visible() and pg.locator("#ainote").is_visible(), "AI method shows its own choices and note")
    pg.click("#go"); pg.wait_for_timeout(500); msg = pg.inner_text("#msg"); check("local version" in msg, f"AI in the browser says what is needed: {msg}")
    pg.select_option("#o_upEngine", "sharp")
    # ---- slow motion: blend, motion, smooth
    pg.click("#tabs button[data-t=slowmo]"); pg.set_input_files("#picker", [str(IN / "tiny.mp4")]); pg.wait_for_selector("#files .vt")
    check(pg.locator("#o_slowModel").is_hidden(), "slow motion: model hidden unless AI")
    for eng, mode, name, dur, fps in (("blend", "slow", "tiny_slow2x.mp4", 4, 12), ("motion", "slow", "tiny_slow2x.mp4", 4, 12), ("blend", "smooth", "tiny_smooth2x.mp4", 2, 24)):
        pg.select_option("#o_slowEngine", eng); pg.select_option("#o_slowMode", mode); pg.select_option("#o_slowFactor", "2")
        n = pg.evaluate("VJ.JOBS.length"); pg.click("#go"); wait_job(pg, n + 1); st = newest(pg)
        check(st["s"] == "done" and st["f"] == 0, f"slow motion {eng}/{mode} done {st}")
        r = results(pg, 0); s, d = probe(r[name]) if name in r else ({}, 0)
        fr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate", "-of", "csv=p=0", str(r.get(name, ""))], capture_output=True, text=True).stdout.strip()
        a, c = (fr.split("/") + ["1"])[:2]
        check(name in r and abs(d - dur) < 0.3 and abs(float(a) / float(c) - fps) < 0.5, f"{eng}/{mode}: {name in r} {d:.2f} s {float(a)/float(c):.1f} fps")
    # ---- Loop Hospital
    pg.goto(H); pg.wait_for_selector("#drop")
    check(pg.locator("#c3").is_hidden(), "nothing to treat before a clip is chosen")
    pg.set_input_files("#picker", str(IN / "tiny.mp4")); pg.wait_for_selector("#findings li", timeout=60000)
    items = pg.locator("#findings li span").all_inner_texts()
    check(any("Small picture" in t for t in items) and any("Very short" in t for t in items), f"examination finds problems: {items}")
    pg.click("#healall"); check(pg.is_checked("[data-use=up]") and pg.is_checked("[data-use=slow]"), "'Add all suggested treatments' ticks the steps")
    pg.uncheck("[data-use=up]"); pg.check("[data-use=look]"); pg.select_option("#h_look_id", "grainy"); pg.check("[data-use=loop]"); pg.select_option("#h_loop_mode", "pingpong")
    pg.click("#prev"); pg.wait_for_function("document.querySelector('#vafter').src.startsWith('blob:')", timeout=120000); pg.wait_for_function("!document.querySelector('#prev').disabled", timeout=120000)
    check(pg.locator("#fafter").is_visible(), "preview shows the treated clip next to the original")
    pg.click("#go"); pg.wait_for_selector("#res a", timeout=240000); pg.wait_for_function("!document.querySelector('#go').disabled")
    name = pg.locator("#res a").first.get_attribute("download"); data = pg.evaluate("""async () => { const r = await fetch(document.querySelector('#res a').href); const u8 = new Uint8Array(await r.arrayBuffer()); let s=''; for (let k=0;k<u8.length;k+=0x8000) s+=String.fromCharCode.apply(null,u8.subarray(k,k+0x8000)); return btoa(s); }""")
    out = T / "healed.mp4"; out.write_bytes(base64.b64decode(data)); s, d = probe(out)
    check(name == "tiny_healed.mp4" and s["codec_name"] == "h264" and d > 6.5, f"treated clip: {name} {s['width']}x{s['height']} {d:.1f} s (slow 2x then forward-backward)")
    pg.set_input_files("#pickermore", [str(IN / "isloop.mp4"), str(IN / "nonloop.mp4")]); pg.wait_for_function("document.querySelectorAll('#res a').length >= 3", timeout=240000)
    check(pg.locator("#zipall").is_visible(), "more clips treated the same way, with a zip button")
    check(not errs, f"no script errors {errs[:2]}")
    # phone width
    ctx2 = b.new_context(viewport={"width": 320, "height": 640}); p2 = ctx2.new_page(); p2.goto(H); p2.wait_for_selector("#drop"); p2.set_input_files("#picker", str(IN / "tiny.mp4"))
    ctx2.add_init_script(ENGINE_JS)
    ov = p2.evaluate("document.documentElement.scrollWidth - innerWidth"); check(ov <= 0, f"Loop Hospital fits 320 px ({ov})")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
