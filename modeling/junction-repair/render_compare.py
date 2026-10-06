"""Render geometry-only comparisons using the unmodified published lighting fixture."""
import bpy,sys,argparse,json,hashlib,re
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('fixture',type=Path);p.add_argument('input_glb',type=Path);p.add_argument('out',type=Path);p.add_argument('--neutral-lens',type=float,default=27.59811019897461);p.add_argument('--views',default='opening,reverse,close,close-reverse,neutral,neutral-reverse');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(a.fixture.resolve()));s=bpy.context.scene
mats={re.sub(r'\.\d{3}$','',m.name):m for m in bpy.data.materials}
bpy.ops.import_scene.gltf(filepath=str(a.input_glb.resolve()))
for o in s.objects:
 if o.type=='MESH':
  for slot in o.material_slots:
   slot.material=mats[re.sub(r'\.\d{3}$','',slot.material.name)]
views=[('opening',(1.5,-4.8,1.6),(-.5,6,.8)),('reverse',(-.1,7.8,1.6),(1.1,-3.8,.65)),('close',(-.42,-4.90,1.87),(-3.018,-1.569,.57)),('close-reverse',(-5.58,1.79,1.87),(-3.018,-1.569,.57))]
manifest={'source':str(a.input_glb),'source_sha256':hashlib.sha256(a.input_glb.read_bytes()).hexdigest(),'fixture_sha256':hashlib.sha256(a.fixture.read_bytes()).hexdigest(),'resolution':[s.render.resolution_x,s.render.resolution_y],'samples':s.cycles.samples,'denoising':s.cycles.use_denoising,'views':{},'disclosure':'Matched offline Cycles renders. Not browser captures. No caustics; fish remain in matched static poses. Fixture world, compositor, lights and materials unchanged for opening/reverse/close views.'}
for name,pos,target in views:
 if name not in a.views.split(','):continue
 s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(a.out/(name+'.png'));bpy.ops.render.render(write_still=True);manifest['views'][name]={'position':pos,'target':target,'lens':s.camera.data.lens}
# Separate neutral diagnostic isolates geometry. It is not presented as in-scene lighting.
if any(x.startswith('neutral') for x in a.views.split(',')):
 s.camera.data.lens=a.neutral_lens;s.use_nodes=False;s.world=bpy.data.worlds.new('Neutral diagnostic world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.10,.10,.10,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 for o in s.objects:
  if o.type=='MESH':o.hide_render=o.name!='Coral_Staghorn_Thicket_01'
  elif o.type=='LIGHT':o.hide_render=True
 mat=bpy.data.materials.new('Diagnostic gray only');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.68
 ob=bpy.data.objects['Coral_Staghorn_Thicket_01'];ob.data.materials.clear();ob.data.materials.append(mat)
 for name,pos,energy,size in [('Diagnostic large key',(-2,-4,5),500,4),('Diagnostic rim',(-5,1,3),300,3)]:
  d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;obj=bpy.data.objects.new(name,d);s.collection.objects.link(obj);obj.location=pos;obj.rotation_euler=(Vector((-3,-1.5,.55))-obj.location).to_track_quat('-Z','Y').to_euler()
 for name,pos,target in [('neutral',views[2][1],views[2][2]),('neutral-reverse',views[3][1],views[3][2])]:
  if name not in a.views.split(','):continue
  s.camera.location=pos;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(a.out/(name+'.png'));bpy.ops.render.render(write_still=True);manifest['views'][name]={'position':pos,'target':target,'lens':s.camera.data.lens,'diagnostic':'Isolated target; gray material, neutral world, two area lights, compositor off. Identical before/after.'}
(a.out/'render-manifest.json').write_text(json.dumps(manifest,indent=2))
