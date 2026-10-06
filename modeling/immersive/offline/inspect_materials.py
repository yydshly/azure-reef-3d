import bpy,json,sys,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('scene',type=Path);p.add_argument('output',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);bpy.ops.wm.open_mainfile(filepath=str(a.scene.resolve()))
used={slot.material for o in bpy.context.scene.objects if o.type=='MESH'for slot in o.material_slots if slot.material};result=[]
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 textures=[{'node':n.name,'image':n.image.name if n.image else None,'path':n.image.filepath if n.image else None}for n in mat.node_tree.nodes if n.type=='TEX_IMAGE']
 result.append({'material':mat.name,'assigned_to_mesh':mat in used,'texture_nodes':textures,'has_caustics_image':any('caustic'in (n['image']or'').lower()or'caustic'in(n['path']or'').lower()for n in textures),'node_types':[n.bl_idname for n in mat.node_tree.nodes]})
a.output.write_text(json.dumps(result,indent=2));print(json.dumps([{'name':r['material'],'used':r['assigned_to_mesh'],'caustics':r['has_caustics_image'],'images':[t['image']for t in r['texture_nodes']]}for r in result],indent=2))
