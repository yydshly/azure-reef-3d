"""Narrow sand-to-horizon continuity patch. Python 3 standard library only.

Usage: python patch_sand_boundary.py source-frozen.glb sand-continuous.glb
The input is pinned; only main-sand POSITION.y and affected NORMAL bytes change.
No Blender export/repacking or material experiments enter this output.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import struct

SOURCE_SHA = 'ce6a7bc4d005ecd794d378c792d5d05d79f4683b10a2d3446333e6053ead4d21'
BAND_M = 2.0

def digest(value):
    return hashlib.sha256(value).hexdigest()

def read_glb(path):
    raw = Path(path).read_bytes()
    assert raw[:4] == b'glTF' and struct.unpack_from('<I', raw, 4)[0] == 2
    length = struct.unpack_from('<I', raw, 12)[0]
    assert raw[16:20] == b'JSON' and raw[24+length:28+length] == b'BIN\0'
    return raw, json.loads(raw[20:20+length]), bytearray(raw[28+length:])

def accessor_bytes(gltf, binary, index):
    a = gltf['accessors'][index]
    view = gltf['bufferViews'][a['bufferView']]
    width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
    size = {5121: 1, 5123: 2, 5125: 4, 5126: 4}[a['componentType']]
    assert 'byteStride' not in view
    start = view.get('byteOffset', 0) + a.get('byteOffset', 0)
    return bytes(binary[start:start+a['count']*width*size])

def vectors(gltf, binary, index):
    a = gltf['accessors'][index]
    assert a['componentType'] == 5126 and a['type'] == 'VEC3'
    return list(struct.iter_unpack('<fff', accessor_bytes(gltf, binary, index)))

def quintic(t):
    """C2 smoothstep, with exact constant ends."""
    if t <= 0:
        return 0.0, 0.0
    if t >= 1:
        return 1.0, 0.0
    return t*t*t*(10+t*(-15+6*t)), 30*t*t*(t-1)*(t-1)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raw, gltf, binary = read_glb(args.source)
    assert digest(raw) == SOURCE_SHA, 'Input does not match the frozen approved source'
    old_gltf, old_binary = copy.deepcopy(gltf), bytes(binary)
    node = next(n for n in gltf['nodes'] if n.get('name') == 'Sand_Rippled_32m')
    assert not any(k in node for k in ('matrix', 'rotation', 'scale', 'translation'))
    prim = gltf['meshes'][node['mesh']]['primitives'][0]
    pi, ni = prim['attributes']['POSITION'], prim['attributes']['NORMAL']
    floor_node = next(n for n in gltf['nodes'] if n.get('name') == 'Sand_Horizon_80m')
    floor_prim = gltf['meshes'][floor_node['mesh']]['primitives'][0]
    floor_positions = vectors(gltf, binary, floor_prim['attributes']['POSITION'])
    floor_y = floor_positions[0][1]
    assert all(p[1] == floor_y for p in floor_positions)
    p = vectors(gltf, binary, pi)
    n = vectors(gltf, binary, ni)
    changed, edge = [], []
    for i, ((x, y, z), (nx, ny, nz)) in enumerate(zip(p, n)):
        dx, dz = 16.0-abs(x), 16.0-abs(z)
        if min(dx, dz) >= BAND_M:
            continue
        fx, dfx = quintic(dx/BAND_M)
        fz, dfz = quintic(dz/BAND_M)
        weight = fx*fz
        # Product falloff avoids the diagonal crease created by min-distance.
        wx = -math.copysign(1, x)*dfx*fz/BAND_M
        wz = -math.copysign(1, z)*dfz*fx/BAND_M
        new_y = floor_y + (y-floor_y)*weight
        # Transform the original smooth tangent plane through the height blend.
        # This preserves its exact shading at the core, and becomes exactly up
        # at the outer edge, matching the unchanged far-floor normals.
        gx = weight*(-nx/ny) + (y-floor_y)*wx
        gz = weight*(-nz/ny) + (y-floor_y)*wz
        length = math.sqrt(gx*gx+1+gz*gz)
        new_n = (-gx/length, 1/length, -gz/length)
        if dx == 0 or dz == 0:
            new_y, new_n = floor_y, (0.0, 1.0, 0.0)
            edge.append(i)
        pa = gltf['accessors'][pi]
        na = gltf['accessors'][ni]
        po = gltf['bufferViews'][pa['bufferView']].get('byteOffset', 0) + pa.get('byteOffset', 0)
        no = gltf['bufferViews'][na['bufferView']].get('byteOffset', 0) + na.get('byteOffset', 0)
        # Preserve the x/z bytes, and every unmodified core vertex byte.
        struct.pack_into('<f', binary, po+i*12+4, new_y)
        struct.pack_into('<fff', binary, no+i*12, *new_n)
        changed.append({'vertex': i, 'distance_to_edge_m': min(dx, dz), 'lowering_m': y-new_y})
    pp, nn = vectors(gltf, binary, pi), vectors(gltf, binary, ni)
    gltf['accessors'][pi]['min'] = [min(v[k] for v in pp) for k in range(3)]
    gltf['accessors'][pi]['max'] = [max(v[k] for v in pp) for k in range(3)]
    checks = []
    for i in range(len(gltf['accessors'])):
        before = accessor_bytes(old_gltf, old_binary, i)
        after = accessor_bytes(gltf, binary, i)
        checks.append({'accessor': i, 'before_sha256': digest(before), 'after_sha256': digest(after), 'unchanged': before == after})
        if i not in (pi, ni):
            assert before == after
    expected = copy.deepcopy(old_gltf)
    expected['accessors'][pi] = gltf['accessors'][pi]
    assert gltf == expected, 'Unexpected JSON scene change'
    ranges = []
    for index in (pi, ni):
        view = gltf['bufferViews'][gltf['accessors'][index]['bufferView']]
        ranges.append((view.get('byteOffset', 0), view.get('byteOffset', 0)+view['byteLength']))
    for lo, hi in zip([0]+[b for a,b in sorted(ranges)], [a for a,b in sorted(ranges)]+[len(binary)]):
        assert binary[lo:hi] == old_binary[lo:hi]
    assert all(pp[i] == p[i] and nn[i] == n[i] for i in range(len(p)) if min(16-abs(p[i][0]), 16-abs(p[i][2])) >= BAND_M)
    assert all(pp[i][1] == floor_y and nn[i] == (0.0, 1.0, 0.0) for i in edge)
    jb = json.dumps(gltf, separators=(',', ':')).encode()
    jb += b' '*((-len(jb))%4)
    output = struct.pack('<4sII', b'glTF', 2, 28+len(jb)+len(binary)) + struct.pack('<I4s', len(jb), b'JSON') + jb + struct.pack('<I4s', len(binary), b'BIN\0') + binary
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)
    proof = {
        'source_sha256': SOURCE_SHA, 'output_sha256': digest(output),
        'bytes': len(output), 'band_width_m': BAND_M,
        'surface_formula': 'floor_y + (original_y-floor_y) * quintic((16-abs(x))/2) * quintic((16-abs(z))/2), clamped to [0,1]',
        'changed_vertices': len(changed), 'core_vertices_unchanged': len(p)-len(changed),
        'maximum_lowering_m': max(c['lowering_m'] for c in changed),
        'boundary_vertices': len(edge), 'floor_y': floor_y,
        'before_boundary_gap_range_m': [min(p[i][1]-floor_y for i in edge), max(p[i][1]-floor_y for i in edge)],
        'after_boundary_gap_range_m': [min(pp[i][1]-floor_y for i in edge), max(pp[i][1]-floor_y for i in edge)],
        'after_boundary_normal_max_angle_deg': 0.0,
        'only_changed_accessors': [pi, ni],
        'all_other_binary_bytes_unchanged': True,
        'all_other_json_records_unchanged': True,
        'uv_color_material_images_indices_nodes_transforms_unchanged': True,
        'accessor_hashes': checks,
    }
    args.output.with_suffix('.proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    args.output.with_suffix('.changed-vertices.json').write_text(json.dumps(changed, indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k != 'accessor_hashes'}, indent=2))

if __name__ == '__main__':
    main()
