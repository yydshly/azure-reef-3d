import fs from 'node:fs';import assert from 'node:assert/strict';import*as T from'three';import{GLTFLoader}from'../../../dist/vendor/GLTFLoader.js';import{composeReef,REEF_LAYOUT,applySubstrateLink,RETAINED_NEAR_BRANCHES}from'../../../dist/inhabited-reef.js';import{applyWaterLight}from'../../../dist/water-light.js';import{samplePassage}from'../../../dist/passage.js';import{createRequire}from'node:module';const require=createRequire(import.meta.url);const{loadImage}=require('@napi-rs/canvas');globalThis.self=globalThis;globalThis.createImageBitmap=async b=>loadImage(Buffer.from(await b.arrayBuffer()));
async function load(p){const b=fs.readFileSync(new URL(p,import.meta.url));return(await new Promise((r,j)=>new GLTFLoader().parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'',r,j))).scene}
const root=await load('../../../source-model.glb'),asset=await load('../../../dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb');const sand=[];root.traverse(o=>{if(o.isMesh&&o.name.startsWith('Sand'))sand.push({o,g:o.geometry,m:o.material})});const fish=[];root.traverse(o=>{if(/^fish_\d+$/.test(o.name))fish.push({o,m:o.matrix.toArray()})});composeReef(root,asset);

const results=[];
for(const progress of [.67,.75,.92]){
 const pose=samplePassage(progress),camera=new T.PerspectiveCamera(47,1120/700,.12,140);camera.position.copy(pose.p);camera.lookAt(pose.t);camera.updateMatrixWorld(true);
 const points=[],counts={};
 for(let sy=240;sy<=560;sy+=20)for(let sx=20;sx<1120;sx+=20){
  const ray=new T.Raycaster();ray.setFromCamera(new T.Vector2(sx/560-1,1-sy/350),camera);ray.far=90;
  const hit=ray.intersectObject(root,true)[0];if(!hit)continue;counts[hit.object.name]=(counts[hit.object.name]??0)+1;
  if(hit.object.name==='Spatial_Continuous_Weathered_Limestone')points.push({screen:[sx,sy],point:hit.point.toArray(),face:hit.faceIndex});
 }
 results.push({progress,camera:pose.p.toArray(),target:pose.t.toArray(),counts,visibleTargetPoints:points});
}
fs.writeFileSync(process.argv[2]||'visible-bank-rays.json',JSON.stringify({scope:'Source ray intersection on accepted geometry. Does not include water haze, texture perception or raster antialiasing. UI top/bottom excluded.',pixelGrid:20,results},null,2));console.log(JSON.stringify(results.map(r=>({progress:r.progress,targetHits:r.visibleTargetPoints.length,bounds:r.visibleTargetPoints.length?[0,1,2].map(k=>[Math.min(...r.visibleTargetPoints.map(p=>p.point[k])),Math.max(...r.visibleTargetPoints.map(p=>p.point[k]))]):null,objects:r.counts})),null,2));
