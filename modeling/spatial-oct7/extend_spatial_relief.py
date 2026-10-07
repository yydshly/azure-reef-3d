"""Append bounded, closed limestone relief to the accepted reef without editing it.

Portable deterministic recipe: Python 3 and NumPy. Coordinates are glTF / runtime
Y-up metres. Interpretive composition, not a measured Caribbean survey.
"""
import argparse, copy, hashlib, json, math, struct
from pathlib import Path
import numpy as np

SOURCE_SHA = 'a5d9412ede847ba165f1198967b487dd3787e3f71e5e25ed30831f40a7ac5a0b'
ROUTE = [
    {'id':'start','position':[1.5,2.1,4.8],'target':[-.5,.8,-6]},
    {'id':'mid','position':[0,2.7,-18],'target':[-1.5,1,-31]},
    {'id':'open','position':[-3.8,3.6,-36],'target':[0,1.2,-50]},
    {'id':'look-back','position':[-3.8,3.6,-36],'target':[0,.9,-8]},
]
WAYPOINTS = [[1.5,2.1,4.8],[.2,2.4,-8],[0,2.7,-18],[-1.5,3.1,-27],[-3.8,3.6,-36]]
# Irregular elongated shelves form two asymmetric interrupted reef margins.
# Dimensions, heights and azimuths differ; no ring placement or copied rocks.
LOBES = [
    (-11.4,-20.5,4.9,8.0,.82,.18),
    (-10.5,-32.0,5.3,8.8,1.72,-.32),
    (-17.0,-42.5,4.5,8.1,1.28,-.52),
    (10.1,-27.5,6.0,8.0,1.12,.42),
    (12.6,-43.0,5.7,10.0,2.32,-.27),
    (-1.1,-53.5,10.2,4.8,1.33,.22),
    (-18.1,-29.0,3.1,6.0,.47,.73),
    (20.0,-33.5,2.4,5.0,.56,-.32),
]
# Four source-mesh occurrences, with different shape, orientation and scale.
# Broad local attachment shelves are integrated into the continuous field.
COLONIES = [
    {'source':0,'cx':-10.0,'cz':-29.8,'scale':.91,'angle':.3,'height':1.39},
    {'source':6,'cx':11.0,'cz':-30.0,'scale':.72,'angle':1.4,'height':.70},
    {'source':17,'cx':12.0,'cz':-44.0,'scale':.89,'angle':-1.0,'height':2.04},
    {'source':8,'cx':-7.0,'cz':-53.0,'scale':.78,'angle':2.3,'height':.55},
]

def smooth(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)

def height(x,z):
    x=np.asarray(x);z=np.asarray(z)
    # Low-frequency warping makes connected shorelines and unequal alcoves.
    xx=x+.48*np.sin(z*.37)+.18*np.sin(z*.91+x*.2)
    zz=z+.52*np.sin(x*.31)+.25*np.sin(x*.88-z*.12)
    fields=[]
    for k,(cx,cz,rx,rz,h,angle) in enumerate(LOBES):
        c=math.cos(angle);s=math.sin(angle)
        u=((xx-cx)*c+(zz-cz)*s)/rx
        v=(-(xx-cx)*s+(zz-cz)*c)/rz
        a=np.abs(u)**3.4+np.abs(v)**3.1
        # A weathered low shelf, stepped in height, not a stretched sphere.
        skirt=.18*np.exp(-a*.65)
        shelf=(h-.18)*np.exp(-a*1.65)
        broad=.07*np.sin(xx*1.14+zz*.67+k)*np.sin(zz*.83-xx*.29)
        wear=.035*np.sin(xx*3.3+zz*1.4)*np.sin(zz*2.7-xx*.51)
        fields.append(skirt+shelf+(broad+wear)*np.exp(-a*1.8))
    # Smooth max retains uneven ridges without summing them into tall humps.
    f=np.stack(fields)
    peak=f.max(axis=0)
    h=-.37+peak+.06*np.sum(np.minimum(f,.1),axis=0)
    # A few metre-scale erosional clefts break the long crests. These are
    # broad saddles and uneven low recesses, not tiny noise or tall pillars.
    for cx,cz,rx,rz,depth,skew in [
        (-8.4,-26.6,2.8,1.25,.34,.32),
        (-10.7,-35.2,5.1,1.65,.61,-.20),
        (8.7,-31.4,2.6,1.2,.28,.28),
        (12.6,-39.4,6.0,1.7,.66,.20),
        (16.0,-46.3,2.0,3.8,.36,-.35),
        (3.2,-52.6,2.1,4.0,.34,.40),
    ]:
        u=(x-cx)/rx;v=(z-cz+skew*(x-cx))/rz
        h-=depth*np.exp(-np.abs(u)**3.2-v*v)
    # Limited rough exposed rock on two flanks, softened into their shelves.
    rough_window=np.exp(-((x+10.4)/3.5)**4-((z+27.4)/3.0)**4)+np.exp(-((x-9.4)/3.1)**4-((z+36.4)/3.2)**4)
    h+=(.10*np.sin(x*1.65+z*.95)+.07*np.cos(x*.87-z*1.3))*rough_window*smooth((h+.15)/.4)
    # Wide meandering sand channel; stays open through and beyond all cameras.
    center=np.interp(z,[-60,-45,-36,-27,-18,-10],[-2.5,-3,-3.8,-1.5,0,.2])
    corridor=1-smooth((np.abs(x-center)-2.5)/1.3)
    h=h*(1-corridor)+(-.37)*corridor
    # Preserve original added thickets and their low support surfaces.
    for cx,cz,rx,rz in [(-3.1,-13.2,2.8,2.9),(3.6,-16.8,2.8,2.9),(-4.5,-21.1,3.2,3.2),(1.8,-26,3.0,3.0),(-12,-15,3.8,3.4),(10,-21,4.0,3.2)]:
        d=np.sqrt(((x-cx)/rx)**2+((z-cz)/rz)**2)
        cut=1-smooth((d-.95)/.3)
        h=h*(1-cut)+(-.37)*cut
    for q in COLONIES:
        d=np.sqrt((x-q['cx'])**2+(z-q['cz'])**2)
        blend=1-smooth((d-1.55)/1.05)
        h=h*(1-blend)+q['height']*blend
    # Buried rectangular outer perimeter. Its edges never break the sand.
    edge=smooth(np.minimum.reduce([(x+24)/2,(24-x)/2,(z+61)/2,(-11-z)/2]))
    return -.4+(h+.4)*edge

def load(path):
    raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0]
    return raw,json.loads(raw[20:20+n]),bytearray(raw[28+n:])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
    raw,j,b=load(a.input);assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA,'Unexpected source GLB; original accepted sand fix required'
    before=copy.deepcopy(j);binary_before=bytes(b)
    xs=np.linspace(-24,24,97);zs=np.linspace(-61,-11,101)
    xx,zz=np.meshgrid(xs,zs)
    h=height(xx,zz)
    verts=np.column_stack((xx.ravel(),h.ravel(),zz.ravel())).tolist()
    faces=[];nx=len(xs);nz=len(zs)
    for iz in range(nz-1):
        for ix in range(nx-1):
            p=iz*nx+ix
            if (ix+iz)%2:faces.extend([(p,p+nx,p+1),(p+1,p+nx,p+nx+1)])
            else:faces.extend([(p,p+nx+1,p+1),(p,p+nx,p+nx+1)])
    top_count=len(verts);top_face_count=len(faces)
    # Clockwise in the x/z plane; duplicated bottom ring and bottom fan make
    # every boundary edge incident to exactly two triangles.
    ring=list(range(nx))+[i*nx+nx-1 for i in range(1,nz)]+[(nz-1)*nx+i for i in range(nx-2,-1,-1)]+[i*nx for i in range(nz-2,0,-1)]
    lower=[]
    for q in ring:
        lower.append(len(verts));v=verts[q];verts.append([v[0],-.86,v[2]])
    for k,up in enumerate(ring):
        kn=(k+1)%len(ring);faces.extend([(up,ring[kn],lower[k]),(ring[kn],lower[kn],lower[k])])
    center=len(verts);verts.append([0,-.86,-36])
    for k in range(len(ring)):faces.append((center,lower[k],lower[(k+1)%len(ring)]))
    v=np.asarray(verts,dtype='<f4');idx=np.asarray(faces,dtype='<u2')
    normals=np.zeros_like(v)
    fn=np.cross(v[idx[:,1]]-v[idx[:,0]],v[idx[:,2]]-v[idx[:,0]])
    for col in range(3):np.add.at(normals,idx[:,col],fn)
    length=np.linalg.norm(normals,axis=1);assert np.all(length>1e-9)
    normals/=length[:,None]
    uv=np.column_stack((v[:,0]*.65,-v[:,2]*.65)).astype('<f4')
    mott=.90+.065*np.sin(v[:,0]*.66+v[:,2]*.91)+.05*np.sin(v[:,0]*2.12-v[:,2]*.7)
    # Derived from the existing limestone vertex-color range, not new material.
    colors=(np.asarray([.172,.187,.132])*mott[:,None]).astype('<f4')
    def accessor(array,kind,ctype=5126,target=34962,bounds=False):
        b.extend(b'\0'*((-len(b))%4));off=len(b);data=array.tobytes();b.extend(data)
        vi=len(j['bufferViews']);j['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(data),'target':target})
        ac={'bufferView':vi,'componentType':ctype,'count':len(array),'type':kind}
        if bounds:ac.update(min=array.min(axis=0).tolist(),max=array.max(axis=0).tolist())
        ai=len(j['accessors']);j['accessors'].append(ac);return ai
    attrs={'POSITION':accessor(v,'VEC3',bounds=True),'NORMAL':accessor(normals,'VEC3'),'TEXCOORD_0':accessor(uv,'VEC2'),'COLOR_0':accessor(colors,'VEC3')}
    ia=accessor(idx.ravel(),'SCALAR',5123,34963)
    mi=len(j['meshes']);j['meshes'].append({'name':'Spatial_Continuous_Weathered_Limestone','primitives':[{'attributes':attrs,'indices':ia,'material':2}]})
    ni=len(j['nodes']);j['nodes'].append({'name':'Spatial_Continuous_Weathered_Limestone','mesh':mi});j['scenes'][j.get('scene',0)]['nodes'].append(ni)
    colonies=[]
    for k,q in enumerate(COLONIES):
        src=next(n for n in before['nodes'] if n['name']==f"Coral_Staghorn_Thicket_{q['source']:02d}")
        ac=before['accessors'][before['meshes'][src['mesh']]['primitives'][0]['attributes']['POSITION']]
        mn=ac['min'];mx=ac['max'];cx=(mn[0]+mx[0])/2;cz=(mn[2]+mx[2])/2;sc=q['scale'];ang=q['angle'];c=math.cos(ang);s=math.sin(ang)
        ty=q['height']-.055
        trans=[q['cx']-sc*(c*cx+s*cz),ty,q['cz']-sc*(-s*cx+c*cz)]
        node={'name':f'Spatial_Staghorn_Linked_{k:02d}','mesh':src['mesh'],'translation':trans,'rotation':[0,math.sin(ang/2),0,math.cos(ang/2)],'scale':[sc,sc,sc]}
        ni=len(j['nodes']);j['nodes'].append(node);j['scenes'][j.get('scene',0)]['nodes'].append(ni)
        colonies.append({'node':node,'source':src['name'],'center':[q['cx'],q['height'],q['cz']],'support':'Integrated flat center radius 1.55 m blending over 1.05 m into continuous limestone; branch bases embedded .055 m'})
    j['buffers'][0]['byteLength']=len(b);jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);b+=b'\0'*((-len(b))%4)
    out=struct.pack('<4sII',b'glTF',2,28+len(jb)+len(b))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(b),b'BIN\0')+b
    assert len(out)<30_000_000, len(out)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(out)
    edges=np.sort(np.concatenate([idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
    assert np.all(counts==2),'Nonmanifold terrain'
    report={'input_sha256':SOURCE_SHA,'output_sha256':hashlib.sha256(out).hexdigest(),'bytes':len(out),'original_binary_prefix_unchanged':b[:len(binary_before)]==binary_before,'original_nodes_unchanged':j['nodes'][:len(before['nodes'])]==before['nodes'],'original_meshes_unchanged':j['meshes'][:len(before['meshes'])]==before['meshes'],'original_materials_images_textures_unchanged':all(j[k]==before[k]for k in ['materials','images','textures']),'new_vertices':len(v),'new_triangles':len(idx),'closed_manifold_edge_incidence':{'min':int(counts.min()),'max':int(counts.max())},'terrain_bounds':[v.min(0).tolist(),v.max(0).tolist()],'terrain_top_triangles':top_face_count,'terrain_top_vertices':top_count,'perimeter_top_y_min_max':[float(v[ring,1].min()),float(v[ring,1].max())],'lobes':LOBES,'colonies':colonies,'route':ROUTE,'waypoints':WAYPOINTS,'provenance':'Original deterministic inferred limestone composition and four shared original procedural staghorn meshes. No paid assets, scans, species additions, or measured-habitat claims.'}
    a.output.with_suffix('.proof.json').write_text(json.dumps(report,indent=2));a.output.with_name('spatial-route.json').write_text(json.dumps({'views':ROUTE,'waypoints':WAYPOINTS},indent=2))
    print(json.dumps({k:report[k]for k in ['output_sha256','bytes','new_vertices','new_triangles','terrain_bounds','original_binary_prefix_unchanged','original_nodes_unchanged']}))

if __name__=='__main__':main()
