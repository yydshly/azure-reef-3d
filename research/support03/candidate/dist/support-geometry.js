import {GLTFLoader} from './vendor/GLTFLoader.js';
export const SUPPORT_GEOMETRY_URL='./assets/geometry/db694e926309b798/support03.glb';
export function replaceSupportGeometry(root, geometry){
 const target=root.getObjectByName('Distant_Limestone_Support_03');
 if(!target?.isMesh||target.geometry.index?.count!==144150)throw Error('Expected unchanged support03 source geometry');
 if(geometry.index?.count!==44280||geometry.attributes.position.count!==7775)throw Error('Unexpected support03 replacement');
 for(const key of ['position','normal','uv','color'])if(!geometry.attributes[key])throw Error('Missing support attribute '+key);
 geometry.computeBoundingBox();geometry.computeBoundingSphere();target.geometry=geometry;return target;
}
export async function simplifySupport(root){
 const {scene}=await new GLTFLoader().loadAsync(SUPPORT_GEOMETRY_URL);let mesh;
 scene.traverse(o=>{if(o.isMesh){if(mesh)throw Error('Expected one replacement geometry');mesh=o;}});
 if(!mesh)throw Error('Missing replacement geometry');return replaceSupportGeometry(root,mesh.geometry);
}
