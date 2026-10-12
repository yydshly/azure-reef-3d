from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json,threading,functools
root=Path(__file__).resolve().parent;output=root/'artifacts/composition-inspection';output.mkdir(parents=True,exist_ok=True)
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
report={'errors':[],'frames':[],'purpose':'Matched pixel inspection of b92b8ac surface boundary and natural reverse view; no clock injection.'}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,chromium_sandbox=True,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist'])
 page=browser.new_page(viewport={'width':1280,'height':820},device_scale_factor=1);page.on('pageerror',lambda e:report['errors'].append(str(e)))
 page.goto('http://127.0.0.1:'+str(server.server_address[1])+'/artifacts/continuous-candidate/scan-exhibit.html',wait_until='domcontentloaded',timeout=30000)
 page.wait_for_function("() => window.reefExhibit?.getState().ready && window.reefExhibit.getState().assemblage.status==='ready'",timeout=90000)
 page.locator('#hudMoreSummary').click();page.locator('#pauseAmbient').click();page.locator('#closeHudMore').click();page.locator('#startTour').click();page.locator('#pauseNavigation').click()
 page.locator('#hudMoreSummary').click();slider=page.locator('#routeProgress');slider.focus();slider.press('Home')
 for _ in range(50):slider.press('ArrowRight')
 page.locator('#closeHudMore').click()
 def shot(name):
  page.locator('#scanStage').screenshot(path=str(output/(name+'.png')),timeout=20000);report['frames'].append({'name':name,'state':page.evaluate('() => window.reefExhibit.getState()')});print('FRAME',name,flush=True)
 shot('mid-original')
 page.evaluate("async() => {const e=window.reefExhibit;e.ocean.group.getObjectByName('Synthetic_Overhead_Surface').visible=false;return e.observeNextRender(()=>true)}")
 shot('mid-without-alpha-surface')
 # Inspect an actual reverse heading via a native held turning key.
 page.locator('#hudMoreSummary').click();page.locator('#exploreRoute').click();page.locator('#closeHudMore').click();page.locator('#scanCanvas').focus();page.keyboard.down('ArrowRight');page.wait_for_timeout(2860);page.keyboard.up('ArrowRight');shot('mid-reverse-without-alpha-surface')
 page.keyboard.press('Home');page.keyboard.down('ArrowRight');page.wait_for_timeout(2860);page.keyboard.up('ArrowRight');shot('entry-reverse-without-alpha-surface')
 browser.close()
server.shutdown();server.server_close();(output/'inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'errors':report['errors'],'frames':len(report['frames'])}),flush=True)
