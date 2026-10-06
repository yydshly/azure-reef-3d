import * as THREE from 'three';
// Sample real reef geometry once. Smooth, closed routes keep fish above solid
// surfaces while preserving lateral travel and normal depth occlusion.
export function buildSwimRoute(base,index,terrain){
 const count=112,points=[],ray=new THREE.Raycaster();
 for(let i=0;i<count;i++){
  const a=i/count*Math.PI*2+index*.8;
  const x=base.x+Math.sin(a)*(2.15+index*.08),z=base.z+Math.cos(a)*1.65;
  ray.set(new THREE.Vector3(x,9,z),new THREE.Vector3(0,-1,0));ray.far=11;
  const hit=ray.intersectObjects(terrain,false)[0];
  points.push(new THREE.Vector3(x,Math.max(0.86+index*.08,(hit?.point.y??0)+.34),z));
 }
 const raised=points.map((p,i)=>{const q=p.clone();for(let k=-3;k<=3;k++)q.y=Math.max(q.y,points[(i+k+count)%count].y-.015*Math.abs(k));return q});
 const curve=new THREE.CatmullRomCurve3(raised,true,'centripetal');curve.arcLengthDivisions=280;curve.updateArcLengths();return curve;
}
const up=new THREE.Vector3(0,1,0),side=new THREE.Vector3(),vertical=new THREE.Vector3(),basis=new THREE.Matrix4();
export function sampleSwimRoute(curve,time,index){
 const period=37+index*4.5,u=((time/period+index*.217)%1+1)%1;
 const position=curve.getPointAt(u),direction=curve.getTangentAt(u).normalize();
 side.crossVectors(direction,up).normalize();vertical.crossVectors(side,direction).normalize();basis.makeBasis(direction,vertical,side);
 const quaternion=new THREE.Quaternion().setFromRotationMatrix(basis);
 return {position,quaternion,beat:time*(4.7+index*.22)+index*1.7};
}
