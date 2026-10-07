import * as THREE from 'three';
// A composed route through an interpreted shallow reef. Distances are scene units,
// not a surveyed transect, measured visibility, or a certified dive route.
export const PASSAGE_STOPS=[
 {name:'礁缘 · 出发',p:[1.5,2.1,4.8],t:[-.5,.8,-6],progress:0},
 {name:'砂地 · 远行',p:[0,1.7,-18],t:[-1.5,1,-31],progress:.45},
 {name:'远礁 · 回望',p:[-3.8,3.6,-36],t:[0,.9,-8],progress:1}
];
// Preserve the original horizontal route parameterization; eye height is composed separately.
const path=new THREE.CatmullRomCurve3([
 new THREE.Vector3(...PASSAGE_STOPS[0].p),new THREE.Vector3(.2,2.4,-8),
 new THREE.Vector3(0,2.7,-18),new THREE.Vector3(-1.5,3.1,-27),
 new THREE.Vector3(...PASSAGE_STOPS[2].p)
],false,'centripetal');
export function samplePassage(progress,direction=1){
 const u=THREE.MathUtils.clamp(progress,0,1),travel=Math.min(1,u/.9),p=path.getPoint(travel);
 const lookAhead=path.getPoint(Math.min(1,travel+.2));
 const t=new THREE.Vector3(lookAhead.x,.7,lookAhead.z-6);
 const returnLook=THREE.MathUtils.smoothstep(u,.86,1);
 const destination=new THREE.Vector3(...PASSAGE_STOPS[2].t);
 const forward=t.clone().sub(p),back=destination.clone().sub(p);
 const a=Math.atan2(forward.x,forward.z),b=Math.atan2(back.x,back.z);
 const turn=Math.atan2(Math.sin(b-a),Math.cos(b-a));
 const distance=THREE.MathUtils.lerp(Math.max(10,forward.length()),back.length(),returnLook);
 t.set(p.x+Math.sin(a+turn*returnLook)*distance,.7,p.z+Math.cos(a+turn*returnLook)*distance);
 if(direction<0){const back=path.getPoint(Math.max(0,travel-.2));t.set(back.x,.7,back.z+6);}
 if(u===0)t.set(...PASSAGE_STOPS[0].t);
 // Enter the tested reef-side height, then rise into the existing final overview.
 const enter=THREE.MathUtils.smoothstep(u,0,.28);
 const rise=THREE.MathUtils.smoothstep(u,.8,1);
 p.y=THREE.MathUtils.lerp(PASSAGE_STOPS[0].p[1],1.7,enter)+rise*(PASSAGE_STOPS[2].p[1]-1.7);
 // Respect the existing orbit polar bound in both travel directions.
 const horizontal=Math.hypot(t.x-p.x,t.z-p.z);
 p.y=Math.max(p.y,t.y+horizontal*Math.tan(Math.PI*.015)+.015);
 return {p,t};
}
export function nearestPassageProgress(position){let nearest=0,best=Infinity;for(let i=0;i<=100;i++){const d=samplePassage(i/100).p.distanceToSquared(position);if(d<best){best=d;nearest=i/100}}return nearest;}
export const PASSAGE_SECONDS=100;
