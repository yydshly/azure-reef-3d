import {SHOULDER_URL,SUBSTRATE_URL} from './inhabited-version.js?v=inhabited-20261007-r1';
import * as THREE from 'three';
import {GLTFLoader} from './vendor/GLTFLoader.js';
// Reusable original asset, three deliberately staggered rigid compositions.
// These are interpreted scene units, not surveyed colonies or species records.
export const REEF_LAYOUT=[
 {id:'NearLeft',position:[-4.8,.09174240518222349,-10],yaw:1.3,omit:'Attached_small_fan_form'},
 {id:'NearRight',position:[4.8,.19078407404906897,-8.5],yaw:-2.6,omit:'Attached_reticulate_fan_form'},
 {id:'Middle',position:[-4.8,-.06576677229367059,-26],yaw:-.2}
];
export const RETAINED_NEAR_BRANCHES=[0,1,3,12,16];
export function composeReef(root,asset){
 const remove=[];root.traverse(o=>{const m=/^Coral_Staghorn_Thicket_(\d+)$/.exec(o.name);if(m&&!RETAINED_NEAR_BRANCHES.includes(Number(m[1])))remove.push(o)});remove.forEach(o=>o.removeFromParent());
 for(const cfg of REEF_LAYOUT){const group=asset.clone(true);group.position.set(...cfg.position);group.rotation.y=cfg.yaw;group.name='Inhabited_'+cfg.id;
  if(cfg.omit)group.getObjectByName(cfg.omit)?.removeFromParent();
  group.traverse(o=>{if(o!==group)o.name='Inhabited_'+cfg.id+'_'+o.name;if(o.name.includes('Attached_small_fan'))o.userData.qualityOptional=true;});root.add(group);
 }
 root.traverse(o=>{if(o.isMesh&&/(Hardbottom|Limestone)/.test(o.name)&&!o.name.startsWith('Inhabited_')){o.material=o.material.clone();o.material.userData.substrateLink=true;}});
 root.updateMatrixWorld(true);
}
export async function addShoulder(root){
 const {scene}=await new GLTFLoader().loadAsync(SHOULDER_URL);
 const texture=await new THREE.TextureLoader().loadAsync(SUBSTRATE_URL);texture.colorSpace=THREE.SRGBColorSpace;texture.wrapS=texture.wrapT=THREE.MirroredRepeatWrapping;texture.anisotropy=4;
 composeReef(root,scene);return {substrateTexture:texture};
}
export function applySubstrateLink(material,texture){
 if(!material.userData.substrateLink)return;
 const previous=material.onBeforeCompile,previousKey=material.customProgramCacheKey;
 const nearest=REEF_LAYOUT.map(c=>`length(vReefWorld.xz-vec2(${c.position[0].toFixed(8)},${c.position[2].toFixed(8)}))`).reduce((a,b)=>`min(${a},${b})`);
 material.onBeforeCompile=shader=>{previous(shader);shader.uniforms.reefSubstrate={value:texture};
  shader.fragmentShader='uniform sampler2D reefSubstrate;\n'+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <normal_fragment_maps>',`#include <normal_fragment_maps>
vec3 substrateNormal = abs(inverseTransformDirection(normal, viewMatrix));
vec3 substrateWeights = pow(substrateNormal, vec3(4.0));
substrateWeights /= max(dot(substrateWeights, vec3(1.0)), .0001);
vec3 substrateColor = texture2D(reefSubstrate, vReefWorld.yz / .60).rgb * substrateWeights.x
 + texture2D(reefSubstrate, vReefWorld.xz / .60).rgb * substrateWeights.y
 + texture2D(reefSubstrate, vReefWorld.xy / .60).rgb * substrateWeights.z;
float substrateDistance = ${nearest};
float substrateBlend = 1.0-smoothstep(4.0,10.0,substrateDistance);
diffuseColor.rgb = mix(diffuseColor.rgb,substrateColor,substrateBlend*.85);
`);
 };
 material.customProgramCacheKey=()=>previousKey.call(material)+'_inhabitedSubstrateR1';
}
