"""Neutral local shape diagnostic only; neither runtime light nor caustics."""
import bpy,numpy as np,sys,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).parent;d=np.load(root/'shoulder-geometry.npz')
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=960;s.render.resolution_y=600;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('Neutral world');s.world.color=(.3,.3,.3);s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast' if 'Medium High Contrast' in s.view_settings.bl_rna.properties['look'].enum_items.keys() else 'None'
m=bpy.data.materials.new('Neutral limestone');m.diffuse_color=(.42,.43,.44,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.42,.43,.44,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=1
sand=bpy.data.materials.new('Neutral sand');sand.diffuse_color=(.65,.65,.65,1)
bpy.ops.mesh.primitive_plane_add(size=100,location=(0,25,-.22));bpy.context.object.data.materials.append(sand)
ld=bpy.data.lights.new('Neutral broad light','AREA');lo=bpy.data.objects.new('Neutral broad light',ld);s.collection.objects.link(lo);lo.location=(0,16,12);lo.rotation_euler=(Vector((-8,25,0))-lo.location).to_track_quat('-Z','Y').to_euler();ld.energy=1500;ld.size=8
cam=bpy.data.cameras.new('Diagnostic');co=bpy.data.objects.new('Diagnostic',cam);s.collection.objects.link(co);s.camera=co;cam.type='ORTHO';cam.ortho_scale=11.5;co.location=(-.6,19.5,4.4);co.rotation_euler=(Vector((-8.0,24.8,.30))-co.location).to_track_quat('-Z','Y').to_euler()
for mode in ['before','after']:
 v=d['original_vertices']if mode=='before'else d['vertices'];f=d['original_faces']if mode=='before'else d['faces'];v=v[:,[0,2,1]].copy();v[:,1]*=-1
 mesh=bpy.data.meshes.new(mode);mesh.from_pydata(v.tolist(),[],f.tolist());mesh.update();o=bpy.data.objects.new(mode,mesh);s.collection.objects.link(o);o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 s.render.filepath=str(root/('neutral-'+mode+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(o,do_unlink=True)
print('NEUTRAL_READY',flush=True)
