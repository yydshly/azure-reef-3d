"""Matched offline neutral geometry proofs. No browser or underwater appearance claim."""
import bpy,sys,json,math,hashlib,argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);P=a.out;SRC=a.source
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(SRC));target=bpy.data.objects['Corridor_Distant_Linked_03'];before=target.data
prior=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(P/'replacement.glb'));added=list(set(bpy.data.objects)-prior);repl=next(o for o in added if o.type=='MESH');after=repl.data
for o in added:bpy.data.objects.remove(o,do_unlink=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=1120;s.render.resolution_y=700;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
world=bpy.data.worlds.new('Matched neutral world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55;s.world=world
mat=bpy.data.materials.new('Matched neutral gray');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.34,.34,.34,1);bs.inputs['Roughness'].default_value=.72
for me in set([o.data for o in s.objects if o.type=='MESH']+[after]):me.materials.clear();me.materials.append(mat)
for name,pos,energy,size in [('Neutral key',(-2,23,9),1700,7),('Neutral fill',(7,29,6),950,6)]:
 ld=bpy.data.lights.new(name,'AREA');ld.energy=energy;ld.shape='DISK';ld.size=size;lo=bpy.data.objects.new(name,ld);s.collection.objects.link(lo);lo.location=pos;lo.rotation_euler=(Vector((1.8,26,.6))-lo.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Matched camera');co=bpy.data.objects.new('Matched camera',cam);s.collection.objects.link(co);s.camera=co;cam.sensor_fit='VERTICAL';cam.sensor_height=32;cam.lens=16/math.tan(math.radians(47/2));cam.clip_start=.05;cam.clip_end=250
views=[('normal-midpoint',(0,18,2.7),(-1.5,31,1)),('normal-reverse',(3.6,34,2.7),(5.1,21,1)),('front',(1.8,21.7,2.15),(1.8,26,.52)),('reverse',(1.8,30.3,2.15),(1.8,26,.52))]
manifest={'disclosure':'Offline Blender/Cycles geometry diagnostic. Both versions use exactly the same gray material, lights, world, camera, resolution, exposure and 24 samples. No runtime caustics, animation, browser appearance, or underwater realism claim. All source GLB geometry remains present in both normal-midpoint images. Runtime-generated new landmarks are absent, so these are not complete production A/B images.','source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'replacement_sha256':hashlib.sha256((P/'replacement.glb').read_bytes()).hexdigest(),'view_fov_vertical_degrees':47,'aspect':1.6,'views':views,'single_user_preview_target':'Corridor_Distant_Linked_03','output':[]}
# Render the normal comparison and thumbnails first, then the closer paired directions.
for name,pos,tar in views:
 co.location=pos;co.rotation_euler=(Vector(tar)-co.location).to_track_quat('-Z','Y').to_euler()
 for version,me in [('before',before),('candidate',after)]:
  target.data=me;out=P/version;out.mkdir(exist_ok=True);s.render.resolution_percentage=100;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);manifest['output'].append(str(out/(name+'.png')))
  if name in ('normal-midpoint','normal-reverse','reverse'):
   s.render.resolution_percentage=25;s.render.filepath=str(out/(name+'-thumbnail.png'));bpy.ops.render.render(write_still=True);manifest['output'].append(str(out/(name+'-thumbnail.png')))
  (P/'neutral-render-manifest.json').write_text(json.dumps(manifest,indent=2));print('PROOF_RENDER',version,name,flush=True)

# Target-only silhouettes retain each exact camera and target transform. No crop.
for o in s.objects:
 if o.type=='MESH' and o!=target:o.hide_render=True
world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1)
world.node_tree.nodes['Background'].inputs[1].default_value=1
sil=bpy.data.materials.new('Black target silhouette');sil.use_nodes=True
n=sil.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(0,0,0,1);sil.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
for me in (before,after):me.materials.clear();me.materials.append(sil)
for name,pos,tar in views:
 if name not in ('normal-midpoint','normal-reverse'):continue
 co.location=pos;co.rotation_euler=(Vector(tar)-co.location).to_track_quat('-Z','Y').to_euler()
 for version,me in [('before',before),('candidate',after)]:
  target.data=me;s.render.resolution_percentage=100;s.render.filepath=str(P/version/(name+'-silhouette.png'));bpy.ops.render.render(write_still=True);manifest['output'].append(s.render.filepath)
(P/'neutral-render-manifest.json').write_text(json.dumps(manifest,indent=2))
