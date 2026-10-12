// All coordinates are fictional scene units. No survey geometry or scientific scale.
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const smooth=(a,b,v)=>{const t=clamp((v-a)/(b-a),0,1);return t*t*(3-2*t)};
export const EXPLORATION_BOUNDS=Object.freeze({minX:-150,maxX:150,minZ:-420,maxZ:30,surfaceY:11});
export function legacyGroundHeight(x,z){const w=smooth(3,11,Math.hypot(x,z));return -.98+w*(.16*Math.sin(x*.22+z*.1)+.09*Math.sin(z*.35));}
export function floorHeight(x,z){
 const join=smooth(120,163,-z),depth=smooth(238,370,-z);
 const drop=smooth(275,385,-z)*smooth(-5,60,x)*28+smooth(390,560,-z)*22;
 const shelf=-1.2-16*depth-5*smooth(0,100,x)*depth-drop;
 const channel=-1.25*Math.exp(-Math.pow((x-12-12*Math.sin(z*.012))/24,2))*smooth(180,270,-z);
 const ripple=.10*Math.sin(x*.2+z*.065)+.06*Math.sin(z*.29);
 // Broad, continuous depositional banks frame a winding swim lane. This exact
 // function drives rendered vertices and collision floor height, never a visual-only offset.
 const bay=smooth(138,164,-z)*(1-smooth(232,265,-z));
 const lane=4+5*Math.sin((-z-150)*.041);
 const banks=(1.45*Math.exp(-Math.pow((x+17)/15,2)-Math.pow((z+185)/31,2))
   +1.15*Math.exp(-Math.pow((x-22)/17,2)-Math.pow((z+220)/30,2))
   +.70*Math.exp(-Math.pow((x+32)/21,2)-Math.pow((z+233)/25,2)))*bay;
 const sandChannel=-.36*Math.exp(-Math.pow((x-lane)/6,2))*bay;
 const shelfRelief=.9*Math.sin(x*.039+z*.018)*Math.sin(z*.027)*smooth(250,300,-z);
 return legacyGroundHeight(x,z)*(1-join)+(shelf+channel+ripple+banks+sandChannel+shelfRelief)*join;
}
// Asymmetric, broad outcrops and smaller bank anchors, with an open central swim lane.
export const REEF_MASSES=Object.freeze([
 {x:-43,z:-176,rx:18,rz:12,h:3.1,seed:2},
 {x:57,z:-227,rx:26,rz:18,h:4.6,seed:5},
 {x:-46,z:-296,rx:34,rz:24,h:9.1,seed:11},
 {x:-75,z:-350,rx:39,rz:33,h:13,seed:17},
 {x:-26,z:-400,rx:26,rz:21,h:6.7,seed:23},
 // Staggered near/midground anchors; central tour lane remains open.
 {x:-19,z:-156,rx:11,rz:10,h:2.6,seed:43},
 {x:-17,z:-187,rx:10,rz:14,h:3.7,seed:47},
 {x:23,z:-209,rx:10,rz:12,h:3.2,seed:53},
 {x:-30,z:-235,rx:13,rz:10,h:4.1,seed:59},
 {x:-24,z:-286,rx:14,rz:18,h:7,seed:61},
 {x:39,z:-334,rx:14,rz:19,h:12,seed:67},
 {x:-39,z:-367,rx:16,rz:18,h:11,seed:73}
]);
export const DISTANT_MASSES=Object.freeze([{x:130,z:-335,rx:44,rz:37,h:8,seed:31},{x:-140,z:-220,rx:43,rz:31,h:7,seed:37},{x:-62,z:-462,rx:30,rz:24,h:14,seed:41},{x:-5,z:-451,rx:24,rz:23,h:13.5,seed:71,solid:true}]);
export function resolvePosition(position,radius=.65,previous=null){
 const p=Array.isArray(position)?position.slice():[position.x,position.y,position.z];
 const masses=[...REEF_MASSES,...DISTANT_MASSES];
 p[0]=clamp(p[0],-150+radius,150-radius);p[2]=clamp(p[2],-420+radius,30-radius);
 p[1]=clamp(p[1],floorHeight(p[0],p[2])+radius,11-radius);
 const distance=(q,r)=>Math.hypot((q[0]-r.x)/(r.rx+radius),(q[2]-r.z)/(r.rz+radius));
 const inside=(q,r)=>distance(q,r)<1.16-1e-8&&q[1]<floorHeight(q[0],q[2])+r.h+radius-1e-8;
 if(previous){
  // Ordinary swimming never depenetrates by jumping to the edge of a broad
  // reef proxy. Reject only the blocked axis; the caller can slide along others.
  for(const r of masses){if(!inside(p,r))continue;
   if(!inside(previous,r))return previous.slice();
   // A changed/late obstacle must still allow a swimmer to escape gradually.
   if(p[1]<=previous[1]+1e-9&&distance(p,r)<=distance(previous,r)+1e-9)return previous.slice();
  }
  return p;
 }
 // Absolute placement (tour waypoints/reset/adopt) resolves the union, not just
 // the final ellipse. Bounded iterations and a vertical escape handle overlaps.
 for(let pass=0;pass<8;pass++){
  let changed=false;
  for(const r of masses){if(!inside(p,r))continue;const a=Math.atan2((p[2]-r.z)/(r.rz+radius),(p[0]-r.x)/(r.rx+radius));
   p[0]=r.x+Math.cos(a)*(r.rx+radius)*1.16;p[2]=r.z+Math.sin(a)*(r.rz+radius)*1.16;
   if(p[0]>150-radius)p[0]=r.x-(r.rx+radius)*1.16;if(p[0]<-150+radius)p[0]=r.x+(r.rx+radius)*1.16;
   p[0]=clamp(p[0],-150+radius,150-radius);p[2]=clamp(p[2],-420+radius,30-radius);changed=true;
  }
  if(!changed)break;
 }
 for(const r of masses)if(inside(p,r))p[1]=Math.max(p[1],floorHeight(p[0],p[2])+r.h+radius);
 p[1]=clamp(p[1],floorHeight(p[0],p[2])+radius,11-radius);return p;
}
export function regionAt(position){const z=Array.isArray(position)?position[2]:position.z;return z> -120?'原生扫描礁区':z> -245?'开阔海草浅湾':'大陆架与深水边缘';}
export const EXPLORATION_TOUR_STOPS=Object.freeze([
 {label:'原生扫描礁区',position:[4,3.2,10],target:[3,1,-15]},
 {label:'穿过原礁盆',position:[6,6,-85],target:[-5,1,-118]},
 {label:'海草浅湾入口',position:[4,3,-164],target:[-5,.4,-192]},
 {label:'横游开放浅湾',position:[-6,3.2,-227],target:[0,-1,-259]},
 {label:'大陆架断崖',position:[12,-3,-310],target:[-36,-5,-326]},
 {label:'深水蓝境',position:[8,-10,-393],target:[-16,-12,-417]}
]);
