import fs from 'node:fs';
import assert from 'node:assert/strict';
import {GLTFLoader} from './dist/vendor/GLTFLoader.js';
import * as T from 'three';
import {sampleSwimRoute} from './dist/fish-motion.js';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {loadImage}=require('@napi-rs/canvas');
globalThis.self=globalThis;
globalThis.createImageBitmap=async blob=>loadImage(Buffer.from(await blob.arrayBuffer()));
const b=fs.readFileSync(process.env.REEF_MODEL_PATH||'source-model.glb');
const {scene:s}=await new Promise((r,j)=>new GLTFLoader().parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'',r,j));
const fish=[],terrain=[];
s.traverse(o=>{if(/^fish_\d+$/.test(o.name))fish.push(o);if(o.isMesh&&!/^fish_/.test(o.name))terrain.push(o)});
s.updateMatrixWorld(true);
const savedRoutes=JSON.parse(fs.readFileSync('dist/assets/swim-routes.json','utf8'));
// Three user-facing presets plus an attainable low lateral orbit view.
const cameras=[[1.5,1.6,4.8],[-8,3.7,-11],[1.6,1.8,5.8],[6,1.1,5]];
const results=[];
for(let i=0;i<fish.length;i++){
 const saved=savedRoutes.find(r=>r.name===fish[i].name);
 const curve=new T.CatmullRomCurve3(saved.points.map(p=>new T.Vector3(...p)),true,'centripetal');
 curve.arcLengthDivisions=280;curve.updateArcLengths();
 let min=Infinity,maxStep=0,last=null,hidden=0;
 // Cover each complete period. This is sampled geometry QA, not continuous collision detection.
 for(let t=0;t<37+i*4.5;t+=.5){
  const pose=sampleSwimRoute(curve,t,i);
  const ray=new T.Raycaster(new T.Vector3(pose.position.x,9,pose.position.z),new T.Vector3(0,-1,0),0,11);
  const hit=ray.intersectObjects(terrain,false)[0];
  if(hit)min=Math.min(min,pose.position.y-hit.point.y);
  if(last)maxStep=Math.max(maxStep,pose.position.distanceTo(last));
  last=pose.position;
  for(const position of cameras){
   const camera=new T.Vector3(...position);
   const r=new T.Raycaster(camera,pose.position.clone().sub(camera).normalize(),.1,pose.position.distanceTo(camera)-.15);
   if(r.intersectObjects(terrain,false).length)hidden++;
  }
  assert.ok(Number.isFinite(pose.quaternion.w));
  assert.ok(Math.abs(pose.quaternion.length()-1)<.0001);
 }
 results.push({fish:fish[i].name,minCenterClearance:min,maxStepPer05Seconds:maxStep,occludedSamplesAcrossFourViews:hidden});
 assert.ok(min>.18,fish[i].name+' center clearance: '+min);
 assert.ok(maxStep<.55,'No position jumps');
}
console.log(JSON.stringify(results,null,2));
assert.ok(results.some(r=>r.occludedSamplesAcrossFourViews>0),'Coral occlusion retained');
