"""Loop Hospital: the step 'Bring it to life' in the page (suggestion, styles, advanced sliders, a real 16 s result)."""
import base64, functools, http.server, json, re, shutil, subprocess, tempfile, threading, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent
T = Path(tempfile.mkdtemp(prefix="spklong_")); IN, FS = T / "in", T / "fs"; IN.mkdir(); FS.mkdir()
bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)

def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *a], check=True)
ff("-f", "lavfi", "-i", "color=c=black:s=640x360:r=25:d=4,geq=lum='150+80*sin(2*PI*(X/160+T/4))':cb=128:cr=128", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(IN / "loop4.mp4"))
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

with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={"width": 1000, "height": 900}, service_workers="block")
    ctx.add_init_script("try{localStorage.setItem('spk_desktop','1')}catch(e){}"); ctx.add_init_script(ENGINE_JS)
    pg = ctx.new_page(); pg.expose_function("host", host); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/tools/hospital/index.html"); pg.wait_for_selector("#picker", state="attached")
    check(pg.locator("[data-tile=life]").count() == 1 and "life" in pg.inner_text("#tiles").lower(), "the tile 'Bring it to life' exists")
    pg.set_input_files("#picker", str(IN / "loop4.mp4")); pg.wait_for_selector("#findings li", timeout=60000)
    check("16 s" in pg.inner_text("#findings") and pg.locator("#findings [data-fix]").count() >= 1, "a 4 s clip is offered 'Bring it to life' (repeated to 16 s)")
    # add it from the suggestions
    n = pg.locator("#findings li").count(); fix = None
    for i in range(n):
        if "16 s" in pg.locator("#findings li").nth(i).inner_text(): fix = pg.locator("#findings li").nth(i).locator("[data-fix]"); break
    fix.click(); pg.wait_for_timeout(300)
    check(pg.locator("[data-step=life]").is_visible(), "adding the suggestion turns the step on")
    check(pg.input_value("#h_life_breathe") == "35" and pg.input_value("#h_life_minSeconds") == "16", "calm style filled the sliders (breathing 35, at least 16 s)")
    check(not pg.locator("[data-step=life] details.adv").evaluate("e => e.open"), "the fine-tuning sliders are behind Advanced")
    pg.locator("[data-step=life] input[value=float]").check(force=True); pg.wait_for_timeout(200)
    check(pg.evaluate("HOSP.R.life.drift") == 60 and pg.evaluate("HOSP.R.life.style") == "float", "choosing Floating sets drift to 60")
    pg.locator("[data-step=life] details.adv summary").click(); pg.fill("#h_life_ease", "80"); pg.dispatch_event("#h_life_ease", "input"); pg.wait_for_timeout(200)
    check(pg.evaluate("HOSP.R.life.style") == "custom" and pg.locator("[data-step=life] input[name=h_life_style]:checked").count() == 0, "moving a slider makes it a custom mix")
    pg.click("#go"); pg.wait_for_selector("#res .rr", timeout=240000)
    dur = pg.evaluate("""async () => { const u8 = new Uint8Array(await (await fetch(document.querySelector('#vafter').src)).arrayBuffer()); let i = 0;
      for (; i < u8.length - 24; i++) if (u8[i] === 0x6d && u8[i+1] === 0x76 && u8[i+2] === 0x68 && u8[i+3] === 0x64) break;   // 'mvhd'
      const dv = new DataView(u8.buffer, i); return dv.getUint32(20) / dv.getUint32(16); }""")
    check(abs(dur - 16) < 0.3, f"the finished clip is 16 s long ({dur})")
    fits = pg.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")
    check(fits and not errs, f"no overflow, no page errors {errs[:2]}")
    pg.set_viewport_size({"width": 320, "height": 700}); pg.wait_for_timeout(300)
    r = pg.evaluate(JS); check(r["sw"] <= r["W"] and not r["out"], f"the new step fits 320 px: {r['sw']}/{r['W']} {r['out']}")
    b.close()
print("\nALL OK" if not bad else "\nFAILED: " + "; ".join(bad[:15])); sys.exit(1 if bad else 0)
