import bpy,json,sys,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;f=P/'full-scene-editable.blend';bpy.ops.wm.open_mainfile(filepath=str(f));s=bpy.context.scene
assert s.world is None and not s.use_nodes and not any(o.type in {'CAMERA','LIGHT'}for o in s.objects)
assert all(im.packed_file for im in bpy.data.images if im.users and im.source=='FILE' and im.type!='RENDER_RESULT')
meshes=[o for o in s.objects if o.type=='MESH'];names={o.name for o in s.objects};assert all(f'Coral_Staghorn_Thicket_{i:02d}'in names for i in range(22));assert any(o.name.startswith('fish_')for o in s.objects);assert any(o.name.startswith('Sand_')for o in meshes)
report={'blend_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'reopen_pass':True,'objects':len(s.objects),'mesh_objects':len(meshes),'all22_original_thickets':True,'fish_present':True,'sand_present':True,'camera_and_light_count':0,'world':None,'compositor_enabled':False,'all_used_file_images_packed':True,'geometry_triangles_unique':sum(sum(len(p.vertices)-2 for p in m.polygons)for m in bpy.data.meshes)};(P/'editable-reopen-proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
