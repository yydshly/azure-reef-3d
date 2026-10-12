from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import threading,functools,json,time,statistics,hashlib,urllib.request
root=Path(__file__).resolve().parent;out=root/'artifacts/garden-qa';out.mkdir(parents=True,exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path=='/blank':
   data=b'<!doctype html><title>Reef ready</title><link rel="icon" href="data:,">';self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  else:super().do_GET()
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root/'dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_address[1]);url=base+'/preview/reef-garden-v1/'
assert urllib.request.urlopen(base+'/blank',timeout=3).status==200
report={'status':'RUNNING','errors':[],'requestsFailed':[],'checks':{},'sourceHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (root/'dist/preview/reef-garden-v1').iterdir()if p.is_file()},'clockInjection':False}
def save():(out/'browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
save()
with sync_playwright()as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,chromium_sandbox=True,timeout=20000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist'])
 context=browser.new_context(viewport={'width':1280,'height':820},device_scale_factor=1,has_touch=True,record_video_dir=str(out/'video'),record_video_size={'width':1280,'height':820});page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('requestfailed',lambda r:report['requestsFailed'].append(r.url))
 try:
  cdp=context.new_cdp_session(page);args=cdp.send('Browser.getBrowserCommandLine')['arguments'];assert not any(a in args for a in ['--no-sandbox','--disable-gpu-sandbox','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']);r=context.request.get(base+'/blank',timeout=3000);assert r.status==200;r.dispose();page.goto(base+'/blank',wait_until='commit',timeout=10000);page.wait_for_function("() => document.title==='Reef ready'",timeout=3000)
  page.goto(url,wait_until='commit',timeout=15000);page.wait_for_function('() => window.reefGarden?.getState().ready || window.reefGardenFailure',timeout=20000);assert not page.evaluate('() => window.reefGardenFailure')
  state=lambda:page.evaluate('() => window.reefGarden.getState()')
  report['initial']=state();print('GARDEN_READY',flush=True)
  page.evaluate('''() => {const e=window.reefGarden,r=e.renderer,render=r.render;window.__gardenFrames=[];window.__gardenEvents=[];let previous=performance.now();for(const type of ['keydown','keyup','click','pointerdown','pointerup'])document.addEventListener(type,event=>window.__gardenEvents.push({type,trusted:event.isTrusted,target:event.target.id||null,key:event.code||null}),true);r.render=function(...args){const result=render.apply(this,args),now=performance.now(),s=e.getState();window.__gardenFrames.push({wallMs:now,gap:now-previous,elapsed:s.route.elapsed,mode:s.route.mode,position:s.camera,triangles:r.info.render.triangles,draws:r.info.render.calls});previous=now;return result}}''')
  page.locator('#tour').click();start=time.monotonic();milestones=[(12,'tour-portal'),(31,'tour-meadow'),(53,'tour-moon-arc')];i=0
  while True:
   page.wait_for_timeout(700);s=state()
   if i<len(milestones)and s['route']['elapsed']>=milestones[i][0]:page.screenshot(path=str(out/(milestones[i][1]+'.png')),timeout=10000);print('NATURAL_TOUR',s['route']['elapsed'],s['camera'],flush=True);i+=1
   if s['route']['mode']=='completed':break
   assert time.monotonic()-start<105,'Bounded natural tour deadline'
  wall=time.monotonic()-start;assert wall>=72 and s['route']['elapsed']==72;report['checks']['naturalTour']={'passed':True,'wallSeconds':wall,'elapsed':72,'final':s};page.screenshot(path=str(out/'tour-completed.png'),timeout=10000)
  page.locator('#tour').click();page.wait_for_timeout(600);a=state();assert 0<a['route']['elapsed']<3;page.locator('#pause').click();a=state();page.wait_for_timeout(500);b=state();assert a['camera']==b['camera']and a['route']['elapsed']==b['route']['elapsed'];page.locator('#pause').click();page.wait_for_timeout(500);assert state()['route']['elapsed']>b['route']['elapsed'];report['checks']['pauseResumeReplay']={'passed':True}
  page.locator('#free').click();page.locator('#sea').focus();a=state();page.keyboard.down('ArrowRight');page.wait_for_timeout(2860);page.keyboard.up('ArrowRight');b=state();assert a['camera']==b['camera'];assert abs(b['route']['yaw']-a['route']['yaw'])>2;report['checks']['turnInPlace']={'passed':True};page.keyboard.press('Home');assert state()['camera']==[0,4.2,24]
  page.keyboard.down('w');page.keyboard.down('Shift');page.wait_for_timeout(5500);page.keyboard.up('Shift');page.keyboard.up('w');a=state();assert a['camera'][2]<-30,'Free swimming must pass the coral portal';page.screenshot(path=str(out/'free-through-portal.png'),timeout=10000);page.keyboard.down('s');page.wait_for_timeout(900);page.keyboard.up('s');b=state();assert b['camera'][2]>a['camera'][2]+2;report['checks']['freePortalForwardReverse']={'passed':True,'forward':a['camera'],'reverse':b['camera']}
  page.keyboard.press('Home');page.keyboard.down('w');page.wait_for_timeout(4100);page.keyboard.up('w');page.keyboard.down('d');page.wait_for_timeout(6200);page.keyboard.up('d');a=state();page.keyboard.down('d');page.wait_for_timeout(900);page.keyboard.up('d');b=state();assert abs(a['camera'][0]-b['camera'][0])<.6;page.keyboard.down('a');page.wait_for_timeout(700);page.keyboard.up('a');c=state();assert c['camera'][0]<b['camera'][0]-1;report['checks']['reefCollisionEscape']={'passed':True,'blocked':b['camera'],'escaped':c['camera']};page.keyboard.press('Home');assert state()['camera']==[0,4.2,24];report['checks']['returnHome']={'passed':True}
  frames=page.evaluate('() => window.__gardenFrames');events=page.evaluate('() => window.__gardenEvents');assert all(e['trusted']for e in events);report['events']=events;report['frames']=frames;gaps=[f['gap']for f in frames if f['mode']=='tour'and .5<f['elapsed']<71 and 0<f['gap']<2000];report['performance']={'medianFrameGapMs':statistics.median(gaps),'p95FrameGapMs':sorted(gaps)[int(len(gaps)*.95)],'recordingActive':True,'scope':'One Intel UHD Windows desktop; not a physical phone benchmark.'}
  narrow=browser.new_context(viewport={'width':390,'height':740},device_scale_factor=1,has_touch=True,is_mobile=True,reduced_motion='reduce');mobile=narrow.new_page();mobile.goto(base+'/blank',wait_until='commit',timeout=10000);mobile.goto(url,wait_until='commit',timeout=15000);mobile.wait_for_function('() => window.reefGarden?.getState().ready',timeout=20000);mobile.locator('[data-key="KeyW"]').tap();a=mobile.evaluate('() => window.reefGarden.getState()');assert a['route']['reduced']and a['camera'][2]<24;mobile.locator('#home').tap();assert mobile.evaluate('() => window.reefGarden.getState().camera')==[0,4.2,24];mobile.screenshot(path=str(out/'mobile-390.png'),timeout=10000);narrow.close();report['checks']['mobileReducedTouch']={'passed':True,'physicalPhoneTested':False};assert not report['errors']and not report['requestsFailed'];report['status']='PASS'
 except Exception as e:
  report['status']='FAIL';report['failure']=repr(e);print('GARDEN_FAILURE',repr(e),flush=True)
  try:report['failureState']=state();page.screenshot(path=str(out/'failure.png'),timeout=8000)
  except Exception:pass
 finally:video=page.video;context.close();report['video']=str(Path(video.path()).relative_to(root));browser.close();save()
server.shutdown();server.server_close();print(json.dumps({'status':report['status'],'checks':list(report['checks']),'performance':report.get('performance'),'failure':report.get('failure')}),flush=True)
if report['status']!='PASS':raise SystemExit(1)
