"""Append geometry only and replace22 original mesh primitives, preserving every original node and binary byte."""
import sys,json,struct,copy,hashlib,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('replacement',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
def read(f):
 raw=f.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);size=struct.unpack_from('<I',raw,20+n)[0];return raw,j,bytearray(raw[28+n:28+n+size])
raw,source,b=read(a.source);rr,r,rb=read(a.replacement);assert hashlib.sha256(raw).hexdigest()=='deac6a8e6d2173fc649023b763264f3b195fc5c084bf5a2c58c3ca76c4abcb0e';original_bin=bytes(b);j=copy.deepcopy(source);mapping={};views={};changed=[]
def copy_accessor(i):
 if i in mapping:return mapping[i]
 ac=copy.deepcopy(r['accessors'][i]);vi=ac['bufferView'];assert 'sparse'not in ac
 if vi not in views:
  v=copy.deepcopy(r['bufferViews'][vi]);off=v.get('byteOffset',0);data=rb[off:off+v['byteLength']];b.extend(b'\0'*(-len(b)%4));v['byteOffset']=len(b);v['buffer']=0;b.extend(data);views[vi]=len(j['bufferViews']);j['bufferViews'].append(v)
 ac['bufferView']=views[vi];mapping[i]=len(j['accessors']);j['accessors'].append(ac);return mapping[i]
for rn in r['nodes']:
 if not rn.get('name','').startswith('Coral_Staghorn_Thicket_'):continue
 sn=next(n for n in j['nodes']if n.get('name')==rn['name']);mi=sn['mesh'];rm=copy.deepcopy(r['meshes'][rn['mesh']]);rm['name']=j['meshes'][mi]['name'];assert not any(k in rn for k in ('translation','rotation','scale','matrix'))
 assert len(rm['primitives'])==len(j['meshes'][mi]['primitives'])==1;mat=j['meshes'][mi]['primitives'][0]['material']
 for prim in rm['primitives']:prim['attributes']={k:copy_accessor(v)for k,v in prim['attributes'].items()};prim['indices']=copy_accessor(prim['indices']);prim['material']=mat
 j['meshes'][mi]=rm;changed.append({'name':rn['name'],'mesh_index':mi,'shared_nodes':[n['name']for n in j['nodes']if n.get('mesh')==mi]})
assert len(changed)==22
j['buffers'][0]['byteLength']=len(b);jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*(-len(jb)%4);b+=b'\0'*(-len(b)%4);out=struct.pack('<4sII',b'glTF',2,28+len(jb)+len(b))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(b),b'BIN\0')+b;a.output.write_bytes(out);ids={c['mesh_index']for c in changed}
checks={'all_nodes_transforms_and_mesh_references_unchanged':j['nodes']==source['nodes'],'all_noncoral_meshes_unchanged':all(m==j['meshes'][i]for i,m in enumerate(source['meshes'])if i not in ids),'all_original_accessors_unchanged':j['accessors'][:len(source['accessors'])]==source['accessors'],'all_original_buffer_views_unchanged':j['bufferViews'][:len(source['bufferViews'])]==source['bufferViews'],'entire_original_binary_prefix_unchanged':bytes(b[:len(original_bin)])==original_bin,'materials_images_textures_samplers_unchanged':all(j.get(k)==source.get(k)for k in ('materials','images','textures','samplers')),'all_other_scene_state_unchanged':all(j[k]==v for k,v in source.items()if k not in ('meshes','accessors','bufferViews','buffers'))};assert all(checks.values())
h=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest();report={'source_sha256':hashlib.sha256(raw).hexdigest(),'candidate_sha256':hashlib.sha256(out).hexdigest(),'candidate_bytes':len(out),'appended_binary_bytes':len(b)-len(original_bin),'checks':checks,'changed_original_meshes':changed,'preserved_hashes':{k:h(j.get(k))for k in ('nodes','materials','images','textures','samplers','scenes','animations')},'scope':'Only22 original thicket mesh primitive accessor references updated. Existing distant nodes automatically use their shared corrected original meshes, with transforms unchanged.'};a.output.with_suffix('.proof.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k not in ('changed_original_meshes','preserved_hashes')},indent=2))
