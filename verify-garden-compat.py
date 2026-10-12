from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import threading,functools,json,time,urllib.request,statistics
root=Path(__file__).resolve().parent;out=root/'artifacts/garden-qa';first=json.loads((out/'browser.json').read_text(encoding='utf-8'));(out/'native-tour-first.json').write_text(json.dumps(first,ensure_ascii=False,indent=2),encoding='utf-8')
assert first['checks']['naturalTour']['passed']and first['checks']['pauseResumeReplay']['passed']and first['checks']['turnInPlace']['passed']and first['checks']['freePortalForwardReverse']['passed']
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path=='/blank':
   data=b'<!doctype html><title>Ready</title><link rel="icon" href="data:,">';self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  else:super().do_GET()
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root/'dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_address[1]);urllib.request.urlopen(base+'/blank',timeout=3).read();report={'status':'RUNNING','errors':[],'checks':{},'reasonForRetest':'The first collision assertion selected a low reef while the swimmer was above its top. Runtime is unchanged; target the actual tall portal pillar.'}
with sync_playwright()as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,chromium_sandbox=True,timeout=20000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist']);context=browser.new_context(viewport={'width':1280,'height':820},has_touch=True);page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
 try:
  cdp=context.new_cdp_session(page);cdp.send('Browser.getBrowserCommandLine');r=context.request.get(base+'/blank',timeout=3000);r.dispose();page.goto(base+'/blank',wait_until='commit',timeout=10000);page.goto(base+'/preview/reef-garden-v1/',wait_until='commit',timeout=15000);page.wait_for_function('() => window.reefGarden?.getState().ready',timeout=20000);state=lambda:page.evaluate('() => window.reefGarden.getState()');page.locator('#sea').focus();page.keyboard.press('Home');page.keyboard.down('w');page.wait_for_timeout(7200);page.keyboard.up('w');print('PILLAR_APPROACH',state()['camera'],flush=True);page.keyboard.down('d');page.wait_for_timeout(3500);page.keyboard.up('d');a=state();page.keyboard.down('d');page.wait_for_timeout(1000);page.keyboard.up('d');b=state();assert abs(a['camera'][0]-b['camera'][0])<.5,'Tall portal pillar should stop the swimmer';page.keyboard.down('a');page.wait_for_timeout(700);page.keyboard.up('a');c=state();assert c['camera'][0]<b['camera'][0]-1;report['checks']['portalCollisionEscape']={'passed':True,'blocked':b['camera'],'escaped':c['camera']};page.screenshot(path=str(out/'portal-collision.png'),timeout=8000);page.keyboard.press('Home');assert state()['camera']==[0,4.2,24];report['checks']['returnHome']={'passed':True}
  narrow=browser.new_context(viewport={'width':390,'height':740},device_scale_factor=1,has_touch=True,is_mobile=True,reduced_motion='reduce');mobile=narrow.new_page();mobile.goto(base+'/blank',wait_until='commit',timeout=10000);mobile.goto(base+'/preview/reef-garden-v1/',wait_until='commit',timeout=15000);mobile.wait_for_function('() => window.reefGarden?.getState().ready',timeout=20000);mobile.locator('[data-key="KeyW"]').tap();a=mobile.evaluate('() => window.reefGarden.getState()');assert a['route']['reduced']and a['camera'][2]<24;mobile.locator('#home').tap();assert mobile.evaluate('() => window.reefGarden.getState().camera')==[0,4.2,24];mobile.screenshot(path=str(out/'mobile-390.png'),timeout=8000);narrow.close();report['checks']['mobileReducedTouch']={'passed':True,'physicalPhoneTested':False};assert not report['errors'];report['status']='PASS'
 except Exception as e:
  report['status']='FAIL';report['failure']=repr(e)
  try:report['failureState']=state();page.screenshot(path=str(out/'compat-failure.png'),timeout=5000)
  except Exception:pass
 finally:browser.close()
server.shutdown();server.server_close();(out/'compat.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report),flush=True)
if report['status']!='PASS':raise SystemExit(1)
final={'status':'PASS','sourceHashes':first['sourceHashes'],'nativeTourSeconds':first['checks']['naturalTour']['wallSeconds'],'checks':{**first['checks'],**report['checks']},'video':first['video'],'scope':'Real desktop tour and input; one bounded collision target correction; 390x740 touch/reduced-motion emulation. Physical phone performance remains untested.','clockInjection':False,'firstFailurePreserved':'native-tour-first.json'};(out/'FINAL.json').write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding='utf-8')
