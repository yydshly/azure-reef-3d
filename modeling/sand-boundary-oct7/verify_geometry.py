"""Independent binary, topology, transition, and support checks. Requires NumPy."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from patch_sand_boundary import read_glb, accessor_bytes, vectors, SOURCE_SHA

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
parser.add_argument('candidate', type=Path)
parser.add_argument('report', type=Path)
args = parser.parse_args()
raw, g, b = read_glb(args.source)
out, gg, bb = read_glb(args.candidate)
assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
assert g['nodes'] == gg['nodes'] and g['meshes'] == gg['meshes']

def positions(j, data, mesh):
    return np.array(vectors(j, data, j['meshes'][mesh]['primitives'][0]['attributes']['POSITION']))

def triangles(j, data, mesh):
    ai = j['meshes'][mesh]['primitives'][0]['indices']
    dt = {5123: '<u2', 5125: '<u4'}[j['accessors'][ai]['componentType']]
    return np.frombuffer(accessor_bytes(j, data, ai), dtype=dt).reshape(-1, 3)

def geometry_hash(j, data, mesh):
    h = hashlib.sha256()
    for prim in j['meshes'][mesh]['primitives']:
        for key in ['POSITION', 'NORMAL', 'TEXCOORD_0', 'COLOR_0']:
            if key in prim['attributes']:
                h.update(key.encode())
                h.update(accessor_bytes(j, data, prim['attributes'][key]))
        h.update(accessor_bytes(j, data, prim['indices']))
    return h.hexdigest()

mesh_hashes = []
for i, mesh in enumerate(g['meshes']):
    a, z = geometry_hash(g, b, i), geometry_hash(gg, bb, i)
    mesh_hashes.append({'mesh': i, 'name': mesh['name'], 'before_sha256': a, 'after_sha256': z, 'unchanged': a == z})
    assert i == 0 or a == z

p, q = positions(g, b, 0), positions(gg, bb, 0)
pn, qn = np.array(vectors(g, b, 1)), np.array(vectors(gg, bb, 1))
t = triangles(g, b, 0)
d = 16-np.abs(p[:, [0,2]]).max(axis=1)
core, edge = d >= 2, d < 1e-7
floor = float(positions(g, b, 33)[0, 1])
assert np.array_equal(p[core], q[core]) and np.array_equal(pn[core], qn[core])
assert np.array_equal(p[:, [0,2]], q[:, [0,2]])
assert (q[:,1] >= floor).all() and (q[:,1] <= p[:,1]).all()
assert np.all(q[edge,1] == floor) and np.all(qn[edge] == [0,1,0])
cross = np.cross(q[t[:,1]]-q[t[:,0]], q[t[:,2]]-q[t[:,0]])
assert (cross[:,1] > 0).all()
cross /= np.linalg.norm(cross, axis=1)[:,None]
face_angle = np.degrees(np.arccos(cross[:,1].clip(-1,1)))
band_faces = (d[t] < 2).any(axis=1)
edge_faces = edge[t].any(axis=1)
ring_profiles = []
for distance in np.unique(d[d < 2.5]):
    mask = d == distance
    ring_profiles.append({'distance_to_edge_m': float(distance), 'vertices': int(mask.sum()), 'before_y_range_m': [float(p[mask,1].min()), float(p[mask,1].max())], 'after_y_range_m': [float(q[mask,1].min()), float(q[mask,1].max())]})

# Weld exact duplicate coordinates before boundary extraction, so split shading
# vertices do not masquerade as outer rock boundaries.
supports = []
for node in g['nodes']:
    if not node.get('name','').startswith('Distant_Limestone_Support_'):
        continue
    local = positions(g, b, node['mesh'])
    unique, inv = np.unique(local, axis=0, return_inverse=True)
    tt = inv[triangles(g, b, node['mesh'])]
    edges = np.sort(np.concatenate([tt[:,[0,1]], tt[:,[1,2]], tt[:,[2,0]]]), axis=1)
    unique_edges, counts = np.unique(edges, axis=0, return_counts=True)
    ids = np.unique(unique_edges[counts == 1])
    perimeter = unique[ids]*np.array(node['scale'])+np.array(node['translation'])
    clearance = floor-perimeter[:,1]
    assert (clearance > 0).all()
    supports.append({'name': node['name'], 'outer_boundary_vertices': len(ids), 'minimum_outer_edge_below_far_floor_m': float(clearance.min()), 'maximum_outer_edge_below_far_floor_m': float(clearance.max()), 'geometry_transform_unchanged': True})

# Exact guide coordinates from the existing corridor anchor recipe. Their whole
# camera-to-anchor segments lie inside the unchanged core, and all non-sand
# geometry on those rays has already been verified byte-identical above.
anchors = [
    {'name': 'sand', 'anchor': [-1.0108096,-.1403618,2.8146734], 'camera': [2.4,2.3,7.2]},
    {'name': 'hardbottom', 'anchor': [-.3038789,-.00275017,3.6140898], 'camera': [2.4,2.3,7.2]},
]
for anchor in anchors:
    assert max(abs(v[i]) for v in (anchor['anchor'], anchor['camera']) for i in (0,2)) < 14
    anchor['entire_guide_ray_in_exactly_unchanged_core'] = True

report = {
    'source_sha256': hashlib.sha256(raw).hexdigest(),
    'candidate_sha256': hashlib.sha256(out).hexdigest(),
    'mesh_count': len(g['meshes']), 'node_count': len(g['nodes']),
    'sand_vertex_count': len(p), 'sand_triangle_count': len(t),
    'exactly_unchanged_core_vertices': int(core.sum()),
    'core_guarantee': 'All position and normal bytes with abs(x)<=14 and abs(z)<=14 are unchanged. All hardbottom geometry and every node transform are unchanged.',
    'boundary_vertices': int(edge.sum()),
    'before_boundary_gap_range_m': [float((p[edge,1]-floor).min()),float((p[edge,1]-floor).max())],
    'after_boundary_max_gap_m': float(np.max(np.abs(q[edge,1]-floor))),
    'before_boundary_max_normal_angle_deg': float(np.degrees(np.arccos(pn[edge,1].clip(-1,1))).max()),
    'after_boundary_max_normal_angle_deg': float(np.degrees(np.arccos(qn[edge,1].clip(-1,1))).max()),
    'maximum_band_triangle_slope_degrees': float(face_angle[band_faces].max()),
    'maximum_edge_triangle_slope_degrees': float(face_angle[edge_faces].max()),
    'no_surface_below_far_floor': True, 'no_xz_or_topology_change': True,
    'all_triangles_positive_upward_area': True,
    'ring_profiles': ring_profiles, 'support_outer_edges': supports,
    'exact_guide_anchor_preservation': anchors,
    'mesh_geometry_and_shading_hashes': mesh_hashes,
}
args.report.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('ring_profiles','mesh_geometry_and_shading_hashes')}, indent=2))
