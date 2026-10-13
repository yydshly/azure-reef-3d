import * as THREE from 'three';
// All environmental geometry/light here is synthetic illustration in uncalibrated units.
// The captured scan is not altered or used to invent surrounding measured terrain.
export const OCEAN_VIEWS=Object.freeze({near:{position:[4.4,1.8,5.6],target:[0,-.12,0]},wide:{position:[7.2,3.2,12],target:[6,2,-12]}});
const waterField=`vec3 exhibitWater(vec3 d){
 float depth=smoothstep(245.,415.,-cameraPosition.z)*.62+smoothstep(4.,34.,-cameraPosition.y)*.38;
 vec3 lower=mix(vec3(.007,.052,.075),vec3(.002,.024,.057),depth);
 vec3 upper=mix(vec3(.038,.215,.26),vec3(.012,.105,.16),depth);
 float overhead=smoothstep(-.58,.92,d.y);
 float sun=pow(max(0.,dot(d,normalize(vec3(-.45,.86,.25)))),22.);
 return mix(lower,upper,overhead)+vec3(.012,.021,.019)*sun*(1.-depth*.7);
}`;
export function createScanOcean(scene,pattern){
 const group=new THREE.Group();group.name='Synthetic_Underwater_Context';group.userData={synthetic:true,measuredSite:false};scene.add(group);const compiled=[],mode={value:1},currentTime={value:0};
 function configure(material,{sand=false,sandBounds=null}={}){
  const sandEdge=sand?{bounds:new THREE.Vector4(sandBounds.min.x,sandBounds.max.x,sandBounds.min.z,sandBounds.max.z),width:.25*Math.min(sandBounds.max.x-sandBounds.min.x,sandBounds.max.z-sandBounds.min.z)}:null;
  const previous=material.onBeforeCompile,previousKey=material.customProgramCacheKey();
  material.onBeforeCompile=shader=>{previous.call(material,shader);shader.uniforms.exhibitOceanMode=mode;shader.uniforms.exhibitOceanTime=currentTime;shader.uniforms.exhibitCaustics={value:pattern};shader.vertexShader='varying vec3 vExhibitWorld;\n'+shader.vertexShader;shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>','vec4 exhibitLocal=vec4(transformed,1.);\n#ifdef USE_INSTANCING\nexhibitLocal=instanceMatrix*exhibitLocal;\n#endif\nvExhibitWorld=(modelMatrix*exhibitLocal).xyz;\n#include <project_vertex>');shader.fragmentShader='uniform float exhibitOceanMode;\nuniform float exhibitOceanTime;\nuniform sampler2D exhibitCaustics;\nvarying vec3 vExhibitWorld;\n'+waterField+'\n'+shader.fragmentShader;
   if(sand)shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
float ripple=.5+.5*sin(vExhibitWorld.x*6.8+sin(vExhibitWorld.z*.23)*2.4+sin(vExhibitWorld.x*.09)*3.);
float grain=fract(sin(dot(floor(vExhibitWorld.xz*180.),vec2(127.1,311.7)))*43758.5453);
diffuseColor.rgb*=.93+.035*ripple+.035*grain;`);
   shader.fragmentShader=shader.fragmentShader.replace('#include <lights_fragment_end>',`#include <lights_fragment_end>
if(exhibitOceanMode>.5){
 vec2 uv=vExhibitWorld.xz*.24;
 float waves=texture2D(exhibitCaustics,uv+vec2(exhibitOceanTime*.004,exhibitOceanTime*-.003)).r;
 vec3 worldNormal=inverseTransformDirection(normal,viewMatrix);
 float bottomDepth=max(-vExhibitWorld.y,0.);
 reflectedLight.directDiffuse*=(1.+waves*.27*max(worldNormal.y,0.))*mix(1.,.42,smoothstep(53.,69.,-vExhibitWorld.z))*mix(1.,1.65,smoothstep(128.,168.,-vExhibitWorld.z))*exp(-bottomDepth*.024);
}`);
   shader.fragmentShader=shader.fragmentShader.replace('#include <opaque_fragment>',`if(exhibitOceanMode>.5){
 vec3 ray=vExhibitWorld-cameraPosition;
 float deepWater=smoothstep(240.,415.,-cameraPosition.z);
 vec3 transmission=exp(-mix(vec3(.026,.013,.010),vec3(.038,.026,.021),deepWater)*length(ray));
 outgoingLight=outgoingLight*transmission+exhibitWater(normalize(ray))*(vec3(1.)-transmission);
}
#include <opaque_fragment>`).replace('#include <fog_fragment>','');
   if(sand){
    shader.uniforms.exhibitSandBounds={value:sandEdge.bounds};shader.uniforms.exhibitSandEdgeWidth={value:sandEdge.width};
    shader.vertexShader='varying vec2 vExhibitSandLocal;\n'+shader.vertexShader;
    shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvExhibitSandLocal=position.xz;');
    shader.fragmentShader='varying vec2 vExhibitSandLocal;\nuniform vec4 exhibitSandBounds;\nuniform float exhibitSandEdgeWidth;\n'+shader.fragmentShader;
    const attenuation='outgoingLight=outgoingLight*transmission+exhibitWater(normalize(ray))*(vec3(1.)-transmission);';
    shader.fragmentShader=shader.fragmentShader.replace(attenuation,attenuation+'\nfloat sandEdgeDistance=min(min(vExhibitSandLocal.x-exhibitSandBounds.x,exhibitSandBounds.y-vExhibitSandLocal.x),min(vExhibitSandLocal.y-exhibitSandBounds.z,exhibitSandBounds.w-vExhibitSandLocal.y));\nfloat sandInterior=smoothstep(0.,exhibitSandEdgeWidth,sandEdgeDistance);\noutgoingLight=mix(exhibitWater(normalize(ray)),outgoingLight,sandInterior);');
   }
   compiled.push(shader);
   const releaseShader=()=>{const i=compiled.indexOf(shader);if(i>=0)compiled.splice(i,1);material.removeEventListener('dispose',releaseShader);};material.addEventListener('dispose',releaseShader);
  };material.customProgramCacheKey=()=>previousKey+'_exhibitOcean2_'+sand+(sand?'_sandEdge1':'');
 }
 const envelopeMaterial=new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,fog:false,toneMapped:true,vertexShader:'varying vec3 dir;void main(){dir=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'varying vec3 dir;\n'+waterField+'\nvoid main(){gl_FragColor=vec4(exhibitWater(normalize(dir)),1.);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}'});
 const envelope=new THREE.Mesh(new THREE.SphereGeometry(180,32,20),envelopeMaterial);envelope.name='Synthetic_Water_Volume';envelope.renderOrder=-10;envelope.frustumCulled=false;group.add(envelope);
 const groundGeo=new THREE.PlaneGeometry(150,210,60,84);groundGeo.rotateX(-Math.PI/2);const p=groundGeo.attributes.position;
 for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getZ(i)-40;p.setZ(i,z);const d=Math.hypot(x,z),w=THREE.MathUtils.smoothstep(d,3,11);p.setY(i,-.98+w*(.16*Math.sin(x*.22+z*.1)+.09*Math.sin(z*.35)));}groundGeo.computeVertexNormals();groundGeo.computeBoundingBox();
 const sandMaterial=new THREE.MeshStandardMaterial({color:'#9e9672',roughness:.98});configure(sandMaterial,{sand:true,sandBounds:groundGeo.boundingBox});const ground=new THREE.Mesh(groundGeo,sandMaterial);ground.name='Synthetic_Receding_Sand';ground.receiveShadow=true;group.add(ground);
 // Remote low weathered silhouettes establish scale/depth; no ring at the scan foot.
 const rocks=[];
 const surfaceUniforms={time:{value:0}};const surfaceMaterial=new THREE.ShaderMaterial({uniforms:surfaceUniforms,side:THREE.DoubleSide,transparent:true,opacity:.6,depthWrite:false,toneMapped:true,vertexShader:'varying vec2 uvv;void main(){uvv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:`varying vec2 uvv;uniform float time;void main(){vec2 p=uvv*72.;float a=sin(p.x*1.4+sin(p.y*.7)+time*.13);float b=sin(p.y*1.8+sin(p.x*.5)-time*.1);float light=pow(max(0.,a*b),3.);float edgeDistance=min(min(uvv.x,1.-uvv.x)*180.,min(uvv.y,1.-uvv.y)*250.);float edgeOpacity=smoothstep(0.,48.,edgeDistance);gl_FragColor=vec4(vec3(.045,.20,.23)+vec3(.022,.037,.033)*light,.25*edgeOpacity);\n#include <tonemapping_fragment>\n#include <colorspace_fragment>\n}`});
 const surface=new THREE.Mesh(new THREE.PlaneGeometry(180,250),surfaceMaterial);surface.rotation.x=Math.PI/2;surface.scale.set(4,4,1);surface.position.set(0,12,-220);surface.name='Synthetic_Overhead_Surface';group.add(surface);
 let seed=9345;const rand=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};const coords=[];for(let i=0;i<110;i++)coords.push((rand()-.5)*50,rand()*8,(rand()-.5)*120-35);const particleGeo=new THREE.BufferGeometry();particleGeo.setAttribute('position',new THREE.Float32BufferAttribute(coords,3));const particles=new THREE.Points(particleGeo,new THREE.PointsMaterial({color:'#d3e7d9',size:.018,transparent:true,opacity:.24,depthWrite:false}));particles.name='Synthetic_Suspended_Particles';group.add(particles);
 const hemi=new THREE.HemisphereLight('#d1e8e7','#345258',1.6);group.add(hemi);const sun=new THREE.DirectionalLight('#fff1d0',2.8);sun.position.set(-6,9,6);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-34,right:34,top:34,bottom:-34,near:.2,far:160});sun.shadow.normalBias=.015;sun.shadow.bias=-.0002;sun.shadow.intensity=.48;group.add(sun,sun.target);
 return {group,configure,ground,rocks,setEnabled(enabled){group.visible=enabled;mode.value=enabled?1:0},update(time,camera){currentTime.value=time;surfaceUniforms.time.value=time;envelope.position.copy(camera.position);sun.position.set(camera.position.x-25,65,camera.position.z+28);sun.target.position.set(camera.position.x,-10,camera.position.z-16);sun.target.updateMatrixWorld();particles.rotation.y=Math.sin(time*.018)*.018;},userData:{synthetic:true,floorY:-.98,nearestRemoteRockCenter:Math.hypot(-11,-16),scanVerticesEdited:false}};
}
