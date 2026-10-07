"""Matched Cycles specimen renders, explicitly not the production water shader."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector, Matrix
P = Path(__file__).resolve().parent
data = json.loads((P.parents[1] / 'evidence/fish-surface-oct7/preview-input.json').read_text())
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s = bpy.context.scene
s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = 32
s.cycles.use_denoising = False; s.cycles.max_bounces = 4
s.render.resolution_x = 800; s.render.resolution_y = 560; s.render.resolution_percentage = 100
s.render.image_settings.file_format = 'PNG'; s.render.film_transparent = False
s.world.use_nodes = True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.075, .115, .12, 1)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .5
s.view_settings.view_transform = 'AgX'
def area(name, xyz, energy, size):
    d = bpy.data.lights.new(name, 'AREA'); d.energy = energy; d.shape = 'DISK'; d.size = size
    o = bpy.data.objects.new(name, d); s.collection.objects.link(o); o.location = xyz
    o.rotation_euler = (Vector((-.15, .06, 0)) - o.location).to_track_quat('-Z', 'Y').to_euler()
area('Fixed upper key', (1.4, 2.6, 3.4), 230, 3)
area('Fixed reverse fill', (-1.1, .8, -3.6), 170, 3)
d = bpy.data.cameras.new('Diagnostic specimen camera'); cam = bpy.data.objects.new('Diagnostic specimen camera', d); s.collection.objects.link(cam); s.camera = cam
d.type = 'ORTHO'; d.ortho_scale = 1.95
def material(obj, candidate):
    m = bpy.data.materials.new(('candidate ' if candidate else 'baseline ') + obj['name']); m.use_nodes = True
    nt = m.node_tree; nodes = nt.nodes; links = nt.links; bs = nodes.get('Principled BSDF'); bs.inputs['Roughness'].default_value = .7200000286102295
    vc = nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Source pigment'
    links.new(vc.outputs['Color'], bs.inputs['Base Color'])
    def op(operation, a, b=None, c=None):
        node = nodes.new('ShaderNodeMath'); node.operation = operation
        for i, value in enumerate([a, b, c]):
            if value is None: continue
            if isinstance(value, (int, float)): node.inputs[i].default_value = value
            else: links.new(value, node.inputs[i])
        return node.outputs[0]
    def smooth(x, low, high):
        t = op('MINIMUM', op('MAXIMUM', op('DIVIDE', op('SUBTRACT', x, low), high-low), 0), 1)
        return op('MULTIPLY', op('MULTIPLY', t, t), op('SUBTRACT', 3, op('MULTIPLY', 2, t)))
    def vec(components):
        n = nodes.new('ShaderNodeCombineXYZ')
        for i, v in enumerate(components):
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: links.new(v, n.inputs[i])
        return n.outputs[0]
    if candidate and obj['name'].endswith('_body'):
        tc = nodes.new('ShaderNodeTexCoord'); sep = nodes.new('ShaderNodeSeparateXYZ'); links.new(tc.outputs['Object'], sep.inputs[0]); x,y,z = sep.outputs
        yy = op('DIVIDE', y, .32); zz = op('DIVIDE', z, .15)
        height = op('DIVIDE', yy, op('MAXIMUM', op('SQRT', op('ADD', op('MULTIPLY', yy, yy), op('MULTIPLY', zz, zz))), .00001))
        band = op('SINE', op('ADD', op('MULTIPLY', x, 34), op('MULTIPLY', y, 3)))
        pigment = smooth(band, .44, .68)
        ramps = [vec([op('ADD', p['center'][i], op('MULTIPLY', p['slope'][i], height)) for i in range(3)]) for p in data['palette']]
        mix = nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MIX'; links.new(pigment, mix.inputs[0]); links.new(ramps[0], mix.inputs[1]); links.new(ramps[1], mix.inputs[2]); links.new(mix.outputs[0], bs.inputs['Base Color'])
    elif candidate and obj['finCoords']:
        uv = nodes.new('ShaderNodeUVMap'); uv.uv_map = 'FishFinCoord'
        sep = nodes.new('ShaderNodeSeparateXYZ'); links.new(uv.outputs[0], sep.inputs[0]); x,y,_ = sep.outputs
        phase = op('MULTIPLY', op('ARCTAN2', y, op('MAXIMUM', x, .00001)), 30)
        wave = op('ADD', .5, op('MULTIPLY', .5, op('COSINE', phase)))
        ray = smooth(wave, .71, .89)
        length = op('SQRT', op('ADD', op('MULTIPLY', x, x), op('MULTIPLY', y, y)))
        factor = op('ADD', .94, op('MULTIPLY', .095, op('MULTIPLY', ray, smooth(length, .04, .25))))
        mix = nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1; links.new(vc.outputs['Color'], mix.inputs[1]); links.new(factor, mix.inputs[2]); links.new(mix.outputs[0], bs.inputs['Base Color'])
    return m
for mode in ['baseline', 'candidate']:
    for obj in data[mode]:
        me = bpy.data.meshes.new(obj['name']); verts = [obj['positions'][i:i+3] for i in range(0, len(obj['positions']), 3)]; faces = [obj['indices'][i:i+3] for i in range(0, len(obj['indices']), 3)]
        me.from_pydata(verts, [], faces); me.update()
        col = me.color_attributes.new(name='Source pigment', type='FLOAT_COLOR', domain='POINT')
        for i, v in enumerate(col.data): v.color = (*obj['colors'][i*3:i*3+3], 1)
        for poly in me.polygons: poly.use_smooth = True
        me.normals_split_custom_set_from_vertices([obj['normals'][i:i+3] for i in range(0, len(obj['normals']), 3)])
        if obj['finCoords']:
            uv = me.uv_layers.new(name='FishFinCoord')
            for loop in me.loops: uv.data[loop.index].uv = obj['finCoords'][loop.vertex_index*2:loop.vertex_index*2+2]
        ob = bpy.data.objects.new(obj['name'], me); s.collection.objects.link(ob); ob.data.materials.append(material(obj, mode == 'candidate'))
    for label, pos in [('side', (.15,.15,3.0)), ('reverse-quarter', (-1.8,.5,-3.0))]:
        cam.location = pos
        direction = (Vector((-.16,.04,0)) - cam.location).normalized()
        right = direction.cross(Vector((0,1,0))).normalized(); up = right.cross(direction).normalized()
        cam.rotation_euler = Matrix((right, up, -direction)).transposed().to_quaternion().to_euler()
        s.render.filepath = str(P / ('offline-' + mode + '-' + label + '.png')); bpy.ops.render.render(write_still=True)
        print('OFFLINE_FRAME_READY', mode, label, flush=True)
    for ob in list(s.objects):
        if ob.type == 'MESH': bpy.data.objects.remove(ob, do_unlink=True)
(P / 'offline-render-disclosure.json').write_text(json.dumps({'renderer': 'Blender '+bpy.app.version_string+' Cycles CPU', 'source': 'preview-input.json exported from actual JS prototype', 'samples': 32, 'matchedCamerasAndLighting': True, 'bodyPositionAndNormals': 'actual source arrays, unchanged', 'candidatePigment': 'same analytic phase and fitted source palette, offline derivative-free node equivalent', 'finRays': 'same low-contrast analytic field, offline derivative-free node equivalent', 'notIncluded': ['production water/caustic shader', 'WebGL shader compilation', 'browser pixel behavior', 'physical GPU performance', 'live animation'], 'provenance': 'Original authored geometry/shading only; no reference photographs included'}, indent=2))
