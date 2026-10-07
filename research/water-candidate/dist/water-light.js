import * as THREE from 'three';
// Illustrative homogeneous water, in scene units; not measured ocean coefficients.
// The same linear-radiance asymptote is used for surfaces and the surrounding water.
const waterField = `
vec3 reefWaterRadiance(vec3 direction) {
 float overhead = smoothstep(-.12, .85, direction.y);
 return mix(vec3(.004,.040,.075), vec3(.018,.18,.24), overhead);
}`;
export function applyWaterLight(material,pattern,compiledShaders){
 if(!material.isMeshStandardMaterial)return;
 material.onBeforeCompile=shader=>{
  shader.uniforms.reefTime={value:0};shader.uniforms.reefCaustics={value:pattern};
  shader.vertexShader='varying vec3 vReefWorld;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>','vReefWorld = (modelMatrix * vec4(transformed, 1.0)).xyz;\n#include <project_vertex>');
  shader.fragmentShader='uniform float reefTime;\nuniform sampler2D reefCaustics;\nvarying vec3 vReefWorld;\n'+waterField+'\n'+shader.fragmentShader;
  // Modulate direct diffuse illumination, not albedo: shaded surfaces do not glow.
  shader.fragmentShader=shader.fragmentShader.replace('#include <lights_fragment_end>',`#include <lights_fragment_end>
vec2 waterUV = vReefWorld.xz * .15;
float lightA = texture2D(reefCaustics, waterUV + vec2(reefTime * .004, -reefTime * .003)).r;
float lightB = texture2D(reefCaustics, mat2(.8,-.6,.6,.8)*waterUV * 1.37 + vec2(-reefTime * .002, reefTime * .0035) + vec2(.37,.61)).r;
vec3 reefWorldNormal = inverseTransformDirection(normal, viewMatrix);
float upwardLight = max(reefWorldNormal.y,0.0);
float waterDepth = max(8.0-vReefWorld.y,0.0);
float reefDistance = length(cameraPosition-vReefWorld);
float focusVisibility = exp(-waterDepth*.055) * exp(-reefDistance*.028);
float waterFocus = lightA*.6 + lightB*.4;
vec3 downTransmission = exp(-vec3(.020,.008,.004)*waterDepth);
reflectedLight.directDiffuse *= downTransmission * (1.0 + waterFocus*.55*upwardLight*focusVisibility);
reflectedLight.directSpecular *= downTransmission;`);
  // Beer-law form before tone mapping/output conversion; no second RGB fog pass.
  shader.fragmentShader=shader.fragmentShader.replace('#include <opaque_fragment>',`
vec3 reefView = vReefWorld-cameraPosition;
vec3 transmission = exp(-vec3(.065,.035,.025)*length(reefView));
outgoingLight = outgoingLight*transmission + reefWaterRadiance(normalize(reefView))*(vec3(1.0)-transmission);
#include <opaque_fragment>`).replace('#include <fog_fragment>','');
  compiledShaders.push(shader);
 };
 material.customProgramCacheKey=()=> 'reefWaterLightV4';
}
export function createWaterEnvelope(){
 const material=new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,fog:false,toneMapped:true,vertexShader:'varying vec3 waterDirection; void main(){waterDirection=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',fragmentShader:`varying vec3 waterDirection;
${waterField}
void main(){gl_FragColor=vec4(reefWaterRadiance(normalize(waterDirection)),1.0);
#include <tonemapping_fragment>
#include <colorspace_fragment>
}`});
 const envelope=new THREE.Mesh(new THREE.SphereGeometry(90,32,24),material);envelope.name='Water_color_field';envelope.renderOrder=-10;envelope.frustumCulled=false;return envelope;
}
