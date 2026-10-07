import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
import * as T from './dist/vendor/three.module.js';
import {GLTFLoader} from './dist/vendor/GLTFLoader.js';
const modelPath=process.argv[2];if(!modelPath)throw Error('Pass the frozen GLB path');
const bytes=fs.readFileSync(modelPath),loaded=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
const points=loaded.scene.getObjectByName('Source_points'),surface=loaded.scene.getObjectByName('Reconstructed_surface');
assert.ok(points?.isPoints);assert.ok(surface?.isMesh);assert.ok(surface.material.isMeshBasicMaterial);assert.equal(points.geometry.attributes.position,surface.geometry.attributes.position);assert.equal(points.geometry.attributes.color,surface.geometry.attributes.color);assert.ok(surface.geometry.index.count>0);const positions=points.geometry.attributes.position.array.slice();
async function run(hasGL){
 const elements=new Map(),modes=[],views=[],buttons=[];
 function element(){return {hidden:false,textContent:'',disabled:false,attrs:{},listeners:{},dataset:{},setAttribute(k,v){this.attrs[k]=v},addEventListener(k,v){this.listeners[k]=v}}}
 function q(s){if(!elements.has(s))elements.set(s,element());return elements.get(s)}
 for(const m of ['surface','points']){const b=element();b.dataset.mode=m;modes.push(b);buttons.push(b)}
 for(const v of ['front','reverse','top']){const b=element();b.dataset.view=v;views.push(b);buttons.push(b)}
 q('#scene').getContext=()=>hasGL?{}:null;
 class Renderer{setPixelRatio(){}setSize(){}render(){}}
 class Controls{constructor(camera){this.camera=camera;this.target=new T.Vector3()}update(){this.camera.lookAt(this.target);this.camera.updateMatrixWorld()}}
 let raf;
 const ctx={THREE:{...T,WebGLRenderer:Renderer},OrbitControls:Controls,GLTFLoader:class{async loadAsync(){return loaded}},MODEL_URL:'sample.glb',console,document:{querySelector:q,querySelectorAll:s=>s==='[data-mode]'?modes:s==='[data-view]'?views:buttons},window:{addEventListener(){}},innerWidth:1120,innerHeight:700,devicePixelRatio:1,requestAnimationFrame:f=>raf=f};vm.createContext(ctx);vm.runInContext(fs.readFileSync('dist/app.js','utf8').replace(/^import .*;\n/gm,''),ctx);await new Promise(r=>setTimeout(r,10));
 if(!hasGL){assert.equal(q('#error').hidden,false);assert.ok(q('#error').textContent.includes('WebGL2'));assert.ok(buttons.every(b=>b.disabled));assert.equal(ctx.window.reefResearch,undefined);return}
 const app=ctx.window.reefResearch;assert.ok(app.getState().ready);assert.equal(app.getState().mode,'surface');assert.equal(app.getState().pointVisible,false);assert.equal(app.getState().surfaceVisible,true);assert.equal(app.getState().frontFacesOnly,true);
 modes[1].onclick();assert.equal(app.getState().mode,'points');assert.equal(app.getState().surfaceVisible,false);assert.equal(modes[1].attrs['aria-pressed'],'true');
 modes[0].onclick();assert.equal(app.getState().pointVisible,false);assert.equal(app.getState().surfaceVisible,true);
 const front=app.camera.position.clone();views[1].onclick();assert.ok(front.distanceTo(app.camera.position)>1);views[2].onclick();assert.ok(app.camera.position.y>Math.abs(app.camera.position.x));
 let prevented=false;q('#scene').listeners.keydown({key:'ArrowLeft',preventDefault(){prevented=true}});assert.ok(prevented);
 assert.deepEqual(points.geometry.attributes.position.array,positions);q('#scene').listeners.webglcontextlost({preventDefault(){}});assert.equal(app.getState().ready,false);assert.ok(buttons.every(b=>b.disabled));assert.equal(q('#error').hidden,false);
}
await run(true);await run(false);
console.log('PASS: real GLB import; shared source/surface positions and colors; unlit surface; exclusive mode controls, camera presets/keyboard, source positions unchanged, context-loss and no-WebGL states. Simulated DOM/renderer only; not browser pixel acceptance.');
