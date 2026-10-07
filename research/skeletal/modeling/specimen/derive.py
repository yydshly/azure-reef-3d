"""Blender4.3.2: blender -b --python modeling/specimen/derive.py"""
import bpy
from pathlib import Path
p=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(p/'usnm_74016-100k-2048_std.glb'))
m=next(o for o in bpy.context.scene.objects if o.type=='MESH');m.name='USNM_74016_Dry_Skeleton_25k'
bpy.context.view_layer.objects.active=m
d=m.modifiers.new('Single bounded 25 percent simplification','DECIMATE');d.ratio=.25;d.use_collapse_triangulate=True
bpy.ops.object.modifier_apply(modifier=d.name)
bpy.ops.export_scene.gltf(filepath=str(p/'regenerated.glb'),export_format='GLB',export_yup=True,export_animations=False)
