"""Matched old-fixture images, plus geology-only diagnostic views."""
import argparse,bpy,hashlib,json,re,sys
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('fixture',type=Path);p.add_argument('model',type=Path);p.add_argument('output',type=Path);p.add_argument('--diagnostic',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.output.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(a.fixture.resolve()));s=bpy.context.scene
assert not any(o.type in {'MESH','EMPTY'} for o in s.objects)
materials={re.sub(r'\.\d{3}$','',m.name):m for m in bpy.data.materials}
bpy.ops.import_scene.gltf(filepath=str(a.model.resolve()))
for o in s.objects:
    if o.type=='MESH':
        for slot in o.material_slots:
            if slot.material:slot.material=materials[re.sub(r'\.\d{3}$','',slot.material.name)]
        if a.diagnostic:o.hide_render=not(o.name.startswith(('Sand_','Hardbottom_','Distant_Limestone_','Spatial_Continuous_')))
s.render.resolution_x=1120;s.render.resolution_y=700;s.render.resolution_percentage=100;s.cycles.samples=24;s.cycles.use_denoising=False
s.camera.data.type='PERSP';s.camera.data.lens=41.32;s.camera.data.sensor_width=36
views=[('mid',[0,2.7,-18],[-1.5,1,-31]),('look-back',[-3.8,3.6,-36],[0,.9,-8])]
if a.diagnostic:
    views=[('terrain-front',[16,24,0],[0,0,-35]),('terrain-back',[-20,24,-73],[0,0,-35]),('terrain-overhead',[0,58,-36],[0,0,-36])]
    s.use_nodes=False;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=63
for name,position,target in views:
    s.camera.location=(position[0],-position[2],position[1]);t=Vector((target[0],-target[2],target[1]));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str((a.output/(name+'.png')).resolve());bpy.ops.render.render(write_still=True);print('RENDER_READY',name,flush=True)
report={'input_sha256':hashlib.sha256(a.model.read_bytes()).hexdigest(),'fixture_sha256':hashlib.sha256(a.fixture.read_bytes()).hexdigest(),'views':[{'name':n,'position':p,'target':t}for n,p,t in views],'samples':24,'resolution':[1120,700],'diagnostic':a.diagnostic,'disclosure':'Offline Cycles reimport, same old fixture, camera, light and materials in before/after. Static fish. No runtime water, caustics, UI or animations. Terrain diagnostics hide biology and omit depth fog only.'}
(a.output/'render-manifest.json').write_text(json.dumps(report,indent=2))
