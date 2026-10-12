from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import threading,functools,json,time,hashlib,shutil,traceback,statistics
root=Path(__file__).resolve().parent;out=root/'artifacts/garden-stage';out.mkdir(exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root/'dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_address[1]);url=base+'/preview/reef-garden-v1/'
report={'status':'RUNNING','errors':[],'failedRequests':[],'views':[],'checks':{},'clockInjection':False,'device':json.loads((root/'artifacts/garden-stage-device.json').read_text(encoding='utf-8-sig')),'sourceHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (root/'dist/preview/reef-garden-v1').iterdir()if p.is_file()},'v11Hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (root/'dist/preview/reef-garden-v11').iterdir()if p.is_file()}}
def save():(out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
with sync_playwright()as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True,chromium_sandbox=True,timeout=20000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist']);context=browser.new_context(viewport={'width':1280,'height':820},device_scale_factor=1,record_video_dir=str(out/'video'),record_video_size={'width':1280,'height':820});page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('requestfailed',lambda r:report['failedRequests'].append(r.url));page.set_default_timeout(15000)
 try:
  cdp=context.new_cdp_session(page);args=cdp.send('Browser.getBrowserCommandLine')['arguments'];assert not any(a in args for a in ['--no-sandbox','--disable-gpu-sandbox','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']);report['browser']=cdp.send('Browser.getVersion');start=time.monotonic();page.goto(url,wait_until='commit',timeout=20000);page.wait_for_function('() => window.reefGarden?.getState().frames>2||window.reefGardenFailure',timeout=25000);assert not page.evaluate('() => window.reefGardenFailure');report['loadToReadySeconds']=time.monotonic()-start
  report['webgl']=page.evaluate("() => {const g=document.querySelector('canvas').getContext('webgl2'),e=g.getExtension('WEBGL_debug_renderer_info');return {renderer:g.getParameter(e.UNMASKED_RENDERER_WEBGL),vendor:g.getParameter(e.UNMASKED_VENDOR_WEBGL),hardwareConcurrency:navigator.hardwareConcurrency,deviceMemory:navigator.deviceMemory,viewport:[innerWidth,innerHeight],pixelRatio:devicePixelRatio}}")
  state=lambda:page.evaluate('() => window.reefGarden.getState()');assert state()['stats']['version']=='01.2-stage'
  page.locator('#more').click();page.locator('#ambient').click();page.locator('#more').click()
  def shot(name):
   page.wait_for_timeout(180);page.screenshot(path=str(out/(name+'.png')),timeout=10000);report['views'].append({'name':name,'state':state()});save();print('VIEW',name,flush=True)
  def reverse(name):
   page.locator('#free').click();page.locator('#sea').focus();page.keyboard.down('ArrowRight');page.wait_for_timeout(2860);page.keyboard.up('ArrowRight');shot(name)
  for i in range(6):
   page.locator('[data-stop="'+str(i)+'"]').click();shot('station-'+str(i+1)+'-front');reverse('station-'+str(i+1)+'-return')
  print('ALL_SIX_STATIONS_CAPTURED',flush=True);report['checks']['sixStationsAndReturn']={'passed':True,'frames':12}
  page.locator('#home').click();page.locator('#more').click();page.locator('#ambient').click();page.locator('#more').click()
  page.evaluate('''() => {const r=window.reefGarden.renderer,render=r.render;window.__stageFrames=[];let last=performance.now();r.render=function(...args){const result=render.apply(this,args),now=performance.now(),s=window.reefGarden.getState();window.__stageFrames.push({gapMs:now-last,elapsed:s.route.elapsed,mode:s.route.mode,camera:s.camera,draws:r.info.render.calls,triangles:r.info.render.triangles});last=now;return result}}''')
  page.locator('#tour').click();start=time.monotonic();i=0
  while True:
   page.wait_for_timeout(600);s=state()
   if i<5 and s['route']['elapsed']>=[12,26,40,54,66][i]:shot('natural-motion-'+str(i+1));i+=1
   if s['route']['mode']=='completed':break
   assert time.monotonic()-start<105,'Bounded natural tour deadline'
  wall=time.monotonic()-start;assert wall>=72 and s['route']['elapsed']==72;shot('natural-end');report['checks']['naturalTour']={'passed':True,'wallSeconds':wall,'elapsed':72,'final':s};print('NATURAL_TOUR_COMPLETE',wall,flush=True)
  frames=page.evaluate('() => window.__stageFrames');gaps=[f['gapMs']for f in frames if f['mode']=='tour'and .5<f['elapsed']<71];assert len(gaps)>200
  report['performance']={'sampleFrames':len(gaps),'medianFrameGapMs':statistics.median(gaps),'p95FrameGapMs':sorted(gaps)[int(len(gaps)*.95)],'maxFrameGapMs':max(gaps),'over100ms':sum(g>100 for g in gaps),'over250ms':sum(g>250 for g in gaps),'recordingActive':True,'scope':'This Windows machine, 1280x820, Edge headless, actual ANGLE GPU above; includes screenshot/recording overhead. Not a physical phone or other-device performance claim.'};(out/'tour-frames.json').write_text(json.dumps(frames),encoding='utf-8');print('PERFORMANCE',json.dumps(report['performance']),flush=True)
  page.locator('#tour').click();page.wait_for_timeout(700);a=state();assert 0<a['route']['elapsed']<3;page.locator('#pause').click();a=state();page.wait_for_timeout(400);assert state()['camera']==a['camera']and state()['route']['elapsed']==a['route']['elapsed'];page.locator('#pause').click();page.wait_for_timeout(400);assert state()['route']['elapsed']>a['route']['elapsed'];report['checks']['replayPauseResume']={'passed':True}
  page.locator('#home').click();assert state()['camera']==[0,4.2,24];page.locator('#sea').focus();page.keyboard.down('w');page.keyboard.down('Shift');page.wait_for_timeout(5500);page.keyboard.up('Shift');page.keyboard.up('w');a=state();assert a['camera'][2]<-30;shot('free-through-portal');page.keyboard.down('s');page.wait_for_timeout(800);page.keyboard.up('s');assert state()['camera'][2]>a['camera'][2]+1;report['checks']['freeForwardReverse']={'passed':True}
  page.keyboard.press('Home');page.locator('#sea').focus();page.keyboard.down('w');approach=time.monotonic()
  while state()['camera'][2]>-25.8:
   page.wait_for_timeout(100);assert time.monotonic()-approach<15,'Bounded approach to portal pillar'
  page.keyboard.up('w');page.keyboard.down('d');page.wait_for_timeout(6000);page.keyboard.up('d');a=state();page.keyboard.down('d');page.wait_for_timeout(1000);page.keyboard.up('d');b=state();assert 7<b['camera'][0]<9 and abs(a['camera'][0]-b['camera'][0])<.5,'Portal pillar collision';page.keyboard.down('a');page.wait_for_timeout(900);page.keyboard.up('a');c=state();assert c['camera'][0]<b['camera'][0]-1;shot('collision-escape');page.keyboard.press('Home');assert state()['camera']==[0,4.2,24];report['checks']['collisionEscapeAndHome']={'passed':True,'blocked':b['camera'],'escaped':c['camera']}
  page.locator('#previous').click();assert page.locator('#previousMenu').is_visible();page.keyboard.press('Escape');assert not page.locator('#previousMenu').is_visible();report['checks']['desktopMenu']={'passed':True,'hrefs':page.locator('#previousMenu a').evaluate_all('(links) => links.map(a=>a.getAttribute("href"))')}
  mobileContext=browser.new_context(viewport={'width':390,'height':740},has_touch=True,is_mobile=True,reduced_motion='reduce');mobile=mobileContext.new_page();mobile.goto(url,wait_until='commit',timeout=20000);mobile.wait_for_function('() => window.reefGarden?.getState().ready',timeout=25000);mobile.locator('#previous').tap();assert mobile.locator('#previousMenu').is_visible();menu=mobile.locator('#previousMenu').bounding_box();touch=mobile.locator('.touch-controls').bounding_box();dock=mobile.locator('.dock').bounding_box();assert menu['y']+menu['height']<min(touch['y'],dock['y']);mobile.screenshot(path=str(out/'mobile-menu.png'),timeout=10000);mobile.locator('#closePrevious').tap();assert not mobile.locator('#previousMenu').is_visible();mobile.locator('[data-key="KeyW"]').tap();assert mobile.evaluate('() => window.reefGarden.getState().camera[2]')<24;mobile.locator('#home').tap();assert mobile.evaluate('() => window.reefGarden.getState().camera')==[0,4.2,24];mobile.screenshot(path=str(out/'mobile-closed.png'),timeout=10000);mobileContext.close();report['checks']['mobileMenuCloseSwimHome']={'passed':True,'physicalPhoneTested':False};assert not report['errors']and not report['failedRequests'];report['status']='PASS'
 except Exception as e:
  report['status']='FAIL';report['failure']=repr(e);report['failureState']=state();report['traceback']=traceback.format_exc();print(report['traceback'],flush=True)
  try:page.screenshot(path=str(out/'failure.png'),timeout=8000)
  except Exception:pass
 finally:
  video=page.video;context.close();shutil.copyfile(video.path(),out/'complete-demo.webm');browser.close()
server.shutdown();server.server_close();save();print(json.dumps({'status':report['status'],'checks':list(report['checks']),'failure':report.get('failure')}),flush=True)
if report['status']!='PASS':raise SystemExit(1)
