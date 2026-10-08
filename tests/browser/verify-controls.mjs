import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';

// Missing-coverage continuation only. Does not change any product source/model.
const target=process.env.REEF_TARGET;
if(target!=='http://127.0.0.1:4173/')throw Error('Controls continuation requires isolated branch-preview');
const out=path.resolve('render-evidence');await fs.mkdir(out,{recursive:true});
const started=Date.now(),limitMs=240000;
const report={mode:'missing-controls',priorRun:'https://github.com/yydshly/azure-reef-3d/actions/runs/37719408252',checkoutCommit:process.env.GITHUB_SHA||null,startedAt:new Date().toISOString(),passed:false,checks:[],errors:[],limitations:['Controls/layout test uses reduced motion and deviceScaleFactor 0.5; not normal-motion or visual-quality/performance acceptance.','Prior desktop comparison cameras matched, but animated fish phases differed; other pixels were not held identical.','No recapture of the three completed desktop comparison pairs. Cyan material and irregular scan boundary remain visually unaccepted.','Native pointer clicks are preceded by DOM visibility, enabled-state, viewport and hit-target checks; Playwright frame-stability waits are not used. Free exploration is entered through the header guide toggle; the inner sticky guideExplore button remains unverified.']};
const save=async()=>{report.elapsedMs=Date.now()-started;await fs.writeFile(path.join(out,'controls.json'),JSON.stringify(report,null,2)+'\n');};
const sha=b=>createHash('sha256').update(b).digest('hex');
const expected={'app.js':'513bf445774f6893917943bf0bd8310170e3e38895c2e49768efc6f0f4f68636','model-version.js':'9bb2544b7d26ec235dd5d068e832711d391174005cb6c1077760cde324a2f975','reef-scan.js':'cebe9aa3f812ad0f0610340de55b22a9fe0e1d47809c37f182254593fdd03555','index.html':'3bfe541b30daf6c7841ae26bfdad70e0860884745b38b295be236f943081b50d','style.css':'a6d76cd3babf219df568ab7294f5489748ec07871d574a83a55b22ec3ccb0bc6','guide-data.js':'7ca273c4c3d93f2e2de9f062a30107488f08d0d210c2f78f4ad5ab515f2be1c9','assets/reefs4d/C12019-web.glb':'975228622829cb715ba9b48c0c5cc45c92e8b79d6689102cf188479318362502'};
let browser,context,page;
const watchdog=setTimeout(async()=>{report.errors.push('Controls-only 240-second wall-clock budget exhausted; remaining checks unknown');await save();process.exit(2);},limitMs);
const assert=(ok,message)=>{if(!ok)throw Error(message);};
const poseEqual=(a,b)=>['camera','target'].every(k=>a[k].every((v,i)=>Math.abs(v-b[k][i])<1e-6));
try{
 await save();
 browser=await chromium.launch({channel:'chromium',headless:true,chromiumSandbox:true,timeout:30000,args:['--enable-automation'],ignoreDefaultArgs:['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist']});
 const cdp=await browser.newBrowserCDPSession();const command=await cdp.send('Browser.getBrowserCommandLine');
 report.forbiddenFlags=command.arguments.filter(x=>['--no-sandbox','--disable-gpu-sandbox','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'].includes(x));assert(report.forbiddenFlags.length===0,'Unexpected weakened graphics/security flag');
 context=await browser.newContext({viewport:{width:800,height:700},deviceScaleFactor:.5,reducedMotion:'reduce'});
 report.context={viewport:[800,700],deviceScaleFactor:.5,reducedMotion:'reduce',lowQualityMode:false};
 report.sourceHashes={};
 for(const [file,hash] of Object.entries(expected)){
  assert(sha(await fs.readFile(path.join('dist',file)))===hash,'Frozen checkout changed: '+file);
  const response=await context.request.get(new URL(file,target).href,{timeout:10000});assert(response.ok(),'Source request failed: '+file);
  const served=sha(await response.body());assert(served===hash,'Served candidate changed: '+file);report.sourceHashes[file]=served;
 }
 await save();
 page=await context.newPage();page.setDefaultTimeout(8000);page.on('pageerror',e=>report.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text());});page.on('requestfailed',r=>report.errors.push('Request failed: '+r.url()));page.on('response',r=>{if(r.status()>=400)report.errors.push('HTTP '+r.status()+': '+r.url());});
 await page.goto(target,{waitUntil:'domcontentloaded',timeout:20000});
 await page.waitForFunction(()=>window.reef3d?.getState().scan?.state==='ready'||!document.querySelector('#unsupported').hidden,null,{timeout:65000,polling:500});
 assert(!(await page.locator('#unsupported').isVisible()),'WebGL app did not initialize');
 const state=()=>page.evaluate(()=>window.reef3d.getState());
 // A slow software renderer can stall Playwright's frame-based stability gate.
 // Do not infer invisibility from that combined gate. Save actual DOM evidence.
 report.clickEvidence=[];
 const inspectControl=async(id,scroll=false)=>page.evaluate(({id,scroll})=>{
  const el=document.querySelector(id);if(!el)return {id,exists:false};
  if(scroll)el.scrollIntoView({block:'nearest',inline:'nearest',behavior:'instant'});
  const css=getComputedStyle(el),r=el.getBoundingClientRect();
  const left=Math.max(0,r.left),right=Math.min(innerWidth,r.right),top=Math.max(0,r.top),bottom=Math.min(innerHeight,r.bottom);
  const point={x:(left+right)/2,y:(top+bottom)/2},hit=right>left&&bottom>top?document.elementFromPoint(point.x,point.y):null;
  const hiddenAncestors=[];for(let a=el;a;a=a.parentElement){const c=getComputedStyle(a);if(a.hidden||c.display==='none'||c.visibility==='hidden')hiddenAncestors.push(a.id||a.tagName);}
  return {id,exists:true,hidden:el.hidden,disabled:!!el.disabled,display:css.display,visibility:css.visibility,opacity:css.opacity,pointerEvents:css.pointerEvents,rect:{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom},point,hit:hit?{id:hit.id,tag:hit.tagName}:null,hitMatches:!!hit&&(hit===el||el.contains(hit)),hiddenAncestors,inViewport:right>left&&bottom>top};
 },{id,scroll});
 const click=async(id)=>{
  const evidence=await inspectControl(id,true);report.clickEvidence.push({elapsedMs:Date.now()-started,...evidence});await save();
  assert(evidence.exists&&!evidence.hidden&&!evidence.disabled&&evidence.hiddenAncestors.length===0&&evidence.visibility==='visible'&&Number(evidence.opacity)>0&&evidence.inViewport&&evidence.hitMatches,'Native control is not visibly actionable: '+id+'; see clickEvidence');
  await page.mouse.click(evidence.point.x,evidence.point.y);
 };
 const checkpoint=async(name,details={})=>{report.checks.push({name,passed:true,elapsedMs:Date.now()-started,...details});await save();};
 const initial=await state();assert(initial.ready&&initial.scan.state==='ready'&&initial.fish===6,'Expected frozen scene, scan and six fish');
 report.startupControls={guideExplore:await inspectControl('#guideExplore'),guideEntry:await inspectControl('#guideEntry'),guideCardHidden:await page.locator('#guideCard').getAttribute('hidden')};
 await checkpoint('loaded-frozen-runtime',{state:initial});
 await click('#guideEntry');assert(!(await state()).guide.active,'Header guide toggle did not enter free exploration');await click('#scanCandidate');const before=await state();
 await click('#scanFocus');const focused=await state();assert(focused.scan.inspection,'Desktop scan focus failed');
 await click('#scanReturn');const returned=await state();assert(!returned.scan.inspection&&poseEqual(before,returned),'Desktop scan return failed');
 await checkpoint('desktop-scan-focus-return',{before,focused,returned});
 await click('#scanFocus');await page.keyboard.press('Escape');const escaped=await state();assert(!escaped.scan.inspection&&poseEqual(before,escaped),'Repeated focus/Escape return failed');
 await checkpoint('desktop-repeat-focus-escape',{state:escaped});
 await click('#guideEntry');
 for(let i=0;i<5;i++){
  await click(`[data-guide="${i}"]`);const s=await state();assert(s.guide.active&&s.guide.index===i,'Guide step selection failed: '+i);
  await checkpoint('guide-stop-'+i,{state:s,title:await page.locator('#guideTitle').innerText()});
  if(i===2){
   await click('#scanCandidate');const prior=await state();await click('#specimenInspect');const inner=await state();assert(inner.specimenInspection,'Skeleton focus failed');
   await click('#specimenReturn');const after=await state();assert(!after.specimenInspection&&poseEqual(prior,after),'Skeleton return failed');await checkpoint('skeleton-focus-return',{before:prior,focused:inner,returned:after});
  }
 }
 await click('#guideEntry');assert(!(await state()).guide.active,'Header free exploration toggle failed');await checkpoint('guide-free-exploration',{method:'Visible header guide toggle; inner sticky button not exercised'});
 await page.setViewportSize({width:390,height:844});
 const layout=async()=>{
  const x=await page.evaluate(()=>{const rect=selector=>{const e=document.querySelector(selector);if(!e||e.hidden||getComputedStyle(e).display==='none')return null;const r=e.getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height};};return {viewport:[innerWidth,innerHeight],panel:rect('#scanPanel'),guide:rect('#guideCard'),footer:rect('footer'),buttons:['#scanBaseline','#scanCandidate','#scanFocus','#scanReturn'].map(id=>({id,rect:rect(id)})).filter(x=>x.rect)};});
  const p=x.panel;assert(p&&p.x>=0&&p.y>=0&&p.right<=390&&p.bottom<=844,'Mobile scan panel outside viewport');
  const overlap=(a,b)=>b&&Math.min(a.right,b.right)>Math.max(a.x,b.x)&&Math.min(a.bottom,b.bottom)>Math.max(a.y,b.y);
  assert(!overlap(p,x.guide)&&!overlap(p,x.footer),'Mobile panel overlaps guide or footer');
  for(const b of x.buttons)assert(b.rect.width>=40&&b.rect.height>=30,'Mobile button too small: '+b.id);return x;
 };
 const freeLayout=await layout();await click('#scanBaseline');const mobileBefore=await state();await click('#scanCandidate');const mobileAfter=await state();assert(!mobileBefore.scan.visible&&mobileAfter.scan.visible&&poseEqual(mobileBefore,mobileAfter),'Mobile comparison failed');
 await checkpoint('mobile-native-comparison',{layout:freeLayout,before:mobileBefore,after:mobileAfter});
 await click('#guideEntry');await click('[data-guide="0"]');await click('#scanCandidate');const guideLayout=await layout();await checkpoint('mobile-guide-layout',{layout:guideLayout});
 const mBefore=await state();await click('#scanFocus');const mFocus=await state();assert(mFocus.scan.inspection,'Mobile focus failed');const focusLayout=await layout();await click('#scanReturn');const mReturned=await state();assert(!mReturned.scan.inspection&&mReturned.guide.active&&poseEqual(mBefore,mReturned),'Mobile return failed');
 await checkpoint('mobile-focus-return',{layout:focusLayout,before:mBefore,focused:mFocus,returned:mReturned});
 report.contextLost=await page.evaluate(()=>document.querySelector('#reef').getContext('webgl2').isContextLost());assert(!report.contextLost,'WebGL context lost');
 report.controlsComplete=true;report.passed=report.errors.length===0;await save();
 // One optional layout image, strictly capped; no repeated expensive desktop renders.
 if(limitMs-(Date.now()-started)>25000){try{await page.screenshot({path:path.join(out,'mobile-controls-only.png'),timeout:12000,animations:'disabled'});report.mobileScreenshot='mobile-controls-only.png';}catch(e){report.screenshotWarning=String(e);}}
 else report.screenshotWarning='Skipped optional image to preserve wall-clock bound';
 await save();if(!report.passed)process.exitCode=1;
}catch(e){report.errors.push(String(e?.stack||e));report.passed=false;process.exitCode=1;await save();}
finally{clearTimeout(watchdog);await save();await context?.close().catch(()=>{});await browser?.close().catch(()=>{});}
