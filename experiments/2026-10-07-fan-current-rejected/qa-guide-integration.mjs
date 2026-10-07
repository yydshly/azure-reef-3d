import {seaFanAmplitude} from './dist/sea-fan-current.js';
import {SpecimenFocus} from './dist/specimen-focus.js';
import {SPECIMEN,SPECIMEN_LESSON} from './dist/specimen.js';
import {TourClock,advanceTourPose} from './dist/tour-clock.js';
import {composeReef,applySubstrateLink} from './dist/inhabited-reef.js';
import {addCompanionFish} from './dist/fish-population.js';
import {PASSAGE_STOPS,samplePassage,nearestPassageProgress,PASSAGE_SECONDS} from './dist/passage.js';
import {MODEL_URL} from './dist/model-version.js';
import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';import * as T from 'three';import {GUIDE_STOPS,GuideJourney} from './dist/guide-data.js';import {sampleSwimRoute} from './dist/fish-motion.js';import {applyWaterLight,createWaterEnvelope} from './dist/water-light.js';
const els=new Map(),viewButtons=[],guideButtons=[];const make=()=>({hidden:false,disabled:false,open:false,textContent:'',style:{},attrs:{},dataset:{},listeners:{},classList:{toggle(){}},setAttribute(k,v){this.attrs[k]=v},addEventListener(k,fn){this.listeners[k]=fn},appendChild(c){guideButtons.push(c)}});const $=s=>{if(!els.has(s))els.set(s,make());return els.get(s)};for(let i=0;i<3;i++){const e=make();e.dataset.view=i;viewButtons.push(e)}$('#reef').getContext=()=>({});const root=new T.Group();for(let i=1;i<=4;i++){let f=new T.Group();f.name='fish_0'+i;f.position.set(i-2,1.4,0);root.add(f)}for(const name of ['Corridor_Distant_Linked_00','Distant_Limestone_Support_00']){const o=new T.Object3D();o.name=name;root.add(o)}class Renderer{constructor(){this.shadowMap={}}setPixelRatio(){}setSize(){}render(){}}class Controls{constructor(camera){this.target=new T.Vector3();this.camera=camera;this.listeners={}}addEventListener(k,f){this.listeners[k]=f}update(){this.listeners.change?.();this.camera.lookAt(this.target);this.camera.updateMatrixWorld()}}let raf,clockNow=0;const events={};const fakeAsset=new T.Group();for(const name of ['Shoulder_closed_irregular_skeleton','Attached_reticulate_fan_form','Attached_small_fan_form']){const m=new T.Mesh(new T.BoxGeometry(),new T.MeshStandardMaterial());m.name=name;fakeAsset.add(m)}const addShoulder=async r=>{composeReef(r,fakeAsset);return {substrateTexture:new T.Texture()}};let refinementCalls=0;const refineFish03=()=>{refinementCalls++;}; // Geometry is independently checked against actual GLTF resources.
const addSpecimen=async r=>{const g=new T.Group();g.name='Teaching_CoralSkeleton_USNM74016';r.add(g);return g};
// This fixture isolates app clock wiring; actual fan geometry/shaders are tested separately.
const installSeaFanCurrent=()=>{let amplitude=0;return{update:t=>{amplitude=seaFanAmplitude(t)},getState:()=>({amplitude})}};
const context={installSeaFanCurrent,SpecimenFocus,SPECIMEN,SPECIMEN_LESSON,addSpecimen,TourClock,advanceTourPose,refineFish03,addShoulder,applySubstrateLink,addCompanionFish,PASSAGE_STOPS,samplePassage,nearestPassageProgress,PASSAGE_SECONDS,MODEL_URL,THREE:{...T,WebGLRenderer:Renderer,TextureLoader:class{async loadAsync(){return new T.Texture()}}},OrbitControls:Controls,GLTFLoader:class{async loadAsync(){return {scene:root}}},GUIDE_STOPS,GuideJourney,sampleSwimRoute,applyWaterLight,createWaterEnvelope,console,document:{body:{classList:{toggle(){}}},querySelector:$,querySelectorAll:s=>s==='[data-view]'?viewButtons:s==='[data-guide]'?guideButtons:[],createElement:make,addEventListener:(name,fn)=>events[name]=fn,hidden:false},window:{addEventListener(){}},matchMedia:()=>({matches:process.env.REEF_REDUCED_MOTION==='1'}),innerWidth:1280,innerHeight:800,devicePixelRatio:1,requestAnimationFrame:f=>raf=(now)=>{clockNow=now;f(now)},performance:{now:()=>clockNow},fetch:async()=>({ok:true,json:async()=>JSON.parse(fs.readFileSync('dist/assets/swim-routes.json'))}),setTimeout};vm.createContext(context);let src=fs.readFileSync('dist/app.js','utf8').replace(/^import .*;\n/gm,'');vm.runInContext(src,context);await new Promise(r=>setTimeout(r,10));const app=context.window.reef3d;assert.ok(app);assert.equal(refinementCalls,1,'one refinement call after companion setup');$('#quality').onclick();assert.equal(app.getState().low,true);assert.equal(root.getObjectByName('Corridor_Distant_Linked_00').visible,false);assert.equal(root.getObjectByName('Distant_Limestone_Support_00').visible,false);assert.equal(root.getObjectByName('Inhabited_Middle_Attached_small_fan_form').visible,false);$('#quality').onclick();assert.equal(app.getState().low,false);assert.equal(root.getObjectByName('Corridor_Distant_Linked_00').visible,true);assert.equal(root.getObjectByName('Inhabited_Middle_Attached_small_fan_form').visible,true);assert.equal(app.getState().guide.index,0);assert.ok($('#guideTitle').textContent.includes('这片浅海'));$('#guideNext').onclick();assert.equal(app.getState().guide.index,1);assert.equal($('#guideSource').href,GUIDE_STOPS[1].url);$('#guidePlay').onclick();assert.equal(app.getState().guide.playing,true);for(let i=0;i<80;i++)raf(i*33);assert.equal($('#focusMarker span').textContent,'砂底');assert.equal($('#focusMarkerSecondary span').textContent,'坚硬礁面');assert.equal($('#focusMarkerSecondary').hidden,false);$('#guidePlay').onclick();assert.equal(app.getState().guide.paused,true);$('#guideExplore').onclick();assert.equal(app.getState().guide.active,false);assert.equal($('#guideCard').hidden,true);assert.equal($('#focusMarkerSecondary').hidden,true);$('#guideEntry').onclick();assert.equal(app.getState().guide.index,1);assert.equal(app.getState().guide.active,true);app.goGuide(3);for(let i=0;i<110;i++)raf(3000+i*33);assert.ok($('#focusMarker span').textContent.includes('非物种鉴定'));assert.equal($('#focusMarkerSecondary').hidden,true);app.goGuide(4);$('#guideNext').onclick();assert.equal(app.getState().guide.active,false);console.log('PASS: actual app module guide wiring in simulated DOM/renderer: load, next, sources, play/pause, free/resume, fish label, finish. Not WebGL/browser verification.');
// Verify that the journey actually translates through the world, and can be interrupted.
app.preset(0);for(let i=0;i<160;i++)raf(7000+i*33);
$('#orbit').onclick();assert.equal(app.getState().tour,true);
const departure=app.camera.position.clone();for(let i=0;i<1900;i++)raf(14000+i*60);
assert.equal(app.getState().tour,false);assert.ok(app.camera.position.distanceTo(departure)>35);assert.ok(app.camera.position.z < -35);
$('#orbit').onclick();assert.equal(app.getState().tour,true);for(let i=0;i<100;i++)raf(130000+i*60);
assert.ok(app.getState().passageProgress < .9);$('#orbit').onclick();assert.equal(app.getState().tour,false);
const paused=app.camera.position.clone();for(let i=0;i<30;i++)raf(140000+i*60);assert.ok(app.camera.position.distanceTo(paused)<1e-8);
assert.ok(app.controls.maxTargetRadius>=60);assert.ok(app.controls.maxDistance>=30);
console.log('PASS: world journey travels >35 scene units, completes, reverses, pauses exactly, and expands exploratory camera bounds. Simulated controls, not pixel review.');

const pausedProgress=app.getState().passageProgress;raf(150000);$('#orbit').onclick();for(let i=0;i<90;i++)raf(150000+i*60);assert.ok(app.getState().passageProgress<pausedProgress);$('#orbit').onclick();console.log('PASS: paused return trip resumes in the same direction.');

app.goGuide(1);for(let i=0;i<260;i++)raf(170000+i*33);assert.ok(Math.abs(app.controls.target.y-.02)<.001);console.log('PASS: the actual change handler preserves the seabed guide target at y=.02 instead of clamping it to .3.');

// Scene time follows elapsed visible wall time; camera damping remains capped.
app.leaveGuide();app.setTour(false);raf(900000);const clockStart=app.getState().simulationTime;raf(903000);
assert.ok(Math.abs(app.getState().simulationTime-clockStart-(process.env.REEF_REDUCED_MOTION==='1'?0:3))<1e-7);
context.document.hidden=true;context.performance.now=()=>1200000;events.visibilitychange();raf(1200000);const hiddenTime=app.getState().simulationTime;raf(1210000);assert.equal(app.getState().simulationTime,hiddenTime);
context.document.hidden=false;context.performance.now=()=>1300000;events.visibilitychange();raf(1300040);assert.ok(Math.abs(app.getState().simulationTime-hiddenTime-(process.env.REEF_REDUCED_MOTION==='1'?0:.04))<1e-7);
assert.equal(app.getState().fanCurrent.amplitude,seaFanAmplitude(app.getState().simulationTime));
assert.equal(app.getState().fish,6);$('#quality').onclick();assert.equal(root.getObjectByName('fish_05').visible,false);$('#quality').onclick();assert.equal(root.getObjectByName('fish_05').visible,true);
console.log('PASS: elapsed scene time at dropped frames, hidden-tab resume without jump, reduced-motion pause, six fish and low-quality companion visibility.');

// Actual app state, with simulated rendering: clocks are measured in wall seconds.
context.performance.now=()=>clockNow;
const tourSamples=[];
for(const hz of [60,15,1,.3]){
 app.preset(0);for(let i=0;i<400;i++)raf(clockNow+1000/60);
 app.setTour(true);const from=app.getState().passageProgress,start=clockNow;
 while(clockNow<start+30000-1e-7)raf(Math.min(start+30000,clockNow+1000/hz));
 const end=app.getState();assert.ok(Math.abs(end.passageProgress-from-.3)<1e-8);assert.equal(end.tour,true);
 app.setTour(false);const p=end.passageProgress,cam=app.camera.position.clone();raf(clockNow+60000);assert.equal(app.getState().passageProgress,p);assert.ok(cam.distanceTo(app.camera.position)<1e-8);
 app.setTour(true);assert.equal(app.getState().passageProgress,p);raf(clockNow+1000);assert.ok(Math.abs(app.getState().passageProgress-p-.01)<1e-8);
 context.document.hidden=true;events.visibilitychange();raf(clockNow+300000);context.document.hidden=false;events.visibilitychange();const hiddenP=app.getState().passageProgress;raf(clockNow+40);assert.ok(Math.abs(app.getState().passageProgress-hiddenP-.0004)<1e-8);
 const stallP=app.getState().passageProgress;raf(clockNow+20000);assert.equal(app.getState().tour,false);assert.equal(app.getState().passageProgress,stallP);assert.ok($('#viewName').textContent.includes('停顿'));
 app.setTour(true);raf(clockNow+40);assert.ok(Math.abs(app.getState().passageProgress-stallP-.0004)<1e-8);app.setTour(false);
 tourSamples.push({hz,progressAfter30Seconds:end.passageProgress-from,camera:end.camera,target:end.target});
}
fs.mkdirSync('evidence/tour-clock-oct7',{recursive:true});fs.writeFileSync('evidence/tour-clock-oct7/app-timing-checks'+(process.env.REEF_REDUCED_MOTION==='1'?'-reduced':'')+'.json',JSON.stringify({scope:'Actual app logic in simulated DOM/rendering; not native browser performance',tourSamples,manualPauseResume:'exact phase preserved',hiddenResume:'40ms only',foregroundStall:'paused without travel'},null,2));
console.log('PASS: actual app native-tour phase follows visible time at60/15/1/.3Hz; manual pause, hidden resume and long-stall pause preserve route phase.');

app.goGuide(2);for(let i=0;i<400;i++)raf(clockNow+1000/60);
const beforeFocus={p:app.camera.position.clone(),t:app.controls.target.clone(),near:app.camera.near};
assert.equal($('#specimenInspect').hidden,false);$('#specimenInspect').onclick();
assert.equal(app.getState().specimenInspection,true);assert.equal(app.controls.minDistance,.85);assert.equal(app.controls.enablePan,false);assert.equal(app.camera.near,.01);assert.equal($('#guidePlay').disabled,true);assert.ok($('#guideTitle').textContent.includes('真实珊瑚骨架'));assert.equal($('#guideSource').href,SPECIMEN.source);
assert.equal($('#focusMarker').hidden,true);assert.equal($('#focusMarkerSecondary').hidden,true);
const nearCamera=app.camera.position.clone();$('#specimenInspect').onclick();assert.ok(app.camera.position.distanceTo(nearCamera)<1e-10);
for(let i=0;i<80;i++)$('#reef').listeners.keydown({key:'+',preventDefault(){}});
assert.ok(Math.abs(app.camera.position.distanceTo(app.controls.target)-.85)<1e-8);
for(let i=0;i<80;i++)$('#reef').listeners.keydown({key:'ArrowDown',preventDefault(){}});
const sph=new T.Spherical().setFromVector3(app.camera.position.clone().sub(app.controls.target));assert.ok(sph.phi<=Math.PI/3+1e-8);assert.ok(app.camera.position.y>=.425-1e-8);
events.keydown({key:'Escape'});assert.equal(app.getState().specimenInspection,false);assert.ok(app.camera.position.distanceTo(beforeFocus.p)<1e-8);assert.ok(app.controls.target.distanceTo(beforeFocus.t)<1e-8);assert.equal(app.camera.near,beforeFocus.near);assert.equal(app.controls.minDistance,3.2);assert.equal($('#guidePlay').disabled,false);
$('#specimenInspect').onclick();$('#guideNext').onclick();assert.equal(app.getState().specimenInspection,false);assert.equal(app.getState().guide.index,3);assert.equal(app.controls.minDistance,3.2);
app.goGuide(2);$('#specimenInspect').onclick();$('#guideExplore').onclick();assert.equal(app.getState().specimenInspection,false);assert.equal(app.getState().guide.active,false);assert.ok(!$('#viewName').textContent.includes('真实骨架'));
app.goGuide(2);$('#specimenInspect').onclick();$('#orbit').onclick();assert.equal(app.getState().specimenInspection,false);assert.equal(app.getState().tour,true);app.setTour(false);
console.log('PASS actual app inspection button/source/marker, repeated entry, keyboard bounds, Escape, next guide, free explore and tour exit restore world controls. Simulated DOM/rendering only.');

assert.equal(app.getState().fanCurrent.amplitude,seaFanAmplitude(app.getState().simulationTime));
console.log('PASS: sea fan receives the actual app visible-seconds clock, including hidden/reduced-motion resume and explicit tours. Mock fan controller, not WebGL.');
