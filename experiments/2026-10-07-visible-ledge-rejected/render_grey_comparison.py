"""Fixed grey OFFLINE Cycles evidence, never a runtime or science-validation claim."""
import argparse, bpy, hashlib, json, math, sys
from pathlib import Path
from mathutils import Vector

p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('candidate',type=Path);p.add_argument('landmark',type=Path);p.add_argument('output',type=Path);p.add_argument('--view',default='actual-route-75');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.output.mkdir(parents=True,exist_ok=True)

# One immutable lighting/camera setup used for both geometry variants.
views=[
    ('actual-route-75',[-2.208167284183959,3.259500550508243,-30.006196517022275],[-3.835229074543919,.7,-42.26543655798051], 'PERSP',47.0),
    ('actual-route-92',[-3.8,3.6,-36],[12.158926956576405,.7,-42.51154851389471], 'PERSP',47.0),
    ('neutral-reverse',[16.0,7.0,-51.0],[6.0,.8,-47.5], 'ORTHO',17.0),
]

views=[v for v in views if v[0]==a.view]
def to_blender(p):return Vector((p[0],-p[2],p[1]))
def material(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(*color,1);bsdf.inputs['Roughness'].default_value=.92
    return m

manifest={'scope':'OFFLINE fixed neutral grey structural comparison, not browser/runtime evidence. No water, caustics, textures, changing lighting or animation.',
          'resolution':[800,500],'samples':24,'views':views,'landmark_pose_y_up':{'position':[3.5,-.015196346640586854,-44],'yaw':1.3,'omitted':'Attached_reticulate_fan_form','retained':'Attached_small_fan_form'},
          'models':{},'units':'interpreted scene units'}
for label,path in [('before',a.source),('after',a.candidate)]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False
    s.render.resolution_x=800;s.render.resolution_y=500;s.render.resolution_percentage=100
    s.world=bpy.data.worlds.new('Fixed neutral world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.21,.21,.21,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
    s.view_settings.view_transform='AgX'
    grey=material('Fixed grey rock',(.43,.43,.43));ground=material('Fixed pale grey sand',(.58,.58,.58));coral=material('Fixed grey biological geometry',(.34,.34,.34))
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()))
    # Include the unmodified source context, with the same runtime pruning.
    for o in list(s.objects):
        if o.name.startswith('Coral_Staghorn_Thicket_'):
            try:k=int(o.name.rsplit('_',1)[-1].split('.')[0])
            except ValueError:k=-1
            if k not in [0,1,3,12,16]:bpy.data.objects.remove(o,do_unlink=True);continue
        if o.type=='MESH':
            m=ground if 'Sand' in o.name else coral if ('Staghorn' in o.name or 'Coral' in o.name) else grey
            o.data.materials.clear();o.data.materials.append(m)
    prior=set(s.objects)
    bpy.ops.import_scene.gltf(filepath=str(a.landmark.resolve()))
    imported=set(s.objects)-prior
    for o in list(imported):
        if o.name.startswith('Attached_reticulate_fan_form'):
            imported.remove(o)
            bpy.data.objects.remove(o,do_unlink=True);continue
        if o.type=='MESH':o.data.materials.clear();o.data.materials.append(grey)
    # glTF Y-up yaw becomes rotation around Blender +Z.
    group=bpy.data.objects.new('Exact accepted FarRight pose',None);s.collection.objects.link(group)
    group.location=to_blender([3.5,-.015196346640586854,-44]);group.rotation_euler[2]=1.3
    for o in imported:
        if o.name in s.objects and o.parent is None:o.parent=group
    for name,pos,energy,size in [('Large key',[-3,20,-34],2100,12),('Large fill',[18,13,-48],1350,10)]:
        d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=to_blender(pos);o.rotation_euler=(to_blender([9,0,-43])-o.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.cameras.new('Matched camera');camera=bpy.data.objects.new('Matched camera',d);s.collection.objects.link(camera);s.camera=camera
    for name,position,target,kind,value in views:
        camera.location=to_blender(position);camera.rotation_euler=(to_blender(target)-camera.location).to_track_quat('-Z','Y').to_euler();d.type=kind
        if kind=='ORTHO':d.ortho_scale=value
        else:
            d.sensor_fit='HORIZONTAL';d.sensor_width=36;d.lens=36/(2*math.tan(math.radians(value)/2)*(800/500))
        s.render.filepath=str((a.output/(label+'-'+name+'.png')).resolve());bpy.ops.render.render(write_still=True)
        print('RENDER_READY',label,name,flush=True)
    manifest['models'][label]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
manifest['landmark_sha256']=hashlib.sha256(a.landmark.read_bytes()).hexdigest()
(a.output/('render-manifest-'+a.view+'.json')).write_text(json.dumps(manifest,indent=2)+'\n')
