import fs from 'node:fs';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';import {createRequire} from 'node:module';import * as T from 'three';import {GLTFLoader} from './dist/vendor/GLTFLoader.js';import {SPECIMEN,placeSpecimen} from './dist/specimen.js';import {applyWaterLight} from './dist/water-light.js';
const require=createRequire(import.meta.url),{loadImage}=require('@napi-rs/canvas');globalThis.self=globalThis;globalThis.createImageBitmap=async b=>loadImage(Buffer.from(await b.arrayBuffer()));
const b=fs.readFileSync('dist/'+SPECIMEN.url.slice(2));
const gltf=await new Promise((r,j)=>new GLTFLoader().parse(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'',r,j));const root=new T.Group(),g=placeSpecimen(root,gltf.scene);g.updateMatrixWorld(true);
const results=[];
for(const [w,h] of [[1120,700],[1440,900],[390,844],[700,900],[320,568]])for(const az of [25,205]){
 const camera=new T.PerspectiveCamera(47,w/h,.01,140),target=new T.Vector3(...SPECIMEN.focus.target);
 camera.position.copy(target).add(new T.Vector3().setFromSpherical(new T.Spherical(.85,Math.PI/3,az*Math.PI/180)));camera.lookAt(target);camera.setViewOffset(w,h,w>700?w*.12:0,w<=700?h*.18:0,w,h);camera.updateMatrixWorld(true);
 let min=[Infinity,Infinity],max=[-Infinity,-Infinity];g.traverse(o=>{if(!o.isMesh)return;const a=o.geometry.attributes.position;for(let i=0;i<a.count;i++){const p=new T.Vector3().fromBufferAttribute(a,i).applyMatrix4(o.matrixWorld).project(camera);const xy=[(p.x+1)*w/2,(1-p.y)*h/2];for(let j=0;j<2;j++){min[j]=Math.min(min[j],xy[j]);max[j]=Math.max(max[j],xy[j]);}}});
 assert.ok(min[0]>=0&&min[1]>=0&&max[0]<=w&&max[1]<=h,'Object clipped');
 if(w<=700)assert.ok(max[1]<h*.56-18,'Specimen enters maximum-height compact guide card');
 results.push({viewport:[w,h],azimuth:az,pixelBounds:{min,max},scope:'Projection only; DOM overlay and native touch not tested'});
}
fs.writeFileSync('evidence/skeletal-patch-oct7/projection-check.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results));
