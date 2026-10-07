"""Fixed offline GLB material evidence; no production water shader or FPS claim."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
model=P.parents[1]/'source-model.glb'
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=False;s.cycles.max_bounces=3;s.cycles.seed=178
s.render.resolution_x=1120;s.render.resolution_y=700;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('Fixed offline world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.22,.25,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
s.view_settings.view_transform='AgX'
bpy.ops.import_scene.gltf(filepath=str(model));target=bpy.data.objects['Distant_Limestone_Support_03'];target.pass_index=1
# Match the app's retained base branches. Supplemental colony placements are exact rigid transforms.
for o in list(s.objects):
 if o.name.startswith('Coral_Staghorn_Thicket_') and int(o.name.split('_')[-1]) not in [0,1,3,12,16]:bpy.data.objects.remove(o,do_unlink=True)
asset=str(P.parents[1]/'dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb')
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

import hashlib,numpy as np
assert hashlib.sha256(model.read_bytes()).hexdigest()=='c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd'
# Both arms retain the already-published node78 pose. Only node66 differs.
accepted=bpy.data.objects['Corridor_Distant_Linked_03'];bpy.context.view_layer.update();mat=accepted.matrix_world.copy();mat.translation.z-=.12711730762552115;accepted.matrix_world=mat
sibling=bpy.data.objects['Depth_Staghorn_Linked_01_1'];sibling.pass_index=2;bpy.context.view_layer.update();base_matrix=sibling.matrix_world.copy();shift=.10224513179842109
s.cycles.samples=20;s.cycles.seed=178
views=[('passage20',[.29437670936632904,2.364790323719224,-6.645862253821183],[.13504281746656863,.7,-21.069232030809317]),('diagnostic',[4.7,1.65,-8],[2.2,.9,-12.3])]
gray=bpy.data.materials.new('Explicit gray shape diagnostic');gray.use_nodes=True;gray.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.42,.42,.42,1);gray.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
s.view_layers[0].use_pass_object_index=True;s.use_nodes=True;nt=s.node_tree;nt.nodes.clear();rl=nt.nodes.new('CompositorNodeRLayers');comp=nt.nodes.new('CompositorNodeComposite');nt.links.new(rl.outputs['Image'],comp.inputs[0]);out=nt.nodes.new('CompositorNodeOutputFile');out.base_path=str(P);out.format.file_format='OPEN_EXR';out.format.color_depth='32';nt.links.new(rl.outputs['IndexOB'],out.inputs[0])
before={o.name:tuple(tuple(row)for row in o.matrix_world)for o in s.objects if o.type=='MESH'};frames=[]
# The first actual images are the unshifted source at both requested cameras.
jobs=[('before','passage20','textured'),('before','diagnostic','textured'),('candidate','passage20','textured'),('candidate','diagnostic','textured'),('before','passage20','gray'),('before','diagnostic','gray'),('candidate','passage20','gray'),('candidate','diagnostic','gray')]
for pose,view,style in jobs:
 sibling.matrix_world=base_matrix.copy()
 if pose=='candidate':
  mat=sibling.matrix_world.copy();mat.translation.z-=shift;sibling.matrix_world=mat
 label,position,target=next(v for v in views if v[0]==view);cam.location=(position[0],-position[2],position[1]);tar=Vector((target[0],-target[2],target[1]));cam.rotation_euler=(tar-cam.location).to_track_quat('-Z','Y').to_euler();s.view_layers[0].material_override=gray if style=='gray' else None
 name=f'offline-{pose}-{view}-{style}';s.render.filepath=str(P/(name+'.png'));out.file_slots[0].path=name+'-index-';bpy.ops.render.render(write_still=True)
 maskimg=bpy.data.images.load(str(P/(name+'-index-0001.exr')));pixels=np.array(maskimg.pixels[:]).reshape(700,1120,4);mask=np.flipud(pixels[:,:,0]>1.5);ids=np.argwhere(mask);box=[int(ids[:,1].min()),int(ids[:,0].min()),int(ids[:,1].max()),int(ids[:,0].max())]if len(ids)else None;frames.append({'pose':pose,'view':view,'style':style,'file':name+'.png','node66_visible_pixels':int(mask.sum()),'node66_fraction_of_frame':float(mask.mean()),'node66_visible_bbox_xyxy':box});print('FRAME_READY',json.dumps(frames[-1]),flush=True)
 (P/'offline-frame-progress.json').write_text(json.dumps(frames,indent=2)+'\n')
for ob in s.objects:
 if ob.type=='MESH' and ob!=sibling:assert before[ob.name]==tuple(tuple(row)for row in ob.matrix_world),ob.name
(P/'offline-sibling-pose-manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'both_arms_published_node78_downshift_scene_units':.12711730762552115,'only_candidate_change':{'object':'Depth_Staghorn_Linked_01_1','source_node':66,'world_y_downshift_scene_units':shift,'nonuniform_scale_blender_preserved':list(sibling.scale),'source_nonuniform_scale_gltf':[.722000002861023,.722000002861023,.6822900176048279]},'all_other_mesh_world_matrices_unchanged':True,'geometry_materials_textures':'Original source shared data untouched; pose-only change to node66 in this offline scene','views':[{'name':n,'position':p,'target':t}for n,p,t in views],'vertical_fov_degrees':47,'resolution':[1120,700],'samples':20,'seed':178,'renderer':'Blender '+bpy.app.version_string+' Cycles CPU','frames':frames,'disclosure':'Offline fixed-light original-GLB-material pose comparison. Both arms preserve published node78 grounding. Production world-space linked substrate shader, water/fog/caustics, browser output, dynamic fish and performance are not reproduced. No source GLB, runtime module, ground geometry or pose file was edited.','distance_units':'Uncalibrated scene units; no surveyed physical scale.'},indent=2)+'\n')
