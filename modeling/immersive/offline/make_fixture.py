import bpy,sys,argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
bpy.ops.wm.open_mainfile(filepath=str(a.source.resolve()))
# Retain only materials actually assigned to the accepted reimport geometry.
used={slot.material for o in bpy.context.scene.objects if o.type=='MESH' for slot in o.material_slots if slot.material}
for mat in used:mat.use_fake_user=True
for o in list(bpy.data.objects):
 if o.type in {'MESH','EMPTY'}:bpy.data.objects.remove(o,do_unlink=True)
for mesh in list(bpy.data.meshes):
 if mesh.users==0:bpy.data.meshes.remove(mesh)
for mat in list(bpy.data.materials):
 if mat not in used:bpy.data.materials.remove(mat)
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(a.output.resolve()),compress=True)
report={'bytes':a.output.stat().st_size,'objects':[{'name':o.name,'type':o.type}for o in bpy.data.objects],'meshes':len(bpy.data.meshes),'materials':[m.name for m in bpy.data.materials],'images':[{'name':im.name,'packed':bool(im.packed_file)}for im in bpy.data.images]}
a.output.with_suffix('.json').write_text(json.dumps(report,indent=2));print(report)
