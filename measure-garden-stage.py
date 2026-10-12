from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import threading,functools,json,time,statistics,hashlib
root=Path(__file__).resolve().parent;out=root/'artifacts/garden-stage'
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root/'dist')));threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_address[1])+'/preview/reef-garden-v1/'
with sync_playwright()as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True,chromium_sandbox=True,timeout=20000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist']);page=browser.new_page(viewport={'width':1280,'height':820},device_scale_factor=1);start=time.monotonic();page.goto(url,wait_until='commit',timeout=20000);page.wait_for_function('() => window.reefGarden?.getState().frames>5',timeout=25000);load=time.monotonic()-start
 page.evaluate('''() => {const r=window.reefGarden.renderer,render=r.render;window.__gaps=[];let last=performance.now();r.render=function(...args){const result=render.apply(this,args),now=performance.now();window.__gaps.push(now-last);last=now;return result}}''');page.locator('#tour').click();start=time.monotonic()
 while time.monotonic()-start<15:page.wait_for_timeout(750)
 gaps=page.evaluate('() => window.__gaps').copy()[10:];assert len(gaps)>150
 gpu=page.evaluate("() => {const g=document.querySelector('canvas').getContext('webgl2'),e=g.getExtension('WEBGL_debug_renderer_info');return g.getParameter(e.UNMASKED_RENDERER_WEBGL)}")
 result={'status':'MEASURED','loadToRenderedSeconds':load,'durationSeconds':time.monotonic()-start,'sampleFrames':len(gaps),'medianFrameGapMs':statistics.median(gaps),'p95FrameGapMs':sorted(gaps)[int(len(gaps)*.95)],'maxFrameGapMs':max(gaps),'over100ms':sum(g>100 for g in gaps),'over250ms':sum(g>250 for g in gaps),'recordingActive':False,'screenshotsDuringMeasurement':False,'gpu':gpu,'scope':'15-second moving tour segment on this machine at 1280x820 in sandboxed headless Edge. No claim about physical mobile, other GPUs or user subjective acceptance.','sourceHashes':{q.name:hashlib.sha256(q.read_bytes()).hexdigest()for q in(root/'dist/preview/reef-garden-v1').iterdir()if q.is_file()}};browser.close()
server.shutdown();server.server_close();(out/'unrecorded-performance.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result),flush=True)
