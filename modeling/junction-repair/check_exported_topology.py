"""Zero-tolerance exported topology and frozen specimen equivalence. Read only."""
import json,struct,hashlib,collections
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent

def read(p):
 r=p.read_bytes();n=struct.unpack_from('<I',r,12)[0];return r,json.loads(r[20:20+n]),r[28+n:]
def arr(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];cols={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.ndarray((a['count'],cols),dtype=dtype,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',np.dtype(dtype).itemsize*cols),np.dtype(dtype).itemsize))
raw,j,b=read(P/'candidate.glb');reports=[]
for node in j['nodes']:
 if not node.get('name','').startswith('Coral_Staghorn_Thicket_'):continue
 prim=j['meshes'][node['mesh']]['primitives'][0];v=arr(j,b,prim['attributes']['POSITION']);f=arr(j,b,prim['indices']).reshape(-1,3);u,remap=np.unique(v,axis=0,return_inverse=True);t=remap[f];edges=collections.Counter();directions=collections.Counter();neighbors=[set()for _ in u]
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
 r={'name':node['name'],'export_vertices':len(v),'exact_unique_positions':len(u),'triangles':len(t),'components':components,'boundary_edges':sum(n==1 for n in edges.values()),'nonmanifold_edges':sum(n!=2 for n in edges.values()),'orientation_inconsistent_edges':sum(directions[e]!=1 or directions[e[::-1]]!=1 for e in edges),'degenerate_triangles':sum(len(set(map(int,t)))<3 for t in t)}
 assert r['boundary_edges']==r['nonmanifold_edges']==r['orientation_inconsistent_edges']==r['degenerate_triangles']==0,r
 reports.append(r)
# The source01 primitive must also be the same already-reviewed replacement arrays, not a new iteration.
fingerprints=json.loads((P/'frozen-hero-primitive-hashes.json').read_text())['primitive'];n=next(x for x in j['nodes']if x.get('name')=='Coral_Staghorn_Thicket_01');p=j['meshes'][n['mesh']]['primitives'][0]
match={}
for k,i in dict(p['attributes'],indices=p['indices']).items():
 data=arr(j,b,i);expected=fingerprints[k];match[k]=hashlib.sha256(data.tobytes()).hexdigest()==expected['sha256'] and list(data.shape)==expected['shape'] and str(data.dtype)==expected['dtype']
assert all(match.values()),match
proof={'candidate_sha256':hashlib.sha256(raw).hexdigest(),'all22_exact_export_topology_pass':True,'method':'Exact float32 coordinate tuple remapping only; no tolerance or asset edits','frozen_one_specimen_attribute_arrays_identical':match,'total_triangles':sum(x['triangles']for x in reports),'total_exact_vertices':sum(x['exact_unique_positions']for x in reports),'meshes':reports};(P/'exported-topology-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps({k:v for k,v in proof.items()if k!='meshes'},indent=2))
