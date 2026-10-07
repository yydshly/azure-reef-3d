import {GLTFLoader} from './vendor/GLTFLoader.js';
export async function addShoulder(root){
 const {scene}=await new GLTFLoader().loadAsync('assets/shoulder-v3/pilot.glb');
 scene.name='Interpreted_shoulder_local_v3';scene.position.set(-6.4,.20,-26);
 root.add(scene);root.updateMatrixWorld(true);return scene;
}
