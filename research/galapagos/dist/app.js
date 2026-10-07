import * as THREE from 'three';
import {OrbitControls} from './vendor/OrbitControls.js';
import {GLTFLoader} from './vendor/GLTFLoader.js';
import {MODEL_URL} from './model-version.js';
const canvas=document.querySelector('#scene'),loading=document.querySelector('#loading'),error=document.querySelector('#error');
let renderer,camera,controls,root,points,surface,ready=false,mode='surface',span=1;
function fail(message){ready=false;loading.hidden=true;error.hidden=false;error.textContent=message;document.querySelectorAll('button').forEach(b=>b.disabled=true)}
function setMode(value){if(!ready||!['points','surface'].includes(value))return;mode=value;points.visible=value==='points';surface.visible=value==='surface';document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)))}
function setView(value){if(!ready)return;const directions={front:[.9,.8,1.1],reverse:[-.9,.7,-1.1],top:[.02,1.9,.02]};if(!directions[value])return;controls.target.set(0,0,0);camera.position.set(...directions[value]).multiplyScalar(span);controls.update();camera.updateMatrixWorld()}
function layout(){if(!renderer)return;camera.aspect=innerWidth/innerHeight;camera.setViewOffset(innerWidth,innerHeight,innerWidth>800?innerWidth*.1:0,innerWidth<=550?innerHeight*.12:0,innerWidth,innerHeight);camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)}
async function start(){try{
const gl=canvas.getContext('webgl2',{alpha:false,antialias:true});if(!gl){fail('此浏览器未能启动 WebGL2，研究模型没有显示。请使用可用的三维浏览器；没有用图片替代交互模型。');return}
renderer=new THREE.WebGLRenderer({canvas,context:gl,antialias:true,alpha:false});renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.NoToneMapping;
const scene=new THREE.Scene();scene.background=new THREE.Color('#17262d');camera=new THREE.PerspectiveCamera(45,innerWidth/innerHeight,.005,100);controls=new OrbitControls(camera,canvas);controls.enableDamping=true;controls.dampingFactor=.08;controls.minPolarAngle=.02;controls.maxPolarAngle=Math.PI-.02;
root=(await new GLTFLoader().loadAsync(MODEL_URL)).scene;points=root.getObjectByName('Source_points');surface=root.getObjectByName('Reconstructed_surface');if(!points||!surface)throw Error('Required source and surface objects are absent');
const box=new THREE.Box3().setFromObject(root),center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());span=Math.max(size.x,size.y,size.z);if(!Number.isFinite(span)||span<=0)throw Error('Invalid model bounds');root.position.sub(center);scene.add(root);
// Display transform only: geometry remains in the attributed source-derived GLB.
root.traverse(o=>{if(o.isPoints){o.material.size=span*.004;o.material.sizeAttenuation=true;}if(o.isMesh){o.material.side=THREE.FrontSide;}});
controls.minDistance=span*.28;controls.maxDistance=span*4;controls.maxTargetRadius=span;camera.near=Math.max(.002,span/1500);camera.far=span*30;ready=true;loading.hidden=true;setMode('surface');setView('front');layout();
window.reefResearch={scene,camera,controls,root,setMode,setView,getState:()=>({ready,mode,sourcePoints:points.geometry?.attributes.position.count??0,surfaceTriangles:surface.geometry?.index?surface.geometry.index.count/3:(surface.geometry?.attributes.position.count??0)/3,camera:camera.position.toArray(),target:controls.target.toArray(),pointVisible:points.visible,surfaceVisible:surface.visible,frontFacesOnly:surface.material.side===THREE.FrontSide})};
function loop(){if(ready){controls.update();renderer.render(scene,camera)}requestAnimationFrame(loop)}requestAnimationFrame(loop);
}catch(e){console.error('Research scene load failed',e);fail('研究样本加载失败。模型、源数据与重建记录仍需完整核对后才能展示。')}}
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>setMode(b.dataset.mode));document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>setView(b.dataset.view));window.addEventListener('resize',layout);
canvas.addEventListener('keydown',e=>{if(!ready)return;const s=new THREE.Spherical().setFromVector3(camera.position.clone().sub(controls.target));let used=true;switch(e.key){case'ArrowLeft':s.theta-=.12;break;case'ArrowRight':s.theta+=.12;break;case'ArrowUp':s.phi-=.08;break;case'ArrowDown':s.phi+=.08;break;case'+':case'=':s.radius*=.9;break;case'-':s.radius*=1.1;break;default:used=false}if(used){e.preventDefault();s.phi=THREE.MathUtils.clamp(s.phi,.02,Math.PI-.02);s.radius=THREE.MathUtils.clamp(s.radius,controls.minDistance,controls.maxDistance);camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(s));controls.update()}});
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();fail('图形上下文已中断；当前没有可验证的实时画面。请重新载入。')});
start();
