import bpy,math,random,json,hashlib,struct,os
from mathutils import Vector,Matrix
from pathlib import Path
ROOT=Path(__file__).resolve().parent
P=str(ROOT/'artifacts'/'depth');os.makedirs(P,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'artifacts'/'edge'/'reef-garden-edge-blended.blend'))
def signature(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('fff',*v.co))
 for p in o.data.polygons:h.update(struct.pack('I'*len(p.vertices),*p.vertices))
 h.update(str([list(row) for row in o.matrix_world]).encode()); return h.hexdigest()
original={o.name:signature(o) for o in bpy.context.scene.objects if o.type=='MESH'}
random.seed(613)
mat=bpy.data.materials['Limestone | reference-led porous PBR']
# Low, closed irregular rock rises: no flat backdrop, no new species.
placements=[(-10,3,2.3,1.9,.50,.3),(1.5,12,3.1,2.0,.64,-.6),(11,8,2.3,2.7,.42,.8),(-12,15,3.3,2.5,.65,.5),(10,21,3.8,2.8,.57,-.4),(-20,2,3.0,2.5,.52,.7),(-3,-14,3.1,2.1,.46,-.9),(14,-9,2.8,1.9,.58,.2),(-15,-11,2.5,2.4,.43,-.5)]
verts=[];faces=[];colors=[]
N=48;R=15
for k,(cx,cy,rx,ry,h,rot) in enumerate(placements):
 start=len(verts)
 # Rings run over an oblate closed rock, including its hidden underside.
 for i in range(R+1):
  phi=math.pi*i/R;rr=math.sin(phi);zz=math.cos(phi)
  for j in range(N):
   a=2*math.pi*j/N
   irregular=1+.13*math.sin(3*a+k*1.7)+.07*math.sin(7*a-k)+.035*math.cos(11*a+k)
   x=rx*rr*math.cos(a)*irregular;y=ry*rr*math.sin(a)*irregular
   z=-.24+(h+.24)*zz
   if zz>0:z+=.055*math.sin(x*3.3+y*2.5+k)*rr+.035*math.cos(x*5-y*4)*rr
   verts.append((cx+x*math.cos(rot)-y*math.sin(rot),cy+x*math.sin(rot)+y*math.cos(rot),z))
   shade=.80+.12*math.sin(x*2.2+y*3.7+k)+.045*random.random()
   colors.append((.23*shade,.255*shade,.19*shade,1))
 for i in range(R):
  for j in range(N):
   a=start+i*N+j;b=start+i*N+(j+1)%N;c=b+N;d=a+N;faces.append((a,d,c,b))
mesh=bpy.data.meshes.new('Depth_Hardbottom_Closed_Irregular_Rises');mesh.from_pydata(verts,[],faces);mesh.materials.append(mat);mesh.update()
obj=bpy.data.objects.new('Depth_Hardbottom_Closed_Irregular_Rises',mesh);bpy.context.collection.objects.link(obj)
col=mesh.color_attributes.new(name='ReefColor',type='FLOAT_COLOR',domain='POINT')
for i,c in enumerate(colors):col.data[i].color=c
uv=mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
 poly.use_smooth=True
 for li in poly.loop_indices:
  v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v.x/3,v.y/3)
# Shared original staghorn meshes: transforms varied, no topology copy.
instances=[]
for k,(cx,cy,rx,ry,h,rot) in enumerate(placements):
 offsets=[(-.55,-.12),(.65,.30)] if k in [0,1,3] else [(0,.05)]
 for j,(dx,dy) in enumerate(offsets):
  index=[14,8,0,12,5,17,2,4,16][k]
  if j:index=(index+3)%22
  src=bpy.data.objects[f'Coral_Staghorn_Thicket_{index:02d}'];o=src.copy();o.data=src.data;o.name=f'Depth_Staghorn_Linked_{k:02d}_{j}';bpy.context.collection.objects.link(o)
  vs=src.data.vertices;center=Vector(((min(v.co.x for v in vs)+max(v.co.x for v in vs))/2,(min(v.co.y for v in vs)+max(v.co.y for v in vs))/2,0))
  scale=[.88,.95,.82,.92,.78,.74,.83,.9,.77][k]*(1 if j==0 else .76)
  angle=rot+k*.83+j*2.1
  # Coral starts on each genuine low rock rise.
  o.matrix_world=Matrix.Translation(Vector((cx+dx,cy+dy,h-.05)))@Matrix.Rotation(angle,4,'Z')@Matrix.Diagonal((scale,scale*(.92+.025*k),scale,1))@Matrix.Translation(-center)
  instances.append({'name':o.name,'source':src.name,'shared_mesh':o.data==src.data,'world_translation':list(o.location),'scale':scale})
unchanged={name:signature(bpy.data.objects[name])==sig for name,sig in original.items()};assert all(unchanged.values())
for o in bpy.context.scene.objects:o.select_set(o.type in {'MESH','EMPTY'})
bpy.ops.export_scene.gltf(filepath=P+'/reef-garden-spatial-depth.glb',export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_texcoords=True,export_normals=True,export_materials='EXPORT')
bpy.ops.wm.save_as_mainfile(filepath=P+'/reef-garden-spatial-depth.blend')
proof={'source':'reef3d-edge-pass/reef-garden-edge-blended.blend','provenance':'Original procedural closed hardbottom rises and linked copies of existing procedural staghorn meshes. NOAA reference images informed restraint and morphology only. The generated reference image informed spatial composition only. Unseen geometry is inferred, not image-reconstructed.','new_unique_vertices':len(verts),'new_rock_faces':len(faces),'added_objects':1+len(instances),'original_geometry_and_transforms_unchanged':unchanged,'placements':placements,'instances':instances,'materials_changed':False,'glb_bytes':os.path.getsize(P+'/reef-garden-spatial-depth.glb')}
json.dump(proof,open(P+'/geometry-proof.json','w'),indent=2)
print('GLB_READY',proof['glb_bytes'],flush=True)
