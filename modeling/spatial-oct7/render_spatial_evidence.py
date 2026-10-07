"""Offline GLB reimport evidence only; browser water/light is not reproduced."""
import argparse, bpy, hashlib, json, math, re, sys
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('fixture',type=Path);p.add_argument('model',type=Path);p.add_argument('output',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.output.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(a.fixture.resolve()));s=bpy.context.scene
assert not any(o.type in {'MESH','EMPTY'} for o in s.objects)
materials={re.sub(r'\.\d{3}$','',m.name):m for m in bpy.data.materials}
bpy.ops.import_scene.gltf(filepath=str(a.model.resolve()))
for o in s.objects:
    if o.type=='MESH':
        for slot in o.material_slots:
            if slot.material:slot.material=materials[re.sub(r'\.\d{3}$','',slot.material.name)]
s.render.resolution_x=1120;s.render.resolution_y=700;s.render.resolution_percentage=100;s.cycles.samples=24;s.cycles.use_denoising=False
s.camera.data.type='PERSP';s.camera.data.lens=41.32;s.camera.data.sensor_width=36
views=[('departure',[1.5,2.1,4.8],[-.5,.8,-6]),('mid',[0,2.7,-18],[-1.5,1,-31]),('far-open',[-3.8,3.6,-36],[0,1.2,-50]),('far-look-back',[-3.8,3.6,-36],[0,.9,-8]),('overhead',[0,42,-30],[0,0,-30])]
for name,position,target in views:
    if name=='overhead':s.camera.data.type='ORTHO';s.camera.data.ortho_scale=64;s.use_nodes=False
    else:s.camera.data.type='PERSP';s.use_nodes=True
    s.camera.location=(position[0],-position[2],position[1]);t=Vector((target[0],-target[2],target[1]));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str((a.output/(name+'.png')).resolve());bpy.ops.render.render(write_still=True);print('RENDER_READY',name,flush=True)
report={'input_sha256':hashlib.sha256(a.model.read_bytes()).hexdigest(),'fixture_sha256':hashlib.sha256(a.fixture.read_bytes()).hexdigest(),'views':[{'name':n,'position':p,'target':t}for n,p,t in views],'samples':s.cycles.samples,'resolution':[1120,700],'disclosure':'Offline Cycles imported GLB with fixed prior evidence material/lighting fixture. Fish static. Runtime caustics, water/light changes and animated fish are not reproduced or verified. Overhead is a diagnostic orthographic view without depth fog.'}
(a.output/'render-manifest.json').write_text(json.dumps(report,indent=2))
