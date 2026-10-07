import json,struct,hashlib,collections,argparse
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();P=a.out;SRC=a.source

def read(p):
 raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);sz=struct.unpack_from('<I',raw,20+n)[0];return raw,j,raw[28+n:28+n+sz]
def arr(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dt={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.ndarray((a['count'],n),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',np.dtype(dt).itemsize*n),np.dtype(dt).itemsize))
raw,j,b=read(P/'replacement.glb');sr,sj,sb=read(SRC);prim=j['meshes'][0]['primitives'][0];sp=sj['meshes'][47]['primitives'][0];v=arr(j,b,prim['attributes']['POSITION']);sv=arr(sj,sb,sp['attributes']['POSITION']);f=arr(j,b,prim['indices']).reshape(-1,3);u,remap=np.unique(v,axis=0,return_inverse=True);t=remap[f];edges=collections.Counter();directions=collections.Counter();neighbors=[set()for _ in u]
for x,y,z in t:
 for a,c in [(x,y),(y,z),(z,x)]:edges[tuple(sorted((int(a),int(c))))]+=1;directions[(int(a),int(c))]+=1;neighbors[a].add(int(c));neighbors[c].add(int(a))
seen=set();components=0
for root in range(len(u)):
 if root in seen:continue
 components+=1;stack=[root]
 while stack:
  a=stack.pop()
  if a in seen:continue
  seen.add(a);stack.extend(neighbors[a]-seen)
checks={'triangle_budget_identical':len(t)==22168,'inside_original_local_envelope':bool(np.all(v.min(axis=0)>=sv.min(axis=0))and np.all(v.max(axis=0)<=sv.max(axis=0))),'zero_boundary_edges':all(n!=1 for n in edges.values()),'zero_nonmanifold_edges':all(n==2 for n in edges.values()),'consistent_edge_orientation':all(directions[e]==1 and directions[e[::-1]]==1 for e in edges),'zero_degenerate_index_triangles':all(len(set(map(int,x)))==3 for x in t),'zero_area_triangles':bool(np.all(np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>0))}
attrs={k:{'shape':list(arr(j,b,i).shape),'bytes':arr(j,b,i).nbytes}for k,i in prim['attributes'].items()};attrs['indices']={'shape':list(arr(j,b,prim['indices']).shape),'bytes':arr(j,b,prim['indices']).nbytes}
views=set(j['accessors'][i]['bufferView']for i in list(prim['attributes'].values())+[prim['indices']]);proof={'status':'PASS'if all(checks.values())else'FAIL','checks':checks,'triangles':len(t),'exported_vertices':len(v),'exact_unique_positions':len(u),'closed_connected_components':components,'replacement_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':hashlib.sha256(sr).hexdigest(),'attributes':attrs,'additional_geometry_buffer_bytes_if_single_user_mesh_appended':sum(j['bufferViews'][i]['byteLength']for i in views),'additional_runtime_attribute_and_index_bytes_if_integrated':sum(x['bytes']for x in attrs.values()),'runtime_memory_note':'Typed geometry buffers only; driver allocation, CPU object overhead, duplicated cache and renderer-specific costs are not measured. Textures and material are to be reused.'}
(P/'exported-topology-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2));assert all(checks.values())
