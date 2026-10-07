import sys,copy,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector,Quaternion
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent));from glb_tools import *
RECIPE=Path('/workspace/scratch/56bf13a306b9/coral-3d/modeling/junction-repair');sys.path.insert(0,str(RECIPE));from replay_thickets import replay,correct
raw,g,b=read(SOURCE);assert hashlib.sha256(raw).hexdigest()==SHA
branch=geom(g,b,47);graph=json.loads(Path('/workspace/scratch/56bf13a306b9/reef-thicket-hierarchy-oct7/candidate-branch-graph.json').read_text())['source_graph'];m=next(x for x in replay(RECIPE/'original_geometry_recipe.py') if x.name=='Coral_Staghorn_Thicket_11');assert m.tubes==graph;correct(m)
rawp=np.array(m.v,dtype=np.float32);local=rawp[:,[0,2,1]];local[:,2]*=-1
used={i for f in m.f for i in f};assert {tuple(v) for v in local[list(used)]}=={tuple(v) for v in branch['POSITION']}
parents={c:i for i,n in enumerate(g['nodes']) for c in n.get('children',[])}
def mat(i):
 n=g['nodes'][i]
 if 'matrix' in n:a=np.array(n['matrix']).reshape(4,4).T
 else:
  tr=np.array(n.get('translation',[0,0,0]));ss=np.array(n.get('scale',[1,1,1]));q=n.get('rotation',[0,0,0,1]);rot=np.array(Quaternion((q[3],q[0],q[1],q[2])).to_matrix());a=np.eye(4);a[:3,:3]=rot@np.diag(ss);a[:3,3]=tr
 return mat(parents[i])@a if i in parents else a
def transform(p,i):
 a=mat(i);return p.astype(float)@a[:3,:3].T+a[:3,3]
world=transform(local,78);bp=branch['POSITION'];btri=branch['tri'];lookup={tuple(v):i for i,v in enumerate(local)}
# Actual original basal cap triangles from the current GLB, using position membership.
roots=[]
for ordinal,(i,t) in enumerate((x for x in enumerate(graph) if x[1]['parent'] is None),1):
 ids=np.arange(t['first_vertex'],t['first_vertex']+10);coords={tuple(v) for v in local[ids]};isring=np.array([tuple(v) in coords for v in bp]);caps=btri[isring[btri].all(1)];assert len(caps)==8,(ordinal,len(caps));capworld=transform(bp,78)[caps]
 children=[(j,c) for j,c in enumerate(graph) if c['parent']==i];joints=[]
 for ci,c in children:
  usedids=[v for v in range(c['first_vertex'],c['first_vertex']+10) if v in used]
  if not usedids:usedids=list(range(t['first_vertex']+60,t['first_vertex']+70))
  assert len(usedids)==10
  joints.append({'child_segment':ci,'world_ring':world[usedids].tolist()})
 roots.append({'root':ordinal,'segment':i,'world_ring':world[ids].tolist(),'actual_cap_triangles_world':capworld.tolist(),'center_world':world[ids].mean(0).tolist(),'primary_junction_rings':joints,'stem_rows_world':[world[t['first_vertex']+10*row:t['first_vertex']+10*(row+1)].tolist()for row in range(7)]})
tree_of={}
for i,t in enumerate(graph):tree_of[i]=i if t['parent'] is None else tree_of[t['parent']]
root_number={r['segment']:r['root'] for r in roots}
vertex_roots=np.array([root_number[tree_of[lookup[tuple(v)]//70]] for v in bp])
face_roots=vertex_roots[btri];assert (face_roots==face_roots[:,:1]).all()
# Highest actual source sand/limestone, including every matching source node.
sv=[];sf=[];owner=[];catalog=[];offset=0
for i,n in enumerate(g['nodes']):
 if 'mesh' not in n or not any(tag in n.get('name','') for tag in ['Sand','Hardbottom','Limestone']):continue
 d=geom(g,b,n['mesh']);p=transform(d['POSITION'],i);tris=d['tri'];sv.extend(p);sf.extend(tris.astype(np.int64)+offset);owner.extend([i]*len(tris));catalog.append({'node':i,'name':n['name'],'vertices':len(p),'triangles':len(tris),'world_bounds':[p.min(0).tolist(),p.max(0).tolist()]});offset+=len(p)
_,cg,cb=read(P.parent/'support03-geometry-only.glb');c=geom(cg,cb,0);cp=transform(c['POSITION'],86)
np.savez(P/'geometry-input.npz',substrate_positions=np.array(sv),substrate_triangles=np.array(sf,np.int64),substrate_owner=np.array(owner),candidate_positions=cp,candidate_triangles=c['tri'],thicket_positions=transform(bp,78),thicket_triangles=btri,thicket_triangle_root=face_roots[:,0])
report={'source_sha256':SHA,'distance_units':'uncalibrated scene units','source_branch_graph_exact_replay':True,'all_used_replayed_positions_exactly_equal_current_GLBF32_position_set':True,'source_height_scale':m.height_scale,'coordinate_conversion':'Replay already applies original height_scale; then Blender XYZ -> glTF [x,z,-y], then complete node78 world matrix.','node78':g['nodes'][78],'node78_world_matrix':mat(78).tolist(),'substrates':catalog,'root_count':len(roots),'roots':roots}
(P/'basal-rings.json').write_text(json.dumps(report,indent=2)+'\n');print('EXTRACTED',len(roots),'exact basal rings; source height scale',m.height_scale,'substrate triangles',len(sf),flush=True)
