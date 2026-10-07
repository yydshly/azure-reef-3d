import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';

const mode=process.argv[2]||'probe';
if(!['probe','render'].includes(mode))throw Error('Expected probe or render');
const out=path.resolve('render-evidence',process.env.REEF_ARM||'probe');await fs.mkdir(out,{recursive:true});
const target=process.env.REEF_TARGET||'https://yydshly.github.io/azure-reef-3d/';
if(!['https://yydshly.github.io/azure-reef-3d/','http://127.0.0.1:4173/dist/','http://127.0.0.1:4173/research/branch-grounding/baseline/dist/','http://127.0.0.1:4173/research/branch-grounding/candidate/dist/'].includes(target))throw Error('Unapproved test target');
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
  context=await browser.newContext({viewport:{width:1120,height:700},deviceScaleFactor:1,reducedMotion:process.env.REEF_NATIVE==='true'?'no-preference':'reduce',...(mode==='render'&&process.env.RECORD_VIDEO==='true'?{recordVideo:{dir:path.join(out,'video'),size:{width:1120,height:700}}}:{})});
  page=await context.newPage();page.setDefaultTimeout(30000);
  await page.addInitScript(()=>{window.__qaFreeze=false;window.__qaFrames=[];const native=requestAnimationFrame.bind(window);window.requestAnimationFrame=cb=>native(t=>{if(window.__qaFreeze)return;cb(t);const r=window.reef3d;if(r?.getState().ready){window.__qaFrames.push({wallMs:performance.now(),time:r.getState().simulationTime,fan:r.fanCurrent?.getState()});if(window.__qaFrames.length>500)window.__qaFrames.shift()}})});
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
    async function capture(name){const file=path.join(out,`${name}.png`);await page.screenshot({path:file,timeout:45000});const state=await page.evaluate(()=>window.reef3d.getState());const rendererInfo=await page.evaluate(()=>({render:{...window.__qaRenderer.info.render},memory:{...window.__qaRenderer.info.memory},programCount:window.__qaRenderer.info.programs.length}));report.captures.push({rendererInfo,file:`${name}.png`,sha256:sha(await fs.readFile(file)),state});await save();}
    async function fixedCamera(position,target,free=true){
      await page.evaluate(({position,target,free})=>{const r=window.reef3d;if(free)r.leaveGuide();r.setTour(false);r.camera.position.set(...position);r.controls.target.set(...target);r.controls.update();r.camera.updateMatrixWorld();},{position,target,free});
      const actual=await page.evaluate(()=>window.reef3d.getState());
      if(actual.camera.some((v,i)=>Math.abs(v-position[i])>.001)||actual.target.some((v,i)=>Math.abs(v-target[i])>.001))throw Error('Application constrained the requested camera; not the claimed fixed viewpoint');
      await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve(true)))));
    }
    report.method='Two equal QA renderer references for counters; unchanged47-degree FOV, fixed reduced-motion t0. No native performance trial.';
    const views=[{id:'midway',p:[0,2.7,-18],t:[-1.5,1,-31]},{id:'diagnostic-close',p:[4.7,1.25,-21.7],t:[1.8,0,-25.45]}];
    report.views=[];
    for(const v of views){await page.evaluate(()=>{const c=window.reef3d.camera;c.clearViewOffset();c.fov=47;c.updateProjectionMatrix()});await fixedCamera(v.p,v.t);await capture(v.id);report.views.push(await page.evaluate(()=>{const r=window.reef3d;const fish=[];r.root.traverse(o=>{if(/^fish_\d+$/.test(o.name))fish.push({name:o.name,p:o.position.toArray(),q:o.quaternion.toArray()})});return {state:r.getState(),fish,glError:document.querySelector('#reef').getContext('webgl2').getError()}}));}
    report.isolation=await page.evaluate(async()=>{const r=window.reef3d,meshes=[];r.root.traverse(o=>{if(o.isMesh)meshes.push(o)});const hash=async a=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new Uint8Array(a.buffer,a.byteOffset,a.byteLength)))).map(x=>x.toString(16).padStart(2,'0')).join('');const items=await Promise.all(meshes.map(async o=>{const attributes={};for(const [key,a] of Object.entries(o.geometry.attributes))attributes[key]=await hash(a.array);const m=o.material;return {name:o.name,indexCount:o.geometry.index?.count??0,indexHash:o.geometry.index?await hash(o.geometry.index.array):null,attributes,position:o.position.toArray(),scale:o.scale.toArray(),quaternion:o.quaternion.toArray(),material:{name:m.name,color:m.color?.toArray(),roughness:m.roughness,metalness:m.metalness,vertexColors:m.vertexColors,maps:['map','normalMap','roughnessMap','metalnessMap','aoMap'].map(k=>({slot:k,present:!!m[k],width:m[k]?.image?.width??null,height:m[k]?.image?.height??null}))}}}));const {GUIDE_STOPS}=await import('./guide-data.js');return {items,fish:r.getState().fish,guide:GUIDE_STOPS.length}});
    if(report.isolation.fish!==6||report.isolation.guide!==5)throw Error('Scene count mismatch');
    const branch=report.isolation.items.find(o=>o.name==='Corridor_Distant_Linked_03'),support=report.isolation.items.find(o=>o.name==='Distant_Limestone_Support_03');
    if(branch.indexCount!==66504||support.indexCount!==144150)throw Error('Geometry changed');
    const expectedY=process.env.REEF_ARM==='candidate'?-.3340986692829022:-.20698136165738104;if(Math.abs(branch.position[1]-expectedY)>1e-9)throw Error('Wrong branch placement');
    if(report.views.some(v=>v.glError!==0||v.state.simulationTime!==0))throw Error('GL/frozen time mismatch');
    report.passed=report.pageErrors.length===0&&report.consoleErrors.length===0&&report.failedRequests.length===0&&report.httpErrors.length===0&&!report.actualCanvas.contextLost;
    if(!report.passed)throw Error('Runtime error');

  }
}catch(e){report.error=String(e?.stack||e);report.passed=false;console.error(report.error);if(mode==='probe'&&process.env.GITHUB_OUTPUT)await fs.appendFile(process.env.GITHUB_OUTPUT,'available=false\n');if(mode==='render')process.exitCode=1;}
finally{await save();await context?.close().catch(()=>{});await browser?.close().catch(()=>{});}
