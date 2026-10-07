"""Append original textures + cloned target material without re-exporting geometry."""
import argparse,copy,hashlib,json,struct
from pathlib import Path
TARGET='Coral_Staghorn_Thicket_01';EXPECTED='ce6a7bc4d005ecd794d378c792d5d05d79f4683b10a2d3446333e6053ead4d21'
def read(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);size=struct.unpack_from('<I',raw,20+n)[0];return raw,doc,raw[28+n:28+n+size]
def write(path,doc,bin):
 jb=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode();jb+=b' '*((-len(jb))%4);bin+=b'\0'*((-len(bin))%4);path.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(jb)+len(bin))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(bin),b'BIN\0')+bin)
def sh(b):return hashlib.sha256(b).hexdigest()
def accessor_bytes(doc,blob,i):
 a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];return blob[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
def run(source,out,textures):
 raw,d,bb=read(source);assert sh(raw)==EXPECTED
 target=next(n for n in d['nodes']if n.get('name')==TARGET)['mesh'];prim=d['meshes'][target]['primitives'][0];mi=prim['material'];proof={'source_sha256':sh(raw),'source_bytes':len(raw),'unique_mesh_triangle_count':sum(d['accessors'][p['indices']]['count']//3 for m in d['meshes']for p in m['primitives']),'instanced_scene_triangle_count':sum(sum(d['accessors'][p['indices']]['count']//3 for p in d['meshes'][n['mesh']]['primitives'])for n in d['nodes']if 'mesh'in n),'target_triangle_count':d['accessors'][prim['indices']]['count']//3,'target_mesh':target,'source_material':mi,'variants':{}}
 hashes={str(i):sh(accessor_bytes(d,bb,i))for i in range(len(d['accessors']))};(out/'frozen-accessor-hashes.json').write_text(json.dumps(hashes,indent=2))
 for variant in ['fine','soft']:
  nd=copy.deepcopy(d);nb=bytearray(bb);clone=copy.deepcopy(d['materials'][mi]);clone['name']='Staghorn01 | '+variant+' surface test';normal_index=None;rough_index=None
  for kind in ['normal','metallic-roughness']:
   data=(textures/(variant+'-'+kind+'.png')).read_bytes();nb.extend(b'\0'*((-len(nb))%4));view=len(nd['bufferViews']);nd['bufferViews'].append({'buffer':0,'byteOffset':len(nb),'byteLength':len(data)});nb.extend(data)
   image=len(nd['images']);nd['images'].append({'name':variant+'-'+kind,'bufferView':view,'mimeType':'image/png'});texture=len(nd['textures']);nd['textures'].append({'sampler':d['textures'][clone['normalTexture']['index']]['sampler'],'source':image})
   if kind=='normal':normal_index=texture
   else:rough_index=texture
  clone['normalTexture']['index']=normal_index;clone['pbrMetallicRoughness']['metallicRoughnessTexture']['index']=rough_index
  ni=len(nd['materials']);nd['materials'].append(clone);nd['meshes'][target]['primitives'][0]['material']=ni;nd['buffers'][0]['byteLength']=len(nb)
  path=out/(variant+'.glb');write(path,nd,nb);rr,rd,rb=read(path)
  assert rb[:len(bb)]==bb
  assert all(sh(accessor_bytes(rd,rb,i))==h for i,h in ((int(k),v)for k,v in hashes.items()))
  assert rd['nodes']==d['nodes'] and rd['accessors']==d['accessors'] and rd['scenes']==d['scenes']
  for i,m in enumerate(d['meshes']):
   rm=copy.deepcopy(rd['meshes'][i]);
   if i==target:rm['primitives'][0]['material']=mi
   assert rm==m
  assert rd['materials'][:len(d['materials'])]==d['materials']
  proof['variants'][variant]={'path':path.name,'sha256':sh(rr),'bytes':len(rr),'added_bytes':len(rr)-len(raw),'target_material_index':ni,'target_material_name':clone['name'],'original_binary_prefix_identical':True,'all_accessor_hashes_identical':True,'all_nodes_scenes_accessors_identical':True,'all_original_materials_identical':True,'only_target_material_assignment_changed':True,'geometry_uv_normals_colors_indices_unchanged':True,'normal_scale':clone['normalTexture']['scale']}
 (out/'asset-preservation-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--textures',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);run(a.source,a.out,a.textures or a.out/'textures')
