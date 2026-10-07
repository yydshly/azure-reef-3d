import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as T from 'three';
import {TourClock,advanceTourPose,TOUR_STALL_SECONDS} from './dist/tour-clock.js';
import {samplePassage,PASSAGE_SECONDS} from './dist/passage.js';
function run(hz,direction=1){
 const clock=new TourClock();clock.start(0);let progress=direction>0?0:1;
 const first=samplePassage(progress,direction),camera=first.p.clone(),target=first.t.clone();
 let now=0,last=0,maxSpeed=0;
 while(now<30000){now=Math.min(30000,now+1000/hz);const before=camera.clone(),seconds=clock.tick(now);progress=advanceTourPose({progress,direction,seconds,duration:PASSAGE_SECONDS,camera,target,sample:samplePassage});maxSpeed=Math.max(maxSpeed,camera.distanceTo(before)/((now-last)/1000));last=now;}
 assert.ok(Math.abs(progress-(direction>0?.3:.7))<1e-9,'phase follows visible seconds');
 assert.ok(!clock.interrupted);return {hz,direction,seconds:now/1000,progress,camera:camera.toArray(),target:target.toArray(),maxSpeed};
}
const samples=[1,-1].flatMap(d=>[60,15,1,.3].map(hz=>run(hz,d)));
for(const d of [1,-1]){const baseline=samples.find(s=>s.direction===d&&s.hz===60);for(const s of samples.filter(s=>s.direction===d)){assert.ok(new T.Vector3(...s.camera).distanceTo(new T.Vector3(...baseline.camera))<.002);assert.ok(new T.Vector3(...s.target).distanceTo(new T.Vector3(...baseline.target))<.002);}}
const clock=new TourClock();clock.start(0);assert.equal(clock.tick(3000),3);clock.sync(500000);assert.equal(clock.tick(500040),.04);clock.pause();assert.equal(clock.tick(800000),0);clock.start(900000);assert.equal(clock.tick(900060),.06);assert.equal(clock.tick(920000),0);assert.equal(clock.interrupted,true);assert.equal(clock.running,false);clock.start(1000000);assert.equal(clock.tick(1000060),.06);assert.equal(clock.interrupted,false);
// Endpoint integration is clamped, including a late frame spanning the end.
for(const direction of [1,-1]){const p=direction>0?.999:.001,pose=samplePassage(p,direction);assert.equal(advanceTourPose({progress:p,direction,seconds:4,duration:100,camera:pose.p,target:pose.t,sample:samplePassage}),direction>0?1:0);}
const report={scope:'Pure clock and camera follower source tests, not browser or frame-rate evidence',stallThresholdSeconds:TOUR_STALL_SECONDS,samples,pausedHiddenResume:'passed',longStall:'pauses without catch-up',endpoints:'passed'};
fs.mkdirSync('evidence/tour-clock-oct7',{recursive:true});fs.writeFileSync('evidence/tour-clock-oct7/clock-checks.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
