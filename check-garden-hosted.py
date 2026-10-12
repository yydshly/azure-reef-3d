from pathlib import Path
from playwright.sync_api import sync_playwright
import json,urllib.request,hashlib,time
root=Path(__file__).resolve().parent;out=root/'artifacts/garden-hosted';out.mkdir(parents=True,exist_ok=True);release=json.loads((root/'artifacts/garden-release.json').read_text());base='https://yydshly.github.io/azure-reef-3d/';url=base+'preview/reef-garden-v1/';report={'url':url,'errors':[],'failedRequests':[],'checks':{}}
for name,expected in release['protectedPublicHashes'].items():
 actual=hashlib.sha256(urllib.request.urlopen(base+name,timeout=15).read()).hexdigest();assert actual==expected,'Old published file changed '+name
report['checks']['protectedOldPublicBytes']={'passed':True,'files':release['protectedPublicHashes'],'worldPointerChanged':False}
local=root/'dist/preview/reef-garden-v1';served={}
for p in local.iterdir():
 if p.is_file():
  body=urllib.request.urlopen(url+p.name,timeout=15).read();actual=hashlib.sha256(body).hexdigest();assert actual==hashlib.sha256(p.read_bytes()).hexdigest(),'Served preview mismatch '+p.name;served[p.name]=actual
report['checks']['servedSourceHashes']={'passed':True,'hashes':served}
with sync_playwright()as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,chromium_sandbox=True,timeout=20000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist']);page=browser.new_page(viewport={'width':1280,'height':820},device_scale_factor=1);page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('requestfailed',lambda r:report['failedRequests'].append(r.url))
 try:
  cdp=page.context.new_cdp_session(page);cdp.send('Browser.getBrowserCommandLine');report['initialBlank']=page.evaluate('() => ({url:location.href,ready:document.readyState})');r=page.request.get(url,timeout=10000);assert r.status==200;r.dispose();page.goto(url,wait_until='commit',timeout=20000);page.wait_for_function('() => window.reefGarden?.getState().ready || window.reefGardenFailure',timeout=25000);assert not page.evaluate('() => window.reefGardenFailure');report['initial']=page.evaluate('() => window.reefGarden.getState()');page.screenshot(path=str(out/'live-entry.png'),timeout=10000)
  page.locator('#tour').click();page.wait_for_timeout(1200);a=page.evaluate('() => window.reefGarden.getState()');assert a['route']['mode']=='tour'and a['route']['elapsed']>.5;page.locator('#pause').click();a=page.evaluate('() => window.reefGarden.getState()');page.wait_for_timeout(400);b=page.evaluate('() => window.reefGarden.getState()');assert a['camera']==b['camera']and a['route']['elapsed']==b['route']['elapsed'];page.locator('#home').click();assert page.evaluate('() => window.reefGarden.getState().camera')==[0,4.2,24];report['checks']['hostedStartPauseReturn']={'passed':True};assert not report['errors']and not report['failedRequests'];report['status']='PASS'
 except Exception as e:report['status']='FAIL';report['failure']=repr(e)
 finally:browser.close()
(out/'hosted.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':report['status'],'url':url,'checks':list(report['checks']),'errors':report['errors'],'failure':report.get('failure')}),flush=True)
if report['status']!='PASS':raise SystemExit(1)
