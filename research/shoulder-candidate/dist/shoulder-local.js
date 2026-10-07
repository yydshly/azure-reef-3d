import {GLTFLoader} from './vendor/GLTFLoader.js';
export async function addShoulder(root){
 const {scene}=await new GLTFLoader().loadAsync('assets/shoulder-v3/pilot.glb');
 scene.name='Interpreted_shoulder_local_v3';scene.position.set(-4.8,-.06576677229367059,-26);
 scene.rotation.y=-.2;root.add(scene);root.updateMatrixWorld(true);return scene;
}
