"""Optional same-camera geometry illustration. Does NOT execute runtime GLSL."""
import bpy, math, json, os
from mathutils import Vector
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(BASE/'dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb'))
# glTF import maps Three Y-up to Blender Z-up. This is the unchanged pilot
# component used by Middle, shown in local coordinates for a geometry check.
fan=bpy.data.objects.get('Attached_reticulate_fan_form')
assert fan and fan.type=='MESH'
original=[v.co.copy() for v in fan.data.vertices]
# The fixed source asset's local Y becomes Blender Z.
assert abs(max(v.z for v in original)-2.6220932006835938)<1e-6
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=20;s.cycles.use_denoising=False
s.render.resolution_x=1000;s.render.resolution_y=760;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Neutral diagnostic world');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.08,.1,.12,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
# One fixed three-quarter view of the source support and whole fan.
# Three local coordinates: camera(-2.7,2.6,2.65), target(-.76,1.95,.14).
def to_blender(p):return Vector((p[0],-p[2],p[1]))
cam_data=bpy.data.cameras.new('Same_camera_all_phases');cam=bpy.data.objects.new('Same_camera_all_phases',cam_data);s.collection.objects.link(cam);s.camera=cam
camera=(-2.7,2.6,2.65);target=(-.76,1.95,.14);cam.location=to_blender(camera);cam.rotation_euler=(to_blender(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam_data.lens=58
for name,pos,energy,size in [('Key',(-2,5,3),500,4),('Fill',(2,3,-2),220,3)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.location=to_blender(pos);o.rotation_euler=(to_blender(target)-o.location).to_track_quat('-Z','Y').to_euler()
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
phases=[('rest',0),('positive',2),('negative',6)]
for name,t in phases:
 a=.04*math.sin(t*2*math.pi/8)
 for vertex,p in zip(fan.data.vertices,original):
  h=max(0,min(1,(p.z-1.84)/(2.6220932006835938-1.84)))
  vertex.co=p.copy();vertex.co.y-=a*h*h*(3-2*h)
 fan.data.update()
 s.render.filepath=str(OUT/('offline-'+name+'.png'));bpy.ops.render.render(write_still=True)
json.dump({'scope':'Isolated original pilot component, same camera and neutral offline lighting; CPU-deformed geometry illustration, NOT runtime GLSL, app pixels, biological validation, or full-scene composition evidence.','phases':[{'name':n,'seconds':t,'amplitude':.04*math.sin(t*2*math.pi/8)}for n,t in phases],'cameraThreeLocal':camera,'targetThreeLocal':target,'size':[1000,760],'lensMM':58,'cyclesSamples':20,'onlyMeshChanged':fan.name,'originalVertices':len(original),'maxDisplacement':.04,'fixedThroughY':1.84},open(OUT/'offline-render.json','w'),indent=2)
