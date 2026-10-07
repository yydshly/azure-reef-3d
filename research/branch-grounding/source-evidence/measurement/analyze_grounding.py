"""Read-only exact piecewise-linear basal-cap / highest-substrate overlay."""
from pathlib import Path
import numpy as np,json,time
P=Path(__file__).resolve().parent;data=json.loads((P/'basal-rings.json').read_text());z=np.load(P/'geometry-input.npz')
EPS=1e-11

def area(p):
 return abs(float(np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1)))*.5) if len(p)>2 else 0

def signed(p):return float(np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1)))*.5

def line(a,b):return np.array([a[1]-b[1],b[0]-a[0],a[0]*b[1]-a[1]*b[0]])
def clip(p,c):
 if len(p)<3:return np.zeros((0,2))
 v=p@c[:2]+c[2];out=[]
 for i in range(len(p)):
  j=(i+1)%len(p);inside=v[i]>=-EPS;nextin=v[j]>=-EPS
  if inside:out.append(p[i])
  if inside!=nextin:
   t=v[i]/(v[i]-v[j]);out.append(p[i]+t*(p[j]-p[i]))
 return np.array(out) if len(out)>=3 else np.zeros((0,2))
def split(p,c):
 v=p@c[:2]+c[2]
 if v.min()>=-EPS or v.max()<=EPS:return [p]
 return [q for q in (clip(p,c),clip(p,-c)) if area(q)>1e-14]
def tri_edges(v):
 if signed(v)<0:v=v[::-1]
 return [line(v[i],v[(i+1)%3]) for i in range(3)]
def mk_surface(mode):
 tt=z['substrate_positions'][z['substrate_triangles']];owners=z['substrate_owner']
 if mode=='candidate':
  keep=owners!=86;tt=np.concatenate([tt[keep],z['candidate_positions'][z['candidate_triangles']]]);owners=np.r_[owners[keep],np.full(len(z['candidate_triangles']),86)]
 xz=tt[:,:,[0,2]];design=np.concatenate([xz,np.ones((*xz.shape[:2],1))],axis=2);det=np.linalg.det(design);ok=abs(det)>1e-14;tt=tt[ok];xz=xz[ok];owners=owners[ok];coeff=np.linalg.solve(design[ok],tt[:,:,1,None])[:,:,0]
 return {'tt':tt,'xz':xz,'owners':owners,'coeff':coeff,'min':xz.min(1),'max':xz.max(1)}
def candidates(s,poly):return np.flatnonzero(((s['max']>=poly.min(0)-EPS)&(s['min']<=poly.max(0)+EPS)).all(1))
def top_at(s,points):
 heights=[];owners=[]
 for p in np.array(points):
  ix=np.flatnonzero(((s['max']>=p[[0,2]]-EPS)&(s['min']<=p[[0,2]]+EPS)).all(1));valid=[]
  for i in ix:
   if all(p[[0,2]]@l[:2]+l[2]>=-EPS for l in tri_edges(s['xz'][i])):valid.append(i)
  vv=np.array(valid);h=s['coeff'][vv]@np.r_[p[[0,2]],1];i=int(vv[np.argmax(h)]);heights.append(float(h.max()));owners.append(int(s['owners'][i]))
 return np.array(heights),owners

def cap_cells(s,triangles):
 result=[]
 for t in np.array(triangles):
  cap=t[:,[0,2]]
  if area(cap)<1e-14:continue
  capcoeff=np.linalg.solve(np.c_[cap,np.ones(3)],t[:,1]);ix=candidates(s,cap);eligible=[];lines={}
  for i in ix:
   poly=cap.copy();ed=tri_edges(s['xz'][i])
   for l in ed:poly=clip(poly,l)
   if area(poly)<1e-14:continue
   eligible.append(i)
   for l in ed:
    norm=np.linalg.norm(l[:2]);ll=l/norm
    if ll[0]<-EPS or (abs(ll[0])<=EPS and ll[1]<0):ll=-ll
    lines[tuple(np.round(ll,11))]=ll
  cells=[cap]
  for l in lines.values():cells=[q for cell in cells for q in split(cell,l)]
  for cell in cells:
   center=cell.mean(0);cover=[i for i in eligible if all(center@l[:2]+l[2]>=-EPS for l in tri_edges(s['xz'][i]))];assert cover
   sub=[cell]
   for j,a in enumerate(cover):
    for b in cover[j+1:]:
     diff=s['coeff'][a]-s['coeff'][b]
     if np.linalg.norm(diff[:2])>EPS:sub=[q for x in sub for q in split(x,diff)]
   for poly in sub:
    cent=poly.mean(0);heights=s['coeff'][cover]@np.r_[cent,1];owner=int(cover[int(np.argmax(heights))]);gapcoeff=capcoeff-s['coeff'][owner];vals=poly@gapcoeff[:2]+gapcoeff[2];result.append({'polygon':poly,'gap_coeff':gapcoeff,'min':float(vals.min()),'max':float(vals.max()),'area':area(poly),'substrate_node':int(s['owners'][owner])})
 return result

def info(cells,delta=0):
 a=sum(c['area'] for c in cells);above=sum(area(clip(c['polygon'],c['gap_coeff']-np.array([0,0,delta]))) for c in cells);mi=min(c['min'] for c in cells)-delta;ma=max(c['max'] for c in cells)-delta
 return {'minimum_vertical_gap_scene_units':mi,'maximum_vertical_gap_scene_units':ma,'projected_cap_area':a,'above_substrate_projected_area_fraction':float(np.clip(above/a,0,1)),'state':'fully_floating' if mi>1e-7 else 'fully_below_substrate' if ma<-1e-7 else 'intersects_substrate','top_surface_nodes':sorted({c['substrate_node'] for c in cells})}

out={'distance_units':'uncalibrated scene units','method':'Exact piecewise-linear overlay of every actual basal-cap GLB triangle with all vertically projected source sand/limestone triangles. Partition by all projected triangle edges and competing height-plane intersections; select highest ground within each cell. Gap extrema occur at cell vertices. No center/radius approximation. Float64 with 1e-11 clipping tolerance, not interval arithmetic. Positive gap = branch cap above ground; negative = buried.','source_replay_and_transform_proof':'basal-rings.json','arms':{}}
for mode in ['baseline','candidate']:
 s=mk_surface(mode);records=[];allcells=[];junction_min=float('inf');primary=[];started=time.time()
 for r in data['roots']:
  cells=cap_cells(s,r['actual_cap_triangles_world']);allcells.append(cells);rec={'root':r['root'],'segment':r['segment'],'center_world':r['center_world'],**info(cells)};ring=np.array(r['world_ring']);h,own=top_at(s,ring);rec['actual_10_ring_vertex_gaps_scene_units']=(ring[:,1]-h).tolist();rec['ring_vertex_top_surface_nodes']=own
  jr=[]
  for joint in r['primary_junction_rings']:
   ring=np.array(joint['world_ring']);fan=np.array([[ring[0],ring[k],ring[k+1]]for k in range(1,9)]);jc=cap_cells(s,fan);ji=info(jc);ji['child_segment']=joint['child_segment'];jr.append(ji);junction_min=min(junction_min,ji['minimum_vertical_gap_scene_units'])
  rec['primary_junction_cross_sections']=jr;primary.extend(jr);records.append(rec)
  print(mode,'root',r['root'],rec['state'],rec['minimum_vertical_gap_scene_units'],rec['maximum_vertical_gap_scene_units'],flush=True)
 minimum_contact_shift=max(0,max(x['minimum_vertical_gap_scene_units'] for x in records));all_caps_below_shift=max(0,max(x['maximum_vertical_gap_scene_units'] for x in records));states={k:sum(x['state']==k for x in records)for k in ['fully_floating','intersects_substrate','fully_below_substrate']}
 for rec,cells in zip(records,allcells):rec['after_analytical_minimum_contact_downshift']=info(cells,minimum_contact_shift);rec['after_analytical_full_cap_downshift']=info(cells,all_caps_below_shift)
 out['arms'][mode]={'states':states,'roots':records,'distribution_of_root_minimum_gaps_scene_units':{str(q):float(np.quantile([r['minimum_vertical_gap_scene_units']for r in records],q))for q in [0,.25,.5,.75,.9,1]},'maximum_gap_any_basal_surface_scene_units':max(x['maximum_vertical_gap_scene_units'] for x in records),'rigid_vertical_shift_analysis':{'minimum_downshift_for_at_least_one_contact_point_per_root_scene_units':minimum_contact_shift,'minimum_downshift_for_every_basal_cap_point_at_or_below_ground_scene_units':all_caps_below_shift,'first_primary_branch_cross_section_contacts_ground_at_downshift_scene_units':junction_min,'at_least_one_contact_solution_before_primary_branch_burial':minimum_contact_shift<junction_min,'entire_cap_solution_before_primary_branch_burial':all_caps_below_shift<junction_min,'remaining_first_primary_branch_clearance_after_minimum_contact_shift_scene_units':junction_min-minimum_contact_shift,'remaining_first_primary_branch_clearance_after_full_cap_shift_scene_units':junction_min-all_caps_below_shift,'maximum_basal_burial_after_minimum_contact_shift_scene_units':-min(x['minimum_vertical_gap_scene_units'] for x in records)+minimum_contact_shift,'maximum_basal_burial_after_full_cap_shift_scene_units':-min(x['minimum_vertical_gap_scene_units'] for x in records)+all_caps_below_shift,'no_geometry_or_transform_was_changed':True},'seconds':time.time()-started}
errs=[]
for mode,arm in out['arms'].items():
 for rec,raw in zip(arm['roots'],data['roots']):
  tt=np.array(raw['actual_cap_triangles_world'])[:,:,[0,2]];expected=float(np.abs(np.linalg.det(tt[:,1:]-tt[:,:1])).sum()/2);error=rec['projected_cap_area']-expected;errs.append(abs(error));rec['original_projected_cap_area']=expected;rec['overlay_area_coverage_error']=error
base=out['arms']['baseline']['rigid_vertical_shift_analysis'];delta=base['minimum_downshift_for_every_basal_cap_point_at_or_below_ground_scene_units']+.005
out['continuous_overlay_validation']={'maximum_projected_area_partition_error':max(errs),'cap_count':42,'method_scope':'Every original basal cap GLB triangle, not point samples. Float64 exhaustive arrangement with 1e-11 clipping tolerance, not interval arithmetic or a certified exact floating-point bound.','classification_tolerance_scene_units':1e-7}
out['requested_analytical_pose_proposal']={'scope':'Analytical only, original support baseline; no geometry or pose was changed.','downshift_scene_units':delta,'derivation':'Original complete-cap maximum positive gap 0.12211730762552114 plus 0.005 scene-unit embed allowance.','node78_translation_y_before':data['node78']['translation'][1],'node78_translation_y_if_applied':data['node78']['translation'][1]-delta,'maximum_basal_cap_gap_after_shift_scene_units':-.005,'deepest_basal_cap_burial_after_shift_scene_units':delta-min(x['minimum_vertical_gap_scene_units'] for x in out['arms']['baseline']['roots']),'first_primary_junction_cross_section_clearance_after_shift_scene_units':base['first_primary_branch_cross_section_contacts_ground_at_downshift_scene_units']-delta,'junction_scope':'All actual first-order branch starting rings, or the repaired root terminal ring for a continuation whose initial ring is absent; evaluated as finite cross-sections. This bounds those first primary junctions, not a whole-world collision certificate.'}
(P/'grounding-proof.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:{'states':v['states'],'rigid_vertical_shift_analysis':v['rigid_vertical_shift_analysis']}for k,v in out['arms'].items()},indent=2))
