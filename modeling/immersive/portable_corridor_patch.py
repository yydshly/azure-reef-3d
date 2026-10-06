import struct,json,numpy as np,math,hashlib,argparse
from pathlib import Path
parser=argparse.ArgumentParser(description='Reproduce accepted corridor from exact frozen baseline. Requires numpy.')
parser.add_argument('input',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
raw=args.input.read_bytes()
EXPECTED='22978ea17f029220f439dfab68a616e2fa3135dd0bc58b465a735ac09a036094'
assert hashlib.sha256(raw).hexdigest()==EXPECTED,'Wrong baseline SHA-256; refusing to alter a different model'
n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);b=bytearray(raw[28+n:])
moves={'Coral_Staghorn_Thicket_02': -0.6709111045177252, 'Coral_Staghorn_Thicket_03': 2.0729397338888824, 'Coral_Staghorn_Thicket_04': 0.8789262747522101, 'Coral_Staghorn_Thicket_09': -1.681306874286085, 'Coral_Staghorn_Thicket_10': 0.9751676902059861, 'Coral_Staghorn_Thicket_14': -1.1162401330792724, 'Coral_Staghorn_Thicket_15': 0.5925483967429089, 'Coral_Staghorn_Thicket_18': -0.3331158363714941, 'Coral_Staghorn_Thicket_19': 1.9194411772560667, 'Coral_Staghorn_Thicket_20': 1.057804808273512}
for node in j['nodes']:
 if node['name'] in moves:node['translation']=[moves[node['name']],0,0]
node=next(x for x in j['nodes']if x['name']=='Hardbottom_Low_Irregular_Limestone');p=j['meshes'][node['mesh']]['primitives'][0]
def array(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dtype={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];cols={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.ndarray((a['count'],cols),dtype=dtype,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',np.dtype(dtype).itemsize*cols),np.dtype(dtype).itemsize))
v=array(p['attributes']['POSITION']);old=v.copy();x,y,z=v.T;c=.8+.12*z+.28*np.sin((z+1)*.6);w=.76+.11*np.sin(z*.8+.4)
def sm(t):t=np.clip(t,0,1);return t*t*(3-2*t)
weight=(1-sm((np.abs(x-c)-w)/.65))*sm((z+10.7)/.7)*sm((4.3-z)/.8)*sm((np.sqrt((x+.3038789)**2+(z-3.6140898)**2)-.45)/.4)
v[:,1]=np.minimum(y,y+(-.255-y)*weight)
# Update smooth vertex normals from unchanged triangle topology.
idx=array(p['indices']).reshape(-1,3);norm=array(p['attributes']['NORMAL']);ns=np.zeros_like(v);face=np.cross(v[idx[:,1]]-v[idx[:,0]],v[idx[:,2]]-v[idx[:,0]])
for col in range(3):np.add.at(ns,idx[:,col],face)
length=np.linalg.norm(ns,axis=1);mask=length>1e-12;norm[mask]=ns[mask]/length[mask,None]
a=j['accessors'][p['attributes']['POSITION']];a['min']=v.min(axis=0).tolist();a['max']=v.max(axis=0).tolist()
jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);b+=b'\0'*((-len(b))%4);out=struct.pack('<4sII',b'glTF',2,28+len(jb)+len(b))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(b),b'BIN\0')+b
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(out);print(hashlib.sha256(out).hexdigest(),len(out))
