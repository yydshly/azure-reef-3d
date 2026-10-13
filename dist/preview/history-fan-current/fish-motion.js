import * as THREE from 'three';
// Sample real reef geometry once. Smooth, closed routes keep fish above solid
// surfaces while preserving lateral travel and normal depth occlusion.
export function buildSwimRoute(base,index,terrain){
 const count=336,points=[],ray=new THREE.Raycaster();
 for(let i=0;i<count;i++){
  const a=i/count*Math.PI*2+index*.8;
  const x=base.x+Math.sin(a)*(2.15+index*.08),z=base.z+Math.cos(a)*1.65;
  let roof=0;
  // Sample a body-width footprint rather than a center ray that misses thin branches.
  for(const [dx,dz] of [[0,0],[.28,0],[-.28,0],[0,.28],[0,-.28]]){
   ray.set(new THREE.Vector3(x+dx,9,z+dz),new THREE.Vector3(0,-1,0));ray.far=11;
   const hit=ray.intersectObjects(terrain,false)[0];roof=Math.max(roof,hit?.point.y??0);
  }
  points.push(new THREE.Vector3(x,Math.max(0.86+index*.08,roof+.4),z));
 }
 const raised=points.map((p,i)=>{const q=p.clone();for(let k=-9;k<=9;k++)q.y=Math.max(q.y,points[(i+k+count)%count].y-.005*Math.abs(k));return q});
 const curve=new THREE.CatmullRomCurve3(raised,true,'centripetal');curve.arcLengthDivisions=280;curve.updateArcLengths();return curve;
}
const up=new THREE.Vector3(0,1,0),side=new THREE.Vector3(),vertical=new THREE.Vector3(),basis=new THREE.Matrix4();
export function sampleSwimRoute(curve,time,index,behavior={}){
 const period=behavior.period??(37+index*4.5),phase=behavior.phase??(index*.217);
 const strength=behavior.slowStrength??0,slowPhase=behavior.slowPhase??0;
 const cycle=time/period+phase,angle=(cycle-slowPhase)*Math.PI*2;
 // Smooth non-uniform travel: local lingering and cruising, with no phase jump.
 const travel=cycle+strength*Math.sin(angle)/(Math.PI*2),u=((travel%1)+1)%1;
 const speed=curve.getLength()*(1+strength*Math.cos(angle))/period;
 const directionAt=v=>curve.getPointAt((v+.01)%1).sub(curve.getPointAt((v+.99)%1)).normalize();
 const position=curve.getPointAt(u),direction=directionAt(u);
 side.crossVectors(direction,up).normalize();vertical.crossVectors(side,direction).normalize();basis.makeBasis(direction,vertical,side);
 const quaternion=new THREE.Quaternion().setFromRotationMatrix(basis);
 const before=directionAt((u+.988)%1),after=directionAt((u+.012)%1);
 const turn=Math.atan2(new THREE.Vector3().crossVectors(before,after).y,before.dot(after));
 const bank=THREE.MathUtils.clamp(-turn*.8,-.10,.10)*Math.min(speed/.3,1);
 quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1,0,0),bank));
 return {position,quaternion,speed,group:behavior.group??'near-reef',
  beat:time*1.9+curve.getLength()*travel*7+index*1.7,
  tailAmplitude:.065+.16*THREE.MathUtils.clamp(speed/.45,0,1),
  finAmplitude:.06+.065*(1-THREE.MathUtils.clamp(speed/.35,0,1))};
}
