"""Bounded geometry resampling of an authored solid. Not calibrated erosion physics."""
import bpy,bmesh,json,hashlib,math,argparse,sys
from pathlib import Path
from mathutils import Vector,noise
from mathutils.bvhtree import BVHTree
parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--input-solid',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);P=args.out.resolve();P.mkdir(parents=True,exist_ok=True);src=args.source.resolve();asset=args.input_solid.resolve()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(src));t=bpy.data.objects['Spatial_Continuous_Weathered_Limestone'];bpy.context.view_layer.update();bvh=BVHTree.FromObject(t,bpy.context.evaluated_depsgraph_get());matrix=t.matrix_world.copy();inv=matrix.inverted()
def floor(x,y):
 hit=bvh.ray_cast(inv@Vector((x,y,15)),(inv.to_3x3()@Vector((0,0,-1))).normalized(),40)[0]
 return (matrix@hit).z if hit else -1
old=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(asset));o=next(v for v in set(bpy.context.scene.objects)-old if v.type=='MESH');bpy.context.view_layer.objects.active=o
# Spatial remesh creates evenly sized faces across the formerly broad planes.
m=o.modifiers.new('Volume resampling','REMESH');m.mode='VOXEL';m.voxel_size=.065;m.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=m.name)
maxmove=0;protected=0
for v in o.data.vertices:
 p=o.matrix_world@v.co;h=p.z-floor(p.x,p.y);q=max(0,min(1,(h-.06)/.30));w=q*q*(3-2*q)
 if w==0:protected+=1
 # Smooth spatial warp at two declared geometric scales, not a texture normal.
 # Same field on outer faces and recesses avoids independently pasted patches.
 d=(noise.noise_vector(p*.95,noise_basis='PERLIN_ORIGINAL')*.21+noise.noise_vector(p*4.3+Vector((4,9,2)),noise_basis='PERLIN_ORIGINAL')*.05)*w
 maxmove=max(maxmove,d.length);v.co+=o.matrix_world.inverted().to_3x3()@d
# Preserve enough geometry to keep the irregular silhouette without huge new cost.
m=o.modifiers.new('Count actual triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=m.name)
m=o.modifiers.new('Bounded topology budget','DECIMATE');m.ratio=min(1,18000/max(1,len(o.data.polygons)));bpy.ops.object.modifier_apply(modifier=m.name)
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
unseen=set(bm.verts);components=[]
while unseen:
 seed=unseen.pop();stack=[seed];n=0
 while stack:
  v=stack.pop();n+=1
  for e in v.link_edges:
   w=e.other_vert(v)
   if w in unseen:unseen.remove(w);stack.append(w)
 components.append(n)
proof={'triangles':len(bm.faces),'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonmanifoldEdges':sum(not e.is_manifold for e in bm.edges),'degenerateTriangles':sum(f.calc_area()<1e-10 for f in bm.faces),'signedVolume':bm.calc_volume(signed=True),'components':components,'maxWarpDistance':maxmove,'buriedVerticesProtected':protected,'voxelSize':.065,'units':'uncalibrated scene units','scope':'Geometric surface reconstruction, not physical erosion or visual acceptance'}
bm.to_mesh(o.data);bm.free();o.name='Original_Resampled_Reef_Solid';o.data.name=o.name
for f in o.data.polygons:f.use_smooth=True
for ob in list(bpy.data.objects):
 if ob!=o:bpy.data.objects.remove(ob,do_unlink=True)
o.select_set(True);bpy.context.view_layer.objects.active=o
assert proof['boundaryEdges']==0 and proof['nonmanifoldEdges']==0 and proof['degenerateTriangles']==0
bpy.ops.export_scene.gltf(filepath=str(P/'volume-shoulder.glb'),export_format='GLB',use_selection=True,export_yup=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(P/'volume-shoulder.blend'))
proof['sourceAssetHash']=hashlib.sha256(asset.read_bytes()).hexdigest();proof['assetBytes']=(P/'volume-shoulder.glb').stat().st_size;(P/'geometry-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
