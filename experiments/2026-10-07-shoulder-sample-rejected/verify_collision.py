"""Import the final GLB and measure the full Three.js route against static mesh faces."""
import argparse,bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('model',type=Path);p.add_argument('route',type=Path);p.add_argument('output',type=Path);p.add_argument('--baseline',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(a.model.resolve()))
route=json.loads(a.route.read_text());points=[Vector((q[0],-q[2],q[1]))for q in route['samples']]
bvhs=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.name.startswith('fish_'):continue
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    bvh=BVHTree.FromPolygons(vs,[tuple(poly.vertices)for poly in o.data.polygons],all_triangles=True)
    bvhs.append((o.name,bvh))
# Baseline terrain is read directly so every original basal contact can be
# compared without importing another full scene.
import struct,numpy as np
raw=a.baseline.read_bytes();jl=struct.unpack_from('<I',raw,12)[0];gj=json.loads(raw[20:20+jl]);gb=raw[28+jl:];gp=next(m for m in gj['meshes']if m['name']=='Spatial_Continuous_Weathered_Limestone')['primitives'][0]
def array(ac):
 ac=gj['accessors'][ac];bv=gj['bufferViews'][ac['bufferView']];cols={'VEC3':3,'SCALAR':1}[ac['type']];dt={5123:'<u2',5125:'<u4',5126:'<f4'}[ac['componentType']]
 return np.frombuffer(gb,dtype=dt,offset=bv['byteOffset'],count=ac['count']*cols).reshape(-1,cols)
bv=array(gp['attributes']['POSITION']);bf=array(gp['indices']).reshape(-1,3);baseline=BVHTree.FromPolygons([(float(q[0]),float(-q[2]),float(q[1]))for q in bv],bf.tolist(),all_triangles=True)
support_checks=[]
terrain=next(bvh for name,bvh in bvhs if name=='Spatial_Continuous_Weathered_Limestone')
for o in bpy.context.scene.objects:
    if not o.name.startswith('Spatial_Staghorn_Linked_'):continue
    roots=[o.matrix_world@v.co for v in o.data.vertices if v.co.z<=.045]
    gaps=[]
    for q in roots:
        co,n,idx,d=terrain.ray_cast(Vector((q.x,q.y,10)),Vector((0,0,-1)),12)
        assert co is not None,'Missing rock below added colony root'
        gaps.append(q.z-co.z)
    support_checks.append({'object':o.name,'basal_vertices_checked':len(roots),'maximum_root_above_rock_m':max(gaps),'minimum_root_above_rock_m':min(gaps)})
assert all(item['maximum_root_above_rock_m']<=.005 for item in support_checks),'Added colony root floats above limestone'
original_root_overlap=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not ('Staghorn' in o.name or o.name.startswith('Corridor_Distant_Linked_')) or o.name.startswith('Spatial_'):continue
    overlaps=[]
    for v in o.data.vertices:
        if v.co.z>.045:continue
        q=o.matrix_world@v.co
        if not(-24<q.x<24 and 11<q.y<61):continue
        co,n,idx,d=terrain.ray_cast(Vector((q.x,q.y,10)),Vector((0,0,-1)),12)
        if co is not None:overlaps.append(co.z-q.z)
    if overlaps:original_root_overlap.append({'object':o.name,'basal_vertices_checked':len(overlaps),'maximum_new_terrain_above_original_root_m':max(overlaps)})
assert all(q['maximum_new_terrain_above_original_root_m']<.11 for q in original_root_overlap),'New terrain buries original colony more than 11 cm'
minimum={'distance':float('inf')};by_object={}
for i,q in enumerate(points):
    for name,bvh in bvhs:
        co,n,idx,d=bvh.find_nearest(q,minimum['distance'])
        if co is not None and d<minimum['distance']:
            minimum={'distance':d,'sample':i,'progress':i/(len(points)-1),'camera_three':route['samples'][i],'object':name,'nearest_three':[co.x,co.z,-co.y]}
spacing=max((b-a).length for a,b in zip(points,points[1:]))
continuous_lower=minimum['distance']-spacing/2
# Nearest-triangle distance is 1-Lipschitz. Half maximum sample spacing bounds
# the sampled polyline. The smooth spline receives an additional 1 cm allowance;
# sample_route.mjs also records its sampled midpoint deviation. This is sampled
# static-camera QA, not a proof of every runtime camera/animation trajectory.
clearance=continuous_lower-.01
report={'model_sha256':hashlib.sha256(a.model.read_bytes()).hexdigest(),'curve':route['curve'],'samples':len(points),'static_mesh_objects':len(bvhs),'minimum_sampled_clearance':minimum,'maximum_sample_spacing_m':spacing,'conservative_path_clearance_m':clearance,'camera_sphere_radius_m':.45,'camera_sphere_has_clearance':clearance>.45,'added_colony_support_checks':support_checks,'exclusions':['Animated fish: checked by runtime route QA, not treated as terrain obstacles'],'coordinate_mapping':'glTF [x,y,z] to Blender [x,-z,y]','method':'Blender BVHTree exact nearest mesh-face distance; dense arc-length Three.js centripetal CatmullRom samples; conservative spacing and curvature allowance.'}
report['original_colony_root_overlap_checks']=original_root_overlap
contact_changes=[]
stable_geology=[b for name,b in bvhs if name!='Spatial_Continuous_Weathered_Limestone' and any(k in name for k in ['Sand','Hardbottom','Limestone'])]
for o in bpy.context.scene.objects:
 if o.type!='MESH'or not('Staghorn'in o.name or o.name.startswith('Corridor_Distant_Linked_')):continue
 diffs=[];terrain_diffs=[]
 for v in o.data.vertices:
  if v.co.z>.045:continue
  q=o.matrix_world@v.co
  if not(-24<q.x<24 and 11<q.y<61):continue
  origin=Vector((q.x,q.y,10));direction=Vector((0,0,-1));old=baseline.ray_cast(origin,direction,12)[0];new=terrain.ray_cast(origin,direction,12)[0]
  if old is not None and new is not None:
   terrain_diffs.append(abs(old.z-new.z))
   stable=[b.ray_cast(origin,direction,12)[0]for b in stable_geology];heights=[p.z for p in stable if p is not None]
   diffs.append(abs(max([old.z]+heights)-max([new.z]+heights)))
 if diffs:contact_changes.append({'object':o.name,'basal_vertices':len(diffs),'maximum_support_height_change_m':max(diffs),'maximum_underlying_terrain_height_change_m':max(terrain_diffs)})
report['baseline_basal_contact_comparison']=contact_changes
print('BASAL_CONTACT_DIFFERENCES',json.dumps(contact_changes),flush=True)
assert max(q['maximum_support_height_change_m']for q in contact_changes)<1e-5,'Actual basal support surface changed' 
report['method']='Blender BVHTree nearest mesh-face distance; 4,001 actual runtime getPoint spline samples; half-spacing subtraction plus 1 cm curvature allowance. Sampled static-camera check, not all runtime trajectories.'
report['maximum_sampled_midpoint_chord_deviation_m']=route.get('maximum_sampled_midpoint_chord_deviation_m')
a.output.write_text(json.dumps(report,indent=2));print('COLLISION_PROOF',json.dumps(report),flush=True)
assert clearance>.45,'Route camera sphere intersects terrain'
