from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import base64,json,hashlib,sys
repo=Path.cwd();out=repo/'artifacts/remaining-release'/('public' if '--public' in sys.argv else ('local-rebuilt' if '--rebuilt' in sys.argv else 'local'));out.mkdir(exist_ok=True)
class H(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=None
if '--public' in sys.argv:base='https://yydshly.github.io/azure-reef-3d/'
else:server=ThreadingHTTPServer(('127.0.0.1',0),partial(H,directory=str(repo/'dist')));Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_port)+'/'
result={'base':base,'samples':[],'errors':[],'actualWebgl2PixelProbe':'browser-capability.json'}
try:
 print('NATIVE_BROWSER_TEST_START',flush=True)
 with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,chromium_sandbox=True,timeout=15000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist']);page=browser.new_page(viewport={'width':1280,'height':820});page.on('pageerror',lambda e:result['errors'].append(str(e)))
    for key in (['connected-hardbottom','shoulder-sample','visible-ledge','late-bank-grey'] if '--rebuilt' in sys.argv else ['solid-shoulder','staggered-colony','volume-shoulder']):
        print('SAMPLE_BEGIN',key,flush=True)
        page.goto(base+'preview/sample-'+key+'/',wait_until='commit',timeout=20000);page.wait_for_function('window.originalSample?.getState().frames>3',timeout=20000)
        state=page.evaluate('window.originalSample.getState()');assert state['renderer']['calls']>0 and state['triangles']>0;assert state['modelMatrix']==state['originalMatrix']
        raw=page.evaluate('window.originalSample.capture()');(out/(key+'.png')).write_bytes(base64.b64decode(raw.split(',',1)[1]));before=state['camera'];page.locator('[data-view="side"]').click();after=page.evaluate('window.originalSample.getState().camera');assert sum(abs(a-b) for a,b in zip(before,after))>.01
        metadata=page.evaluate('window.originalSample.metadata');result['samples'].append({'id':key,'ready':True,'drawCalls':state['renderer']['calls'],'triangles':state['triangles'],'cameraChanged':True,'originalRootTransformPreserved':True,'sourceSha256':metadata['sha256']});print('RAW_SAMPLE_RENDER_AND_VIEW_PASS',key,flush=True)
    assert not result['errors'];result['status']='PASS';browser.close()
except Exception as e:result.update(status='FAIL',error=str(e));raise
finally:
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    if server:server.shutdown();server.server_close()
