"""Author a repeatable light-density pattern from periodic wave slopes.
This is a visual approximation, not calibrated ocean optics or a scientific model.
"""
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
N=512;S=1024
v,u=np.mgrid[0:S,0:S]/S
rng=np.random.default_rng(20261006);dx=np.zeros_like(u);dy=np.zeros_like(v)
for _ in range(9):
 kx,ky=rng.integers(-4,5,2)
 if kx==0 and ky==0:continue
 phase=rng.uniform(0,np.pi*2);amplitude=rng.uniform(.002,.0045)
 slope=np.cos(2*np.pi*(kx*u+ky*v)+phase)*amplitude
 dx+=slope*kx;dy+=slope*ky
x=((u+dx)*N)%N;y=((v+dy)*N)%N
ix=np.floor(x).astype(int);iy=np.floor(y).astype(int);fx=x-ix;fy=y-iy
acc=np.zeros((N,N))
for ox,oy,w in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:np.add.at(acc,((iy+oy)%N,(ix+ox)%N),w)
acc=np.maximum(0,acc/4-.7);acc=np.clip(acc/np.percentile(acc,99.4),0,1)**.8
path=Path(__file__).resolve().parent/'dist'/'assets'/'water-caustics.png'
Image.fromarray((acc*255).astype('uint8')).filter(ImageFilter.GaussianBlur(.55)).save(path)
print(path)
