from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import threading,functools,json,time,hashlib,traceback
root=Path(__file__).resolve().parent;out=root/'artifacts/basin-proof';out.mkdir(exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root/'dist')));threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_address[1])+'/preview/reef-basin-proof/'
report={'status':'RUNNING','errors':[],'consoleErrors':[],'failedRequests':[],'views':[],'sourceHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in(root/'dist/preview/reef-basin-proof').iterdir()if p.is_file()}}
with sync_playwright()as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True,chromium_sandbox=True,timeout=20000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist']);page=browser.new_page(viewport={'width':1280,'height':820},device_scale_factor=1);page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('requestfailed',lambda r:report['failedRequests'].append(r.url));page.on('console',lambda m:report['consoleErrors'].append(m.text)if m.type=='error'else None)
 try:
  args=page.context.new_cdp_session(page).send('Browser.getBrowserCommandLine')['arguments'];assert not any(a in args for a in ['--no-sandbox','--disable-gpu-sandbox','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']);start=time.monotonic();page.goto(url,wait_until='commit',timeout=20000);page.wait_for_function('() => window.basinProof?.getState().frames>3||window.basinFailure',timeout=30000);assert not page.evaluate('() => window.basinFailure');report['loadSeconds']=time.monotonic()-start;state=lambda:page.evaluate('() => window.basinProof.getState()')
  def shot(name):page.screenshot(path=str(out/(name+'.png')),timeout=12000);report['views'].append({'name':name,'state':state()});print('VIEW',name,flush=True)
  shot('first-front');page.locator('#free').click();page.locator('#sea').focus();page.keyboard.down('ArrowRight');page.wait_for_timeout(2860);page.keyboard.up('ArrowRight');shot('first-return');page.keyboard.down('ArrowRight');page.wait_for_timeout(1430);page.keyboard.up('ArrowRight');shot('first-side');page.keyboard.press('Home');report['gpu']=page.evaluate("() => {const g=document.querySelector('canvas').getContext('webgl2'),e=g.getExtension('WEBGL_debug_renderer_info');return g.getParameter(e.UNMASKED_RENDERER_WEBGL)}");assert not report['errors']and not report['consoleErrors']and not report['failedRequests'];report['status']='TECHNICAL_CAPTURE_PASS_VISUAL_REVIEW_PENDING'
 except Exception as e:
  report['status']='FAIL';report['failure']=repr(e);report['traceback']=traceback.format_exc();print(report['traceback'],flush=True)
  try:page.screenshot(path=str(out/'capture-failure.png'),timeout=8000)
  except Exception:pass
 finally:browser.close()
server.shutdown();server.server_close();(out/'first-capture.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':report['status'],'errors':report['errors'],'consoleErrors':report['consoleErrors'],'failure':report.get('failure')}),flush=True)
if report['status']=='FAIL':raise SystemExit(1)
