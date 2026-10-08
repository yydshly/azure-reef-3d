import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';

// Candidate 2 only. Four desktop frames; bounded small-mobile checks.
const target=process.env.REEF_TARGET;
if(target!=='http://127.0.0.1:4173/')throw Error('Refinement QA requires isolated branch preview');
const out=path.resolve('render-evidence');await fs.mkdir(out,{recursive:true});
const started=Date.now(),limitMs=320000;
const report={mode:'scan-refinement',candidate:2,checkoutCommit:process.env.GITHUB_SHA||null,startedAt:new Date().toISOString(),passed:false,checks:[],captures:[],errors:[],warnings:[],limitations:['Four bounded fixed-camera frames, reduced-motion enabled to hold fish/water simulation phase constant. Not normal-motion, user-device or performance acceptance.','Device scale factor 1, default quality/shadows unchanged. Software-WebGL visual review is required separately from successful screenshots.','Raw mode removes only display chroma reduction; source photographs retain baked underwater lighting and both modes use synthetic world light/water.','Contact audit covers sampled boundary vertices, not continuous proof. Interior scan holes are not repaired.','Prior full native controls belong to candidate 1 run 37721951538; this run covers changed display/toggle/layout only.']};
const save=async()=>{report.elapsedMs=Date.now()-started;await fs.writeFile(path.join(out,'refinement.json'),JSON.stringify(report,null,2)+'\n');};
const sha=b=>createHash('sha256').update(b).digest('hex');
const expected={
  "app.js": "f68ccefa19aef5e43f5fb2253326049e5ddb488f377cda1d78511fa297b8e3e6",
  "reef-scan.js": "cd0dd7069a0797a1af72a4da117d961857bb5aff10708891025919a10cbe60ee",
  "index.html": "e0e386bfabf321df751482ade4823d5a170f973a9b26a065040c9e620622b8ac",
  "style.css": "22177bdd7dc46a8499ed1b51e4d0a95a5fca945d85b8b33b8df7027e1c709f89",
  "model-version.js": "9bb2544b7d26ec235dd5d068e832711d391174005cb6c1077760cde324a2f975",
  "guide-data.js": "7ca273c4c3d93f2e2de9f062a30107488f08d0d210c2f78f4ad5ab515f2be1c9",
  "assets/reefs4d/C12019-web.glb": "975228622829cb715ba9b48c0c5cc45c92e8b79d6689102cf188479318362502"
};
const assert=(ok,message)=>{if(!ok)throw Error(message);};
const poseEqual=(a,b)=>['camera','target'].every(k=>a[k].every((v,i)=>Math.abs(v-b[k][i])<1e-6));
let browser,context,page;
const watchdog=setTimeout(async()=>{report.errors.push('320-second wall-clock budget exhausted; uncompleted checks unknown');await save();process.exit(2);},limitMs);
try{
 await save();
 browser=await chromium.launch({channel:'chromium',headless:true,chromiumSandbox:true,timeout:30000,args:['--enable-automation'],ignoreDefaultArgs:['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist']});
 const cdp=await browser.newBrowserCDPSession();const command=await cdp.send('Browser.getBrowserCommandLine');
 report.forbiddenFlags=command.arguments.filter(x=>['--no-sandbox','--disable-gpu-sandbox','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'].includes(x));assert(report.forbiddenFlags.length===0,'Unexpected weakened graphics/security flag');
 context=await browser.newContext({viewport:{width:1120,height:700},deviceScaleFactor:1,reducedMotion:'reduce'});
 report.context={viewport:[1120,700],deviceScaleFactor:1,reducedMotion:'reduce',lowQualityMode:false};report.sourceHashes={};
 for(const [file,hash] of Object.entries(expected)){
  assert(sha(await fs.readFile(path.join('dist',file)))===hash,'Candidate checkout hash mismatch: '+file);
  const response=await context.request.get(new URL(file,target).href,{timeout:10000});assert(response.ok(),'Source request failed: '+file);
  const served=sha(await response.body());assert(served===hash,'Served candidate hash mismatch: '+file);report.sourceHashes[file]=served;
 }
 await save();page=await context.newPage();page.setDefaultTimeout(8000);
 page.on('pageerror',e=>report.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text());});page.on('requestfailed',r=>report.errors.push('Request failed: '+r.url()));page.on('response',r=>{if(r.status()>=400)report.errors.push('HTTP '+r.status()+': '+r.url());});
 await page.goto(target,{waitUntil:'domcontentloaded',timeout:20000});
 await page.waitForFunction(()=>window.reef3d?.getState().scan?.state==='ready'||!document.querySelector('#unsupported').hidden,null,{timeout:65000,polling:500});
 assert(!(await page.locator('#unsupported').isVisible()),'WebGL app did not initialize');
 const state=()=>page.evaluate(()=>window.reef3d.getState());
 const checkpoint=async(name,details={})=>{report.checks.push({name,passed:true,elapsedMs:Date.now()-started,...details});await save();};
 report.clickEvidence=[];
 const inspect=async(id)=>page.evaluate(id=>{
  const el=document.querySelector(id);if(!el)return {id,exists:false};const css=getComputedStyle(el),r=el.getBoundingClientRect();const left=Math.max(0,r.left),right=Math.min(innerWidth,r.right),top=Math.max(0,r.top),bottom=Math.min(innerHeight,r.bottom);const point={x:(left+right)/2,y:(top+bottom)/2};const hit=right>left&&bottom>top?document.elementFromPoint(point.x,point.y):null;
  const hiddenAncestors=[];for(let a=el;a;a=a.parentElement){const c=getComputedStyle(a);if(a.hidden||c.display==='none'||c.visibility==='hidden')hiddenAncestors.push(a.id||a.tagName);}
  return {id,exists:true,hidden:el.hidden,disabled:!!el.disabled,visibility:css.visibility,opacity:css.opacity,rect:{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom},point,hit:hit?{id:hit.id,tag:hit.tagName}:null,hitMatches:!!hit&&(hit===el||el.contains(hit)),hiddenAncestors,inViewport:right>left&&bottom>top};
 },id);
 const click=async(id)=>{const evidence=await inspect(id);report.clickEvidence.push({elapsedMs:Date.now()-started,...evidence});await save();assert(evidence.exists&&!evidence.hidden&&!evidence.disabled&&!evidence.hiddenAncestors.length&&evidence.visibility==='visible'&&Number(evidence.opacity)>0&&evidence.inViewport&&evidence.hitMatches,'Native control not actionable: '+id);await page.mouse.click(evidence.point.x,evidence.point.y);};
 const display=()=>page.evaluate(()=>{const g=window.reef3d.scene.getObjectByName('Reefs4D_C12019'),materials=[];g.traverse(o=>{if(o.isMesh)for(const m of Array.isArray(o.material)?o.material:[o.material])materials.push({amount:m.userData.scanDisplayAmount?.value,mapUUID:m.map?.uuid,geometryUUID:o.geometry.uuid});});return {position:g.position.toArray(),raw:g.userData.rawTextureDisplay,materials};});
 const nextFrame=async()=>{await page.evaluate(()=>new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Timed out awaiting two rendered frames')),20000);requestAnimationFrame(()=>requestAnimationFrame(()=>{clearTimeout(timer);resolve(true);}));}));};
 const capture=async(file)=>{const before=await state();await save();try{await nextFrame();await page.screenshot({path:path.join(out,file),timeout:22000,animations:'disabled'});const after=await state();assert(poseEqual(before,after),'Camera changed during capture');assert(before.simulationTime===after.simulationTime,'Simulation phase changed during reduced-motion capture');const entry={file,sha256:sha(await fs.readFile(path.join(out,file))),before,after,display:await display()};report.captures.push(entry);await save();return entry;}catch(e){report.errors.push('Capture '+file+': '+String(e));await save();return null;}};
 const initial=await state();assert(initial.ready&&initial.fish===6&&!initial.low&&!initial.scan.rawTexture,'Expected default softened scan and six fish');await checkpoint('candidate2-initialized',{state:initial,display:await display()});
 if(initial.guide.active)await click('#guideEntry');await click('#scanFocus');const focus=await state();assert(focus.scan.inspection,'Native focus failed');
 await capture('candidate2-focus-soft.png');
 const beforeRaw=await state(),beforeDisplay=await display();await click('#scanRaw');const raw=await state(),rawDisplay=await display();assert(raw.scan.rawTexture&&poseEqual(beforeRaw,raw),'Raw toggle changed camera or did not enable');assert(rawDisplay.materials.every(m=>m.amount===0),'Raw shader uniform not zero');assert(beforeDisplay.materials.every((m,i)=>m.mapUUID===rawDisplay.materials[i].mapUUID&&m.geometryUUID===rawDisplay.materials[i].geometryUUID),'Toggle replaced original map or geometry');await checkpoint('focus-native-raw-toggle',{before:beforeRaw,after:raw,display:rawDisplay});
 await capture('candidate2-focus-raw.png');
 await click('#scanRaw');assert((await display()).materials.every(m=>m.amount===.3),'Softened uniform did not restore');await click('#scanReturn');await click('#reset');const ordinary=await state();assert(!ordinary.scan.inspection&&!ordinary.scan.rawTexture,'Ordinary softened state not restored');
 await capture('candidate2-ordinary-soft.png');
 await click('#scanRaw');const ordinaryRaw=await state();assert(ordinaryRaw.scan.rawTexture&&poseEqual(ordinary,ordinaryRaw),'Ordinary raw toggle failed');await capture('candidate2-ordinary-raw.png');await checkpoint('ordinary-native-raw-toggle',{before:ordinary,after:ordinaryRaw});
 // Check new toggle dimensions/hit target and panel overlap; screenshot only with spare budget.
 await page.setViewportSize({width:390,height:844});
 const layout=async()=>page.evaluate(()=>{const rect=s=>{const e=document.querySelector(s);if(!e||e.hidden||getComputedStyle(e).display==='none')return null;const r=e.getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height};};return {panel:rect('#scanPanel'),guide:rect('#guideCard'),footer:rect('footer'),label:rect('.view-label'),raw:rect('#scanRaw')};});
 const validateLayout=x=>{const p=x.panel,overlap=(a,b)=>b&&Math.min(a.right,b.right)>Math.max(a.x,b.x)&&Math.min(a.bottom,b.bottom)>Math.max(a.y,b.y);assert(p&&p.x>=0&&p.y>=0&&p.right<=390&&p.bottom<=844,'Mobile panel outside viewport');assert(!overlap(p,x.guide)&&!overlap(p,x.footer),'Mobile panel overlaps guide/footer');assert(x.raw?.width>=44&&x.raw?.height>=30,'Mobile raw toggle too small');};
 const freeLayout=await layout();validateLayout(freeLayout);const mobileBefore=await state();await click('#scanRaw');const mobileAfter=await state();assert(!mobileAfter.scan.rawTexture&&poseEqual(mobileBefore,mobileAfter),'Mobile native raw toggle failed');await checkpoint('mobile-free-panel-and-toggle',{layout:freeLayout,before:mobileBefore,after:mobileAfter});
 await click('#scanBaseline');assert((await inspect('#scanRaw')).disabled,'Raw toggle must disable while scan hidden');await click('#scanCandidate');await click('#guideEntry');const guideLayout=await layout();validateLayout(guideLayout);await checkpoint('mobile-guided-panel',{layout:guideLayout});
 const mobileInfo=await page.evaluate(()=>{const gl=document.querySelector('#reef').getContext('webgl2');return {contextLost:gl.isContextLost(),canvas:[gl.drawingBufferWidth,gl.drawingBufferHeight]};});assert(!mobileInfo.contextLost,'WebGL context lost');report.mobileWebGL=mobileInfo;
 if(limitMs-(Date.now()-started)>35000)await capture('candidate2-mobile-panel.png');else report.warnings.push('Optional mobile screenshot skipped to preserve wall-clock bound; DOM/hit-target checks recorded.');
 assert(report.captures.filter(c=>!c.file.includes('mobile')).length===4,'Missing required desktop comparison frame(s)');
 for(const prefix of ['focus','ordinary']){const a=report.captures.find(c=>c.file===`candidate2-${prefix}-soft.png`),b=report.captures.find(c=>c.file===`candidate2-${prefix}-raw.png`);assert(poseEqual(a.after,b.after)&&a.after.simulationTime===b.after.simulationTime,'Comparison pose/phase not matched: '+prefix);}
 report.passed=report.errors.length===0;await save();if(!report.passed)process.exitCode=1;
}catch(e){report.errors.push(String(e?.stack||e));report.passed=false;process.exitCode=1;await save();}
finally{clearTimeout(watchdog);await save();await context?.close().catch(()=>{});await browser?.close().catch(()=>{});}
