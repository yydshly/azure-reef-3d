# One bounded Middle sea-fan current candidate

Status: source and geometry checks pass. Actual WebGL shader compilation, matched runtime pixels, realtime motion and performance are pending the publisher's separate verification. Nothing has been published. This is independent of the rejected coral morphology work.

Frozen baseline: source commit `2372e912e23cfef9cf9eaf2ce862289c5a923008`, public `a95871f`. The complete candidate is a separate archive copy at `/workspace/scratch/56bf13a306b9/reef-fan-current-oct7`. Original Site/source/GitHub were not edited. Only `dist/app.js` and new `dist/sea-fan-current.js` change runtime behavior. See `frozen-delta.json` for exact hashes.

## Exact change

Only `Inhabited_Middle_Attached_reticulate_fan_form` bends. It is a single 50,583-vertex / 75,926-triangle mesh, identity local transform inside Middle's existing Y rotation and translation. Its mainly X/Y fan plane bends along local Z, equivalent to world direction `[-0.1986693308, 0, 0.9800665778]`. No topology, triangles, vertex colors, materials at rest, textures, instances, species or layout are added/replaced. Other corals remain static.

The lower band through local Y=1.84 stays exactly fixed. 11,780 vertices are anchored. Original buried/contact surfaces remain unchanged; this is not a claim that the old geometry was newly repaired. The original stalk has long triangles: fixing only Y≤1.65 would not freeze every surface crossing into the support's coarse envelope. Triangle inspection found that all faces within the support-plus-.04 vertical margin end by local Y=1.8307042122. Y=1.84 freezes those entire faces without subdividing anything.

Above the fixed band, `h=clamp((y-1.84)/0.7820932006835938,0,1)` and the displacement is local `z += amplitude*h*h*(3-2*h)`. One CPU sine per rendered update computes `amplitude=.04*sin(2π*visibleSeconds/8)`; there is no vertex sine. The max absolute displacement is .04 scene units, reached at the upper tip. Normals use the inverse-transpose bend Jacobian; tangents use the direct Jacobian. Water light reads the deformed world position and corrected normal. The material is isolated from the three other fans that shared it. Identical position deformation and the same uniform object are attached to custom depth/distance materials.

The geometry wrapper shares all immutable vertex/index buffers and expands its box/sphere by the full displacement. The actual main/shadow draw geometry therefore matches. CPU raycasting remains undeformed; this fan is not an interaction target, and the fish use their unchanged precomputed routes.

## Geometry and clock evidence

`source-checks.json` records 129 phases × 50,583 vertices, finite normals, analytic derivative/orthogonality checks, t0 equality, shared buffers, material isolation and shader assembly. It checks all moving triangles, including triangles crossing the rigid band, against every actual terrain triangle whose X/Z bounds overlap the entire swept fan envelope. The minimum moving-surface/support vertical gap is 0.2091335058 scene units; bending never changes Y. Nearby continuous limestone clears by 1.28461 units. Original fixed-base contact is preserved.

Each saved Catmull-Rom route is enclosed using its cubic Bezier control hull. A conservative fish sphere includes all mesh vertices, root scale and arbitrary tail/fin rotations. The closest whole-route fish body envelope is fish_05 at 1.1433420152 scene units from the full swept fan box. This bound is deliberately conservative, not a behavioral/biological claim.

The specimen inspection certificate bytes, control domain and geometry stay unchanged. Even the full fan envelope remains at least 18.0945 units from that whole camera domain. The globally free camera still has no global collision certificate.

The app feeds the existing visible-elapsed-seconds clock. Hidden-tab time is excluded through its existing visibility reset; reduced-motion pauses the shared clock except when the user explicitly starts the existing tour. No new clock or resume catch-up is introduced. Actual app logic in the DOM/renderer fixture passes normal and reduced-motion runs; the fan fixture verifies clock plumbing, while actual fan buffers/shader assembly are covered separately. This is not native input or GPU evidence.

## Budget (loaded root only)

Before and after: 99 meshes, 1,478,169 triangles, 99 unculled main mesh draws, 275 unique attribute/index buffers, 25,328,194 attribute bytes, 11 material texture objects. This counts the composed root after specimen, six-fish setup and refined fish_03; it excludes the unchanged separate water envelope, particle points, lights, renderer-owned targets, and camera-dependent culling/shadow passes.

Geometry wrapper objects: 67→68; surface material objects: 23→24. Two new custom shadow material objects are added; the directional depth one is active, the point-light distance one is supplied for parity but the scene has no point shadow light. No added GPU attribute bytes or textures; expected main/shadow mesh draw delta is zero. There will be a distinct surface/depth shader variant and per-vertex polynomial/normal math for this one mesh. Actual compiled program counts, draw calls, frame time and physical-GPU performance must be measured in runtime and are not inferred from these source budgets.

## Publisher: matched runtime evidence

Do not accept from these source checks alone. Use the existing safe software-WebGL runner. Check console/request/shader errors and `renderer.info`, then take actual identical-camera phases and a short chronological motion clip. Compare baseline t0 with candidate t0 as well.

Suggested exact three-quarter camera in world coordinates, using the existing 47° perspective:

- camera: `[-7.972653486778265, 2.5342332277063293, -23.939230761867375]`
- target: `[-5.572664305470652, 1.8842332277063294, -26.013779370506473]`
- `reef3d.leaveGuide(); reef3d.setTour(false);` clears the guide and pending target move
- set camera and controls target, clear camera view offset, update projection and controls
- normal quality: `getState().low === false`; shadows enabled; identical resolution/exposure and no specimen inspection

Runtime API: `window.reef3d.fanCurrent.update(seconds)` changes the shared amplitude uniform; `window.reef3d.fanCurrent.getState()` and `window.reef3d.getState().fanCurrent` report it. Ordinary RAF continues to overwrite it with shared scene time. For fixed-phase screenshots, hold/intercept RAF with the runner's existing mechanism and render the actual scene after the call; do not rely on changing the uniform while unconstrained RAF runs. Hold fish and water at the same phase for the isolated before/after comparison.

Actual fan phases: `update(0)` = 0; `update(2)` = +.04; `update(6)` = -.04. The full period is 8 seconds. Short motion evidence should advance the real/shared clock through part or all of this cycle while keeping the same camera. It must be labelled if driven at fixed phases instead of native realtime. Check low-quality toggling/recompile and hidden/reduced resume as well.

Optional offline phase images, if generated, only show CPU-deformed source geometry of the isolated original pilot component under fixed neutral Blender lighting. They do not run the runtime GLSL, reconstruct full app composition, or prove shader/normal/shadow compilation. Any such evidence is supplemental and outside the frozen runtime delta.

## Checks run

- `node --check dist/sea-fan-current.js` and `node --check dist/app.js`
- `node --import ./qa-register.mjs qa-sea-fan-current.mjs`
- `node --import ./qa-register.mjs qa-water-light.mjs`
- `node --import ./qa-register.mjs qa-guide-integration.mjs`
- `REEF_REDUCED_MOTION=1 node --import ./qa-register.mjs qa-guide-integration.mjs`
- `node --import ./qa-register.mjs qa-tour-clock.mjs`
- `node --import ./qa-register.mjs qa-tour-controls.mjs`
- `node --import ./qa-register.mjs qa-life.mjs`

## References and limits

Smithsonian Q?rius describes flexible sea fans swaying in currents: https://qrius.si.edu/taxonomy/term/11903 . NOAA's coral-growth overview provides broad coral growth context: https://oceanservice.noaa.gov/education/tutorial_corals/coral03_growth.html . These support a qualitative motion cue only. They do not specify this amplitude, period, material stiffness, drag, anatomy, species identity or scene layout. This is not a hydrodynamic simulation or a biologically calibrated coral model.

Still-static surroundings, repeated/illustrative forms, broad texture patches and macro scene realism limits remain. A small living-water motion cue does not establish that the whole reef is naturalistic.
