# Distant 3D fan detail candidate, 2026-10-07

Baseline: published Site527ef99 / GitHub6f9dd123. Production remains unchanged during this test.

Only the four visible fan representations change with distance. The original high-detail geometry, materials and world placement are preserved for close viewing; no billboard replaces them. At distance, a480-site irregular 3D network (rather than2200 sites) preserves the source extent profile and original main stem/vein paths. Thin tube radius scales with the square root of site-count ratio to approximate integrated far-view coverage. This is an artistic render approximation, not a biological growth claim. The extra GLB is859,492 bytes.

THREE.LOD selects low detail beyond9 scene units for the main fan or5.5 for the small fan, measured from its geometry center.15% hysteresis prevents repeated toggling near the boundary. Two optional small-fan LOD groups still hide in power-saving mode. New immutable asset directory is assets/fan-lod/d11ef2d64a9258b1; app/composition/version-module URLs use fan-lod-20261007-r1. Reef placement, water/substrate shading, rocks, sand, fish routes, guide and view route remain unchanged.

## Local evidence

- Original7 high-detail mesh geometry objects retained; world-matrix difference at most8.9e-16 from center-based reparenting.
- Source visible triangles at departure:1,082,005→842,005 (-22.2%); middle508,223→388,223 (-23.6%); return1,368,941→1,128,941 (-17.5%). Counts are not GPU timing or device FPS.
- Close fan camera[-5.1,2.8,-22]→[-5.71,1.88,-26] selects the original main fan.
- Four detail groups, correct threshold hysteresis, small-fan quality toggles, normal/reduced-motion guide wiring, no-WebGL notice and conservative164s fish clearance (both representations included) pass.

Actual acceptance remains pending: compare the three unchanged whole views plus close fan, inspect a short approach across the threshold for noticeable silhouette/opacity jumps, and measure same-runner native tour/RAF after a completed first frame. Do not call fewer triangles a performance gain until measured, and do not accept visibly degraded fans merely to improve numbers. One bounded candidate, no additional scene population or water restyle.
