// Synthetic demo units. No DOM/Three dependencies: exactly the same controller is tested in Node.
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const finite=v=>Number.isFinite(v)?v:0;
const wrap=v=>((v+Math.PI)%(Math.PI*2)+Math.PI*2)%(Math.PI*2)-Math.PI;
const copy=v=>v.slice();
export const TOUR_SECONDS=72;
// Clear, level swim lane above the preserved near-reef collision proxies.
export const EXPLORATION_SPAWN=Object.freeze({position:[4,5,10],target:[4,5,-15]});
export function createExplorationNavigation({stops,resolvePosition=p=>p,regionAt=()=>'',speed=7,spawn=EXPLORATION_SPAWN,movePosition=null}){
 if(!Array.isArray(stops)||stops.length<3)throw Error('Three spatial tour stops required');
 let active=false,mode='free',paused=false,elapsed=0,position=copy(spawn.position),yaw=0,pitch=0,velocity=0,reduced=false;
 const keys=new Set();
 function face(target){const d=target.map((v,i)=>v-position[i]);yaw=Math.atan2(d[0],-d[2]);pitch=clamp(Math.atan2(d[1],Math.hypot(d[0],d[2])),-1.1,1.1);}
 face(spawn.target);
 function pose(){const c=Math.cos(pitch);return {position:copy(position),target:[position[0]+Math.sin(yaw)*c*10,position[1]+Math.sin(pitch)*10,position[2]-Math.cos(yaw)*c*10]};}
 function stop(){keys.clear();velocity=0;}
 function tourPose(t){
  const u=clamp(t/TOUR_SECONDS,0,1)*(stops.length-1),i=Math.min(stops.length-2,Math.floor(u)),f=u-i;
  // Ease only at endpoints of each leg; every waypoint is visited exactly.
  const a=stops[i],b=stops[i+1],s=f*f*(3-2*f);
  position=resolvePosition(a.position.map((v,j)=>v+(b.position[j]-v)*s));
  face(a.target.map((v,j)=>v+(b.target[j]-v)*s));
 }
 function free(){active=true;mode='free';paused=false;stop();}
 function tick(dt){
  dt=Math.max(0,finite(dt));if(mode!=='tour')dt=Math.min(dt,.05);if(!active||paused||!dt)return false;
  const before=position.join(',')+yaw+','+pitch;
  if(mode==='tour'){
   if(reduced)return false;
   const old=copy(position);elapsed=Math.min(TOUR_SECONDS,elapsed+dt);if(TOUR_SECONDS-elapsed<1e-8)elapsed=TOUR_SECONDS;tourPose(elapsed);velocity=Math.hypot(...position.map((v,i)=>v-old[i]))/dt;
   if(elapsed>=TOUR_SECONDS){mode='completed';paused=true;velocity=0;}
  }else if(mode==='free'){
   const turn=(keys.has('ArrowRight')?1:0)-(keys.has('ArrowLeft')?1:0),tilt=(keys.has('ArrowUp')?1:0)-(keys.has('ArrowDown')?1:0);
   yaw=wrap(yaw+turn*dt*1.1);pitch=clamp(pitch+tilt*dt*.8,-1.1,1.1);
   const forward=(keys.has('KeyW')?1:0)-(keys.has('KeyS')?1:0),strafe=(keys.has('KeyD')?1:0)-(keys.has('KeyA')?1:0),vertical=(keys.has('KeyE')?1:0)-(keys.has('KeyQ')?1:0);
   const move=[Math.sin(yaw)*Math.cos(pitch)*forward+Math.cos(yaw)*strafe,Math.sin(pitch)*forward+vertical,-Math.cos(yaw)*Math.cos(pitch)*forward+Math.sin(yaw)*strafe];
   const norm=Math.max(1,Math.hypot(...move)),rate=speed*(keys.has('ShiftLeft')||keys.has('ShiftRight')?1.8:1),old=copy(position);
   const candidate=position.map((v,i)=>v+move[i]/norm*dt*rate);position=movePosition?movePosition(candidate,old):resolvePosition(candidate);velocity=Math.hypot(...position.map((v,i)=>v-old[i]))/dt;
  }
  return before!==position.join(',')+yaw+','+pitch;
 }
 return {
  getState:()=>({active,mode,paused,elapsed,duration:TOUR_SECONDS,progress:elapsed/TOUR_SECONDS,goal:elapsed/TOUR_SECONDS,yaw,pitch,position:copy(position),speed:velocity,region:regionAt(position),reduced,heldKeys:[...keys]}),pose,tick,stop,
  enter:free,leave(){stop();active=false;paused=true;},free,
  look(dx,dy){if(mode!=='free'||paused)return;yaw=wrap(yaw+finite(dx));pitch=clamp(pitch+finite(dy),-1.1,1.1);},
  resetLook(){face([position[0],position[1],position[2]-10]);},
  reset(){free();position=resolvePosition(copy(spawn.position));face(spawn.target);elapsed=0;},
  startTour(){stop();active=true;mode='tour';elapsed=0;paused=reduced;tourPose(0);},
  pause(value=true){paused=!!value;stop();},
  togglePause(){if(mode==='completed')return;paused=!paused;stop();},
  request(value){stop();active=true;mode='tour';paused=true;elapsed=clamp(finite(value),0,1)*TOUR_SECONDS;tourPose(elapsed);},
  setReduced(value){reduced=!!value;stop();if(reduced)paused=true;},
  adopt(p,target){free();position=resolvePosition(copy(p));face(target);},
  key(code,down=true){if(!down){keys.delete(code);velocity=0;return;}if(mode!=='free')free();if(paused)paused=false;keys.add(code);if(reduced){tick(.05);keys.delete(code);velocity=0;}},
 };
}
