import bpy,json,math,hashlib,struct,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
ROOT=Path(__file__).resolve().parent
P=str(ROOT/'artifacts'/'edge');os.makedirs(P,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'artifacts'/'reference'/'reef-garden-reference.blend'))
def signature(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('fff',*v.co))
 for p in o.data.polygons:h.update(struct.pack('I'*len(p.vertices),*p.vertices))
 h.update(str([list(row) for row in o.matrix_world]).encode())
 return h.hexdigest()
original={o.name:signature(o) for o in bpy.context.scene.objects if o.type=='MESH'}
hard=bpy.data.objects['Hardbottom_Low_Irregular_Limestone']; sand=bpy.data.objects['Sand_Rippled_32m'];under=bpy.data.objects['Sand_Horizon_80m']
bvh=BVHTree.FromPolygons([sand.matrix_world@v.co for v in sand.data.vertices],[list(p.vertices) for p in sand.data.polygons])
vs=hard.data.vertices;xmin=min(v.co.x for v in vs);xmax=max(v.co.x for v in vs);ymin=min(v.co.y for v in vs);ymax=max(v.co.y for v in vs)
edges=[];changes=[]
for v in vs:
 x,y,z=v.co;dist=min(x-xmin,xmax-x,y-ymin,ymax-y)
 # Vary the transition width rather than cutting a uniform inset around the grid.
 width=.74+.16*math.sin(x*2.7+y*1.9)+.075*math.sin(x*6.1-y*4.7)
 hit=bvh.ray_cast(Vector((x,y,2)),Vector((0,0,-1)))[0]
 if hit is None:raise RuntimeError('No sand beneath hardbottom')
 if dist<width:
  t=max(0,min(1,dist/width));s=t*t*(3-2*t);target=min(z,hit.z-.04)
  v.co.z=target*(1-s)+z*s
  if abs(v.co.z-z)>1e-7:changes.append({'vertex':v.index,'delta_z':v.co.z-z,'distance_to_boundary':dist})
 if dist<1e-5:edges.append({'vertex':v.index,'z':v.co.z,'sand_z':hit.z,'clearance':hit.z-v.co.z})
hard.data.update()
# Extend the same four underlay vertices; preserve normal and roughness density.
for v in under.data.vertices:v.co.x*=10;v.co.y*=10
for loop in under.data.uv_layers.active.data:loop.uv*=10
under.data.update()
unchanged={o.name:signature(o)==original[o.name] for o in bpy.context.scene.objects if o.type=='MESH' and o not in [hard,under]}
assert all(unchanged.values())
assert min(e['clearance'] for e in edges)>=.03999
for o in bpy.context.scene.objects:o.select_set(o.type in {'MESH','EMPTY'})
bpy.ops.export_scene.gltf(filepath=P+'/reef-garden-edge-blended.glb',export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT')
bpy.ops.wm.save_as_mainfile(filepath=P+'/reef-garden-edge-blended.blend')
proof={'source':'reef3d-reference-rebuild/final/reef-garden-reference.blend','hardbottom_vertex_count':len(vs),'hardbottom_face_count':len(hard.data.polygons),'modified_hardbottom_vertices':len(changes),'max_inward_change_distance_m':max(c['distance_to_boundary'] for c in changes),'max_lowering_m':-min(c['delta_z'] for c in changes),'boundary_vertices':len(edges),'boundary_z_range':[min(e['z'] for e in edges),max(e['z'] for e in edges)],'sampled_sand_z_range':[min(e['sand_z'] for e in edges),max(e['sand_z'] for e in edges)],'minimum_boundary_below_sand_m':min(e['clearance'] for e in edges),'maximum_boundary_below_sand_m':max(e['clearance'] for e in edges),'unchanged_mesh_geometry_and_world_transform_sha256':unchanged,'underlay_vertices':len(under.data.vertices),'underlay_extent_m':[-400,400],'materials_changed':False,'glb_bytes':os.path.getsize(P+'/reef-garden-edge-blended.glb')}
json.dump(proof,open(P+'/geometry-proof.json','w'),indent=2)
json.dump(edges,open(P+'/boundary-height-samples.json','w'),indent=2)
print('GLB_READY',P+'/reef-garden-edge-blended.glb',json.dumps(proof),flush=True)
