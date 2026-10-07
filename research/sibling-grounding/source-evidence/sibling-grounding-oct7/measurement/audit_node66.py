"""Read-only node66 audit, reusing the frozen original cap and ground arrays."""
from pathlib import Path
import json,hashlib,sys,time
import numpy as np
P=Path(__file__).resolve().parent;study=P.parent;sys.path.insert(0,str(study));from glb_tools import *
F=study/'grounding-diagnostic';helper=F/'analyze_grounding.py';namespace={'__file__':str(helper)};exec(helper.read_text().split("out={'distance_units'")[0],namespace)
mk_surface=namespace['mk_surface'];cap_cells=namespace['cap_cells'];info=namespace['info'];top_at=namespace['top_at'];old=json.loads((F/'basal-rings.json').read_text())
raw,g,b=read(SOURCE);assert hashlib.sha256(raw).hexdigest()==SHA;target=g['nodes'][66];assert target['name']=='Depth_Staghorn_Linked_01_1'and target['mesh']==47
parents={c:i for i,n in enumerate(g['nodes'])for c in n.get('children',[])}
def mat(i):
 n=g['nodes'][i]
 if 'matrix'in n:a=np.array(n['matrix']).reshape(4,4).T
 else:
  x,y,z,w=n.get('rotation',[0,0,0,1]);xx=x*x;yy=y*y;zz=z*z;xy=x*y;xz=x*z;yz=y*z;wx=w*x;wy=w*y;wz=w*z
  rot=np.array([[1-2*(yy+zz),2*(xy-wz),2*(xz+wy)],[2*(xy+wz),1-2*(xx+zz),2*(yz-wx)],[2*(xz-wy),2*(yz+wx),1-2*(xx+yy)]])
  a=np.eye(4);a[:3,:3]=rot@np.diag(n.get('scale',[1,1,1]));a[:3,3]=n.get('translation',[0,0,0])
 return mat(parents[i])@a if i in parents else a
inverse78=np.linalg.inv(np.array(old['node78_world_matrix']));matrix66=mat(66);mapping=matrix66@inverse78

def relocate(points):
 arr=np.array(points);return arr@mapping[:3,:3].T+mapping[:3,3]
# Validate inverse mapping recovers the exact finite source vertices, not synthetic rings.
mesh=geom(g,b,47);positions={tuple(v)for v in mesh['POSITION']};recovered=[]
for r in old['roots']:
 ring=np.array(r['world_ring']);local=ring@inverse78[:3,:3].T+inverse78[:3,3];assert all(tuple(v.astype(np.float32))in positions for v in local);recovered.extend(local)
surface=mk_surface('baseline');roots=[];allcells=[];junction_min=float('inf');start=time.time()
for r in old['roots']:
 ring=relocate(r['world_ring']);caps=relocate(r['actual_cap_triangles_world']);cells=cap_cells(surface,caps);allcells.append(cells);rec={'root':r['root'],'source_graph_segment':r['segment'],'world_ring':ring.tolist(),'actual_cap_triangles_world':caps.tolist(),'center_world':ring.mean(0).tolist(),**info(cells)}
 expected=float(np.abs(np.linalg.det(caps[:,1:,[0,2]]-caps[:,:1,[0,2]])).sum()/2);rec['original_projected_cap_area']=expected;rec['overlay_area_coverage_error']=rec['projected_cap_area']-expected
 h,owners=top_at(surface,ring);rec['ring_vertex_vertical_gaps_scene_units']=(ring[:,1]-h).tolist();rec['ring_vertex_top_surface_nodes']=owners;jr=[]
 for j in r['primary_junction_rings']:
  points=relocate(j['world_ring']);tri=np.array([[points[0],points[k],points[k+1]]for k in range(1,9)]);result=info(cap_cells(surface,tri));result['child_segment']=j['child_segment'];jr.append(result);junction_min=min(junction_min,result['minimum_vertical_gap_scene_units'])
 rec['primary_junction_cross_sections']=jr;roots.append(rec);print('root',r['root'],rec['state'],rec['minimum_vertical_gap_scene_units'],rec['maximum_vertical_gap_scene_units'],flush=True)
contact=max(0,max(r['minimum_vertical_gap_scene_units']for r in roots));full=max(0,max(r['maximum_vertical_gap_scene_units']for r in roots));states={key:sum(r['state']==key for r in roots)for key in ['fully_floating','intersects_substrate','fully_below_substrate']}
for r,cells in zip(roots,allcells):r['hypothetical_minimum_contact_downshift_result']=info(cells,contact);r['hypothetical_full_cap_downshift_result']=info(cells,full)
result={'distance_units':'uncalibrated scene units','scope':'Only retained runtime source node66 Depth_Staghorn_Linked_01_1; node51 runtime-removed original instance is excluded. No pose or geometry changes; no new scene renders or QA.','source_sha256':SHA,'source_node66':target,'full_world_matrix66':matrix66.tolist(),'source_node78_world_matrix_for_inverse_mapping':old['node78_world_matrix'],'shared_mesh':47,'source_graph_roots':21,'source_ring_vertices_recovered_and_matched_to_GLBF32':len(recovered),'nonuniform_scale_preserved':target['scale'],'reused_inputs':{'basal_caps':str(F/'basal-rings.json'),'ground_triangles':str(F/'geometry-input.npz'),'continuous_overlay_implementation':str(helper)},'method':'Inverse-map the frozen node78 cap/ring world coordinates to exact original mesh-local F32 positions, then apply the complete node66 glTF world matrix including nonuniform scale. Reuse original full sand/limestone substrate arrays and continuous triangle overlay. This is exhaustive piecewise-linear geometry with float64 clipping tolerance 1e-11, not point sampling or interval-arithmetic certification.','classification_tolerance_scene_units':1e-7,'states':states,'maximum_gap_any_basal_cap_scene_units':max(r['maximum_vertical_gap_scene_units']for r in roots),'minimum_gap_any_basal_cap_scene_units':min(r['minimum_vertical_gap_scene_units']for r in roots),'root_minimum_gap_distribution_scene_units':{str(q):float(np.quantile([r['minimum_vertical_gap_scene_units']for r in roots],q))for q in [0,.25,.5,.75,1]},'minimum_primary_junction_cross_section_clearance_scene_units':junction_min,'roots':roots,'analytical_constraints':{'minimum_downshift_for_at_least_one_contact_point_per_root_scene_units':contact,'minimum_downshift_for_every_basal_cap_point_at_or_below_ground_scene_units':full,'downshift_before_first_primary_branch_cross_section_meets_ground_scene_units':junction_min,'contact_shift_preserves_primary_junction_clearance':contact<junction_min,'full_cap_shift_preserves_primary_junction_clearance':full<junction_min,'remaining_primary_junction_clearance_after_contact_shift_scene_units':junction_min-contact,'remaining_primary_junction_clearance_after_full_cap_shift_scene_units':junction_min-full,'maximum_basal_burial_after_contact_shift_scene_units':contact-min(r['minimum_vertical_gap_scene_units']for r in roots),'maximum_basal_burial_after_full_cap_shift_scene_units':full-min(r['minimum_vertical_gap_scene_units']for r in roots),'previous_node78_downshift_not_applied':True,'no_change_was_made':True},'maximum_projected_cap_area_partition_error':max(abs(r['overlay_area_coverage_error'])for r in roots),'duration_seconds':time.time()-start}
(P/'node66-grounding-proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['roots','reused_inputs']},indent=2))
