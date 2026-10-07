import json,struct,hashlib
from pathlib import Path
import numpy as np
SOURCE=Path(__file__).resolve().parents[2]/'source-model.glb'
SHA='c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd'
def read(path):
 r=Path(path).read_bytes();assert r[:4]==b'glTF';n=struct.unpack_from('<I',r,12)[0];return r,json.loads(r[20:20+n]),bytearray(r[28+n:])
def acc(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];assert 'byteStride' not in v
 w={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];d={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]
 return np.frombuffer(b,dtype=d,count=a['count']*w,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,w).copy()
def geom(g,b,mesh=59):
 pr=g['meshes'][mesh]['primitives'][0];return {k:acc(g,b,v) for k,v in pr['attributes'].items()}|{'tri':acc(g,b,pr['indices']).reshape(-1,3)}
def append(g,b,a,type,component=5126):
 b.extend(b'\0'*((-len(b))%4));start=len(b);a=np.asarray(a,dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[component]);b.extend(a.tobytes());v=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':a.nbytes});i=len(g['accessors']);d={'bufferView':v,'componentType':component,'count':len(a),'type':type};
 if type=='VEC3':d.update(min=a.min(0).tolist(),max=a.max(0).tolist())
 g['accessors'].append(d);return i

def save(g,b,path):
 g['buffers'][0]['byteLength']=len(b);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);b+=b'\0'*((-len(b))%4);r=struct.pack('<4sII',b'glTF',2,28+len(j)+len(b))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(b),b'BIN\0')+b;Path(path).write_bytes(r)
