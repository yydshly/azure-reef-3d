"""Independent BVH checks on the actual exported terrain mesh."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
p=Path(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2]);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p.resolve()));o=bpy.data.objects['Spatial_Continuous_Weathered_Limestone'];vs=[o.matrix_world@v.co for v in o.data.vertices];faces=[tuple(f.vertices)for f in o.data.polygons];bvh=BVHTree.FromPolygons(vs,faces,all_triangles=True);pairs=bvh.overlap(bvh);nonadjacent=[]
for a,b in pairs:
 if a>=b or set(faces[a])&set(faces[b]):continue
 nonadjacent.append([a,b])
report={'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nonadjacent_triangle_intersections':len(nonadjacent),'intersecting_pairs':nonadjacent[:30],'method':'Blender BVH self-overlap on reimported terrain; pairs sharing a vertex excluded as intentional neighbors','guide_anchors':'The guide anchors are in unchanged foreground meshes; byte preservation of guide-data.js is checked separately.'};out.write_text(json.dumps(report,indent=2));print(json.dumps(report));assert not nonadjacent,'Self-intersection found'
