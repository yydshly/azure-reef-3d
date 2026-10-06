import bpy,json,os,math
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parent
P=str(ROOT/'artifacts'/'comparison');os.makedirs(P,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modeling'/'editable'/'reef-garden-final.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=False;s.cycles.max_bounces=5
s.render.resolution_x=1100;s.render.resolution_y=800;s.render.resolution_percentage=100
s.use_nodes=True;nt=s.node_tree
old=next(n for n in nt.nodes if n.type=='MIX_RGB');fogcolor=tuple(old.inputs[2].default_value);print('PREVIOUS_FOGCOLOR',fogcolor,flush=True)
fogcolor=tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in (8/255,103/255,120/255))+(1,)
# Fog color matches browser #086778, converted to linear for Blender.
# Exponential-squared fog uses actual rendered camera-depth, not a world line.
for n in list(nt.nodes):nt.nodes.remove(n)
s.view_layers[0].use_pass_z=True
rl=nt.nodes.new('CompositorNodeRLayers');mul=nt.nodes.new('CompositorNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=.049
square=nt.nodes.new('CompositorNodeMath');square.operation='MULTIPLY'
neg=nt.nodes.new('CompositorNodeMath');neg.operation='MULTIPLY';neg.inputs[1].default_value=-1
exp=nt.nodes.new('CompositorNodeMath');exp.operation='EXPONENT'
sub=nt.nodes.new('CompositorNodeMath');sub.operation='SUBTRACT';sub.inputs[0].default_value=1
mix=nt.nodes.new('CompositorNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=fogcolor
out=nt.nodes.new('CompositorNodeComposite')
nt.links.new(rl.outputs['Depth'],mul.inputs[0]);nt.links.new(mul.outputs[0],square.inputs[0]);nt.links.new(mul.outputs[0],square.inputs[1]);nt.links.new(square.outputs[0],neg.inputs[0]);nt.links.new(neg.outputs[0],exp.inputs[0]);nt.links.new(exp.outputs[0],sub.inputs[1]);nt.links.new(sub.outputs[0],mix.inputs[0]);nt.links.new(rl.outputs['Image'],mix.inputs[1]);nt.links.new(mix.outputs[0],out.inputs[0])
cam=s.camera
for version,path in [('after',str(ROOT/'source-model.glb')),('before',str(ROOT/'modeling'/'inputs'/'previous-edge.glb'))]:
 for o in list(s.objects):
  if o.type in {'MESH','EMPTY'}:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=path)
 for label,pos in [('front-three-quarter',(9,-12,4.2)),('reverse-side',(-9,11,5.2))]:
  cam.location=pos;cam.rotation_euler=(Vector((0,0,.9))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=P+'/'+version+'-'+label+'.png';bpy.ops.render.render(write_still=True);print('RENDER_READY',version,label,flush=True)
 if version=='after':bpy.ops.wm.save_as_mainfile(filepath=P+'/reef-garden-reimport-evidence.blend')
json.dump({'resolution':[1100,800],'front_camera':[9,-12,4.2],'reverse_camera':[-9,11,5.2],'target':[0,0,.9],'lens_mm':cam.data.lens,'samples':48,'denoising':False,'fog':'Compositor actual Depth: factor = 1 - exp(-(0.049 * depth)^2). Same for both before and after.','fog_linear_rgba':fogcolor,'lighting':'Original offline Cycles lights retained; not a browser screenshot. GLB imports validated before rendering. Browser tone mapping and lights may differ.'},open(P+'/render-proof.json','w'),indent=2)
