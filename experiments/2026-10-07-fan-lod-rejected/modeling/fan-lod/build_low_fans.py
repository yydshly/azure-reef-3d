"""Distant 3D fan representation: same stem/major veins and extent profile,
coarser original reticulate network. No billboard or new biological claim.
Usage: blender -b -t 2 --python-exit-code 1 --python build_low_fans.py -- MASTER.blend OUTDIR
"""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,noise
from math import sin,cos,pi
ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:];master=Path(args[0]).resolve();OUT=Path(args[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(master));rock=bpy.data.objects['Shoulder_closed_irregular_skeleton'];fanmat=bpy.data.materials['Pilot_gorgonian_form']
for o in list(bpy.context.scene.objects):
 if o!=rock:bpy.data.objects.remove(o,do_unlink=True)
def roof(x,y):
 ok,p,n,_=rock.ray_cast(Vector((x,y,5)),Vector((0,0,-1)),distance=10)
 if not ok:raise RuntimeError('Missing original attachment')
 return p.z
def paint(o,mat,base,variation=.15):
 o.data.materials.clear();o.data.materials.append(mat);ca=o.data.color_attributes.new(name='ReefColor',type='FLOAT_COLOR',domain='POINT')
 for v,c in zip(o.data.vertices,ca.data):
  p=v.co;large=noise.noise(p*.85);medium=noise.noise(p*4.1+Vector((7,11,3)));fine=noise.noise(p*19)
  f=1+variation*(large*.6+medium*.3+fine*.1)
  c.color=(*[max(.018,x*f) for x in base],1)
 for p in o.data.polygons:p.use_smooth=True
class Network:
 def __init__(self,name):self.name=name;self.v=[];self.f=[]
 def tube(self,points,radii,sides=5):
  rows=[]
  for i,p in enumerate(points):
   p=Vector(p);t=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)]);t.normalize();a=t.cross(Vector((0,1,0)))
   if a.length<.01:a=t.cross(Vector((1,0,0)))
   a.normalize();b=t.cross(a).normalized();row=[]
   for k in range(sides):row.append(len(self.v));self.v.append(tuple(p+radii[i]*(a*cos(2*pi*k/sides)+b*sin(2*pi*k/sides))))
   rows.append(row)
  for i in range(len(rows)-1):
   for k in range(sides):self.f.append((rows[i][k],rows[i][(k+1)%sides],rows[i+1][(k+1)%sides],rows[i+1][k]))
  self.f += [tuple(reversed(rows[0])),tuple(rows[-1])]
 def finish(self,mat,col):
  me=bpy.data.meshes.new(self.name);me.from_pydata(self.v,[],self.f);me.update();o=bpy.data.objects.new(self.name,me);bpy.context.collection.objects.link(o);paint(o,mat,col,.12);return o

def fan(name,x,y,height,width,angle,col):
 z=roof(x,y)-.025;net=Network(name);rows=[]
 def world(u,v):
  depth=.045*sin(v*5+u*3)+.025*sin(u*9-v*2)
  return (x+u*cos(angle)-depth*sin(angle),y+u*sin(angle)+depth*cos(angle),z+v)
 net.tube([world(0,0),world(.01,.20),world(-.015,.40)], [.025,.018,.010],7)
 edges=json.loads((ROOT/'fan-network-low.json').read_text())['edges']
 for i,(p,q) in enumerate(edges):
  # An irregular polygonal web at a finer scale, not repeated diamond rows.
  t=(p[1]+q[1])*.5/1.35;r=.0022*math.sqrt(2200/480)*(1+.22*sin(i*1.73))
  net.tube([world(p[0]*width/1.55,p[1]*height/1.2),world(q[0]*width/1.55,q[1]*height/1.2)],[r,r*.96],4)
 for i in range(22):
  t=(i+1)/22;w=width*(sin(pi*t)**.58)*min(1,t*4);rows.append([((-1+2*j/16)*w*.5,.15+t*height) for j in range(17)])
 # A basal stem branches at different heights; no perimeter rails or closing frame.
 paths=[
  ([(0,.10),(.015,.30),(-.055,.55),(.035,.78),(.030,1.08)],[.024,.018,.012,.007,.003]),
  ([(-.02,.40),(-.12,.52),(-.27,.68),(-.39,.90),(-.45,1.02)],[.013,.010,.007,.004,.002]),
  ([(-.04,.55),(.10,.63),(.27,.80),(.39,.98)],[.012,.009,.005,.002]),
  ([(-.18,.58),(-.38,.66),(-.52,.78)],[.006,.004,.0018]),
  ([(-.03,.75),(-.18,.86),(-.25,1.10)],[.006,.004,.0018]),
  ([(.18,.72),(.45,.76),(.61,.88)],[.005,.003,.0016])]
 for coords,radii in paths:
  net.tube([world(u*width/1.55,v*height/1.2) for u,v in coords],radii,6)
 return net.finish(fanmat,col)

fan('LOW_Attached_reticulate_fan_form',-.90,-.12,1.20,1.55,-.20,(.27,.19,.12))
fan('LOW_Attached_small_fan_form',-2.0,.92,.72,.85,.72,(.30,.225,.15))
bpy.data.objects.remove(rock,do_unlink=True)
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH')
# Keep only data used by the two authored low-detail fans, not unused master textures.
for _ in range(3):
 for collection in [bpy.data.meshes,bpy.data.materials,bpy.data.images,bpy.data.textures]:
  for data in list(collection):
   if data.users==0:collection.remove(data)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'low-fans-editable.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'low-fans.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False,export_extras=True)
report={'source':'Original master fan profile and primary veins; 480-site reticulate appearance network instead of2200, thicker small tubes to approximate distant coverage. Artist LOD, not biological simplification or scan.','master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'network_sha256':hashlib.sha256((ROOT/'fan-network-low.json').read_bytes()).hexdigest(),'meshes':{o.name:{'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)}for o in bpy.context.scene.objects if o.type=='MESH'},'glb_sha256':hashlib.sha256((OUT/'low-fans.glb').read_bytes()).hexdigest(),'glb_bytes':(OUT/'low-fans.glb').stat().st_size}
(OUT/'provenance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
