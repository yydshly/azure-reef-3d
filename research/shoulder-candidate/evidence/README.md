# Actual local shoulder A/B

Run37585092762 / QA8d9f416 compares frozen source db08563 against accepted public1e1a055 on one sandboxed Chromium153/SwiftShader runner. Midpoint, local-front and local-reverse camera coordinates match exactly, as do fixed-time fish states. Both arms passed with no console errors. These are controlled camera images, not an assertion of full native exploration or user-device performance.

Visual acceptance remains pending. Actual screenshots reveal readable recesses and fan silhouettes, but ground integration at the rounded front edge and the authored stacked-rock appearance require review. A technical pass does not establish a natural reef or justify replacing production.

The v3 visual review rejected expansion: the right-front projection looked unsupported over the old sand slope, and the main fan was cropped in the standard midpoint. Source39a9cfb makes one physical support correction by extending932 base vertices down toward sampled original terrain. It does not change the top, fans, materials, placement or scene. The midpoint cropping remains explicitly unresolved. The next bounded run compares originalv3 against groundedv4 in local front/reverse only; production remains unchanged.

## Grounded v4 actual comparison

Run37586644231 compares v3 and v4 at identical front/reverse cameras and fish phase. Both technically pass; actual served v4 GLB SHA256618797ee32308fc39ded467f74a0f0d13dd6decd5a393fd12c4fe3f518363519 matches the frozen candidate.

Actual pixel inspection shows that downward extension reduces the unsupported gap but produces a conspicuous vertical skirt and stretched surface pattern at the front/right and back. This technical pass is not natural ground-integration acceptance. No production update is included.

Final review rejects v4 for the visible geometric skirt and UV stretching. The direct downward-extension approach is closed. Production remains public commit1e1a055. A future rigid-placement investigation must retain originalv3 geometry/UV and pass separate numerical and visual checks; no such candidate is accepted here.

New isolated rigid placement candidate21706b1 restores the exact originalv3 geometry/UV, changing only position and yaw. This is a separate test after rejecting v4, not a reversal of that rejection. Three original fixed cameras compare originalv3 placement against v5; production remains unchanged.

## Rigid v5 actual comparison

Run37588768850 / QA0445652 compares originalv3 placement against source21706b1 rigid placement with the exact originalv3 GLB. Both arms pass at all three original cameras, with equal fixed fish phase and no console errors. The midpoint fan now fits in frame and the rejectedv4 vertical extrusion is absent. At the unchanged local-front diagnostic camera the right side extends beyond the frame; terrain integration and authored-rock appearance remain subjects for visual review. No acceptance of a complete reef or production deployment is implied.
