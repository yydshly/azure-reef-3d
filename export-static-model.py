"""Losslessly externalize GLB buffers, respecting the host's per-file limit."""
import hashlib
import json
import pathlib
import re
import struct

ASSET_ROOT = pathlib.Path('dist/assets')
BUFFER_BUDGET = 25_000_000
HOST_LIMIT = 26_214_400
raw = pathlib.Path('source-model.glb').read_bytes()
# Include packing implementation in the immutable URL identity as well as source.
model_id = hashlib.sha256(raw + pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
ASSETS = ASSET_ROOT / 'models' / model_id
ASSETS.mkdir(parents=True, exist_ok=True)
json_length = struct.unpack_from('<I', raw, 12)[0]
doc = json.loads(raw[20:20 + json_length])
start = 20 + json_length
binary_length, chunk_type = struct.unpack_from('<I4s', raw, start)
assert chunk_type == b'BIN\0'
binary = raw[start + 8:start + 8 + binary_length]
original_views = doc['bufferViews']
image_views = {im['bufferView'] for im in doc.get('images', []) if 'bufferView' in im}

def view_bytes(view):
    offset = view.get('byteOffset', 0)
    return binary[offset:offset + view['byteLength']]

for index, im in enumerate(doc.get('images', [])):
    view = original_views[im.pop('bufferView')]
    suffix = {'image/png': 'png', 'image/jpeg': 'jpg'}[im['mimeType']]
    name = f'reef-texture-{index}.{suffix}'
    (ASSETS / name).write_bytes(view_bytes(view))
    im['uri'] = name

# The authoritative source retains prior authoring data for provenance. Drop only
# unreferenced mesh/accessor records from the deployment, without changing any
# live scene attribute, index, material, node, skin or animation value.
assert 'KHR_draco_mesh_compression' not in doc.get('extensionsUsed', []), 'Compressed mesh externalization needs its own view handling'
used_meshes = sorted({node['mesh'] for node in doc.get('nodes', []) if 'mesh' in node})
mesh_map = {old: new for new, old in enumerate(used_meshes)}
doc['meshes'] = [doc['meshes'][index] for index in used_meshes]
for node in doc.get('nodes', []):
    if 'mesh' in node:
        node['mesh'] = mesh_map[node['mesh']]
used_accessors = set()
for mesh in doc['meshes']:
    for primitive in mesh['primitives']:
        used_accessors.update(primitive.get('attributes', {}).values())
        if 'indices' in primitive:
            used_accessors.add(primitive['indices'])
        for target in primitive.get('targets', []):
            used_accessors.update(target.values())
for skin in doc.get('skins', []):
    if 'inverseBindMatrices' in skin:
        used_accessors.add(skin['inverseBindMatrices'])
for animation in doc.get('animations', []):
    for sampler in animation['samplers']:
        used_accessors.update((sampler['input'], sampler['output']))
accessor_map = {old: new for new, old in enumerate(sorted(used_accessors))}
for mesh in doc['meshes']:
    for primitive in mesh['primitives']:
        primitive['attributes'] = {key: accessor_map[value] for key, value in primitive['attributes'].items()}
        if 'indices' in primitive:
            primitive['indices'] = accessor_map[primitive['indices']]
        for target in primitive.get('targets', []):
            for key, value in list(target.items()):
                target[key] = accessor_map[value]
for skin in doc.get('skins', []):
    if 'inverseBindMatrices' in skin:
        skin['inverseBindMatrices'] = accessor_map[skin['inverseBindMatrices']]
for animation in doc.get('animations', []):
    for sampler in animation['samplers']:
        sampler['input'] = accessor_map[sampler['input']]
        sampler['output'] = accessor_map[sampler['output']]
doc['accessors'] = [doc['accessors'][index] for index in sorted(used_accessors)]
used_views = set()
for accessor in doc['accessors']:
    if 'bufferView' in accessor:
        used_views.add(accessor['bufferView'])
    for value in accessor.get('sparse', {}).values():
        if isinstance(value, dict) and 'bufferView' in value:
            used_views.add(value['bufferView'])

new_views, buffers, mapping = [], [bytearray()], {}
for index, view in enumerate(original_views):
    if index not in used_views:
        continue
    payload = view_bytes(view)
    assert len(payload) <= BUFFER_BUDGET, 'One bufferView exceeds the bounded-buffer budget'
    aligned_size = (len(buffers[-1]) + 3) // 4 * 4
    if aligned_size + len(payload) > BUFFER_BUDGET:
        buffers.append(bytearray())
    data = buffers[-1]
    while len(data) % 4:
        data.append(0)
    updated = dict(view)
    updated['buffer'] = len(buffers) - 1
    updated['byteOffset'] = len(data)
    data.extend(payload)
    mapping[index] = len(new_views)
    new_views.append(updated)

for accessor in doc.get('accessors', []):
    if 'bufferView' in accessor:
        accessor['bufferView'] = mapping[accessor['bufferView']]
    for value in accessor.get('sparse', {}).values():
        if isinstance(value, dict) and 'bufferView' in value:
            value['bufferView'] = mapping[value['bufferView']]

names = ['reef.bin'] if len(buffers) == 1 else [f'reef-{i}.bin' for i in range(len(buffers))]
for name, data in zip(names, buffers):
    (ASSETS / name).write_bytes(data)
# Only remove obsolete outputs owned by this generator, never arbitrary assets.
for path in ASSETS.iterdir():
    if re.fullmatch(r'reef(?:-\d+)?\.bin', path.name) and path.name not in names:
        path.unlink()
doc['bufferViews'] = new_views
doc['buffers'] = [{'uri': name, 'byteLength': len(data)} for name, data in zip(names, buffers)]
(ASSETS / 'reef.gltf').write_text(json.dumps(doc, separators=(',', ':')))

# Verify every surviving original view byte-for-byte, including sparse data.
for old_index, new_index in mapping.items():
    view = new_views[new_index]
    offset = view['byteOffset']
    actual = buffers[view['buffer']][offset:offset + view['byteLength']]
    assert actual == view_bytes(original_views[old_index]), old_index
for path in ASSETS.iterdir():
    if path.is_file():
        assert path.stat().st_size <= HOST_LIMIT, (path, path.stat().st_size)
pathlib.Path('dist/model-version.js').write_text("export const MODEL_URL = './assets/models/" + model_id + "/reef.gltf';\n")
print(json.dumps({
    'model_url': './assets/models/' + model_id + '/reef.gltf',
    'source_glb_sha256': hashlib.sha256(raw).hexdigest(),
    'binary_bytes': sum(map(len, buffers)),
    'binary_buffers': {name: len(data) for name, data in zip(names, buffers)},
    'images': len(doc.get('images', [])),
    'lossless_externalization': True,
}))
