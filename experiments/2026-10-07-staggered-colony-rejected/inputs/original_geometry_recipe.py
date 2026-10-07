"""Minimal archived original geometry body, read by replay_thickets.py.
No scene files, textures, absolute paths or Blender scene setup are needed.
The original seed/RNG prelude is reproduced in replay_thickets.py; the exact baseline GLB position sets are the acceptance gate.
"""
import random
from math import sin,cos,pi
from mathutils import Vector

def tint(c,f):return tuple(max(.008,min(.8,v*f)) for v in c)
def tube(m,start,end,r0,r1,col,tip=False):
 a=Vector(start);b=Vector(end);direction=(b-a).normalized();across=direction.cross(Vector((0,0,1)))
 if across.length<.08:across=direction.cross(Vector((0,1,0)))
 across.normalize();up=direction.cross(across).normalized();bend=across*random.uniform(-.025,.025)+up*random.uniform(-.018,.018);rows=[]
 # Blunt pale terminal tip, not a long needle or white branch.
 for j,t in enumerate([0,.22,.46,.7,.88,.96,1.]):
  p=a+(b-a)*t+bend*sin(t*pi);rad=(r0*(1-t)+r1*t)*(1 if t<1 else .38)
  color=tuple(col[k]*(1-max(0,(t-.88)/.12)*.9)+(.70,.67,.50)[k]*max(0,(t-.88)/.12)*.9 for k in range(3)) if tip else col
  row=[]
  for k in range(10):
   q=p+rad*(cos(2*pi*k/10)*across+sin(2*pi*k/10)*up);row.append(m.vert(q,tint(color,.92+.08*sin(k*3+j))))
  rows.append(row)
 for j in range(len(rows)-1):
  for k in range(10):m.face(rows[j][k],rows[j][(k+1)%10],rows[j+1][(k+1)%10],rows[j+1][k])
 m.face(*reversed(rows[0]));m.face(*rows[-1])

def shoot(m,start,direction,length,rad,depth,col):
 d=Vector(direction).normalized();end=Vector(start)+d*length;tube(m,start,end,rad,rad*.80,col,depth==0)
 if depth:
  # Forks have differing length, azimuth, and angles, unlike radial garden symmetry.
  for k in range(2 if random.random()<.8 else 3):
   angle=random.uniform(0,2*pi);side=Vector((cos(angle),sin(angle),random.uniform(-.10,.22)));nd=(d*.73+side*.68).normalized()
   if nd.z<.1:nd.z=.1;nd.normalize()
   st=Vector(start)+(end-Vector(start))*(random.uniform(.66,.93) if k else 1.)
   shoot(m,st,nd,length*random.uniform(.60,.82),max(.009,rad*.77),depth-1,col)

def boulder(m,c,s,col):
 rows=[];M=24;N=48
 for j in range(M+1):
  th=.005+(pi-.01)*j/M;row=[]
  for k in range(N):
   ph=k*2*pi/N;u=sin(th)*cos(ph);v=sin(th)*sin(ph);w=cos(th)
   f=1+.11*sin(u*7+v*3)*cos(w*8-u*2)+.06*sin(v*15+w*11)+.025*sin(u*33-v*21+w*14)
   mott=.76+.12*sin(u*9+v*14+w*8)+.08*sin(u*31-v*21)+.10*w
   row.append(m.vert((c[0]+s[0]*u*f,c[1]+s[1]*v*f,c[2]+s[2]*w*f),tint(col,mott)))
  rows.append(row)
 for j in range(M):
  for k in range(N):m.face(rows[j][k],rows[j][(k+1)%N],rows[j+1][(k+1)%N],rows[j+1][k])
 m.face(*reversed(rows[0]));m.face(*rows[-1])

# Irregular contiguous: end of original tube/shape function body
centers=[(-4.5,-1.0),(-2.9,-1.7),(-.5,-.7),(1.1,-1.8),(2.7,-.8),(4.6,.0),(-5.0,1.2),(-3.3,.5),(-1.7,1.0),(.2,1.4),(2.0,.8),(3.8,2.0),(-4.2,3.1),(-2.4,3.3),(-.6,3.2),(1.3,3.3),(2.8,4.1),(-3.8,5.1),(-1.9,5.3),(.3,5.2),(1.4,6.3),(4.2,3.8)]
