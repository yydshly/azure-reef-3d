"""Original interpretive reef solid: new topology, no source deformation or photo texture."""
import bpy,bmesh,json,math,hashlib,argparse,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);P=args.out.resolve();P.mkdir(parents=True,exist_ok=True);source=args.source.resolve()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source))
terrain=bpy.data.objects.get('Spatial_Continuous_Weathered_Limestone');assert terrain
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get();bvh=BVHTree.FromObject(terrain,dg)
def floor(x,z):
 m=terrain.matrix_world;start=m.inverted()@Vector((x,-z,15));direction=(m.inverted().to_3x3()@Vector((0,0,-1))).normalized();hit=bvh.ray_cast(start,direction,40)[0]
 assert hit is not None,(x,z)
 return (m@hit).z
# Hand-authored unequal, leaning polygonal bodies. Interpreted scene units.
measure=[];created=[]
def stone(name,x,z,rx,rz,top,phase=0):
 base=floor(x,z)-.28; high=floor(x,z)+top
 measure.append({'name':name,'xz':[x,z],'terrainY':floor(x,z),'bottomY':base,'topY':high})
 pts=[]
 # Irregular five-sided footprints and nonparallel top planes, not ellipsoids.
 profile=[(-.94,-.63),(.26,-1.0),(1,.02),(.62,.86),(-.79,.97)]
 for i,(a,b) in enumerate(profile):pts.append((x+a*rx,-z+b*rz,base+(.06 if i%2 else -.03)))
 for i,(a,b) in enumerate(profile):pts.append((x+(a*.78+.11)*rx,-z+(b*.81-.08)*rz,high+[.05,-.16,.13,-.07,-.23][(i+phase)%5]))
 bm=bmesh.new();vs=[bm.verts.new(p)for p in pts];bmesh.ops.convex_hull(bm,input=vs,use_existing_faces=False);bm.faces.ensure_lookup_table();bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
 me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);created.append(o);return o
# Support bodies overlap; upper extensions are shorter than the whole patch.
stone('Near_supported_face',5.15,-45.6,.94,1.16,.90,0)
stone('Recessed_middle_mass',6.42,-47.0,1.04,1.13,.70,2)
stone('Unequal_back_buttress',7.12,-48.7,.95,1.19,1.06,4)
stone('Low_cross_support',5.65,-47.5,.84,.84,.42,1)
# Deterministic solid union: original terrain remains untouched.
body=created[0];bpy.context.view_layer.objects.active=body
for o in created[1:]:
 mod=body.modifiers.new('Solid union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=o;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(o,do_unlink=True)
# Asymmetric side bites: low recess mouths, not a continuous roof/channel.
for i,(x,z,sx,sy,sz,raise_y) in enumerate([(4.72,-45.68,.66,.64,.36,.35),(5.72,-47.18,.70,.77,.40,.43),(6.58,-48.82,.64,.72,.44,.43)]):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,-z,floor(x,z)+raise_y));cut=bpy.context.object;cut.scale=(sx,sy,sz);cut.rotation_euler=(.2,-.12,.35+i*.31);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Irregular side recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
# Small chamfer only softens sharp mathematical intersections. No displacement/noise.
bpy.context.view_layer.objects.active=body
mod=body.modifiers.new('Weathered edge breadth','BEVEL');mod.width=.075;mod.segments=3;mod.limit_method='ANGLE';mod.angle_limit=.40
bpy.ops.object.modifier_apply(modifier=mod.name)
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=bm.faces);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);degenerate=sum(f.calc_area()<1e-10 for f in bm.faces);triangles=len(bm.faces);bm.to_mesh(body.data);bm.free()
body.name='Original_Solid_Late_Shoulder';body.data.name=body.name
for f in body.data.polygons:f.use_smooth=False
mat=bpy.data.materials.new('Neutral structural sample');mat.diffuse_color=(.43,.43,.43,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9;body.data.materials.clear();body.data.materials.append(mat)
for o in list(bpy.data.objects):
 if o!=body:bpy.data.objects.remove(o,do_unlink=True)
body.select_set(True);bpy.context.view_layer.objects.active=body
assert triangles<=20000 and boundary==0 and nonmanifold==0 and degenerate==0 and volume>0,(triangles,boundary,nonmanifold,degenerate,volume)
bpy.ops.export_scene.gltf(filepath=str(P/'solid-shoulder.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(P/'solid-shoulder.blend'))
proof={'scope':'Original inferred new solid topology; geometry gate only, not visual/scientific/runtime acceptance','sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'inputTerrainUnmodified':True,'supportMeasurements':measure,'trianglesAdded':triangles,'boundaryEdges':boundary,'nonmanifoldEdges':nonmanifold,'degenerateTriangles':degenerate,'signedVolume':volume,'units':'uncalibrated scene units','assetBytes':(P/'solid-shoulder.glb').stat().st_size}
(P/'geometry-proof.json').write_text(json.dumps(proof,indent=2));print('SOLID_READY',json.dumps(proof))
