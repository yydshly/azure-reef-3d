"""Deterministic original geometry/branch-graph replay. Runs inside Blender."""
import math,random,ast
from math import sin,cos,pi
from mathutils import Vector
class Mesh:
 def __init__(self,name,mat):self.name=name;self.mat=mat;self.v=[];self.f=[];self.c=[];self.tubes=[]
 def vert(self,p,c):self.v.append(tuple(p));self.c.append((*c[:3],1));return len(self.v)-1
 def face(self,*f):self.f.append(f)
def replay(recipe_path):
 script=recipe_path.read_text();random.seed(932)
 ns={'random':random,'Vector':Vector,'sin':sin,'cos':cos,'pi':pi,'Mesh':Mesh}
 exec(script[script.index('def tint'):script.index('# Irregular contiguous')],ns)
 original_tube=ns['tube'];original_shoot=ns['shoot'];stack=[]
 def tube(m,start,end,r0,r1,col,tip=False):
  ident=len(m.tubes);stack[-1]['tube']=ident;m.tubes.append({'start':list(start),'end':list(end),'r0':r0,'r1':r1,'tip':tip,'first_vertex':len(m.v),'first_face':len(m.f),'parent':stack[-2]['tube']if len(stack)>1 else None,'depth':stack[-1]['depth']});original_tube(m,start,end,r0,r1,col,tip)
 def shoot(m,start,direction,length,rad,depth,col):
  stack.append({'depth':depth,'tube':None});original_shoot(m,start,direction,length,rad,depth,col);stack.pop()
 ns['tube']=tube;ns['shoot']=shoot;boulder=ns['boulder'];tint=ns['tint']
 for i in range(140):
  x=random.uniform(-6.5,6);y=random.uniform(-4.5,7.5)
  if ((x+.4)/6.5)**2+((y-1.3)/7.)**2>1:continue
  if ((x+1.1)/1.3)**2+((y+2.7)/.9)**2<1 or ((x-3.5)/1.4)**2+((y-4.5)/1.5)**2<1:continue
  random.uniform(.42,1.1);random.uniform(.65,1.25);random.uniform(.14,.28);random.choice([0,1,2])
 m=Mesh('mound','coral')
 for x,y,s in [(-4.7,-2.8,.62),(3.7,-2.1,.81),(-.6,1.6,.58),(3.8,5.8,.77),(-4.5,4,.52)]:
  for j in range(3):boulder(m,(x+random.uniform(-.25,.25),y+random.uniform(-.25,.25),.06),(s*random.uniform(.65,1),s*random.uniform(.5,.88),s*random.uniform(.27,.45)),random.choice([(.20,.18,.09),(.145,.17,.09),(.21,.20,.12)]))
 centers=next(ast.literal_eval(n.value)for n in ast.parse(script).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='centers'for t in n.targets))
 results=[]
 for idx,(cx,cy) in enumerate(centers):
  m=Mesh('Coral_Staghorn_Thicket_%02d'%idx,'coral');size=random.uniform(.8,1.22);basecol=random.choice([(.26,.205,.080),(.22,.185,.07),(.29,.245,.105),(.19,.17,.065)])
  for j in range(random.randint(13,21)):
   a=random.random()*2*pi;rr=random.uniform(.07,.55)*size;st=(cx+cos(a)*rr,cy+sin(a)*rr,random.uniform(-.02,.10));direction=Vector((cos(a)*random.uniform(.4,1.05),sin(a)*random.uniform(.4,1.05),random.uniform(.7,1.35)))
   shoot(m,st,direction,random.uniform(.44,.64)*size,random.uniform(.021,.033),2,tint(basecol,random.uniform(.8,1.12)))
  m.raw_vertices=list(m.v);h=max(v[2]for v in m.v)-min(v[2]for v in m.v);m.height_scale=1.4/h if h>1.4 else 1.0
  if h>1.4:
   vecs=[Vector(v)for v in m.v]
   for v in vecs:v.z*=m.height_scale
   m.v=[tuple(v)for v in vecs]
  results.append(m)
 return results

def correct(m):
 # Fixed algorithm already reviewed on specimen01. All calculations begin in the source's unscaled coordinates.
 source_vertices=list(m.v);raw=list(m.raw_vertices);remove_faces=set();extra=[];joints=[];changed=[]
 for pi,parent in enumerate(m.tubes):
  if parent['tip']:continue
  children=[(ci,c)for ci,c in enumerate(m.tubes)if c['parent']==pi and (Vector(c['start'])-Vector(parent['end'])).length<1e-6];assert len(children)==1
  ci,child=children[0];center=Vector(parent['end']);pd=(center-Vector(parent['start'])).normalized();cd=(Vector(child['end'])-Vector(child['start'])).normalized();rot=pd.rotation_difference((pd+cd).normalized());pr=[parent['first_vertex']+60+k for k in range(10)];cr=[child['first_vertex']+10+k for k in range(10)]
  for vi in pr:
   # Match the reviewed operation order exactly: restore radius, then rotate.
   restored=center+(Vector(raw[vi])-center)/.38;raw[vi]=tuple(center+rot@(restored-center));q=Vector(raw[vi]);q.z*=m.height_scale;m.v[vi]=tuple(q);changed.append(vi)
  cc=sum((Vector(raw[i])for i in cr),Vector())/10
  shift=min(range(10),key=lambda shift:sum(((Vector(raw[pr[k]])-center).normalized()-(Vector(raw[cr[(k+shift)%10]])-cc).normalized()).length_squared for k in range(10)))
  for k in range(10):extra.append((pr[k],pr[(k+1)%10],cr[(k+1+shift)%10],cr[(k+shift)%10]))
  remove_faces.update([parent['first_face']+61,child['first_face']+60]);remove_faces.update(child['first_face']+k for k in range(10));joints.append({'parent':pi,'continuation_child':ci})
 m.f=[f for fi,f in enumerate(m.f)if fi not in remove_faces]+extra
 assert all(m.v[k]==source_vertices[k]for t in m.tubes if t['tip']for k in range(t['first_vertex']+10,t['first_vertex']+70))
 assert all(m.v[k]==source_vertices[k]for t in m.tubes if t['parent']is None for k in range(t['first_vertex'],t['first_vertex']+10))
 return {'name':m.name,'source_tubes':len(m.tubes),'basal_shoots':sum(t['parent']is None for t in m.tubes),'terminal_segments':sum(t['tip']for t in m.tubes),'joints_corrected':len(joints),'changed_vertices':len(changed),'triangles':sum(len(f)-2 for f in m.f),'height_scale_preserved':m.height_scale,'all_terminal_tips_and_basal_roots_unchanged':True,'bbox_before':[[min(v[k]for v in source_vertices)for k in range(3)],[max(v[k]for v in source_vertices)for k in range(3)]],'bbox_after':[[min(v[k]for v in m.v)for k in range(3)],[max(v[k]for v in m.v)for k in range(3)]],'joints':joints}
