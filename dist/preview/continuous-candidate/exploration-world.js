import * as T from 'three';
import {REAR_CONNECTED_DATA as SCAN_FORMS} from './rear-connected-data.js';
import {floorHeight,legacyGroundHeight,resolvePosition,regionAt,EXPLORATION_BOUNDS,EXPLORATION_TOUR_STOPS,REEF_MASSES,DISTANT_MASSES} from './exploration-world-data.js?v=layered-habitat-20261011-v1';
export {floorHeight,resolvePosition,regionAt,EXPLORATION_TOUR_STOPS} from './exploration-world-data.js?v=layered-habitat-20261011-v1';
// Procedural synthetic scenery only: no downloads, imported surveys, or changes to existing support surfaces.
export function createExplorationWorld({scene,configure=()=>{},ground}){
 const group=new T.Group();group.name='Synthetic_Continuous_Exploration_Regions';scene.add(group);
 const geometries=new Set(),materials=new Set(),instances=[],animated=[];let disposed=false,paused=false,reduced=false,hidden=false,lastTime=0;
 const dummy=new T.Object3D(),color=new T.Color();let seed=814273;
 const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
 const smooth=(a,b,v)=>T.MathUtils.smoothstep(v,a,b);
 const mat=(color,opts={})=>{const m=new T.MeshStandardMaterial({color,roughness:1,...opts});configure(m);materials.add(m);return m};
 function mesh(name,g,m){geometries.add(g);const o=new T.Mesh(g,m);o.name=name;o.receiveShadow=true;group.add(o);return o;}
 function batch(name,g,m,items){geometries.add(g);const o=new T.InstancedMesh(g,m,items.length);o.name=name;o.receiveShadow=true;items.forEach((p,i)=>{dummy.position.fromArray(p.p);dummy.rotation.set(0,p.a||0,0);dummy.scale.fromArray(p.s||[1,1,1]);dummy.updateMatrix();o.setMatrixAt(i,dummy.matrix);if(p.c)o.setColorAt(i,color.set(p.c));});o.computeBoundingSphere();group.add(o);instances.push(o);return o;}
 // Connected shelf: actual bottom extends far outside navigable bounds. It is not a scaled copy of the reef.
 // A narrow new transition tongue begins beyond all retained scan supports.
 const sand=mat('#ffffff',{vertexColors:true});
 const prior=sand.onBeforeCompile;sand.onBeforeCompile=shader=>{prior.call(sand,shader);shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
float drift=sin(vExhibitWorld.z*.19)*2.+sin(vExhibitWorld.x*.07+vExhibitWorld.z*.055)*3.;
float micro=.5+.5*sin(vExhibitWorld.x*5.8+drift);
float sandPatch=.5+.5*sin(vExhibitWorld.x*.47+sin(vExhibitWorld.z*.21))*sin(vExhibitWorld.z*.36);
float grain=fract(sin(dot(floor(vExhibitWorld.xz*140.),vec2(127.1,311.7)))*43758.5453);
diffuseColor.rgb*=.91+.035*micro+.035*grain+.045*sandPatch;`)};
 sand.customProgramCacheKey=()=>'exploration-sand-ocean-v2';
 const tile=100;
 for(let z=-620;z<80;z+=tile)for(let x=-300;x<300;x+=tile){
  const step=(Math.abs(x+50)>160||z < -420)?5:2.5;
  const p=[],c=[],ind=[];const n=tile/step;
  for(let j=0;j<=n;j++)for(let i=0;i<=n;i++){
   const px=x+i*step,pz=z+j*step;let h=floorHeight(px,pz);
   // Do not cover the retained reef, its original seabed, or its support aprons.
   const newRegion=pz<=-125||Math.abs(px)>=75;
   if(pz>-145&&pz<=-125)h=legacyGroundHeight(px,pz)+.012;
   p.push(px,h,pz);const d=smooth(230,390,-pz),patch=.5+.5*Math.sin(px*.031+pz*.027)*Math.sin(px*.077-pz*.018);const bank=smooth(138,164,-pz)*(1-smooth(240,270,-pz));const mottling=.5+.5*Math.sin(px*.13+Math.sin(pz*.07)*2)*Math.sin(pz*.11-px*.06);color.set('#beb897').lerp(new T.Color('#78937d'),bank*mottling*.27).lerp(new T.Color('#557b78'),d*.53).multiplyScalar(.89+.14*patch);c.push(color.r,color.g,color.b);
  }
  for(let j=0;j<n;j++)for(let i=0;i<n;i++){const px=x+(i+.5)*step,pz=z+(j+.5)*step;if(pz>-125&&Math.abs(px)<75&&pz<65)continue;const a=j*(n+1)+i,b=a+1,d=a+n+1;ind.push(a,d,b,b,d,d+1);}
  if(!ind.length)continue;const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(p,3));g.setAttribute('color',new T.Float32BufferAttribute(c,3));g.setIndex(ind);g.computeVertexNormals();mesh('Continuous_Shelf_Sediment_'+x+'_'+z,g,sand);
 }
 // Angular layered erosional limestone, each unique footprint and stratigraphy.
 const rock=mat('#ffffff',{vertexColors:true});const outcrops=new Map();
 const rockPrevious=rock.onBeforeCompile;rock.onBeforeCompile=shader=>{rockPrevious.call(rock,shader);shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
float strata=.5+.5*sin(vExhibitWorld.y*5.+sin(vExhibitWorld.x*.21)*1.3+sin(vExhibitWorld.z*.18));
float pores=fract(sin(dot(floor(vExhibitWorld*20.),vec3(127.1,311.7,74.7)))*43758.5453);
float mineral=.5+.5*sin(vExhibitWorld.x*1.7+sin(vExhibitWorld.z*2.1))*sin(vExhibitWorld.y*2.9);
diffuseColor.rgb*=.77+.17*strata+.16*mineral+.07*pores;
diffuseColor.rgb=mix(diffuseColor.rgb,diffuseColor.rgb*vec3(1.13,.91,.85),smoothstep(.68,.9,mineral)*.35);`);};

 rock.customProgramCacheKey=()=>'exploration-strata-ocean-v1';
 // Reuse four distinct, already-tested CC0 scan-derived compositions as sparse
 // landmarks. Original arrays are read-only; only these copies are normalized.
 const formGroups=['near_offset_patch','back_right_islet','left_receding_patch','rear_broken_outline'];
 function outcrop(r){
  const sourceGroup=r.solid?'near_offset_patch':formGroups[(r.seed+Math.floor(r.seed/7))%formGroups.length];
  // The deep landmark uses one intact CC0-derived boulder with a broad mass,
  // rather than stretching three low reef shelves into blade-like spires.
  const selected=Object.values(SCAN_FORMS.meshes).filter(d=>d.group===sourceGroup);
  const forms=r.solid?selected.slice(0,1):selected;
  const box=new T.Box3();forms.forEach(d=>d.vertices.forEach(p=>box.expandByPoint(new T.Vector3(...p))));const size=box.getSize(new T.Vector3()),center=box.getCenter(new T.Vector3());
  const p=[],c=[],idx=[];
  for(let f=0;f<forms.length;f++){const d=forms[f],off=p.length/3;for(const v of d.vertices){
    let nx=(v[0]-center.x)/size.x*2,nz=(v[2]-center.z)/size.z*2;
    // Mirror selected entire compositions, never perturb individual source vertices.
    if(r.seed%2)nx=-nx;
    const x=r.x+nx*r.rx*.82,z=r.z+nz*r.rz*.84;
    const y=floorHeight(x,z)+((v[1]-box.min.y)/size.y)*r.h-.18;
    p.push(x,y,z);color.set(f===0?'#829087':f===1?'#7a8981':'#9a9d87');c.push(color.r,color.g,color.b);
   }for(const triangle of d.triangles){const t=triangle.map(i=>i+off);idx.push(...(r.seed%2?[t[0],t[2],t[1]]:t));}}
  const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(p,3));g.setAttribute('color',new T.Float32BufferAttribute(c,3));g.setIndex(idx);g.computeVertexNormals();
  const o=mesh('Broken_Scan_Derived_Reef_'+r.seed,g,rock);o.userData={synthetic:true,terrestrialScanArt:true,source:'https://polyhaven.com/a/boulder_01',license:'CC0',sourceComposition:sourceGroup,sourceUnmodified:true};outcrops.set(r.seed,o);
 }
 // Existing collision footprints retained; textured 3D buttresses supply the candidate scenery.
 // REEF_MASSES.forEach(outcrop);
 // Remote singular mesas make the world extend past the route rather than forming two walls.
 // DISTANT_MASSES.forEach(outcrop);
 // Broad, curling leaves form canopies and low cushions, not repeated vertical spikes.
 // Six leaves × five segments per tuft. All growth is world-positioned.
 const blades=[];for(let j=0;j<6;j++){const a=j*2.399,h=.95+(j%3)*.31,bend=.68+(j%2)*.40;for(let k=0;k<5;k++){const t=k/5,u=(k+1)/5;const vertex=(q,side)=>{const w=(.025+.082*Math.sin(q*Math.PI))*(1-q*.75);const curl=bend*q*q;return [Math.cos(a)*curl+Math.sin(a)*w*side,h*(q-.18*q*q*q),Math.sin(a)*curl-Math.cos(a)*w*side]};blades.push(...vertex(t,-1),...vertex(t,1),...vertex(u,-1),...vertex(t,1),...vertex(u,1),...vertex(u,-1));}}
 const grassG=new T.BufferGeometry();grassG.setAttribute('position',new T.Float32BufferAttribute(blades,3));grassG.computeVertexNormals();
 const grassM=mat('#ffffff',{side:T.DoubleSide});const grassTime={value:0};const grassPrior=grassM.onBeforeCompile;grassM.onBeforeCompile=shader=>{grassPrior.call(grassM,shader);shader.uniforms.explorationTime=grassTime;shader.vertexShader='uniform float explorationTime;\n'+shader.vertexShader;shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
float sway=sin(explorationTime*.65+instanceMatrix[3].x*.23+instanceMatrix[3].z*.14);
transformed.x+=sway*position.y*position.y*.12;
transformed.z+=cos(explorationTime*.53+instanceMatrix[3].z*.17)*position.y*position.y*.06;`)};
 grassM.customProgramCacheKey=()=>'exploration-curved-canopy-ocean-v2';
 // Clustered stands on banks, with scalloped margins and visible sand channels.
 const meadowPatches=[[-6,-163,13,17],[18,-178,13,19],[-15,-192,19,22],[23,-213,16,20],[-18,-230,22,18],[29,-242,18,13],[-47,-218,18,19],[-18,-258,18,14],[-11,-209,12,14],[14,-196,8,14]];
 let grassCount=0;
 for(let k=0;k<meadowPatches.length;k++){const [cx,cz,rx,rz]=meadowPatches[k],items=[];
  for(let i=0;i<355;i++){const a=random()*Math.PI*2,rad=Math.sqrt(random()),x=cx+Math.cos(a)*rx*rad,z=cz+Math.sin(a)*rz*rad;
   const lane=4+5*Math.sin((-z-150)*.041);if(Math.abs(x-lane)<3.9)continue;
   const edge=.83+.14*Math.sin(a*5+k);if(rad>edge)continue;
   if(REEF_MASSES.some(r=>Math.hypot((x-r.x)/r.rx,(z-r.z)/r.rz)<.84))continue;
   const cluster=.5+.5*Math.sin(x*.57+Math.sin(z*.31))*Math.cos(z*.39-x*.16);if(cluster<.21)continue;
   const scale=.7+random()*.68,tall=cluster>.66?1.4:.9;
   items.push({p:[x,floorHeight(x,z)-.035,z],a:random()*6.28,s:[scale*1.2,scale*tall,scale*1.2],c:['#5c7846','#7f9359','#4e795c','#9da064'][i%4]});
  }grassCount+=items.length;const canopy=batch('Open_Bay_Seagrass_Meadow_'+k,grassG,grassM,items);canopy.boundingSphere.radius+=1.;
 }
 // Surface-seated colonies punctuate the banks and layered reefs: cupped plates,
 // warm branching fans and low sponge clusters, all in the same synthetic world.
 const pp=[],pi=[];for(let j=0;j<3;j++)for(let i=0;i<14;i++){const a=i/14*Math.PI*2,r=[.07,.67,1][j]*(1+.11*Math.sin(a*5));pp.push(Math.cos(a)*r,[.03,.11,.26][j]+.07*Math.sin(a*3)*j/2,Math.sin(a)*r);}
 for(let j=0;j<2;j++)for(let i=0;i<14;i++){const a=j*14+i,b=j*14+(i+1)%14,c=a+14,d=b+14;pi.push(a,c,b,b,c,d);}
 const plateG=new T.BufferGeometry();plateG.setAttribute('position',new T.Float32BufferAttribute(pp,3));plateG.setIndex(pi);plateG.computeVertexNormals();
 const seatRay=new T.Raycaster(),down=new T.Vector3(0,-1,0);group.updateMatrixWorld(true);
 const plates=[],fans=[],sponges=[];
 for(const r of []){for(let i=0;i<26;i++){const a=random()*6.28,rad=.10+Math.sqrt(random())*.63,x=r.x+Math.cos(a)*r.rx*rad,z=r.z+Math.sin(a)*r.rz*rad;seatRay.set(new T.Vector3(x,40,z),down);const hit=seatRay.intersectObject(outcrops.get(r.seed),false)[0];if(!hit||hit.face.normal.y<.18)continue;const y=hit.point.y-.025;
  if(i%3!==0)plates.push({p:[x,y,z],a,s:[.7+random()*1.1,.8+random(),.6+random()],c:['#a79876','#8a9772','#789486','#b09482'][i%4]});
  if(i%4===0)fans.push({p:[x,y,z],a,s:[.9+random(),1.3+random()*1.4,1],c:i%2?'#aa8a7c':'#bf996b'});
  if(i%4===1)sponges.push({p:[x,y,z],a,s:[.6+random()*.6,.6+random()*.9,.6+random()*.6],c:i%2?'#ba986b':'#9f9980'});
 }}
 batch('Shelf_Top_Encrusting_Colonies',plateG,mat('#ffffff',{side:T.DoubleSide}),plates);
 const fp=[];function limb(x,y,xx,yy,w){const z=.12*Math.sin(y*2+x);fp.push(x-w,y,z,x+w,y,z,xx,yy,.12*Math.sin(yy*2+xx))}limb(0,0,0,1.15,.046);for(let i=0;i<12;i++){const y=.14+i*.068,w=.72*Math.sin((i+1)/13*Math.PI);for(const side of[-1,1]){limb(0,y,w*side,y+.49,.025);for(let j=1;j<5;j++)limb(w*side*j/5,y+.49*j/5,side*(w*j/5+.17),y+.49*j/5+.27,.012);}}
 const fanG=new T.BufferGeometry();fanG.setAttribute('position',new T.Float32BufferAttribute(fp,3));fanG.computeVertexNormals();batch('Deep_Edge_Sea_Fans',fanG,mat('#ffffff',{side:T.DoubleSide}),fans);
 const spongeP=[],spongeI=[];for(let stem=0;stem<3;stem++){const off=spongeP.length/3,h=.6+stem*.27,cx=Math.cos(stem*2.4)*.27,cz=Math.sin(stem*2.4)*.27;for(let ring=0;ring<3;ring++)for(let k=0;k<8;k++){const a=k/8*Math.PI*2,r=[.2,.24,.14][ring];spongeP.push(cx+Math.cos(a)*r+(ring?stem*.07:0),[0,h,h-.17][ring],cz+Math.sin(a)*r);}for(let ring=0;ring<2;ring++)for(let k=0;k<8;k++){const a=off+ring*8+k,b=off+ring*8+(k+1)%8;spongeI.push(a,a+8,b,b,a+8,b+8);}}
 const spongeG=new T.BufferGeometry();spongeG.setAttribute('position',new T.Float32BufferAttribute(spongeP,3));spongeG.setIndex(spongeI);spongeG.computeVertexNormals();batch('Warm_Tube_Sponge_Clusters',spongeG,mat('#ffffff',{side:T.DoubleSide}),sponges);
 // Native fish silhouettes form schools in each region, with restrained motion.
 const bodyG=new T.SphereGeometry(1,9,6).toNonIndexed(),fishPositions=[];const bodyP=bodyG.attributes.position;for(let i=0;i<bodyP.count;i++)fishPositions.push(bodyP.getX(i)*.48-.12,bodyP.getY(i)*.15,bodyP.getZ(i)*.11);bodyG.dispose();fishPositions.push(.27,0,0,.60,.23,0,.60,-.23,0,.27,0,0,.60,0,.08,.60,.23,0);
 const fishG=new T.BufferGeometry();fishG.setAttribute('position',new T.Float32BufferAttribute(fishPositions,3));fishG.computeVertexNormals();
 const fishM=mat('#b7c8b8',{side:T.DoubleSide});
 // Near and middle-distance schools have bounded, independent trajectories in
 // world coordinates. No camera-follow fish, particles or fabricated parallax.
 const schools=[{c:[-3,3.6,-185],n:36,s:.95,spread:[8,1.4,6]}, {c:[14,3.0,-224],n:30,s:.80,spread:[8,1.3,8]}, {c:[-14,-5,-292],n:26,s:1.1,spread:[7,2.1,7]}, {c:[2,-14,-410],n:32,s:.95,spread:[10,2.8,9]}];
 for(const [j,school]of schools.entries()){const items=Array.from({length:school.n},(_,i)=>{const a=random()*6.28,r=Math.sqrt(random()),scale=school.s*(.72+random()*.5);return {p:[school.c[0]+Math.cos(a)*school.spread[0]*r,school.c[1]+(random()-.5)*school.spread[1],school.c[2]+Math.sin(a)*school.spread[2]*r],s:[scale,scale,scale],phase:random()*6.28,c:i%5?'#a8beb6':'#c7b785'};});const f=batch('Regional_Silver_School_'+j,fishG,fishM,items);f.boundingSphere.radius+=4.5;animated.push({mesh:f,center:school.c,items,j});}
 // One water envelope supplied by scan-ocean spans the route. Removing the
 // finite, flat alpha sheet avoids its hard horizon-like edge in the bay.
 group.userData={synthetic:true,measuredSite:false,scanChanges:0,bounds:EXPLORATION_BOUNDS,regions:['原生扫描礁区','开阔海草浅湾','大陆架与深水边缘'],newDownloads:0,visualRevision:'layered-habitat-v1',cameraAttachedLife:false,grassInstances:grassCount,landmarkSource:'https://polyhaven.com/a/boulder_01',landmarkLicense:'CC0',scanDerivedSource:'existing rear-connected-data.js; read-only; fictional composition'};
 const meshes=[];group.traverse(o=>{if(o.isMesh)meshes.push(o)});const budget={meshes:meshes.length,drawCalls:meshes.length,triangles:meshes.reduce((s,o)=>s+(o.geometry.index?.count||o.geometry.attributes.position.count)/3*(o.isInstancedMesh?o.count:1),0),instances:instances.reduce((s,o)=>s+o.count,0),geometryBytes:[...geometries].reduce((s,g)=>s+Object.values(g.attributes).reduce((a,b)=>a+b.array.byteLength,0)+(g.index?.array.byteLength||0),0),newTextureBytes:0,newModelBytes:0};group.userData.budget=budget;
 function update(time,camera){if(disposed||paused||reduced||hidden)return;lastTime=Number.isFinite(time)?time:lastTime;grassTime.value=lastTime;for(const school of animated){school.items.forEach((item,i)=>{dummy.position.fromArray(item.p);const phase=lastTime*.13+school.j*1.7;dummy.position.x+=Math.sin(phase)*3.5;dummy.position.z+=Math.cos(phase)*2.5;dummy.position.y+=Math.sin(lastTime*.8+item.phase)*.18;dummy.rotation.set(Math.sin(lastTime*.6+item.phase)*.025,-Math.atan2(-Math.sin(phase)*2.5,Math.cos(phase)*3.5)+Math.PI,Math.sin(lastTime*2+item.phase)*.035);dummy.scale.fromArray(item.s);dummy.updateMatrix();school.mesh.setMatrixAt(i,dummy.matrix);});school.mesh.instanceMatrix.needsUpdate=true;}}
 function dispose(){if(disposed)return;disposed=true;group.removeFromParent();instances.forEach(o=>o.dispose());geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());}
 return {group,budget,bounds:EXPLORATION_BOUNDS,floorHeight,sampleGroundHeight:floorHeight,resolvePosition,regionAt,tourStops:EXPLORATION_TOUR_STOPS,update,dispose,setPaused(v){paused=!!v},setReducedMotion(v){reduced=!!v},setHidden(v){hidden=!!v},getState:()=>({disposed,paused,reduced,hidden,lastTime,budget})};
}
