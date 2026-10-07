"""Independent exported-byte proof. No geometry recipe imports."""
import argparse,hashlib,json,struct
from pathlib import Path
import numpy as np

def read(p):
 r=p.read_bytes();assert struct.unpack_from('<4sII',r)==(b'glTF',2,len(r));n=struct.unpack_from('<I',r,12)[0];return r,json.loads(r[20:20+n]),r[28+n:]
def array(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];d={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];c={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
 return np.ndarray((a['count'],c),d,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',c*np.dtype(d).itemsize),np.dtype(d).itemsize))
p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('output',type=Path);p.add_argument('--runtime-snapshot',type=Path);a=p.parse_args()
old,oj,ob=read(a.baseline);raw,j,b=read(a.candidate);assert hashlib.sha256(old).hexdigest()=='c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd'
tm=next(n['mesh']for n in oj['nodes']if n['name']=='Spatial_Continuous_Weathered_Limestone');op=oj['meshes'][tm]['primitives'][0];pr=j['meshes'][tm]['primitives'][0]
assert j['nodes']==oj['nodes'];assert j['accessors'][:len(oj['accessors'])]==oj['accessors'];assert j['bufferViews'][:len(oj['bufferViews'])]==oj['bufferViews'];assert b[:len(ob)]==ob
for k in oj:
 if k not in ['accessors','bufferViews','buffers','meshes']:assert j[k]==oj[k],k
payload=0
for i,m in enumerate(oj['meshes']):
 if i==tm:continue
 assert j['meshes'][i]==m
 for p in m['primitives']:
  for ac in list(p['attributes'].values())+[p['indices']]:assert array(oj,ob,ac).tobytes()==array(j,b,ac).tobytes();payload+=1
v=array(j,b,pr['attributes']['POSITION']);f=array(j,b,pr['indices']).reshape(-1,3);v0=array(oj,ob,op['attributes']['POSITION']);f0=array(oj,ob,op['indices']).reshape(-1,3);assert np.array_equal(v[:len(v0)],v0)
assert np.isfinite(v).all();assert f.max()<len(v);norm=array(j,b,pr['attributes']['NORMAL']);assert np.isfinite(norm).all();used=np.unique(f);assert np.max(np.abs(np.linalg.norm(norm[used],axis=1)-1))<1e-5
# Every original face outside the selected square is exact and in order.
cent=v0[f0].mean(1);cut=(cent[:,0]>-13)&(cent[:,0]<-3)&(cent[:,2]>-29)&(cent[:,2]<-19)&(f0.max(1)<9797);retained=f0[~cut];assert np.array_equal(f[:len(retained)],retained)
newf=f[len(retained):];nv=v[newf.ravel()];assert (nv[:,0]>=-13-1e-6).all()and(nv[:,0]<=-3+1e-6).all()and(nv[:,2]>=-29-1e-6).all()and(nv[:,2]<=-19+1e-6).all()
# All original vertex attribute bytes, other than boundary normals, are exact.
for k in ['POSITION','TEXCOORD_0','COLOR_0']:
 x=array(oj,ob,op['attributes'][k]);y=array(j,b,pr['attributes'][k]);assert np.array_equal(x,y[:len(x)])
n0=array(oj,ob,op['attributes']['NORMAL']);changed=np.where(np.any(norm[:len(n0)]!=n0,axis=1))[0];q=v0[changed];assert np.all(((q[:,0]==-13)|(q[:,0]==-3)|(q[:,2]==-29)|(q[:,2]==-19))&((q[:,0]>=-13)&(q[:,0]<=-3)&(q[:,2]>=-29)&(q[:,2]<=-19)))
fn=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);areas=np.linalg.norm(fn,axis=1)/2;assert areas.min()>1e-8
ed=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);edges,inv,c=np.unique(np.sort(ed,axis=1),return_inverse=True,return_counts=True,axis=0);orient=np.zeros(len(edges),int);np.add.at(orient,inv,np.where(ed[:,0]<ed[:,1],1,-1));assert(c==2).all()and(orient==0).all();volume=np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()/6;assert volume>0
adj={int(i):[]for i in used}
for x,y in edges:adj[int(x)].append(int(y));adj[int(y)].append(int(x))
seen={int(used[0])};todo=[int(used[0])]
while todo:
 for nxt in adj[todo.pop()]:
  if nxt not in seen:seen.add(nxt);todo.append(nxt)
assert len(seen)==len(used)
runtime={}
if a.runtime_snapshot:
 snap=json.loads(a.runtime_snapshot.read_text())
 for name,sha in snap['files'].items():actual=hashlib.sha256((Path(snap['root'])/name).read_bytes()).hexdigest();assert actual==sha;runtime[name]=True
report={'baseline_sha256':hashlib.sha256(old).hexdigest(),'candidate_sha256':hashlib.sha256(raw).hexdigest(),'candidate_bytes':len(raw),'under_32MiB':len(raw)<32*1024*1024,'all_original_binary_bytes_exact':True,'all_node_transforms_exact':True,'original_nonterrain_meshes_exact':len(oj['meshes'])-1,'protected_primitive_payloads':payload,'all_original_materials_images_textures_lights_cameras_scenes_exact':True,'unchanged_original_faces':len(retained),'removed_faces_in_local_square':int(cut.sum()),'new_patch_faces':len(newf),'patch_bounds_x_z':[-13,-3,-29,-19],'original_positions_uv_colors_exact':True,'original_boundary_normals_recomputed':len(changed),'nonmanifold_edges':int(sum(c!=2)),'inconsistent_edge_orientations':int(sum(orient!=0)),'degenerate_faces':int(sum(areas<=1e-8)),'minimum_triangle_area_m2':float(areas.min()),'signed_volume_m3':float(volume),'connected_referenced_mesh':True,'terrain_vertices':len(v),'terrain_triangles':len(f),'retained_unused_original_vertices':len(v)-len(used),'new_downward_facing_triangles':int(sum(fn[len(retained):,1]<-1e-7)),'runtime_files_unchanged':runtime}
a.output.write_text(json.dumps(report,indent=2));print(json.dumps(report))
