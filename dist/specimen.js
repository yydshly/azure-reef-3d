import * as THREE from 'three';
import {GLTFLoader} from './vendor/GLTFLoader.js';
export const SPECIMEN={
  "url": "./assets/specimens/fe5fc88fe1bb4ae6/skeleton.glb",
  "position": [
    -0.4,
    -0.03827932751178741,
    -6.5
  ],
  "quaternion": [
    0,
    0.21643961393810288,
    0,
    0.9762960071199334
  ],
  "scale": [
    1,
    1,
    1
  ],
  "focus": {
    "position": [
      -0.08890157184493325,
      0.425,
      -5.832847267861814
    ],
    "target": [
      -0.4,
      0,
      -6.5
    ],
    "limits": {
      "minDistance": 0.85,
      "maxDistance": 1.6,
      "minPolarAngle": 0.2,
      "maxPolarAngle": 1.0471975511965976
    }
  },
  "marker": [
    -0.4,
    0.035,
    -6.5
  ],
  "catalog": "USNM 74016",
  "source": "https://3d.si.edu/object/3d/acropora-cervicornis:dd875177-c986-48e2-9468-8e58f01099d3"
};
export const SPECIMEN_LESSON={title:'近看一块真实珊瑚骨架',look:'拖动绕到侧面和背面，观察分枝与杯状小结构；滚轮缩放，不能平移。',text:'眼前是鹿角珊瑚的干制馆藏骨架扫描，宽约28厘米。珊瑚的活组织与骨架不同；这里保留骨架形态和干制外观，没有把它当作活体扫描。',note:'Smithsonian NMNH，USNM 74016，CC0。原标本1984年采自墨西哥加勒比地区。模型按1米对应1场景单位放置；其余世界不是实测地形。此处为教学摆放，不能说明该群落的真实共存或死亡原因。',source:'Smithsonian · 原始馆藏与扫描',url:SPECIMEN.source,marker:SPECIMEN.marker,label:'干制珊瑚骨架 · 教学摆放'};
export function placeSpecimen(root,scene){const g=new THREE.Group();g.name='Teaching_CoralSkeleton_USNM74016';g.position.fromArray(SPECIMEN.position);g.quaternion.fromArray(SPECIMEN.quaternion);g.scale.fromArray(SPECIMEN.scale);g.userData.specimen=true;g.add(scene);root.add(g);return g;}
export async function addSpecimen(root){const {scene}=await new GLTFLoader().loadAsync(SPECIMEN.url);return placeSpecimen(root,scene);}

