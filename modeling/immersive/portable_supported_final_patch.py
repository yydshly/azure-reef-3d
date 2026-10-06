import struct,json,hashlib,math,argparse,copy,numpy as np
from pathlib import Path
parser=argparse.ArgumentParser(description='Add shared original limestone support beneath distant thickets. No new morphology.')
parser.add_argument('input',type=Path);parser.add_argument('baseline',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
def read(p):
 raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];return raw,json.loads(raw[20:20+n]),bytearray(raw[28+n:])
raw,j,b=read(args.input);original,s,sb=read(args.baseline)
assert hashlib.sha256(raw).hexdigest()=='f97a6f44ce9664d06c8f4e098a315e18ca30706e2d175f721d312dbf8be54863','Wrong depth candidate'
assert hashlib.sha256(original).hexdigest()=='22978ea17f029220f439dfab68a616e2fa3135dd0bc58b465a735ac09a036094','Wrong original baseline'
source=next(n for n in s['nodes']if n['name']=='Hardbottom_Low_Irregular_Limestone');mesh=copy.deepcopy(s['meshes'][source['mesh']]);mesh['name']='Original_Limestone_Shared_Distant_Support'
# Copy original baseline limestone accessor bytes intact, including original shape before corridor carving.
accessors={};views={}
def ca(i):
 if i in accessors:return accessors[i]
 a=copy.deepcopy(s['accessors'][i]);vi=a['bufferView']
 if vi not in views:
  view=copy.deepcopy(s['bufferViews'][vi]);off=view.get('byteOffset',0);data=sb[off:off+view['byteLength']];b.extend(b'\0'*((-len(b))%4));view['byteOffset']=len(b);view['buffer']=0;b.extend(data);views[vi]=len(j['bufferViews']);j['bufferViews'].append(view)
 a['bufferView']=views[vi];accessors[i]=len(j['accessors']);j['accessors'].append(a);return accessors[i]
for p in mesh['primitives']:
 p['indices']=ca(p['indices']);p['attributes']={k:ca(v)for k,v in p['attributes'].items()}
 # Resolve material by name rather than assuming index ordering.
 p['material']=next(i for i,m in enumerate(j['materials'])if m['name']==s['materials'][p['material']]['name'])
mi=len(j['meshes']);j['meshes'].append(mesh);proof=[]
for node in list(j['nodes']):
 if not node['name'].startswith('Corridor_Distant_Linked_'):continue
 k=int(node['name'].rsplit('_',1)[1]);a=j['accessors'][j['meshes'][node['mesh']]['primitives'][0]['attributes']['POSITION']];mn=a['min'];mx=a['max'];sc=node['scale'][0];q=node['rotation'];angle=2*math.atan2(q[1],q[3]);c=math.cos(angle);sn=math.sin(angle);localx=(mn[0]+mx[0])/2;localz=(mn[2]+mx[2])/2
 cx=node['translation'][0]+sc*(c*localx+sn*localz);cz=node['translation'][2]+sc*(-sn*localx+c*localz)
 if k in (0,4):node['translation'][2]+= -1.1 if k==0 else 1.1;cz+= -1.1 if k==0 else 1.1
 # Broad shallow bed: exposed upper surface only, with most of its volume hidden in existing sand.
 width=sc*((mx[0]-mn[0])*abs(c)+(mx[2]-mn[2])*abs(sn));depth=sc*((mx[0]-mn[0])*abs(sn)+(mx[2]-mn[2])*abs(c))
 sx=(width+.6)/15;sz=(depth+.6)/14;sy=.4;surface=-.12 if k in(0,4) else -.19
 # Baseline center in Three z is -1.6. The thicket's base remains embedded through the rock surface.
 support={'name':f'Distant_Limestone_Support_{k:02d}','mesh':mi,'translation':[cx,surface,cz+1.6*sz],'scale':[sx,sy,sz]}
 index=len(j['nodes']);j['nodes'].append(support);j['scenes'][j.get('scene',0)]['nodes'].append(index)
 zb=[cz-depth/2-.3,cz+depth/2+.3];assert min(zb)>10 or max(zb)<-10
 proof.append({'coral':node['name'],'support':support,'support_z_bounds':zb,'source_mesh':source['name'],'source_geometry':'Original baseline limestone mesh reused, with derived perimeter lowering only; one shared support mesh','layout':'Low partly buried inferred attachment beds on existing sand, not observed survey reconstruction'})
# Feather only the newly copied support perimeter. Its center stays byte-exact.
def arr(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];cols={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.ndarray((a['count'],cols),dtype=dtype,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',np.dtype(dtype).itemsize*cols),np.dtype(dtype).itemsize))
p=mesh['primitives'][0];verts=arr(p['attributes']['POSITION']);radius=np.sqrt((verts[:,0]/7.5)**2+((verts[:,2]+1.6)/7)**2);t=np.clip((radius-.63)/.37,0,1);weight=t*t*(3-2*t);verts[:,1]-=.85*weight
pa=j['accessors'][p['attributes']['POSITION']];pa['min']=verts.min(axis=0).tolist();pa['max']=verts.max(axis=0).tolist()
indices=arr(p['indices']).reshape(-1,3);norm=arr(p['attributes']['NORMAL']);ns=np.zeros_like(verts);faces=np.cross(verts[indices[:,1]]-verts[indices[:,0]],verts[indices[:,2]]-verts[indices[:,0]])
for col in range(3):np.add.at(ns,indices[:,col],faces)
lens=np.linalg.norm(ns,axis=1);mask=lens>1e-12;norm[mask]=ns[mask]/lens[mask,None]
for item in proof:item['perimeter_correction']='New shared support only: radius <= .63 untouched; smooth .85 local-unit downward taper outside, burying perimeter. Derived original limestone morphology; old core unchanged.'
j['buffers'][0]['byteLength']=len(b);jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);b+=b'\0'*((-len(b))%4);out=struct.pack('<4sII',b'glTF',2,28+len(jb)+len(b))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(b),b'BIN\0')+b;args.output.write_bytes(out)
args.output.with_suffix('.proof.json').write_text(json.dumps({'glb_bytes':len(out),'sha256':hashlib.sha256(out).hexdigest(),'supports':proof,'existing_binary_prefix_unchanged':b[:len(read(args.input)[2])]==read(args.input)[2],'unchanged_core_nodes':j['nodes'][:75]==read(args.input)[1]['nodes'][:75]},indent=2));print('SUPPORTED_READY',len(out))
