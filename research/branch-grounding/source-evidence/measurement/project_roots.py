import json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;d=json.loads((P/'basal-rings.json').read_text());proof=json.loads((P/'grounding-proof.json').read_text());z=np.load(P/'geometry-input.npz')
QA=Path('/workspace/scratch/56bf13a306b9/reef-support03-ci-37673506367/support03-37673506367');render=json.loads((QA/'baseline/render.json').read_text());capture=next(x for x in render['captures']if x['file']=='diagnostic-close.png');cam=np.array(capture['state']['camera']);target=np.array(capture['state']['target']);f=target-cam;f/=np.linalg.norm(f);right=np.cross(f,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,f);tan=np.tan(np.deg2rad(47/2));width,height=1120,700

def project(points):
 p=np.array(points)-cam;zz=p@f
 return np.c_[width/2+(p@right)/zz/tan/(width/height)*width/2,height/2-(p@up)/zz/tan*height/2]
branch=BVHTree.FromPolygons(z['thicket_positions'].tolist(),z['thicket_triangles'].tolist(),all_triangles=True)
out={'camera':cam.tolist(),'target':target.tolist(),'vertical_fov_degrees':47,'image_size':[width,height],'source_runtime_capture':str(QA/'baseline/diagnostic-close.png'),'roots':[]}
for mode in ['baseline','candidate']:
 tt=z['substrate_triangles'];vv=z['substrate_positions']
 if mode=='candidate':
  tt=np.r_[tt[z['substrate_owner']!=86],z['candidate_triangles'].astype(np.int64)+len(vv)];vv=np.r_[vv,z['candidate_positions']]
 ground=BVHTree.FromPolygons(vv.tolist(),tt.tolist(),all_triangles=True)
 for i,r in enumerate(d['roots']):
  points=np.array(r['world_ring']);center=np.mean(points,0);direction=center-cam;distance=np.linalg.norm(direction);direction/=distance
  a,an,ai,ad=branch.ray_cast(Vector(cam),Vector(direction));b,bn,bi,bd=ground.ray_cast(Vector(cam),Vector(direction));hitdist=min(ad if ad is not None else float('inf'),bd if bd is not None else float('inf'));visible=abs(distance-hitdist)<.0002
  if mode=='baseline':out['roots'].append({'root':r['root'],'segment':r['segment'],'center_world':center.tolist(),'pixel_center':project([center])[0].tolist(),'pixel_ring':project(points).tolist(),'arms':{}})
  rec=proof['arms'][mode]['roots'][i];out['roots'][i]['arms'][mode]={'cap_center_unoccluded_within_0_0002_scene_units':bool(visible),'nearest_branch_ray_distance_scene_units':ad,'nearest_ground_ray_distance_scene_units':bd,'cap_center_ray_distance_scene_units':distance,'first_occluder':'branch'if (ad or float('inf'))<(bd or float('inf'))else'ground','minimum_vertical_gap_scene_units':rec['minimum_vertical_gap_scene_units'],'maximum_vertical_gap_scene_units':rec['maximum_vertical_gap_scene_units'],'state':rec['state'],'first_branch_hit_root':int(z['thicket_triangle_root'][ai]) if ai is not None else None,'cap_center_hidden_by_own_stem_surface':bool(ai is not None and int(z['thicket_triangle_root'][ai])==r['root'] and ad is not None and ad<distance-.0002)}
(P/'root-screen-map.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
