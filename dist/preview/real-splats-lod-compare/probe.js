import * as THREE from 'three';
import { SparkRenderer, SplatMesh } from '@sparkjsdev/spark';
import { PRESETS, validLod, cadence, movement, outsideReference, shaHex } from './probe-core.js';

const $=id=>document.getElementById(id), canvas=$('reef'), keys=new Set();
const history=[], errors=[], reports=[], listeners=[];
let manifest, runtime=null, epoch=0, framePromise=Promise.resolve(), lifecyclePromise=Promise.resolve();
let selectedLod=4, retainedPose=null, monitorHandle=0;
let aborter=null, frameHandle=0, yaw=0,pitch=0,drag=null,currentView='overview',guides=true,state='boot',lastTime=0;
const stats={loads:0,unloads:0,contextLosses:0,frames:0,lastDispose:null,assetSha:null,peakActiveRuntimes:0};
function listen(target,type,fn,options){target.addEventListener(type,fn,options);listeners.push(()=>target.removeEventListener(type,fn,options));}
function record(event,detail={}){history.push({at:new Date().toISOString(),event,...detail});if(history.length>300)history.shift();}
function setState(next,label,detail){state=next;document.body.dataset.state=next;$('stage').textContent=label;if(detail)$('detail').textContent=detail;record(next);}
function recordError(error,kind='runtime'){const value={kind,message:String(error?.message||error),at:new Date().toISOString()};errors.push(value);console.error(error);return value;}
function fail(error,kind='runtime') {recordError(error,kind);setState('error','检查未通过',String(error?.message||error));$('failure').textContent=String(error?.message||error);$('fallback').hidden=false;}
async function boundedOperation(promise,ms,rt,label){
  let timer;
  try{return await Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>{const error=new Error(`${label} 超时；停止此轮检查。请刷新页面释放整个浏览器上下文。`);error.code='GPU_OPERATION_TIMEOUT';rt.quarantined=true;rt.stopping=true;reject(error);},ms);})]);}
  finally{clearTimeout(timer);}
}
function incompleteDispose(rt){stats.lastDispose={at:new Date().toISOString(),status:'INCOMPLETE_RELOAD_REQUIRED',meshCleared:false,reason:'Pending worker/GPU operation cannot be safely freed in place'};record('quarantined',stats.lastDispose);return false;}
function updateControls(){
  for(const id of ['unload','reload'])$(id).disabled=state==='unloading';
  for(const button of document.querySelectorAll('[data-lod]')){button.setAttribute('aria-pressed',String(Number(button.dataset.lod)===selectedLod));button.disabled=state==='unloading';}
  const actual=runtime?.ready?runtime.asset:null,target=manifest?.assets?.[selectedLod];
  $('asset').textContent=actual?`当前 LOD${actual.lod} · ${actual.count.toLocaleString()} 个 Gaussian · ${actual.bytes.toLocaleString()} B 原始数据`:`当前无已解析数据 · 请求 LOD${selectedLod}${target?' · '+target.bytes.toLocaleString()+' B 原始数据':''}`;
}
function cameraPose(rt=runtime){return rt?{position:rt.camera.position.toArray(),quaternion:rt.camera.quaternion.toArray(),view:currentView}:retainedPose;}
function restorePose(rt,pose){if(!pose){setView('overview');return;}rt.camera.position.fromArray(pose.position);rt.camera.quaternion.fromArray(pose.quaternion);orientFromCamera(rt.camera);rt.dirty=true;currentView=pose.view;}
function cadenceReport(rt){if(!rt)return null;const now=performance.now(),fallback=rt.readyAt&&now-rt.readyAt>=3000?{samples:0,spanMs:Math.min(5000,now-rt.readyAt),hz:0}:null,render=cadence(rt.renderTimes,now)||fallback,raf=cadence(rt.rafTimes,now)||fallback;return {windowMs:5000,render,raf,totalRendered:rt.rendered,totalRafCallbacks:rt.rafCallbacks,lowCadence:!!render&&render.spanMs>=3000&&render.hz<20,note:'render = completed renderer.render submissions per second; independent RAF callbacks are scheduling cadence, neither measures GPU presentation FPS.'};}
function monitorCadence(rt){if(runtime!==rt||rt.stopping)return;monitorHandle=requestAnimationFrame(now=>{monitorHandle=0;if(runtime!==rt||rt.stopping)return;rt.rafCallbacks++;rt.rafTimes.push(now);while(rt.rafTimes.length>900)rt.rafTimes.shift();const c=cadenceReport(rt);if(now-rt.lastCadenceUi>500){rt.lastCadenceUi=now;$('cadence').textContent=c.render?`${c.lowCadence?'低帧限制 · ':''}实际 render ${c.render.hz.toFixed(1)}/s · 独立 RAF ${c.raf?.hz.toFixed(1)??'待测'}/s；不是用户设备流畅保证`:'渲染节奏待测；来源大小与 RAF 都不能证明流畅';$('cadence').dataset.low=String(c.lowCadence);}monitorCadence(rt);});}
function registerRender(rt){rt.rendered++;rt.renderTimes.push(performance.now());while(rt.renderTimes.length>900)rt.renderTimes.shift();}
function storageReport(rt){const ext=rt?.mesh?.extSplats;const arrays={};for(const [i,value] of (ext?.extArrays||[]).entries())if(ArrayBuffer.isView(value))arrays['extArrays.'+i]=value.byteLength;for(const [key,value] of Object.entries(ext?.extra||{}))if(ArrayBuffer.isView(value))arrays['extra.'+key]=value.byteLength;return {sourceArrayBytesObserved:arrays,sourceArraySumBytes:Object.values(arrays).reduce((a,b)=>a+b,0),sourceMaxSplats:ext?.maxSplats??null,sourceMaxSh:ext?.maxSh??null,meshMaxSh:rt?.mesh?.maxSh??null,sourceShDegree:ext?.getNumSh?.()??null,effectiveShDegree:ext?Math.min(rt.mesh.maxSh,ext.maxSh,ext.getNumSh()):null,automaticLodDataPresent:!!(rt?.mesh?.lodSplats||ext?.lodSplats),threeMemory:rt?{...rt.renderer.info.memory}:null,jsHeap:performance.memory?{usedJSHeapSize:performance.memory.usedJSHeapSize,totalJSHeapSize:performance.memory.totalJSHeapSize,jsHeapSizeLimit:performance.memory.jsHeapSizeLimit}:null,gpuTotalBytes:null,peakTotalBytes:null,note:'Observed JS source arrays and Three counters are partial. GPU driver, decoder/WASM peaks and global decoder pool are not measured.'};}

function orientFromCamera(camera){const e=new THREE.Euler().setFromQuaternion(camera.quaternion,'YXZ');yaw=e.y;pitch=e.x;}
function setView(name){if(!PRESETS[name]||!runtime)return false;const p=PRESETS[name];runtime.camera.position.fromArray(p.position);runtime.camera.lookAt(new THREE.Vector3(...p.target));orientFromCamera(runtime.camera);runtime.dirty=true;currentView=name;keys.clear();record('view',{name,position:p.position});return true;}
function updateBoundary(rt){const outside=outsideReference(rt.camera.position.toArray(),manifest.coordinates.rawOrigin,manifest.bounds.orthoXY);$('boundary').textContent=outside?'当前在参考范围外：这里及背面/空洞处均没有完整数据保证。':'在参考范围内：框内也可能缺失；橙色框不是实测实体或覆盖保证。';}
function addGuides(rt){
  const group=new THREE.Group();group.name='Non-data reference markers';
  const b=manifest.bounds.orthoXY,c=manifest.coordinates.rawOrigin,min=manifest.bounds.worldCenterMin,max=manifest.bounds.worldCenterMax;
  const box=new THREE.Box3(new THREE.Vector3(b.min_x-c[0],min[1],c[1]-b.max_y),new THREE.Vector3(b.max_x-c[0],max[1],c[1]-b.min_y));
  const helper=new THREE.Box3Helper(box,0xd29a52);helper.material.transparent=true;helper.material.opacity=.65;group.add(helper);
  // One metre reference outside the center cloud. It is deliberately a line, never a surrogate seabed.
  const y=min[1]-.35,z=c[1]-b.min_y+.35,x=b.min_x-c[0];
  const pts=[[x,y,z],[x+1,y,z],[x,y-.08,z],[x,y+.08,z],[x+1,y-.08,z],[x+1,y+.08,z]];
  const ruler=new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(pts.map(p=>new THREE.Vector3(...p))),new THREE.LineBasicMaterial({color:0xf9dc91}));ruler.name='1 m reference ruler';group.add(ruler);
  group.visible=guides;rt.scene.add(group);rt.guides=group;
}
function instrumentDraws(rt){
  const gl=rt.renderer.getContext();rt.draw={hookInstalled:false,instancedCalls:0,nonzeroSplatDraws:0,instancesSubmitted:0,lastInstances:0,lastAt:null};let inSpark=false;
  const before=rt.spark.onBeforeRender.bind(rt.spark),after=rt.spark.onAfterRender.bind(rt.spark);
  rt.spark.onBeforeRender=(...args)=>{before(...args);inSpark=true;};
  rt.spark.onAfterRender=(...args)=>{inSpark=false;after(...args);};
  rt.restoreGl=[];
  for(const name of ['drawElementsInstanced','drawArraysInstanced']){
    const original=gl[name];
    const wrapped=function(...args){
      const result=original.apply(this,args);
      if(inSpark){const count=args.at(-1);rt.draw.instancedCalls++;rt.draw.lastInstances=count;rt.draw.instancesSubmitted+=count;if(count>0)rt.draw.nonzeroSplatDraws++;rt.draw.lastAt=performance.now();}
      return result;
    };
    try{gl[name]=wrapped;if(gl[name]!==wrapped)throw new Error('WebGL function not writable');rt.restoreGl.push(()=>{gl[name]=original;});}
    catch(error){record('draw-hook-unavailable',{method:name,message:String(error)});}
  }
  rt.draw.hookInstalled=rt.restoreGl.length===2;
}
function resize(){if(!runtime)return;const rt=runtime;rt.renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));rt.renderer.setSize(innerWidth,innerHeight,false);rt.camera.aspect=innerWidth/innerHeight;rt.camera.updateProjectionMatrix();rt.renderer.getDrawingBufferSize(rt.spark.renderSize);rt.dirty=true;}
function schedule(){if(!runtime||runtime.stopping||runtime.capturing||frameHandle)return;frameHandle=requestAnimationFrame(now=>{frameHandle=0;framePromise=frame(now);framePromise.catch(error=>{if(runtime){void unload().then(()=>fail(error,'frame'));}});});}
async function frame(now){
  const rt=runtime;if(!rt||rt.stopping)return;const start=performance.now();const dt=lastTime?(now-lastTime)/1000:0;lastTime=now;
  if(document.visibilityState!=='hidden'){
    const delta=movement(keys,(keys.has('ShiftLeft')||keys.has('ShiftRight')) ? 0.5 : 1.5,dt,yaw,pitch);
    if(delta.some(v=>v!==0)){rt.camera.position.add(new THREE.Vector3(...delta));rt.dirty=true;currentView='free';}
    rt.camera.rotation.set(pitch,yaw,0,'YXZ');rt.scene.updateMatrixWorld(true);rt.camera.updateMatrixWorld(true);
    if(rt.dirty){rt.dirty=false;await boundedOperation(rt.spark.update({scene:rt.scene,camera:rt.camera}),10000,rt,'Gaussian GPU 更新');}
    if(rt.stopping||runtime!==rt)return;
    rt.renderer.render(rt.scene,rt.camera);registerRender(rt);stats.frames++;rt.frameMs.push(performance.now()-start);if(rt.frameMs.length>600)rt.frameMs.shift();
    if(stats.frames%10===0){$('stage').textContent=`${"LOD"+rt.asset.lod} · ${rt.mesh?.numSplats?.toLocaleString()||0} Gaussian 已解析 · ${rt.spark.activeSplats.toLocaleString()} 参与绘制`;$('detail').textContent=rt.draw.nonzeroSplatDraws>0?'已观测到 WebGL 实例化绘制调用；外观与完整度仍需目视验收。':'已解析不等于可见。正在等待真实 Gaussian draw。';updateBoundary(rt);}
  }
  schedule();
}
async function fetchBytes(asset,signal){
  const url=asset.url;
  const response=await fetch(url,{signal,cache:'no-cache'});if(!response.ok)throw new Error(`数据读取失败 HTTP ${response.status}`);
  const reader=response.body?.getReader();if(!reader){const wire=new Uint8Array(await response.arrayBuffer());return decodeTransport(wire,asset);}
  const parts=[];let length=0;for(;;){const {done,value}=await reader.read();if(done)break;parts.push(value);length+=value.length;if(length>asset.transport.bytes){await reader.cancel();throw new Error(`数据大小超出固定 LOD${asset.lod} 压缩包，停止加载`);}$('detail').textContent=`读取 LOD${asset.lod} 压缩包：${(length/1e6).toFixed(2)} / ${(asset.transport.bytes/1e6).toFixed(2)} MB；解压后 ${(asset.bytes/1e6).toFixed(2)} MB`;}
  const bytes=new Uint8Array(length);let offset=0;for(const part of parts){bytes.set(part,offset);offset+=part.length;}parts.length=0;return decodeTransport(bytes,asset);
}
async function decodeTransport(wire,asset){
  if(wire.length!==asset.transport.bytes)throw new Error(`LOD${asset.lod} 传输大小不符`);
  if(!crypto.subtle)throw new Error('需要 localhost 或 HTTPS 安全上下文验证 SHA256。');
  if(shaHex(await crypto.subtle.digest('SHA-256',wire))!==asset.transport.sha256)throw new Error('压缩包 SHA256 不符，停止');
  if(typeof DecompressionStream!=='function')throw new Error('此浏览器没有标准 gzip 解压支持，停止；不会改用低清数据冒充。');
  const stream=new Blob([wire]).stream().pipeThrough(new DecompressionStream('gzip'));
  const reader=stream.getReader(),bytes=new Uint8Array(asset.bytes);let length=0;
  try{for(;;){const {done,value}=await reader.read();if(done)break;if(length+value.length>asset.bytes)throw new Error('解压数据超出已核验字节数');bytes.set(value,length);length+=value.length;}}catch(error){await reader.cancel().catch(()=>{});throw error;}
  if(length!==asset.bytes)throw new Error('解压后原始 PLY 大小不符');return bytes;
}
async function initialize(token,lod,pose){
  const asset=manifest.assets[lod];stats.assetSha=null;

  $('fallback').hidden=true;setState('loading','正在检查 WebGL2 与固定数据');
  let renderer;
  try{renderer=new THREE.WebGLRenderer({canvas,antialias:false,alpha:false,preserveDrawingBuffer:false,powerPreference:'high-performance'});}
  catch{throw new Error('当前环境无法创建 WebGL2。CPU 解析和源码检查不能代替真实 GPU 验证。');}
  const rt={asset,frameMs:[],renderTimes:[],rafTimes:[],rendered:0,rafCallbacks:0,lastCadenceUi:0,renderer,scene:new THREE.Scene(),camera:new THREE.PerspectiveCamera(65,1,.03,80),mesh:null,spark:null,guides:null,stopping:false,dirty:true,loadToken:token};if(runtime)throw new Error('禁止同时保留两档场景');runtime=rt;stats.peakActiveRuntimes=Math.max(stats.peakActiveRuntimes,1);updateControls();
  rt.scene.background=new THREE.Color('#151920');renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.NoToneMapping;renderer.debug.checkShaderErrors=true;
  renderer.debug.onShaderError=(gl,program,vs,fs)=>{throw new Error('GPU shader compilation/link failed: '+[gl.getProgramInfoLog(program),gl.getShaderInfoLog(vs),gl.getShaderInfoLog(fs)].filter(Boolean).join('\n'));};
  rt.spark=new SparkRenderer({renderer,autoUpdate:false,enableLod:false,enableDriveLod:false});rt.spark.name='Spark Gaussian renderer';rt.scene.add(rt.spark);instrumentDraws(rt);addGuides(rt);resize();restorePose(rt,pose);
  aborter=new AbortController();const bytes=await boundedOperation(fetchBytes(asset,aborter.signal),30000,rt,'本地数据读取');if(bytes.length!==asset.bytes)throw new Error(`LOD${lod} 大小不符：${bytes.length}`);
  if(!crypto.subtle)throw new Error('需要 localhost 或 HTTPS 安全上下文验证原始数据 SHA256。');
  const hash=shaHex(await crypto.subtle.digest('SHA-256',bytes));if(hash!==asset.sha256)throw new Error('原始文件 SHA256 不符，停止');stats.assetSha=hash;
  if(token!==epoch)return;
  const mesh=new SplatMesh({fileBytes:bytes,fileName:`lod${lod}.ply`,extSplats:true,lod:false,enableLod:false,raycastable:false});rt.mesh=mesh;
  await boundedOperation(mesh.initialized,15000,rt,'Gaussian 解码');if(token!==epoch||rt.stopping)return;
  if(mesh.numSplats!==asset.count)throw new Error(`Gaussian 数量不符：${mesh.numSplats}`);
  // Positive source Z -> world up is a documented inference pending visual validation.
  // Applying a rigid transform on SplatMesh also rotates Gaussian covariance and view-dependent SH direction.
  const c=manifest.coordinates.rawOrigin;mesh.rotation.x=-Math.PI/2;mesh.position.set(-c[0],-c[2],c[1]);mesh.name=`Unmodified Soneva LOD${lod} Gaussian payload`;rt.scene.add(mesh);
  rt.sourceBounds=mesh.getBoundingBox(true);rt.ready=true;rt.readyAt=performance.now();stats.loads++;setState('ready','原始数据已解析 · 真实绘制待观察','未加入水雾、鱼群或缺失面的补造。');record('decoded',{lod,bytes:asset.bytes,count:mesh.numSplats,bounds:{min:rt.sourceBounds.min.toArray(),max:rt.sourceBounds.max.toArray()}});lastTime=0;updateControls();monitorCadence(rt);schedule();
}
async function destroy(rt){
  if(!rt)return;retainedPose=cameraPose(rt);rt.stopping=true;cancelAnimationFrame(frameHandle);cancelAnimationFrame(monitorHandle);frameHandle=0;monitorHandle=0;
  // The explicit update loop never overlaps sorts; finish the current promise before freeing its workers/textures.
  if(rt.quarantined)return incompleteDispose(rt);
  try{await boundedOperation(framePromise.catch(()=>{}),10000,rt,'GPU 释放前等待');}catch(error){recordError(error,'teardown-timeout');return incompleteDispose(rt);}
  if(rt.quarantined)return incompleteDispose(rt);
  const before={...rt.renderer.info.memory};const sourceStorageBefore=storageReport(rt);const disposedLod=rt.asset.lod;
  if(rt.mesh){rt.scene.remove(rt.mesh);rt.mesh.dispose();rt.mesh=null;}
  if(rt.spark){rt.scene.remove(rt.spark);rt.spark.dispose();}
  rt.guides?.traverse(obj=>{obj.geometry?.dispose();if(Array.isArray(obj.material))obj.material.forEach(m=>m.dispose());else obj.material?.dispose();});
  rt.restoreGl?.forEach(fn=>fn());rt.scene.clear();rt.renderer.renderLists.dispose();rt.renderer.dispose();
  const after={...rt.renderer.info.memory};stats.lastDispose={at:new Date().toISOString(),disposedLod,sourceStorageBefore,before,after,sceneChildren:rt.scene.children.length,meshCleared:rt.mesh===null,sortWorkerCleared:rt.spark?.sortWorker===null,animationLoopCancelled:frameHandle===0,scope:'Per-runtime mesh/GPU resources and sort worker; Spark global decoder pool may remain alive'};
  record('disposed',stats.lastDispose);stats.unloads++;if(runtime===rt)runtime=null;stats.assetSha=null;updateControls();return true;
}
function unload(){
  epoch++;aborter?.abort();keys.clear();if(runtime)runtime.stopping=true;cancelAnimationFrame(frameHandle);frameHandle=0;setState('unloading','正在释放资源');updateControls();
  lifecyclePromise=lifecyclePromise.catch(()=>{}).then(async()=>{const complete=await destroy(runtime);if(complete===false)fail(new Error('释放未完成：后台操作超时，请刷新页面后重试。'),'teardown');else setState('unloaded','数据已卸载','已释放此场景的模型/GPU资源；解码工作线程池可能留在页面中。');updateControls();});return lifecyclePromise;
}
function load(lod=selectedLod){
  if(!validLod(lod))return Promise.reject(new Error('仅允许 LOD4 与 LOD3；本次不继续升级'));
  const pose=cameraPose();keys.clear();drag=null;selectedLod=lod;updateControls();
  if(runtime?.quarantined){fail(new Error('上一轮后台操作未完成，请刷新页面后重新检查。'),'quarantine');return Promise.resolve(false);}
  const token=++epoch;aborter?.abort();if(runtime)runtime.stopping=true;
  lifecyclePromise=lifecyclePromise.catch(()=>{}).then(async()=>{const complete=await destroy(runtime);if(complete===false){fail(new Error('上一轮释放未完成，请刷新页面后重新检查。'),'quarantine');return;}if(token!==epoch)return;try{await initialize(token,lod,pose);}catch(error){await destroy(runtime);if(token===epoch&&error?.name!=='AbortError')fail(error,'load');}updateControls();});return lifecyclePromise;
}
function sampleGlError(rt){
  const gl=rt.renderer.getContext();rt.glErrors??=[];
  for(let i=0;i<16;i++){const code=gl.getError();if(code===gl.NO_ERROR)break;rt.glErrors.push({code,at:new Date().toISOString()});recordError(new Error('WebGL error '+code),'webgl');}
  return rt.glErrors[0]?.code??0;
}
function report(){const rt=runtime,gl=rt?.renderer.getContext(),debug=gl?.getExtension('WEBGL_debug_renderer_info'),frames=(rt?.frameMs||[]).slice().sort((a,b)=>a-b);return {schemaVersion:2,at:new Date().toISOString(),status:state,view:currentView,source:{requestedLod:selectedLod,lod:rt?.ready?rt.asset.lod:null,sha256:rt?.ready?stats.assetSha:null,count:rt?.ready?rt.mesh.numSplats:0,bytes:rt?.ready?rt.asset.bytes:0,expectedCount:manifest?.assets?.[selectedLod]?.count??null,expectedBytes:manifest?.assets?.[selectedLod]?.bytes??null,transportBytes:rt?.asset?.transport.bytes??null},dependencies:{three:THREE.REVISION,spark:'2.3.1'},comparison:manifest?.comparison,renderSettings:rt?{toneMapping:rt.renderer.toneMapping,exposure:rt.renderer.toneMappingExposure,outputColorSpace:rt.renderer.outputColorSpace,enableLod:rt.spark?.enableLod,enableDriveLod:rt.spark?.enableDriveLod,autoUpdate:rt.spark?.autoUpdate,accumExtSplats:rt.spark?.accumExtSplats,meshScale:rt.mesh?.scale.toArray(),meshPosition:rt.mesh?.position.toArray(),meshQuaternion:rt.mesh?.quaternion.toArray()}:null,viewport:rt?{width:innerWidth,height:innerHeight,dpr:devicePixelRatio,drawingWidth:gl.drawingBufferWidth,drawingHeight:gl.drawingBufferHeight}:null,cadence:cadenceReport(rt),storage:storageReport(rt),lifecycle:{activeLods:rt?.ready?[rt.asset.lod]:[],allocatedMeshLods:rt?.mesh?[rt.asset.lod]:[],meshCountInScene:rt?rt.scene.children.filter(x=>x instanceof SplatMesh).length:0,quarantined:!!rt?.quarantined,pendingLod:state==='loading'?selectedLod:null},camera:rt?{position:rt.camera.position.toArray(),quaternion:rt.camera.quaternion.toArray(),fov:rt.camera.fov,near:rt.camera.near,far:rt.camera.far,aspect:rt.camera.aspect,projectionMatrix:rt.camera.projectionMatrix.toArray()}:null,draw:rt?{...rt.draw,activeSplats:rt.spark.activeSplats,instanceCount:rt.spark.geometry.instanceCount,rendererInfo:{...rt.renderer.info.render}}:null,gl:rt?{version:rt.renderer.getContext().getParameter(rt.renderer.getContext().VERSION),renderer:gl.getParameter(gl.RENDERER),unmaskedRenderer:debug?gl.getParameter(debug.UNMASKED_RENDERER_WEBGL):null,unmaskedVendor:debug?gl.getParameter(debug.UNMASKED_VENDOR_WEBGL):null,isContextLost:rt.renderer.getContext().isContextLost(),error:sampleGlError(rt),errorHistory:[...(rt.glErrors||[])]}:null,stats:{...stats,frameMs:undefined,frameWorkMedianMs:frames.length?frames[Math.floor(frames.length*.5)]:null,frameWorkP95Ms:frames.length?frames[Math.floor(frames.length*.95)]:null},errors:[...errors],history:[...history],captures:[...reports],visualAcceptance:'NOT_AUTOMATIC: actual side/back/low screenshots and reviewer judgement required',performanceNote:'frameWork includes awaited Spark update; not FPS. cadence.render tracks actual render submissions; cadence.raf is a separate RAF monitor. Neither is GPU presentation FPS or proof of client performance.'};}
async function captureEvidence(name=currentView){
  const rt=runtime;if(!rt?.mesh||rt.stopping||rt.capturing)throw new Error('数据尚不可采样或已有采样进行中');
  rt.capturing=true;cancelAnimationFrame(frameHandle);frameHandle=0;
  const previousFrame=framePromise;
  const capture=previousFrame.then(async()=>{
    if(runtime!==rt||rt.stopping)throw new Error('采样已取消：场景正在卸载');
    rt.camera.rotation.set(pitch,yaw,0,'YXZ');rt.scene.updateMatrixWorld(true);rt.camera.updateMatrixWorld(true);
    await boundedOperation(rt.spark.update({scene:rt.scene,camera:rt.camera}),10000,rt,'Gaussian GPU 更新');rt.dirty=false;
    if(runtime!==rt||rt.stopping)throw new Error('采样已取消：场景正在卸载');
    const wasVisible=rt.guides.visible;rt.guides.visible=false;
    try{rt.renderer.render(rt.scene,rt.camera);registerRender(rt);const gl=rt.renderer.getContext(),w=gl.drawingBufferWidth,h=gl.drawingBufferHeight,pixels=new Uint8Array(w*h*4);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,pixels);const background=[21,25,32];let changed=0;for(let i=0;i<pixels.length;i+=4)if(Math.max(Math.abs(pixels[i]-background[0]),Math.abs(pixels[i+1]-background[1]),Math.abs(pixels[i+2]-background[2]))>12)changed++;
      const result={name,lod:rt.asset.lod,sourceSha256:stats.assetSha,sourceBytes:rt.asset.bytes,sourceCount:rt.mesh.numSplats,at:new Date().toISOString(),width:w,height:h,nonBackgroundPixels:changed,coverage:changed/(w*h),guidesHidden:true,draw:{...rt.draw},activeSplats:rt.spark.activeSplats,glError:sampleGlError(rt),camera:rt.camera.position.toArray(),quaternion:rt.camera.quaternion.toArray(),note:'Coverage is a non-background pixel diagnostic, never evidence of completeness or visual quality.'};reports.push(result);return result;
    }finally{rt.guides.visible=wasVisible;if(!rt.stopping){rt.renderer.render(rt.scene,rt.camera);registerRender(rt);}}
  });
  // Teardown waits for this same serialized GPU operation, never disposes mid-capture.
  framePromise=capture;try{return await capture;}finally{rt.capturing=false;if(runtime===rt&&!rt.stopping)schedule();}
}
function downloadReport(){const blob=new Blob([JSON.stringify(report(),null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='reef-splat-gpu-report.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}

listen(window,'resize',resize);listen(window,'blur',()=>{keys.clear();drag=null;});listen(document,'visibilitychange',()=>{keys.clear();drag=null;lastTime=0;});
listen(window,'keydown',e=>{if(e.target.closest?.('button,summary,a,input,textarea'))return;if(['KeyW','KeyS','KeyA','KeyD','KeyQ','KeyE','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','ShiftLeft','ShiftRight'].includes(e.code)){e.preventDefault();keys.add(e.code);}});
listen(window,'keyup',e=>keys.delete(e.code));
listen(canvas,'pointerdown',e=>{if(e.button!==0)return;canvas.focus();drag={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
listen(canvas,'pointermove',e=>{if(drag?.id!==e.pointerId||!runtime)return;yaw-=(e.clientX-drag.x)*.003;pitch=Math.max(-1.48,Math.min(1.48,pitch-(e.clientY-drag.y)*.003));drag.x=e.clientX;drag.y=e.clientY;runtime.dirty=true;currentView='free';});
for(const event of ['pointerup','pointercancel','lostpointercapture'])listen(canvas,event,()=>{drag=null;});
for(const button of document.querySelectorAll('[data-key]')){listen(button,'pointerdown',e=>{e.preventDefault();button.setPointerCapture(e.pointerId);keys.add(button.dataset.key);});for(const event of ['pointerup','pointercancel','lostpointercapture'])listen(button,event,()=>keys.delete(button.dataset.key));}
for(const button of document.querySelectorAll('[data-view]'))listen(button,'click',()=>{setView(button.dataset.view);canvas.focus();});
listen($('guides'),'click',()=>{guides=!guides;if(runtime)runtime.guides.visible=guides;$('guides').setAttribute('aria-pressed',String(guides));$('guides').textContent=`范围标记：${guides?'开':'关'}`;});
for(const button of document.querySelectorAll('[data-lod]'))listen(button,'click',()=>void load(Number(button.dataset.lod)));
listen($('unload'),'click',()=>void unload());listen($('reload'),'click',()=>void load());listen($('retry'),'click',()=>{if(runtime?.quarantined||stats.contextLosses)location.reload();else void load();});listen($('export'),'click',downloadReport);
listen(canvas,'webglcontextlost',e=>{e.preventDefault();epoch++;aborter?.abort();stats.contextLosses++;if(runtime)runtime.quarantined=true;recordError(new Error('WebGL context lost'),'context');if(runtime)runtime.stopping=true;cancelAnimationFrame(frameHandle);frameHandle=0;fail(new Error('图形上下文丢失。停止检查；刷新页面后再试。'),'context-stop');});
listen(window,'pagehide',()=>{void unload();});
listen(window,'unhandledrejection',e=>{recordError(e.reason,'unhandled-promise');});
window.reefProbe={report,load,unload,setView,switchLod:load,captureEvidence,downloadReport,getState:()=>state,get manifest(){return manifest;}};
const response=await fetch('./assets/manifest.json');if(!response.ok)throw new Error('缺少扫描 metadata');manifest=await response.json();updateControls();await load(4);
