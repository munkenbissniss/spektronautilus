"""Tests the new tools (Crop & trim, Sizes, HAP / ProRes, Catalogue, Loop pack) in the browser, with the computer's own ffmpeg as the engine."""
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

with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={"width": 1180, "height": 900}); ctx.add_init_script(ENGINE_JS)
    pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.expose_function("host", host)
    pg.goto(URL); pg.wait_for_selector("#tabs button")
    tabs = pg.locator("#tabs button").all_inner_texts()
    check(all(t in tabs for t in ("Crop & trim", "Sizes", "HAP / ProRes", "Catalogue", "Loop pack")), f"the new tabs are there: {tabs}")
    def tool(t, files):
        pg.click(f"#tabs button[data-t={t}]"); pg.set_input_files("#picker", [str(IN / f) for f in files]); pg.wait_for_selector("#files .vt")
    # ---------------- crop and trim
    tool("crop", ["wide clip.mp4", "tall.mp4"]); pg.select_option("#o_cropShape", "916"); pg.fill("#o_trimStart", "1"); pg.fill("#o_trimLen", "1"); pg.select_option("#o_preset", "ultrafast")
    check(pg.locator("#groups details[data-tools='crop']").is_visible() and not pg.locator("#groups details[data-tools='pro']").is_visible(), "crop settings are shown, pro settings are hidden")
    pg.click("#go"); wait_job(pg, 1); st = newest(pg); check(st["s"] == "done" and st["f"] == 0, f"crop job done {st}")
    r = results(pg, 0); wide = r.get("wide_clip.mp4"); tall = r.get("tall.mp4")
    s, d = probe(wide); check((s["width"], s["height"]) == (404, 720) and 0.8 < d < 1.3, f"16:9 clip cut to vertical 9:16 and trimmed to 1 s: {s['width']}x{s['height']}, {d:.2f} s")
    s, d = probe(tall); check(abs(s["width"] / s["height"] - 9 / 16) < 0.01, f"a clip that is already vertical keeps its shape: {s['width']}x{s['height']}")
    # square, start of picture
    pg.select_option("#o_cropShape", "11"); pg.fill("#o_trimStart", "0"); pg.fill("#o_trimLen", "0"); pg.click("#go"); wait_job(pg, 2); r = results(pg, 0)
    s, d = probe(r["wide_clip.mp4"]); check((s["width"], s["height"]) == (720, 720) and d > 2.5, f"square crop, full length: {s['width']}x{s['height']}, {d:.1f} s")
    pg.fill("#o_trimStart", "9"); pg.click("#go"); wait_job(pg, 3); st = newest(pg); check(st["f"] == 2, "a start time after the end of the clip fails with a message")
    # ---------------- sizes
    tool("sizes", ["wide clip.mp4", "tall.mp4"]); pg.check("input[data-z='480']"); pg.uncheck("input[data-z='1080']"); pg.check("input[data-z='1080']"); pg.select_option("#o_preset", "ultrafast")
    check("× 3" in pg.inner_text("#runinfo") or "3 size" in pg.inner_text("#runinfo"), "run info counts sizes: " + pg.inner_text("#runinfo"))
    pg.click("#go"); wait_job(pg, 4); st = newest(pg); r = results(pg, 0)
    check(st["s"] == "done" and sorted(r) == ["wide_clip_480p.mp4", "wide_clip_720p.mp4"], f"sizes: only sizes that are not bigger than the clip are made {sorted(r)} {st['log'][-2:]}")
    s, _ = probe(r["wide_clip_480p.mp4"]); check((s["width"], s["height"]) == (854, 480), f"480p proxy {s['width']}x{s['height']}")
    check(any("tall.mp4" in l for l in pg.evaluate("VJ.JOBS[0].log")) and not any(n.startswith("tall") for n in r), "a vertical clip smaller than every chosen size is not enlarged")
    # ---------------- pro formats
    tool("pro", ["wide clip.mp4"]); check(pg.locator("#pronote").is_visible(), "the web version says that HAP / ProRes need the Linux version")
    pg.click("#go"); pg.wait_for_timeout(400); check("Linux" in pg.inner_text("#msg") and pg.evaluate("VJ.JOBS.length") == 4, "no job is started in the web version")
    pg.evaluate("window.__VJ_ENGINE__.kind = 'native'; window.__VJ_ENGINE__.info = { cores: 4, version: 'test' }"); pg.click("#tabs button[data-t=crop]"); pg.click("#tabs button[data-t=pro]"); check(not pg.locator("#pronote").is_visible(), "with the local engine the note is gone")
    pg.select_option("#o_proFormat", "hap"); pg.click("#go"); wait_job(pg, 5); st = newest(pg); r = results(pg, 0)
    check(st["s"] == "done" and list(r) == ["wide_clip.mov"], f"HAP job {st}")
    s, d = probe(r["wide_clip.mov"]); check(s["codec_name"] == "hap" and s["width"] % 4 == 0 and s["height"] % 4 == 0, f"HAP file: {s['codec_name']} {s['width']}x{s['height']}")
    pg.select_option("#o_proFormat", "prores_hq"); pg.click("#go"); wait_job(pg, 6); r = results(pg, 0); s, _ = probe(r["wide_clip.mov"])
    check(s["codec_name"] == "prores" and s["pix_fmt"] == "yuv422p10le", f"ProRes HQ file: {s['codec_name']} {s['pix_fmt']}")
    # ---------------- catalogue
    tool("catalog", ["isloop.mp4", "nonloop.mp4", "wide clip.mp4"]); pg.fill("#o_catTitle", "Test <catalogue>"); pg.click("#go"); wait_job(pg, 7); st = newest(pg); r = results(pg, 0)
    check(st["s"] == "done" and sorted(r) == ["catalogue.csv", "catalogue.html"], f"catalogue files {sorted(r)} {st['log'][-1:]}")
    html = r["catalogue.html"].read_text(); csv = r["catalogue.csv"].read_text(encoding="utf-8-sig").splitlines()
    check(len(csv) == 4 and csv[0].startswith("file,folder,width,height"), f"csv has a header and 3 rows ({len(csv)} lines)")
    check("Test &lt;catalogue&gt;" in html and "<catalogue>" not in html and html.count("data:image/jpeg;base64,") == 3, "html page: title is escaped and has 3 pictures")
    rowmap = {l.split(",")[0]: l.split(",") for l in csv[1:]}
    check(rowmap["isloop.mp4"][8] == "loops" and rowmap["nonloop.mp4"][8] in ("jump", "almost"), f"loop quality: isloop={rowmap['isloop.mp4'][8]} nonloop={rowmap['nonloop.mp4'][8]}")
    pg2 = ctx.new_page(); pg2.goto((r["catalogue.html"]).as_uri()); pg2.click("th[data-k='2']"); first = pg2.locator("#t tbody tr").first.inner_text(); pg2.fill("#q", "isl")
    check(pg2.locator("#t tbody tr:visible").count() == 1 and "isloop" in pg2.locator("#t tbody tr:visible").first.inner_text(), "the catalogue page can search and sort"); pg2.close()
    # ---------------- loop pack
    tool("pack", ["isloop.mp4", "nonloop.mp4", "tall.mp4"]); pg.fill("#o_packName", "Åse's Neon Pack!"); pg.fill("#o_packAuthor", "DJ Test"); pg.select_option("#o_packLicence", "ccby"); pg.fill("#o_packNotes", "Thanks for using it")
    pg.click("#go"); wait_job(pg, 8); st = newest(pg); r = results(pg, 0)
    check(st["s"] == "done" and "ase-s-neon-pack.zip" in r and "contact-sheet.jpg" in r, f"pack files {sorted(r)} {st['log'][-1:]}")
    z = zipfile.ZipFile(r["ase-s-neon-pack.zip"]); names = z.namelist()
    check(z.testzip() is None, "the zip is valid")
    need = {"ase-s-neon-pack/" + n for n in ("README.txt", "pack.json", "index.html", "catalogue.csv", "contact-sheet.jpg", "isloop.mp4", "nonloop.mp4", "tall.mp4")}
    check(need <= set(names), f"zip content {sorted(set(names))}")
    check(z.read("ase-s-neon-pack/isloop.mp4") == (IN / "isloop.mp4").read_bytes(), "the videos in the pack are the originals, untouched")
    pj = json.loads(z.read("ase-s-neon-pack/pack.json")); rd = z.read("ase-s-neon-pack/README.txt").decode()
    check(pj["author"] == "DJ Test" and pj["licence"]["id"] == "ccby" and len(pj["loops"]) == 3 and "CC BY" in rd and "DJ Test" in rd, "pack.json and README have author, licence and loops")
    check("Mun" + "ken" not in rd and "Mun" + "ken" not in z.read("ase-s-neon-pack/index.html").decode(), "no old product name anywhere")
    sheet = r["contact-sheet.jpg"]; s, _ = probe(sheet); check(s["codec_name"] in ("mjpeg", "jpeg") and s["width"] > 600, f"contact sheet picture {s['width']}x{s['height']}")
    check(not errs, f"no script errors {errs[:2]}"); b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
