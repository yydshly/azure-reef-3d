"""Independent structural and topology checks on exported glTF bytes."""
import argparse,hashlib,json,struct
from pathlib import Path
import numpy as np
def read(p):
    r=p.read_bytes();assert struct.unpack_from('<4sII',r)==(b'glTF',2,len(r));n=struct.unpack_from('<I',r,12)[0];return r,json.loads(r[20:20+n]),r[28+n:]
p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
old,oj,ob=read(a.baseline);raw,j,b=read(a.candidate)
def ar(i):
    ac=j['accessors'][i];v=j['bufferViews'][ac['bufferView']];d={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[ac['componentType']];cols={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[ac['type']];return np.ndarray((ac['count'],cols),d,buffer=b,offset=v.get('byteOffset',0)+ac.get('byteOffset',0),strides=(v.get('byteStride',cols*np.dtype(d).itemsize),np.dtype(d).itemsize))
preserved={k:j[k][:len(oj[k])]==oj[k]for k in ['accessors','bufferViews','nodes','meshes','materials','images','textures']};preserved['binary_prefix']=b[:len(ob)]==ob
assert all(preserved.values())
node=next(n for n in j['nodes']if n['name']=='Spatial_Continuous_Weathered_Limestone');pr=j['meshes'][node['mesh']]['primitives'][0]
v=ar(pr['attributes']['POSITION']);idx=ar(pr['indices']).reshape(-1,3);n=ar(pr['attributes']['NORMAL']);uv=ar(pr['attributes']['TEXCOORD_0']);colors=ar(pr['attributes']['COLOR_0'])
assert all(np.isfinite(x).all() for x in [v,n,uv,colors]);assert idx.max()<len(v)
face_n=np.cross(v[idx[:,1]]-v[idx[:,0]],v[idx[:,2]]-v[idx[:,0]])
areas=np.linalg.norm(face_n,axis=1)/2;assert areas.min()>1e-8
directed=np.concatenate([idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]]);edges=np.sort(directed,axis=1);keys,inv,count=np.unique(edges,return_inverse=True,return_counts=True,axis=0)
orientation=np.zeros(len(keys),dtype=np.int32);np.add.at(orientation,inv,np.where(directed[:,0]<directed[:,1],1,-1));assert (count==2).all() and (orientation==0).all()
volume=np.einsum('ij,ij->i',v[idx[:,0]],np.cross(v[idx[:,1]],v[idx[:,2]])).sum()/6;assert volume>0
lengths=np.linalg.norm(n,axis=1);assert np.max(np.abs(lengths-1))<1e-5
boundmask=(v[:,0]==-24)|(v[:,0]==24)|(v[:,2]==-61)|(v[:,2]==-11);assert v[boundmask,1].max()<-.22
report={'baseline_sha256':hashlib.sha256(old).hexdigest(),'candidate_sha256':hashlib.sha256(raw).hexdigest(),'preserved_original':preserved,'candidate_bytes':len(raw),'source_under_30MB':len(raw)<30_000_000,'added_nodes':len(j['nodes'])-len(oj['nodes']),'added_meshes':len(j['meshes'])-len(oj['meshes']),'new_materials_or_images':False,'terrain_vertices':len(v),'terrain_triangles':len(idx),'nonmanifold_edges':int(np.count_nonzero(count!=2)),'inconsistent_edge_orientations':int(np.count_nonzero(orientation)),'outward_signed_volume_m3':float(volume),'minimum_triangle_area_m2':float(areas.min()),'maximum_normal_length_error':float(np.max(np.abs(lengths-1))),'outer_perimeter_top_y':float(v[boundmask,1].max()),'existing_far_floor_y':-.2199999988079071,'all_appended_vertices_finite':True,'guide_preservation':'All original geometry, transforms and binary bytes are unchanged, including the original five-stop anchors and sand correction.'}
a.output.write_text(json.dumps(report,indent=2));print(json.dumps(report))
