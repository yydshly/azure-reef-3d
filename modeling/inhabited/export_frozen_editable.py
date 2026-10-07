import bpy,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];source=Path(args[0]).resolve();target=Path(args[1]).resolve();target.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
for image in bpy.data.images:
 if image.packed_file:
  image.filepath=''
  image.name=image.name.replace('_albedo','-albedo').replace('_roughness','-roughness')
for obj in bpy.context.scene.objects:obj.select_set(obj.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False,export_extras=True)
