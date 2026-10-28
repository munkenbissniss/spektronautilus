"""Browser test of the shared queue (docs/shared/queue.js + docs/queue). Jobs reported in one tab must show up live in the Queue tab,
Stop must reach the owning tab, results must be downloadable later, lost jobs must be flagged, and both Magic Mixers must report."""
import functools, http.server, threading, zipfile, io
from pathlib import Path
ROOT = Path(__file__).resolve().parent; DOCS = ROOT / "docs"; bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=str(DOCS))); threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f"http://127.0.0.1:{srv.server_port}"
from playwright.sync_api import sync_playwright
OWN = """async () => { const Q = await import('/shared/queue.js'); window.Q = Q; window.cancels = [];
  Q.onCancel((app, id) => window.cancels.push(app + '/' + id));
  window.job = { id: 7, app: 'tools', appLabel: 'Convert', url: '/tools/app/', title: 'a.mov, b.mov', status: 'running', progress: .25, done: 1, total: 4, failed: 0, current: 'b.mov', results: [], canCancel: true };
  window.key = Q.report(window.job); return window.key; }"""
with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(accept_downloads=True); errs = []
    own = ctx.new_page(); own.on("pageerror", lambda e: errs.append(str(e))); own.goto(B + "/queue/index.html")   # any same-origin page works as the job owner
    q = ctx.new_page(); q.on("pageerror", lambda e: errs.append(str(e))); q.goto(B + "/queue/index.html"); q.wait_for_selector("#list")
    check("Nothing here yet" in q.inner_text("#list"), "empty queue says so")
    key = own.evaluate(OWN)
    q.wait_for_selector(".card", timeout=4000)
    check("a.mov, b.mov" in q.inner_text(".card") and "Convert" in q.inner_text(".card"), "a job reported in another tab shows up live")
    check("1/4" in q.inner_text(".card") and "running" in q.inner_text(".card"), "count and status are shown")
    check(q.evaluate("document.querySelector('.bar i').style.width") == "25%", "progress bar follows the job")
    own.evaluate("() => Q.report({ ...job, progress: .75, done: 3 })"); q.wait_for_function("document.querySelector('.bar i').style.width==='75%'", timeout=4000)
    check(True, "progress updates live")
    check(q.evaluate("JSON.parse(localStorage.spk_q).n") == 1, "running count is stored for the menu badge")
    # stop goes to the owner
    q.click("button[data-a=stop]"); own.wait_for_function("window.cancels.length>0", timeout=4000)
    check(own.evaluate("window.cancels[0]") == "tools/7", "Stop in the Queue reaches the tab that owns the job")
    # finish with results
    own.evaluate("""async () => { const blob = new Blob(['hello one'], {type:'text/plain'}), b2 = new Blob(['hello two'], {type:'text/plain'});
      await Q.saveResults(key, [{name:'one.txt', blob}, {name:'two.txt', blob:b2}]);
      Q.report({ ...job, status:'done', progress:1, done:4, canCancel:false, results:[{name:'one.txt', size:9},{name:'two.txt', size:9}] }); }""")
    q.wait_for_selector(".card .chip.done", timeout=4000)
    check(q.inner_text(".card .acts").count("Stop") == 0, "no Stop button once done")
    check(q.evaluate("JSON.parse(localStorage.spk_q).n") == 0, "running count drops to 0")
    with q.expect_download() as d: q.click("a[data-dl='one.txt']")
    check(Path(d.value.path()).read_text() == "hello one", "a stored result file can be downloaded from the Queue")
    with q.expect_download() as d: q.click("button[data-a=zip]")
    z = zipfile.ZipFile(Path(d.value.path())); check(sorted(z.namelist()) == ["one.txt", "two.txt"] and z.read("two.txt") == b"hello two", "Download all gives a zip with every file")
    # history survives a reload (closed tab)
    own.close(); q.reload(); q.wait_for_selector(".card")
    check("done" in q.inner_text(".card") and "a.mov" in q.inner_text(".card"), "finished jobs are still listed after a reload")
    # lost job
    p2 = ctx.new_page(); p2.goto(B + "/queue/index.html")
    p2.evaluate("""async () => { const Q = await import('/shared/queue.js'); Q.report({ id: 1, app: 'magic', appLabel: 'Magic Mixer', url: '/mixer/', title: 'Show video', status: 'running', progress: .1, canCancel: true }); }""")
    q.wait_for_selector("text=Show video", timeout=4000); p2.close()
    q.evaluate("() => { for (const j of window.__queue.JOBS.values()) if (j.title === 'Show video') j.updated -= 60000; }"); q.evaluate("document.querySelector('#clear')&&0")
    q.wait_for_selector(".chip.lost", timeout=7000)
    check(True, "a running job that stopped reporting is flagged as lost")
    # remove + clear
    q.click(".card:has(.chip.lost) button[data-a=rm]"); q.wait_for_timeout(300)
    check("Show video" not in q.inner_text("#list"), "Remove takes a job away")
    q.click("#clear"); q.wait_for_timeout(500)
    check("Nothing here yet" in q.inner_text("#list"), "Clear finished empties the list")
    # the Magic Mixers report
    for app, path in (("magic", "/mixer/index.html?desktop=1"), ("magic-mobile", "/mixer-mobile/index.html")):
        m = ctx.new_page(); m.on("pageerror", lambda e: errs.append(str(e))); m.goto(B + path); m.wait_for_function("typeof window.__spkq==='function'", timeout=5000)
        m.evaluate("() => { const j = { id: 99, name: 'Test render', status: 'rendering', prog: .4, msg: 'Rendering…' }; window.__tj = j; window.__spkq(j); }")
        q.wait_for_selector("text=Test render", timeout=4000)
        check(app in q.evaluate("[...window.__queue.JOBS.keys()].join(' ')") and "Magic Mixer" in q.inner_text("#list"), f"{app}: a render job shows in the Queue")
        m.evaluate("() => { window.__tj.status = 'done'; window.__spkq(window.__tj); }"); q.wait_for_selector(".card:has-text('Test render') .chip.done", timeout=4000)
        check(True, f"{app}: finished state arrives")
        check(q.locator(".card:has-text('Test render') a:has-text('Open page')").count() == 1, f"{app}: Open page link is offered")
        m.close(); q.click("#clear"); q.wait_for_timeout(300)
    # menu badge on a normal site page
    s = ctx.new_page(); s.goto(B + "/index.html"); s.evaluate("localStorage.setItem('spk_q', JSON.stringify({n:2,t:Date.now()}))"); s.reload(); s.wait_for_timeout(300)
    check(s.is_visible(".qn") and s.inner_text(".qn") == "2", "the menu Queue link shows the running count")
    check(not errs, "no page errors: " + "; ".join(errs[:3]))
    b.close()
print("\nALL OK" if not bad else "\nFAILED: " + "; ".join(bad)); raise SystemExit(1 if bad else 0)
