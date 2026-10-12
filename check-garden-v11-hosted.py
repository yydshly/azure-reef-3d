from pathlib import Path
from playwright.sync_api import sync_playwright
import json,urllib.request,hashlib
root=Path(__file__).resolve().parent;out=root/'evidence/reef-garden-v11';base='https://yydshly.github.io/azure-reef-3d/';url=base+'preview/reef-garden-v1/';release=json.loads((root/'artifacts/garden-v11/release.json').read_text());local=json.loads((out/'verification.json').read_text(encoding='utf-8'));report={'url':url,'browser':'Existing Microsoft Edge, temporary task profile, sandbox enabled','errors':[],'failedRequests':[],'checks':{}}
for name,h in release['protectedPublicHashes'].items():assert hashlib.sha256(urllib.request.urlopen(base+name,timeout=20).read()).hexdigest()==h,name
report['checks']['protectedPublicBytes']={'passed':True,'hashes':release['protectedPublicHashes'],'worldPointerChanged':False}
for path,expected in [('preview/reef-garden-v1/',local['sourceHashes']),('preview/reef-garden-v1-first/',local['firstVersionHashes'])]:
 for name,h in expected.items():assert hashlib.sha256(urllib.request.urlopen(base+path+name,timeout=20).read()).hexdigest()==h,path+name
report['checks']['newAndFrozenPublicSourceBytes']={'passed':True,'current':local['sourceHashes'],'firstVersion':local['firstVersionHashes']}
with sync_playwright()as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',headless=True,chromium_sandbox=True,timeout=20000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist']);context=browser.new_context(viewport={'width':1280,'height':820},device_scale_factor=1);page=context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('requestfailed',lambda r:report['failedRequests'].append(r.url))
 try:
  args=context.new_cdp_session(page).send('Browser.getBrowserCommandLine')['arguments'];assert not any(a in args for a in ['--no-sandbox','--disable-gpu-sandbox','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']);response=page.goto(url,wait_until='commit',timeout=20000);assert response.status==200;page.wait_for_function('() => window.reefGarden?.getState().frames>2||window.reefGardenFailure',timeout=25000);assert not page.evaluate('() => window.reefGardenFailure');state=lambda:page.evaluate('() => window.reefGarden.getState()');report['initial']=state();assert state()['stats']['seaFans']==9
  page.screenshot(path=str(out/'live-entry.png'),timeout=10000);page.locator('#tour').click();page.wait_for_timeout(1200);assert state()['route']['elapsed']>.5;page.locator('#pause').click();a=state();page.wait_for_timeout(400);assert state()['camera']==a['camera']and state()['route']['elapsed']==a['route']['elapsed'];page.locator('#home').click();assert state()['camera']==[0,4.2,24];report['checks']['publicStartPauseHome']={'passed':True}
  links=[]
  for selector,path in [('#oldWorld','preview/world/'),('#realProbe','preview/real-splats-probe/'),('#firstGarden','preview/reef-garden-v1-first/')]:
   page.locator('#previous').click()
   with page.expect_popup(timeout=15000)as result:page.locator(selector).click()
   popup=result.value;popup.wait_for_load_state('domcontentloaded',timeout=20000)
   if selector=='#firstGarden':popup.wait_for_function('() => window.reefGarden?.getState().ready',timeout=25000);assert popup.evaluate('() => window.reefGarden.getState().stats.formations')==29
   else:popup.locator('h1').wait_for(state='visible',timeout=15000)
   assert popup.url==base+path,popup.url;links.append({'url':popup.url,'title':popup.title()});popup.close();assert not page.locator('#previousMenu').is_visible()
  report['checks']['publicMenuLinksNativeClicks']={'passed':True,'links':links,'scope':'Old entry UI and URL opened; original scan GPU completeness is not reaccepted.'}
  page.locator('[data-stop="5"]').click();page.wait_for_timeout(300);page.screenshot(path=str(out/'live-deep.png'),timeout=10000);report['deep']=state();page.locator('#free').click();page.locator('#sea').focus();page.keyboard.down('ArrowRight');page.wait_for_timeout(2860);page.keyboard.up('ArrowRight');page.screenshot(path=str(out/'live-deep-return.png'),timeout=10000);report['checks']['publicEndpointAndReverse']={'passed':True,'camera':state()['camera']}
  mobileContext=browser.new_context(viewport={'width':390,'height':740},has_touch=True,is_mobile=True,reduced_motion='reduce');mobile=mobileContext.new_page();mobile.goto(url,wait_until='commit',timeout=20000);mobile.wait_for_function('() => window.reefGarden?.getState().ready',timeout=25000);mobile.locator('#previous').tap();assert mobile.locator('#previousMenu').is_visible();menu=mobile.locator('#previousMenu').bounding_box();touch=mobile.locator('.touch-controls').bounding_box();assert menu['y']+menu['height']<touch['y'];mobile.screenshot(path=str(out/'live-mobile-menu.png'),timeout=10000);mobile.locator('#closePrevious').tap();assert not mobile.locator('#previousMenu').is_visible();mobile.locator('[data-key="KeyW"]').tap();assert mobile.evaluate('() => window.reefGarden.getState().camera[2]')<24;mobile.locator('#home').tap();assert mobile.evaluate('() => window.reefGarden.getState().camera')==[0,4.2,24];mobileContext.close();report['checks']['publicMobileMenuCloseThenSwim']={'passed':True,'physicalPhoneTested':False};assert not report['errors']and not report['failedRequests'];report['status']='PASS'
 except Exception as e:report['status']='FAIL';report['failure']=repr(e)
 finally:browser.close()
(out/'hosted-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':report['status'],'checks':list(report['checks']),'errors':report['errors'],'failure':report.get('failure')}),flush=True)
if report['status']!='PASS':raise SystemExit(1)
