# Connected hardbottom experiment · 2026-10-07

**结构实验，视觉未接受。Do not integrate this GLB into production.**

The experiment improves local rock continuity and face occlusion, but the final matched images still read as bare terraced quarry/canyon terrain. It does not meet the natural reef visual goal. The owner rejected it after reviewing the final mid and look-back images. Geometry work stopped after one substantive silhouette correction; the current published release remains unchanged.

## Frozen candidate and boundaries

- Candidate: `connected-hardbottom.glb`, 30,515,244 bytes (29.10 MiB)
- SHA-256: `75a181a1fea752a05792a055cc2fad2a42c0d0516f42ed9ae64a3d8300f64265`
- Required input: public GitHub release `ea1fd274a2e5e4f373c818303c959710b1a1558f` (corresponding Site source `117079e`), `source-model.glb`
- Input SHA-256: `c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd`
- Fixed offline fixture SHA-256: `f4ca30b9338ef08eeda09af95d94cee39508aa2eceb4eeaf9dd074bef58af55d`
- All work is isolated in this directory. No source checkout, Site, runtime, publisher directory, remote, or deployed artifact was changed by this task

Only `Spatial_Continuous_Weathered_Limestone` was replaced. The four existing `Spatial_Staghorn_Linked_*` instances were moved vertically to seat them on the changed terrain. Their x/z positions, orientation, scale and source biological meshes stayed exact. No new species, colonies, meshes, materials, textures, lights or cameras were introduced. The prior terrain's coordinate-based vertex-color function is unchanged.

## What was learned

Useful local results:

- Explicit parent outlines can join formerly isolated round support margins into low, noncircular hardbottom fingers
- Sand can cut into a parent body as deep bays while a lower, narrow rock neck remains connected
- Overlapping upper ledges create genuine local faces and floor occlusion at the unchanged mid-passage camera
- The final terrain-only footprint has two visible connected bodies, rather than being connected only through buried triangles

Why the final candidate is rejected:

- The first pass formed two overly uniform parallel ridges with repetitive stepped edges. Its diagnostics are retained under `rejected-first-pass-diagnostic/`
- The one corrective pass introduced strongly unequal necks, a broad southeast body and a diagonal west spur, but long naked terrace faces remained visually dominant
- The repeated shelf construction still feels authored as landform tiers. It does not look sufficiently like accumulated, weathered reef structure in the supplied NOAA photographs
- The unchanged biological distribution remains sparse and the original distant support pods remain recognizable. More branches or lighting adjustments would not validate this geometry experiment

The next investigation should verify actual terrain data and its provenance before deciding whether it provides a better structural basis. This record makes no claim that a Looe Key dataset has yet been obtained, licensed, inspected or found suitable.

## Evidence to review

The important final images are the matched pair and the terrain-only diagnostics:

- `before/mid.png` → `after/mid.png`
- `before/look-back.png` → `after/look-back.png`
- `diagnostic/terrain-front.png`
- `diagnostic/terrain-back.png`
- `diagnostic/terrain-overhead.png`

All before/after images use the same old Blender lighting/material fixture, camera coordinates, lens, 1120×700 resolution and 24 Cycles samples. Fish remain in their same static GLB pose. The terrain diagnostics additionally hide all biological meshes and turn off depth fog; they preserve the fixture's existing geology materials and lighting. These are offline renders, not browser captures. No browser A/B, runtime caustics, animated-fish behavior, device frame rate or full interaction claim is made for this rejected experiment.

Matched camera positions/targets in glTF/runtime coordinates:

- Mid: position `[0,2.7,-18]`, target `[-1.5,1,-31]`
- Look-back: position `[-3.8,3.6,-36]`, target `[0,0.9,-8]`

## Checks completed on exported bytes

`asset-verification.json` independently reads the exported GLB, without importing the generator:

- All 60 non-terrain meshes and 268 protected primitive payloads are byte-identical
- Every protected node and all materials, images, textures, samplers and scene membership are exact
- Only the four permitted linked instances have changed node transforms, and only their y translations differ
- All 16 snapshotted runtime files are unchanged, including five-stop guide data, fish routes, passage code, water/light code and controls
- The new terrain has 27,703 vertices and 55,402 triangles; no degenerate triangles, nonmanifold edges or inconsistent edge orientations were found
- Signed volume is positive; the outer boundary remains buried at y = -0.4 m below the sand
- The two visible above-sand components contain 7,130 and 6,596 grid samples, covering all visible terrain samples

`route-clearance.json` uses Blender BVH queries on the actual reimported candidate:

- 4,001 new samples were taken from the actual unchanged `dist/passage.js` spline, using its actual Three.js implementation
- Minimum sampled static-mesh clearance: 1.020486 m
- Clearance estimate after half the maximum sample spacing and an additional 1 cm curvature allowance: 1.003913 m, above the 0.45 m camera-sphere radius
- All 753 basal vertices of the four reseated colonies are below their triangulated support surface by at least 1.9979 cm
- The new terrain rises at most 4.5001 cm above checked original distant-colony basal vertices; it does not engulf their branches
- Original fish meshes and routes are exact. Animated fish are excluded from the static obstacle query

The route result is a dense sampled static-camera check, not an analytic proof of every runtime trajectory. Maximum sampled midpoint chord deviation was approximately 0.000000481 m; this empirical check does not replace the stated allowance.

## Portable reproduction

Requirements: Python 3 with NumPy for patch/byte checks, Node.js with the existing project for sampling, and Blender 4.3.2 for BVH/render evidence. The recipe refuses an input with the wrong SHA-256. A second independent invocation produced the exact same GLB hash.

```sh
python replace_hardbottom.py /path/to/published/source-model.glb rebuilt.glb
python verify_preservation.py /path/to/published/source-model.glb rebuilt.glb asset-verification.json
node sample_route.mjs /path/to/published/project route-samples.json
blender -b -t 8 --python verify_collision.py -- rebuilt.glb route-samples.json route-clearance.json
blender -b -t 8 --python render_comparison.py -- /path/to/lighting-fixture.blend /path/to/published/source-model.glb before
blender -b -t 8 --python render_comparison.py -- /path/to/lighting-fixture.blend rebuilt.glb after
blender -b -t 8 --python render_comparison.py -- /path/to/lighting-fixture.blend rebuilt.glb diagnostic --diagnostic
```

Run Blender jobs sequentially on a memory-constrained executor. One early concurrent candidate render was killed by the environment; its complete final evidence was regenerated successfully in sequence. This has no effect on the frozen candidate or proofs.

The optional `--runtime-snapshot baseline-runtime-hashes.json` argument to `verify_preservation.py` checks the original checkout at the root recorded in that snapshot. For a different machine, preserve the hashes and update only that snapshot's root to the corresponding frozen checkout.

## Qualitative reference inputs

Visual review of the linked NOAA photographs informed these structure criteria: connected irregular parent masses, changing neck width, overlapping faces and sand gaps. No photo or scan was copied into the asset, and no image is redistributed here. Species composition was not inferred or copied. This is not a Looe Key reconstruction.

- [NOAA Looe Key photograph](https://sanctuaries.noaa.gov/media/mag/5/fknms-looekey-shawnverne-1200.jpg)
- [NOAA Florida Keys reef photograph](https://floridakeys.noaa.gov/media/img/20231222-florida-keys-coral-reef-vessels-1000.jpg)
- [NOAA Molasses Reef relief photograph](https://floridakeys.noaa.gov/media/img/2021-fknms-molassesreef-softcorals-rachelplunkett-1000.jpg)
- [NOAA reef context](https://floridakeys.noaa.gov/corals/coralreefs.html)

## Experiment record integration

The small recipe, QA scripts, JSON reports, this README and final before/after/diagnostic images may be used for an experimental source-history record. Keep the candidate GLB in its separate experimental directory; do not replace the published `source-model.glb`, runtime GLB, release tag or Site. `rejected-first-pass*` and `replayed.glb` are local process artifacts and are not the final deliverable.
