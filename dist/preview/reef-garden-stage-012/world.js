import * as T from 'three';
import {mergeGeometries} from '../../utils/BufferGeometryUtils.js';
export const STOPS=[
 {label:'珊瑚门廊',position:[0,4.2,24],target:[0,5,-22]},
 {label:'虹色礁庭',position:[-1,4,-22],target:[3,4,-44]},
 {label:'光羽海草湾',position:[15,3.4,-65],target:[-7,4,-96]},
 {label:'月弧峡湾',position:[0,3.2,-108],target:[-40,6,-110]},
 {label:'星珊瑚穹顶',position:[-22,2.3,-144],target:[-18,7,-159]},
 {label:'归航眺台',position:[-18,5,-199],target:[1,5,-183]}
];
export const STAGE_VERSION='01.2-stage';
export const STATION_HABITATS=['shell-portal','rose-plate-garden','sea-feather-bay','blue-canyon','umbrella-grove','gold-fan-lookout'];
export const SPAWN={position:STOPS[0].position,target:STOPS[0].target};
const smooth=(a,b,x)=>T.MathUtils.smoothstep(x,a,b);
export function floorHeight(x,z){return -1.8-1.9*smooth(35,180,-z)+.16*Math.sin(x*.11+z*.075)+.13*Math.cos(z*.12-x*.045)}
export function createGarden(scene){
 const root=new T.Group();root.name='Azure_Stylized_Complete_Sea';scene.add(root);
 const geoms=new Set(),mats=new Set(),batches=[],obstacles=[],dummy=new T.Object3D(),col=new T.Color();let seed=1729;
 const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
 const mat=(c,o={})=>{const m=new T.MeshStandardMaterial({color:c,roughness:.91,metalness:0,...o});mats.add(m);return m};
 function mesh(name,g,m,p=[0,0,0],s=[1,1,1]){geoms.add(g);const o=new T.Mesh(g,m);o.name=name;o.position.fromArray(p);o.scale.fromArray(s);o.receiveShadow=true;root.add(o);return o;}
 function batch(name,g,m,items,cast=false){geoms.add(g);const o=new T.InstancedMesh(g,m,items.length);o.name=name;o.castShadow=cast;o.receiveShadow=true;items.forEach((p,i)=>{dummy.position.fromArray(p.p);dummy.rotation.set(...(p.r||[0,p.a||0,0]));dummy.scale.fromArray(p.s||[1,1,1]);dummy.updateMatrix();o.setMatrixAt(i,dummy.matrix);if(p.c)o.setColorAt(i,col.set(p.c))});o.computeBoundingSphere();root.add(o);batches.push(o);return o;}
 const zone=z=>z>0?0:z>-46?1:z>-90?2:z>-130?3:z>-176?4:5;
 const coralColors=[['#d9bc8c','#b6cab1'],['#d997a0','#e1b79a'],['#76ae9b','#b0cdb0'],['#93abc3','#92b7b7'],['#bc97c0','#caa3b9'],['#e1c28f','#cbd7ae']];
 const palette={sand:'#a7c6b0',reef:'#426c7a',mint:'#7ead9a',peach:'#d6a58a',rose:'#ba819a',lilac:'#9987b5',gold:'#d2b887',grass:'#60968a'};
 const terrain=new T.PlaneGeometry(350,460,140,184);terrain.rotateX(-Math.PI/2);terrain.translate(0,0,-75);const tp=terrain.attributes.position,tc=[];
 for(let i=0;i<tp.count;i++){const x=tp.getX(i),z=tp.getZ(i);tp.setY(i,floorHeight(x,z));col.set(palette.sand).lerp(new T.Color('#6a9d9b'),smooth(75,190,-z)*.40).multiplyScalar(.96+.04*Math.sin(x*.10+z*.09));tc.push(...col.toArray())}terrain.setAttribute('color',new T.Float32BufferAttribute(tc,3));terrain.computeVertexNormals();mesh('Continuous_Illustrated_Sand',terrain,mat('#ffffff',{vertexColors:true}));
 // Sculpted volumetric reef shelves. Bands and irregular silhouettes belong to
 // one original visual language, never texture-scanned stone mixed with cartoons.
 const rp=[],ri=[],rc=[];const rings=[{y:0,r:1.06},{y:.18,r:1.04},{y:.40,r:1},{y:.66,r:.88},{y:.89,r:.76},{y:1,r:.67}],segments=14;
 for(let j=0;j<rings.length;j++)for(let i=0;i<segments;i++){const a=i/segments*Math.PI*2,r=rings[j].r*(1+.10*Math.sin(a*3)+.045*Math.cos(a*7+j));rp.push(Math.cos(a)*r,rings[j].y+.025*Math.sin(a*4+j)*(j?1:0),Math.sin(a)*r);col.set(j>=4?'#88ad99':j%2?'#507c86':'#3f6577');rc.push(...col.toArray())}
 for(let j=0;j<rings.length-1;j++)for(let i=0;i<segments;i++){const a=j*segments+i,b=j*segments+(i+1)%segments,c=a+segments,d=b+segments;ri.push(a,c,b,b,c,d)}
 const top=rp.length/3;rp.push(0,1,0);rc.push(...new T.Color('#91b5a2').toArray());for(let i=0;i<segments;i++)ri.push(top,5*segments+(i+1)%segments,5*segments+i);
 const reefG=new T.BufferGeometry();reefG.setAttribute('position',new T.Float32BufferAttribute(rp,3));reefG.setAttribute('color',new T.Float32BufferAttribute(rc,3));reefG.setIndex(ri);reefG.computeVertexNormals();const reefM=mat('#ffffff',{vertexColors:true,flatShading:true});
 const formations=[[-16,10,9,3.4,10],[19,0,12,5,13],[-21,-26,10,6,12],[17,-43,9,4.7,12],[-20,-53,13,4,13],[-6,-74,8,4.1,9],[38,-75,12,6,17],[-26,-91,13,8,15],[31,-103,14,5,13],[17,-120,12,8,12],[-40,-131,10,7,15],[9,-144,16,5.5,17],[-45,-157,14,9,19],[5,-183,14,8,18],[-38,-196,16,6,15],[-36,-226,13,8,13],[27,-212,18,8,22],[-26,56,11,4.5,12],[23,53,10,6,12],[-48,6,16,6,17],[50,-44,18,9,19],[-52,-101,18,13,20],[48,-152,17,10,19],[-55,-214,17,10,21],[54,33,16,6,17],[-8,91,17,7,16],[44,95,16,10,19],[-30,-247,13,11,16],[15,-251,18,8,19]];
 // Smaller asymmetric outcrops punctuate the sand banks without adding gateways.
 formations.push([-7,14,3.1,1.5,3.6],[8,1,3.8,1.8,3.1],[7,-14,2.6,1.4,3.8],[-9,-39,3.7,2.1,4.8],[10,-52,2.8,1.6,3.5],[24,-77,3.4,2.5,4.8],[3,-89,3.1,1.8,3.6],[-10,-119,4.2,2.7,4.4],[-30,-139,3.5,2.2,4.5],[-6,-171,3.2,2.1,4.3],[-9,-209,3.8,2,4.5],[-10,-229,6,4.2,7],[12,-236,13,9,16]);
 const reefItems=Array.from({length:6},()=>[]),gardens=[];
 for(const [k,r]of formations.entries()){
  const [x,z,rx,h,rz]=r,base=floorHeight(x,z)-h*.25;reefItems[zone(z)].push({p:[x,base,z],s:[rx,h,rz],a:k*.74});obstacles.push({x,z,rx:rx*.75,rz:rz*.75,y0:base,y1:base+h*.9,name:'reef-'+k});
  for(let j=0;j<(rx<5?6:12);j++){const angle=rand()*6.28,rad=Math.sqrt(rand())*.52,px=x+Math.cos(angle)*rx*rad,pz=z+Math.sin(angle)*rz*rad;gardens.push({x:px,z:pz,y:base+h*.96,scale:.8+rand()*1.2,index:j+k})}
 }
 // Six deformations of the same volumetric shelf, with unchanged formation count.
 const reefTops=['#abc3a8','#bcb1a1','#90b7a1','#6e9ea8','#aba6bc','#a9c0ae'];
 const reefSides=['#527c81','#796f7b','#3e7d7b','#426377','#666c89','#527c86'];
 for(let v=0;v<6;v++){const g=reefG.clone(),p=g.attributes.position,c=g.attributes.color;
  for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i),z=p.getZ(i),a=Math.atan2(z,x);let fx=1,fz=1,ox=0,oz=0;
   if(v===0){fx=1+.12*Math.cos(a*2);oz=.10*y*y}
   if(v===1){fx=1+.19*Math.sin(a*3+.4);fz=.88+.12*Math.cos(a*2);ox=.17*y}
   if(v===2){fx=1+.20*Math.sin(a*2);fz=1+.12*Math.cos(a*3);oz=-.15*y*y}
   if(v===3){fx=.87+.20*Math.cos(a*2);fz=1+.16*Math.sin(a*3);ox=.26*y*y}
   if(v===4){fx=1+.15*Math.cos(a*4);fz=1+.11*Math.sin(a*3);ox=-.12*y}
   if(v===5){fx=1+.23*Math.sin(a*2+.7);fz=.90+.15*Math.cos(a*3);oz=.22*y*y}
   p.setXYZ(i,x*fx+ox,y,z*fz+oz);col.set(y>.85?reefTops[v]:reefSides[v]).multiplyScalar(y>.85?1:((Math.floor(y*8)%2)?.90:1.06));c.setXYZ(i,col.r,col.g,col.b)
  }g.computeVertexNormals();batch('Habitat_Reef_'+STATION_HABITATS[v],g,reefM,reefItems[v],true)
 }reefG.dispose();
 
 // Fine branching coral, softly curved instead of straight skeletal spikes.
 function branching(){const pieces=[];function stem(a,b,r){const curve=new T.CatmullRomCurve3([new T.Vector3(...a),new T.Vector3((a[0]+b[0])/2+.05,(a[1]+b[1])/2,(a[2]+b[2])/2+.05),new T.Vector3(...b)]);pieces.push(new T.TubeGeometry(curve,5,r,5,false))}
  stem([0,0,0],[0,1.4,0],.065);for(let k=0;k<7;k++){const a=k*2.399,y=.20+k*.14,b=[Math.cos(a)*.5,y+.5,Math.sin(a)*.5];stem([0,y,0],b,.041);for(let j=0;j<3;j++)stem(b,[b[0]+Math.cos(a+j*.8)*.25,b[1]+.28+j*.07,b[2]+Math.sin(a+j*.8)*.23],.023)}
  const g=mergeGeometries(pieces,false);pieces.forEach(p=>p.dispose());return g;
 }
 const branchItems=gardens.filter((_,i)=>i%3===0).map(p=>({p:[p.x,p.y,p.z],s:[p.scale*(zone(p.z)===3?.65:1),p.scale*(zone(p.z)===3?2.1:zone(p.z)===2?.7:1.4),p.scale*(zone(p.z)===3?.65:1)],a:rand()*6.28,c:coralColors[zone(p.z)][p.index%2]}));batch('Pastel_Coral_Thickets',branching(),mat('#ffffff'),branchItems);
 function cup(){const p=[],ind=[];for(let j=0;j<4;j++)for(let i=0;i<28;i++){const a=i/28*6.28,r=[.08,.55,.86,1][j]*(1+.06*Math.sin(a*5));p.push(Math.cos(a)*r,[0,.10,.20,.33][j]+.035*Math.sin(a*4),Math.sin(a)*r)}for(let j=0;j<3;j++)for(let i=0;i<28;i++){const a=j*28+i,b=j*28+(i+1)%28;ind.push(a,a+28,b,b,a+28,b+28)}const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(p,3));g.setIndex(ind);g.computeVertexNormals();return g}
 const cupG=cup(),cupM=mat('#ffffff',{side:T.DoubleSide});const cupItems=[];
 gardens.filter((_,i)=>i%3===1).forEach(p=>{for(let j=0;j<3;j++)cupItems.push({p:[p.x+.15*j,p.y+.22*j,p.z],s:[p.scale*(1.25-j*.15)*(zone(p.z)===1?1.25:.9),p.scale*(zone(p.z)===1?1.6:.7),p.scale*(1.25-j*.15)],a:rand()*6.28,c:coralColors[zone(p.z)][(p.index+j)%2]})});batch('Ruffled_Plate_Coral_Gardens',cupG,cupM,cupItems);
 const bulbG=new T.IcosahedronGeometry(1,2);const bulbItems=gardens.filter((_,i)=>i%3===2).map(p=>({p:[p.x,p.y+.32*p.scale,p.z],s:[p.scale*.85,p.scale*.62,p.scale],a:rand()*6.28,c:coralColors[zone(p.z)][p.index%2]}));batch('Rounded_Coral_Cushions',bulbG,mat('#ffffff',{flatShading:true}),bulbItems);
 // Fan coral grows as a curved radial crown, distinct from the round plate gardens.
 function seaFan(){const pieces=[];const tube=(points,r)=>pieces.push(new T.TubeGeometry(new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p))),7,r,5,false));tube([[0,0,0],[0,.6,0],[.04,1.2,.06]],.075);
  for(let i=0;i<11;i++){const a=-1.12+i*.224,x=Math.sin(a)*1.8,y=.5+Math.cos(a)*2.3;const tip=[x,y,.18+Math.abs(x)*.12];tube([[0,.65,0],[x*.45,1.35,.07],tip],.038);for(let k=0;k<3;k++)tube([[x*.66,.85+(y-.85)*.66,.13],[x*.85+(k-1)*.1,y-.2,.20],[x+(k-1)*.22,y+.13-Math.abs(k-1)*.13,.23]],.022)}
  const g=mergeGeometries(pieces,false);pieces.forEach(p=>p.dispose());return g;
 }
 const fanSites=[[13,42,1.5,.7],[-19,-27,1.6,-.5],[29,-38,1.4,.4],[-26,-97,1.2,.5],[-33,-144,1.2,.5],[-8,-169,1.1,-.5],[-32,-192,1.9,-.8],[1,-183,2.1,.5],[-34,-224,1.7,-.6]];
 const bankHeight=(x,z)=>{const r=formations.find(([a,b,rx,,rz])=>Math.hypot((x-a)/rx,(z-b)/rz)<.56);return r?floorHeight(r[0],r[1])+r[3]*.71:floorHeight(x,z)};
 const fanItems=fanSites.map(([x,z,s,a],i)=>({p:[x,bankHeight(x,z),z],s:[s,s,s*.65],a,c:coralColors[zone(z)][i%2]}));batch('Curved_Sea_Fan_Groves',seaFan(),mat('#ffffff'),fanItems);
 // Keep the original two landmarks; no additional arches are introduced.
 function arch(name,x,z,width,height,c){const curve=new T.CatmullRomCurve3([new T.Vector3(x-width/2,floorHeight(x,z),z),new T.Vector3(x-width/2,height*.68,z),new T.Vector3(x,height,z),new T.Vector3(x+width/2,height*.64,z),new T.Vector3(x+width/2,floorHeight(x,z),z)]);const o=mesh(name,new T.TubeGeometry(curve,44,1.65,8,false),mat(c,{flatShading:true}));o.castShadow=true;for(const side of[-1,1])obstacles.push({x:x+side*width/2,z,rx:2.1,rz:2.1,y0:floorHeight(x,z),y1:height*.72,name});obstacles.push({x,z,rx:width*.26,rz:1.9,y0:height-2,y1:height+2,name:name+'-roof'});for(let j=0;j<8;j++){const p=curve.getPoint(.2+j*.085);const g=cupG;mesh(name+'-bloom-'+j,g,cupM,[p.x,p.y+1.05,p.z],[1.7,.9,1.7]).material=mat(j%2?palette.peach:palette.lilac,{side:T.DoubleSide})}}
 arch('Coral_Portal',0,-27,21,10.5,'#749b95');arch('Moon_Arc',-39,-165,18,9.5,'#8279a8');
 const giants=[[-31,-130,8.4,4.5],[20,-140,7.2,3.8],[-22,-137,10.8,6.4],[-8,-151,12,6.8],[-34,-164,8.8,5.3],[8,-174,8.2,4.2],[-38,-156,7.2,3.7],[19,-169,9.8,5.3],[-47,-145,8.5,4.9],[38,-159,9,5.3]];
 giants.forEach(([x,z,h,r],i)=>{const y=floorHeight(x,z),stem=mesh('Umbrella_Coral_Stem_'+i,new T.CylinderGeometry(.38,.82,h,9),mat(i%2?'#71899b':'#9a8dac'),[x,y+h/2,z]);stem.castShadow=true;obstacles.push({x,z,rx:1.2,rz:1.2,y0:y,y1:y+h,name:stem.name});for(let k=0;k<3;k++){const shade=[palette.lilac,palette.rose,palette.peach][i%3];const c=mesh('Umbrella_Coral_Canopy_'+i+'_'+k,cupG,mat(shade,{side:T.DoubleSide,emissive:shade,emissiveIntensity:.18}),[x,y+h+k*.45,z],[r-k*.9,1.4,r-k*.9]);c.castShadow=true}obstacles.push({x,z,rx:r*.85,rz:r*.85,y0:y+h-.4,y1:y+h+1.8,name:'canopy-'+i})});
 // Curved low plants cover banks throughout all headings, leaving a meandering lane.
 const leaves=[];for(let leaf=0;leaf<5;leaf++){const a=leaf*2.399,h=.7+(leaf%3)*.25;for(let k=0;k<8;k++){const v=(t,side)=>{const w=.11*Math.sin(Math.PI*t)+.015,lean=.65*t*t;return [Math.cos(a)*lean+Math.sin(a)*w*side,h*(t-.15*t*t*t),Math.sin(a)*lean-Math.cos(a)*w*side]};const t=k/8,u=(k+1)/8;leaves.push(...v(t,-1),...v(t,1),...v(u,1),...v(t,-1),...v(u,1),...v(u,-1))}}
 const leafG=new T.BufferGeometry();leafG.setAttribute('position',new T.Float32BufferAttribute(leaves,3));leafG.computeVertexNormals();const leafM=mat('#ffffff',{side:T.DoubleSide});const wind={value:0},old=leafM.onBeforeCompile;leafM.onBeforeCompile=s=>{old.call(leafM,s);s.uniforms.gardenTime=wind;s.vertexShader='uniform float gardenTime;\n'+s.vertexShader;s.vertexShader=s.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed.x+=sin(gardenTime*.7+instanceMatrix[3].z*.2)*position.y*position.y*.1;')};
 function laneDistance(x,z){let best=Infinity;for(let i=0;i<STOPS.length-1;i++){const a=STOPS[i].position,b=STOPS[i+1].position,dx=b[0]-a[0],dz=b[2]-a[2],t=T.MathUtils.clamp(((x-a[0])*dx+(z-a[2])*dz)/(dx*dx+dz*dz),0,1);best=Math.min(best,Math.hypot(x-a[0]-dx*t,z-a[2]-dz*t))}return best}
 const plants=[];for(let i=0;i<1800;i++){const x=(rand()-.5)*155,z=80-rand()*310;if(laneDistance(x,z)<3.5||obstacles.some(o=>Math.hypot((x-o.x)/o.rx,(z-o.z)/o.rz)<1.03))continue;const density=.5+.5*Math.sin(x*.11+z*.065)*Math.sin(z*.08);if(rand()>density*.85)continue;const s=.6+rand()*1.4;plants.push({p:[x,floorHeight(x,z),z],s:[s,s,s],a:rand()*6.28,c:i%3?palette.grass:'#8dad93'})}
 // Redistribute the existing plant budget: the bay becomes a true meadow,
 // while entrance return banks and the final fan overlook keep low vegetation.
 plants.splice(512);for(let i=0;i<plants.length;i++){const item=plants[i];if(i<200||i>=200&&i<260){let x,z,found=false;for(let attempt=0;attempt<50;attempt++){x=i<200?-12+rand()*49:-34+rand()*68;z=i<200?-92+rand()*43:35+rand()*46;if(laneDistance(x,z)>=4&&!obstacles.some(o=>Math.hypot((x-o.x)/o.rx,(z-o.z)/o.rz)<1.05)){found=true;break}}if(found)item.p=[x,floorHeight(x,z),z]}
  const v=zone(item.p[2]),k=item.s[0];item.s=v===2?[k*.85,k*3.2,k*.85]:[k,k*(v===0?.85:.65),k];item.c=v===2?(i%3?'#72ac95':'#b8c78d'):v===3?'#7b9fad':v===5?'#b5bc91':palette.grass;
 }batch('Sea_Feather_Meadows',leafG,leafM,plants);
 // Small shell-like original accents keep the near path alive without blocking it.
 const accents=[];for(let i=0;i<170;i++){const z=35-rand()*250,x=(rand()-.5)*95;if(obstacles.some(o=>Math.hypot((x-o.x)/o.rx,(z-o.z)/o.rz)<1))continue;accents.push({p:[x,floorHeight(x,z)+.05,z],s:[.17+rand()*.22,.10,.25+rand()*.2],a:rand()*6.28,c:i%2?palette.gold:palette.peach})}batch('Seabed_Shell_Accents',new T.IcosahedronGeometry(1,1),mat('#ffffff',{flatShading:true}),accents);
 const fishParts=[];function part(g,c){g=g.index?g.toNonIndexed():g;g.deleteAttribute('uv');const colors=[];for(let i=0;i<g.attributes.position.count;i++)colors.push(...new T.Color(c).toArray());g.setAttribute('color',new T.Float32BufferAttribute(colors,3));fishParts.push(g)}
 const body=new T.SphereGeometry(1,10,7);body.scale(.55,.13,.09);part(body,'#b5d4c4');const fins=new T.BufferGeometry();fins.setAttribute('position',new T.Float32BufferAttribute([-.43,0,0,-.76,.18,0,-.76,-.18,0,-.2,.08,0,.04,.22,0,.25,.08,0],3));fins.computeVertexNormals();part(fins,palette.gold);for(const z of[-.075,.075]){const eye=new T.SphereGeometry(.016,5,4);eye.translate(.35,.025,z);part(eye,'#183e49')}const fishG=mergeGeometries(fishParts,false);fishParts.forEach(g=>g.dispose());const fishM=mat('#ffffff',{vertexColors:true,side:T.DoubleSide});
 const schoolCentres=[[-6,4,6],[12,5,-34],[22,5,-63],[-17,6,-87],[5,6,-114],[-26,5,-137],[-15,7,-174],[14,5,48],[-12,5,-212],[4,8,-82],[-8,9,-121],[-24,8,-185],[3,8,-230]],fish=[];
 schoolCentres.forEach((p,j)=>{for(let i=0;i<(j>=9?18:24);i++){const a=rand()*6.28,r=rand()*(j>=9?6:4),s=(j>=9?.8:.55)+rand()*.35;fish.push({p:[p[0]+Math.cos(a)*r,p[1]+(rand()-.5)*1.6,p[2]+Math.sin(a)*r],s:[s,s*(zone(p[2])===1?.7:zone(p[2])===5?1.4:1),s],a:0,c:zone(p[2])===1?'#e3bd93':zone(p[2])===3?'#a7cbd5':zone(p[2])===4?'#d1b6c6':zone(p[2])===5?'#e1ca8f':'#b2cfbc',j,phase:rand()*6.28})}});const school=batch('Garden_Fish_Schools',fishG,fishM,fish);school.boundingSphere.radius+=4;
 // A single original manta silhouette glides through the open bay.
 const mantaP=[],mantaI=[];for(let j=0;j<9;j++)for(let i=0;i<17;i++){const u=i/16*2-1,v=j/8*2-1,width=(1-Math.abs(v)*.65);mantaP.push(u*width*2.5,.16*Math.cos(u*Math.PI)-.10*v*v,v*1.3)}for(let j=0;j<8;j++)for(let i=0;i<16;i++){const a=j*17+i;mantaI.push(a,a+17,a+1,a+1,a+17,a+18)}const mg=new T.BufferGeometry();mg.setAttribute('position',new T.Float32BufferAttribute(mantaP,3));mg.setIndex(mantaI);mg.computeVertexNormals();const manta=mesh('Original_Stylized_Manta',mg,mat('#62939b',{side:T.DoubleSide}),[9,8,-55]);const tailCurve=new T.CatmullRomCurve3([new T.Vector3(0,0,1),new T.Vector3(0,-.1,2.5),new T.Vector3(.5,-.3,4)]);const tail=new T.Mesh(new T.TubeGeometry(tailCurve,12,.035,5,false),manta.material);geoms.add(tail.geometry);manta.add(tail);
 const hemi=new T.HemisphereLight('#d8f2d4','#365779',2.5);scene.add(hemi,new T.AmbientLight('#c7d8ed',.55));const sun=new T.DirectionalLight('#ffe4b0',3.4);sun.position.set(-30,70,30);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-38,right:38,top:38,bottom:-38,near:.1,far:160});sun.shadow.normalBias=.04;sun.shadow.bias=-.0002;sun.shadow.intensity=.35;scene.add(sun,sun.target);const fill=new T.DirectionalLight('#a2dcda',1);fill.position.set(45,22,-80);scene.add(fill);
 // Infinite-looking directional envelope: no finite transparent water sheet.
 const skyM=new T.ShaderMaterial({side:T.BackSide,depthWrite:false,fog:false,uniforms:{time:wind},vertexShader:'varying vec3 d;void main(){d=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'varying vec3 d;uniform float time;void main(){vec3 r=normalize(d);float t=smoothstep(-.45,.85,r.y);vec3 c=mix(vec3(.020,.087,.13),vec3(.075,.30,.32),t);float glow=pow(max(0.,dot(r,normalize(vec3(-.3,.9,.15)))),16.);c+=vec3(.16,.20,.13)*glow;gl_FragColor=vec4(c,1.);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}'});mats.add(skyM);const sky=mesh('Continuous_Sea_Light',new T.SphereGeometry(280,24,16),skyM);sky.renderOrder=-50;sky.frustumCulled=false;
 scene.fog=new T.Fog('#165967',65,195);
 function resolve(p,previous=null){const q=p.slice();q[0]=T.MathUtils.clamp(q[0],-108,108);q[2]=T.MathUtils.clamp(q[2],-235,95);q[1]=T.MathUtils.clamp(q[1],floorHeight(q[0],q[2])+.55,16);const inside=(v,o)=>v[1]>o.y0-.55&&v[1]<o.y1+.55&&Math.hypot((v[0]-o.x)/(o.rx+.55),(v[2]-o.z)/(o.rz+.55))<1;
  for(const o of obstacles){if(!inside(q,o))continue;if(previous&&!inside(previous,o))return previous.slice();const a=Math.atan2((q[2]-o.z)/(o.rz+.6),(q[0]-o.x)/(o.rx+.6));q[0]=o.x+Math.cos(a)*(o.rx+.6);q[2]=o.z+Math.sin(a)*(o.rz+.6)}return q}
 function move(candidate,previous){let q=previous.slice();for(const i of[0,2,1]){const next=q.slice();next[i]=candidate[i];q=resolve(next,q)}return q}
 let paused=false;function update(time,camera){wind.value=time;sky.position.copy(camera.position);sun.position.set(camera.position.x-30,70,camera.position.z+30);sun.target.position.set(camera.position.x,-3,camera.position.z-15);sun.target.updateMatrixWorld();if(paused)return;for(let i=0;i<fish.length;i++){const f=fish[i],a=time*.17+f.j;dummy.position.fromArray(f.p);dummy.position.x+=Math.sin(a)*2.5;dummy.position.z+=Math.cos(a)*2;dummy.position.y+=Math.sin(time*.8+f.phase)*.17;dummy.rotation.set(0,Math.atan2(Math.sin(a)*2,Math.cos(a)*2.5),Math.sin(time*2+f.phase)*.03);dummy.scale.fromArray(f.s);dummy.updateMatrix();school.setMatrixAt(i,dummy.matrix)}school.instanceMatrix.needsUpdate=true;manta.position.set(9+Math.sin(time*.08)*15,8+Math.sin(time*.25)*.5,-60+Math.cos(time*.08)*12);manta.rotation.set(.05,Math.atan2(Math.sin(time*.08)*12,Math.cos(time*.08)*15),Math.sin(time*.6)*.08);manta.scale.y=1+Math.sin(time*1.2)*.28}
 const stats={version:STAGE_VERSION,habitats:STATION_HABITATS,reefVariants:6,coralInstances:branchItems.length+cupItems.length+bulbItems.length,artLanguage:'pastel-sculpted-reef-garden',originalProcedural:true,scansInThisScene:false,formations:formations.length,seaFans:fanItems.length,giantCorals:giants.length,fish:fish.length,plantTufts:plants.length,obstacles:obstacles.length,triangles:0};root.traverse(o=>{if(o.isMesh)stats.triangles+=(o.geometry.index?.count||o.geometry.attributes.position.count)/3*(o.isInstancedMesh?o.count:1)});
 return{root,resolve,move,update,stats,setPaused(v){paused=!!v},dispose(){batches.forEach(o=>o.dispose());geoms.forEach(g=>g.dispose());mats.forEach(m=>m.dispose());root.removeFromParent()}};
}
