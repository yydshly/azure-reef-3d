"""Losslessly externalize an exported GLB for the host's per-file limit."""
import json,struct,hashlib,pathlib
p=pathlib.Path('dist/assets');raw=pathlib.Path('source-model.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);start=20+n;bn,typ=struct.unpack_from('<II',raw,start);binary=raw[start+8:start+8+bn]
image_views={im['bufferView'] for im in doc.get('images',[]) if 'bufferView'in im}
for i,im in enumerate(doc.get('images',[])):
 v=doc['bufferViews'][im.pop('bufferView')];part=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];name=f'reef-texture-{i}.png';(p/name).write_bytes(part);im['uri']=name
new=[];data=bytearray();mapping={}
for i,v in enumerate(doc['bufferViews']):
 if i in image_views:continue
 while len(data)%4:data.append(0)
 original=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];w=dict(v);w['buffer']=0;w['byteOffset']=len(data);data.extend(original);mapping[i]=len(new);new.append(w)
for a in doc.get('accessors',[]):
 if 'bufferView'in a:a['bufferView']=mapping[a['bufferView']]
 for v in a.get('sparse',{}).values():
  if isinstance(v,dict) and 'bufferView'in v:v['bufferView']=mapping[v['bufferView']]
doc['bufferViews']=new;doc['buffers']=[{'uri':'reef.bin','byteLength':len(data)}];(p/'reef.bin').write_bytes(data);(p/'reef.gltf').write_text(json.dumps(doc,separators=(',',':')))
for f in p.iterdir():assert f.stat().st_size<=26214400,(f,f.stat().st_size)
print(json.dumps({'source_glb_sha256':hashlib.sha256(raw).hexdigest(),'binary_bytes':len(data),'images':len(doc.get('images',[])),'lossless_externalization':True}))
