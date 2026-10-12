from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import threading,functools,json,time,hashlib,urllib.request
root=Path(__file__).resolve().parent;out=root/'artifacts/garden-views';out.mkdir(parents=True,exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path=='/blank':
   data=b'<!doctype html><meta charset="utf-8"><title>Reef ready</title><link rel="icon" href="data:,">';self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  else:super().do_GET()
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root/'dist')));threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_address[1])
report={'errors':[],'failedRequests':[],'frames':[],'sourceHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (root/'dist/preview/reef-garden-v1').iterdir()if p.is_file()}}
report['localBlankBytes']=len(urllib.request.urlopen(base+'/blank',timeout=3).read());report['localAppBytes']=len(urllib.request.urlopen(base+'/preview/reef-garden-v1/',timeout=3).read())
with sync_playwright()as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,chromium_sandbox=True,timeout=20000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist'])
 page=browser.new_page(viewport={'width':1280,'height':820},device_scale_factor=1);page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('requestfailed',lambda r:report['failedRequests'].append(r.url));page.on('console',lambda m:report.setdefault('console',[]).append({'type':m.type,'text':m.text}))
 try:
  cdp=page.context.new_cdp_session(page);report['browserCommandVerified']=bool(cdp.send('Browser.getBrowserCommandLine')['arguments'])
  r=page.request.get(base+'/blank',timeout=3000);assert r.status==200;r.dispose();page.goto(base+'/blank',wait_until='commit',timeout=10000);page.wait_for_function("() => document.title==='Reef ready'",timeout=3000);r=page.request.get(base+'/preview/reef-garden-v1/',timeout=3000);assert r.status==200;r.dispose()
  page.goto(base+'/preview/reef-garden-v1/',wait_until='commit',timeout=15000);page.wait_for_function('() => window.reefGarden?.getState().ready || window.reefGardenFailure',timeout=20000)
  failure=page.evaluate('() => window.reefGardenFailure');assert not failure,failure
  page.locator('#more').click();page.locator('#ambient').click();page.locator('#more').click()
  def shot(name):
   page.wait_for_timeout(180);page.screenshot(path=str(out/(name+'.png')),timeout=10000);report['frames'].append({'name':name,'state':page.evaluate('() => window.reefGarden.getState()')});print('FRAME',name,flush=True)
  def reverse(name):
   page.locator('#free').click();page.locator('#sea').focus();page.keyboard.down('ArrowRight');page.wait_for_timeout(2860);page.keyboard.up('ArrowRight');shot(name)
  shot('entry');reverse('entry-reverse');page.locator('[data-stop="2"]').click();shot('mid');reverse('mid-reverse');page.locator('[data-stop="5"]').click();shot('deep');reverse('deep-reverse')
  report['driver']=page.evaluate("() => {const g=document.querySelector('canvas').getContext('webgl2');const e=g.getExtension('WEBGL_debug_renderer_info');return g.getParameter(e.UNMASKED_RENDERER_WEBGL)}");report['status']='PASS'if not report['errors']and not report['failedRequests']else'FAIL'
 except Exception as e:
  report['status']='FAIL';report['failure']=str(e)
  try:report['failureState']=page.evaluate('() => ({url:location.href,failure:window.reefGardenFailure,text:document.body.innerText})');page.screenshot(path=str(out/'failure.png'),timeout=5000)
  except Exception:pass
  print('FAIL',str(e),'CONSOLE',json.dumps(report.get('console',[])),flush=True)
 finally:browser.close()
server.shutdown();server.server_close();(out/'views.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':report['status'],'errors':report['errors'],'failure':report.get('failure'),'frames':len(report['frames'])}),flush=True)
