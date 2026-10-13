// Native tour time is independent of render frequency. This is not an FPS fix.
// Gaps above eight seconds are treated as interruption, not catch-up travel.
export const TOUR_STALL_SECONDS = 8;
export class TourClock {
  constructor(){this.last=null;this.running=false;this.lastStep=0;this.interrupted=false;}
  start(now){this.running=true;this.last=now;this.lastStep=0;this.interrupted=false;}
  pause(){this.running=false;this.last=null;this.lastStep=0;}
  sync(now){this.last=now;this.lastStep=0;}
  tick(now){
    if(!this.running){this.lastStep=0;return 0;}
    if(this.last===null){this.last=now;return 0;}
    const seconds=Math.max(0,(now-this.last)/1000);this.last=now;
    if(seconds>TOUR_STALL_SECONDS){this.running=false;this.interrupted=true;this.lastStep=0;return 0;}
    this.lastStep=seconds;return seconds;
  }
}
// Integrate the existing exponential camera follower with small time steps.
// Sampling the same path between rendered frames avoids frame-rate-dependent
// lag and corner cutting; missed frames themselves cannot be made smooth.
export function advanceTourPose({progress,direction,seconds,duration,camera,target,sample}){
  let remaining=Math.max(0,seconds),u=progress;
  while(remaining>1e-10){
    const h=Math.min(remaining,1/60);remaining-=h;
    u=Math.max(0,Math.min(1,u+direction*h/duration));
    const pose=sample(u,direction),alpha=-Math.expm1(-2*h);
    camera.lerp(pose.p,alpha);target.lerp(pose.t,alpha);
    if(u===0||u===1)break;
  }
  return u;
}
