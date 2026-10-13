from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import json,base64,sys
repo=Path.cwd();public='--public' in sys.argv
out=repo/'artifacts/remaining-release'/('public-portal' if public else 'local-portal');out.mkdir(exist_ok=True)
class H(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=None
if public:base='https://yydshly.github.io/azure-reef-3d/'
else:
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(H,directory=str(repo/'dist')))
    Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_port)+'/'
result={'base':base,'errors':[]}
try:
    print('PORTAL_START',flush=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,chromium_sandbox=True,timeout=15000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist'])
        page=browser.new_page(viewport={'width':1280,'height':820});page.set_default_timeout(15000)
        page.on('pageerror',lambda e:result['errors'].append(str(e)))
        page.goto(base,wait_until='commit',timeout=20000);page.wait_for_function('document.querySelectorAll(".version-card").length===37',timeout=20000)
        assert page.locator('iframe').count()==0
        assert page.locator('[data-version^="sample-"]').count()==7
        page.locator('[data-open="sample-solid-shoulder"]').last.click()
        page.wait_for_function('document.querySelector("iframe")?.contentWindow.originalSample?.getState().frames>3',timeout=20000)
        frame=page.frames[-1];state=frame.evaluate('originalSample.getState()');canvas=frame.locator('canvas');bounds=canvas.bounding_box();assert bounds
        samples=[];page.mouse.move(bounds['x']+bounds['width']*.6,bounds['y']+bounds['height']*.55);page.mouse.down()
        for i in range(8):
            page.mouse.move(bounds['x']+bounds['width']*(.6-i*.025),bounds['y']+bounds['height']*(.55+i*.01))
            page.wait_for_timeout(80);samples.append(frame.evaluate('originalSample.getState().camera'))
        page.mouse.up();assert len(set(tuple(round(n,5) for n in v) for v in samples))>=6
        png=frame.evaluate('originalSample.capture()');(out/'continuous-drag.png').write_bytes(base64.b64decode(png.split(',',1)[1]))
        result['continuousMovement']={'steps':8,'distinctCameraPositions':len(set(tuple(v) for v in samples)),'start':state['camera'],'end':samples[-1],'actualPixelCapture':'continuous-drag.png'}
        page.locator('#version-switch').select_option('sample-staggered-colony')
        page.wait_for_function('document.querySelector("iframe")?.contentWindow.originalSample?.metadata.id==="staggered-colony"',timeout=20000)
        page.locator('#return').click();assert page.locator('iframe').count()==0;assert not page.locator('#viewer').evaluate('(e)=>e.open')
        result['switchAndReturn']=True
        page.set_viewport_size({'width':390,'height':740});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        result['smallViewport']={'width':390,'height':740,'horizontalOverflow':False,'physicalPhone':False}
        assert not result['errors'];result['status']='PASS';print('PORTAL_RENDER_DRAG_SWITCH_RETURN_PASS',flush=True);browser.close()
except Exception as e:result.update(status='FAIL',error=str(e));raise
finally:
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
    if server:server.shutdown();server.server_close()
