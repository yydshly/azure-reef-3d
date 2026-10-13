// Close inspection stays inside the existing 3D world. It does not rescale assets.
// The provided pose and orbit limits must first pass scene-clearance checks.
const keys=['minDistance','maxDistance','minPolarAngle','maxPolarAngle','minAzimuthAngle','maxAzimuthAngle','enablePan','enableDamping'];
export class SpecimenFocus {
  constructor(camera,controls){this.camera=camera;this.controls=controls;this.saved=null;}
  get active(){return this.saved!==null;}
  enter({position,target,limits}){
    if(this.active)return false;
    if(!position?.every(Number.isFinite)||!target?.every(Number.isFinite)||position.length!==3||target.length!==3)throw Error('Invalid specimen inspection pose');
    for(const key of ['minDistance','maxDistance','minPolarAngle','maxPolarAngle'])if(!Number.isFinite(limits?.[key]))throw Error('Missing specimen orbit bound');
    if(limits.minDistance<=0||limits.maxDistance<limits.minDistance||limits.minPolarAngle<0||limits.maxPolarAngle>Math.PI||limits.maxPolarAngle<limits.minPolarAngle)throw Error('Invalid specimen orbit bounds');
    const c=this.controls,k=this.camera,damping=c.enableDamping;
    // Drain pending orbit inertia before applying the measured inspection pose.
    c.enableDamping=false;c.update(0);c.enableDamping=damping;
    this.saved={position:k.position.clone(),target:c.target.clone(),near:k.near,limits:Object.fromEntries(keys.map(key=>[key,c[key]]))};
    for(const key of ['minDistance','maxDistance','minPolarAngle','maxPolarAngle']){
      c[key]=limits[key];
    }
    c.minAzimuthAngle=limits.minAzimuthAngle??-Infinity;c.maxAzimuthAngle=limits.maxAzimuthAngle??Infinity;c.enablePan=false;
    k.near=.01;k.position.fromArray(position);c.target.fromArray(target);k.updateProjectionMatrix();c.update(0);return true;
  }
  exit(){
    if(!this.active)return false;
    const c=this.controls,k=this.camera,s=this.saved;
    c.enableDamping=false;c.update(0);
    Object.assign(c,s.limits);k.near=s.near;k.position.copy(s.position);c.target.copy(s.target);k.updateProjectionMatrix();c.update(0);this.saved=null;return true;
  }
}
