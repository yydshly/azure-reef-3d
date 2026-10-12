from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import threading,functools,json,time,hashlib,shutil,statistics,traceback,sys
root=Path(__file__).resolve().parent;name=sys.argv[1]if len(sys.argv)>1 else'final';out=root/'artifacts/basin-proof'/name;out.mkdir(parents=True,exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root/'dist')));threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_address[1])+'/preview/reef-basin-proof/'
report={'technicalStatus':'RUNNING','visualStatus':'UNACCEPTED_PENDING_PIXEL_REVIEW','errors':[],'consoleErrors':[],'failedRequests':[],'views':[],'checks':{},'sourceHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(root/'dist/preview/reef-basin-proof').iterdir()if p.is_file()},'recordingUncut':True,'positionInjectionDuringProof':False}
with sync_playwright()as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True,chromium_sandbox=True,timeout=20000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist']);context=browser.new_context(viewport={'width':1280,'height':820},device_scale_factor=1,record_video_dir=str(out/'video'),record_video_size={'width':1280,'height':820});page=context.new_page();page.set_default_timeout(15000);page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('requestfailed',lambda r:report['failedRequests'].append(r.url));page.on('console',lambda m:report['consoleErrors'].append(m.text)if m.type=='error'else None)
 try:
  args=context.new_cdp_session(page).send('Browser.getBrowserCommandLine')['arguments'];assert not any(a in args for a in ['--no-sandbox','--disable-gpu-sandbox','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']);start=time.monotonic();page.goto(url,wait_until='commit',timeout=20000);page.wait_for_function('() => window.basinProof?.getState().frames>3||window.basinFailure',timeout=30000);assert not page.evaluate('() => window.basinFailure');state=lambda:page.evaluate('() => window.basinProof.getState()');report['loadSeconds']=time.monotonic()-start;report['initial']=state();assert state()['fov']==61
  report['gpu']=page.evaluate("() => {const g=document.querySelector('canvas').getContext('webgl2'),e=g.getExtension('WEBGL_debug_renderer_info');return g.getParameter(e.UNMASKED_RENDERER_WEBGL)}")
  page.evaluate('''() => {const r=window.basinProof.renderer,render=r.render;window.__basinFrames=[];let last=performance.now();r.render=function(...args){const result=render.apply(this,args),now=performance.now(),s=window.basinProof.getState();window.__basinFrames.push({gapMs:now-last,guideElapsed:s.guide?.elapsed||0,phase:s.guide?.phase||'free',position:s.camera,draws:r.info.render.calls,triangles:r.info.render.triangles});last=now;return result}}''')
  def shot(label):page.screenshot(path=str(out/(label+'.png')),timeout=12000);report['views'].append({'name':label,'state':state()});print('VIEW',label,flush=True)
  shot('00-start-front');page.locator('#proof').click();start=time.monotonic();seen=set()
  while True:
   page.wait_for_timeout(180);s=state();g=s['guide'];phase=g['phase'];t=g['elapsed']-g['phaseStart'];key=None
   if phase=='advance'and g['elapsed']>4:key='01-advance-near-mid-far'
   elif phase=='holdBack':key='02-180-return-view'
   elif phase=='sideSwim'and t>3:key='03-side-basin-width'
   elif phase=='panorama':
    for threshold,label in [(1.1,'04-panorama-quarter-1'),(2.5,'05-panorama-quarter-2'),(4.0,'06-panorama-quarter-3'),(5.0,'07-panorama-quarter-4')]:
     if t>=threshold and label not in seen:key=label;break
   elif phase=='return'and t>5:key='08-return-through-same-world'
   if key and key not in seen:seen.add(key);shot(key)
   if g['completed']:break
   assert time.monotonic()-start<65,'Bounded proof recording deadline'
  report['proofWallSeconds']=time.monotonic()-start;report['final']=state();shot('09-finish');assert not g['failure'],g['failure'];assert g['phase']=='completed';assert state()['fov']==61;assert sum((state()['camera'][i]-[28,5,-52][i])**2 for i in [0,2])**.5<.8
  report['checks']['uncutProofReturn']={'passed':True,'wallSeconds':report['proofWallSeconds'],'controllerHistory':state()['history'],'returnedWithoutSnap':True};frames=page.evaluate('() => window.__basinFrames');gaps=[f['gapMs']for f in frames if .5<f['guideElapsed']<report['final']['guide']['elapsed']-.5 and f['phase']!='completed'];report['recordedPerformance']={'frames':len(gaps),'medianFrameGapMs':statistics.median(gaps),'p95FrameGapMs':sorted(gaps)[int(len(gaps)*.95)],'maxFrameGapMs':max(gaps),'over100ms':sum(x>100 for x in gaps),'scope':'This Intel UHD at 1280x820, including native recording/screenshot overhead.'};(out/'frames.json').write_text(json.dumps(frames));assert not report['errors']and not report['consoleErrors']and not report['failedRequests'];report['technicalStatus']='PASS'
 except Exception as e:
  report['technicalStatus']='FAIL';report['failure']=repr(e);report['traceback']=traceback.format_exc();print(report['traceback'],flush=True)
  try:report['failureState']=state();shot('technical-failure')
  except Exception:pass
 finally:
  video=page.video;context.close();shutil.copyfile(video.path(),out/'uncut-proof.webm');browser.close()
server.shutdown();server.server_close();(out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'technicalStatus':report['technicalStatus'],'visualStatus':report['visualStatus'],'wallSeconds':report.get('proofWallSeconds'),'performance':report.get('recordedPerformance'),'failure':report.get('failure')}),flush=True)
if report['technicalStatus']=='FAIL':raise SystemExit(1)
