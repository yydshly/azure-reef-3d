import bpy
from pathlib import Path
p=str(Path(__file__).resolve().parent/'artifacts'/'legacy-base')+'/'
bpy.ops.wm.open_mainfile(filepath=p+'reef-garden.blend')
me=bpy.data.meshes.new('Sand_Horizon_80m');me.from_pydata([(-40,-40,-.22),(40,-40,-.22),(40,40,-.22),(-40,40,-.22)],[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new('Sand_Horizon_80m',me);bpy.context.collection.objects.link(o);me.materials.append(bpy.data.materials['Rippling sand']);ca=me.color_attributes.new(name='ReefColor',type='FLOAT_COLOR',domain='POINT')
for c in ca.data:c.color=(.67,.63,.45,1)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:o.select_set(o.type in {'MESH','EMPTY'})
bpy.ops.export_scene.gltf(filepath=p+'reef-garden.glb',export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=p+'reef-garden.blend')
print('EXTENDED_EXPORT_COMPLETE',flush=True)
