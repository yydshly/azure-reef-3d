"""Targeted native collision/phone-layout retest; preserves the recorded tour run."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json,threading,functools,time,statistics
root=Path(__file__).resolve().parent;output=root/'artifacts/continuous-compat';output.mkdir(parents=True,exist_ok=True)
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
report={'status':'RUNNING','checks':{},'errors':[],'clockInjection':False,'previousTourRun':'../continuous-motion/verification.json','previousFailureReason':'The first collision check strafed at z=10, outside the visible near-left reef. The assertion selected an empty location; no runtime change was made for this retest.'}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,chromium_sandbox=True,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist'])
 page=browser.new_page(viewport={'width':1280,'height':820},has_touch=True)
 page.on('pageerror',lambda e:report['errors'].append(str(e)))
 url='http://127.0.0.1:'+str(server.server_address[1])+'/artifacts/continuous-candidate/scan-exhibit.html'
 try:
  page.goto(url,wait_until='domcontentloaded',timeout=30000);page.wait_for_function("() => window.reefExhibit?.getState().ready && window.reefExhibit.getState().assemblage.status==='ready'",timeout=90000)
  page.evaluate('''() => {const e=window.reefExhibit,r=e.renderer,original=r.render;window.__compatFrames=[];let previous=performance.now();r.render=function(...args){const value=original.apply(this,args),now=performance.now();window.__compatFrames.push({gap:now-previous,triangles:r.info.render.triangles,draws:r.info.render.calls});previous=now;return value;}}''')
  state=lambda:page.evaluate('() => window.reefExhibit.getState()')
  canvas=page.locator('#scanCanvas');canvas.focus();page.keyboard.press('Home');page.keyboard.down('w');page.wait_for_timeout(4300);page.keyboard.up('w');a=state();print('COLLISION_APPROACH',a['camera'],flush=True)
  page.keyboard.down('a');page.wait_for_timeout(5500);page.keyboard.up('a');a=state();page.keyboard.down('a');page.wait_for_timeout(1200);page.keyboard.up('a');b=state()
  assert abs(a['camera'][0]-b['camera'][0])<.4,'Strafe should stop at visible near-left reef'
  assert -28<a['camera'][0]<3.9 and a['camera'][2]<-5
  report['checks']['nativeVisibleReefCollision']={'passed':True,'first':a['camera'],'second':b['camera']};page.locator('#scanStage').screenshot(path=str(output/'native-collision.png'),timeout=20000)
  page.keyboard.down('d');page.wait_for_timeout(800);page.keyboard.up('d');c=state();assert c['camera'][0]>b['camera'][0]+1
  report['checks']['escapeFromCollision']={'passed':True,'position':c['camera']}
  page.keyboard.press('Home');report['frames']=page.evaluate('() => window.__compatFrames');gaps=[f['gap']for f in report['frames'] if 0<f['gap']<1500]
  report['performance']={'medianFrameGapMs':statistics.median(gaps),'p95FrameGapMs':sorted(gaps)[int(len(gaps)*.95)],'actualFrames':len(report['frames']),'maxTriangles':max(f['triangles']for f in report['frames']),'maxDraws':max(f['draws']for f in report['frames']),'scope':'This one Intel UHD desktop during a 12-second native free-movement segment, no video recording; not a mobile benchmark.'}
  narrow=browser.new_context(viewport={'width':390,'height':740},device_scale_factor=1,has_touch=True,is_mobile=True,reduced_motion='reduce');mobile=narrow.new_page();mobile.on('pageerror',lambda e:report['errors'].append(str(e)))
  mobile.goto(url,wait_until='domcontentloaded',timeout=30000);mobile.wait_for_function('() => window.reefExhibit?.getState().ready',timeout=90000)
  mobile.locator('#swimForward').tap();a=mobile.evaluate('() => window.reefExhibit.getState()');assert a['route']['reduced'];assert a['camera'][2]<10
  mobile.locator('#hudMoreSummary').tap();mobile.locator('#resetExhibit').tap();mobile.locator('#closeHudMore').tap();b=mobile.evaluate('() => window.reefExhibit.getState()');assert b['camera']==[4,5,10]
  mobile.locator('#scanStage').screenshot(path=str(output/'mobile-390.png'),timeout=20000)
  report['checks']['emulatedTouchAndReducedMotion']={'passed':True,'viewport':[390,740],'tapMoved':a['camera'],'reset':b['camera'],'hardwareTouchTested':False};narrow.close()
  assert not report['errors'];report['status']='PASS'
 except Exception as e:
  report['status']='FAIL';report['failure']=str(e);print('COMPAT_FAILURE',str(e),flush=True)
  try:report['failureState']=state();page.screenshot(path=str(output/'failure.png'),timeout=15000)
  except Exception:pass
 finally:browser.close()
server.shutdown();server.server_close();(output/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':report['checks'],'performance':report.get('performance'),'failure':report.get('failure')}),flush=True)
if report['status']!='PASS':raise SystemExit(1)
