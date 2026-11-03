"""Progress bars: never backwards, alive while nothing is known, pause/resume (Tools and from the Queue page), clock, and the Queue page seeing jobs."""
import base64, functools, http.server, json, re, shutil, subprocess, tempfile, threading, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent
T = Path(tempfile.mkdtemp(prefix="spkprog_")); IN, FS = T / "in", T / "fs"; IN.mkdir(); FS.mkdir()
bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
def ff(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *a], check=True)
FILES = []
for i in range(3):
    f = IN / f"clip{i}.mp4"; ff("-f", "lavfi", "-i", f"testsrc2=size=320x180:rate=25:duration=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(f)); FILES.append(str(f))
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
  window.__VJ_ENGINE__ = { kind: 'wasm', async load() {}, async exec(args) { await new Promise(r => setTimeout(r, 1400)); return JSON.parse(await window.host('exec', JSON.stringify(args))); },
    async write(p, u8) { await window.host('write', p, b64(u8)); }, async read(p) { return un64(await window.host('read', p)); }, async remove(p) { await window.host('remove', p); },
    async mount(file) { const d = 'm' + (++n); await window.host('write', d + '/' + file.name, b64(new Uint8Array(await file.arrayBuffer()))); return d + '/' + file.name; },
    async unmount(p) { await window.host('rmdir', p.split('/')[0]); }, terminate() {} }; })();"""
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_port}"
with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={"width": 900, "height": 900}, service_workers="block")
    ctx.add_init_script("try{localStorage.setItem('spk_desktop','1')}catch(e){}"); ctx.add_init_script(ENGINE_JS)
    ctx.expose_function("host", host)
    errs = []
    pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE + "/tools/app/index.html"); pg.wait_for_selector("#tabs button"); pg.click("#tabs button[data-t=convert]")
    pg.set_input_files("#picker", FILES); pg.wait_for_selector("#files .vt", timeout=60000)
    pg.evaluate("window.__samples=[];setInterval(()=>{const j=VJ.JOBS[0];if(j)__samples.push(j.progress)},60)")
    pg.click("#go"); pg.wait_for_function("VJ.JOBS.length && VJ.JOBS[0].status==='running'", timeout=20000); pg.wait_for_timeout(500)
    check(pg.locator("#jobs .bar.ind").count() == 1, "Tools: the bar is 'alive' (moving stripes) while no progress is known yet")
    check(pg.locator("#jobs .ptime").inner_text() != "", "Tools: a clock is shown: " + pg.locator("#jobs .ptime").inner_text())
    check(pg.locator("#jobs [data-a=pause]").count() == 1, "Tools: a Pause button exists for a job with several files")
    # the Queue page sees the job, with a bar and a Pause button
    qp = ctx.new_page(); qp.on("pageerror", lambda e: errs.append(str(e))); qp.goto(BASE + "/queue/index.html"); qp.wait_for_function("window.__queue", timeout=10000)
    qp.wait_for_selector("[data-k] .bar", timeout=8000); check(True, "Queue page opened after the job started still shows it with a bar (hello/resend)")
    check(qp.locator("[data-a=pause]").count() == 1, "Queue: Pause button")
    qp.click("[data-a=pause]")
    pg.wait_for_function("VJ.JOBS[0].paused===true", timeout=15000); check(True, "Pause from the Queue page pauses the job after the current file")
    p1 = pg.evaluate("VJ.JOBS[0].progress"); pg.wait_for_timeout(2500); p2 = pg.evaluate("VJ.JOBS[0].progress")
    check(p1 == p2 and 0 < p1 < 1, f"progress stands still while paused ({p1:.2f})")
    check("Paused" in pg.locator("#jobs .ptime").inner_text() and pg.locator("#jobs .bar.pz").count() == 1, "Tools: says 'Paused' in words and the bar is dimmed")
    qp.wait_for_function("document.querySelector('[data-k] .chip').textContent.trim()==='paused'", timeout=8000); check(True, "Queue: chip says paused")
    e1 = pg.locator("#jobs .ptime").inner_text(); pg.wait_for_timeout(2200); e2 = pg.locator("#jobs .ptime").inner_text()
    check(re.findall(r"(\d+:\d\d) elapsed", e1) == re.findall(r"(\d+:\d\d) elapsed", e2), f"the elapsed clock stops while paused ({e1} / {e2})")
    pg.click("#jobs [data-a=pause]")   # resume
    pg.wait_for_function("['done','failed'].includes(VJ.JOBS[0].status)", timeout=60000)
    r = pg.evaluate("({s:VJ.JOBS[0].status,n:VJ.JOBS[0].results.length,p:VJ.JOBS[0].progress,smp:__samples})")
    check(r["s"] == "done" and r["n"] == 3 and r["p"] == 1, f"resumed job finishes all 3 files ({r['s']}, {r['n']})")
    check(all(b2 >= a - 1e-9 for a, b2 in zip(r["smp"], r["smp"][1:])) and all(0 <= x <= 1 for x in r["smp"]), "progress never goes backwards or outside 0..1")
    # removing a finished job from Jobs also removes it from the Queue (page and pop-up panel), also after a reload
    qp.wait_for_selector("[data-k] .chip.done", timeout=8000)
    ep = ctx.new_page(); ep.goto(BASE + "/queue/index.html?embed=1"); ep.wait_for_selector("[data-k] .chip.done", timeout=8000)
    pg.click("#jobs [data-a=del]")
    qp.wait_for_function("document.querySelectorAll('[data-k]').length===0", timeout=8000); ep.wait_for_function("document.querySelectorAll('[data-k]').length===0", timeout=8000)
    check(True, "Remove from list in Tools empties the Queue page and the pop-up Queue at once")
    qp.reload(); qp.wait_for_function("window.__queue", timeout=8000); qp.wait_for_timeout(600)
    check(qp.locator("[data-k]").count() == 0, "...and it stays gone after a reload")
    # helper rules
    h = pg.evaluate("""async () => { const m = await import('/shared/progress.js');
      return { clamp: [m.clamp01(-1), m.clamp01(2), m.clamp01(.4)], dur: [m.fmtDur(65), m.fmtDur(3723)],
        eta: m.timeLine({progress:.5, started: Date.now()-20000}, s=>s), noeta: m.timeLine({progress:.01, started: Date.now()-20000}, s=>s), pz: m.timeLine({progress:.5, started: Date.now()-60000, paused:true, pauseStart: Date.now()-40000}, s=>s),
        quiet: [m.quietNote(Date.now()-30000, s=>s), m.quietNote(Date.now()-3000, s=>s)], ind: m.barHTML({frac:0}).includes('ind'), notind: !m.barHTML({frac:.3}).includes('ind'), paused: m.barHTML({frac:0, paused:true}).includes('pz') && !m.barHTML({frac:0, paused:true}).includes('ind') } }""")
    check(h["clamp"] == [0, 1, .4] and h["dur"] == ["1:05", "1:02:03"], f"clamp/format helpers {h['clamp']} {h['dur']}")
    check("left" in h["eta"] and "left" not in h["noeta"], f"estimate only when trustworthy: '{h['eta']}' / '{h['noeta']}'")
    check("0:20 elapsed" in h["pz"], f"elapsed excludes paused time: '{h['pz']}'")
    check(h["quiet"][0] != "" and h["quiet"][1] == "", "'still working' note appears only after a quiet spell")
    check(h["ind"] and h["notind"] and h["paused"], "bar: stripes when unknown, solid when known, dim (no stripes) when paused")
    up = pg.evaluate("""async () => { const calls = [], say = (m, f) => calls.push([m, f]), ctl = { stop: false, pause: true };
      const real = window.fetch; let patches = 0;
      window.fetch = async (u, o) => { if (String(u).includes('api.vimeo.com/me/videos')) return new Response(JSON.stringify({ upload: { upload_link: 'https://up.test/x' }, link: 'https://vimeo.com/1' }), { status: 200 });
        if (o && o.method === 'PATCH') { patches++; const off = +o.headers['Upload-Offset'] + o.body.size; return new Response(null, { status: 204, headers: { 'Upload-Offset': String(off) } }); } return new Response('', { status: 200 }); };
      const file = new File([new Uint8Array(9 * 1024 * 1024)], 'a.mp4'); const p = SPK_UP._vimeo(file, { title: 't', vprivacy: 'unlisted' }, 'tok', say, ctl);
      await new Promise(r => setTimeout(r, 700)); const whilePaused = patches; ctl.pause = false; const r = await p; window.fetch = real;
      return { whilePaused, patches, link: r.link, pausedMsg: calls.some(c => /Paused/.test(c[0])), fracs: calls.map(c => c[1]).filter(x => x != null) }; }""")
    check(up["whilePaused"] == 0 and up["patches"] == 3 and up["pausedMsg"], f"Upload: pause holds the next piece back, says Paused, then finishes ({up['patches']} pieces)")
    check(all(b2 >= a - 1e-9 for a, b2 in zip(up["fracs"], up["fracs"][1:])), "Upload: bar only moves forward")
    check(not errs, f"no page errors {errs[:2]}")
    b.close()
print("\nALL OK" if not bad else "\nFAILED: " + "; ".join(bad[:15])); sys.exit(1 if bad else 0)
