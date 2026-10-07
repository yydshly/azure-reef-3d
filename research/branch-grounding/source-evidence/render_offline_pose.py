"""Fixed offline GLB material evidence; no production water shader or FPS claim."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
model=Path('/workspace/scratch/56bf13a306b9/coral-3d/source-model.glb')
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=False;s.cycles.max_bounces=3;s.cycles.seed=178
s.render.resolution_x=1120;s.render.resolution_y=700;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('Fixed offline world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.22,.25,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
s.view_settings.view_transform='AgX'
bpy.ops.import_scene.gltf(filepath=str(model));target=bpy.data.objects['Distant_Limestone_Support_03'];target.pass_index=1
# Match the app's retained base branches. Supplemental colony placements are exact rigid transforms.
for o in list(s.objects):
 if o.name.startswith('Coral_Staghorn_Thicket_') and int(o.name.split('_')[-1]) not in [0,1,3,12,16]:bpy.data.objects.remove(o,do_unlink=True)
asset='/workspace/scratch/56bf13a306b9/coral-3d/dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb'
for name,pos,yaw,omit in [('NearLeft',[-4.8,.09174240518222349,-10],1.3,'Attached_small_fan_form'),('FarRight',[3.5,-.015196346640586854,-44],1.3,'Attached_reticulate_fan_form'),('Middle',[-4.8,-.06576677229367059,-26],-.2,None)]:
 old=set(s.objects);bpy.ops.import_scene.gltf(filepath=asset);new=set(s.objects)-old
 root=bpy.data.objects.new('Inhabited_'+name,None);s.collection.objects.link(root);root.location=(pos[0],-pos[2],pos[1]);root.rotation_euler[2]=yaw
 for o in new:
  if omit and o.name.split('.')[0]==omit:bpy.data.objects.remove(o,do_unlink=True);continue
  if o.parent not in new:o.parent=root
# Original imported maps and vertex pigment retained. Runtime world-space linked albedo/fog/caustics omitted.
d=bpy.data.lights.new('Fixed large key','AREA');d.energy=2500;d.shape='DISK';d.size=15;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=(-8,19,15);o.rotation_euler=(Vector((0,25,0))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.lights.new('Fixed sun','SUN');d.energy=2.0;d.angle=.18;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.rotation_euler=(.3,-.5,-.3)
d=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',d);s.collection.objects.link(cam);s.camera=cam;d.type='PERSP';d.sensor_fit='VERTICAL';d.sensor_height=24;d.lens=24/(2*math.tan(math.radians(47)/2));d.clip_end=1500

# One rigid pose preview only; imported shared mesh/material data are untouched.
import hashlib
assert hashlib.sha256(model.read_bytes()).hexdigest()=='c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd'
root=bpy.data.objects['Corridor_Distant_Linked_03'];original_matrix=root.matrix_world.copy();shift=.12711730762552115
cam.location=(4.7,21.7,1.25);target_point=Vector((1.8,25.45,0));cam.rotation_euler=(target_point-cam.location).to_track_quat('-Z','Y').to_euler()
s.cycles.samples=20;s.cycles.seed=178
s.use_nodes=False
gray=bpy.data.materials.new('Explicit gray shape diagnostic');gray.use_nodes=True;gray.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.42,.42,.42,1);gray.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
bpy.context.view_layer.update()
before={o.name:tuple(tuple(row)for row in o.matrix_world)for o in s.objects if o.type=='MESH'}
for pose in ['before','pose-preview']:
 root.matrix_world=original_matrix.copy()
 if pose=='pose-preview':
  matrix=root.matrix_world.copy();matrix.translation.z-=shift;root.matrix_world=matrix
 for style in ['textured','gray']:
  s.view_layers[0].material_override=gray if style=='gray' else None
  s.render.filepath=str(P/f'offline-{pose}-close-{style}.png');bpy.ops.render.render(write_still=True);print('FRAME_READY',s.render.filepath,flush=True)
for o in s.objects:
 if o.type=='MESH' and o!=root:assert before[o.name]==tuple(tuple(row)for row in o.matrix_world)
(P/'offline-pose-manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'changed_object':'Corridor_Distant_Linked_03','world_y_downshift_scene_units':shift,'coordinate_note':'glTF world Y is Blender world Z','geometry_materials_textures':'Original source and shared data untouched; pose-only change to the one object in this offline scene','camera':{'position':[4.7,1.25,-21.7],'target':[1.8,0,-25.45],'vertical_fov_degrees':47},'resolution':[1120,700],'samples':20,'seed':178,'renderer':'Blender '+bpy.app.version_string+' Cycles CPU','disclosure':'Offline pose preview only. Original high-detail limestone and source GLB maps, pigment, fixed lighting, current supplemental rigid colonies. Production world-space substrate shader, water/fog/caustics, browser output, dynamic fish and performance are not reproduced. No source GLB, production module or transform file was edited.','distance_units':'Uncalibrated scene units; no surveyed physical scale.'},indent=2)+'\n')
