import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';

const mode=process.argv[2]||'probe';
if(!['probe','render'].includes(mode))throw Error('Expected probe or render');
const out=path.resolve('render-evidence',process.env.REEF_ARM||'probe');await fs.mkdir(out,{recursive:true});
const target=process.env.REEF_TARGET||'https://yydshly.github.io/azure-reef-3d/';
if(!['https://yydshly.github.io/azure-reef-3d/','http://127.0.0.1:4173/research/shoulder-v3-baseline/dist/','http://127.0.0.1:4173/research/shoulder-candidate/dist/'].includes(target))throw Error('Unapproved test target');
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
  context=await browser.newContext({viewport:{width:1120,height:700},deviceScaleFactor:1,reducedMotion:'reduce',...(mode==='render'&&process.env.RECORD_VIDEO==='true'?{recordVideo:{dir:path.join(out,'video'),size:{width:1120,height:700}}}:{})});
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
    for(const f of ['app.js','model-version.js','assets/shoulder-v3/pilot.glb']){
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
    const planned=[{name:'midway',p:[0,2.7,-18],t:[-1.5,1,-31]},{name:'local-front',p:[-2,2.4,-20],t:[-6.4,.9,-26]},{name:'local-reverse',p:[-10,2.7,-32],t:[-6.4,.9,-26]}];
    await page.evaluate(()=>window.reef3d.leaveGuide());
    report.plannedViews=planned;
    for(let i=0;i<planned.length;i++){const v=planned[i];await fixedCamera(v.p,v.t);await capture(`${i+1}-${v.name}`);}
    const fish=()=>page.evaluate(()=>{const a=[];window.reef3d.root.traverse(o=>{if(/^fish_\d+$/.test(o.name))a.push({name:o.name,position:o.position.toArray()});});return a;});
    const before=await fish();await page.waitForTimeout(1500);const after=await fish();
    report.fixedTime={reducedMotion:true,tour:await page.evaluate(()=>window.reef3d.getState().tour),before,after,fishUnchanged:JSON.stringify(before)===JSON.stringify(after)};
    report.passed=report.pageErrors.length===0&&report.consoleErrors.length===0&&report.failedRequests.length===0&&report.httpErrors.length===0&&!report.actualCanvas.contextLost&&report.fixedTime.fishUnchanged&&report.fixedTime.tour===false;
    if(!report.passed)throw Error('Runtime or fixed-time check failed');

  }
}catch(e){report.error=String(e?.stack||e);report.passed=false;console.error(report.error);if(mode==='probe'&&process.env.GITHUB_OUTPUT)await fs.appendFile(process.env.GITHUB_OUTPUT,'available=false\n');if(mode==='render')process.exitCode=1;}
finally{await save();await context?.close().catch(()=>{});await browser?.close().catch(()=>{});}
