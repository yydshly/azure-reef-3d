import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';

const mode=process.argv[2]||'probe';
if(!['probe','render'].includes(mode))throw Error('Expected probe or render');
const out=path.resolve('render-evidence',process.env.REEF_ARM||'probe');await fs.mkdir(out,{recursive:true});
const target=process.env.REEF_TARGET||'https://yydshly.github.io/azure-reef-3d/';
if(!['https://yydshly.github.io/azure-reef-3d/','http://127.0.0.1:4173/dist/','http://127.0.0.1:4173/research/skeletal/dist/'].includes(target))throw Error('Unapproved test target');
const viewSet=process.env.REEF_VIEW_SET||'passage';
const sha=b=>createHash('sha256').update(b).digest('hex');
const report={mode,target,viewSet,checkedAt:new Date().toISOString(),checkoutCommit:process.env.GITHUB_SHA||null,
  sandbox:true,unsafeGraphicsFlags:false,limitations:['Hosted runner rendering is not user-device performance or physical GPU acceptance.','Screenshots require human visual review; successful rendering alone is not realism acceptance.']};
let browser,context,page;
const save=()=>fs.writeFile(path.join(out,`${mode}.json`),JSON.stringify(report,null,2)+'\n');
async function capability(p){return p.evaluate(()=>{
  const c=document.createElement('canvas');c.width=16;c.height=16;
  const gl=c.getContext('webgl2');if(!gl)return {available:false,reason:'getContext(webgl2) returned null'};
  const debug=gl.getExtension('WEBGL_debug_renderer_info');gl.clearColor(.2,.4,.6,1);gl.clear(gl.COLOR_BUFFER_BIT);gl.finish();
  const pixel=new Uint8Array(4);gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,pixel);
  const result={available:true,version:gl.getParameter(gl.VERSION),shadingLanguage:gl.getParameter(gl.SHADING_LANGUAGE_VERSION),vendor:gl.getParameter(gl.VENDOR),renderer:gl.getParameter(gl.RENDERER),unmaskedVendor:debug?gl.getParameter(debug.UNMASKED_VENDOR_WEBGL):null,unmaskedRenderer:debug?gl.getParameter(debug.UNMASKED_RENDERER_WEBGL):null,pixel:Array.from(pixel),error:gl.getError()};
  gl.getExtension('WEBGL_lose_context')?.loseContext();return result;
});}
try{
  browser=await chromium.launch({channel:'chromium',headless:true,chromiumSandbox:true,timeout:45000,args:['--enable-automation'],
    ignoreDefaultArgs:['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist']});
  report.browserVersion=browser.version();
  const cdp=await browser.newBrowserCDPSession();
  const command=await cdp.send('Browser.getBrowserCommandLine');
  report.securityFlags={sandboxDisabled:command.arguments.includes('--no-sandbox'),gpuSandboxDisabled:command.arguments.includes('--disable-gpu-sandbox'),unsafeSwiftshader:command.arguments.includes('--enable-unsafe-swiftshader'),gpuBlocklistIgnored:command.arguments.includes('--ignore-gpu-blocklist')};
  if(Object.values(report.securityFlags).some(Boolean))throw Error('Unexpected security-weakening browser flag');
  context=await browser.newContext({viewport:process.env.REEF_MOBILE==='true'?{width:390,height:844}:{width:1120,height:700},deviceScaleFactor:1,reducedMotion:'reduce',...(mode==='render'&&process.env.RECORD_VIDEO==='true'?{recordVideo:{dir:path.join(out,'video'),size:{width:1120,height:700}}}:{})});
  page=await context.newPage();page.setDefaultTimeout(30000);
  report.webgl2=await capability(page);report.webgl2.softwareRenderer=/swiftshader|llvmpipe|software/i.test(report.webgl2.unmaskedRenderer||report.webgl2.renderer||'');
  console.log('WEBGL2_PROBE',JSON.stringify(report.webgl2));await save();
  if(mode==='probe'){
    if(process.env.GITHUB_OUTPUT)await fs.appendFile(process.env.GITHUB_OUTPUT,`available=${report.webgl2.available}\n`);
  }else{
    if(!report.webgl2.available)throw Error('WebGL2 unavailable; rendering not attempted');
    report.consoleErrors=[];report.pageErrors=[];report.failedRequests=[];report.httpErrors=[];
    page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push(m.text());});
    page.on('pageerror',e=>report.pageErrors.push(String(e)));
    page.on('requestfailed',r=>report.failedRequests.push({url:r.url(),error:r.failure()?.errorText}));
    page.on('response',r=>{if(r.status()>=400)report.httpErrors.push({url:r.url(),status:r.status()});});
    report.sourceMatch={};
    for(const f of ['app.js','model-version.js','inhabited-reef.js']){
      const r=await context.request.get(new URL(f,target).href);const bytes=await r.body();
      report.sourceMatch[f]={status:r.status(),served:sha(bytes),checkout:sha(await fs.readFile(`${process.env.REEF_SOURCE_DIR||'dist'}/${f}`))};
      if(!r.ok()||report.sourceMatch[f].served!==report.sourceMatch[f].checkout)throw Error(`Pages source differs from checked-out ${f}`);
    }
    await page.goto(target,{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForFunction(()=>window.reef3d?.getState().ready===true||!document.querySelector('#unsupported').hidden,{},{timeout:150000});
    if(await page.locator('#unsupported').isVisible())throw Error(await page.locator('#failure').innerText());
    report.runtime=await page.evaluate(()=>window.reef3d.getState());
    report.actualCanvas=await page.evaluate(()=>{const c=document.querySelector('#reef');const gl=c.getContext('webgl2');const ext=gl.getExtension('WEBGL_debug_renderer_info');return {width:c.width,height:c.height,contextLost:gl.isContextLost(),renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER)};});
    report.captures=[];report.fixedViewMethod='Explicit camera/target and guide state through the existing app API; not an assertion that native input or transition smoothness passed.';
    async function capture(name){const file=path.join(out,`${name}.png`);await page.screenshot({path:file,timeout:45000});const state=await page.evaluate(()=>window.reef3d.getState());report.captures.push({file:`${name}.png`,sha256:sha(await fs.readFile(file)),state});await save();}
    async function fixedCamera(position,target,free=true){
      await page.evaluate(({position,target,free})=>{const r=window.reef3d;if(free)r.leaveGuide();r.setTour(false);r.camera.position.set(...position);r.controls.target.set(...target);r.controls.update();r.camera.updateMatrixWorld();},{position,target,free});
      const actual=await page.evaluate(()=>window.reef3d.getState());
      if(actual.camera.some((v,i)=>Math.abs(v-position[i])>.001)||actual.target.some((v,i)=>Math.abs(v-target[i])>.001))throw Error('Application constrained the requested camera; not the claimed fixed viewpoint');
      await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve(true)))));
    }
    report.scope='Bounded specimen label and narrow viewport QA. Software browser, not physical mobile hardware.';
    async function click(selector){const r=await page.locator(selector).boundingBox();if(!r)throw Error('Button unavailable: '+selector);await page.mouse.click(r.x+r.width/2,r.y+r.height/2);}
    await click('[data-guide="2"]');await page.waitForFunction(()=>window.reef3d.getState().guide.index===2);
    report.original=await page.evaluate(()=>window.reef3d.getState());
    await click('#specimenInspect');await page.waitForFunction(()=>window.reef3d.getState().specimenInspection);
    await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    report.layout=await page.evaluate(()=>{const r=window.reef3d,objects=[];r.root.traverse(o=>{if(o.name==='USNM_74016_Dry_Skeleton_25k'){const a=o.geometry.attributes.position;const p=r.camera.position.clone(),bounds={min:[Infinity,Infinity],max:[-Infinity,-Infinity]};for(let i=0;i<a.count;i++){p.fromBufferAttribute(a,i).applyMatrix4(o.matrixWorld).project(r.camera);const x=(p.x+1)*innerWidth/2,y=(1-p.y)*innerHeight/2;bounds.min[0]=Math.min(bounds.min[0],x);bounds.min[1]=Math.min(bounds.min[1],y);bounds.max[0]=Math.max(bounds.max[0],x);bounds.max[1]=Math.max(bounds.max[1],y)}objects.push(bounds)}});const card=document.querySelector('#guideCard').getBoundingClientRect();return {viewport:[innerWidth,innerHeight],scrollWidth:document.documentElement.scrollWidth,objects,card:{x:card.x,y:card.y,width:card.width,height:card.height},markersHidden:document.querySelector('#focusMarker').hidden&&document.querySelector('#focusMarkerSecondary').hidden,glError:document.querySelector('#reef').getContext('webgl2').getError()}});
    if(!report.layout.markersHidden||report.layout.scrollWidth>report.layout.viewport[0]||report.layout.glError!==0)throw Error('Label/overflow/GL failure');
    if(report.layout.objects.length!==1)throw Error('Specimen bounds missing');
    const b=report.layout.objects[0],v=report.layout.viewport,c=report.layout.card;
    if(b.min[0]<0||b.min[1]<0||b.max[0]>v[0]||b.max[1]>v[1])throw Error('Specimen clipped by viewport');
    if(b.max[0]>c.x&&b.min[0]<c.x+c.width&&b.max[1]>c.y&&b.min[1]<c.y+c.height)throw Error('Card overlaps specimen');
    await capture('01-unobscured-inspection');
    if(process.env.REEF_MOBILE==='true'){
      await click('#guideEvidence summary');await capture('02-source-expanded');
      const cr=await page.locator('#guideCard').boundingBox();await page.mouse.move(cr.x+cr.width/2,cr.y+cr.height/2);await page.mouse.wheel(0,650);
      await page.waitForTimeout(300);report.scrolled=await page.evaluate(()=>({scrollTop:document.querySelector('#guideCard').scrollTop,source:document.querySelector('#guideSource').href}));
      await capture('03-source-scrolled');
      await page.locator('#specimenReturn').scrollIntoViewIfNeeded();await click('#specimenReturn');await page.waitForFunction(()=>!window.reef3d.getState().specimenInspection);
      report.returned=await page.evaluate(()=>window.reef3d.getState());
      if(report.returned.camera.some((v,i)=>Math.abs(v-report.original.camera[i])>.001)||report.returned.target.some((v,i)=>Math.abs(v-report.original.target[i])>.001))throw Error('Return pose mismatch');
      await capture('04-returned');
    }
    report.counts=await page.evaluate(async()=>{const {GUIDE_STOPS}=await import('./guide-data.js');return {fish:window.reef3d.getState().fish,stops:GUIDE_STOPS.length}});
    if(report.counts.fish!==6||report.counts.stops!==5)throw Error('Count mismatch');report.nativeFlowPassed=true;
    const fish=()=>page.evaluate(()=>{const a=[];window.reef3d.root.traverse(o=>{if(/^fish_\d+$/.test(o.name))a.push({name:o.name,position:o.position.toArray()});});return a;});
    const before=await fish();await page.waitForTimeout(1500);const after=await fish();
    report.fixedTime={reducedMotion:true,tour:await page.evaluate(()=>window.reef3d.getState().tour),before,after,fishUnchanged:JSON.stringify(before)===JSON.stringify(after)};
    report.passed=report.pageErrors.length===0&&report.consoleErrors.length===0&&report.failedRequests.length===0&&report.httpErrors.length===0&&!report.actualCanvas.contextLost&&report.fixedTime.fishUnchanged&&report.fixedTime.tour===false;
    if(!report.passed)throw Error('Runtime or fixed-time check failed');

  }
}catch(e){report.error=String(e?.stack||e);report.passed=false;console.error(report.error);if(mode==='probe'&&process.env.GITHUB_OUTPUT)await fs.appendFile(process.env.GITHUB_OUTPUT,'available=false\n');if(mode==='render')process.exitCode=1;}
finally{await save();await context?.close().catch(()=>{});await browser?.close().catch(()=>{});}
