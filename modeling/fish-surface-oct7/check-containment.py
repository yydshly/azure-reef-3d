"""Independent numerical check of exported prototype, using original fin hulls."""
import json
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull

P = Path(__file__).resolve().parent
data = json.loads((P.parents[1] / 'evidence/fish-surface-oct7/preview-input.json').read_text())
original = {o['name']: o for o in data['baseline']}
report = []
max_support_violation = -float('inf')
for obj in data['candidate']:
    if obj['finCoords'] is None:
        continue
    name = obj['name']
    a = np.asarray(original[name]['positions']).reshape(-1, 3)
    b = np.asarray(obj['positions']).reshape(-1, 3)
    hull = ConvexHull(a)
    violations = b @ hull.equations[:, :3].T + hull.equations[:, 3]
    maximum = float(violations.max())
    assert maximum < 3e-8, (name, maximum)
    # Stronger than a hull test: every candidate x/y lies in an original cap
    # triangle, and candidate z lies between that triangle's two original layers.
    n = len(a) // 2
    indices = np.asarray(original[name]['indices']).reshape(-1, 3)
    cap = indices[np.all(indices < n, axis=1)]
    middle = (a[:n] + a[n:]) / 2
    inside = []
    for point in b:
        valid = False
        for tri in cap:
            xy = a[tri, :2]
            matrix = np.vstack([xy.T, np.ones(3)])
            w = np.linalg.solve(matrix, [*point[:2], 1])
            if min(w) >= -3e-6:
                upper, lower = w @ a[tri, 2], w @ a[tri + n, 2]
                valid |= lower - 3e-8 <= point[2] <= upper + 3e-8
        inside.append(valid)
    assert all(inside), name + ' left original concave prism'
    # Same app pivot and allowed articulation amplitude, with varied whole-fish
    # headings. This supplements, rather than replaces, affine containment.
    extent = .225 if name.endswith('_tail') else .125
    pivot = np.array([-.49, 0., 0.]) if name.endswith('_tail') else np.zeros(3)
    worst = -float('inf')
    for angle in np.linspace(-extent, extent, 25):
        c, s = np.cos(angle), np.sin(angle)
        rotation = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        aa, bb = (a - pivot) @ rotation.T + pivot, (b - pivot) @ rotation.T + pivot
        for heading in np.linspace(0, 2 * np.pi, 25):
            c, s = np.cos(heading), np.sin(heading)
            world = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
            aw, bw = aa @ world.T, bb @ world.T
            violation = max(float((aw.min(0) - bw.min(0)).max()), float((bw.max(0) - aw.max(0)).max()))
            worst = max(worst, violation)
    assert worst < 4e-8, (name, worst)
    def volume(positions, triangles):
        points = np.asarray(positions).reshape(-1, 3)
        faces = points[np.asarray(triangles).reshape(-1, 3)]
        return abs(float(np.einsum('ij,ij->i', faces[:, 0], np.cross(faces[:, 1], faces[:, 2])).sum() / 6))
    original_volume = volume(original[name]['positions'], original[name]['indices'])
    candidate_volume = volume(obj['positions'], obj['indices'])
    report.append({'name': name, 'originalVolume': original_volume, 'candidateVolume': candidate_volume,
                   'remainingVolumeFraction': candidate_volume / original_volume,
                   'maxOriginalHullPlaneViolation': maximum, 'everyVertexInsideOriginalConcavePrism': True,
                   'maxSampledArticulatedSupportViolation': worst, 'samples': 625})
    max_support_violation = max(max_support_violation, worst)
result = {'scope': 'Original finite prism containment plus sampled articulation support; no route or ecological inference',
          'continuousEnvelopeArgument': 'Each new vertex stays in an original cap-triangle prism. The cap and rim triangles stay in the same finite prism union, with shared x/y tessellation and positive depth. A rigid fin rotation about the unchanged app pivot, followed by the same whole-fish affine transform, preserves containment. Therefore the original conservative convex envelope cannot expand at any animation phase.',
          'coordinateTolerance': 4e-8, 'fins': report, 'maxSampledArticulatedSupportViolation': max_support_violation}
(P / 'containment-checks.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
