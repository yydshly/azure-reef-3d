"""One original bounded topology-preserving grey experiment, 7 Oct 2026.

Coordinates and heights are interpreted scene units, never survey measurements.
No photo texture, purchased asset, new biological form, or new triangles.
The existing closed heightfield permits open incisions and shelves, not undercuts,
arches or the through-holes visible in the NPS photographic reference.
"""
import argparse, hashlib, json, struct
from pathlib import Path
import numpy as np

SOURCE_SHA = 'c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd'
LANDMARK_SHA = 'd6377e6bcfc5145ef6da7c139de26772b6065b30fbe24c2d3180bcba9ae48cdf'

def smooth(x):
    x = np.clip(x, 0, 1)
    return x*x*(3-2*x)

def glb(path):
    raw = path.read_bytes()
    length = struct.unpack_from('<I', raw, 12)[0]
    return raw, json.loads(raw[20:20+length]), 28+length

def array(raw, j, base, idx):
    a = j['accessors'][idx]
    view = j['bufferViews'][a['bufferView']]
    components = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
    dtype = {5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
    offset = base + view.get('byteOffset', 0) + a.get('byteOffset', 0)
    assert not view.get('byteStride')
    v = np.frombuffer(raw, dtype=dtype, count=a['count']*components, offset=offset)
    return v.reshape(a['count'],components).copy(), offset

def path_distance(x, z, points):
    """Distance and interpolated scalar along a hand-authored sinuous incision."""
    best = np.full_like(x, 1e10)
    amount = np.zeros_like(x)
    for a,b in zip(points, points[1:]):
        ax,az,ah=a; bx,bz,bh=b
        t=np.clip(((x-ax)*(bx-ax)+(z-az)*(bz-az))/((bx-ax)**2+(bz-az)**2),0,1)
        d=np.hypot(x-(ax+t*(bx-ax)),z-(az+t*(bz-az)))
        chosen=d<best
        best=np.where(chosen,d,best)
        amount=np.where(chosen,ah+(bh-ah)*t,amount)
    return best, amount

def polygon_distance(x,z,vertices):
    inside = np.zeros(x.shape, dtype=bool)
    dist = np.full_like(x, 1e10)
    for a,b in zip(vertices, vertices[1:]+vertices[:1]):
        ax,az=a;bx,bz=b
        crossing=((az>z)!=(bz>z)) & (x < (bx-ax)*(z-az)/(bz-az+1e-20)+ax)
        inside ^= crossing
        t=np.clip(((x-ax)*(bx-ax)+(z-az)*(bz-az))/((bx-ax)**2+(bz-az)**2),0,1)
        dist=np.minimum(dist,np.hypot(x-(ax+t*(bx-ax)),z-(az+t*(bz-az))))
    return np.where(inside,dist,-dist)

def sculpt(v):
    x,y,z = v.T.astype('f8')
    # The first affected column is x=4.5. x=4.0 is a zero-change seam.
    # This meets the fixed landmark only at its low rear toe near z=-43.5;
    # its conspicuous high recess near z=-45 remains open and unchanged.
    bound=smooth((x-4.0)/.65)*smooth((17.0-x)/.9)*smooth((z+49)/.8)*smooth((-38-z)/.8)
    protect=smooth((np.hypot(x-12,z+44)-1.9)/.55)
    mask=bound*protect*(np.arange(len(v))<97*101)
    h=y.copy()

    # Deep broad negative spaces run into the bank from different directions.
    # They are asymmetric branching troughs, not extra positive rounded lobes.
    incisions=[
        ([(5.4,-41.7,.35),(7.1,-41.5,.85),(8.9,-41.0,1.15),(11.2,-40.5,1.20),(13.4,-39.6,.95),(16.2,-39.0,.45)], .90),
        ([(5.7,-46.8,.30),(7.5,-46.5,.90),(9.0,-46.1,1.45),(10.2,-46.9,1.40),(12.3,-47.2,1.55),(14.6,-47.8,1.25),(16.5,-47.7,.45)], .72),
        ([(17.0,-41.7,.55),(15.5,-42.1,1.35),(14.2,-41.9,1.30),(13.6,-41.0,.90)], .65),
    ]
    for points,width in incisions:
        d,depth=path_distance(x,z,points)
        cut=(1-smooth((d-.17)/width))*depth
        h-=cut
    h=np.maximum(h,-.30)

    # A bent, sloping exposed spur reaches the fixed landmark's low rear toe.
    # Unequal planform corners and an inclined crest avoid a constant platform.
    spur=[(4.1,-43.1),(5.3,-42.9),(6.4,-43.2),(7.8,-42.8),
          (8.8,-43.2),(10.4,-44.0),(10.7,-44.8),(9.8,-45.4),
          (8.6,-44.7),(7.4,-45.0),(6.1,-44.3),(4.3,-44.0)]
    d=polygon_distance(x,z,spur)
    crest=-.02+.29*(x-4.5)+.10*np.sin((x-4.5)*1.9)+.08*np.sin((z+44)*2.2)
    crest=np.minimum(crest,1.95)
    slope=smooth((d+.46)/.85)
    raised=h+(np.maximum(h,crest)-h)*slope
    h=np.maximum(h,raised)

    # Two different high/low edge steps are carved into the remaining bank.
    # These broad cuts interrupt the mound silhouette behind the connector.
    backcut=[(12.8,-38.3),(14.9,-38.7),(16.5,-39.5),(16.3,-40.3),
             (15.0,-40.1),(14.3,-40.8),(12.7,-40.2)]
    sd=polygon_distance(x,z,backcut)
    h-=(1.02+.12*np.sin(x*1.1))*smooth((sd+.5)/.9)
    # A diagonal recess across the connector's inner shoulder introduces a
    # second height interval while remaining safely outside the support disk.
    d,depth=path_distance(x,z,[(6.3,-44.8,.35),(7.2,-44.5,.35),(8.3,-44.7,.26)])
    h-=depth*(1-smooth(d/.64))
    h=np.maximum(h,-.30)
    out=v.copy()
    out[:,1]=(y+(h-y)*mask).astype('<f4')
    return out, mask

def main():
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('landmark',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    raw,j,base=glb(a.source)
    assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    assert hashlib.sha256(a.landmark.read_bytes()).hexdigest()==LANDMARK_SHA
    node=next(n for n in j['nodes'] if n.get('name')=='Spatial_Continuous_Weathered_Limestone')
    primitive=j['meshes'][node['mesh']]['primitives'][0]
    v,po=array(raw,j,base,primitive['attributes']['POSITION'])
    old_normals,no=array(raw,j,base,primitive['attributes']['NORMAL'])
    faces,_=array(raw,j,base,primitive['indices']);faces=faces.reshape(-1,3)
    candidate,mask=sculpt(v)
    changed=np.any(v!=candidate,axis=1)
    affected_faces=np.any(changed[faces],axis=1)
    affected_vertices=np.zeros(len(v),dtype=bool);affected_vertices[np.unique(faces[affected_faces])]=True
    tri=candidate[faces]
    fn=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    normal=np.zeros_like(candidate)
    for i in range(3):np.add.at(normal,faces[:,i],fn)
    norm=np.linalg.norm(normal,axis=1)
    assert np.all(norm>1e-10)
    normal/=norm[:,None]
    final_normals=old_normals.copy();final_normals[affected_vertices]=normal[affected_vertices]
    out=bytearray(raw)
    out[po:po+candidate.nbytes]=candidate.tobytes()
    out[no:no+final_normals.nbytes]=final_normals.tobytes()
    # The new maximum never exceeds the existing thicket support height, so
    # even accessor bounds and every JSON byte remain exactly unchanged.
    assert np.all(candidate.min(0)==v.min(0)) and np.all(candidate.max(0)==v.max(0))
    for lo,hi in [(0,min(po,no)),(min(po+v.nbytes,no+old_normals.nbytes),max(po,no)),(max(po+v.nbytes,no+old_normals.nbytes),len(raw))]:
        assert out[lo:hi]==raw[lo:hi]
    protected=np.hypot(v[:,0]-12,v[:,2]+44)<=1.9
    sand=np.abs(v[:,0]+3)<=4
    assert np.array_equal(candidate[protected],v[protected])
    assert np.array_equal(candidate[sand],v[sand])
    assert np.array_equal(candidate[9797:],v[9797:])
    assert np.all(np.isfinite(candidate)) and np.all(np.isfinite(final_normals))
    area=np.linalg.norm(fn,axis=1)*.5
    assert area.min()>1e-8
    assert np.all(fn[:19200,1]>0)
    edges=np.sort(np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]),axis=1)
    _,counts=np.unique(edges,axis=0,return_counts=True);assert np.all(counts==2)
    allowed=np.zeros(len(raw),dtype=bool);allowed[po:po+v.nbytes]=True;allowed[no:no+old_normals.nbytes]=True
    bytechange=np.frombuffer(raw,'u1')!=np.frombuffer(out,'u1')
    assert not np.any(bytechange&~allowed)
    samples=[]
    for x,z in [(4.5,-43.5),(5,-43.5),(6,-43.5),(7.5,-44),(9,-44.5),(9,-46),(10,-46.5),(12,-44),(14,-42),(15,-42),(14,-47.5)]:
        k=np.argmin((v[:9797,0]-x)**2+(v[:9797,2]-z)**2)
        samples.append({'x':float(v[k,0]),'z':float(v[k,2]),'before_y':float(v[k,1]),'after_y':float(candidate[k,1])})
    proof={
        'scope':'OFFLINE original bounded late-bank morphology experiment; not published, not runtime validation',
        'units':'interpreted scene units, not measured metres or a surveyed habitat',
        'source_sha256':SOURCE_SHA,'candidate_sha256':hashlib.sha256(out).hexdigest(),
        'landmark_sha256':LANDMARK_SHA,'glb_bytes_before_after':[len(raw),len(out)],
        'all_json_bytes_unchanged':True,'all_non_position_normal_binary_bytes_unchanged':True,
        'all_nodes_materials_images_uv_colors_indices_transforms_unchanged':True,
        'changed_node':'Spatial_Continuous_Weathered_Limestone',
        'mesh_vertices_before_after':[len(v),len(candidate)],'mesh_triangles_before_after':[len(faces),len(faces)],
        'vertices_moved':int(changed.sum()),'normals_recalculated':int(affected_vertices.sum()),
        'moved_xyz_bounds':[candidate[changed].min(0).tolist(),candidate[changed].max(0).tolist()],
        'height_delta_min_max':[float((candidate-v)[:,1].min()),float((candidate-v)[:,1].max())],
        'closed_manifold_edge_incidence_min_max':[int(counts.min()),int(counts.max())],
        'min_triangle_area':float(area.min()),'finite_positions_and_normals':True,
        'normal_length_min_max':[float(np.linalg.norm(final_normals,axis=1).min()),float(np.linalg.norm(final_normals,axis=1).max())],
        'top_faces_upward':True,'bottom_and_perimeter_unchanged':True,
        'thicket_support_disk_radius_1_9_unchanged':True,'sand_route_x_minus3_plusminus4_unchanged':True,
        'height_samples':samples,
        'limit':'Single closed heightfield. Open gullies, inclined spurs and uneven ledges are possible; overhangs, through-cavities and exact NPS reference reconstruction are not. Coarse 0.5 scene-unit sampling limits sharp fracture relief. No landmark vertex or pose is edited.',
        'reference':{'page':'https://www.nps.gov/drto/learn/nature/corals.htm','image':'DRTO-DUW-046.jpg','credit':'NPS Submerged Resource Center','use':'Viewed pixels for macro irregular exposed skeleton and recess hierarchy only. No photo as texture; no habitat, species or survey fidelity claim.'},
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(out)
    a.output.with_suffix('.proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof,indent=2))

if __name__=='__main__':main()
