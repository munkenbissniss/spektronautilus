"""Tools: inside the iPhone app (SPK_IOS present) a plain conversion goes to the phone's video chips and never touches ffmpeg.wasm."""
import functools, http.server, threading, subprocess, tempfile, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent; T = Path(tempfile.mkdtemp())
subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","testsrc2=size=640x360:rate=30:duration=1","-c:v","libx264","-pix_fmt","yuv420p",str(T/"a.mp4")],check=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1",0), functools.partial(Q,directory=str(ROOT/"docs"))); threading.Thread(target=srv.serve_forever,daemon=True).start()
INIT = """window.__calls=[]; window.__engine_used=false;
window.SPK_IOS={features:{transcode:true},
  probe:async f=>({width:640,height:360,duration:1,fps:30,hasAudio:false,codec:'h264',nativeFile:'in1'}),
  convert:async (f,o)=>{__calls.push(o); o.onProgress&&o.onProgress(0.5); return new Blob([new Uint8Array(1000)],{type:'video/mp4'})},
  cancelConvert:async()=>{}};
window.__VJ_ENGINE__={kind:'wasm',async load(){__engine_used=true},async exec(){__engine_used=true;return{code:1,log:[]}},async write(){},async read(){return new Uint8Array()},async remove(){},async mount(){__engine_used=true;return 'x'},async unmount(){},terminate(){}};"""
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(); ctx.add_init_script(INIT); pg=ctx.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{srv.server_port}/tools/app/index.html"); pg.wait_for_selector("#tabs button"); pg.click("#tabs button[data-t=convert]")
    pg.set_input_files("#picker",[str(T/"a.mp4")]); pg.wait_for_selector("#go:not([disabled])",timeout=30000); pg.click("#go")
    pg.wait_for_function("VJ.JOBS.length && ['done','failed'].includes(VJ.JOBS[0].status)",timeout=30000)
    r=pg.evaluate("({s:VJ.JOBS[0].status,n:VJ.JOBS[0].results.length,name:VJ.JOBS[0].results[0]&&VJ.JOBS[0].results[0].name,calls:__calls,eng:__engine_used,err:VJ.JOBS[0].error||''})")
    print(r)
    for ok,m in [(r["s"]=="done" and r["n"]==1,"job finished with one result"),(len(r["calls"])==1 and r["calls"][0]["width"]==640 and r["calls"][0]["codec"]=="h264","native convert called with target size"),
                 (str(r["name"]).endswith(".mp4"),"result is an mp4"),(not r["eng"],"ffmpeg.wasm engine was not used"),(not errs,"no page errors")]:
        print(("ok   " if ok else "FAIL ")+m); 
        if not ok: bad.append(m)
    b.close()
sys.exit(1 if bad else 0)
