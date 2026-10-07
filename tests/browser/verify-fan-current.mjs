import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';

const mode=process.argv[2]||'probe';
if(!['probe','render'].includes(mode))throw Error('Expected probe or render');
const out=path.resolve('render-evidence',process.env.REEF_ARM||'probe');await fs.mkdir(out,{recursive:true});
const target=process.env.REEF_TARGET||'https://yydshly.github.io/azure-reef-3d/';
if(!['https://yydshly.github.io/azure-reef-3d/','http://127.0.0.1:4173/dist/','http://127.0.0.1:4173/research/fan-current/baseline/dist/','http://127.0.0.1:4173/research/fan-current/candidate/dist/'].includes(target))throw Error('Unapproved test target');
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
    async function capture(name){const file=path.join(out,`${name}.png`);await page.screenshot({path:file,timeout:45000});const state=await page.evaluate(()=>window.reef3d.getState());report.captures.push({file:`${name}.png`,sha256:sha(await fs.readFile(file)),state});await save();}
    async function fixedCamera(position,target,free=true){
      await page.evaluate(({position,target,free})=>{const r=window.reef3d;if(free)r.leaveGuide();r.setTour(false);r.camera.position.set(...position);r.controls.target.set(...target);r.controls.update();r.camera.updateMatrixWorld();},{position,target,free});
      const actual=await page.evaluate(()=>window.reef3d.getState());
      if(actual.camera.some((v,i)=>Math.abs(v-position[i])>.001)||actual.target.some((v,i)=>Math.abs(v-target[i])>.001))throw Error('Application constrained the requested camera; not the claimed fixed viewpoint');
      await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve(true)))));
    }
    report.method='Two equally instrumented QA copies expose the existing renderer only. Fixed phases explicitly freeze RAF and render after fan update; native segment uses genuine RAF/visible elapsed time. Not a device FPS claim.';
    const pose={p:[-7.972653486778265,2.5342332277063293,-23.939230761867375],t:[-5.572664305470652,1.8842332277063294,-26.013779370506473]};
    await page.evaluate(()=>{window.reef3d.camera.clearViewOffset();window.reef3d.camera.fov=47;window.reef3d.camera.updateProjectionMatrix()});await fixedCamera(pose.p,pose.t);
    if(process.env.REEF_NATIVE==='true'){
      const before=await page.evaluate(()=>({wallMs:performance.now(),state:window.reef3d.getState(),frames:window.__qaFrames.length}));
      await page.waitForTimeout(24000);const after=await page.evaluate(()=>({wallMs:performance.now(),state:window.reef3d.getState(),frames:window.__qaFrames.length,samples:window.__qaFrames}));report.native={before,after,wallSeconds:(after.wallMs-before.wallMs)/1000,observedRaf:after.frames-before.frames};
      if(after.state.simulationTime<=before.state.simulationTime)throw Error('Native scene time did not advance');
      await capture('native-observation-end');
    }else{
      const phases=process.env.REEF_ARM==='baseline'?[0]:[0,2,6];report.phases=[];
      for(const seconds of phases){const state=await page.evaluate(seconds=>{window.__qaFreeze=true;const r=window.reef3d;r.fanCurrent?.update(seconds);window.__qaRenderer.render(r.scene,r.camera);const gl=document.querySelector('#reef').getContext('webgl2');const fish=[];r.root.traverse(o=>{if(/^fish_\d+$/.test(o.name))fish.push({name:o.name,p:o.position.toArray(),q:o.quaternion.toArray()})});return {app:r.getState(),fish,glError:gl.getError()}},seconds);report.phases.push({seconds,state});if(state.app.simulationTime!==0||state.glError!==0)throw Error('Fixed-time or GL check failed');if(state.app.fanCurrent&&Math.abs(state.app.fanCurrent.amplitude-(seconds===2?.04:seconds===6?-.04:0))>1e-9)throw Error('Wrong phase amplitude');await capture('phase-'+seconds);}
      if(process.env.REEF_ARM!=='baseline'){
        report.quality=[];for(let i=0;i<2;i++){const rect=await page.locator('#quality').boundingBox();await page.mouse.click(rect.x+rect.width/2,rect.y+rect.height/2);report.quality.push(await page.evaluate(()=>{const r=window.reef3d;window.__qaRenderer.render(r.scene,r.camera);return {low:r.getState().low,glError:document.querySelector('#reef').getContext('webgl2').getError(),programs:window.__qaRenderer.info.programs.map(p=>({name:p.name,runnable:p.diagnostics?.runnable??null}))}}));}if(report.quality.some(x=>x.glError!==0)||report.quality.at(-1).low)throw Error('Quality restore/GL failure');
      }
    }
    report.passed=report.pageErrors.length===0&&report.consoleErrors.length===0&&report.failedRequests.length===0&&report.httpErrors.length===0&&!report.actualCanvas.contextLost;
    if(!report.passed)throw Error('Runtime errors');

  }
}catch(e){report.error=String(e?.stack||e);report.passed=false;console.error(report.error);if(mode==='probe'&&process.env.GITHUB_OUTPUT)await fs.appendFile(process.env.GITHUB_OUTPUT,'available=false\n');if(mode==='render')process.exitCode=1;}
finally{await save();await context?.close().catch(()=>{});await browser?.close().catch(()=>{});}
