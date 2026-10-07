# Read-only diagnosis of the 21 basal roots

**The apparent detachment is partly real and already present in the original scene.** Both the original and simplified limestone supports leave the same 11 complete basal caps floating, 8 intersecting the highest substrate and 2 entirely below it. The visible dark ends include both genuinely detached roots and already-grounded roots. No geometry, object pose, production file or CI configuration was changed.

All distances are **uncalibrated scene units**. Positive signed gap means the basal cap lies above the highest sand/limestone surface; negative means it is buried.

## Actual screenshot evidence

The inputs were viewed directly:

- `/workspace/scratch/56bf13a306b9/reef-support03-ci-37673506367/support03-37673506367/baseline/diagnostic-close.png`
- `/workspace/scratch/56bf13a306b9/reef-support03-ci-37673506367/support03-37673506367/candidate/diagnostic-close.png`

The verified QA camera is [4.7, 1.25, −21.7], target [1.8, **0**, −25.45], vertical FOV 47°, 1120 × 700. The target y=0 comes from each QA capture's actual state; it is not the earlier offline target y=−0.2.

Marked full captures: `baseline-front-ends-annotated.png`, `candidate-front-ends-annotated.png`. Enlarged original-pixel crops with all 21 root IDs: `baseline-all-roots-crop.png`, `candidate-all-roots-crop.png`. The crop uses nearest-neighbor enlargement, not generated image content.

## Complete-cap findings

| Quantity | Original support | Simplified support |
|---|---:|---:|
| Entire basal cap floating | 11 | 11 |
| Basal cap intersects substrate | 8 | 8 |
| Entire basal cap below substrate | 2 | 2 |
| Maximum positive gap anywhere on a basal cap | 0.1221173076 | 0.1234341647 |
| Largest root's minimum gap | 0.0577503338 | 0.0567542902 |
| Minimum signed cap gap anywhere | −0.0656358439 | −0.0618589456 |
| Median of per-root minimum gaps | 0.0086275303 | 0.0030340236 |

Fully floating in both arms: R01, R02, R03, R05, R07, R09, R11, R12, R14, R19, R20. Fully buried in both: R13 and R17. All other roots intersect. The per-root distributions and all ring vertices are in `grounding-proof.json` and `all-21-basal-caps.csv`.

## Which front dark ends these are

| Root | Approximate screenshot pixel | Original complete-cap gap range | Interpretation |
|---|---|---:|---|
| R11 | (503,362) | +0.016599 .. +0.067045 | Entire base truly floats |
| R19 | (560,368) | +0.041684 .. +0.083765 | Entire base truly floats |
| R14 | (584,358) | +0.056754 .. +0.098306 | Entire base truly floats |
| R06 | (565,369) | −0.001001 .. +0.062768 | Barely intersects; 99.78% of cap's projected area remains above ground |
| R16 | (596,363) | −0.019766 .. +0.010771 | Intersects substrate |
| R17 | (623,377) | −0.034861 .. −0.007608 | Entire basal cap is already below ground |

For these projected front-end positions, a ray to the ring center first hits the corresponding root's own stem wall. Their center points are partly hidden by their near-side walls, not mislabeled rear roots. The labels identify the actual finite basal-ring locations. A dark terminal-looking appearance alone does not establish a gap, as R17 demonstrates. `root-screen-map.json` records triangle-owned root IDs, ray distances, camera state and projected ring polygons.

## Method and numerical boundary

1. Replayed the original source branch recipe and verified its graph equals the provided `source_graph` (21 `parent=null` roots)
2. Verified every used original replay position equals the current GLB float32 position set for mesh 47. Original height scale is 1.0
3. Converted original Blender XYZ to glTF [x,z,−y], then applied the complete current node78 world matrix. Ring positions were not inferred from center/radius alone
4. Matched each actual ten-vertex basal ring back to the current GLB and extracted its **eight actual cap triangles**
5. Included every source Sand/Hardbottom/Limestone node (492,238 total substrate triangles), replacing only node86 geometry in the simplified arm. Actual upper surfaces below the bases reduce to source sand node37 and limestone node86
6. For each basal triangle, partitioned its projected domain by all intersecting substrate-triangle edges and competing substrate height-plane intersections. Each final cell has a fixed highest substrate plane. The cap-minus-ground function is affine within that cell; its extrema occur at the cell vertices

Thus this is an **exhaustive continuous triangle-surface calculation**, not a ten-point or interior-sample estimate. It uses float64 and a 1e−11 polygon clipping tolerance, not interval arithmetic; it is not described as a machine-certified exact floating-point bound. Classification tolerance is 1e−7 scene units. Across all 42 root/arm combinations, projected cap-area partition error is at most 6.87e-14. No root was unclassified or omitted.

## Analytical rigid-placement bounds, original support baseline

A pure world-Y translation preserves every triangle, root, branch and relative shape. Ground heights at unchanged XZ remain fixed, so every signed gap decreases by exactly the downshift.

- Downshift **0.05775033381333827** makes every root touch at least at one point. It does not eliminate all residual cap exposure, so it is a weak contact criterion
- Downshift **0.12211730762552114** puts every point of every basal cap at/below its substrate
- The owner's proposed complete-cap allowance is **0.12711730762552115**, adding 0.005 embed. If separately applied later, node78 translation.y would change from **−0.20698136165738104** to **−0.3340986692829022**; X/Z, rotation, scale, mesh and materials would remain the same
- At that hypothetical shift, the least-embedded cap point is 0.005 below ground; the deepest basal cap point is **0.192753151539593** below ground
- The earliest first-primary-branch cross-section would touch substrate only at downshift **0.36720087362803966**. At the proposed shift it therefore retains **0.2400835660025185** clearance

The main-junction check uses the finite original first-order starting rings, or the repaired root terminal ring when a continuation's initial ring is absent. It bounds those first major junction cross-sections, not every possible whole-world collision or an aesthetic guarantee. The measured interval accommodates complete basal embedding before those principal junctions are buried. Basal portions of already-grounded roots would sink farther, which should be inspected in the owner's separate minimal pose candidate.

This report contains only the unmoved measurement and screenshots. It does not apply the proposed translation, mix in simplified support for the repair baseline, make footings, enlarge rocks, create skirts, or alter topology.

## Reproducibility and artifacts

- `extract_geometry.py`: exact source graph/ring/cap extraction and world transforms
- `analyze_grounding.py`: continuous upper-surface overlay for both support arms
- `project_roots.py`: actual QA-camera projection and root-owned ray mapping
- `package_report.py`: screenshot annotations and CSV/report packaging
- `basal-rings.json`: all exact original finite rings/caps and coordinate provenance
- `grounding-proof.json`: complete per-root classifications, area fractions, bounds and analytical pose proposal
- `root-screen-map.json`: actual QA camera and per-root projected positions
- `geometry-input.npz`: read-only extracted source inputs

Pinned source SHA-256: `c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd`. The source remains unchanged. Native source snapshots and original screenshots were only read. No network, new downloads, new CI or production actions were used.
