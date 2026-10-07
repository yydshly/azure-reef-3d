import assert from 'node:assert/strict';import * as T from 'three';import {OrbitControls} from './dist/vendor/OrbitControls.js';import {SpecimenFocus} from './dist/specimen-focus.js';
const c=new T.PerspectiveCamera(47,1.6,.12,140);c.position.set(1.5,2.1,4.8);const controls=new OrbitControls(c,null);Object.assign(controls,{minDistance:3.2,maxDistance:30,minPolarAngle:.2,maxPolarAngle:Math.PI*.485,enablePan:true,enableDamping:true});controls.target.set(-.5,.8,-6);controls.update();
const start=c.position.clone(),target=controls.target.clone(),focus=new SpecimenFocus(c,controls);
// Synthetic unobstructed pose only: actual habitat pose is verified separately.
const conf={position:[.6,.8,.6],target:[0,.1,0],limits:{minDistance:.85,maxDistance:1.6,minPolarAngle:.3,maxPolarAngle:Math.PI/3}};
assert.equal(focus.enter(conf),true);assert.equal(focus.enter(conf),false);assert.equal(controls.minDistance,.85);assert.equal(controls.enablePan,false);assert.equal(c.near,.01);assert.equal(focus.active,true);
assert.equal(focus.exit(),true);assert.equal(focus.exit(),false);assert.ok(c.position.distanceTo(start)<1e-10);assert.ok(controls.target.distanceTo(target)<1e-10);assert.equal(c.near,.12);assert.equal(controls.minDistance,3.2);assert.equal(controls.maxDistance,30);assert.equal(controls.enablePan,true);assert.equal(controls.enableDamping,true);
for(let n=0;n<5;n++){focus.enter(conf);focus.exit();}assert.ok(c.position.distanceTo(start)<1e-10);
console.log('PASS focus state restores original camera/controls/clip plane, idempotent entry/exit and repeat cycles. Synthetic pose; not habitat clearance or pixel evidence.');
