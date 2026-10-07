"""Import the final GLB and measure the full Three.js route against static mesh faces."""
import argparse,bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('model',type=Path);p.add_argument('route',type=Path);p.add_argument('output',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(a.model.resolve()))
route=json.loads(a.route.read_text());points=[Vector((q[0],-q[2],q[1]))for q in route['samples']]
bvhs=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.name.startswith('fish_'):continue
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    bvh=BVHTree.FromPolygons(vs,[tuple(poly.vertices)for poly in o.data.polygons],all_triangles=True)
    bvhs.append((o.name,bvh))
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
minimum={'distance':float('inf')};by_object={}
for i,q in enumerate(points):
    for name,bvh in bvhs:
        co,n,idx,d=bvh.find_nearest(q,minimum['distance'])
        if co is not None and d<minimum['distance']:
            minimum={'distance':d,'sample':i,'progress':i/(len(points)-1),'camera_three':route['samples'][i],'object':name,'nearest_three':[co.x,co.z,-co.y]}
spacing=max((b-a).length for a,b in zip(points,points[1:]))
continuous_lower=minimum['distance']-spacing/2
# Nearest-triangle distance is 1-Lipschitz. Half maximum sample spacing gives
# a conservative continuous bound for the sampled polyline. The smooth spline
# receives an extra 1 cm allowance, larger than observed local curve sag.
clearance=continuous_lower-.01
report={'model_sha256':hashlib.sha256(a.model.read_bytes()).hexdigest(),'curve':route['curve'],'samples':len(points),'static_mesh_objects':len(bvhs),'minimum_sampled_clearance':minimum,'maximum_sample_spacing_m':spacing,'conservative_path_clearance_m':clearance,'camera_sphere_radius_m':.45,'camera_sphere_has_clearance':clearance>.45,'added_colony_support_checks':support_checks,'exclusions':['Animated fish: checked by runtime route QA, not treated as terrain obstacles'],'coordinate_mapping':'glTF [x,y,z] to Blender [x,-z,y]','method':'Blender BVHTree exact nearest mesh-face distance; dense arc-length Three.js centripetal CatmullRom samples; conservative spacing and curvature allowance.'}
a.output.write_text(json.dumps(report,indent=2));print('COLLISION_PROOF',json.dumps(report),flush=True)
assert clearance>.45,'Route camera sphere intersects terrain'
