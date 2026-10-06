"""Original deterministic periodic surface maps, no source imagery or external assets.
Coral: randomly scattered shallow cup-shaped corallites and finer micropores.
Rock: multiscale Fourier limestone grain plus irregular pitting.
Sand: warped periodic ripples with fine grains. Normal convention: OpenGL +Y.
"""
import numpy as np
from PIL import Image
import os,json,hashlib
from pathlib import Path
P=str(Path(__file__).resolve().parent/'modeling'/'inputs');os.makedirs(P+'/textures',exist_ok=True)
N=1024;rng=np.random.default_rng(240601);v,u=np.mgrid[0:N,0:N]/N

def noise(band,count):
 a=np.zeros((N,N))
 for _ in range(count):
  x,y=rng.integers(-band,band+1,2);a+=np.sin(2*np.pi*(x*u+y*v)+rng.uniform(0,2*np.pi))
 return a/np.sqrt(count)
def pores(count,small,large):
 a=np.zeros((N,N))
 for _ in range(count):
  x,y=rng.random(2);r=rng.uniform(small,large);dx=np.minimum(abs(u-x),1-abs(u-x));dy=np.minimum(abs(v-y),1-abs(v-y));d=(dx*dx+dy*dy)/(r*r)
  a+=-.60*np.exp(-d*2)+.12*np.exp(-((np.sqrt(d)-1.0)/.23)**2)
 return a
stats={}
for name in ['coral','limestone','sand']:
 if name=='coral':
  h=pores(640,.003,.010)+.024*noise(90,32)+.03*noise(15,22);rough=np.clip(.68+.09*noise(9,30)+h*.12,.45,.91);strength=15
 elif name=='limestone':
  h=.22*noise(5,24)+.11*noise(18,32)+.055*noise(65,40)+pores(190,.003,.025);rough=np.clip(.84+.055*noise(10,26),.64,.97);strength=22
 else:
  h=.19*np.sin(2*np.pi*(v*8+.13*np.sin(u*2*np.pi*2)+.05*np.sin(u*2*np.pi*5)))+.035*noise(170,54);rough=np.clip(.85+.045*noise(120,35),.68,.98);strength=16
 dx=(np.roll(h,-1,1)-np.roll(h,1,1))*.5*strength;dy=(np.roll(h,-1,0)-np.roll(h,1,0))*.5*strength
 norm=np.stack([-dx,dy,np.ones_like(h)],axis=-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
 for kind,a in [('normal',norm*.5+.5),('roughness',rough)]:
  pixels=np.round(np.clip(a,0,1)*255).astype('uint8');path=P+'/textures/'+name+'_'+kind+'.png';Image.fromarray(pixels).save(path)
  stats[name+'_'+kind]={'size':[N,N],'min':int(pixels.min()),'max':int(pixels.max()),'stddev':float(pixels.std()),'sha256':hashlib.sha256(open(path,'rb').read()).hexdigest()}
json.dump({'original':True,'seed':240601,'generator':'generate_textures.py','normal_convention':'OpenGL tangent-space +Y','maps':stats},open(P+'/texture-provenance.json','w'),indent=2)
