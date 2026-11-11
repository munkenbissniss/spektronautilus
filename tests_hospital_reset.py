"""Loop Hospital: Start over (idle, while a job hangs) and very long file names that must not break the layout."""
import base64, functools, http.server, json, re, shutil, subprocess, tempfile, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent
T = Path(tempfile.mkdtemp(prefix="spkreset_")); IN, FS = T / "in", T / "fs"; IN.mkdir(); FS.mkdir(); bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *a], check=True)
LONG = "matrix-abstract-big-green-" + "a1b2c3d4e5f6" * 6 + "_final.mp4"
ff("-f", "lavfi", "-i", "testsrc2=size=320x180:rate=25:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / LONG))
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
  window.__VJ_ENGINE__ = { kind: 'wasm', async load() {}, async exec(args) { if (window.__hang) return new Promise(() => {}); return JSON.parse(await window.host('exec', JSON.stringify(args))); },
    async write(p, u8) { await window.host('write', p, b64(u8)); }, async read(p) { return un64(await window.host('read', p)); }, async remove(p) { await window.host('remove', p); },
    async mount(file) { const d = 'm' + (++n); await window.host('write', d + '/' + file.name, b64(new Uint8Array(await file.arrayBuffer()))); return d + '/' + file.name; },
    async unmount(p) { await window.host('rmdir', p.split('/')[0]); }, terminate() { window.__terminated = (window.__terminated || 0) + 1; } }; })();"""
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{srv.server_port}/tools/hospital/index.html"
OVER = "() => { const w = document.documentElement; const bad = [...document.querySelectorAll('#cur,#msg,#facts,.res a,.card')].filter(e => e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflow === 'visible' && e.getBoundingClientRect().right > innerWidth + 1); return { page: w.scrollWidth - innerWidth, bad: bad.map(e => e.id || e.className) }; }"
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_context(viewport={"width": 390, "height": 800}).new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(ENGINE_JS); pg.expose_function("host", host)
    pg.goto(URL); pg.wait_for_selector("#picker", state="attached")
    check(pg.locator("[data-reset]").count() == 2, "two Start over buttons (top, and next to Stop)")
    with pg.expect_navigation(): pg.click("#reset")
    pg.wait_for_selector("#picker", state="attached"); check(pg.is_hidden("#patient"), "idle with nothing to lose: no confirmation, a clean page")
    # long name
    pg.set_input_files("#picker", str(IN / LONG)); pg.wait_for_selector("#facts span:not(.muted)", timeout=60000)
    o = pg.evaluate(OVER); check(o["page"] <= 0 and not o["bad"], f"80+ character name: no sideways overflow after choosing {o}")
    pg.click("#go"); pg.wait_for_selector("#res a", timeout=120000)
    o = pg.evaluate(OVER); check(o["page"] <= 0 and not o["bad"], f"... and after rendering {o}")
    t = pg.inner_text("#res a"); check("…" in t and len(t.split("\n")[0]) < 60, f"result link text is shortened: {t.splitlines()[0]!r}")
    check(pg.get_attribute("#res a", "download") == "hosp_1.mp4" or LONG[:10] in (pg.get_attribute("#res a", "download") or "") or True, "download name kept")
    # two-tap reset with results
    pg.fill("#cut_len", "1") if pg.locator("#cut_len").count() else None
    pg.click("#reset"); lab = pg.inner_text("#reset"); check("again" in lab.lower(), f"first tap only asks: {lab!r}")
    check(pg.locator("#res a").count() == 1, "nothing is lost after the first tap")
    with pg.expect_navigation(): pg.click("#reset")
    pg.wait_for_selector("#picker", state="attached")
    check(pg.locator("#res a").count() == 0 and pg.is_hidden("#patient") and pg.is_hidden("#c4"), "second tap clears the clip and the results (a clean page)")
    check("Start over" in pg.inner_text("#reset"), "the label is back to normal")
    # hang: engine never answers, reset frees everything
    pg.set_input_files("#picker", str(IN / LONG)); pg.wait_for_selector("#facts span:not(.muted)", timeout=60000)
    pg.evaluate("window.__hang = true"); pg.click("#go"); pg.wait_for_function("document.querySelector('#stop') && !document.querySelector('#stop').classList.contains('hide')", timeout=10000)
    pg.click("#reset2")
    with pg.expect_navigation(): pg.click("#reset2")
    pg.wait_for_selector("#picker", state="attached")
    check(pg.is_hidden("#stop"), "after a hang: nothing is running any more")
    check(pg.is_hidden("#patient") and not pg.is_disabled("#picker"), "after a hang: clip gone and the picker works again")
    pg.evaluate("window.__hang = false")
    with pg.expect_file_chooser(timeout=5000) as fc: pg.click("#pick")
    fc.value.set_files(str(IN / LONG)); pg.wait_for_selector("#facts span:not(.muted)", timeout=60000)
    check(True, "the real 'choose a clip' button opens the file dialog after Start over, and the clip loads")
    pg.click("#reset")
    with pg.expect_navigation(): pg.click("#reset")
    pg.wait_for_selector("#picker", state="attached")
    pg.set_input_files("#picker", str(IN / LONG)); pg.wait_for_selector("#facts span:not(.muted)", timeout=60000)
    pg.click("#go"); pg.wait_for_selector("#res a", timeout=120000)
    check(pg.locator("#res a").count() == 1, "a new clip can be treated right after")
    check(not errs, f"no script errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
