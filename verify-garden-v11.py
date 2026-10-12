from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import threading,functools,json,time,hashlib,shutil,traceback,sys
root=Path(__file__).resolve().parent;out=root/'artifacts/garden-v11';out.mkdir(exist_ok=True)
public='https://yydshly.github.io/azure-reef-3d/'
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path in ['/preview/world/','/preview/real-splats-probe/']:
   self.send_response(302);self.send_header('Location',public+self.path.lstrip('/'));self.end_headers()
  else:super().do_GET()
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root/'dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_address[1]);url=base+'/preview/reef-garden-v1/'
report={'status':'RUNNING','errors':[],'failedRequests':[],'views':[],'checks':{},'clockInjection':False,'sourceHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (root/'dist/preview/reef-garden-v1').iterdir()if p.is_file()},'firstVersionHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (root/'dist/preview/reef-garden-v1-first').iterdir()if p.is_file()}}
resume='--resume-controls'in sys.argv
if resume:
 previous=json.loads((out/'verification.json').read_text(encoding='utf-8'));assert previous['sourceHashes']==report['sourceHashes'];report['views']=previous['views'];(out/'first-link-assertion-failure.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),encoding='utf-8')
with sync_playwright()as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True,chromium_sandbox=True,timeout=20000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist'])
 context=browser.new_context(viewport={'width':1280,'height':820},device_scale_factor=1,record_video_dir=str(out/'video'),record_video_size={'width':1280,'height':820});page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('requestfailed',lambda r:report['failedRequests'].append(r.url))
 try:
  args=context.new_cdp_session(page).send('Browser.getBrowserCommandLine')['arguments'];assert not any(a in args for a in ['--no-sandbox','--disable-gpu-sandbox','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
  page.goto(url,wait_until='commit',timeout=20000);page.wait_for_function('() => window.reefGarden?.getState().frames>2 || window.reefGardenFailure',timeout=25000);assert not page.evaluate('() => window.reefGardenFailure')
  state=lambda:page.evaluate('() => window.reefGarden.getState()')
  page.locator('#more').click();page.locator('#ambient').click();page.locator('#more').click()
  def shot(name):
   page.wait_for_timeout(180);page.screenshot(path=str(out/(name+'.png')),timeout=10000);report['views'].append({'name':name,'state':state()});print('VIEW',name,flush=True)
  def reverse(name):
   page.locator('#free').click();page.locator('#sea').focus();page.keyboard.down('ArrowRight');page.wait_for_timeout(2860);page.keyboard.up('ArrowRight');shot(name)
  if not resume:
   shot('entry');reverse('entry-reverse');page.locator('[data-stop="2"]').click();shot('mid');reverse('mid-reverse');page.locator('[data-stop="5"]').click();shot('deep');reverse('deep-reverse')
  page.locator('#previous').click();assert page.locator('#previousMenu').is_visible();shot('desktop-menu');page.keyboard.press('Escape');assert not page.locator('#previousMenu').is_visible()
  links=[]
  for selector,path in [('#oldWorld','preview/world/'),('#realProbe','preview/real-splats-probe/')]:
   page.locator('#previous').click()
   with page.expect_popup(timeout=15000)as result:page.locator(selector).click()
   popup=result.value;popup.wait_for_load_state('domcontentloaded',timeout=20000);popup.locator('h1').wait_for(state='visible',timeout=15000);assert popup.url==public+path,popup.url;popup.wait_for_timeout(800);popup.screenshot(path=str(out/(selector[1:]+'-opened.png')),timeout=10000);links.append({'url':popup.url,'title':popup.title(),'heading':popup.locator('h1').inner_text(),'probeStatus':popup.locator('#stage').inner_text()if selector=='#realProbe'else None});popup.close();assert not page.locator('#previousMenu').is_visible(),'Menu must close after native link click'
  report['checks']['previousLinksOpened']={'passed':True,'links':links,'scope':'Native popup clicks and rendered old page UI; no new Gaussian diagnostics or old-scene completeness acceptance.'};print('OLD_LINKS_OPEN',flush=True)
  page.locator('#previous').click()
  with page.expect_popup(timeout=15000)as result:page.locator('#firstGarden').click()
  first=result.value;first.wait_for_function('() => window.reefGarden?.getState().ready',timeout=20000);assert first.evaluate('() => window.reefGarden.getState().stats.formations')==29;first.close();report['checks']['frozenFirstVersion']={'passed':True}
  page.locator('#home').click();page.locator('#more').click();page.locator('#ambient').click();page.locator('#more').click();page.locator('#tour').click();start=time.monotonic();i=0
  while True:
   page.wait_for_timeout(600);s=state()
   if i<3 and s['route']['elapsed']>=[15,35,58][i]:shot('motion-'+str(i+1));i+=1
   if s['route']['mode']=='completed':break
   assert time.monotonic()-start<105,'Bounded natural tour deadline'
  wall=time.monotonic()-start;assert wall>=72 and s['route']['elapsed']==72;shot('tour-end');report['checks']['naturalTour']={'passed':True,'wallSeconds':wall,'elapsed':72,'final':s};print('NATURAL_TOUR_COMPLETE',wall,flush=True)
  reverse('end-return-look');page.locator('#home').click();assert state()['camera']==[0,4.2,24]
  page.locator('#tour').click();page.wait_for_timeout(700);page.locator('#pause').click();a=state();page.wait_for_timeout(400);b=state();assert a['camera']==b['camera']and a['route']['elapsed']==b['route']['elapsed'];page.locator('#pause').click();page.wait_for_timeout(300);assert state()['route']['elapsed']>b['route']['elapsed'];page.locator('#home').click();report['checks']['pauseResumeHome']={'passed':True}
  mobileContext=browser.new_context(viewport={'width':390,'height':740},has_touch=True,is_mobile=True,reduced_motion='reduce');mobile=mobileContext.new_page();mobile.goto(url,wait_until='commit',timeout=20000);mobile.wait_for_function('() => window.reefGarden?.getState().ready',timeout=25000);mobile.locator('#previous').tap();assert mobile.locator('#previousMenu').is_visible();menu=mobile.locator('#previousMenu').bounding_box();touch=mobile.locator('.touch-controls').bounding_box();dock=mobile.locator('.dock').bounding_box();assert menu['y']+menu['height']<min(touch['y'],dock['y']);mobile.screenshot(path=str(out/'mobile-menu.png'),timeout=10000);mobile.locator('#closePrevious').tap();assert not mobile.locator('#previousMenu').is_visible();mobile.locator('[data-key="KeyW"]').tap();assert mobile.evaluate('() => window.reefGarden.getState().camera[2]')<24;mobile.locator('#home').tap();mobile.locator('#previous').tap();mobile.locator('#home').tap();assert not mobile.locator('#previousMenu').is_visible();assert mobile.evaluate('() => window.reefGarden.getState().camera')==[0,4.2,24];mobile.screenshot(path=str(out/'mobile-closed.png'),timeout=10000);mobileContext.close();report['checks']['mobileMenuCloseSwimAndOutsideDismiss']={'passed':True,'menuBounds':menu,'physicalPhoneTested':False}
  assert not report['errors']and not report['failedRequests'];report['status']='PASS'
 except Exception as e:
  report['status']='FAIL';report['failure']=repr(e);report['traceback']=traceback.format_exc();print('FAIL',report['traceback'],flush=True)
  try:page.screenshot(path=str(out/'failure.png'),timeout=8000)
  except Exception:pass
 finally:
  video=page.video;context.close();shutil.copyfile(video.path(),out/'natural-tour.webm');browser.close()
server.shutdown();server.server_close();(out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':report['status'],'checks':list(report['checks']),'failure':report.get('failure')}),flush=True)
if report['status']!='PASS':raise SystemExit(1)
