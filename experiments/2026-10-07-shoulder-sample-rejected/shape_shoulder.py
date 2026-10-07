"""One explicit local shoulder, with two short under-lips and an open sand notch.

No scan is represented. Profiles are qualitative interpretation of NOAA's
Molasses Reef image. Only this 10 x 10 metre region is resampled.
"""
import argparse,hashlib,json,struct
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
SOURCE_SHA='c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd'
TERRAIN='Spatial_Continuous_Weathered_Limestone'
BOUNDS=(-13.,-3.,-29.,-19.)

def read(p):
 r=p.read_bytes();n=struct.unpack_from('<I',r,12)[0];return r,json.loads(r[20:20+n]),bytearray(r[28+n:])
def arr(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];d={5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];c={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
 return np.ndarray((a['count'],c),d,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',c*np.dtype(d).itemsize),np.dtype(d).itemsize)).copy()
def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
def old_height(x,z,original):
 # Exact piecewise linear surface of the original checkerboard triangulation.
 x=np.asarray(x);z=np.asarray(z);fx=(x+24)*2;fz=(z+61)*2;ix=np.floor(fx).astype(int);iz=np.floor(fz).astype(int);u=fx-ix;v=fz-iz
 ix=np.clip(ix,0,95);iz=np.clip(iz,0,99);g=original[:9797,1].reshape(101,97);a=g[iz,ix];b=g[iz,ix+1];c=g[iz+1,ix];d=g[iz+1,ix+1]
 return np.where((ix+iz)%2, np.where(u+v<=1,a+(b-a)*u+(c-a)*v,d+(c-d)*(1-u)+(b-d)*(1-v)),np.where(v<=u,a+(b-a)*(u-v)+(d-a)*v,a+(d-a)*u+(c-a)*(v-u)))

def compose(original):
 # The authored front is a broken oblique shoulder, not a constant-height bench.
 # z, edge x, crest height, lip height, under-lip horizontal inset, cavity-floor height.
 key=np.array([
 [-29,-6.0,.72,.52,0,.08],[-28.25,-6.3,.98,.68,.04,.02],
 [-27.35,-6.45,1.20,.91,.52,.13],[-26.60,-7.15,.96,.69,.62,-.03],
 [-25.85,-7.7,.57,.34,.17,-.10],[-25.25,-9.00,.24,.08,0,-.25],
 [-24.75,-8.15,.71,.49,.20,-.12],[-24.15,-6.75,.94,.68,.52,-.05],
 [-23.55,-7.55,.77,.56,.35,-.06],[-22.75,-8.2,.55,.29,0,-.17],
 [-21.75,-8.45,.51,.29,0,-.22],[-20,-8.4,.45,.2,0,-.22],[-19,-8.4,.45,.2,0,-.22]])
 ps=PchipInterpolator(key[:,0],key[:,1:],axis=0)
 # Smooth subdivisions of the original 0.5 m triangulation; boundary vertices
 # are shared with the original ring rather than duplicated.
 xs=np.linspace(-13,-3,81);zs=np.linspace(-29,-19,81)
 uu,zz=np.meshgrid((xs+13)/10,zs);zflat=zz.ravel();u=uu.ravel();base_x=-13+10*u;base_y=old_height(base_x,zflat,original)
 values=ps(zflat);edge,crest,lip,inset,floor=values.T
 # ONE correction: the first neutral view exposed continuous rolled shelves.
 # Localize recesses, bury the lower apron, and give the exposed rim short
 # unequal broken segments. These are explicit erosion features, not noise.
 cavities=np.exp(-((zflat+27.20)/.46)**4)+.82*np.exp(-((zflat+24.02)/.33)**4)
 inset*=np.minimum(1,cavities)
 for cz,width,depth in [(-27.65,.19,.12),(-26.95,.24,.20),(-24.48,.18,.13),(-23.90,.16,.11),(-23.28,.23,.14)]:
  bite=np.exp(-((zflat-cz)/width)**4)
  edge-=.25*bite;lip-=depth*bite;crest-=depth*.32*bite
 floor=np.minimum(floor,-.235)
 # Nonuniform x/y section. Short reverse-x intervals form genuine under-lips.
 # The two short faces share the same body with a deep notch at z=-25.25.
 xp=np.stack([np.full_like(edge,-13),np.full_like(edge,-12),edge-2.2,edge-1.15,edge-.48,edge,edge-inset,edge+.23,edge+.7,np.full_like(edge,-3)],axis=1)
 yp=np.stack([old_height(-13+np.zeros_like(zflat),zflat,original),old_height(-12+np.zeros_like(zflat),zflat,original)+.02,crest*.68,crest,crest*.92,lip,floor,np.full_like(edge,-.30),np.full_like(edge,-.36),np.full_like(edge,-.37)],axis=1)
 knots=np.array([0,.10,.29,.44,.53,.61,.68,.75,.84,1.0])
 # Linear sections keep lips honest; PCHIP along z avoids repeated terraces.
 col=np.minimum(np.searchsorted(knots,u,side='right')-1,len(knots)-2);col=np.maximum(col,0);t=(u-knots[col])/(knots[col+1]-knots[col]);ix=np.arange(len(u));x=xp[ix,col]*(1-t)+xp[ix,col+1]*t;y=yp[ix,col]*(1-t)+yp[ix,col+1]*t
 # Local linear interpolation of hand-placed, unequal crest depressions. No
 # random displacement or periodic noise is added.
 window=smooth((zflat+29)/1.4)*smooth((-21.25-zflat)/1.6)*smooth(u/.10)*smooth((1-u)/.13)
 # Preserve all of the established (-10,-29.8) colony's broad attachment zone.
 radius=np.hypot(base_x+10,zflat+29.8);window*=smooth((radius-2.35)/.85)
 x=base_x+(x-base_x)*window;y=base_y+(y-base_y)*window
 v=original.copy().tolist();mapping={};new_ids=[]
 # Keep old grid nodes on the patch edge; subdivide only patch interior.
 # One fan per boundary cell joins the 0.125 m patch to the old 0.5 m edge.
 for zi,z in enumerate(zs):
  for xi,xx in enumerate(xs):
   if zi in (0,80) or xi in (0,80):
    if zi%4 or xi%4:continue
    oi=round((z+61)*2)*97+round((xx+24)*2);mapping[(zi,xi)]=oi
   else:
    mapping[(zi,xi)]=len(v);new_ids.append(len(v));k=zi*81+xi;v.append([x[k],y[k],z])
 v=np.array(v,dtype='<f4');faces=[]
 # Interior grid and coarse transition strips, split into boundary fans.
 for zi in range(1,79):
  for xi in range(1,79):
   a=mapping[(zi,xi)];b=mapping[(zi,xi+1)];c=mapping[(zi+1,xi)];d=mapping[(zi+1,xi+1)];faces.extend([(a,c,b),(b,c,d)])
 # General polygon triangulation fans joining perimeter coarse nodes and inner
 # grid. The corner sectors are handled with the same strips.
 def fan(poly):
  vs=v[poly];center=vs.mean(axis=0);ci=len(vlist);vlist.append(center.tolist())
  for i in range(len(poly)):faces.append((ci,poly[i],poly[(i+1)%len(poly)]))
 vlist=v.tolist()
 # Orient each strip consistently upward (clockwise in x/z coordinates).
 for k in range(0,80,4):
  lo=max(1,k);hi=min(79,k+4)
  fan([mapping[(0,k)],mapping[(0,k+4)]]+[mapping[(1,j)]for j in range(hi,lo-1,-1)])
  fan([mapping[(80,k+4)],mapping[(80,k)]]+[mapping[(79,j)]for j in range(lo,hi+1)])
  fan([mapping[(k+4,0)],mapping[(k,0)]]+[mapping[(j,1)]for j in range(lo,hi+1)])
  fan([mapping[(k,80)],mapping[(k+4,80)]]+[mapping[(j,79)]for j in range(hi,lo-1,-1)])
 # Corner strip polygons share a diagonal corner-to-inner edge but leave the
 # triangle between two strips. Close each triangular corner explicitly.
 # No extra corner face is required: both strips share that edge directly.
 return np.asarray(vlist,dtype='<f4'),np.asarray(faces,dtype='<u4'),new_ids

def main():
 p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--geometry-only',action='store_true');a=p.parse_args()
 raw,j,b=read(a.input);assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA
 node=next(n for n in j['nodes']if n['name']==TERRAIN);pr=j['meshes'][node['mesh']]['primitives'][0];v0=arr(j,b,pr['attributes']['POSITION']);idx0=arr(j,b,pr['indices']).reshape(-1,3)
 v,newf,new_ids=compose(v0)
 tri=v0[idx0];cent=tri.mean(1);cut=(cent[:,0]>-13)&(cent[:,0]<-3)&(cent[:,2]>-29)&(cent[:,2]<-19)&(idx0.max(1)<9797)
 idx=np.vstack([idx0[~cut],newf]).astype('<u2')
 # Strip orientation is checked below; flip all new faces whose initial x/z
 # orientation points down only on the boundary transition. Interior folded
 # faces intentionally include some downward normals.
 start=len(idx0)-int(cut.sum());boundary_start=start+78*78*2
 for k in range(boundary_start,len(idx)):
  f=idx[k];normal=np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]])
  if normal[1]<0:idx[k]=f[[0,2,1]]
 n=arr(j,b,pr['attributes']['NORMAL']);uv=arr(j,b,pr['attributes']['TEXCOORD_0']);color=arr(j,b,pr['attributes']['COLOR_0'])
 fn=np.cross(v[idx[:,1]]-v[idx[:,0]],v[idx[:,2]]-v[idx[:,0]]);norm=np.zeros_like(v)
 for col in range(3):np.add.at(norm,idx[:,col],fn)
 lengths=np.linalg.norm(norm,axis=1);used=lengths>1e-12;norm[used]/=lengths[used,None]
 # Preserve original normals except the boundary vertices affected by new faces.
 changed=set(idx[boundary_start:].ravel().tolist());protected=np.array([i for i in range(len(v0))if i not in changed]);norm[protected]=n[protected]
 tex=np.column_stack((v[:,0]*.65,-v[:,2]*.65)).astype('<f4');tex[:len(v0)]=uv
 mott=.90+.065*np.sin(v[:,0]*.66+v[:,2]*.91)+.05*np.sin(v[:,0]*2.12-v[:,2]*.7);colors=(np.array([.172,.187,.132])*mott[:,None]).astype('<f4');colors[:len(v0)]=color
 edges=np.sort(np.concatenate([idx[:,[0,1]],idx[:,[1,2]],idx[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True);assert np.all(counts==2),np.unique(counts,return_counts=True)
 outdir=a.output.parent;outdir.mkdir(parents=True,exist_ok=True);np.savez(outdir/'shoulder-geometry.npz',vertices=v,faces=idx,original_vertices=v0,original_faces=idx0,changed_normal_ids=np.array(sorted(changed)),new_face_start=start,patch_bounds=np.array(BOUNDS))
 if a.geometry_only:print(json.dumps({'stage':'neutral geometry','vertices':len(v),'faces':len(idx),'patch_faces_removed':int(cut.sum()),'closed_edge_incidence':True}));return
 # Appending new accessors leaves all original binary bytes exact, including
 # original terrain attributes. Only this terrain primitive points elsewhere.
 def access(array,kind,ctype=5126,target=34962,bounds=False):
  b.extend(b'\0'*((-len(b))%4));off=len(b);data=array.tobytes();b.extend(data);vi=len(j['bufferViews']);j['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(data),'target':target});ac={'bufferView':vi,'componentType':ctype,'count':len(array),'type':kind}
  if bounds:ac.update(min=array.min(0).tolist(),max=array.max(0).tolist())
  ai=len(j['accessors']);j['accessors'].append(ac);return ai
 pr['attributes']={'POSITION':access(v,'VEC3',bounds=True),'NORMAL':access(norm,'VEC3'),'TEXCOORD_0':access(tex,'VEC2'),'COLOR_0':access(colors,'VEC3')};pr['indices']=access(idx.ravel(),'SCALAR',5123,34963)
 j['buffers'][0]['byteLength']=len(b);jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);b+=b'\0'*((-len(b))%4);out=struct.pack('<4sII',b'glTF',2,28+len(jb)+len(b))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(b),b'BIN\0')+b
 assert len(out)<32*1024*1024;a.output.write_bytes(out);print(json.dumps({'sha256':hashlib.sha256(out).hexdigest(),'bytes':len(out),'vertices':len(v),'triangles':len(idx),'new_normal_boundary_vertices':len(changed)}))
if __name__=='__main__':main()
