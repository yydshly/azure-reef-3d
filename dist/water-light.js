import * as THREE from 'three';
// Artistic, deterministic water-light approximation. Not a calibrated optical simulation.
export function applyWaterLight(material,pattern,compiledShaders){
 if(!material.isMeshStandardMaterial)return;
 material.onBeforeCompile=shader=>{
  shader.uniforms.reefTime={value:0};shader.uniforms.reefCaustics={value:pattern};
  shader.vertexShader='varying vec3 vReefWorld;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>','vReefWorld = (modelMatrix * vec4(transformed, 1.0)).xyz;\n#include <project_vertex>');
  shader.fragmentShader='uniform float reefTime;\nuniform sampler2D reefCaustics;\nvarying vec3 vReefWorld;\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
vec2 waterUV = vReefWorld.xz * .15;
float lightA = texture2D(reefCaustics, waterUV + vec2(reefTime * .004, -reefTime * .003)).r;
float lightB = texture2D(reefCaustics, waterUV * 1.13 + vec2(-reefTime * .002, reefTime * .0035) + vec2(.37,.61)).r;
vec3 reefFace = normalize(cross(dFdx(vReefWorld), dFdy(vReefWorld)));
float upwardLight = mix(.35,1.0,abs(reefFace.y));
float depthLight = clamp(1.0-vReefWorld.y*.055,.65,1.0);
float waterFocus = lightA*.8 + lightB*.2;
diffuseColor.rgb *= .95 + waterFocus * 1.15 * upwardLight * depthLight;
diffuseColor.rgb *= mix(vec3(.84,.98,1.0),vec3(1.0),clamp(vReefWorld.y/7.0,0.0,1.0));`);
  compiledShaders.push(shader);
 };
 material.customProgramCacheKey=()=> 'reefWaterLightV3';
}
export function createWaterEnvelope(){
 const material=new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,fog:false,toneMapped:false,uniforms:{deepColor:{value:new THREE.Color('#064358')},upperColor:{value:new THREE.Color('#167f96')}},vertexShader:'varying vec3 waterDirection; void main(){waterDirection=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',fragmentShader:`uniform vec3 deepColor;uniform vec3 upperColor;varying vec3 waterDirection;
void main(){float overhead=smoothstep(-.08,.8,normalize(waterDirection).y);gl_FragColor=vec4(mix(deepColor,upperColor,overhead),1.0);
#include <colorspace_fragment>
}`});
 const envelope=new THREE.Mesh(new THREE.SphereGeometry(90,32,24),material);envelope.name='Water_color_field';envelope.renderOrder=-10;envelope.frustumCulled=false;return envelope;
}
