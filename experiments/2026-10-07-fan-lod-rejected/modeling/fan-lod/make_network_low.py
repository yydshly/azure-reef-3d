from pathlib import Path
import numpy as np,json
from scipy.spatial import Voronoi
rng=np.random.default_rng(71028)
def inside(p):
 x,z=p;t=(z-.15)/1.20
 if not .025<t<.995:return False
 center=.045*np.sin(t*3.8)+.025*t
 w=1.55*np.sin(np.pi*t)**.58*min(1,t*4)
 asym=.89+.06*np.cos(t*6) if x<center else 1.02+.06*np.sin(t*5)
 return abs(x-center)<w*.5*asym
points=[]
while len(points)<480:
 p=[rng.uniform(-.84,.89),rng.uniform(.17,1.35)]
 if inside(p):points.append(p)
v=Voronoi(points);edges=[]
for a,b in v.ridge_vertices:
 if a<0 or b<0:continue
 p,q=v.vertices[a],v.vertices[b]
 if not inside(p) or not inside(q):continue
 if np.linalg.norm(p-q)>.2034:continue
 edges.append([p.tolist(),q.tolist()])
out=Path(__file__).resolve().parent/'fan-network-low.json';out.write_text(json.dumps({'seed':71028,'note':'Original irregular reticulate appearance network, not a biological growth simulation','edges':edges},separators=(',',':')));print(len(edges),'edges',out)
