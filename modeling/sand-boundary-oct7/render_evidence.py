"""Reproduce the matched-static-pose offline evidence; Blender 4.3.2 / Cycles CPU."""
import bpy,sys,argparse,json,hashlib,re
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('lighting_fixture',type=Path);p.add_argument('input_glb',type=Path);p.add_argument('output_folder',type=Path);p.add_argument('--view',choices=['wide','edge','all'],default='wide');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.output_folder.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(a.lighting_fixture.resolve()));s=bpy.context.scene
assert not any(o.type in {'MESH','EMPTY'}for o in s.objects),'Lighting fixture must contain no asset geometry'
materials={re.sub(r'\.\d{3}$','',m.name):m for m in bpy.data.materials}
bpy.ops.import_scene.gltf(filepath=str(a.input_glb.resolve()))
assignments={}
for obj in s.objects:
 if obj.type!='MESH':continue
 for slot in obj.material_slots:
  imported=slot.material
  if imported is None:continue
  name=re.sub(r'\.\d{3}$','',imported.name)
  if name not in materials:raise RuntimeError('Missing presentation material: '+name)
  slot.material=materials[name];assignments[name]=materials[name].name
# All rendering/light/world/compositor settings are preserved from the fixture.
# Cameras match the accepted frozen evidence; the GLB fish remain in static poses.
views=[('opening',(1.5,-4.8,1.6),(-.5,6,.8)),('reverse',(-.1,7.8,1.6),(1.1,-3.8,.65))]
# Runtime-reachable left edge: Three camera [-20.5,1.6,0], target [-6.9,.3,0].
# Blender import maps Three [x,y,z] to [x,-z,y].
edge_view=[('edge',(-20.5,0,1.6),(-6.9,0,.3))]
if a.view=='edge':views=edge_view
elif a.view=='all':views+=edge_view
for name,position,target in views:
 s.camera.location=position;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str((a.output_folder/(name+'.png')).resolve());bpy.ops.render.render(write_still=True)
report={'blender_version':bpy.app.version_string,'input_glb_sha256':hashlib.sha256(a.input_glb.read_bytes()).hexdigest(),'lighting_fixture_sha256':hashlib.sha256(a.lighting_fixture.read_bytes()).hexdigest(),'render_engine':s.render.engine,'samples':s.cycles.samples,'denoising':s.cycles.use_denoising,'resolution':[s.render.resolution_x,s.render.resolution_y],'materials':assignments,'views':views,'disclosure':'Offline Cycles reimport renders, not browser captures. Fish use matched static GLB poses; runtime movement/caustics are not measured here.'}
(a.output_folder/('render-manifest-'+a.view+'.json')).write_text(json.dumps(report,indent=2))
