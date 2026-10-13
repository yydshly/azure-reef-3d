import * as T from 'three';
import {mergeGeometries} from './utils/BufferGeometryUtils.js';
import {CONTINUOUS_MASSES} from './continuous-layout.js';
import {floorHeight} from './exploration-world-data.js?v=layered-habitat-20261011-v1';

// Uses the existing CC0 Poly Haven boulder and project-authored coral geometry.
// Original scans, mesh bytes, maps and the six-stop tour remain untouched.
export function createContinuousReef({parent,rockScene,corals,configure}){
 const root=new T.Group();root.name='Continuous_Reef_20261012';parent.add(root);
 const geometries=new Set(),materials=new Set(),batches=[],dummy=new T.Object3D(),color=new T.Color();
 const timeUniform={value:0};let seed=68012,disposed=false,lastTime=0;
 const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
 function material(c,opts={}){const m=new T.MeshStandardMaterial({color:c,roughness:.92,...opts});configure(m);materials.add(m);return m;}
 function batch(name,g,m,items,cast=false){
  geometries.add(g);const mesh=new T.InstancedMesh(g,m,items.length);mesh.name=name;mesh.castShadow=cast;mesh.receiveShadow=true;
  for(let i=0;i<items.length;i++){const p=items[i];dummy.position.fromArray(p.p);dummy.rotation.set(...(p.r||[0,p.a||0,0]));if(p.q)dummy.quaternion.fromArray(p.q);dummy.scale.fromArray(p.s||[1,1,1]);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);if(p.c)mesh.setColorAt(i,color.set(p.c));}
  mesh.computeBoundingSphere();root.add(mesh);batches.push(mesh);return mesh;
 }
 rockScene.updateMatrixWorld(true);let sourceRock;rockScene.traverse(o=>{if(o.isMesh&&!sourceRock)sourceRock=o});
 if(!sourceRock)throw Error('Existing CC0 boulder missing');
 const rockG=sourceRock.geometry.clone().applyMatrix4(sourceRock.matrixWorld);rockG.computeBoundingBox();
 const box=rockG.boundingBox,size=box.getSize(new T.Vector3()),center=box.getCenter(new T.Vector3()),a=rockG.attributes.position;
 for(let i=0;i<a.count;i++)a.setXYZ(i,(a.getX(i)-center.x)/size.x*2,(a.getY(i)-box.min.y)/size.y,(a.getZ(i)-center.z)/size.z*2);
 rockG.computeVertexNormals();rockG.computeBoundingBox();rockG.computeBoundingSphere();
 const rockM=sourceRock.material.clone();rockM.color.set('#e4dfc8');rockM.roughness=.96;configure(rockM);materials.add(rockM);
 const rockItems=[],attachments=[];
 for(const r of CONTINUOUS_MASSES){
  // Two intersecting, differently oriented three-dimensional boulders form a
  // buttress. Their embedded bases create connected rock, with readable relief.
  for(let j=0;j<2;j++){
   const x=r.x+(j?-.24:.12)*r.rx,z=r.z+(j?.22:-.12)*r.rz;
   const lowest=Math.min(floorHeight(x,z),...Array.from({length:12},(_,i)=>floorHeight(x+Math.cos(i/12*Math.PI*2)*r.rx*.9,z+Math.sin(i/12*Math.PI*2)*r.rz*.9)));
   rockItems.push({p:[x,lowest-r.h*.30,z],s:[r.rx*(j?.60:.72),r.h*(j?.78:1.12),r.rz*(j?.67:.72)],a:r.seed*.31+j*1.23,c:j?'#f2eddd':'#ffffff'});
  }
 }
 const rock=batch('Textured_Interlocking_Reef_Buttresses',rockG,rockM,rockItems,true);
 root.updateMatrixWorld(true);
 const grounding=[],sample=new T.Vector3(),groundMatrix=new T.Matrix4();
 for(let i=0;i<rockItems.length;i++){rock.getMatrixAt(i,groundMatrix);let minimum=Infinity,buried=0;for(let j=0;j<a.count;j+=4){sample.fromBufferAttribute(a,j).applyMatrix4(groundMatrix);const clearance=sample.y-floorHeight(sample.x,sample.z);minimum=Math.min(minimum,clearance);if(clearance<-.15)buried++;}if(minimum>-.15)throw Error('Reef base lacks seabed contact '+i);grounding.push({instance:i,minVertexClearance:minimum,buriedSampleVertices:buried});}
 const ray=new T.Raycaster(),down=new T.Vector3(0,-1,0),matrix=new T.Matrix4(),normalMatrix=new T.Matrix3();
 function seat(x,z){ray.set(new T.Vector3(x,55,z),down);const hit=ray.intersectObject(rock,false)[0];if(!hit)return null;rock.getMatrixAt(hit.instanceId,matrix);matrix.premultiply(rock.matrixWorld);const normal=hit.face.normal.clone().applyNormalMatrix(normalMatrix.getNormalMatrix(matrix));if(normal.y<.38)return null;return hit.point.y-.05;}
 const branches=[[],[]],plates=[],mounds=[],fans=[],sponges=[];
 for(const r of CONTINUOUS_MASSES){
  for(let j=0;j<32;j++){
   const ang=random()*Math.PI*2,rad=Math.sqrt(random())*.72,x=r.x+Math.cos(ang)*r.rx*rad,z=r.z+Math.sin(ang)*r.rz*rad,y=seat(x,z);
   if(y===null)continue;attachments.push({x,y,z});const s=.7+random()*1.4;
   const item={p:[x,y,z],s:[s,s,s],a:random()*6.28,c:['#a78665','#b19a78','#7d9e89','#977e80'][j%4]};
   if(j%4===0)branches[Math.floor(j/4)%2].push({...item,s:[s*1.4,s*1.7,s*1.4]});
   if(j%4===1)plates.push({...item,s:[s*1.6,s*1.1,s*1.4]});
   if(j%4===2)mounds.push({...item,s:[s*1.0,s*.75,s*1.1]});
   if(j%7===0)fans.push({...item,s:[s*1.0,s*1.5,s],c:j%2?'#a47764':'#898198'});
   if(j%8===1)sponges.push({...item,s:[s*.8,s*1.1,s*.8],c:'#a68d60'});
  }
 }
 // Encrusting communities also colonize the sloping faces. Place their bases
 // on an actual triangle and align their growth axes with its outward normal.
 for(const r of CONTINUOUS_MASSES)for(let j=0;j<19;j++){
  const angle=random()*6.28,base=floorHeight(r.x,r.z),height=base+r.h*(.08+random()*.62);
  const start=new T.Vector3(r.x+Math.cos(angle)*r.rx*2.2,height,r.z+Math.sin(angle)*r.rz*2.2),aim=new T.Vector3(r.x,height,r.z);
  ray.set(start,aim.sub(start).normalize());const hit=ray.intersectObject(rock,false)[0];if(!hit)continue;
  rock.getMatrixAt(hit.instanceId,matrix);matrix.premultiply(rock.matrixWorld);const n=hit.face.normal.clone().applyNormalMatrix(normalMatrix.getNormalMatrix(matrix));
  const q=new T.Quaternion().setFromUnitVectors(new T.Vector3(0,1,0),n).multiply(new T.Quaternion().setFromAxisAngle(new T.Vector3(0,1,0),random()*6.28));
  const s=1.1+random()*1.8,item={p:hit.point.clone().addScaledVector(n,-.065).toArray(),q:q.toArray(),s:[s,s*.68,s],c:['#b49b73','#9aa588','#ad8273','#809d8f'][j%4]};
  (j%3===0?plates:mounds).push(item);attachments.push({x:hit.point.x,y:hit.point.y,z:hit.point.z,flank:true});
 }
 // The original branching colony is normalized once and shared by all copies.
 corals.updateMatrixWorld(true);let k=0;
 corals.traverse(o=>{if(!o.isMesh)return;const g=o.geometry.clone().applyMatrix4(o.matrixWorld);g.computeBoundingBox();const b=g.boundingBox,s=b.getSize(new T.Vector3()),c=b.getCenter(new T.Vector3()),p=g.attributes.position,scale=Math.max(s.x,s.y,s.z);
  for(let i=0;i<p.count;i++)p.setXYZ(i,(p.getX(i)-c.x)/scale*2,(p.getY(i)-b.min.y)/scale*2,(p.getZ(i)-c.z)/scale*2);g.computeVertexNormals();
  const items=branches[k%2];if(items.length)batch('Project_Authored_Branching_Colonies_'+k,g,material('#b8ad90'),items);else g.dispose();k++;
 });
 // Foliose colonies: overlapping ruffled cups rather than isolated flat disks.
 const pp=[],pc=[];for(let layer=0;layer<4;layer++)for(let i=0;i<28;i++){
  const v=(angle,rad)=>{const r=rad*(.70+layer*.17)*(1+.08*Math.sin(angle*7+layer));return [Math.cos(angle)*r,.12+layer*.18+.13*rad*rad+.05*Math.sin(angle*5+layer),Math.sin(angle)*r]};
  const u=i/28*Math.PI*2,w=(i+1)/28*Math.PI*2;pp.push(...v(u,.13),...v(u,1),...v(w,1),...v(u,.13),...v(w,1),...v(w,.13));
 }
 const plateG=new T.BufferGeometry();plateG.setAttribute('position',new T.Float32BufferAttribute(pp,3));plateG.computeVertexNormals();batch('Ruffled_Foliose_Gardens',plateG,material('#b7a184',{side:T.DoubleSide}),plates);
 const moundG=new T.SphereGeometry(1,20,12),mp=moundG.attributes.position;
 for(let i=0;i<mp.count;i++){const x=mp.getX(i),y=mp.getY(i),z=mp.getZ(i),b=1+.06*Math.sin(x*13+y*9)*Math.sin(z*14-y*7);mp.setXYZ(i,x*b,(y+1)*.52*b,z*b)}moundG.computeVertexNormals();
 const moundM=material('#a89b78'),prior=moundM.onBeforeCompile;moundM.onBeforeCompile=s=>{prior.call(moundM,s);s.fragmentShader=s.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
 float maze=sin(vExhibitWorld.x*16.+sin(vExhibitWorld.z*9.))*sin(vExhibitWorld.y*15.+cos(vExhibitWorld.x*11.));
 diffuseColor.rgb*=.80+.20*smoothstep(-.8,.4,maze);`)};moundM.customProgramCacheKey=()=> 'continuous-coral-maze-v1';batch('Massive_Coral_Gardens',moundG,moundM,mounds);
 const fp=[];function segment(ax,ay,bx,by,width){const z=.12*Math.sin(ay*2+ax);fp.push(ax-width,ay,z,ax+width,ay,z,bx+width*.7,by,.12*Math.sin(by*2+bx),ax-width,ay,z,bx+width*.7,by,.12*Math.sin(by*2+bx),bx-width*.7,by,.12*Math.sin(by*2+bx));}
 segment(0,0,0,1.6,.024);for(let i=0;i<21;i++){const y=.10+i*.061,w=.84*Math.sin((i+1)/23*Math.PI);for(const side of [-1,1]){segment(0,y,w*side,y+.50,.012);for(let j=1;j<7;j++)segment(w*side*j/7,y+.50*j/7,side*(w*j/7+.13),y+.50*j/7+.22,.007)}}
 const fanG=new T.BufferGeometry();fanG.setAttribute('position',new T.Float32BufferAttribute(fp,3));fanG.computeVertexNormals();batch('Fine_Branching_Sea_Fans',fanG,material('#b38e77',{side:T.DoubleSide}),fans);
 const tubeP=[],tubeI=[];for(let j=0;j<4;j++){const offset=tubeP.length/3,h=.65+j*.19,cx=Math.cos(j*2.399)*.28,cz=Math.sin(j*2.399)*.28;for(let r=0;r<4;r++)for(let i=0;i<16;i++){const ang=i/16*Math.PI*2,rad=[.16,.21,.13,.13][r];tubeP.push(cx+Math.cos(ang)*rad+h*.14*(r?1:0),[0,h,h,h-.2][r],cz+Math.sin(ang)*rad)}for(let r=0;r<3;r++)for(let i=0;i<16;i++){const aa=offset+r*16+i,b=offset+r*16+(i+1)%16;tubeI.push(aa,aa+16,b,b,aa+16,b+16)}}
 const tubeG=new T.BufferGeometry();tubeG.setAttribute('position',new T.Float32BufferAttribute(tubeP,3));tubeG.setIndex(tubeI);tubeG.computeVertexNormals();batch('Hollow_Tube_Sponges',tubeG,material('#b39364',{side:T.DoubleSide}),sponges);
 // Fish are world-positioned and continuously steer around school centres.
 // The shader bends the tapered tail, including during turns. No camera-follow life.
 const parts=[];function addPart(g,c){g=g.index?g.toNonIndexed():g;g.deleteAttribute('uv');const values=[];for(let i=0;i<g.attributes.position.count;i++)values.push(...new T.Color(c).toArray());g.setAttribute('color',new T.Float32BufferAttribute(values,3));parts.push(g);}
 const body=new T.SphereGeometry(1,16,10),bp=body.attributes.position;for(let i=0;i<bp.count;i++){const x=bp.getX(i),taper=1-.40*Math.max(-x,0);bp.setXYZ(i,x*.60,bp.getY(i)*.13*taper,bp.getZ(i)*.09*taper)}body.computeVertexNormals();addPart(body,'#b7cfca');
 const fin=new T.BufferGeometry();fin.setAttribute('position',new T.Float32BufferAttribute([-.49,0,0,-.81,.17,0,-.81,-.17,0,-.24,.07,0,.07,.20,0,.30,.07,0,-.24,-.07,0,.04,-.17,0,.28,-.07,0,.22,-.025,.07,-.04,-.08,.17,-.17,.01,.07,.22,-.025,-.07,-.17,.01,-.07,-.04,-.08,-.17],3));fin.computeVertexNormals();addPart(fin,'#b3a865');
 for(const z of [-.075,.075]){const eye=new T.SphereGeometry(.015,7,5);eye.translate(.40,.022,z);addPart(eye,'#10222b')}
 const fishG=mergeGeometries(parts,false);parts.forEach(g=>g.dispose());
 const fishM=material('#ffffff',{vertexColors:true,side:T.DoubleSide,roughness:.62,metalness:.12}),fishPrior=fishM.onBeforeCompile;
 fishM.onBeforeCompile=s=>{fishPrior.call(fishM,s);s.uniforms.reefSchoolTime=timeUniform;s.vertexShader='uniform float reefSchoolTime;\n'+s.vertexShader;s.vertexShader=s.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
 transformed.z+=sin(reefSchoolTime*5.+instanceMatrix[3].z*.63)*pow(max(0.,-position.x-.12),1.5)*.20;`)};fishM.customProgramCacheKey=()=> 'continuous-tail-motion-v1';
 const schools=[{c:[-10,5.8,-16],n:28,r:4,s:.72},{c:[20,7,-57],n:32,r:4,s:.68},{c:[-17,6,-105],n:25,r:4,s:.72},{c:[18,5,-148],n:30,r:4,s:.65},{c:[19,4,-203],n:38,r:4,s:.78},{c:[18,2,-251],n:32,r:4,s:.78},{c:[-15,-3,-307],n:34,r:4,s:.88},{c:[21,-9,-363],n:29,r:4,s:.92},{c:[-10,-12,-418],n:38,r:4,s:1}];
 const fish=[];for(const [j,school]of schools.entries())for(let i=0;i<school.n;i++){const angle=random()*6.28,rad=Math.sqrt(random())*school.r*.70,scale=school.s*(.78+random()*.4);fish.push({p:[school.c[0]+Math.cos(angle)*rad,school.c[1]+(random()-.5)*2,school.c[2]+Math.sin(angle)*rad],s:[scale,scale,scale],a:0,c:i%7===0?'#cbb58a':i%3?'#92b6b5':'#c0c4ae',phase:random()*6.28,j});}
 const fishMesh=batch('Route_Wide_Steering_Fish_Schools',fishG,fishM,fish);fishMesh.boundingSphere.radius+=6;
 root.userData={revision:'continuous-reef-v1',synthetic:true,measuredSite:false,source:'https://polyhaven.com/a/boulder_01',license:'CC0',cameraAttached:false,formations:CONTINUOUS_MASSES.length,fish:fish.length,seatedColonies:attachments.length,newAssetDownloads:0};
 const budget={draws:batches.length,instances:batches.reduce((s,m)=>s+m.count,0),triangles:batches.reduce((s,m)=>s+(m.geometry.index?.count||m.geometry.attributes.position.count)/3*m.count,0),geometryBytes:[...geometries].reduce((s,g)=>s+Object.values(g.attributes).reduce((s,a)=>s+a.array.byteLength,0)+(g.index?.array.byteLength||0),0)};
 function update(time){if(disposed)return;lastTime=time;timeUniform.value=time;for(let i=0;i<fish.length;i++){const item=fish[i],phase=time*.16+item.j*.9,dx=Math.cos(phase)*4.1,dz=-Math.sin(phase)*3.1;dummy.position.fromArray(item.p);dummy.position.x+=Math.sin(phase)*4.1;dummy.position.z+=Math.cos(phase)*3.1;dummy.position.y+=Math.sin(time*.75+item.phase)*.22;dummy.rotation.set(0,Math.atan2(-dz,dx),Math.sin(time*2.2+item.phase)*.035);dummy.scale.fromArray(item.s);dummy.updateMatrix();fishMesh.setMatrixAt(i,dummy.matrix)}fishMesh.instanceMatrix.needsUpdate=true;}
 function dispose(){if(disposed)return;disposed=true;root.removeFromParent();batches.forEach(m=>m.dispose());geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());const maps=new Set();rockScene.traverse(o=>{if(o.isMesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material]){for(const v of Object.values(m))if(v?.isTexture)maps.add(v);m.dispose();}}});maps.forEach(m=>m.dispose());}
 return {root,budget,update,dispose,getState:()=>({...root.userData,budget,grounding,disposed,lastTime})};
}
