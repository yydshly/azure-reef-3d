"""Native-input, real-time tour evidence. Does not call tick/request or inject time."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json,time,threading,functools,statistics,hashlib
root=Path(__file__).resolve().parent
output=root/'artifacts/continuous-motion';output.mkdir(parents=True,exist_ok=True)
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
report={'status':'RUNNING','errors':[],'failedRequests':[],'checks':{},'screenshots':[],'clockInjection':False,'navigationMutationByTest':False}
def save(): (output/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
save()
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,chromium_sandbox=True,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist'])
    context=browser.new_context(viewport={'width':1280,'height':820},device_scale_factor=1,record_video_dir=str(output/'video'),record_video_size={'width':1280,'height':820},has_touch=True)
    page=context.new_page()
    page.on('pageerror',lambda e:report['errors'].append(str(e)))
    page.on('requestfailed',lambda r:report['failedRequests'].append({'url':r.url,'failure':r.failure}))
    url='http://127.0.0.1:'+str(server.server_address[1])+'/artifacts/continuous-candidate/scan-exhibit.html'
    try:
        page.goto(url,wait_until='domcontentloaded',timeout=30000)
        page.wait_for_function("() => window.reefExhibit?.getState().ready && ['c4','assemblage','naturalRock','layeredRidges','ray','turtle'].every(k=>window.reefExhibit.getState()[k]?.status==='ready') && window.reefExhibit.coralMidground.getState().status==='ready'",timeout=90000)
        print('NATIVE_READY',flush=True)
        report['initial']=page.evaluate('() => ({state:window.reefExhibit.getState(),continuous:window.reefExhibit.explorationWorld.continuous.getState()})')
        # Passive after-render instrumentation, with no new render, tick or pose.
        page.evaluate('''() => {const e=window.reefExhibit,r=e.renderer,original=r.render;window.__nativeEvidence={frames:[],events:[],previous:performance.now()};for(const type of ['keydown','keyup','pointerdown','pointerup','click'])document.addEventListener(type,event=>{window.__nativeEvidence.events.push({type,trusted:event.isTrusted,key:event.code||null,target:event.target.id||null})},true);r.render=function(...args){const begin=performance.now();const value=original.apply(this,args),end=performance.now(),q=window.__nativeEvidence,s=e.getState();q.frames.push({wallMs:end,frameGapMs:end-q.previous,renderCpuMs:end-begin,elapsed:s.route.elapsed,mode:s.route.mode,position:s.camera,target:s.target,ambient:s.ambient.time,sequence:e.getRenderDemandState().sequence+1,triangles:this.info.render.triangles,draws:this.info.render.calls});q.previous=end;return value;};}''')
        state=lambda:page.evaluate('() => window.reefExhibit.getState()')
        def shot(name):
            page.locator('#scanStage').screenshot(path=str(output/(name+'.png')),timeout=20000)
            report['screenshots'].append({'name':name,'state':state()});save()
        wall_start=time.monotonic();page.locator('#startTour').click();next_shot=0
        milestones=[(10,'tour-near-moving'),(35,'tour-mid-moving'),(59,'tour-deep-moving')]
        while True:
            page.wait_for_timeout(700)
            s=state();elapsed=s['route']['elapsed']
            if next_shot<len(milestones) and elapsed>=milestones[next_shot][0]:
                shot(milestones[next_shot][1]);print('NATIVE_TOUR',elapsed,s['camera'],flush=True);next_shot+=1
            if s['route']['mode']=='completed':break
            assert time.monotonic()-wall_start<110,'Natural tour exceeded bounded wall time'
        wall_elapsed=time.monotonic()-wall_start
        assert s['route']['elapsed']==72 and wall_elapsed>=72
        report['checks']['native72SecondTour']={'passed':True,'wallSeconds':wall_elapsed,'finalState':s};shot('tour-completed')
        # Native replay and pause retain the reached pose and exclude paused time.
        page.locator('#startTour').click();page.wait_for_timeout(600);s=state();assert s['route']['mode']=='tour' and 0<s['route']['elapsed']<5
        page.locator('#pauseNavigation').click();a=state();page.wait_for_timeout(600);b=state();assert a['route']['elapsed']==b['route']['elapsed'] and a['camera']==b['camera']
        report['checks']['replayAndPause']={'passed':True,'elapsed':a['route']['elapsed']}
        page.locator('#pauseNavigation').click();page.wait_for_timeout(500);assert state()['route']['elapsed']>a['route']['elapsed']
        # Take control at the current pose, then turn completely using a held key.
        page.locator('#hudMoreSummary').click();before=state();page.locator('#exploreRoute').click();after=state();assert after['route']['mode']=='free'
        # Before click a running tour can advance; measure the sampled after pose.
        page.locator('#closeHudMore').click();canvas=page.locator('#scanCanvas');canvas.focus()
        a=state();page.keyboard.down('ArrowRight');page.wait_for_timeout(3100);page.keyboard.up('ArrowRight');b=state();assert a['camera']==b['camera'];assert abs(b['route']['yaw']-a['route']['yaw'])>2
        report['checks']['turnInPlace']={'passed':True,'before':a,'after':b};shot('turned-back')
        # Use native Home to return, then swim forward and backward in the entry.
        canvas.focus();page.keyboard.press('Home');a=state();assert a['camera']==[4,5,10]
        page.keyboard.down('w');page.wait_for_timeout(750);page.keyboard.up('w');b=state();assert b['camera'][2]<a['camera'][2]-1
        page.keyboard.down('s');page.wait_for_timeout(750);page.keyboard.up('s');c=state();assert c['camera'][2]>b['camera'][2]+1
        report['checks']['forwardReverseAndReturn']={'passed':True,'home':a['camera'],'forward':b['camera'],'reverse':c['camera']}
        # The conservative continuous mass proxy blocks a native strafe at its
        # near-left face; floor and bounds remain part of the original navigator.
        page.keyboard.press('Home');page.keyboard.down('w');page.wait_for_timeout(4300);page.keyboard.up('w');page.keyboard.down('a');page.wait_for_timeout(5500);page.keyboard.up('a');a=state();page.keyboard.down('a');page.wait_for_timeout(1200);page.keyboard.up('a');b=state()
        assert abs(a['camera'][0]-b['camera'][0])<.4,'Strafe must stop against visible left reef proxy'
        report['checks']['nearReefCollision']={'passed':True,'first':a['camera'],'second':b['camera'],'scope':'The first live near-reef obstacle encountered; new continuous mass proxies also have separate CPU checks.'};shot('reef-collision')
        page.keyboard.down('d');page.wait_for_timeout(800);page.keyboard.up('d');c=state();assert c['camera'][0]>b['camera'][0]+1
        report['checks']['escapeFromCollision']={'passed':True,'position':c['camera']}
        page.keyboard.press('Home');report['timeline']=page.evaluate('() => window.__nativeEvidence')
        assert all(e['trusted'] for e in report['timeline']['events'])
        tour_frames=[f for f in report['timeline']['frames'] if f['mode']=='tour' and .5<f['elapsed']<71]
        gaps=[f['frameGapMs'] for f in tour_frames if 0<f['frameGapMs']<2000]
        report['performance']={'nativeRenderedTourFrames':len(tour_frames),'medianFrameGapMs':statistics.median(gaps),'p95FrameGapMs':sorted(gaps)[int(len(gaps)*.95)],'medianRenderCpuMs':statistics.median(f['renderCpuMs'] for f in tour_frames),'recordingActive':True,'interpretation':'This one Intel UHD desktop during video capture; not a phone benchmark.'}
        # A narrow emulated touch context exercises the actual responsive buttons.
        narrow=browser.new_context(viewport={'width':390,'height':740},device_scale_factor=1,has_touch=True,is_mobile=True,reduced_motion='reduce')
        mobile=narrow.new_page();mobile.goto(url,wait_until='domcontentloaded',timeout=30000)
        mobile.wait_for_function('() => window.reefExhibit?.getState().ready',timeout=90000)
        mobile.locator('#swimForward').tap();a=mobile.evaluate('() => window.reefExhibit.getState()');assert a['route']['reduced'];assert a['camera'][2]<10
        mobile.locator('#hudMoreSummary').tap();mobile.locator('#resetExhibit').tap();mobile.locator('#closeHudMore').tap();b=mobile.evaluate('() => window.reefExhibit.getState()');assert b['camera']==[4,5,10]
        mobile.locator('#scanStage').screenshot(path=str(output/'mobile-390.png'),timeout=20000)
        report['checks']['emulatedTouchAndReducedMotion']={'passed':True,'viewport':[390,740],'tapMoved':a['camera'],'reset':b['camera'],'hardwareTouchTested':False};narrow.close()
        assert not report['errors'] and not report['failedRequests']
        report['status']='PASS'
    except Exception as e:
        report['status']='FAIL';report['failure']=repr(e);print('NATIVE_FAILURE',repr(e),flush=True)
        try:report['failureState']=page.evaluate('() => window.reefExhibit?.getState()');page.screenshot(path=str(output/'failure.png'),timeout=15000)
        except Exception:pass
    finally:
        if 'timeline' not in report:
            try:report['timeline']=page.evaluate('() => window.__nativeEvidence')
            except Exception:pass
        video=page.video;context.close();report['video']=str(Path(video.path()).relative_to(root));browser.close();save()
server.shutdown();server.server_close()
print(json.dumps({'status':report['status'],'checks':list(report['checks']),'performance':report.get('performance'),'failure':report.get('failure')}),flush=True)
if report['status']!='PASS':raise SystemExit(1)
