# Single-fish surface decision — 2026-10-07

Accepted as a bounded visual repair, not biological or whole-scene realism acceptance.

Frozen runtime candidate: 3c853a6ba5f3d3ab6740f669a808de36945e4943. Actual software WebGL run: https://github.com/yydshly/azure-reef-3d/actions/runs/37616743352 . Original six images/reports: https://github.com/yydshly/azure-reef-3d/tree/qa/fish-surface/evidence/fish-surface-ci-37616743352 (archived at f705f067b1620ab650ce7473a810f7cc0f3eb1b0).

Both arms passed, zero GL/console/page/HTTP errors. Actual camera, target, FOV and six fish transforms/t0 matched. Only fish_03 body/five fins refined; fish_05 and all other fish preserved. Closeups use 20-degree diagnostic FOV; normal midpoint uses the production 47-degree FOV.

Owner and independent pixel reviews inspected all six frames. Accepted: removal of stair-stepped pigment discontinuities on both flanks, lighter fin appearance, no normal-distance readability loss or new visible seam/outline tear. Limit: very straight regularly spaced hard pigment edges, old eyes and illustrative body remain; no species/photoreal or ecological claim. Static evidence does not establish motion or device performance. Source-level full-cycle geometry/motion, containment and guide checks cover the unchanged interfaces but are not actual-device motion evidence.

One fish only. +980 fin triangles; body attribute/index bytes unchanged. Closed fins remain contained in original geometry under the existing affine fin motion. No new textures; original procedural shaders only. Reference images were privately viewed and not redistributed. See reference-audit.json.

Release-only changes after captured candidate: app/module query versioning, evidence/source page and documentation. Runtime algorithm and geometry remain the captured bytes apart from the module import query. No new camera path or other-fish refinement adopted.
