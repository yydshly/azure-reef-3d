# Node66 offline pose review

This is a new, separate pose preview. Both arms retain the published node78 world-Y drop of 0.12711730762552115. Only the candidate lowers node66 by **0.10224513179842109**. Original detailed terrain, source geometry/materials, all other objects and node66's nonuniform scale are preserved. No production files, source GLB, prior measurements or CI were changed by this preview.

Distances are uncalibrated scene units.

## Exact requested views

- Normal route view, samplePassage(.2): camera [0.29437670936632904, 2.364790323719224, −6.645862253821183], target [0.13504281746656863, 0.7, −21.069232030809317]
- Diagnostic: camera [4.7, 1.65, −8], target [2.2, 0.9, −12.3]
- Both use 47° vertical FOV, 1120×700. Both satisfy targetY ≥0, cameraY ≥0.4 and camera-target distance ≥3.2. Neither view was replaced or scanned

## Image pairs

- `offline-sibling-compare-passage20-textured.png`
- `offline-sibling-compare-passage20-gray.png`
- `offline-sibling-compare-diagnostic-textured.png`
- `offline-sibling-compare-diagnostic-gray.png`
- Fixed 2× enlarged diagnostic crops: `offline-sibling-diagnostic-crop-textured.png`, `offline-sibling-diagnostic-crop-gray.png`
- Measured lowest primary-junction projection: `offline-before-lowest-junction-projection.png`, `offline-candidate-lowest-junction-projection.png`

The normal view shows node66 in the right-hand rear part of the nearby branching group. The supplied diagnostic view exposes the target without requiring a new camera. Object-index visibility is recorded for every frame in `offline-sibling-pose-manifest.json`.

## Actual offline image review

All four paired normal/diagnostic textured/gray images were inspected, including the fixed diagnostic crop and the projected controlling junction. The target bases now visibly enter the existing mound and their detached-end impression is reduced. The first primary branches remain exposed; no obvious swallowing of the main branching was seen in either requested view. This is a **limited offline visual pass** for this pose change, not production water-shader or browser acceptance.

## Source measurement under the fixed translation

No contact geometry was retuned. The prior complete-cap continuous measurement had maximum positive gap 0.09724513179842109; subtracting the fixed shift leaves **−0.005**. Thus all 21 original basal caps are below their existing substrate. Deepest basal burial is **0.14628798273191**.

The controlling primary junction is root R08, child segment56. Its original complete-cross-section minimum clearance was 0.21484597514086712; after the fixed shift it remains **0.11260084334244602**. The projection image identifies this measured cross-section. That bound concerns those first-primary-junction cross-sections, not all-world collision or perceptual approval.

## Limits

These are Cycles CPU, 20-sample, fixed-light original-GLB-material frames. The production world-space substrate shader, water/fog/caustics, browser output, fish motion and performance are not reproduced. Gray deliberately overrides materials for shape inspection. Exact source asset SHA-256 remains c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd.

`render_offline_sibling_pose.py` reproduces the scene and only the two specified poses. `package_offline_sibling_pose.py` produces comparison layouts. `offline-sibling-pose-manifest.json` records cameras, visibility, renderer and isolation assertions; `offline-sibling-visual-review.json` records the analytically inherited contact/junction facts without changing the old audit.

## Explicit neighboring-clump boundary

The prominent front clump in the normal .2 route view is not node66. It retains its existing pose, and this preview does not claim to fix its grounding. `offline-before-passage20-target-labeled.png` and `offline-candidate-passage20-target-labeled.png` outline only actual visible node66 pixels in cyan.

In the requested diagnostic source frame, all 14 fully floating basal-cap center projections have actual object-index 2 (node66), so the neighboring foreground clump is not covering those projected centers. Self-occlusion among node66 branches remains possible. The already-buried R08 and R15 cap centers project onto ground, as expected. This is a narrow screen-visibility check; it does not substitute for the continuous cap/ground measurement. No fallback viewpoint was needed.
