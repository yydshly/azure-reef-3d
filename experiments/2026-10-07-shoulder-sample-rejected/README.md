# Local reef shoulder experiment — rejected

This isolated geometry experiment was visually rejected. It is not in the published model or runtime. One local design and one correction were tried; no further geometry variations are planned for this experiment.

The published baseline is GitHub `ea1fd274a2e5e4f373c818303c959710b1a1558f`, corresponding to Site source `117079e`. Its `source-model.glb` SHA-256 is `c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd`.

The rejected output is 30,455,516 bytes, SHA-256 `1d0b54fb008b205a102a88c682636cad827114aeb2d0234f2752d57158b31b22`. The archive intentionally excludes that GLB; it can be regenerated from the published baseline.

## Visual finding

The local notch and unequal crests provide real depth, but the first under-lips resemble rolled shelves. The single correction removes their continuous lower aprons. The remaining smooth bevels and authored slab-like faces still do not resemble convincing accumulated, weathered reef structure. Numerical preservation and clearance do not override that visual rejection.

The actual Molasses Reef photograph was inspected as a qualitative reference for local recesses, uneven supporting faces and overlapping heights:
https://floridakeys.noaa.gov/media/img/2021-fknms-molassesreef-softcorals-rachelplunkett-1000.jpg
Context: https://floridakeys.noaa.gov/corals/coralreefs.html

No source photograph, species composition, dimensions, hidden surfaces or measured location was reconstructed. The photographic fauna are not added to the scene. No restricted photograph is included here.

## Fixed comparison and scope

The changed square is x=[-13,-3], z=[-29,-19] in authored glTF scene coordinates. All biological mesh bytes, node transforms, maps, lights and runtime files remain unchanged. Only the local terrain primitive is redirected; all original binary bytes remain in the candidate. The local attachment region is preserved.

`neutral-before.png` and `neutral-after.png` are the decisive shape diagnostic. `before/` and `after/` contain matched local and mid-passage views with identical old Blender fixture, lens, materials and lighting. These are offline Cycles images. They do not show runtime caustics, UI, fish movement or browser performance. This rejected sample was not sent through browser CI.

## Verification

- 60 protected non-terrain meshes and 268 primitive payloads preserved
- Closed, consistently oriented geometry; no degenerate faces or nonadjacent triangle intersections
- All original transforms and biological geometry unchanged
- Existing support-height checks unchanged
- 4,001 samples of the actual passage spline; conservative static clearance 1.0039 scene units for a 0.45-unit camera sphere
- Repeated generation produced the identical output SHA

These are bounded source/static checks, not a proof of natural realism or every possible free-camera trajectory. Dimensions use authored glTF metre convention, not an independently calibrated real reef.

## Reproduction

Use Python 3 with NumPy and SciPy, the existing Three.js project for route samples, and Blender 4.3.2 for the offline checks. The input hash is enforced.

    git show ea1fd274a2e5e4f373c818303c959710b1a1558f:source-model.glb > baseline.glb
    python shape_shoulder.py baseline.glb shoulder-sample.glb

The original fixture is `modeling/immersive/offline/lighting-fixture.blend` in the published source, SHA-256 `f4ca30b9338ef08eeda09af95d94cee39508aa2eceb4eeaf9dd074bef58af55d`.

    blender -b -t 4 --python render_comparison.py -- /path/to/lighting-fixture.blend baseline.glb before
    blender -b -t 4 --python render_comparison.py -- /path/to/lighting-fixture.blend shoulder-sample.glb after

The scripts and JSON reports preserve the experimental chain. Any stored workspace roots are source-run locations; use a local frozen checkout when replaying them. Do not replace the deployed model with this rejected sample.
