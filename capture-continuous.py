from pathlib import Path
from playwright.sync_api import sync_playwright
import json, sys, time
import threading, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
root=Path(__file__).resolve().parent
variant=sys.argv[1] if len(sys.argv)>1 else 'enriched-baseline'
output=root/'artifacts'/('render-'+variant);output.mkdir(parents=True,exist_ok=True)
report={'variant':variant,'errors':[],'failedRequests':[],'frames':[],'sourceHashes':{p.name:__import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in (root/'artifacts'/variant).glob('*.js')}}
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,chromium_sandbox=True,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist'])
    page=browser.new_page(viewport={'width':1280,'height':820},device_scale_factor=1)
    page.on('pageerror',lambda error:report['errors'].append(str(error)))
    page.on('requestfailed',lambda req:report['failedRequests'].append({'url':req.url,'failure':req.failure}))
    page.goto('http://127.0.0.1:'+str(server.server_address[1])+'/artifacts/'+variant+'/scan-exhibit.html',wait_until='domcontentloaded',timeout=30000)
    page.wait_for_function("() => window.reefExhibit?.getState().ready && ['c4','assemblage','naturalRock','layeredRidges','ray','turtle'].every(k=>window.reefExhibit.getState()[k]?.status==='ready') && window.reefExhibit.coralMidground.getState().status==='ready'",timeout=90000)
    print('READY',variant,flush=True)
    page.locator('#hudMoreSummary').click()
    page.locator('#pauseAmbient').click()
    page.locator('#closeHudMore').click()
    report['driver']=page.evaluate("() => {const g=document.querySelector('canvas').getContext('webgl2'),e=g.getExtension('WEBGL_debug_renderer_info');return g.getParameter(e.UNMASKED_RENDERER_WEBGL)}")
    for label,progress in [('entry',None),('mid',50),('deep',100)]:
        if progress is not None:
            if progress==50:
                page.locator('#startTour').click()
                page.locator('#pauseNavigation').click()
            page.locator('#hudMoreSummary').click()
            slider=page.locator('#routeProgress');slider.focus();slider.press('Home')
            for _ in range(progress):slider.press('ArrowRight')
            page.locator('#closeHudMore').click()
        page.wait_for_timeout(350)
        file=output/(label+'.png');page.locator('#scanStage').screenshot(path=str(file),timeout=20000)
        state=page.evaluate('() => window.reefExhibit.getState()');report['frames'].append({'label':label,'file':file.name,'state':state})
        print('FRAME',label,state['camera'],flush=True)
    (output/'fixed-views.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    browser.close()
server.shutdown();server.server_close()
print(json.dumps({'variant':variant,'errors':report['errors'],'failedRequests':report['failedRequests'],'frames':len(report['frames'])}),flush=True)
