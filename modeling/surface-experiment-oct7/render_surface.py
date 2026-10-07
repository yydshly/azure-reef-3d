"""Blender 4.3.2 offline CPU control, frozen fixture/cameras; no browser proof.
Target clone keeps all fixture inputs except map images and the explicit fixed
0.75 runtime normal-strength multiplier (applied to target in every comparison).
"""
import argparse,bpy,hashlib,json,re,sys
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('fixture',type=Path);p.add_argument('asset',type=Path);p.add_argument('out',type=Path);p.add_argument('--mode',choices=['baseline','fine','soft','normal-disabled'],required=True);p.add_argument('--views',default='close,close-reverse,opening');p.add_argument('--save-blend',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.out.mkdir(parents=True,exist_ok=True)
TARGET='Coral_Staghorn_Thicket_01';base='Coral | reference-led porous PBR'
bpy.ops.wm.open_mainfile(filepath=str(a.fixture.resolve()));s=bpy.context.scene
assert not any(o.type in {'MESH','EMPTY'}for o in s.objects)
fixture_materials={re.sub(r'\.\d{3}$','',m.name):m for m in bpy.data.materials}
def simple(v):
 if isinstance(v,(bool,int,float,str)):return v
 try:return list(v)
 except:return str(v)
def nodesig(tree):
 return {'nodes':[{'name':n.name,'type':n.bl_idname,'inputs':[(i.identifier,simple(i.default_value))for i in n.inputs if hasattr(i,'default_value')],'image':n.image.name if n.type=='TEX_IMAGE'and n.image else None}for n in tree.nodes],'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier)for l in tree.links]}
def settings():
 return {'engine':s.render.engine,'samples':s.cycles.samples,'seed':s.cycles.seed,'denoising':s.cycles.use_denoising,'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],'world':nodesig(s.world.node_tree),'compositor':nodesig(s.node_tree),'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'camera_lens':s.camera.data.lens,'lights':[{'name':o.name,'matrix':[list(r)for r in o.matrix_world],'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),'nodes':nodesig(o.data.node_tree)if o.data.node_tree else None}for o in s.objects if o.type=='LIGHT']}
fixture_settings=settings();original_signatures={m.name:nodesig(m.node_tree)for m in fixture_materials.values()}
bpy.ops.import_scene.gltf(filepath=str(a.asset.resolve()))
target=bpy.data.objects[TARGET];imported_target=target.material_slots[0].material
im_normal=next(n.image for n in imported_target.node_tree.nodes if n.type=='TEX_IMAGE'and any(l.to_node.type=='NORMAL_MAP'for l in n.outputs['Color'].links))
im_rough=next(n.image for n in imported_target.node_tree.nodes if n.type=='TEX_IMAGE'and n.image!=im_normal)
for o in s.objects:
 if o.type!='MESH':continue
 for slot in o.material_slots:
  if o.name==TARGET:slot.material=fixture_materials[base]
  else:slot.material=fixture_materials[re.sub(r'\.\d{3}$','',slot.material.name)]
clone=fixture_materials[base].copy();clone.name='TEST target only | '+a.mode;target.material_slots[0].material=clone
nt=clone.node_tree;normal_node=next(n for n in nt.nodes if n.type=='NORMAL_MAP');source_scale=float(normal_node.inputs['Strength'].default_value);normal_node.inputs['Strength'].default_value=source_scale*.75
if a.mode in {'fine','soft'}:
 next(n for n in nt.nodes if n.type=='TEX_IMAGE'and any(l.to_node.type=='NORMAL_MAP'for l in n.outputs['Color'].links)).image=im_normal
 next(n for n in nt.nodes if n.type=='TEX_IMAGE'and any(l.to_node.type=='SEPARATE_COLOR'for l in n.outputs['Color'].links)).image=im_rough
elif a.mode=='normal-disabled':normal_node.inputs['Strength'].default_value=0
for n in nt.nodes:
 if n.type=='TEX_IMAGE':assert n.image.colorspace_settings.name=='Non-Color'
assert settings()==fixture_settings
assert all(nodesig(m.node_tree)==original_signatures[m.name]for m in fixture_materials.values())
assert [o.name for o in s.objects if o.type=='MESH'and any(slot.material==clone for slot in o.material_slots)]==[TARGET]
assert next(l.from_node.type for l in nt.links if l.to_node.type=='BSDF_PRINCIPLED'and l.to_socket.name=='Base Color')=='VERTEX_COLOR'
views={'close':((-.42,-4.90,1.87),(-3.018,-1.569,.57)),'close-reverse':((-5.58,1.79,1.87),(-3.018,-1.569,.57)),'opening':((1.5,-4.8,1.6),(-.5,6,.8))}
report={'mode':a.mode,'asset':a.asset.name,'asset_sha256':hashlib.sha256(a.asset.read_bytes()).hexdigest(),'fixture_sha256':hashlib.sha256(a.fixture.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'settings_unchanged':True,'original_material_graphs_unchanged':True,'settings':fixture_settings,'target':TARGET,'actual_assigned_material':target.material_slots[0].material.name,'assigned_only_to':[TARGET],'actual_assigned_graph':nodesig(clone.node_tree),'source_normal_scale':source_scale,'runtime_multiplier':.75,'fixed_effective_scale':source_scale*.75,'control_effective_scale':float(normal_node.inputs['Strength'].default_value),'views':{},'disclosure':'OFFLINE Cycles CPU renders. Not browser/WebGL proof. No caustics. Frozen fixture, cameras, colors and geometry. Target alone uses fixed runtime-equivalent normal multiplier; other materials retain frozen fixture values. Still frames cannot test moving shimmer.'}
for name in a.views.split(','):
 pos,point=views[name];s.camera.location=pos;s.camera.rotation_euler=(Vector(point)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str((a.out/(name+'.png')).resolve());bpy.ops.render.render(write_still=True);report['views'][name]={'position':pos,'target':point,'matrix':[list(r)for r in s.camera.matrix_world],'lens':s.camera.data.lens,'sha256':hashlib.sha256((a.out/(name+'.png')).read_bytes()).hexdigest()};(a.out/'render-manifest.json').write_text(json.dumps(report,indent=2));print('FRAME_READY',a.mode,name,flush=True)
if a.save_blend:bpy.ops.wm.save_as_mainfile(filepath=str((a.out/(a.mode+'-offline.blend')).resolve()))
print('COMPLETE',a.mode,flush=True)
