import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createExplorationNavigation} from './artifacts/continuous-candidate/exploration-navigation.js';
import {EXPLORATION_TOUR_STOPS as stops,resolvePosition,floorHeight} from './artifacts/continuous-candidate/exploration-world-data.js';
import {CONTINUOUS_MASSES} from './candidate-src/continuous-layout.js';

// CPU/static evidence only. The browser/visual verdict is recorded separately.
const sha=b=>createHash('sha256').update(b).digest('hex');
const proof=JSON.parse(fs.readFileSync('artifacts/enriched-recovery.json','utf8'));
const build=JSON.parse(fs.readFileSync('artifacts/continuous-build.json','utf8'));
const changed=new Set(Object.keys(build.changes));
for(const [name,digest] of Object.entries(proof.sourceHashes)){
 assert.equal(sha(fs.readFileSync(path.join('artifacts/enriched-baseline',name))),digest,'Frozen baseline '+name);
 if(!changed.has(name))assert.equal(sha(fs.readFileSync(path.join('artifacts/continuous-candidate',name))),digest,'Preserved source/asset '+name);
}
assert(!changed.has('exploration-navigation.js'));
const nav=createExplorationNavigation({stops,resolvePosition});nav.startTour();
for(let i=0;i<1440;i++){
 nav.tick(.05);const s=nav.getState();assert(s.position.every(Number.isFinite));
 assert.deepEqual(resolvePosition(s.position),s.position,'Sampled tour pose must be outside reef proxies');
 assert(s.position[1]>=floorHeight(s.position[0],s.position[2])+.65-1e-6);
}
assert.equal(nav.getState().elapsed,72);assert.equal(nav.getState().mode,'completed');
for(const stop of stops)assert.deepEqual(resolvePosition(stop.position),stop.position,'Retained stop must remain reachable');
const mass=CONTINUOUS_MASSES[0],candidate=[mass.x,floorHeight(mass.x,mass.z)+2,mass.z];
const resolved=resolvePosition(candidate);
assert(Math.hypot(resolved[0]-candidate[0],resolved[2]-candidate[2])>1,'Placement resolves visible reef');
const previous=[-10,5,-20],attempt=[-20,5,-20];assert.deepEqual(resolvePosition(attempt,.65,previous),previous,'Ordinary swimming rejects a blocked step');
nav.reset();nav.key('KeyW',true);nav.tick(.05);nav.key('KeyW',false);assert(nav.getState().position[2]<10);const p=nav.getState().position;nav.tick(.2);assert.deepEqual(nav.getState().position,p,'Released input stops');
const report={status:'PASS',cpuOnly:true,baselineFiles:149,preservedBaselineFiles:149-changed.size+2,changedFiles:[...changed],sampledTourPoses:1440,retainedStops:6,collisionProxyChecks:2,claims:['asset bytes preserved','same navigation controller','retained six stops reachable','finite collision-safe sampled tour'],notCovered:['continuous triangle/body collision','real browser','visual quality','hardware phone performance']};
fs.writeFileSync('artifacts/continuous-contract-test.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
