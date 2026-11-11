"""Akai MPD218 one-click setup in the VJ Mixer and Video DJ: the pads are mapped at once, the knobs are learned by turning each once.
A fake MIDI controller sends the same messages as an MPD218 on its factory preset (pads: notes 36-83 on channel 10).
NOT tested here: a real MPD218 (its knob numbers depend on the preset, which is why they are learned)."""
import functools, http.server, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent; bad = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m, flush=True)
    if not c: bad.append(m)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=str(ROOT / "docs"))); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_port}"
FAKE = """window.__mi=[];navigator.requestMIDIAccess=async()=>{const i={name:'MPD218',onmidimessage:null};window.__mi.push(i);return{inputs:new Map([['1',i]]),onstatechange:null}};
window.__send=d=>window.__mi.forEach(i=>i.onmidimessage&&i.onmidimessage({data:new Uint8Array(d)}));
window.__turn=(ch,cc)=>{for(const v of [60,64,70,80])__send([0xb0|ch,cc,v]);};"""
with sync_playwright() as pw:
    b = pw.chromium.launch()
    # the layouts themselves
    pg = b.new_page(); pg.goto(BASE + "/vj-pad/index.html"); pg.wait_for_selector("#pads .pad")
    L = pg.evaluate("import('../shared/mpd218.js').then(m => ({ vj: m.MPD_LAYOUTS.vj, dj: m.MPD_LAYOUTS.dj }))")
    vj = L["vj"]["pads"]
    check([vj[str(36 + i)] for i in range(16)] == [f"pad{i + 1}" for i in range(16)], "VJ: pad bank A = clip pads 1-16")
    check([vj[str(52 + i)] for i in range(16)] == ["pad17", "pad18", "pad19", "pad20"] + [f"fx{i + 1}" for i in range(8)] + ["mix", "tap", "beat1", "posterHide"], "VJ: pad bank B = pads 17-20, 8 effects, mix, tap, beat 1, hide poster")
    check([vj[str(68 + i)] for i in range(13)] == [f"sel{i + 1}" for i in range(6)] + [f"poster{i + 1}" for i in range(4)] + ["logo", "bankPrev", "bankNext"], "VJ: pad bank C = layers, posters, logo, banks")
    ids = pg.evaluate("import('./core.js').then(m => m.VJ_MIDI_ACTIONS.map(a => a.id))")
    check(all(v in ids for v in list(vj.values()) + L["vj"]["knobs"]), "VJ: every mapped action exists")
    pg.close()
    for app, url, storeKey in (("VJ", "/vj-pad/index.html", "spk_vj_midi"), ("DJ", "/live-dj/index.html", None)):
        ctx = b.new_context(viewport={"width": 1280, "height": 900}); ctx.add_init_script(FAKE)
        pg = ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(BASE + url); pg.wait_for_selector("#mpdSetup", state="attached")
        if app == "DJ":
            dj_ids = pg.evaluate("import('./core.js').then(m => m.MIDI_ACTIONS.map(a => a.id))")
            check(all(v in dj_ids for v in list(L["dj"]["pads"].values()) + L["dj"]["knobs"]), "DJ: every mapped action exists")
        pg.click("details:has(summary:text('MIDI')) summary")
        # a hand-learned key for something else is kept
        pg.click("#midiOn"); pg.wait_for_function("document.getElementById('midiStatus').textContent.includes('MPD218')")
        pg.click("button[data-l=logo]"); pg.evaluate("__send([0x90,100,127])")
        pg.click("#mpdSetup"); pg.wait_for_function("!document.getElementById('mpdSkip').hidden")
        check("knob 1" in pg.inner_text("#mpdMsg"), f"{app}: asks to turn knob 1: {pg.inner_text('#mpdMsg')!r}")
        m = pg.evaluate("SPK.S.midi.map")
        check(m.get("note:9:36") and m.get("note:0:36") == m.get("note:9:36"), f"{app}: pads mapped on channel 10 (and 1) at once")
        check(m.get("note:0:100") == "logo", f"{app}: a key learned by hand is kept")
        knobs = L["vj" if app == "VJ" else "dj"]["knobs"]
        # knob 1: CC 3 (turned, many messages), knob 2: CC 9; a pad pressed in between still plays and is not learned
        pg.evaluate("__turn(0,3)"); check("knob 2" in pg.inner_text("#mpdMsg"), f"{app}: one turn learns knob 1, the rest of the turn is ignored")
        pg.evaluate("__send([0x99,36,100])"); check("knob 2" in pg.inner_text("#mpdMsg"), f"{app}: a pad does not count as a knob")
        pg.evaluate("__turn(0,9)")
        if len(knobs) > 3: pg.click("#mpdSkip")
        rest = len(knobs) - (3 if len(knobs) > 3 else 2)
        for i in range(rest): pg.evaluate(f"__turn(0,{12 + i})")
        if not pg.is_hidden("#mpdSkip"): pg.click("#mpdDone")
        check(pg.is_hidden("#mpdSkip") and "ready" in pg.inner_text("#mpdMsg"), f"{app}: done: {pg.inner_text('#mpdMsg')!r}")
        m = pg.evaluate("SPK.S.midi.map")
        check(m.get("cc:0:3") == knobs[0] and m.get("cc:0:9") == knobs[1], f"{app}: knobs 1 and 2 learned ({knobs[0]}, {knobs[1]})")
        if storeKey: check(pg.evaluate(f"JSON.parse(localStorage.getItem('{storeKey}'))['cc:0:3']") == knobs[0], f"{app}: remembered after a reload")
        if app == "VJ":
            pg.evaluate("__send([0x99,56,100])"); check(pg.evaluate("SPK.S.fx[0]") is True, "VJ: pad bank B, first pad of row 2 = effect 1 on")
            pg.evaluate("__send([0x99,69,100])"); check(pg.evaluate("SPK.S.sel") == 1, "VJ: pad bank C pad 2 selects layer A2")
            pg.evaluate("__send([0xb0,3,127])"); check(pg.evaluate("SPK.S.f") > .99, "VJ: knob 1 moves the crossfader")
            pg.evaluate("__send([0xb0,9,0])"); check(pg.evaluate("SPK.cfg.fxAmt") == 0, "VJ: knob 2 = effect amount")
        else:
            pg.evaluate("__send([0xb0,3,0])"); check(abs(pg.evaluate("SPK.S.decks.A.vol")) < .01, "DJ: knob 1 = volume A")
            pg.evaluate("__send([0xb0,12,127])"); check(pg.evaluate("SPK.S.f") > .99, "DJ: knob 3 = crossfader")
        pg.evaluate("__send([0xb0,3,64])")   # learn mode is over: turning knob 1 again does not start anything
        check("ready" in pg.inner_text("#mpdMsg"), f"{app}: after setup the knobs just work")
        check(not errs, f"{app}: no page errors {errs[:2]}")
        ctx.close()
    # no MIDI in the browser: a clear message
    ctx = b.new_context(); ctx.add_init_script("delete Navigator.prototype.requestMIDIAccess; delete navigator.requestMIDIAccess;")
    pg = ctx.new_page(); pg.goto(BASE + "/vj-pad/index.html"); pg.wait_for_selector("#mpdSetup", state="attached")
    pg.click("details:has(summary:text('MIDI')) summary"); pg.click("#mpdSetup")
    check("MIDI" in pg.inner_text("#mpdMsg"), f"no MIDI: clear message {pg.inner_text('#mpdMsg')!r}")
    b.close()
print("\nALL OK" if not bad else f"\n{len(bad)} FAILED"); raise SystemExit(1 if bad else 0)
