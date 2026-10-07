import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';

const mode=process.argv[2]||'probe';
if(!['probe','render'].includes(mode))throw Error('Expected probe or render');
const out=path.resolve('render-evidence');await fs.mkdir(out,{recursive:true});
const target='http://127.0.0.1:4173/';
if(!['https://yydshly.github.io/azure-reef-3d/','http://127.0.0.1:4173/'].includes(target))throw Error('Unapproved test target');
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
  context=await browser.newContext({viewport:{width:1120,height:700},deviceScaleFactor:1,reducedMotion:'no-preference',...(mode==='render'&&process.env.RECORD_VIDEO==='true'?{recordVideo:{dir:path.join(out,'video'),size:{width:1120,height:700}}}:{})});
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
    for(const f of ['app.js','model-version.js']){
      const r=await context.request.get(new URL(f,target).href);const bytes=await r.body();
      report.sourceMatch[f]={status:r.status(),served:sha(bytes),checkout:sha(await fs.readFile(`research/galapagos/dist/${f}`))};
      if(!r.ok()||report.sourceMatch[f].served!==report.sourceMatch[f].checkout)throw Error('Preview source mismatch');
    }
    await page.goto(target,{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForFunction(()=>window.reefResearch?.getState().ready||!document.querySelector('#error').hidden,{},{timeout:150000});
    if(await page.locator('#error').isVisible())throw Error(await page.locator('#error').innerText());
    report.captures=[];report.inputMethod='Native button clicks; two animation frames before each screenshot';
    async function capture(name){
      await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
      const file=path.join(out,name+'.png');await page.screenshot({path:file,timeout:45000});
      const state=await page.evaluate(()=>window.reefResearch.getState());
      report.captures.push({file:name+'.png',sha256:sha(await fs.readFile(file)),state});await save();
    }
    await page.locator('[data-view="front"]').click({noWaitAfter:true});
    await page.locator('[data-mode="points"]').click({noWaitAfter:true});await capture('1-front-points');
    await page.locator('[data-mode="surface"]').click({noWaitAfter:true});await capture('2-front-surface');
    const [a,b]=report.captures;if(JSON.stringify(a.state.camera)!==JSON.stringify(b.state.camera)||!a.state.pointVisible||a.state.surfaceVisible||b.state.pointVisible||!b.state.surfaceVisible)throw Error('Point/surface comparison mismatch');
    await page.locator('[data-view="reverse"]').click({noWaitAfter:true});await capture('3-reverse-surface');
    const before=await page.evaluate(()=>window.reefResearch.getState());
    await page.mouse.move(780,330);await page.mouse.down();await page.mouse.move(840,370,{steps:8});await page.mouse.up();await capture('4-after-native-drag');
    report.nativeDragChanged=JSON.stringify(before.camera)!==JSON.stringify(report.captures.at(-1).state.camera);
    report.actualCanvas=await page.evaluate(()=>{const gl=document.querySelector('#scene').getContext('webgl2');return {contextLost:gl.isContextLost(),error:gl.getError()}});
    report.passed=report.pageErrors.length===0&&report.consoleErrors.length===0&&report.failedRequests.length===0&&report.httpErrors.length===0&&!report.actualCanvas.contextLost&&report.nativeDragChanged;
    if(!report.passed)throw Error('Research runtime check failed');

  }
}catch(e){report.error=String(e?.stack||e);report.passed=false;console.error(report.error);if(mode==='probe'&&process.env.GITHUB_OUTPUT)await fs.appendFile(process.env.GITHUB_OUTPUT,'available=false\n');if(mode==='render')process.exitCode=1;}
finally{await save();await context?.close().catch(()=>{});await browser?.close().catch(()=>{});}
