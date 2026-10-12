from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json,threading,functools,sys,hashlib,urllib.request
root=Path(__file__).resolve().parent;variant=sys.argv[1] if len(sys.argv)>1 else 'composition-candidate';output=root/'artifacts'/('views-'+variant);output.mkdir(parents=True,exist_ok=True)
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
report={'variant':variant,'errors':[],'failedRequests':[],'frames':[],'sourceHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (root/'artifacts'/variant).glob('*.js')}}
url='http://127.0.0.1:'+str(server.server_address[1])+'/artifacts/'+variant+'/scan-exhibit.html'
report['initialDocumentBytes']=len(urllib.request.urlopen(url,timeout=3).read());print('LOCAL_DOCUMENT_READ',report['initialDocumentBytes'],flush=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,chromium_sandbox=True,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist'])
 page=browser.new_page(viewport={'width':1280,'height':820},device_scale_factor=1);page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('requestfailed',lambda q:report['failedRequests'].append(q.url))
 page.goto(url,wait_until='commit',timeout=15000)
 page.wait_for_function("() => window.reefExhibit?.getState().ready && ['c4','assemblage','naturalRock','layeredRidges','ray','turtle'].every(k=>window.reefExhibit.getState()[k]?.status==='ready') && window.reefExhibit.coralMidground.getState().status==='ready'",timeout=90000)
 page.locator('#hudMoreSummary').click();page.locator('#pauseAmbient').click();page.locator('#closeHudMore').click()
 def shot(name):
  page.evaluate('() => window.reefExhibit.observeNextRender(()=>true)');page.locator('#scanStage').screenshot(path=str(output/(name+'.png')),timeout=20000)
  report['frames'].append({'name':name,'state':page.evaluate('() => window.reefExhibit.getState()')});print('FRAME',name,flush=True)
 def tour_pose(progress):
  page.locator('#startTour').click();page.locator('#pauseNavigation').click();page.locator('#hudMoreSummary').click();slider=page.locator('#routeProgress');slider.focus();slider.press('Home')
  for _ in range(progress):slider.press('ArrowRight')
  page.locator('#closeHudMore').click()
 def reverse(name):
  page.locator('#hudMoreSummary').click();page.locator('#exploreRoute').click();page.locator('#closeHudMore').click();page.locator('#scanCanvas').focus();page.keyboard.down('ArrowRight');page.wait_for_timeout(2860);page.keyboard.up('ArrowRight');shot(name)
 shot('entry');tour_pose(50);shot('mid');reverse('mid-reverse');tour_pose(100);shot('deep');reverse('deep-reverse');page.locator('#scanCanvas').focus();page.keyboard.press('Home');reverse('entry-reverse')
 report['budget']=page.evaluate('() => window.reefExhibit.explorationWorld.continuous.getState()');browser.close()
server.shutdown();server.server_close();(output/'fixed-views.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'variant':variant,'frames':len(report['frames']),'errors':report['errors'],'failedRequests':report['failedRequests']}),flush=True)
