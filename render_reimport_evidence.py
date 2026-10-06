import bpy,json,os
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parent
P=str(ROOT/'artifacts'/'renders');os.makedirs(P,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modeling'/'editable'/'reef-garden-final.blend'))
for o in list(bpy.context.scene.objects):
 if o.type in {'MESH','EMPTY'}:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'source-model.glb'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=80;s.cycles.use_denoising=False;s.cycles.max_bounces=5
s.render.resolution_x=1100;s.render.resolution_y=800;s.render.resolution_percentage=100
# Retain original offline lighting and mist for an honest same-camera comparison.
cam=s.camera
for label,pos in [('offline-front-three-quarter',(9,-12,4.2)),('offline-reverse-side',(-9,11,5.2))]:
 cam.location=pos;cam.rotation_euler=(Vector((0,0,.9))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=P+'/'+label+'.png';bpy.ops.render.render(write_still=True);print('RENDER_READY',label,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=P+'/reef-garden-reimport-evidence.blend')
print('REIMPORT_EVIDENCE_COMPLETE',flush=True)
