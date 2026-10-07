"""One finite node-78 macrostructure sample. Source files are read-only."""
import bpy,bmesh,sys,json,hashlib,copy,math,argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);OUT=a.out;OUT.mkdir(parents=True,exist_ok=True);SRC=a.source;RECIPE=Path(__file__).parent/'inputs'
sys.dont_write_bytecode=True
sys.path.insert(0,str(RECIPE));from replay_thickets import replay,correct
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(SRC))
NODE='Corridor_Distant_Linked_03';SOURCE='Coral_Staghorn_Thicket_11';old=bpy.data.objects[NODE];mat=old.data.materials[0];matrix=old.matrix_world.copy()
m=next(m for m in replay(RECIPE/'original_geometry_recipe.py')if m.name==SOURCE)
original=copy.deepcopy(m);original_report=correct(original)
# Exact replay gate before any design change.
origset={tuple(float(x)for x in v.co)for v in bpy.data.objects[SOURCE].data.vertices};used={i for f in original.f for i in f};replayset={tuple(Vector(original.v[i]))for i in used}
assert origset==replayset,(len(origset),len(replayset),len(origset-replayset))
U=Vector((.377640,-.925952,0)).normalized();V=Vector((-U.y,U.x,0));CENTER=Vector((3.8,2,0))
# Fixed authored hierarchy, not noise and not a search. h, spread-u, spread-depth,
# crown-u shift, crown-depth shift. The 21 independent skeletal roots are retained.
# Larger left bank, lower right bank, and a smaller interlacing rear bank.
SPECS=[
 (.60,.76,.86,.30,-.08),(.67,.86,.86,.17,-.04),(.98,.83,.86,-.17,-.07),
 (.53,.80,.92,.20,.05),(.88,.99,.92,-.06,-.07),(.77,.85,.68,-.27,.17),
 (.76,1.01,.88,.00,-.04),(.89,.80,.96,-.26,.07),(.95,.69,.72,-.22,-.09),
 (.78,.82,.84,-.15,.04),(.76,.88,.76,-.25,.12),(.98,.81,.95,-.22,.04),
 (.62,.93,.78,.21,-.05),(.63,.81,.75,-.37,.12),(.85,.77,.94,-.22,-.03),
 (.72,.82,.83,-.33,.06),(.68,.77,.88,.27,-.06),(.88,.90,.83,.05,-.08),
 (.51,.92,.85,-.35,.09),(1.00,1.04,.84,-.04,.10),(.90,.73,.79,-.17,.09)]
roots=[i for i,t in enumerate(m.tubes)if t['parent']is None];root_index={root:k for k,root in enumerate(roots)};tree_of={}
for i,t in enumerate(m.tubes):tree_of[i]=i if t['parent']is None else tree_of[t['parent']]
root_q={r:Vector(m.tubes[r]['start'])for r in roots}
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def warp(q,r):
 if r==roots[1]:return q.copy()
 root=root_q[r];h,su,sv,du,dv=SPECS[root_index[r]];d=q-root
 # Freeze the lowest 6 cm, preserving basal location and the original grounding.
 w=ease((q.z-root.z-.06)/.31)
 target=root+U*(d.dot(U)*su+du*w)+V*(d.dot(V)*sv+dv*w)+Vector((0,0,d.z*(1+(h-1)*w)))
 return target
mins=Vector(tuple(min(q[k]for q in original.v)for k in range(3)));maxs=Vector(tuple(max(q[k]for q in original.v)for k in range(3)))
raw0=[Vector(q)for q in m.raw_vertices];newraw=list(raw0);radinfo={}
for i,t in enumerate(m.tubes):
 p=t['parent'];root=tree_of[i];iscont=p is not None and (Vector(t['start'])-Vector(m.tubes[p]['end'])).length<1e-5
 if p is None:r0=t['r0'];r1=r0*.76
 else:
  pt=m.tubes[p];frac=(Vector(t['start'])-Vector(pt['start'])).length/(Vector(pt['end'])-Vector(pt['start'])).length
  pr0,pr1=radinfo[p];parent_r=pr0*(1-frac)+pr1*frac
  r0=parent_r*(1 if iscont else (.78 if t['depth']==0 else .86));r1=r0*(.69 if t['tip']else .76)
 if root==roots[1]:r0,r1=t['r0'],t['r1']
 radinfo[i]=(r0,r1)
 start=Vector(t['start']);end=Vector(t['end']);old_direction=(end-start).normalized();new_direction=(warp(end,root)-warp(start,root)).normalized();rot=old_direction.rotation_difference(new_direction)
 for row,frac in enumerate([0,.22,.46,.7,.88,.96,1.]):
  ids=[t['first_vertex']+10*row+k for k in range(10)];center=sum((raw0[k]for k in ids),Vector())/10;newcenter=warp(center,root);scale=(r0*(1-frac)+r1*frac)/(t['r0']*(1-frac)+t['r1']*frac)
  for vi in ids:newraw[vi]=newcenter+rot@(raw0[vi]-center)*scale
 # Basal rings stay exactly the original finite vertices.
 if p is None:
  for vi in range(t['first_vertex'],t['first_vertex']+10):newraw[vi]=raw0[vi]
# Approved single constraint correction: freeze the complete root #1 subtree.
for vi in range(len(newraw)):
 if tree_of[vi//70]==roots[1]:newraw[vi]=raw0[vi]
# One analytical envelope limiter. It prevents the candidate leaving the old bounds.
# It is not a parameter trial, clipping, or re-fit of the source roots.
alpha=1.0
for oldq,newq in zip(raw0,newraw):
 for k in range(3):
  d=newq[k]-oldq[k]
  if d>0:alpha=min(alpha,(maxs[k]-oldq[k])/d)
  elif d<0:alpha=min(alpha,(mins[k]-oldq[k])/d)
alpha=max(0,min(1,alpha))
violations=[]
for vi,(oldq,newq) in enumerate(zip(raw0,newraw)):
 for k in range(3):
  if newq[k]<mins[k]-1e-7 or newq[k]>maxs[k]+1e-7:
   d=newq[k]-oldq[k];limit=((maxs[k] if d>0 else mins[k])-oldq[k])/d
   tube=vi//70;root=tree_of[tube]
   violations.append({'vertex':vi,'tube':tube,'root_segment':root,'root_index':root_index[root],'axis':'XYZ'[k],'source':list(oldq),'proposed':list(newq),'min_allowed':mins[k],'max_allowed':maxs[k],'analytical_deformation_limit':limit})
violations.sort(key=lambda x:x['analytical_deformation_limit'])
if alpha<=.65:
 failure={'status':'REJECTED_BEFORE_EXPORT','source_replay_exact':True,'source_unique_used_vertices':len(origset),'source_unused_replay_vertices':len(replayset | {tuple(Vector(q)) for q in original.v})-len(replayset),'target_node':NODE,'node_index':78,'source_mesh_index':47,'triangle_budget':22168,'source_shared_nodes':['Coral_Staghorn_Thicket_11','Depth_Staghorn_Linked_01_1',NODE],'analytical_deformation_fraction':alpha,'source_envelope_local_blender_xyz':[list(mins),list(maxs)],'violating_vertex_coordinate_count':len(violations),'lowest_limits':violations,'violating_segment_indices':sorted({x['tube'] for x in violations}),'in_envelope_segment_count':len(m.tubes)-len({x['tube'] for x in violations}),'in_envelope_entire_root_subtree_count':len(roots)-len({x['root_segment'] for x in violations}),'max_local_protrusion':max([max(v['min_allowed']-v['proposed']['XYZ'.index(v['axis'])],v['proposed']['XYZ'.index(v['axis'])]-v['max_allowed'])for v in violations],default=0),'limiting_segment_source_graph':m.tubes[violations[0]['tube']],'reason':'At least one exact original outer-boundary vertex moves outward; the common deformation limiter allows zero movement. Recipe rejected without export, parameter search or patch.','candidate_written':False,'additional_mesh_bytes':0,'runtime_geometry_memory_change_bytes':0}
 (OUT/'constraint-correction-failure-proof.json').write_text(json.dumps(failure,indent=2));print('FAILURE_PROOF',json.dumps(failure),flush=True)
 raise RuntimeError('Envelope gate rejected the single authored construction; stopping')
# Graph centers get the same bounded deformation as the surface.
old_graph=copy.deepcopy(m.tubes)
for i,t in enumerate(m.tubes):
 root=tree_of[i]
 for key in ('start','end'):
  q=Vector(t[key]);t[key]=list(q+(warp(q,root)-q)*alpha)
 t['r0'],t['r1']=radinfo[i]
m.raw_vertices=[tuple(q+(n-q)*alpha)for q,n in zip(raw0,newraw)];m.v=list(m.raw_vertices)
repair_report=correct(m)
# Repaired continuation rings may protrude slightly: assert final envelope, do not silently clip.
bbox=[[min(q[k]for q in m.v)for k in range(3)],[max(q[k]for q in m.v)for k in range(3)]]
assert all(bbox[0][k]>=mins[k]-1e-6 and bbox[1][k]<=maxs[k]+1e-6 for k in range(3)),(bbox,list(mins),list(maxs))
me=bpy.data.meshes.new(NODE+'_hierarchy');me.from_pydata(m.v,[],m.f);me.update();ob=bpy.data.objects.new(NODE+'_candidate',me);bpy.context.collection.objects.link(ob);me.materials.append(mat)
col=me.color_attributes.new(name='ReefColor',type='FLOAT_COLOR',domain='POINT')
for d,c in zip(col.data,m.c):d.color=c
me.color_attributes.active_color=col
bm=bmesh.new();bm.from_mesh(me);loose=[v for v in bm.verts if not v.link_faces];bmesh.ops.delete(bm,geom=loose,context='VERTS');bmesh.ops.recalc_face_normals(bm,faces=bm.faces);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert boundary==nonmanifold==0;bm.to_mesh(me);bm.free()
for f in me.polygons:f.use_smooth=True
uv=me.uv_layers.new(name='SurfaceUV');me.update()
for poly in me.polygons:
 axis=max(range(3),key=lambda k:abs(poly.normal[k]));dims=[(1,2),(0,2),(0,1)][axis];sign=1 if poly.normal[axis]>=0 else -1
 for li in poly.loop_indices:
  co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[dims[0]]*2.4*sign,co[dims[1]]*2.4)
tri=sum(len(p.vertices)-2 for p in me.polygons);assert tri==22168
basal_equal=all(tuple(m.v[k])==tuple(original.v[k])for r in roots for k in range(m.tubes[r]['first_vertex'],m.tubes[r]['first_vertex']+10));assert basal_equal
# Distance-based clearance comparisons use final world vertices and unchanged scene geometry.
from mathutils.bvhtree import BVHTree
terrain=[o for o in bpy.context.scene.objects if o.type=='MESH'and o.name.startswith(('Hardbottom_','Depth_Hardbottom_','Distant_Limestone_','Corridor_','Spatial_'))and o.name!=NODE and 'Staghorn'not in o.name and 'Linked'not in o.name]
oldbases=[matrix@Vector(old_graph[r]['start'])for r in roots]
# No claim of strict fish clearance: only geometry and routes are preserved.
proof={'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'target_node':NODE,'target_node_index':78,'source_mesh_index':47,'source_mesh_name':SOURCE,'source_shared_nodes':[o.name for o in bpy.data.objects if o.data==old.data],'triangle_budget_before':22168,'triangle_budget_after':tri,'roots_before_after':[21,21],'segments_before_after':[171,171],'tips_before_after':[103,103],'height_scale':m.height_scale,'analytical_envelope_deformation_fraction':alpha,'bbox_before_local_blender':[list(mins),list(maxs)],'bbox_after_local_blender':bbox,'basal_rings_byte_equal':basal_equal,'intrinsic_boundary_edges':boundary,'intrinsic_nonmanifold_edges':nonmanifold,'signed_volume':volume,'authored_group_specs':SPECS,'accepted_continuation_repair_reapplied':repair_report['joints_corrected'],'unchanged_color_samples':m.c==original.c,'source_replay_exact':True,'constraint_correction':'The entire root #1 subtree (segments 7 through 14) stays exact original geometry and radii; all other authored specs unchanged.','frozen_subtree_vertices_equal':all(tuple(m.v[k])==tuple(original.v[k]) for i,t in enumerate(m.tubes) if tree_of[i]==roots[1] for k in range(t['first_vertex'],t['first_vertex']+70)),'caveats':['Interpretive morphology sample, not a scanned specimen, ecological validation, exact density or named-site reconstruction','Independent source roots and intersecting lateral components retained; no invented common basal root network or global union','Offline static clearance only; owner must test full fish animation before integration']}
(OUT/'geometry-proof.json').write_text(json.dumps(proof,indent=2));(OUT/'candidate-branch-graph.json').write_text(json.dumps({'source_graph':old_graph,'candidate_graph':m.tubes,'tree_of':tree_of},indent=2))
# Standalone replacement in source local coordinates. Node transform remains in the exact GLB patch.
for o in list(bpy.data.objects):
 if o!=ob:bpy.data.objects.remove(o,do_unlink=True)
ob.name=NODE;me.name=NODE+'_hierarchy';ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.gltf(filepath=str(OUT/'replacement.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT')
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'thicket-editable.blend'))
print('DONE',json.dumps(proof),flush=True)
