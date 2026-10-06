# Reef iteration record

## 2026-10-06 · Immersive first-version visual pass (checked revision)

### User-facing goal

Build a complete spatial scene first, then improve believability: tranquil breadth, blue depth, layered life, moving underwater light, and the feeling of being surrounded by water. Keep the source-grounded beginner guide.

### Concrete acceptance checks

1. Opening view feels inside a continuous reef environment, not above a tabletop patch
2. Foreground, middle and distant terrain remain distinct, with clear near details and natural-looking distance attenuation
3. Underwater light has visible, restrained movement; rigid hard coral does not wave like vegetation
4. Fish turn and move through real depth without obvious route jumps; generic identity remains explicit
5. Five guide stops and correct sand/hardbottom pointers still work
6. Geometry, material provenance, source-to-model limits and tests are recorded

### Baseline assessment

The current model has real middle/distant geometry, but the high opening camera and flat presentation still read as a model display. The existing staghorn form remains visibly procedural. A generated earlier image is useful for composition only; NOAA references continue to govern biological claims.

### First planned change

Evaluate an eye-level opening camera and stronger directional light/depth separation against the unchanged GLB before adding more geometry. This isolates whether framing and light improve the stated experience. Offline render evidence will be labelled as such; it cannot prove live WebGL appearance.

### Validation boundary

The cloud browser has previously reported unavailable WebGL2, and the private Site also has a sign-in gate. Neither is bypassed. Browser rendering remains unverified until a supported actual rendering route is available. No photorealism or scientific validation is claimed.

### Changes selected after actual image review

- Lowered the opening view to a swimmer-like observation height, retaining unrestricted orbit controls within the existing bounds
- Opened a winding sand gap by translating ten existing thickets and smoothly lowering the existing hardbottom below the unchanged sand mesh; no new coral species or morphology was inferred
- Preserved the original sand and hardbottom guide anchor geometry and first-hit visibility, and the main coral teaching specimen
- Added an original deterministic wave-slope caustic texture, a moving material-light approximation, and a directional water-color field; these are artistic optics rather than measured water parameters
- Rebuilt swim routes after the changed thicket layout exposed a clearance failure; increased route sampling and body-width footprint sampling rather than weakening the clearance check

The same-view opening and reverse offline images visibly establish that the prior branch wall is broken into readable banks around real intervening space. Independent image review still found the flat sand-to-water horizon insufficiently immersive; this prompted a further middle/distant layout pass rather than declaring the visual target complete.

### Habitat attachment check

A further audit caught a distinction between numerical grounding and ecological plausibility: new distant thickets could be physically seated on sand yet lack a hard attachment substrate. The final asset must expose existing-form limestone beneath those new patches or relocate them onto existing hardbottom. Geometry clearance alone is not evidence of a supported habitat relationship. This issue is corrected before publication, rather than leaving it for the viewer to diagnose.

### Checks and remaining limits

- Reimported and inspected same-camera opening and reverse images of the final geometry; intermediate layouts are retained in the reproducible patch chain
- Five-stop guide logic, actual app wiring under a simulated renderer, low-performance distant-object toggles, and reduced-motion wiring pass
- Shader insertion, uniforms, caustic-image dimensions and water-envelope settings pass structural checks; actual GPU compilation, realtime color appearance, input feel and frame rate remain unverified
- Sand/hardbottom guide rays hit the correct first surfaces at all three tested viewport sizes
- Full-period route samples pass: minimum center-to-top-surface clearance about 0.40m; several fish show depth occlusion across the tested presets and lateral orbit view. This is not a continuous body-collision or behavioral simulation
- Normal quality now includes extra distant instances. Low-performance mode hides these added distant thickets and their supports, as well as its existing shadow/particle/resolution reductions. No device performance guarantee is made

Decision: publish this checked improvement and retain the first-version visual goal as open. The readable sand passage is a meaningful advance, but branch morphology still looks procedural, the horizon transition is simple, and offline images do not establish the intended live flowing-water experience. Further presentation work requires actual GPU-rendered review to close that gap responsibly.

Final geometry SHA-256: `deac6a8e6d2173fc649023b763264f3b195fc5c084bf5a2c58c3ca76c4abcb0e`. The last reverse-view check caught rectangular support edges; the new support perimeter was lowered below sand and re-rendered before release. All eight sampled basal attachment sets hit their corresponding limestone supports, with positive gaps below 8mm. Original core bytes and anchors remain preserved.

The portable three-step patch chain was rerun independently from the preceding baseline and reproduced the final GLB byte-for-byte. Static deployment keeps its largest file, reef.bin, at 24,041,060 bytes. Final checks also retain explicit WebGL failure handling without a misleading interactive-2D substitution.

## Evidence boundary correction

Material-assignment audit established that the accepted offline comparison images contain no projected caustic modulation. Unused suffixed material variants had the water texture; actual rendered materials did not. No image was replaced to conceal the discrepancy. Browser water-light code has structural checks only. The compact, geometry-free fixture under modeling/immersive/offline reproduces the pixels actually inspected and records the numerical comparison.
