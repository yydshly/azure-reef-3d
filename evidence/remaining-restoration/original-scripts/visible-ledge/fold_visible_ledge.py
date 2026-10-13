"""One bounded folded reef-edge experiment, 2026-10-07.

The accepted grid's columns become a genuine lateral returning profile.  No
connectivity, vertex count, UV, material, biological form or external asset edits.
Hand-authored longitudinal stations set unequal crest heights and recess depths;
there is no procedural noise, parameter search, appended solid or heightfield cut.
All dimensions are interpreted scene units, not ecological measurements.
"""
import argparse, hashlib, json, struct
from pathlib import Path
import numpy as np

SOURCE_SHA='c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd'
LANDMARK_SHA='d6377e6bcfc5145ef6da7c139de26772b6065b30fbe24c2d3180bcba9ae48cdf'
NODE='Spatial_Continuous_Weathered_Limestone'

def glb(path):
    raw=Path(path).read_bytes();n=struct.unpack_from('<I',raw,12)[0]
    return raw,json.loads(raw[20:20+n]),28+n

def array(raw,j,base,idx):
    a=j['accessors'][idx];b=j['bufferViews'][a['bufferView']]
    n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    dtype={5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
    offset=base+b.get('byteOffset',0)+a.get('byteOffset',0)
    assert not b.get('byteStride')
    return np.frombuffer(raw,dtype=dtype,count=a['count']*n,offset=offset).reshape(a['count'],n).copy(),offset

def smooth(x):
    x=np.clip(x,0,1);return x*x*(3-2*x)

def fold(v):
    result=v.copy();stations=[]
    # In each cross-section, rows 6.0->7.5 return toward the channel as Y rises.
    # That negative dX produces a real underside, not a steep upward gully.
    old_x=np.arange(4.0,10.51,.5)
    base_x=np.array([4,4.5,5.1,5.65,6.0,5.95,5.5,4.9,5.0,5.7,6.9,8.3,10,10.5])
    lateral_weight=np.array([0,0,.15,.5,1,1,1,1,1,.8,.4,.12,0,0])
    zs=np.array([-54,-52,-50.5,-49.5,-48.5,-47.5,-46.5,-45.5,-44.5,-43.5,-42.5])
    heights=np.array([1.15,1.30,1.68,1.40,1.82,1.67,1.20,1.57,1.35,1.20,1.15])
    shifts=np.array([.8,.7,.35,.5,.15,.05,.55,.20,-.75,-.75,-.2])
    for z in np.arange(-54,-42.49,.5):
        ids=np.array([np.flatnonzero((v[:9797,0]==x)&(v[:9797,2]==z))[0] for x in old_x])
        original=v[ids].astype('f8')
        strength=float(smooth((z+54)/2)*smooth((-42.5-z)/1.5))
        if strength==0:continue
        h=float(np.interp(z,zs,heights));shift=float(np.interp(z,zs,shifts))
        floor=float(original[1,1])
        profile_y=np.array([original[0,1],floor,floor+.03,floor+.08,
                            floor+.24,h-.62,h-.43,h-.28,h,h+.08,
                            h-.04,original[11,1],original[12,1],original[13,1]])
        target=original.copy();target[:,0]=base_x+shift*lateral_weight;target[:,1]=profile_y
        result[ids]=(original+(target-original)*strength).astype('<f4')
        stations.append({'z':float(z),'strength':strength,'crest':h,'lateral_shift':shift,
                         'profile_before':original[:,:2].tolist(),'profile_after':result[ids,:2].tolist()})
    return result,stations

def main():
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('landmark',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    raw,j,base=glb(a.source)
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    assert hashlib.sha256(a.landmark.read_bytes()).hexdigest()==LANDMARK_SHA
    node=next(n for n in j['nodes'] if n.get('name')==NODE)
    primitive=j['meshes'][node['mesh']]['primitives'][0]
    v,po=array(raw,j,base,primitive['attributes']['POSITION'])
    normals,no=array(raw,j,base,primitive['attributes']['NORMAL'])
    faces,_=array(raw,j,base,primitive['indices']);faces=faces.reshape(-1,3)
    candidate,stations=fold(v);changed=np.any(v!=candidate,axis=1)
    affected_faces=np.any(changed[faces],axis=1)
    affected_vertices=np.zeros(len(v),dtype=bool);affected_vertices[np.unique(faces[affected_faces])]=True
    tri=candidate[faces].astype('f8');fn=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    normal=np.zeros_like(candidate,dtype='f8')
    for c in range(3):np.add.at(normal,faces[:,c],fn)
    length=np.linalg.norm(normal,axis=1);assert np.all(length>1e-10)
    normal/=length[:,None]
    final_normals=normals.copy();final_normals[affected_vertices]=normal[affected_vertices]
    out=bytearray(raw);out[po:po+candidate.nbytes]=candidate.tobytes();out[no:no+final_normals.nbytes]=final_normals.tobytes()
    allowed=np.zeros(len(raw),dtype=bool);allowed[po:po+v.nbytes]=True;allowed[no:no+normals.nbytes]=True
    bytechange=np.frombuffer(raw,'u1')!=np.frombuffer(out,'u1')
    assert not np.any(bytechange&~allowed)
    protected=np.hypot(v[:,0]-12,v[:,2]+44)<=1.9
    route=np.abs(v[:,0]+3)<=4
    assert np.array_equal(candidate[protected],v[protected])
    assert np.array_equal(candidate[route],v[route])
    assert np.array_equal(candidate[9797:],v[9797:])
    assert np.array_equal(candidate[:,2],v[:,2])
    assert np.array_equal(candidate.min(0),v.min(0)) and np.array_equal(candidate.max(0),v.max(0))
    assert np.all(np.isfinite(candidate)) and np.all(np.isfinite(final_normals))
    area=np.linalg.norm(fn,axis=1)*.5;assert area.min()>1e-8
    directed=np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]])
    edge_sort=np.sort(directed,axis=1);unique,inv,counts=np.unique(edge_sort,axis=0,return_inverse=True,return_counts=True)
    assert np.all(counts==2)
    signs=np.where(directed[:,0]<directed[:,1],1,-1);balance=np.bincount(inv,weights=signs)
    assert np.all(balance==0)
    top_undersides=np.flatnonzero(fn[:19200,1]<-1e-8)
    assert len(top_undersides)>0,'No genuine returning underside was produced'
    assert np.array_equal(fold(v)[0],candidate),'Non-deterministic replay'
    a.output.write_bytes(out)
    np.savez_compressed(a.output.with_suffix('.validation-input.npz'),before=v,after=candidate,faces=faces,changed=changed)
    proof={
      'scope':'Single OFFLINE bounded structural sample. No browser validation, publication or production edits.',
      'units':'interpreted scene units',
      'source_sha256':SOURCE_SHA,'candidate_sha256':hashlib.sha256(out).hexdigest(),'landmark_sha256':LANDMARK_SHA,
      'glb_bytes_before_after':[len(raw),len(out)],
      'all_json_bytes_unchanged':True,'all_non_position_normal_binary_bytes_unchanged':True,
      'all_other_nodes_geometry_materials_images_uvs_colors_indices_transforms_unchanged':True,
      'mesh_vertices_before_after':[len(v),len(candidate)],'mesh_triangles_before_after':[len(faces),len(faces)],
      'vertices_moved':int(changed.sum()),'normals_recalculated':int(affected_vertices.sum()),
      'source_changed_bounds':[v[changed].min(0).tolist(),v[changed].max(0).tolist()],
      'candidate_changed_bounds':[candidate[changed].min(0).tolist(),candidate[changed].max(0).tolist()],
      'max_absolute_displacement_xyz':np.abs(candidate-v).max(0).tolist(),
      'finite_positions_and_normals':True,'normal_length_min_max':[float(np.linalg.norm(final_normals,axis=1).min()),float(np.linalg.norm(final_normals,axis=1).max())],
      'nondegenerate_min_triangle_area':float(area.min()),
      'closed_edge_incidence_min_max':[int(counts.min()),int(counts.max())],
      'consistent_opposite_edge_winding':True,'euler_characteristic':int(len(v)-len(unique)+len(faces)),
      'genuine_downward_facing_former_top_triangles':int(len(top_undersides)),
      'bottom_and_perimeter_unchanged':True,'thicket_support_disk_radius_1_9_unchanged':True,
      'sand_route_x_minus3_plusminus4_unchanged':True,'all_z_coordinates_unchanged':True,
      'deterministic_replay_equal':True,
      'self_intersection_check':'Not evaluated by this preservation-only patcher; run validate_folded_ledge.py and read its separate geometric report.',
      'landmark_clearance_check':'Not evaluated by this preservation-only patcher; run validate_folded_ledge.py and inspect the paired structural renders.',
      'reference':{'page':'https://www.nps.gov/drto/learn/nature/corals.htm','image':'DRTO-DUW-046.jpg','credit':'NPS Submerged Resource Center','use':'Inspected macro irregular exposed skeleton/negative-space hierarchy only. No image texture, species or measured scale claim. JPEG excluded from output.'},
      'stations':stations,
    }
    a.output.with_suffix('.proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k not in ['stations','reference']},indent=2))

if __name__=='__main__':main()
