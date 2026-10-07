"""Independent exact intersection and byte-preservation validator.

Only reads accepted assets and the single candidate. Writes diagnostics beside
this script. Exact predicates use Python integers/Fractions representing the
input IEEE values without epsilon. Landmark world placement is evaluated in
float64 first; intersection predicates then exactly test those world values.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter, defaultdict
import argparse, hashlib, json, math, struct, time
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'coral-3d/source-model.glb'
CANDIDATE = ROOT / 'visible-ledge-candidate.glb'
LANDMARK = ROOT.parent / 'coral-3d/dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb'
NODE = 'Spatial_Continuous_Weathered_Limestone'

def read_glb(path):
    raw = path.read_bytes()
    assert struct.unpack_from('<4sII', raw) == (b'glTF', 2, len(raw))
    chunks = []; cursor = 12
    while cursor < len(raw):
        n, kind = struct.unpack_from('<I4s', raw, cursor)
        chunks.append((kind, cursor + 8, raw[cursor + 8:cursor + 8 + n])); cursor += 8 + n
    assert cursor == len(raw)
    j = json.loads(next(c[2] for c in chunks if c[0] == b'JSON'))
    binary = next(c for c in chunks if c[0] == b'BIN\0')
    return raw, j, binary[1]

def array(raw, j, base, ai):
    a = j['accessors'][ai]; b = j['bufferViews'][a['bufferView']]
    dt = {5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
    cols = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    off = base+b.get('byteOffset',0)+a.get('byteOffset',0)
    assert not a.get('sparse') and not b.get('byteStride')
    return np.frombuffer(raw,dt,a['count']*cols,off).reshape(-1,cols).copy(), off

def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def orient(a,b,p): return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])

def integer_vertices(v):
    ratios = [[float(x).as_integer_ratio() for x in row] for row in v]
    scale = max(d for row in ratios for _,d in row)
    return [tuple(n*(scale//d) for n,d in row) for row in ratios], scale

def cut_axis(tri, distances, axis):
    result = [Q(p[axis]) for p,d in zip(tri, distances) if d == 0]
    for i,j in ((0,1),(1,2),(2,0)):
        if distances[i]*distances[j] < 0:
            result.append(Q(tri[i][axis]*distances[j]-tri[j][axis]*distances[i],distances[j]-distances[i]))
    return min(result), max(result)

def clipped_coplanar(a,b,normal):
    drop = max(range(3), key=lambda i: abs(normal[i])); axes = [i for i in range(3) if i != drop]
    aa = [tuple(Q(p[i]) for i in axes) for p in a]
    bb = [tuple(Q(p[i]) for i in axes) for p in b]
    sign = 1 if orient(*bb) > 0 else -1
    poly = aa
    for i in range(3):
        if not poly: break
        p0,p1 = bb[i],bb[(i+1)%3]; out=[]
        for s,e in zip(poly, poly[1:]+poly[:1]):
            ds,de = sign*orient(p0,p1,s), sign*orient(p0,p1,e)
            if ds >= 0: out.append(s)
            if (ds < 0 and de > 0) or (ds > 0 and de < 0):
                t=ds/(ds-de);out.append(tuple(s[k]+t*(e[k]-s[k]) for k in range(2)))
        poly=out
    return list(dict.fromkeys(poly)), axes

def triangle_intersection(a,b,shared=()):
    """Return None for disjoint/only legal shared simplex, otherwise evidence.

    No adjacency exclusion is used. For noncoplanar triangles the intersection
    is the interval common to their exact plane cuts. For coplanar triangles
    exact convex polygon clipping returns the whole closed intersection set.
    Legal contact is only the mesh's declared common vertex/edge.
    """
    na=cross(sub(a[1],a[0]),sub(a[2],a[0])); nb=cross(sub(b[1],b[0]),sub(b[2],b[0]))
    assert any(na) and any(nb)
    db=[dot(na,sub(p,a[0])) for p in b]
    if min(db)>0 or max(db)<0: return None
    da=[dot(nb,sub(p,b[0])) for p in a]
    if min(da)>0 or max(da)<0: return None
    direction=cross(na,nb)
    if any(direction):
        axis=max(range(3), key=lambda i: abs(direction[i]))
        a0,a1=cut_axis(a,da,axis);b0,b1=cut_axis(b,db,axis)
        lo,hi=max(a0,b0),min(a1,b1)
        if lo>hi:return None
        if shared:
            s=[p[axis] for p in shared]
            if min(s)<=lo and hi<=max(s):return None
        return {'kind':'noncoplanar','axis':axis,'interval':[lo,hi]}
    assert all(d==0 for d in da+db)
    poly,axes=clipped_coplanar(a,b,na)
    if not poly:return None
    if shared:
        s=[tuple(Q(p[i]) for i in axes) for p in shared]
        if len(s)==1 and all(p==s[0] for p in poly): return None
        if len(s)==2 and all(orient(s[0],s[1],p)==0 and all(min(s[0][k],s[1][k])<=p[k]<=max(s[0][k],s[1][k]) for k in range(2)) for p in poly): return None
    return {'kind':'coplanar','axes':axes,'polygon':poly}

def kernel_tests():
    a=((0,0,0),(4,0,0),(0,4,0))
    cases=[
        ('disjoint',((8,8,0),(9,8,0),(8,9,0)),(),False),
        ('coplanar overlap',((1,1,0),(3,1,0),(1,3,0)),(),True),
        ('coplanar shared edge',((4,0,0),(4,4,0),(0,4,0)),(a[1],a[2]),False),
        ('coplanar improper shared edge',((0,0,0),(4,0,0),(1,1,0)),(a[0],a[1]),True),
        ('coplanar shared vertex',((0,0,0),(-3,0,0),(0,-3,0)),(a[0],),False),
        ('coplanar improper shared vertex',((0,0,0),(3,1,0),(1,3,0)),(a[0],),True),
        ('3d crossing',((1,1,-2),(1,1,2),(3,1,0)),(),True),
        ('3d shared vertex',((0,0,0),(-1,-1,-1),(-1,-1,1)),(a[0],),False),
        ('3d improper shared vertex',((0,0,0),(2,2,-1),(2,2,1)),(a[0],),True),
        ('3d shared edge',((0,0,0),(4,0,0),(0,0,3)),(a[0],a[1]),False),
    ]
    for name,b,shared,want in cases:
        assert bool(triangle_intersection(a,b,shared))==want,name
    return [name for name,*_ in cases]

def source_heightfield_proof(v,f):
    top=v[:9797];tf=f[:19200]
    xs=np.unique(top[:,0]);zs=np.unique(top[:,2])
    assert len(xs)==97 and len(zs)==101 and np.all(np.diff(xs)==.5) and np.all(np.diff(zs)==.5)
    assert len(set(map(tuple,top[:,[0,2]])))==len(xs)*len(zs)
    assert np.all(tf<9797)
    cell=defaultdict(list)
    for face in tf:
        coords=[tuple(p) for p in top[face][:,[0,2]]]
        xx=[p[0] for p in coords];zz=[p[1] for p in coords]
        assert max(xx)-min(xx)==.5 and max(zz)-min(zz)==.5
        cell[(min(xx),min(zz))].append(set(coords))
    assert len(cell)==9600
    for key,pair in cell.items():
        assert len(pair)==2 and len(pair[0]|pair[1])==4
        common=list(pair[0]&pair[1]);assert len(common)==2
        assert common[0][0]!=common[1][0] and common[0][1]!=common[1][1]
    bottom=v[9797:];by=bottom[0,1]
    assert np.all(bottom[:,1]==by) and np.all(top[:,1]>by)
    ring=v[9797:10189]; center=v[10189]
    assert len(ring)==392 and center[0]==0 and center[2]==-36
    assert np.all((ring[:,0]==xs[0])|(ring[:,0]==xs[-1])|(ring[:,2]==zs[0])|(ring[:,2]==zs[-1]))
    assert np.all(np.linalg.norm(np.roll(ring,-1,axis=0)-ring,axis=1)==.5)
    assert len(set(map(tuple,ring[:,[0,2]])))==392
    # The ring visits all equally spaced rectangle boundary vertices once;
    # steps are half a unit and every bottom face is one consecutive fan wedge.
    expect_bottom={tuple(sorted((10189,9797+i,9797+(i+1)%392))) for i in range(392)}
    assert set(map(lambda q:tuple(sorted(q)),f[-392:]))==expect_bottom
    side=f[19200:-392];assert len(side)==784
    top_by_xz={tuple(p[[0,2]]):i for i,p in enumerate(top)}
    for i in range(392):
        j=(i+1)%392; ids={9797+i,9797+j,top_by_xz[tuple(ring[i,[0,2]])],top_by_xz[tuple(ring[j,[0,2]])]}
        matches=[set(q) for q in side if set(q)<=ids]
        assert len(matches)==2 and len(matches[0]|matches[1])==4
        diagonal=matches[0]&matches[1]
        assert diagonal in ({9797+i,top_by_xz[tuple(ring[j,[0,2]])]},{9797+j,top_by_xz[tuple(ring[i,[0,2]])]})
    return {'regular_top_cells':len(cell),'top_triangles':len(tf),'side_triangles':len(side),'bottom_triangles':392,'minimum_top_above_bottom':float(top[:,1].min()-by),'proof':'Regular cell triangulation is a single-valued heightfield strictly above flat base; vertical boundary quads and an interior-centered rectangle fan close it without improper intersections.'}

def broad_pairs(v,f,selected):
    tri=v[f];lo=tri.min(1);hi=tri.max(1);selected_set=set(map(int,selected))
    for i in selected:
        hit=np.flatnonzero(np.all(lo<=hi[i],axis=1)&np.all(hi>=lo[i],axis=1))
        for j in hit:
            if i==j or (j in selected_set and j<i):continue
            yield int(i),int(j)

def terrain_check(v,f,changed):
    iv,scale=integer_vertices(v);chosen=np.flatnonzero(np.any(changed[f],axis=1))
    problems=[];count=0;adjacent=Counter()
    for i,j in broad_pairs(v,f,chosen):
        common=set(map(int,f[i]))&set(map(int,f[j]));adjacent[len(common)]+=1
        a=[iv[k] for k in f[i]];b=[iv[k] for k in f[j]]
        result=triangle_intersection(a,b,[iv[k] for k in common]);count+=1
        if result:
            evidence={'faces':[i,j],'shared_vertices':sorted(common),'kind':result['kind'],'triangle_a':v[f[i]].tolist(),'triangle_b':v[f[j]].tolist()}
            evidence['intersection_points']=intersection_points(a,b,result,scale)
            if result['kind']=='noncoplanar':evidence.update(axis=result['axis'],interval=[float(x/scale) for x in result['interval']])
            else:evidence.update(axes=result['axes'],polygon=[[float(x/scale) for x in p] for p in result['polygon']])
            problems.append(evidence)
    pts=np.concatenate([x['intersection_points'] for x in problems]) if problems else None
    return {'affected_faces':len(chosen),'aabb_candidate_pairs':count,'pairs_by_shared_vertex_count':dict(adjacent),'exact_integer_scale':str(scale),'improper_intersections':len(problems),
            'nonzero_intersection_segments':sum(x.get('interval',[0,0])[0]!=x.get('interval',[0,0])[1] for x in problems),
            'shared_vertex_improper_pairs':sum(bool(x['shared_vertices']) for x in problems),
            'intersection_bounds':None if pts is None else [pts.min(0).tolist(),pts.max(0).tolist()],
            'intersection_details':problems,'method':'Exhaustive AABB broad phase for every changed face against every closed terrain face; exact integer plane tests and Fraction plane cuts / convex coplanar clipping. Shared simplices are checked, never wholesale excluded. Unchanged pairs inherit the independently verified source heightfield proof.'}

def intersection_points(a,b,result,scale):
    if result['kind']=='coplanar':
        axes=result['axes'];drop=next(i for i in range(3) if i not in axes)
        normal=cross(sub(a[1],a[0]),sub(a[2],a[0]));constant=dot(normal,a[0]);out=[]
        for q in result['polygon']:
            p=[Q(0)]*3
            for k,x in zip(axes,q):p[k]=x
            p[drop]=(constant-sum(normal[k]*p[k] for k in axes))/normal[drop]
            out.append([float(x/scale) for x in p])
        return out
    k=result['axis'];i,j=[x for x in range(3) if x!=k]
    na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]))
    ca,cb=dot(na,a[0]),dot(nb,b[0]);det=na[i]*nb[j]-na[j]*nb[i];out=[]
    for t in result['interval']:
        va,vb=ca-na[k]*t,cb-nb[k]*t;p=[Q(0)]*3;p[k]=t
        p[i]=(va*nb[j]-na[j]*vb)/det;p[j]=(na[i]*vb-va*nb[i])/det
        out.append([float(x/scale) for x in p])
    return out

def face_metrics(v,f):
    tri=v[f].astype(float);e=np.stack([tri[:,1]-tri[:,0],tri[:,2]-tri[:,1],tri[:,0]-tri[:,2]],axis=1)
    length=np.linalg.norm(e,axis=2);area=np.linalg.norm(np.cross(e[:,0],-e[:,2]),axis=1)/2
    # Equilateral normalized longest-edge / corresponding altitude.
    aspect=np.sqrt(3)*length.max(1)**2/(4*area)
    return {'edge_lengths_min_median_p95_max':[float(x) for x in np.quantile(length,[0,.5,.95,1])],
            'triangle_area_min_median_p95_max':[float(x) for x in np.quantile(area,[0,.5,.95,1])],
            'aspect_equilateral_1_min_median_p95_max':[float(x) for x in np.quantile(aspect,[0,.5,.95,1])]}

def landmark_meshes():
    raw,j,base=read_glb(LANDMARK);c,s=math.cos(1.3),math.sin(1.3)
    rotation=np.array([[c,0,s],[0,1,0],[-s,0,c]]);position=np.array([3.5,-.015196346640586854,-44])
    out=[]
    for node in j['nodes']:
        if node['name']=='Attached_reticulate_fan_form':continue
        assert set(node)<= {'name','mesh'}
        for prim in j['meshes'][node['mesh']]['primitives']:
            v,_=array(raw,j,base,prim['attributes']['POSITION']);f,_=array(raw,j,base,prim['indices'])
            out.append((node['name'],v.astype(float)@rotation.T+position,f.reshape(-1,3)))
    return out

def landmark_contacts(v,f,changed,landmarks):
    t=v[f];tlo,thi=t.min(1),t.max(1);affected=np.any(changed[f],axis=1);summaries=[]
    for name,lv,lf in landmarks:
        allv,scale=integer_vertices(np.concatenate([v,lv]));iv=allv[:len(v)];il=allv[len(v):]
        lt=lv[lf];llo,lhi=lt.min(1),lt.max(1);selected=np.flatnonzero(np.all(tlo<=lv.max(0),axis=1)&np.all(thi>=lv.min(0),axis=1))
        intersections=[];broad_count=0
        for i in selected:
            hits=np.flatnonzero(np.all(llo<=thi[i],axis=1)&np.all(lhi>=tlo[i],axis=1))
            for j in hits:
                a=[iv[k] for k in f[i]];b=[il[k] for k in lf[j]];broad_count+=1
                result=triangle_intersection(a,b)
                if result:intersections.append({'terrain_face':int(i),'landmark_face':int(j),'affected_terrain_face':bool(affected[i]),'points':intersection_points(a,b,result,scale)})
        changed_hits=[x for x in intersections if x['affected_terrain_face']]
        def bounds(rows):
            if not rows:return None
            p=np.concatenate([x['points'] for x in rows]);return [p.min(0).tolist(),p.max(0).tolist()]
        summaries.append({'node':name,'vertices':len(lv),'triangles':len(lf),'world_bounds':[lv.min(0).tolist(),lv.max(0).tolist()],
                          'aabb_candidate_pairs':broad_count,'surface_intersection_pairs':len(intersections),'affected_surface_intersection_pairs':len(changed_hits),
                          'all_contact_bounds':bounds(intersections),'changed_region_contact_bounds':bounds(changed_hits),'contacts':intersections})
    return summaries

def section_segments(v,f,z):
    tri=v[f].astype(float);lo,hi=tri[:,:,2].min(1),tri[:,:,2].max(1);out=[]
    for t in tri[(lo<=z)&(hi>=z)]:
        pts=[]
        for i,j in ((0,1),(1,2),(2,0)):
            a,b=t[i],t[j]
            if a[2]==z:pts.append(a[:2])
            if (a[2]<z<b[2]) or (b[2]<z<a[2]):pts.append(a[:2]+(b[:2]-a[:2])*((z-a[2])/(b[2]-a[2])))
        if not pts:continue
        pts=np.unique(pts,axis=0)
        if len(pts)>=2:
            if len(pts)>2:
                delta=pts[:,None,:]-pts[None,:,:];i,j=np.unravel_index(np.argmax(np.sum(delta**2,axis=2)),delta.shape[:2]);pts=pts[[i,j]]
            out.append(pts)
    return np.array(out)

def segment_distances(a,b):
    a=np.asarray(a);b=np.asarray(b);p=a[:,None,0,:];r=a[:,None,1,:]-p;q=b[None,:,0,:];s=b[None,:,1,:]-q
    def cross2(x,y):return x[...,0]*y[...,1]-x[...,1]*y[...,0]
    den=cross2(r,s)
    with np.errstate(divide='ignore',invalid='ignore'):
        t=cross2(q-p,s)/den;u=cross2(q-p,r)/den
    crossing=(den!=0)&(t>=0)&(t<=1)&(u>=0)&(u<=1)
    def point_to_segment(p,q,s):
        t=np.clip(np.sum((p-q)*s,axis=-1)/np.sum(s*s,axis=-1),0,1)
        return np.linalg.norm(p-(q+t[...,None]*s),axis=-1)
    dist=np.minimum.reduce([point_to_segment(p,q,s),point_to_segment(p+r,q,s),point_to_segment(q,p,r),point_to_segment(q+s,p,r)])
    dist[crossing]=0;return dist

def section_diagnostics(v,v2,f,changed,landmarks):
    name,lv,lf=landmarks[0];affected=f[np.any(changed[f],axis=1)];rows=[]
    for z in [-46,-45.5,-45.25,-45,-44.75,-44.5,-44.25,-44,-43.75,-43.5]:
        l=section_segments(lv,lf,z);before=section_segments(v,affected,z);after=section_segments(v2,affected,z)
        if not len(l) or not len(after):continue
        rows.append({'z':z,'landmark_x_range':[float(l[:,:,0].min()),float(l[:,:,0].max())],
                     'candidate_changed_surface_min_x':float(after[:,:,0].min()),'horizontal_separation_lower_bound':float(after[:,:,0].min()-l[:,:,0].max()),
                     'minimum_2d_surface_gap_before':float(segment_distances(before,l).min()),'minimum_2d_surface_gap_after':float(segment_distances(after,l).min())})
    return {'method':'Fixed Z cross-sections, Euclidean segment distance; negative X separation bound only indicates overlapping X ranges, while zero segment distance indicates actual surface contact. Sampling diagnoses clearance and does not replace the exhaustive exact triangle contact test. This cannot certify visual cavity visibility or view-ray occlusion.','rows':rows}

def main():
    global SOURCE,CANDIDATE,LANDMARK
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('candidate',type=Path)
    parser.add_argument('landmark',type=Path)
    parser.add_argument('output',type=Path,help='JSON output; a human-readable .txt sibling is also written')
    parser.add_argument('--validation-npz',type=Path,help='Optional cross-check only; actual GLB bytes are authoritative')
    args=parser.parse_args()
    SOURCE,CANDIDATE,LANDMARK=args.source,args.candidate,args.landmark
    t=time.time();report={'scope':'Independent OFFLINE geometric diagnostics; no candidate mutation, browser validation, publication or asset acceptance.'}
    report['intersection_kernel_test_cases']=kernel_tests()
    raw,j,base=read_glb(SOURCE);out,j2,base2=read_glb(CANDIDATE)
    report['hashes']={key:hashlib.sha256(p.read_bytes()).hexdigest() for key,p in [('source_glb',SOURCE),('candidate_glb',CANDIDATE),('landmark_glb',LANDMARK)]}
    assert report['hashes']['source_glb']=='c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd'
    assert report['hashes']['candidate_glb']=='9e0cb3f417905582b7947e5fc4e239dbd6596e3bea6905921c177903356e4239','This report is for the fixed rejected candidate only'
    assert report['hashes']['landmark_glb']=='d6377e6bcfc5145ef6da7c139de26772b6065b30fbe24c2d3180bcba9ae48cdf'
    ni=next(i for i,n in enumerate(j['nodes']) if n.get('name')==NODE)
    node=j['nodes'][ni];assert set(node)=={'name','mesh'}
    assert all(ni not in n.get('children',[]) for n in j['nodes'])
    prim=j['meshes'][node['mesh']]['primitives'][0]
    v,po=array(raw,j,base,prim['attributes']['POSITION']);n,no=array(raw,j,base,prim['attributes']['NORMAL']);f,_=array(raw,j,base,prim['indices']);f=f.reshape(-1,3)
    v2,po2=array(out,j2,base2,prim['attributes']['POSITION']);n2,no2=array(out,j2,base2,prim['attributes']['NORMAL'])
    assert len(raw)==len(out) and base==base2 and po==po2 and no==no2
    assert raw[:base]==out[:base] and j==j2
    diff=np.frombuffer(raw,'u1')!=np.frombuffer(out,'u1');allow=np.zeros(len(raw),bool);allow[po:po+v.nbytes]=True;allow[no:no+n.nbytes]=True
    assert not np.any(diff&~allow)
    target_accessors={prim['attributes']['POSITION'],prim['attributes']['NORMAL']}
    for mi,mesh in enumerate(j['meshes']):
        for primitive in mesh['primitives']:
            if mi!=node['mesh']:assert not target_accessors.intersection(primitive['attributes'].values())
    for ai,a in enumerate(j['accessors']):
        if ai in target_accessors:continue
        if a.get('bufferView') is None:continue
        b=j['bufferViews'][a['bufferView']];aoff=base+b.get('byteOffset',0)+a.get('byteOffset',0)
        size={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT2':4,'MAT3':9,'MAT4':16}[a['type']]
        end=aoff+(a['count']-1)*b.get('byteStride',size)+size
        assert not np.any(diff[aoff:end]),('aliased changed accessor',ai)
    changed=np.any(v!=v2,axis=1);normchanged=np.any(n!=n2,axis=1)
    if args.validation_npz:
        bundle=np.load(args.validation_npz)
        for k,values in [('before',v),('after',v2),('faces',f),('changed',changed)]:assert np.array_equal(bundle[k],values),k
    protected=np.hypot(v[:,0]-12,v[:,2]+44)<=1.9;route=np.abs(v[:,0]+3)<=4
    assert np.array_equal(v[protected],v2[protected]) and np.array_equal(v[route],v2[route]) and np.array_equal(v[9797:],v2[9797:]) and np.array_equal(v[:,2],v2[:,2])
    perimeter=(v[:9797,0]==-24)|(v[:9797,0]==24)|(v[:9797,2]==-61)|(v[:9797,2]==-11)
    assert np.array_equal(v[:9797][perimeter],v2[:9797][perimeter])
    directed=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);edges,inv,counts=np.unique(np.sort(directed,axis=1),axis=0,return_inverse=True,return_counts=True)
    assert np.all(counts==2) and np.all(np.bincount(inv,weights=np.where(directed[:,0]<directed[:,1],1,-1))==0)
    tri=v2[f].astype(float);fn=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(fn,axis=1)/2
    assert area.min()>0 and np.all(np.isfinite(v2)) and np.all(np.isfinite(n2))
    report['preservation']={'all_json_header_and_non_position_normal_bytes_identical':True,'other_accessor_bytes_identical_and_target_accessors_not_reused_by_other_meshes':True,'changed_binary_bytes':int(diff.sum()),'moved_vertices':int(changed.sum()),'changed_normals':int(normchanged.sum()),'vertices':len(v),'triangles':len(f),'topology_unchanged':True,'all_z_identical':True,'perimeter_and_bottom_identical':True,'thicket_disk_center':[12,-44],'thicket_disk_radius':1.9,'thicket_vertices_identical':int(protected.sum()),'sand_route_x_range':[-7,1],'sand_route_vertices_identical':int(route.sum()),'finite':True,'minimum_triangle_area':float(area.min()),'closed_opposite_edge_winding':True,'euler_characteristic':int(len(v)-len(edges)+len(f)),'downward_former_top_triangles':int((fn[:19200,1]<0).sum()),'validation_npz_matches_actual_glbs':True if args.validation_npz else 'not requested; actual GLB arrays tested directly'}
    report['source_simple_surface_proof']=source_heightfield_proof(v,f)
    report['terrain_exact_intersection_check']=terrain_check(v2,f,changed)
    selected=np.any(changed[f],axis=1)
    report['changed_face_metrics']={'aspect_definition':'sqrt(3) * longest_edge^2 / (4 * area), equilateral = 1',
                                  'before':face_metrics(v,f[selected]),'after':face_metrics(v2,f[selected]),
                                  'maximum_corresponding_edge_stretch_factor':float((np.linalg.norm(np.diff(v2[f[selected]][:,[0,1,2,0]].astype(float),axis=1),axis=2)/np.linalg.norm(np.diff(v[f[selected]][:,[0,1,2,0]].astype(float),axis=1),axis=2)).max()),
                                  'side_and_bottom_faces_identical':bool(np.array_equal(v[f[19200:]],v2[f[19200:]])),
                                  'interpretation':'Existing interior top-grid triangles are redistributed and stretched. No perimeter or bottom vertex/face was pulled into a skirt.'}
    landmark=landmark_meshes()
    report['landmark_pose']={'position':[3.5,-.015196346640586854,-44],'yaw':1.3,'axis_convention':'glTF Y up','omitted':'Attached_reticulate_fan_form','retained':'Attached_small_fan_form'}
    report['landmark_contact_before']=landmark_contacts(v,f,changed,landmark)
    report['landmark_contact_after']=landmark_contacts(v2,f,changed,landmark)
    baseline_contacts={(x['node'],c['terrain_face'],c['landmark_face']) for x in report['landmark_contact_before'] for c in x['contacts']}
    candidate_contacts={(x['node'],c['terrain_face'],c['landmark_face']) for x in report['landmark_contact_after'] for c in x['contacts']}
    report['landmark_contact_comparison']={'preexisting_contact_pairs_retained':len(baseline_contacts&candidate_contacts),'preexisting_contact_pairs_removed':len(baseline_contacts-candidate_contacts),'new_contact_pairs':len(candidate_contacts-baseline_contacts)}
    report['landmark_section_clearance']=section_diagnostics(v,v2,f,changed,landmark)
    report['verdict']={'candidate_status':'rejected','geometric_failure':'12 improper terrain triangle-pair intersections, including 8 nonzero crossing segments','preservation_status':'passed','visual_acceptance':'not claimed; parent-owned paired camera review'}
    report['elapsed_seconds']=time.time()-t
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    failures=report['terrain_exact_intersection_check'];m=report['changed_face_metrics'];contacts=report['landmark_contact_after'][0];sections=report['landmark_section_clearance']['rows']
    cave=next(x for x in sections if x['z']==-45)
    lines=[
        'REJECTED OFFLINE CANDIDATE: INDEPENDENT VALIDATION',
        'Candidate SHA-256: '+report['hashes']['candidate_glb'],
        '',
        'FAIL: The candidate is not an embedded, intersection-free terrain surface.',
        f"Exact arithmetic found {failures['improper_intersections']} improper triangle pairs: {failures['nonzero_intersection_segments']} nonzero crossing segments plus 4 isolated boundary contacts. Two pairs share a mesh vertex but intersect beyond that allowed vertex. These are real geometry crossings, not the intentional 116 downward-facing former top triangles.",
        'Intersection bounds XYZ: '+json.dumps(failures['intersection_bounds']),
        'Intersecting terrain triangle pairs (zero-based): '+', '.join(str(x['faces']) for x in failures['intersection_details']),
        '',
        'PASS: Exact preservation. 220 positions and 286 normals differ; 4,226 bytes differ, all inside the target terrain POSITION/NORMAL accessors. All JSON, remaining accessors, indices, materials, images, attributes, nodes and transforms remain byte-identical. Actual GLB bytes are authoritative; the NPZ is an optional cross-check only.',
        'Mesh retains 10,190 vertices and 20,376 triangles, closed opposite edge winding, Euler characteristic 2, finite values and nonzero triangle areas. Every Z value, 45 thicket-disk vertices (center 12,-44; radius 1.9), 1,752 sand-route vertices (X -7 to 1), perimeter and base are unchanged. Closed/manifold combinatorics alone does not imply an intersection-free embedding.',
        '',
        'LANDMARK: Both fixed-pose assets are hash-verified; large reticulate fan omitted and small fan retained. All 343 existing basal contact pairs remain, at Y approximately -0.370 to -0.309. The candidate adds 35 upper rear shoulder-contact pairs within XYZ '+json.dumps(contacts['changed_region_contact_bounds'])+'. The retained small fan has no terrain contacts before or after.',
        f"The Z=-45 cavity-adjacent section retains a {cave['minimum_2d_surface_gap_after']:.6f} scene-unit surface gap (before {cave['minimum_2d_surface_gap_before']:.6f}). No new surface intersection occurs near that section; all new contact is within Z -44.611 to -44.287. This distinguishes rear contact from geometric intrusion at Z=-45. It does not certify view-ray cavity visibility, shadow quality, or intentional contact semantics; use the paired fixed-camera images for those judgments.",
        '',
        'FACE REDISTRIBUTION: 504 existing interior top-grid faces are affected. Longest affected edge changes from '+f"{m['before']['edge_lengths_min_median_p95_max'][-1]:.6f} to {m['after']['edge_lengths_min_median_p95_max'][-1]:.6f}; maximum corresponding edge stretch is {m['maximum_corresponding_edge_stretch_factor']:.6f}x. Normalized aspect ratio (equilateral=1) median / 95th / worst changes from "+str(m['before']['aspect_equilateral_1_min_median_p95_max'][1:])+' to '+str(m['after']['aspect_equilateral_1_min_median_p95_max'][1:])+'. All perimeter/side and base faces are identical: stretching comes from redistribution of existing top faces, not a pulled vertical skirt.',
        '',
        'METHOD: Source nonintersection is proved from a regular 9,600-cell heightfield strictly above a flat base, vertical rectangle perimeter quads, and an interior-centered base fan. Candidate unchanged face pairs inherit that proof. Every changed face is tested against all terrain faces using exhaustive bounding boxes (4,383 possible pairs) then exact Python integer/Fraction plane cuts or convex coplanar clipping. Declared shared vertices/edges are verified rather than excluded. Ten adversarial kernel cases include coplanar and noncoplanar improper shared-simplex intersections.',
        'Landmark contacts use exhaustive terrain/landmark AABB pairs and the same exact predicates after the specified float64 rigid world transform. Fixed-Z clearance values are numerical section diagnostics, not exhaustive minimum 3D clearances.',
        '',
        'REPRODUCE: python validate_folded_ledge.py <source.glb> <candidate.glb> <landmark.glb> <output.json>',
        'REQUIRES: Python 3 and NumPy; no Blender, SciPy or source-side validation arrays are needed.',
        'OUTPUTS: <output.json> (full contact and crossing witnesses) and <output.txt> (this report). An optional --validation-npz <input.npz> checks saved arrays against authoritative GLB bytes.',
        'ARCHIVE WHITELIST FOR THIS DIAGNOSTIC: validate_folded_ledge.py; visible-ledge-independent-validation.json; visible-ledge-independent-validation.txt. Candidate/proof/NPZ and fixed grey images are parent-owned evidence. No production asset, candidate shape, browser, deployment or external state was changed.',
    ]
    args.output.with_suffix('.txt').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:r for k,r in report.items() if k not in ['terrain_exact_intersection_check','landmark_contact_before','landmark_contact_after']},indent=2),flush=True)
    print('TERRAIN:',json.dumps({k:r for k,r in report['terrain_exact_intersection_check'].items() if k!='intersection_details'}),flush=True)
    for label in ['landmark_contact_before','landmark_contact_after']:
        print(label,json.dumps([{k:v for k,v in row.items() if k!='contacts'} for row in report[label]]),flush=True)

if __name__=='__main__':main()
