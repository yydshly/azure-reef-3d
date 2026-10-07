"""One authored new branch graph, in uncalibrated scene units. Blender 4.3.2.
No source mutation, parameter search, source-graph warp or museum-mesh reuse.
"""
import argparse,sys,json,hashlib,math,copy
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);SRC=args.source.resolve();OUT=args.out.resolve();OUT.mkdir(parents=True,exist_ok=True)
SOURCE_HASH='c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SOURCE_HASH
sys.path.insert(0,str(P/'inputs'));from replay_thickets import replay,correct
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(SRC))
NODE='Corridor_Distant_Linked_03';old=bpy.data.objects[NODE]
m=next(m for m in replay(P/'inputs/original_geometry_recipe.py') if m.name=='Coral_Staghorn_Thicket_11');correct(m)
used={i for f in m.f for i in f};assert {tuple(v.co) for v in old.data.vertices}=={tuple(Vector(m.v[i])) for i in used}
roots=[t for t in m.tubes if t['parent'] is None]
lo=Vector([min(q[k] for q in m.v) for k in range(3)]);hi=Vector([max(q[k] for q in m.v) for k in range(3)])
# Endpoints are authored independently of old branch tips, around the original colony centre.
# Seven axes cross the central volume instead of continuing the old radial crown.
ENDS=[(-.15,-.10,1.19),(-.25,-1.20,.72),(.54,.65,1.21),(.37,-.70,.82),(-.25,.76,.96),(-.60,.19,1.13),(1.04,-.45,.75),(.32,.45,1.24),(1.05,.40,.97),(.25,-.20,1.14),(-1.18,-.20,.72),(-.30,-.36,1.05),(.05,.30,.88),(-.90,-.53,.92),(-.06,.01,.76),(.30,-.32,.97),(-.30,-.90,.56),(.94,-.01,1.01),(-.70,.02,.69),(-.83,.81,.82),(.60,.72,.87)]
# Different orders and counts are intentional. These are axillary branches, not recursive binary forks.
LEVELS=[(.23,.39,.55,.70,.84),(.28,.49,.72,.86),(.25,.41,.58,.73,.87),(.24,.44,.63,.82),(.22,.38,.57,.76,.88),(.25,.40,.56,.71,.84),(.27,.46,.68,.83),(.21,.37,.52,.69,.85),(.24,.42,.62,.80),(.23,.39,.58,.73,.87),(.26,.48,.69,.85),(.22,.36,.53,.71,.86),(.24,.42,.61,.82),(.23,.39,.57,.75,.88),(.25,.45,.67,.84),(.22,.38,.54,.73,.87),(.29,.50,.72,.87),(.24,.40,.59,.77,.89),(.27,.46,.65,.84),(.23,.40,.57,.74,.87),(.24,.43,.63,.81)]
ANGLES=[15,208,67,319,142,261,96,11,225,151,303,49,193,337,119,282,71,172,22,246,132]
LENGTHS=[.53,.31,.46,.28,.39,.57,.34,.42,.26,.49,.36]
CENTER=Vector((3.8,2,0));graph=[];union_log=[];bounded=[];objects=[]

def mesh_object(name,vertices,faces):
 me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);return ob

def frame(d):
 a=d.cross(Vector((0,0,1)))
 if a.length<.05:a=d.cross(Vector((0,1,0)))
 a.normalize();return a,d.cross(a).normalized()

def tube(name,points,radii,sides=8,first_rings=None):
 vertices=[];faces=[]
 for j,(q,r) in enumerate(zip(points,radii)):
  if first_rings is not None and j<len(first_rings):row=first_rings[j]
  else:
   d=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized();a,b=frame(d)
   row=[q+r*(math.cos(k*math.tau/sides)*a+math.sin(k*math.tau/sides)*b) for k in range(sides)]
  vertices.extend(tuple(x) for x in row)
 for j in range(len(points)-1):
  for k in range(sides):faces.append((j*sides+k,j*sides+(k+1)%sides,(j+1)*sides+(k+1)%sides,(j+1)*sides+k))
 faces.append(tuple(reversed(range(sides))));faces.append(tuple((len(points)-1)*sides+k for k in range(sides)))
 return mesh_object(name,vertices,faces)

def union(parent,child):
 bpy.context.view_layer.objects.active=parent;mod=parent.modifiers.new('Connected lateral junction','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=child
 bpy.ops.object.modifier_apply(modifier=mod.name);union_log.append([parent.name,child.name]);bpy.data.objects.remove(child,do_unlink=True)

def bezier(q0,q1,q2,q3,t):return (1-t)**3*q0+3*(1-t)**2*t*q1+3*(1-t)*t*t*q2+t**3*q3

def new_branch(name,start,direction,length,rad,root,parent,level,secondary=False):
 d=direction.normalized();requested=length
 # Individual ray extent determined before tube authoring, never a global fit or warp.
 # Inner radius padding protects the original local envelope.
 for k in range(3):
  if d[k]>1e-8:length=min(length,(hi[k]-.026-start[k])/d[k])
  elif d[k]<-1e-8:length=min(length,(lo[k]+.026-start[k])/d[k])
 assert length>.10,(name,length)
 if length<requested-1e-6:bounded.append({'branch':name,'requested':requested,'authored':length})
 end=start+d*length
 ts=[0,.12,.37,.65,.88,.97,1] if not secondary else [0,.20,.56,.88,.98,1]
 # Small nonrepeated turn at the terminal third, not a bent main scaffold.
 side=Vector((-d.y,d.x,0)).normalized();curve=side*(.005 if root%2 else -.005)
 points=[start+(end-start)*t+curve*math.sin(math.pi*t) for t in ts]
 radii=[rad*(1-.55*t)*(1 if t<1 else .33) for t in ts]
 ob=tube(name,points,radii,8)
 ident=len(graph);graph.append({'id':ident,'name':name,'root':root,'parent':parent,'attachment_fraction':level,'order':2 if secondary else 1,'start':list(start),'end':list(end),'r0':rad,'tip_radius':radii[-1],'length':length})
 return ob,ident,end,d

for i,rt in enumerate(roots):
 rawrings=[[Vector(m.v[rt['first_vertex']+row*10+k]) for k in range(10)] for row in (0,1)]
 base=sum(rawrings[0],Vector())/10;neck=sum(rawrings[1],Vector())/10
 end=CENTER+Vector(ENDS[i]);d0=(Vector(rt['end'])-Vector(rt['start'])).normalized();dn=(end-neck).normalized();span=(end-neck).length
 q0=neck;q1=neck+d0*min(.17,span*.19);q2=end-dn*span*.32;q3=end
 def pos(t):return bezier(q0,q1,q2,q3,t)
 def tangent(t):return (pos(min(1,t+.001))-pos(max(0,t-.001))).normalized()
 ts=[0,.10,.20,.30,.40,.50,.60,.70,.80,.89,.96,1]
 points=[base]+[pos(t) for t in ts];r0=rt['r0']
 radii=[r0]+[r0*(.956-.52*t)*(1 if t<1 else .32) for t in ts]
 main=tube('Root_%02d_Dominant'%i,points,radii,10,rawrings)
 rootid=len(graph);graph.append({'id':rootid,'name':main.name,'root':i,'parent':None,'order':0,'start':list(base),'neck':list(neck),'end':list(end),'r0':r0,'tip_radius':radii[-1],'length':(neck-base).length+sum((points[k+1]-points[k]).length for k in range(1,len(points)-1)),'basal_ring':list(map(list,rawrings[0]))})
 for k,t in enumerate(LEVELS[i]):
  attach=pos(t);axis=tangent(t);theta=math.radians(ANGLES[i]+k*137.5+(19 if k%2 else -7));horiz=Vector((math.cos(theta),math.sin(theta),0))
  # Long lateral axes alternate diagonal and flatter trajectories, exposing hierarchy.
  direction=(horiz*.73+axis*.30+Vector((0,0,.29+.11*((i+k)%3)))).normalized()
  length=LENGTHS[(i*3+k*2)%len(LENGTHS)]*(1-.24*t)
  pr=r0*(.956-.52*t);rad=pr*(.70 if k<3 else .62)
  branch,bid,bend,bd=new_branch('Root_%02d_Lateral_%02d'%(i,k),attach,direction,length,rad,i,rootid,t)
  # Secondary laterals occur on selected long side axes, staggered far from a tip fork.
  if k<3 and (i+k)%2==0:
   frac=.51 if (i+k)%4 else .64;secstart=attach+(bend-attach)*frac
   sdir=(bd*.42+Vector((-horiz.y,horiz.x,.62))*.72).normalized();slength=.16+.045*((i+2*k)%3)
   sec,sid,_,_=new_branch('Root_%02d_Secondary_%02d'%(i,k),secstart,sdir,slength,rad*.60,i,bid,frac,True)
   union(branch,sec)
  union(main,branch)
 objects.append(main)
 print('BUILT_ROOT',i,len(main.data.polygons),flush=True)

# Keep all 21 independent basal shoots. Each has watertight unioned side junctions.
bpy.ops.object.select_all(action='DESELECT')
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();ob=objects[0];ob.name=NODE;me=ob.data;me.name='Staggered_Lateral_Colony_NewTopology'
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.to_mesh(me);bm.free()
me.calc_loop_triangles();tri=len(me.loop_triangles)
assert tri<=22168,('triangle budget',tri)
assert boundary==0 and nonmanifold==0,(boundary,nonmanifold)
verts={tuple(v.co) for v in me.vertices};basal_equal=all(tuple(Vector(p)) in verts for g in graph if g['order']==0 for p in g['basal_ring']);assert basal_equal
bbox=[[min(v.co[k] for v in me.vertices) for k in range(3)],[max(v.co[k] for v in me.vertices) for k in range(3)]]
assert all(bbox[0][k]>=lo[k]-1e-6 and bbox[1][k]<=hi[k]+1e-6 for k in range(3)),(bbox,list(lo),list(hi))
for poly in me.polygons:poly.use_smooth=True
# Neutral export only. No living appearance, color transfer, or new surface material.
mat=bpy.data.materials.new('Neutral geometry review only');mat.diffuse_color=(.34,.34,.34,1);me.materials.clear();me.materials.append(mat)
for other in list(bpy.data.objects):
 if other!=ob:bpy.data.objects.remove(other,do_unlink=True)
ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.gltf(filepath=str(OUT/'replacement.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=False,export_normals=True,export_materials='EXPORT')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'staggered-colony-editable.blend'))
proof={'status':'POLYGON_STAGE_PASS_EXPORT_AND_VISUAL_REVIEW_REQUIRED','source_sha256':SOURCE_HASH,'replacement_sha256':hashlib.sha256((OUT/'replacement.glb').read_bytes()).hexdigest(),'target_node_index':78,'target_node_name':NODE,'shared_source_mesh_index':47,'shared_source_nodes_unchanged':[51,66],'construction_count':1,'parameter_sweeps':0,'original_graph_transformed':False,'museum_mesh_used':False,'units':'uncalibrated scene units','triangles_before':22168,'triangles_after':tri,'mesh_vertices_before_export':len(me.vertices),'basal_shoots':21,'terminal_tips_before':103,'terminal_tips_after':len(graph),'branch_axes_by_order':{str(k):sum(g['order']==k for g in graph) for k in range(3)},'new_branch_graph_axes':len(graph),'main_axis_lengths':[g['length'] for g in graph if g['order']==0],'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'signed_volume':volume,'original_basal_rings_exact':basal_equal,'original_first_two_basal_rings_preserved_in_authoring':True,'original_local_envelope':[list(lo),list(hi)],'candidate_local_envelope':bbox,'envelope_inset_min':[bbox[0][k]-lo[k] for k in range(3)],'envelope_inset_max':[hi[k]-bbox[1][k] for k in range(3)],'individual_preconstruction_ray_extent_limits':bounded,'boolean_junction_unions':len(union_log),'fish_route_compatibility':'All final vertices remain inside the existing target local AABB; all basal ring vertices exact. No fish route edits. Dense interior can reduce void clearance, so full animation mesh-distance clearance remains unverified and must precede integration.','caveats':['New interpretive topology, not a live scan or calibrated reconstruction','21 independent basal shoots retained; branch connections within each shoot use exact boolean unions','Incidental crossings between independent basal shoots remain overlapping surfaces','Source scene read only; no patched world asset produced','Neutral material only; no texture or living color claims']}
(OUT/'geometry-proof.json').write_text(json.dumps(proof,indent=2));(OUT/'branch-graph.json').write_text(json.dumps({'axes':graph,'authored_endpoints':ENDS,'lateral_attachment_levels':LEVELS,'union_log':union_log},indent=2));print('GEOMETRY_PROOF',json.dumps(proof),flush=True)
