"""Original restrained relief study. Numpy/Pillow; no photographs or scan-derived pixels.
Per-face frozen UVs cannot align motifs to every branch. No biological scale claim.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'textures');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
N=1024;rng=np.random.default_rng(20261007);h=np.zeros((N,N),np.float64)
# Dense, softly raised, open rims. The low, broad back of each motif makes a
# shallow crescent, rather than a closed crater with a deep central depression.
for iy in range(31):
 for ix in range(31):
  cx=(ix+rng.uniform(.12,.88))*N/31;cy=(iy+rng.uniform(.12,.88))*N/31
  rx=rng.uniform(7.,9.5);ry=rx*rng.uniform(1.05,1.4);angle=rng.uniform(0,2*np.pi)
  lim=int(np.ceil(3*ry));xx=np.arange(int(cx)-lim,int(cx)+lim+1);yy=np.arange(int(cy)-lim,int(cy)+lim+1);x,y=np.meshgrid(xx-cx,yy-cy)
  qx=(x*np.cos(angle)+y*np.sin(angle))/rx;qy=(-x*np.sin(angle)+y*np.cos(angle))/ry
  radius=np.sqrt(qx*qx+qy*qy);lip=np.exp(-((radius-.64)/.30)**2)
  opening=np.clip(.62+.50*qy,0,1);body=.25*np.exp(-(qx*qx+qy*qy)*1.8)
  motif=(lip*opening+body)*rng.uniform(.75,1.12)
  h[np.ix_(yy%N,xx%N)]+=motif
# Smooth low-amplitude between-cup irregularity, avoiding sharp granular sparkle.
v,u=np.mgrid[0:N,0:N]/N;grain=np.zeros_like(h)
for _ in range(28):
 kx,ky=rng.integers(-52,53,2);grain+=np.sin(2*np.pi*(kx*u+ky*v)+rng.uniform(0,2*np.pi))/np.sqrt(28)
h+=.018*grain
dx=(np.roll(h,-1,1)-np.roll(h,1,1))*.5;dy=(np.roll(h,-1,0)-np.roll(h,1,0))*.5
rawpeak=np.sqrt(dx*dx+dy*dy).max();report={'seed':20261007,'size':[N,N],'normal_convention':'OpenGL tangent space +Y; image row derivative reversed','texture_sources':'Original procedural functions only; no scan or photo sampling','biological_limit':'Qualitative raised radial-corallite cue only. Frozen per-face UVs cannot ensure branch-tip orientation; texture spacing is an art choice, not a calibrated biological measurement.','variants':{}}
for name,peak in [('fine',1.05),('soft',1.60)]:
 scale=peak/rawpeak;nn=np.stack([-dx*scale,dy*scale,np.ones_like(h)],axis=-1);nn/=np.linalg.norm(nn,axis=-1,keepdims=True)
 normal=np.round((nn*.5+.5)*255).astype(np.uint8)
 rough=np.clip(.715+.014*np.tanh(grain)+.012*np.tanh(h-.25),.68,.75)
 rr=np.round(rough*255).astype(np.uint8);packed=np.stack([np.full_like(rr,255),rr,np.zeros_like(rr)],axis=-1)
 for kind,pixels in [('normal',normal),('roughness',rr),('metallic-roughness',packed)]:Image.fromarray(pixels).save(a.out/(name+'-'+kind+'.png'))
 report['variants'][name]={'raw_max_tangent_slope':peak,'fixed_source_normal_scale':.47999998927116394,'fixed_render_scale':.35999999195337296,'effective_max_slope':peak*.35999999195337296,'roughness_min':int(rr.min())/255,'roughness_max':int(rr.max())/255,'maps':{k:{'sha256':hashlib.sha256((a.out/(name+'-'+k+'.png')).read_bytes()).hexdigest(),'bytes':(a.out/(name+'-'+k+'.png')).stat().st_size}for k in ['normal','roughness','metallic-roughness']}}
(a.out.parent/'texture-provenance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
