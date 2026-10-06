import bpy, bmesh, math, random, json, os
from mathutils import Vector
from math import sin,cos,pi
random.seed(41)
from pathlib import Path
OUT=str(Path(__file__).resolve().parent/'artifacts'/'legacy-base');os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
# Every visible reef form is an original closed mesh. Vertex colors are portable GLTF attributes.
mats={}
def material(name,rough=.75):
 m=bpy.data.materials.new(name);m.use_nodes=True
 n=m.node_tree.nodes; bs=n.get('Principled BSDF'); a=n.new('ShaderNodeVertexColor');a.layer_name='ReefColor';m.node_tree.links.new(a.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=rough
 mats[name]=m;return m
for name,r in [('Living coral',.72),('Limestone',.91),('Rippling sand',.94),('Seagrass',.62)]:material(name,r)
class Mesh:
 def __init__(self,name,mat):self.name=name;self.mat=mat;self.v=[];self.f=[];self.c=[]
 def vert(self,p,c):self.v.append(tuple(p));self.c.append((*c[:3],1));return len(self.v)-1
 def face(self,*f):self.f.append(f)
 def finish(self):
  me=bpy.data.meshes.new(self.name);me.from_pydata(self.v,[],self.f);me.update();ob=bpy.data.objects.new(self.name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(mats[self.mat]);col=me.color_attributes.new(name='ReefColor',type='FLOAT_COLOR',domain='POINT')
  for i,c in enumerate(self.c):col.data[i].color=c
  for p in me.polygons:p.use_smooth=True
  return ob

def tint(c,f):return tuple(min(.95,max(.015,x*f)) for x in c)
def tube(m,pts,radii,color,sides=9):
 starts=[]
 for j,p in enumerate(pts):
  p=Vector(p);t=Vector(pts[min(j+1,len(pts)-1)])-Vector(pts[max(j-1,0)]);t.normalize();a=t.cross(Vector((0,0,1)))
  if a.length<.05:a=t.cross(Vector((1,0,0)))
  a.normalize();b=t.cross(a).normalized();ids=[]
  for k in range(sides):
   ang=k*2*pi/sides; rr=radii[j]*(1+.06*sin(k*4+j));q=p+rr*(cos(ang)*a+sin(ang)*b);ids.append(m.vert(q,tint(color,.77+.3*j/len(pts)+.06*sin(k*3+j))))
  starts.append(ids)
 for j in range(len(starts)-1):
  for k in range(sides):m.face(starts[j][k],starts[j][(k+1)%sides],starts[j+1][(k+1)%sides],starts[j+1][k])
 m.face(*reversed(starts[0]));m.face(*starts[-1])

def branch(m,base,vec,length,rad,depth,color):
 vec=Vector(vec).normalized();base=Vector(base);bend=Vector((random.uniform(-.3,.3),random.uniform(-.3,.3),.12));pts=[]
 for j in range(7):
  t=j/6;pts.append(base+vec*length*t+bend*length*t*t)
 radii=[rad*(1-.48*j/6) for j in range(7)]
 tipdir=(pts[-1]-pts[-2]).normalized();last=pts[-1].copy()
 for u in [.4,.75,.98]:pts.append(last+tipdir*rad*.52*u);radii.append(rad*.52*(1-u*u)**.5)
 tube(m,pts,radii,color,9)
 if depth:
  for t in [.45,.72,1.]:
   pos=base+vec*length*t+bend*length*t*t;ang=random.uniform(0,2*pi);nv=(vec*.32+Vector((cos(ang)*1.0,sin(ang)*1.0,random.uniform(.25,.65)))).normalized();branch(m,pos,nv,length*random.uniform(.5,.72),rad*.54,depth-1,color)

def colony(name,x,y,z,s,color):
 m=Mesh(name,'Living coral')
 for i in range(6):
  a=i*2*pi/6;branch(m,(x+.24*s*cos(a),y+.24*s*sin(a),z),(cos(a)*.85,sin(a)*.85,.85),s*random.uniform(.75,1.03),s*.15,2 if s<.6 else 3,color)
 return m.finish()

def boulder(m,center,scale,color,brain=False):
 N=112 if brain else 32;M=66 if brain else 20; rows=[]
 for j in range(M+1):
  th=.002+(pi-.004)*j/M;row=[]
  for k in range(N):
   ph=2*pi*k/N;u=sin(th)*cos(ph);v=sin(th)*sin(ph);w=cos(th)
   noise=(.045 if brain else .16)*sin(7*u+3*v)*cos(8*w-2*u)+(.025 if brain else .085)*sin(17*v+10*w)+(.0 if brain else .06)*sin(29*u-18*v+9*w)
   ridges=(.032*(.5+.5*sin(39*th+5*sin(8*ph)*sin(th)+3*sin(11*th+2*cos(ph)))) if brain else 0)
   r=1+noise+ridges;col=tint(color,(.73+.27*(ridges/.032) if brain else .7+.15*w+noise*1.3));row.append(m.vert((center[0]+scale[0]*u*r,center[1]+scale[1]*v*r,center[2]+scale[2]*w*r),col))
  rows.append(row)
 for j in range(M):
  for k in range(N):m.face(rows[j][k],rows[j][(k+1)%N],rows[j+1][(k+1)%N],rows[j+1][k])
 m.face(*reversed(rows[0]));m.face(*rows[-1])

def plates(name,c,s,col):
 m=Mesh(name,'Living coral')
 for layer in range(5):
  rad=s*(1-.135*layer);cx=c[0]+.13*sin(layer*2);cy=c[1]+.12*cos(layer*2);z=c[2]+layer*.24*s
  rows=[];N=128;R=13
  # A closed, thick, radially corrugated foliose cup, with distinct upper and underside.
  for side in [0,1]:
   sideRows=[]
   for j in range(R+1):
    t=.018+.982*j/R;ids=[]
    for k in range(N):
     a=2*pi*k/N;r=rad*t*(1+.08*sin(7*a+layer)+.036*sin(17*a));zz=z+.32*s*t*t+(.09*sin(12*a+2*t)+.03*sin(27*a))*s*t**3+.02*sin(t*65+a*5)*s*t-.065*s*side
     ids.append(m.vert((cx+r*cos(a),cy+r*sin(a),zz),tint(col,(.73+.3*t+.07*sin(12*a))*(.68 if side else 1))))
    sideRows.append(ids)
   rows.append(sideRows)
  for side in [0,1]:
   for j in range(R):
    for k in range(N):
     f=(rows[side][j][k],rows[side][j][(k+1)%N],rows[side][j+1][(k+1)%N],rows[side][j+1][k]);m.face(*(f if side==0 else reversed(f)))
  for k in range(N):m.face(rows[0][-1][k],rows[1][-1][k],rows[1][-1][(k+1)%N],rows[0][-1][(k+1)%N]);m.face(rows[1][0][k],rows[0][0][k],rows[0][0][(k+1)%N],rows[1][0][(k+1)%N])
 return m.finish()
# Continuous undulating sand has modeled ripple relief.
m=Mesh('Sand_Rippled_32m','Rippling sand');N=115
for j in range(N+1):
 y=-16+32*j/N
 for i in range(N+1):
  x=-16+32*i/N;z=-.14+.024*sin(y*9+.7*sin(x*.9))+.018*sin(x*1.6+y*.7);m.vert((x,y,z),tint((.67,.63,.45),.95+.055*sin(y*9+.7*sin(x*.9))))
for j in range(N):
 for i in range(N):a=j*(N+1)+i;m.face(a,a+1,a+N+2,a+N+1)
m.finish()
m=Mesh('Rock_Islands_Limestone','Limestone')
for x,y,s in [(-3,0,1.7),(-4,2,1.2),(-2,3,1.4),(3,0,1.6),(4,2,1.4),(2.5,4,1.3),(-4,-2,.85),(4,-2,.9)]:
 boulder(m,(x,y,.3*s),(s*.86,s*.71,.42*s),(.22,.34,.28))
 for k in range(3):boulder(m,(x+random.uniform(-s,s),y+random.uniform(-s,s),.1),(.4,.5,.32),(.35,.44,.36))
m.finish()
colony('Coral_Branch_Peach_Left',-3.8,.1,.85,1.25,(.93,.38,.23))
colony('Coral_Branch_Lavender_Right',3.5,1,.9,1.25,(.52,.36,.73))
colony('Coral_Branch_Cream_BackLeft',-2.6,3.2,.75,.9,(.77,.71,.46))
colony('Coral_Branch_Rose_BackRight',3.3,4,.7,.85,(.78,.26,.40))
colony('Coral_Branch_Turquoise_Left',-5,2,.45,.68,(.12,.59,.49))
plates('Coral_Plates_Teal_FrontLeft',(-2.5,-1.35,.45),1.05,(.16,.58,.48))
plates('Coral_Plates_Salmon_FrontRight',(2.6,-1.1,.35),1.15,(.85,.39,.29))
plates('Coral_Plates_Lilac_FarLeft',(-4.2,3.2,.4),.85,(.48,.40,.64))
m=Mesh('Coral_Brain_Gold_Colonies','Living coral')
for c,s in [((-4.4,-1.7,.65),(.77,.63,.78)),((4.7,-.1,.72),(.85,.7,.85)),((-1.8,1.4,.73),(.67,.58,.74))]:boulder(m,c,s,(.64,.58,.26),True)
m.finish()
m=Mesh('Coral_Brain_Aqua_Colonies','Living coral')
for c,s in [((1.9,2,.7),(.74,.64,.8)),((-3.6,4.5,.5),(.55,.53,.64))]:boulder(m,c,s,(.17,.50,.46),True)
m.finish()
m=Mesh('Seagrass_Tapered_Blades','Seagrass')
for cl in range(70):
 x=random.choice([-1,1])*random.uniform(2.2,7.5);y=random.uniform(-3.5,6.5)
 for k in range(random.randint(4,7)):
  xx=x+random.uniform(-.17,.17);yy=y+random.uniform(-.17,.17);h=random.uniform(.22,.75);a=random.random()*2*pi;pts=[(xx+cos(a)*h*(j/5)**2*.5,yy+sin(a)*h*(j/5)**2*.5,-.09+h*j/5) for j in range(6)];tube(m,pts,[.028*(1-j/6) for j in range(6)],(.17,.36,.20),4)
m.finish()
# Low, colorful satellite colonies knit the islands together.
for i,(x,y,z,ss,cc) in enumerate([(-4.8,-.9,.15,.53,(.73,.31,.48)),(-1.7,-.3,.1,.5,(.25,.65,.49)),(4.6,-1.4,.1,.5,(.80,.56,.21)),(1.8,3.4,.2,.5,(.38,.42,.77)),(-3,4.2,.15,.55,(.79,.44,.28))]):
 colony('Coral_Compact_Base_%02d'%i,x,y,z,ss,cc)
# Four original anatomically readable reef fish. Local forward +X; parent rotates whole fish.
for idx,(pos,scale,col) in enumerate([((-2.0,-2.1,2.1),.82,(.98,.64,.12)),((2.0,-.4,2.5),.72,(.20,.56,.83)),((-.5,2.9,2.8),.65,(.95,.41,.19)),((4.6,2.7,2.1),.67,(.88,.69,.25))]):
 root=bpy.data.objects.new('fish_%02d'%(idx+1),None);bpy.context.collection.objects.link(root);root.location=pos;root.rotation_euler[2]=[.2,2.6,-.7,3.4][idx];root.scale=(scale,scale,scale)
 m=Mesh(root.name+'_body','Living coral');N=48;M=32;rows=[]
 for j in range(M+1):
  th=.006+(pi-.012)*j/M;x=.57*cos(th);row=[]
  for k in range(N):
   a=2*pi*k/N;r=sin(th);yy=.15*r*sin(a);zz=.32*r*cos(a);stripe=(.30 if sin(x*34+zz*3)> .56 else 1.0);c=tint(col,stripe*(.9+.12*cos(a)));row.append(m.vert((x,yy,zz),c))
  rows.append(row)
 for j in range(M):
  for k in range(N):m.face(rows[j][k],rows[j][(k+1)%N],rows[j+1][(k+1)%N],rows[j+1][k])
 m.face(*rows[0]);m.face(*reversed(rows[-1]));o=m.finish();o.parent=root
 def fin(name,coords,c):
  mm=Mesh(root.name+'_'+name,'Living coral');n=len(coords)
  for s in [-1,1]:
   for x,y,z in coords:mm.vert((x,y+.012*s,z),c)
  mm.face(*reversed(range(n)));mm.face(*range(n,2*n))
  for k in range(n):mm.face(k,(k+1)%n,(k+1)%n+n,k+n)
  ob=mm.finish();ob.parent=root
 fin('tail',[(-.49,0,0),(-.91,0,.28),(-.81,0,0),(-.91,0,-.28)],tint(col,.78))
 fin('dorsal',[(.29,0,.23),(-.27,0,.51),(-.39,0,.22)],tint(col,.83))
 fin('ventral',[(.20,0,-.23),(-.29,0,-.43),(-.36,0,-.20)],tint(col,.7))
 for side in [-1,1]:
  fin('pectoral_'+str(side),[(.14,.12*side,.02),(-.16,.36*side,-.14),(-.15,.12*side,-.13)],tint(col,.83))
  mm=Mesh(root.name+'_eye_'+str(side),'Living coral');boulder(mm,(.38,.098*side,.07),(.061,.027,.061),(.94,.91,.69));boulder(mm,(.396,.122*side,.073),(.032,.012,.035),(.018,.026,.033));oo=mm.finish();oo.parent=root

# Export only reef meshes. No cameras, light cards, water plane, or render backdrop in GLB.
reef=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in reef:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();o.data.update()
for o in bpy.context.scene.objects:o.select_set(o.type in {'MESH','EMPTY'})
bpy.ops.export_scene.gltf(filepath=OUT+'/reef-garden.glb',export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
stats={'objects':{},'coordinate_system':'GLB Y up (Blender Z up converted). Sand -16..16m. Reef passage between x=-1 and x=1 along depth.', 'original_procedural_geometry':True,'portable_materials':'PBR roughness plus ReefColor vertex colors; no texture or external asset dependencies','offline_only':'Studio area lighting and turquoise world atmosphere are Blender render presentation, not embedded lighting in GLB.'}
for o in reef:stats['objects'][o.name]={'vertices':len(o.data.vertices),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)}
stats['total_triangles']=sum(o['triangles'] for o in stats['objects'].values());json.dump(stats,open(OUT+'/geometry-manifest.json','w'),indent=2)
print('GLB_READY',stats['total_triangles'],flush=True)
# Render exactly those meshes from opposing positions; no image replacement.
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=False;sc.render.resolution_x=1100;sc.render.resolution_y=800;sc.render.resolution_percentage=100
sc.world.color=(.1,.1,.1);sc.world.use_nodes=True;sc.world.node_tree.nodes.get('Background').inputs[0].default_value=(.11,.28,.32,1);sc.world.node_tree.nodes.get('Background').inputs[1].default_value=.3
sc.view_settings.view_transform='AgX'
def area(name,pos,power,color,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,1,0))-o.location).to_track_quat('-Z','Y').to_euler()
area('Sun shafts softbox',(-3,-4,10),1600,(1,.91,.69),2.5);area('Warm coral fill',(-7,-6,6),450,(1,.77,.59),8);area('Blue rim',(3,7,8),1300,(.26,.77,1),5)
d=bpy.data.cameras.new('Offline evidence camera');cam=bpy.data.objects.new('Offline evidence camera',d);sc.collection.objects.link(cam);sc.camera=cam;cam.data.lens=45
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/reef-garden.blend')
print('GEOMETRY_REFINED',flush=True)
