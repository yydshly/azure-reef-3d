"""Clean packed full-scene Blender artifact: exact GLB import only, no presentation state."""
import bpy,sys,argparse,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('model',type=Path);p.add_argument('output',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;bpy.ops.import_scene.gltf(filepath=str(a.model.resolve()));scene.use_nodes=False;scene.world=None
bpy.ops.file.pack_all();bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
for ob in scene.objects:ob.select_set(False)
hero=bpy.data.objects.get('Coral_Staghorn_Thicket_01');hero.select_set(True);bpy.context.view_layer.objects.active=hero
assert not any(o.type in {'CAMERA','LIGHT'}for o in scene.objects)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(a.output.resolve()),compress=True)
images=[{'name':im.name,'packed':bool(im.packed_file),'users':im.users,'source':im.source}for im in bpy.data.images if im.type!='RENDER_RESULT'];assert all(i['packed']for i in images if i['users']>0 and i['source']=='FILE')
report={'input_glb_sha256':hashlib.sha256(a.model.read_bytes()).hexdigest(),'blend_sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'blend_bytes':a.output.stat().st_size,'scene_objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH'for o in scene.objects),'unique_meshes':len(bpy.data.meshes),'camera_count':sum(o.type=='CAMERA'for o in scene.objects),'light_count':sum(o.type=='LIGHT'for o in scene.objects),'compositor_enabled':scene.use_nodes,'world':scene.world.name if scene.world else None,'materials':[m.name for m in bpy.data.materials],'images':images,'scope':'Clean full exact-candidate GLB import only, all fish and substrate included. Original imported material graphs unchanged, no camera/lights/world/compositor or presentation substitutions. Packed textures and unused datablocks purged; no geometry edits.'};a.output.with_suffix('.proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
