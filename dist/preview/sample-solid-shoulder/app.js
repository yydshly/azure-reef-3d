import * as T from 'three';
import {OrbitControls} from '../../vendor/OrbitControls.js';
import {GLTFLoader} from '../../vendor/GLTFLoader.js';
const canvas=document.querySelector('#sample'),status=document.querySelector('#status');
try{
 const metadata=await fetch('./model.json').then(r=>{if(!r.ok)throw new Error('模型记录读取失败');return r.json();});
 document.querySelector('#title').textContent=metadata.title;document.title=metadata.title+' · 原样查看';document.querySelector('#limits').textContent=metadata.limitations;document.querySelector('#source').href=metadata.sourceURL;
 const renderer=new T.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setClearColor(0x111e27);renderer.outputColorSpace=T.SRGBColorSpace;
 const scene=new T.Scene(),camera=new T.PerspectiveCamera(45,1,.001,10000),controls=new OrbitControls(camera,canvas);controls.enableDamping=true;
 const hemisphere=new T.HemisphereLight(0xdde8ee,0x4c555b,1.4),key=new T.DirectionalLight(0xffffff,2.1);scene.add(hemisphere,key);
 const gltf=await new GLTFLoader().loadAsync('./model.glb');scene.add(gltf.scene);const originalMatrix=gltf.scene.matrixWorld.toArray();const focus=metadata.focusNode?gltf.scene.getObjectByName(metadata.focusNode):gltf.scene;if(!focus)throw new Error('Original inspection target is missing');const bounds=new T.Box3().setFromObject(focus),center=bounds.getCenter(new T.Vector3()),sphere=bounds.getBoundingSphere(new T.Sphere());if(!Number.isFinite(sphere.radius)||sphere.radius<=0)throw new Error('原模型范围无效');
 const distance=sphere.radius/Math.sin(T.MathUtils.degToRad(camera.fov/2))*1.3;controls.target.copy(center);controls.minDistance=sphere.radius*.15;controls.maxDistance=distance*10;camera.near=Math.max(sphere.radius/10000,.0001);camera.far=Math.max(distance*100,100);camera.updateProjectionMatrix();
 function view(name){const d={front:[0,.15,1],side:[1,.15,0],back:[0,.15,-1],overview:[1,.55,1]}[name]||[1,.55,1];camera.position.copy(center).add(new T.Vector3(...d).normalize().multiplyScalar(distance));camera.lookAt(center);controls.update();}
 function resize(){renderer.setSize(innerWidth,innerHeight,false);camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();}resize();addEventListener('resize',resize);view('overview');
 let frames=0,triangles=0,meshes=0;gltf.scene.traverse(o=>{if(o.isMesh){meshes++;triangles+=(o.geometry.index?.count||o.geometry.attributes.position.count)/3;}});
 document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>view(b.dataset.view)));
 status.textContent=`原文件已载入 · ${meshes}个网格 · ${Math.round(triangles).toLocaleString()}三角形`;
 renderer.setAnimationLoop(()=>{controls.update();key.position.copy(camera.position).add(new T.Vector3(sphere.radius,sphere.radius,0));renderer.render(scene,camera);frames++;});
 window.originalSample={scene,camera,renderer,controls,model:gltf.scene,metadata,view,getState:()=>({ready:true,frames,meshes,triangles,camera:camera.position.toArray(),bounds:{min:bounds.min.toArray(),max:bounds.max.toArray()},modelMatrix:gltf.scene.matrixWorld.toArray(),originalMatrix,renderer:{calls:renderer.info.render.calls,triangles:renderer.info.render.triangles}}),capture:()=>{renderer.render(scene,camera);return canvas.toDataURL('image/png');}};
 addEventListener('pagehide',()=>{renderer.setAnimationLoop(null);controls.dispose();gltf.scene.traverse(o=>{if(o.isMesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material]){for(const value of Object.values(m))if(value?.isTexture)value.dispose();m.dispose();}}});renderer.dispose();});
}catch(error){status.textContent='暂时无法显示原样本：'+String(error);window.originalSampleFailure=String(error);console.error(error);}
