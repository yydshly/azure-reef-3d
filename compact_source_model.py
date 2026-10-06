"""Remove unreferenced authoring storage without changing the active GLB scene."""
import argparse, hashlib, json, pathlib, struct
p=argparse.ArgumentParser();p.add_argument('input',type=pathlib.Path);p.add_argument('output',type=pathlib.Path);args=p.parse_args()
raw=args.input.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=raw[28+n:];original_views=doc['bufferViews']
# The authoritative source retains prior authoring data for provenance. Drop only
# unreferenced mesh/accessor records from the deployment, without changing any
# live scene attribute, index, material, node, skin or animation value.
assert 'KHR_draco_mesh_compression' not in doc.get('extensionsUsed', []), 'Compressed mesh externalization needs its own view handling'
used_meshes = sorted({node['mesh'] for node in doc.get('nodes', []) if 'mesh' in node})
mesh_map = {old: new for new, old in enumerate(used_meshes)}
doc['meshes'] = [doc['meshes'][index] for index in used_meshes]
for node in doc.get('nodes', []):
    if 'mesh' in node:
        node['mesh'] = mesh_map[node['mesh']]
used_accessors = set()
for mesh in doc['meshes']:
    for primitive in mesh['primitives']:
        used_accessors.update(primitive.get('attributes', {}).values())
        if 'indices' in primitive:
            used_accessors.add(primitive['indices'])
        for target in primitive.get('targets', []):
            used_accessors.update(target.values())
for skin in doc.get('skins', []):
    if 'inverseBindMatrices' in skin:
        used_accessors.add(skin['inverseBindMatrices'])
for animation in doc.get('animations', []):
    for sampler in animation['samplers']:
        used_accessors.update((sampler['input'], sampler['output']))
accessor_map = {old: new for new, old in enumerate(sorted(used_accessors))}
for mesh in doc['meshes']:
    for primitive in mesh['primitives']:
        primitive['attributes'] = {key: accessor_map[value] for key, value in primitive['attributes'].items()}
        if 'indices' in primitive:
            primitive['indices'] = accessor_map[primitive['indices']]
        for target in primitive.get('targets', []):
            for key, value in list(target.items()):
                target[key] = accessor_map[value]
for skin in doc.get('skins', []):
    if 'inverseBindMatrices' in skin:
        skin['inverseBindMatrices'] = accessor_map[skin['inverseBindMatrices']]
for animation in doc.get('animations', []):
    for sampler in animation['samplers']:
        sampler['input'] = accessor_map[sampler['input']]
        sampler['output'] = accessor_map[sampler['output']]
doc['accessors'] = [doc['accessors'][index] for index in sorted(used_accessors)]
used_views = set()
for accessor in doc['accessors']:
    if 'bufferView' in accessor:
        used_views.add(accessor['bufferView'])
    for value in accessor.get('sparse', {}).values():
        if isinstance(value, dict) and 'bufferView' in value:
            used_views.add(value['bufferView'])


used_views.update(im['bufferView'] for im in doc.get('images',[]) if 'bufferView' in im)
views=[];data=bytearray();mapping={}
for old_index,view in enumerate(original_views):
 if old_index not in used_views:continue
 while len(data)%4:data.append(0)
 offset=view.get('byteOffset',0);payload=binary[offset:offset+view['byteLength']]
 updated=dict(view);updated['buffer']=0;updated['byteOffset']=len(data);data.extend(payload);mapping[old_index]=len(views);views.append(updated)
 assert bytes(data[updated['byteOffset']:updated['byteOffset']+updated['byteLength']])==payload
for accessor in doc['accessors']:
 if 'bufferView' in accessor:accessor['bufferView']=mapping[accessor['bufferView']]
 for value in accessor.get('sparse',{}).values():
  if isinstance(value,dict) and 'bufferView' in value:value['bufferView']=mapping[value['bufferView']]
for im in doc.get('images',[]):
 if 'bufferView' in im:im['bufferView']=mapping[im['bufferView']]
doc['bufferViews']=views;doc['buffers']=[{'byteLength':len(data)}]
js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((-len(js))%4);data+=b'\0'*((-len(data))%4)
out=struct.pack('<4sII',b'glTF',2,28+len(js)+len(data))+struct.pack('<I4s',len(js),b'JSON')+js+struct.pack('<I4s',len(data),b'BIN\0')+data
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(out)
proof={'input_sha256':hashlib.sha256(raw).hexdigest(),'output_sha256':hashlib.sha256(out).hexdigest(),'input_bytes':len(raw),'output_bytes':len(out),'kept_buffer_views':len(views),'removed_unreferenced_views':len(original_views)-len(views),'all_retained_view_bytes_identical':True,'method':'Only unreachable mesh/accessor storage removed; scene nodes, transforms, materials, images and live attribute/index bytes preserved.'}
args.output.with_suffix('.compact-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
