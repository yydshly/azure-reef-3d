"""Replace only the October 7 spatial terrain in the frozen published GLB.

Portable deterministic NumPy recipe; no scans, image textures or new organisms.
Authored metre convention. This is an interpreted arrangement, not a survey.
"""
import argparse, copy, hashlib, json, math, struct
from pathlib import Path
import numpy as np

SOURCE_SHA='c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd'
TERRAIN='Spatial_Continuous_Weathered_Limestone'
# One bounded silhouette correction after the first diagnostic: unequal parent
# bodies with a diagonal west spur and narrow mid-neck, and a broad southeast
# mother body with a much smaller northern arm. These replace the initial
# parallel strips. They are explicit metre-scale changes, not more edge noise.
WEST=[(-20,-11.8),(-12,-12.4),(-10,-14),(-6.3,-13.1),(-3,-12.1),(-2,-13.6),(-4,-15.2),(-7.5,-16.3),(-6.5,-18),(-3.7,-18.6),(-2.3,-21),(-4.8,-23.4),(-5.2,-26),(-3.8,-29),(-5.8,-32.7),(-8.8,-34.9),(-10.3,-37.1),(-10.9,-40),(-9.3,-42.8),(-12.5,-44.7),(-10.8,-47),(-7.1,-49.4),(-4.6,-51),(-6.4,-53.1),(-5,-55.5),(-10,-58.8),(-17,-59.5),(-21,-56),(-18,-52),(-20.5,-49),(-18,-45),(-14.8,-43),(-15.2,-40),(-13.2,-36.5),(-14.8,-34.5),(-19,-33),(-22.8,-28),(-21.9,-25),(-23,-22),(-20.9,-19),(-23,-16)]
EAST=[(10,-12),(17,-13),(19,-17),(18,-20),(20,-23),(17,-25),(16,-28),(15.8,-31),(18,-33),(21.5,-33.7),(23,-36),(21,-39),(23,-43),(21.8,-48),(22.5,-53),(18.4,-56),(14,-59),(9,-57),(8,-54),(5,-54.4),(2,-52),(.5,-49.8),(3,-47.6),(5.5,-45.4),(9.2,-42.4),(5.4,-39.3),(6.1,-36.3),(10,-34.8),(11.5,-32.7),(10,-30),(11,-28),(8,-26.9),(3,-28.2),(.1,-25.8),(2.3,-23.9),(6.1,-23.1),(7.4,-21.4),(3,-20.4),(1.2,-17.7),(2.5,-15.8),(6.2,-15.2),(8.2,-13.4)]
WEST_UP=[(-20.2,-17),(-15.4,-13.8),(-11,-15),(-9.5,-18.7),(-11.5,-20.2),(-8,-23.1),(-9.2,-25.6),(-6.1,-28.2),(-7.4,-31.3),(-10.6,-33.6),(-14,-31.5),(-18.8,-31.8),(-20.5,-27.5),(-18.2,-24.1),(-21.3,-21.4)]
WEST_FAR=[(-16.3,-45.9),(-12.7,-47.3),(-12.2,-50.5),(-7.3,-51.5),(-8.1,-55.5),(-12.3,-57.2),(-16.8,-56.1),(-15.7,-52.8),(-18.3,-50.2)]
EAST_UP=[(10,-37),(14.3,-34.8),(19.6,-36.3),(17.4,-39.3),(20.4,-42.4),(19.8,-46.3),(20.8,-51.8),(16.8,-54.1),(14.8,-56.3),(10.5,-54.8),(11.8,-51),(7.3,-52.1),(4.1,-49.9),(7.4,-47.8),(11.7,-45.6),(11.9,-42.4),(9.4,-40.5)]
EAST_NEAR=[(12.8,-15),(16.5,-15.1),(17.4,-18.4),(15.8,-21.8),(17.5,-23.1),(13.7,-25.1),(10.2,-23.6),(11.7,-20),(10.8,-17.3)]
WEST_CREST=[(-17.7,-22.2),(-14.7,-20.4),(-11.5,-23.5),(-12.6,-26.6),(-9.2,-29),(-11.1,-31.3),(-14.4,-29.9),(-18,-29),(-16.5,-25.9)]
EAST_CREST=[(14.8,-37.9),(17.5,-37.4),(16.2,-40.1),(18.1,-42.7),(16.5,-45.9),(18.2,-48.7),(16.5,-52.1),(13.4,-51.9),(14.5,-48.5),(13.1,-46.3),(14.2,-43.8),(13.1,-41.3)]

def smooth(t):
    t=np.clip(t,0,1);return t*t*(3-2*t)

def signed_distance(x,z,polygon):
    """Exact planar segment distance and parity sign, positive in polygon."""
    inside=np.zeros(np.broadcast(x,z).shape,dtype=bool);d=np.full(inside.shape,np.inf)
    for (ax,az),(bx,bz) in zip(polygon,polygon[1:]+polygon[:1]):
        dx=bx-ax;dz=bz-az
        t=np.clip(((x-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz),0,1)
        d=np.minimum(d,np.hypot(x-ax-t*dx,z-az-t*dz))
        inside^=((az>z)!=(bz>z))&(x<(bx-ax)*(z-az)/(bz-az+1e-20)+ax)
    return np.where(inside,d,-d)

def height(x,z):
    x=np.asarray(x);z=np.asarray(z)
    # Modest boundary scalloping: metre-scale bites, with no repeated ring unit.
    xx=x+.25*np.sin(z*1.49+x*.36)+.13*np.cos(z*2.51-x*.8)
    zz=z+.23*np.sin(x*1.61-z*.18)+.11*np.cos(x*2.57+z*.7)
    d=np.maximum(signed_distance(xx,zz,WEST),signed_distance(xx,zz,EAST))
    low=smooth((d+.38)/.64)
    bench=.29+.075*np.sin(x*.67+z*.39)+.045*np.sin(x*1.8-z*1.17)
    h=-.40+low*bench
    # Irregular shoulder and local faces are 0.5–0.9 m deep. Broad tops vary
    # slowly, leaving rock-to-rock necks between visible reef buttresses.
    shoulder=smooth((d-.25)/.55)
    inner=np.maximum.reduce([signed_distance(xx,zz,q)for q in [WEST_UP,WEST_FAR,EAST_UP,EAST_NEAR]])
    ledge=smooth((inner+.26)/.67)
    shoulder_h=.46+.13*np.sin(z*.27+x*.39)+.08*np.cos(z*.52-x*.16)
    ledge_h=.75+.16*np.sin(z*.23-x*.2)+.12*np.cos(x*.75+z*.19)
    h+=shoulder*shoulder_h+ledge*ledge_h*shoulder
    crest=np.maximum(signed_distance(xx,zz,WEST_CREST),signed_distance(xx,zz,EAST_CREST))
    h+=smooth((crest+.2)/.75)*(.66+.12*np.sin(z*.63+x*.34))*shoulder
    # An exposed low stone neck remains continuous across the western saddle.
    # The two sides now differ in both mass distribution and height rhythm.
    saddle=np.exp(-((x+12.0)/4.6)**4-((z+38.3)/3.1)**4)
    h=h*(1-saddle)+np.minimum(h,.12)*saddle
    # Nonparallel deep recesses stop above the low parent, so upper faces can
    # separate while the footprint remains visibly connected.
    clefts=[(-11.7,-26.5,5.7,.42,.65,.23),(-13.4,-38.5,5.4,.57,.9,-.42),(13.4,-31.9,6,.62,.76,-.25),(14.1,-43.5,4.8,.43,.72,.44),(-10.1,-49.2,3.8,.45,.7,-.56)]
    for cx,cz,rx,rz,depth,skew in clefts:
        mask=np.exp(-((x-cx)/rx)**6-((z-cz+skew*(x-cx))/rz)**4)
        h-=mask*depth*smooth((h-.1)/.65)
    # Broken relief on surfaces and face edges, amplitude kept below large
    # structure. This is geometry, using the pre-existing rock material.
    relief=(.045*np.sin(x*3.37+z*1.31)+.038*np.sin(x*1.59-z*3.53)+.024*np.cos(x*6.27+z*4.1))
    h+=relief*smooth((h+.13)/.45)
    # Same original low thickets: blend their supports into broad low fingers
    # instead of cutting circular holes in surrounding hardbottom.
    for cx,cz,rx,rz,ang in [(-3.1,-13.2,3.0,2.1,-.35),(3.6,-16.8,3.0,2.5,.45),(-4.5,-21.1,3.9,2.65,-.28),(1.8,-26,3.35,2.7,.38),(-12,-15,3.6,2.6,-.2),(10,-21,4,2.5,.3)]:
        c=math.cos(ang);s=math.sin(ang);u=((x-cx)*c+(z-cz)*s)/rx;v=(-(x-cx)*s+(z-cz)*c)/rz
        a=np.maximum(np.abs(u),np.abs(v))
        plateau=1-smooth((a-.76)/.38)
        h=h*(1-plateau)+(-.195)*plateau
    # The existing camera passage is untouched; this ceiling only suppresses
    # accidental high fingers near its path, leaving uneven low channel edges.
    center=np.interp(z,[-61,-49,-36,-27,-18,-11],[-1.7,-1.2,-3.8,-1.5,0,.15])
    half=np.interp(z,[-61,-51,-44,-36,-30,-25,-18,-11],[2.7,2.0,4.0,3.0,1.45,1.55,1.65,1.55])
    channel=1-smooth((np.abs(x-center)-half)/.48)
    h=h*(1-channel)+(-.4)*channel
    # Blending under the sand avoids a visible rectangular asset boundary.
    edge=smooth(np.minimum.reduce([(x+24)/1.2,(24-x)/1.2,(z+61)/1.0,(-11-z)/.6]))
    return -.4+(h+.4)*edge

def read(path):
    raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0]
    return raw,json.loads(raw[20:20+n]),bytearray(raw[28+n:])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
    raw,j,b=read(a.input);assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
    before=copy.deepcopy(j);node=next(n for n in j['nodes'] if n['name']==TERRAIN);pr=j['meshes'][node['mesh']]['primitives'][0]
    first=min(list(pr['attributes'].values())+[pr['indices']]);first_view=min(j['accessors'][k]['bufferView']for k in range(first,len(j['accessors'])))
    cutoff=j['bufferViews'][first_view]['byteOffset'];b=b[:cutoff];j['accessors']=j['accessors'][:first];j['bufferViews']=j['bufferViews'][:first_view]
    xs=np.linspace(-24,24,161);zs=np.linspace(-61,-11,168);xx,zz=np.meshgrid(xs,zs);h=height(xx,zz)
    # Four already-authorized linked colonies are reseated on naturally broad
    # parts of the new ledges; no mesh, orientation, scale, or x/z changes.
    colonies=[]
    for n in j['nodes']:
        if not n['name'].startswith('Spatial_Staghorn_Linked_'):continue
        src=before['meshes'][n['mesh']]['primitives'][0];ac=before['accessors'][src['attributes']['POSITION']];vw=before['bufferViews'][ac['bufferView']]
        raw_b=read(a.input)[2];p=np.ndarray((ac['count'],3),'<f4',buffer=raw_b,offset=vw.get('byteOffset',0)+ac.get('byteOffset',0))
        roots=p[p[:,1]<.045];ang=2*math.atan2(n['rotation'][1],n['rotation'][3]);c=math.cos(ang);s=math.sin(ang);sc=n['scale'][0]
        rx=sc*(c*roots[:,0]+s*roots[:,2])+n['translation'][0];rz=sc*(-s*roots[:,0]+c*roots[:,2])+n['translation'][2]
        cx=float((rx.min()+rx.max())/2);cz=float((rz.min()+rz.max())/2)
        # Flat attachment follows rectangular rock ledge axes, never a circle.
        hwx=(rx.max()-rx.min())/2+.21;hwz=(rz.max()-rz.min())/2+.21
        support=float(np.median(height(rx,rz)));support=max(support,.02)
        d=np.maximum(np.abs(xx-cx)/hwx,np.abs(zz-cz)/hwz)
        blend=1-smooth((d-1)/.7);h=h*(1-blend)+support*blend
        old_y=n['translation'][1];n['translation'][1]=support-.06
        colonies.append({'name':n['name'],'center':[cx,support,cz],'old_y':old_y,'new_y':n['translation'][1],'x_z_rotation_scale_unchanged':True})
    verts=np.column_stack((xx.ravel(),h.ravel(),zz.ravel())).tolist();nx=len(xs);nz=len(zs);faces=[]
    for iz in range(nz-1):
        for ix in range(nx-1):
            k=iz*nx+ix
            if(ix+iz)%2:faces.extend([(k,k+nx,k+1),(k+1,k+nx,k+nx+1)])
            else:faces.extend([(k,k+nx+1,k+1),(k,k+nx,k+nx+1)])
    top_vertices=len(verts);top_triangles=len(faces)
    ring=list(range(nx))+[i*nx+nx-1 for i in range(1,nz)]+[(nz-1)*nx+i for i in range(nx-2,-1,-1)]+[i*nx for i in range(nz-2,0,-1)]
    low=[]
    for k in ring:low.append(len(verts));verts.append([verts[k][0],-.86,verts[k][2]])
    for k,up in enumerate(ring):kn=(k+1)%len(ring);faces.extend([(up,ring[kn],low[k]),(ring[kn],low[kn],low[k])])
    center=len(verts);verts.append([0,-.86,-36])
    for k in range(len(ring)):faces.append((center,low[k],low[(k+1)%len(ring)]))
    v=np.array(verts,dtype='<f4');idx=np.array(faces,dtype='<u2');normals=np.zeros_like(v)
    fn=np.cross(v[idx[:,1]]-v[idx[:,0]],v[idx[:,2]]-v[idx[:,0]])
    for c in range(3):np.add.at(normals,idx[:,c],fn)
    normals/=np.linalg.norm(normals,axis=1)[:,None]
    uv=np.column_stack((v[:,0]*.65,-v[:,2]*.65)).astype('<f4')
    # Exactly the prior recipe's coordinate-based color function, unchanged.
    mott=.90+.065*np.sin(v[:,0]*.66+v[:,2]*.91)+.05*np.sin(v[:,0]*2.12-v[:,2]*.7)
    colors=(np.array([.172,.187,.132])*mott[:,None]).astype('<f4')
    def accessor(array,kind,ctype=5126,target=34962,bounds=False):
        b.extend(b'\0'*((-len(b))%4));off=len(b);data=array.tobytes();b.extend(data)
        vi=len(j['bufferViews']);j['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(data),'target':target})
        ac={'bufferView':vi,'componentType':ctype,'count':len(array),'type':kind}
        if bounds:ac.update(min=array.min(0).tolist(),max=array.max(0).tolist())
        ai=len(j['accessors']);j['accessors'].append(ac);return ai
    pr['attributes']={'POSITION':accessor(v,'VEC3',bounds=True),'NORMAL':accessor(normals,'VEC3'),'TEXCOORD_0':accessor(uv,'VEC2'),'COLOR_0':accessor(colors,'VEC3')}
    pr['indices']=accessor(idx.ravel(),'SCALAR',5123,34963)
    j['buffers'][0]['byteLength']=len(b);jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);b+=b'\0'*((-len(b))%4)
    out=struct.pack('<4sII',b'glTF',2,28+len(jb)+len(b))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(b),b'BIN\0')+b
    assert len(out)<=32*1024*1024
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(out)
    proof={'input_sha256':SOURCE_SHA,'output_sha256':hashlib.sha256(out).hexdigest(),'bytes':len(out),'binary_prefix_cutoff':cutoff,'original_binary_prefix_unchanged':b[:cutoff]==read(a.input)[2][:cutoff],'terrain_vertices':len(v),'terrain_triangles':len(idx),'top_vertices':top_vertices,'top_triangles':top_triangles,'bounds':[v.min(0).tolist(),v.max(0).tolist()],'colonies':colonies,'parent_outlines':[WEST,EAST],'upper_ledges':[WEST_UP,WEST_FAR,EAST_UP,EAST_NEAR],'crest_outlines':[WEST_CREST,EAST_CREST],'materials_lights_cameras_runtime':'Unchanged. The terrain vertex color function is also exactly the preceding coordinate-based function.','limitations':'2.5D stepped hardbottom; no overhangs, scans, measured ecology or additional biological meshes. Actual runtime A/B remains the visual gate.'}
    a.output.with_suffix('.proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps({k:proof[k]for k in ['output_sha256','bytes','terrain_vertices','terrain_triangles','bounds','colonies']}))

if __name__=='__main__':main()
