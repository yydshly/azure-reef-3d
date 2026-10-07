# Read-only sibling-instance grounding audit: node66

**Node66 also has an existing source-placement defect: 14 of its 21 complete basal caps float above the highest actual substrate, 5 intersect it and 2 are entirely buried.** All roots were resolved; none are unknown. This is a geometric contact audit, not a new shape proposal or a visual-quality review.

Only runtime-retained `Depth_Staghorn_Linked_01_1` (node66, original shared mesh47) was checked. Runtime-removed node51 was not checked. No position, transform, geometry, material, frozen node78 measurement or QA package was modified. No renderer, new download or CI was invoked.

All distances are **uncalibrated scene units**. Positive signed gap means the basal cap is above the highest sand/limestone triangle surface; negative means it is buried.

## Actual transform and reuse

- Translation: [4.956271171569824, 0.5899999737739563, −11.1922607421875]
- Quaternion XYZW: [0, 0.9187883734703064, 0, 0.3947504460811615]
- Nonuniform scale: [0.722000002861023, 0.722000002861023, 0.6822900176048279]
- The full glTF matrix, including this unequal Z scale, is recorded in `node66-grounding-proof.json`

The existing frozen 21 finite basal rings and eight actual cap triangles per root were inverse-mapped from node78 world space to mesh-local space. All 210 recovered ring positions were matched back to the current GLB float32 positions. They were then transformed using node66's complete matrix. The original ground-triangle arrays were reused without rebuilding or modifying the world. No radius/center proxy was substituted.

The original highest substrate nodes actually selected beneath these caps are [62]. Their names remain available in the original substrate catalog in `../grounding-diagnostic/basal-rings.json`.

## Results

- Fully floating: R01, R02, R03, R04, R05, R06, R07, R11, R12, R14, R16, R17, R19, R20
- Intersecting: R09, R10, R13, R18, R21
- Fully buried: R08, R15
- Largest positive gap anywhere on a cap: **0.09724513179842**
- Largest per-root minimum gap: **0.07947861884870**
- Most negative existing cap gap: **-0.04404285093349**
- Median of the 21 per-root minimum gaps: **0.01589991863956**

`node66-all-21-caps.csv` contains each root's complete gap range and above-ground projected-cap-area fraction. `node66-grounding-proof.json` also contains the ten actual vertex gaps, full world ring/cap coordinates and first-primary-junction cross-section results.

## This instance's own analytical constraints

These are computed bounds, not an applied or approved pose change. Node78's 0.12711730762552115 shift was **not** copied to this instance.

| Pure world-Y downshift condition | Scene units |
|---|---:|
| Every root touches at least somewhere | 0.07947861884870 |
| Every point of every basal cap reaches or passes below ground | 0.09724513179842 |
| First primary junction cross-section would begin touching ground | 0.21484597514087 |
| Primary-junction clearance remaining at the complete-cap bound | 0.11760084334245 |
| Deepest basal burial at the complete-cap bound | 0.14128798273191 |

Thus an instance-specific rigid downshift has a feasible interval between the complete-cap bound **0.09724513179842109** and the first-primary-junction boundary **0.21484597514086712**. Any additional embed allowance or aesthetic acceptance would require a separate choice and review. The cross-section bound concerns the measured first-order branch junctions, not whole-world collision or visual approval.

## Continuous calculation and precision boundary

The reused algorithm exhaustively partitions each actual cap triangle by projected substrate-triangle edges and competing height-plane intersections. The highest substrate is affine on each resulting cell; signed-gap extrema are evaluated at cell vertices. This is a continuous piecewise-linear triangle calculation, not ten-point or internal sampling.

It uses float64, clipping tolerance 1e−11 and classification tolerance 1e−7; it is not interval-arithmetic certification. Maximum projected cap-area partition discrepancy is **6.85e-15**. The audit reused the original support, not the simplified Support_03 candidate.

## Reproduce

Run `python audit_node66.py` followed by `python package_audit.py` in this directory. The first script reads the existing immutable source/cap/ground arrays, computes only node66 and writes this sibling audit. It does not execute the original node78 audit's output loop. No new image renders are required.

Pinned original GLB SHA-256: `c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd`. All new files are confined to this sibling-audit directory.
