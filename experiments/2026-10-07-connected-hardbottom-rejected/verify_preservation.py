"""Independent exported-byte and topology verification; no recipe imports."""
import argparse,hashlib,json,struct
from collections import deque
from pathlib import Path
import numpy as np

def read(p):
    r=p.read_bytes();assert struct.unpack_from('<4sII',r)==(b'glTF',2,len(r));n=struct.unpack_from('<I',r,12)[0];return r,json.loads(r[20:20+n]),r[28+n:]
def array(j,b,i):
    ac=j['accessors'][i];v=j['bufferViews'][ac['bufferView']];d={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[ac['componentType']];cols={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[ac['type']]
    return np.ndarray((ac['count'],cols),d,buffer=b,offset=v.get('byteOffset',0)+ac.get('byteOffset',0),strides=(v.get('byteStride',cols*np.dtype(d).itemsize),np.dtype(d).itemsize))

p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('output',type=Path);p.add_argument('--runtime-snapshot',type=Path);a=p.parse_args()
old,oj,ob=read(a.baseline);raw,j,b=read(a.candidate)
tn=next(i for i,n in enumerate(oj['nodes'])if n['name']=='Spatial_Continuous_Weathered_Limestone');tm=oj['nodes'][tn]['mesh'];tp=oj['meshes'][tm]['primitives'][0];allowed_accessors=set(tp['attributes'].values())|{tp['indices']};allowed_views={oj['accessors'][i]['bufferView']for i in allowed_accessors}
assert len(j['nodes'])==len(oj['nodes']) and len(j['meshes'])==len(oj['meshes'])
changed=[];protected_nodes=0
for i,(x,y)in enumerate(zip(oj['nodes'],j['nodes'])):
    if x==y:protected_nodes+=1;continue
    assert x['name'].startswith('Spatial_Staghorn_Linked_')
    assert {k:v for k,v in x.items()if k!='translation'}=={k:v for k,v in y.items()if k!='translation'}
    assert x['translation'][0]==y['translation'][0]and x['translation'][2]==y['translation'][2]
    changed.append(x['name'])
assert len(changed)<=4
primitive_hashes={}
for i,m in enumerate(oj['meshes']):
    if i==tm:continue
    assert j['meshes'][i]==m
    for pi,pr in enumerate(m['primitives']):
        for role,ac in list(pr['attributes'].items())+[('indices',pr['indices'])]:
            assert oj['accessors'][ac]==j['accessors'][ac]
            ba=array(oj,ob,ac).tobytes();bb=array(j,b,ac).tobytes();assert ba==bb
            primitive_hashes[f'{i}/{pi}/{role}']=hashlib.sha256(ba).hexdigest()
for i,x in enumerate(oj['accessors']):
    if i not in allowed_accessors:assert j['accessors'][i]==x and array(oj,ob,i).tobytes()==array(j,b,i).tobytes()
for i,vw in enumerate(oj['bufferViews']):
    if i not in allowed_views:
        assert j['bufferViews'][i]==vw
        start=vw.get('byteOffset',0);end=start+vw['byteLength'];assert ob[start:end]==b[start:end]
top_preserved={}
for k in oj:
    if k in ['accessors','bufferViews','buffers','nodes','meshes']:continue
    assert oj[k]==j[k];top_preserved[k]=True
pr=j['meshes'][tm]['primitives'][0];v=array(j,b,pr['attributes']['POSITION']);idx=array(j,b,pr['indices']).reshape(-1,3);n=array(j,b,pr['attributes']['NORMAL'])
assert all(np.isfinite(array(j,b,x)).all()for x in pr['attributes'].values());assert idx.max()<len(v)
face_n=np.cross(v[idx[:,1]]-v[idx[:,0]],v[idx[:,2]]-v[idx[:,0]]);areas=np.linalg.norm(face_n,axis=1)/2;assert areas.min()>1e-8
directed=np.concatenate([idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]]);edges=np.sort(directed,axis=1);keys,inv,count=np.unique(edges,return_inverse=True,return_counts=True,axis=0);orientation=np.zeros(len(keys),dtype=np.int32);np.add.at(orientation,inv,np.where(directed[:,0]<directed[:,1],1,-1));assert(count==2).all()and(orientation==0).all()
volume=np.einsum('ij,ij->i',v[idx[:,0]],np.cross(v[idx[:,1]],v[idx[:,2]])).sum()/6;assert volume>0
normal_error=float(np.max(np.abs(np.linalg.norm(n,axis=1)-1)));assert normal_error<1e-5
bound=(v[:,0]==-24)|(v[:,0]==24)|(v[:,2]==-61)|(v[:,2]==-11);assert v[bound,1].max()<-.22
# Diagnostic visible footprint components, independent of buried mesh links.
nx=len(np.unique(v[:,0]));nz=len(np.unique(v[:,2]));top=v[:nx*nz,1].reshape(nz,nx);mask=top>-.2199;seen=np.zeros_like(mask);components=[]
for iz,ix in zip(*np.where(mask)):
    if seen[iz,ix]:continue
    q=deque([(iz,ix)]);seen[iz,ix]=True;size=0
    while q:
        z,x=q.popleft();size+=1
        for dz,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
            zz,xx=z+dz,x+dx
            if 0<=zz<nz and 0<=xx<nx and mask[zz,xx]and not seen[zz,xx]:seen[zz,xx]=True;q.append((zz,xx))
    components.append(size)
components.sort(reverse=True)
runtime={}
if a.runtime_snapshot:
    snap=json.loads(a.runtime_snapshot.read_text())
    for name,sha in snap['files'].items():
        actual=hashlib.sha256((Path(snap['root'])/name).read_bytes()).hexdigest();assert actual==sha;runtime[name]=True
report={'baseline_sha256':hashlib.sha256(old).hexdigest(),'candidate_sha256':hashlib.sha256(raw).hexdigest(),'candidate_bytes':len(raw),'under_32MiB':len(raw)<=32*1024*1024,'original_nonterrain_meshes_exact':len(oj['meshes'])-1,'protected_primitive_payloads':len(primitive_hashes),'all_protected_nodes_exact':True,'changed_nodes_y_only':changed,'top_level_preservation':top_preserved,'runtime_files_unchanged':runtime,'new_meshes':0,'new_nodes':0,'new_materials_or_images':False,'terrain_vertices':len(v),'terrain_triangles':len(idx),'nonmanifold_edges':int(np.count_nonzero(count!=2)),'inconsistent_edge_orientations':int(np.count_nonzero(orientation)),'outward_signed_volume_m3':float(volume),'minimum_triangle_area_m2':float(areas.min()),'maximum_normal_length_error':normal_error,'outer_perimeter_top_y':float(v[bound,1].max()),'above_sand_grid_components':components,'two_largest_fraction_of_visible_rock_samples':float(sum(components[:2])/sum(components)),'primitive_payload_sha256':primitive_hashes}
a.output.write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='primitive_payload_sha256'}))
