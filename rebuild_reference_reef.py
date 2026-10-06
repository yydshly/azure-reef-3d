import bpy,bmesh,math,random,os,json
from mathutils import Vector
from math import sin,cos,pi
from pathlib import Path
ROOT=Path(__file__).resolve().parent
P=str(ROOT/'artifacts'/'reference');os.makedirs(P,exist_ok=True);random.seed(932)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modeling'/'inputs'/'seed-reef.blend'))
for o in list(bpy.context.scene.objects):
 if o.type=='MESH' and not o.name.startswith(('fish_','Sand_')):bpy.data.objects.remove(o,do_unlink=True)
for me in list(bpy.data.meshes):
 if me.users==0:bpy.data.meshes.remove(me)
mats={}
for name in ['coral','limestone','sand']:
 m=bpy.data.materials.new(name.title()+' | reference-led porous PBR');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');vc=n.new('ShaderNodeVertexColor');vc.layer_name='ReefColor';l.new(vc.outputs['Color'],bs.inputs['Base Color'])
 uv=n.new('ShaderNodeUVMap');uv.uv_map='SurfaceUV'
 for kind in ['normal','roughness']:
  t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'modeling'/'inputs'/'textures'/(name+'_'+kind+'.png')),check_existing=True);t.image.colorspace_settings.name='Non-Color';t.extension='REPEAT';l.new(uv.outputs['UV'],t.inputs['Vector'])
  if kind=='normal':
   nm=n.new('ShaderNodeNormalMap');nm.uv_map='SurfaceUV';nm.inputs['Strength'].default_value={'coral':.48,'limestone':.7,'sand':.35}[name];l.new(t.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs['Normal'],bs.inputs['Normal'])
  else:l.new(t.outputs['Color'],bs.inputs['Roughness'])
 mats[name]=m
class Mesh:
 def __init__(self,name,mat):self.name=name;self.mat=mat;self.v=[];self.f=[];self.c=[]
 def vert(self,p,c):self.v.append(tuple(p));self.c.append((*c[:3],1));return len(self.v)-1
 def face(self,*f):self.f.append(f)
 def finish(self):
  me=bpy.data.meshes.new(self.name);me.from_pydata(self.v,[],self.f);me.update();o=bpy.data.objects.new(self.name,me);bpy.context.collection.objects.link(o);me.materials.append(mats[self.mat]);ca=me.color_attributes.new(name='ReefColor',type='FLOAT_COLOR',domain='POINT')
  for d,c in zip(ca.data,self.c):d.color=c
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
  for p in me.polygons:p.use_smooth=True
  return o

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
# Irregular contiguous, low-relief hardbottom; no symmetric rock garden or aisle.
m=Mesh('Hardbottom_Low_Irregular_Limestone','limestone')
# Preserve the reviewed colony RNG sequence while replacing substrate topology.
for i in range(140):
 x=random.uniform(-6.5,6);y=random.uniform(-4.5,7.5)
 if ((x+.4)/6.5)**2+((y-1.3)/7.)**2>1:continue
 if ((x+1.1)/1.3)**2+((y+2.7)/.9)**2<1 or ((x-3.5)/1.4)**2+((y-4.5)/1.5)**2<1:continue
 random.uniform(.42,1.1);random.uniform(.65,1.25);random.uniform(.14,.28);random.choice([0,1,2])
# One continuous irregular eroded surface avoids repeated flattened rock disks.
N=155
for j in range(N+1):
 y=-5.4+14*j/N
 for i in range(N+1):
  x=-7.5+15*i/N
  edge=1-((x+.3)/6.9)**2-((y-1.3)/7.4)**2+.07*sin(x*2.1+y*1.7)+.04*sin(y*4.3-x)
  hole1=((x+1.1)/1.15)**2+((y+2.7)/.8)**2-1
  hole2=((x-3.7)/1.15)**2+((y-4.5)/1.4)**2-1
  mask=max(0,min(1,edge*5,hole1*2,hole2*2))
  relief=.18+.075*sin(x*3.9+y*2.2)*sin(y*4.5-x*1.7)+.04*sin(x*11+y*7)+.017*sin(x*31-y*23)
  z=-.19+mask*relief
  mott=.80+.16*sin(x*3.1+y*2.6)*sin(y*4.7-x)+.10*sin(x*17+y*13)
  m.vert((x,y,z),tint((.19,.195,.13),mott))
for j in range(N):
 for i in range(N):
  a=j*(N+1)+i;m.face(a,a+1,a+N+2,a+N+1)
m.finish()
# Few low, irregular earthy coral mounds. They do not pretend to have brain-coral grooves.
m=Mesh('Coral_Low_Irregular_Encrusting_Mounds','coral')
for x,y,s in [(-4.7,-2.8,.62),(3.7,-2.1,.81),(-.6,1.6,.58),(3.8,5.8,.77),(-4.5,4,.52)]:
 for j in range(3):boulder(m,(x+random.uniform(-.25,.25),y+random.uniform(-.25,.25),.06),(s*random.uniform(.65,1),s*random.uniform(.5,.88),s*random.uniform(.27,.45)),random.choice([(.20,.18,.09),(.145,.17,.09),(.21,.20,.12)]))
m.finish()
# Closely spaced, unequal thickets based on the observed NOAA staghorn growth habit.
centers=[(-4.5,-1.0),(-2.9,-1.7),(-.5,-.7),(1.1,-1.8),(2.7,-.8),(4.6,.0),(-5.0,1.2),(-3.3,.5),(-1.7,1.0),(.2,1.4),(2.0,.8),(3.8,2.0),(-4.2,3.1),(-2.4,3.3),(-.6,3.2),(1.3,3.3),(2.8,4.1),(-3.8,5.1),(-1.9,5.3),(.3,5.2),(1.4,6.3),(4.2,3.8)]
colony_stats=[]
for idx,(cx,cy) in enumerate(centers):
 m=Mesh('Coral_Staghorn_Thicket_%02d'%idx,'coral');size=random.uniform(.8,1.22);basecol=random.choice([(.26,.205,.080),(.22,.185,.07),(.29,.245,.105),(.19,.17,.065)])
 for j in range(random.randint(13,21)):
  a=random.random()*2*pi;rr=random.uniform(.07,.55)*size;st=(cx+cos(a)*rr,cy+sin(a)*rr,random.uniform(-.02,.10));direction=Vector((cos(a)*random.uniform(.4,1.05),sin(a)*random.uniform(.4,1.05),random.uniform(.7,1.35)))
  shoot(m,st,direction,random.uniform(.44,.64)*size,random.uniform(.021,.033),2,tint(basecol,random.uniform(.8,1.12)))
 ob=m.finish();height=max(v.co.z for v in ob.data.vertices)-min(v.co.z for v in ob.data.vertices)
 if height>1.4:
  for v in ob.data.vertices:v.co.z*=1.4/height
 colony_stats.append({'name':ob.name,'bbox_height':max(v.co.z for v in ob.data.vertices)-min(v.co.z for v in ob.data.vertices)})
# Existing sand geometry remains 3D, but the color is restrained.
for o in bpy.context.scene.objects:
 if o.type=='EMPTY' and o.name.startswith('fish_'):o.scale*=.48
 if o.type!='MESH':continue
 if o.name.startswith('fish_'):
  ca=o.data.color_attributes.active_color
  if ca:
   for d in ca.data:
    c=d.color;lum=.24*c[0]+.58*c[1]+.18*c[2];d.color=(lum*.66+c[0]*.17,lum*.68+c[1]*.14,lum*.62+c[2]*.13,c[3])
  continue
 if o.name.startswith('Sand_'):
  o.data.materials.clear();o.data.materials.append(mats['sand']);ca=o.data.color_attributes.active_color
  if ca:
   ca.name='ReefColor'
   for d in ca.data:d.color=(.31,.285,.20,1)
 typ='sand' if o.name.startswith('Sand_') else 'limestone' if o.name.startswith('Hardbottom') else 'coral'
 me=o.data;uv=me.uv_layers.active or me.uv_layers.new(name='SurfaceUV');uv.name='SurfaceUV';scale={'sand':.9,'limestone':1.3,'coral':2.4}[typ]
 for poly in me.polygons:
  axis=max(range(3),key=lambda i:abs(poly.normal[i]));dims=[(1,2),(0,2),(0,1)][axis];sign=1 if poly.normal[axis]>=0 else -1
  for li in poly.loop_indices:
   co=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[dims[0]]*scale*sign,co[dims[1]]*scale)
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.data.name=o.name
 o.select_set(o.type in {'MESH','EMPTY'})
bpy.ops.export_scene.gltf(filepath=P+'/reef-garden-reference.glb',export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT')
bpy.ops.wm.save_as_mainfile(filepath=P+'/reef-garden-reference.blend')
json.dump({'seed':932,'reference_urls':['https://www.fisheries.noaa.gov/species/staghorn-coral','https://sanctuaries.noaa.gov/news/press/mission-iconic-reefs/'],'scope':'Interpretive Florida/Caribbean shallow staghorn-dominated patch edge; not a named-site reconstruction or validated species model','removed':['all tiered plates','all old thick candy-colored branching corals','old blue/gold brain balls','seagrass','symmetrical rock islands'],'retained':'Original sand meshes and generic fish geometry; fish size reduced to 48% and palette desaturated','colony_stats':colony_stats,'textures':'Original procedural embedded PBR normal/roughness maps; see texture-provenance.json','offline_only':'Original camera/lights/compositor mist preserved; not embedded in GLB'},open(P+'/reference-audit.json','w'),indent=2)
print('REFERENCE_REBUILD_EXPORT_COMPLETE',flush=True)
