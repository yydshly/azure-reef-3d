"""Original interpreted reef-volume pilot. No scanned/restricted asset input.
Blender Z-up authoring; glTF export converts to Y-up. Units are scene units,
not a surveyed Florida location or calibrated coral identification.
"""
import bpy, math, random, json, sys, hashlib
from pathlib import Path
from mathutils import Vector, noise
from math import sin,cos,pi
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'structure-v3';OUT.mkdir(exist_ok=True);random.seed(71026)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def active(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o

def material(name,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');c=m.node_tree.nodes.new('ShaderNodeVertexColor');c.layer_name='ReefColor';m.node_tree.links.new(c.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=rough;return m
rockmat=material('Pilot_weathered_skeleton',.87);fanmat=material('Pilot_gorgonian_form',.72);massmat=material('Pilot_massive_growth_form',.74);covermat=material('Pilot_encrusting_cover',.79)
def paint(o,mat,base,variation=.15):
 o.data.materials.clear();o.data.materials.append(mat);ca=o.data.color_attributes.new(name='ReefColor',type='FLOAT_COLOR',domain='POINT')
 for v,c in zip(o.data.vertices,ca.data):
  p=v.co;large=noise.noise(p*.85);medium=noise.noise(p*4.1+Vector((7,11,3)));fine=noise.noise(p*19)
  f=1+variation*(large*.6+medium*.3+fine*.1)
  c.color=(*[max(.018,x*f) for x in base],1)
 for p in o.data.polygons:p.use_smooth=True

def ellipsoid(name,p,s,rotation=(0,0,0),segments=32,rings=20):
 if name.startswith('skeleton-part'):bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1,location=p)
 else:bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=p)
 o=bpy.context.object;o.name=name;o.scale=s;o.rotation_euler=rotation;active(o);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);return o

def displace(o,scale,strength,depth=2):
 tex=bpy.data.textures.new(o.name+'_weather',type='CLOUDS');tex.noise_scale=scale;tex.noise_depth=depth;tex.noise_basis='IMPROVED_PERLIN';m=o.modifiers.new('Unequal surface weathering','DISPLACE');m.texture=tex;m.strength=strength;m.mid_level=.5;active(o);bpy.ops.object.modifier_apply(modifier=m.name)

def poly_solid(name,footprint,top,thickness):
 n=len(footprint);verts=[(x,y,top[i]-thickness[i]) for i,(x,y) in enumerate(footprint)]+[(x,y,top[i]) for i,(x,y) in enumerate(footprint)]
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o

parts=[]
for i,(p,s,r) in enumerate([
 ((-1.9,.6,-.08),(1.2,.88,.36),(.1,.1,-.2)),
 ((-1.2,.4,.53),(.65,.70,1.0),(.13,-.20,.18)),
 ((.05,.6,.73),(.66,.71,1.1),(-.1,.16,-.2)),
 ((1.22,.8,.50),(.91,.72,.86),(.08,-.15,.32)),
 ((2.10,.6,.10),(.86,.62,.42),(.10,.05,.20)),
 ((-.50,-.64,.02),(.86,.52,.35),(.1,.2,.15)),
 ((-1.82,-.43,.08),(.74,.59,.43),(.2,-.1,-.35)),
 ((-2.35,.25,.20),(.61,.94,.45),(.16,.21,.10))
]):parts.append(ellipsoid('skeleton-part-%02d'%i,p,s,r))
# Different oblique solid supports replace the long rear convex ellipsoid.
parts.append(poly_solid('left-oblique-support',[(-1.65,.70),(-.35,.70),(-.25,1.55),(-1.35,1.70)],[.80,1.35,.95,.50],[1.05,1.60,1.20,.75]))
parts.append(poly_solid('right-thinner-support',[(.35,.90),(1.50,.70),(1.80,1.45),(.65,1.90)],[1.05,.76,.60,.85],[1.30,1.01,.85,1.10]))
# Short chipped overhangs have unequal thickness and no rounded pebble rims.
parts.append(poly_solid('left-short-overhang',[(-1.60,-.65),(-.45,-.82),(.20,-.30),(.05,.40),(-.80,.58),(-1.50,.20)],[1.22,1.33,1.30,1.45,1.42,1.30],[.18,.26,.40,.35,.25,.18]))
parts.append(poly_solid('right-short-overhang',[(.35,-.50),(1.20,-.70),(1.60,-.25),(1.35,.20),(.90,.30),(.38,0)],[1.13,1.12,1.04,1.10,1.30,1.25],[.22,.15,.18,.40,.30,.20]))

bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();rock=bpy.context.object;rock.name='Shoulder_closed_irregular_skeleton';active(rock);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
rm=rock.modifiers.new('Joined physical volume','REMESH');rm.mode='VOXEL';rm.voxel_size=.055;rm.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rm.name)
displace(rock,.55,.24);displace(rock,.16,.105)
# Different recesses: an undercut mouth, a narrow cleft, a scalloped flank,
# and one small oblique through-gap. Never a repeated row of circular holes.
for i,(p,s,r) in enumerate([
 ((-1.12,-.80,.67),(.52,.90,.38),(.08,-.14,.30)),((-.12,-.80,1.0),(.12,.76,.71),(.12,-.23,.21)),((1.55,-.42,.48),(.63,.54,.30),(.12,.22,-.19)),((.67,.3,.85),(.28,1.5,.22),(.0,.09,-.35))]):
 cut=ellipsoid('erosion-cut-%02d'%i,p,s,r,40,24);displace(cut,.24,.09);active(rock);mod=rock.modifiers.new('Open irregular recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
# A skewed rear cleft reaches the top and joins the side-facing negative space.
vs=[(.28,.28,.15),(.50,.28,.15),(.32,2.20,.15),(.10,2.20,.15),(-.45,.28,2.1),(.73,.28,2.1),(.50,2.20,2.1),(-.70,2.20,2.1)]
fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
me=bpy.data.meshes.new('skew cleft');me.from_pydata(vs,[],fs);me.update();cut=bpy.data.objects.new('skew cleft',me);bpy.context.collection.objects.link(cut);active(rock);m=rock.modifiers.new('Top-open rear cleft','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
active(rock);rm=rock.modifiers.new('Unified eroded solid','REMESH');rm.mode='VOXEL';rm.voxel_size=.052;rm.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rm.name)
sm=rock.modifiers.new('Remove voxel stair steps','SMOOTH');sm.factor=.15;sm.iterations=1;bpy.ops.object.modifier_apply(modifier=sm.name)
displace(rock,.095,.04,1)
dec=rock.modifiers.new('Bounded mesh budget','DECIMATE');dec.ratio=.60;bpy.ops.object.modifier_apply(modifier=dec.name)
paint(rock,rockmat,(.21,.18,.115),.35)

def roof(x,y):
 ok,p,n,_=rock.ray_cast(Vector((x,y,5)),Vector((0,0,-1)),distance=10)
 if not ok:raise RuntimeError('Unattached living form at '+str((x,y)))
 return p.z

# Conforming growth relief is continuous with the skeleton; no peelable sheet.
weight=rock.data.color_attributes.new(name='EncrustWeight',type='FLOAT_COLOR',domain='POINT')
for v,w in zip(rock.data.vertices,weight.data):
 p=v.co;zones=[((-1.55,-.45,.65),(1.0,.8,.65)),((.95,-.6,.57),(.95,.6,.7)),((.25,.95,1.2),(.65,.9,.6))]
 score=min(sum(((p[k]-c[k])/r[k])**2 for k in range(3)) for c,r in zones)
 value=max(0,min(1,(1.10+.13*noise.noise(p*5)-score)/.28));value=value*value*(3-2*value)
 v.co += v.normal*(.012*value);w.color=(value,value,value,1)
rock.data.update()

# Broad lobed massive colony, inspired by observed low-frequency form only.
base=roof(1.17,.64);mass=ellipsoid('Attached_massive_form_unidentified',(1.15,.66,base+.04),(1.08,.82,.43),(.06,.04,-.2),72,40)
for v in mass.data.vertices:
 p=v.co;n=p.normalized();a=math.atan2(p.y,p.x);v.co*=1+.11*cos(a*3+.4)*(1-n.z*n.z)+.065*sin(a*5)*abs(n.x);v.co.z+=.035*sin(p.x*6+p.y*4)+.025*noise.noise(p*5)
paint(mass,massmat,(.35,.235,.16),.16)

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
 edges=json.loads((ROOT/'fan-network.json').read_text())['edges']
 for i,(p,q) in enumerate(edges):
  # An irregular polygonal web at a finer scale, not repeated diamond rows.
  t=(p[1]+q[1])*.5/1.35;r=.0022*(1+.22*sin(i*1.73))
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
fan('Attached_reticulate_fan_form',-.90,-.12,1.20,1.55,-.20,(.27,.19,.12))
fan('Attached_small_fan_form',-2.0,.92,.72,.85,.72,(.30,.225,.15))

# Original generated albedo is mapped in object space then baked to a proper UV atlas.
# Its pores/color are inferred appearance, not measured coral microstructure.
def bake_material(o,source_image,cover=False,scale=.60):
 active(o);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(65),island_margin=.008);bpy.ops.object.mode_set(mode='OBJECT')
 m=bpy.data.materials.new(o.name+'_mapped_material');m.use_nodes=True;o.data.materials.clear();o.data.materials.append(m);n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');out=n.get('Material Output')
 tex=n.new('ShaderNodeTexImage');tex.image=source_image;tex.projection='BOX';tex.projection_blend=.30;tex.extension='MIRROR'
 coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=1/scale;l.new(coord.outputs['Object'],mapping.inputs[0]);l.new(mapping.outputs[0],tex.inputs['Vector'])
 color=tex.outputs['Color']
 if cover:
  wc=n.new('ShaderNodeVertexColor');wc.layer_name='EncrustWeight';tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(1.02,.77,.58,1);l.new(color,tint.inputs[1]);mix=n.new('ShaderNodeMixRGB');l.new(wc.outputs['Color'],mix.inputs[0]);l.new(color,mix.inputs[1]);l.new(tint.outputs[0],mix.inputs[2]);color=mix.outputs[0]
 emission=n.new('ShaderNodeEmission');l.new(color,emission.inputs['Color']);l.new(emission.outputs[0],out.inputs['Surface'])
 albedo=bpy.data.images.new(o.name+'_albedo',width=2048,height=2048,alpha=False);target=n.new('ShaderNodeTexImage');target.image=albedo;n.active=target
 bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1;bpy.ops.object.bake(type='EMIT',margin=10);albedo.filepath_raw=str(OUT/(o.name+'-albedo.png'));albedo.file_format='PNG';albedo.save()
 # Authored roughness map is a conservative matte range, not an inferred measurement.
 ns=n.new('ShaderNodeTexNoise');ns.inputs['Scale'].default_value=35;ns.inputs['Detail'].default_value=2;l.new(coord.outputs['Object'],ns.inputs['Vector']);rng=n.new('ShaderNodeMapRange');rng.inputs['From Min'].default_value=0;rng.inputs['From Max'].default_value=1;rng.inputs['To Min'].default_value=.70;rng.inputs['To Max'].default_value=.94;l.new(ns.outputs['Fac'],rng.inputs['Value']);l.new(rng.outputs['Result'],emission.inputs['Color'])
 rough=bpy.data.images.new(o.name+'_roughness',width=1024,height=1024,alpha=False);rough.colorspace_settings.name='Non-Color';target.image=rough;n.active=target;bpy.ops.object.bake(type='EMIT',margin=8);rough.filepath_raw=str(OUT/(o.name+'-roughness.png'));rough.file_format='PNG';rough.save()
 n.clear();bs=n.new('ShaderNodeBsdfPrincipled');out=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],out.inputs['Surface']);ai=n.new('ShaderNodeTexImage');ai.image=albedo;ri=n.new('ShaderNodeTexImage');ri.image=rough;l.new(ai.outputs['Color'],bs.inputs['Base Color']);l.new(ri.outputs['Color'],bs.inputs['Roughness'])
 # Neutralize unused vertex colors so GLTF cannot double-multiply the atlas.
 for ca in o.data.color_attributes:
  for datum in ca.data:datum.color=(1,1,1,1)
 albedo.pack();rough.pack()
image=bpy.data.images.load(str(ROOT/'assets/limestone-encrusting-albedo-v1.png'));bake_material(rock,image,True)
# The unaccepted massive cap is deliberately excluded from this structural pilot.
bpy.data.objects.remove(mass,do_unlink=True)
# Generated tissue appearance is not a measured anatomical texture.

# Save editable asset and export only authored solid/cover meshes.
objects=list(bpy.context.scene.objects)
for o in objects:o.select_set(o.type=='MESH')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'pilot-editable.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'pilot.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False,export_extras=True)
report={'source':'Original procedural/interpreted geometry; no third-party mesh or image','references':['https://www.nps.gov/drto/learn/nature/corals.htm','https://floridakeys.noaa.gov/corals/coralreefs.html'],'units':'uncalibrated scene units','forms':'top-open cleft skeleton, continuous encrusting relief/color, hierarchically supported fan forms; unaccepted massive cap excluded','meshes':{o.name:{'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)} for o in objects if o.type=='MESH'},'glb_sha256':hashlib.sha256((OUT/'pilot.glb').read_bytes()).hexdigest(),'glb_bytes':(OUT/'pilot.glb').stat().st_size}
(OUT/'pilot-provenance.json').write_text(json.dumps(report,indent=2));print('PILOT_EXPORTED',json.dumps(report),flush=True)
