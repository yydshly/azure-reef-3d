# Lower-viewpoint study: static benefit, full route rejected

Production remains source 6750ba68 / Pages a18e1f7. No route changes from this experiment are deployed.

## What was actually seen

The accepted scene was held fixed. Midway and 75% route positions were compared at their original heights and 1.7 interpreted scene units; horizontal positions, targets, field of view, lighting and frozen fish phase were retained. Actual software WebGL frames are archived on qa/camera-height, evidence/camera-height-oct7. Runs 37610541045 and 37610899706 provide the four frames. The first run retains its original failure: an exact floating-point equality assertion treated 8.9e-16 as different from zero after the valid midpoint captures; the unrendered late pair alone was captured with the intended .001 tolerance. An earlier unreachable 1.45-height input was cancelled (37610285974); existing polar limits were not relaxed.

Owner and independent review found a real but limited midpoint benefit: more readable reef sides/undersides and near-eye-level fish. The late view was neutral to slightly improved, with more empty water. This passed only the gate to examine a continuous path, not publication, ecological accuracy or whole-world realism.

## Continuous-path outcome

The first envelope descended too soon: at progress .305 it came within .2841 of an original branch mesh, below the existing .45 camera observation buffer. Its source and failed report are retained. One geometry-directed repair preserved the old high path through that obstacle, descended between .34 and .45, stayed near the tested 1.7 height, then returned to the original high overview. Horizontal path and look-at targets were unchanged; polar-angle constraints were respected. Reverse return retained the original travel-progress range, avoiding an unnecessary stationary turn delay. Normal/return/pause/resume source checks passed.

Final static-triangle sampling (201 poses per direction) found a minimum 1.020598 distance. Real OrbitControls updates across 1001 poses per direction retained requested coordinates. These remain source checks, not browser-route or device-performance evidence.

The separate phase-independent fish check failed the predeclared .45 observation buffer. Exact posed fish triangles confirmed a minimum 0.1605277 at route progress .735 / fish time 59 for fish_06_body. This is NOT proof that the camera center penetrates the fish or that near-plane clipping must occur. The closest tested pose is outside the view frustum; neighboring tested poses can enter it. The decision is failure of the chosen observation-clearance gate, not a demonstrated rendered clipping artifact. Desired fish orientation and the app's fin/tail transforms were used; frame-dependent quaternion lag was not simulated.

The full low route is rejected. No more fish-path, eye-height or camera-target tuning was undertaken, and no browser-route test was launched. Static study value is retained separately from the unsuccessful full-route candidate. Current morphology, sparse banks and realtime performance limitations remain unresolved.

## Replay

Use an isolated checkout of public accepted commit a18e1f71455e76dd7a3bd8a1980a891228928a85. Copy candidate-passage.js to dist/passage.js, the three qa-camera scripts to the checkout root, and the evidence/camera-path-oct7 directory into the checkout. Keep the accepted source-model.glb (SHA c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd), original pilot asset and fish routes. Use the repository's Three/canvas test dependencies.

Run node --import ./qa-register.mjs qa-camera-clearance.mjs, then qa-camera-path.mjs (expected nonzero assertion: camera approaches padded fish body), and qa-camera-fish-contact.mjs. Generated reports expose the limits above. The archival copy may normalize canvas dependency paths; that does not change the rejected camera coordinates or geometry.

## Archive changes and evidence links

The three QA scripts use the declared `@napi-rs/canvas` package instead of the author environment absolute path. Replay still means copying these scripts and the candidate passage into an isolated a18e1f7 checkout as above; do not replace the deployed passage. The original archive-manifest records pre-normalization bytes. archive-file-sha256.json records this portable archive. No checks were rerun or thresholds relaxed for archival.

[Original four images and reports](https://github.com/yydshly/azure-reef-3d/tree/febe46bd5fc54b2b1f3d2dabd517de7fc110c197/evidence/camera-height-oct7) retain the cancelled input and failed floating-point assertion history. The full path was rejected before a new browser-route run.
