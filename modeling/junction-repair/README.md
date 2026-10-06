# Baseline-preserving coral junction correction

Frozen candidate: `candidate.glb`, SHA256 `619806ff9fbe2911d7a805ba2ef94019adea7e0538b6132bb9b7734e7ab06c54`, 47,059,408 bytes.

This is the accepted narrow correction method applied to the 22 existing source thicket meshes. It does not redesign their growth forms. The current source and the accepted one-thicket candidate were not overwritten. No Site, GitHub checkout, deployment, terrain, routes or fish was edited here.

## Change and scope

The original generator erroneously shrank every tube's last ring to 38% radius, including nonterminal continuations. The repair restores only nonterminal end radii and locally bridges each explicitly recorded continuation child, removing the two internal caps. The tangent-bisector ring avoids the former pinched mechanical join.

- All 22 original position sets replay exactly, with no missing or extra unique vertices
- 1,155 explicit continuation joints corrected across 2,901 original source tube segments
- Original 362 basal shoots, 1,746 terminal segments, axes, fork locations, growth-tip surfaces, root rings, palettes and material maps retained
- All 22 bounding envelopes remain exactly unchanged
- 376,056 final thicket triangles, down from 394,536; no polygon explosion
- Side-shoot components, separate roots and incidental crossings remain independent. No global union or invented biological root network
- All scene nodes, transforms, shared-mesh references, fish, non-thicket meshes, materials, images, textures and samplers remain unchanged. Distant instances follow their original shared meshes
- Entire original binary prefix is retained, with 16,569,404 new geometry bytes appended. Deployment may externalize into multiple lossless bounded buffers

Side-shoot base caps remain buried inside their parents as in the source. The change does not claim all branches form a single topological network, ecological validation, photorealism or a named-site reconstruction.

## Deliverables

- `candidate.glb`: frozen full-scene correction
- `full-scene-editable.blend`: clean compressed, packed full-scene import of that GLB only. No camera, lights, world, compositor, or offline material substitutions
- `replacement-thickets.glb` / `thickets-editable.blend`: intermediate 22-thicket-only assets; not substitutes for the full scene
- `all-branch-graphs.json`: original seeded parent/child graph, height scaling, and explicit corrected continuation pairs
- `all-replay-proof.json`: exact source reconstruction for every original thicket, including original height-scaled 03/07/20
- `all-geometry-proof.json`: preserved envelopes/tips/roots and native topology checks
- `candidate.proof.json`: append-only patch, shared references, and unrelated-content preservation
- `exported-topology-proof.json`: zero-tolerance exported topology for every thicket
- `full-scene-editable.proof.json`: clean full-scene file size/hash and packed-image inventory
- `EXPERIMENT_LOG.md`: rejected-design record; v1/v2 assets stay archived outside this minimal bundle

## Verification and evidence

All 22 exported thickets pass exact float32 coordinate tuple remapping, with zero boundary, non-manifold, inconsistent-orientation edges, or degenerate triangles. This is a zero-tolerance, read-only index check, not a broad asset weld. The initial overly strict Blender seam search was reconciled independently and is documented with the frozen one-thicket proof.

The hero specimen's POSITION, NORMAL, TEXCOORD_0, COLOR_0 and triangle-index arrays are identical to the separately accepted one-thicket candidate. Its immutable expected array hashes are in `frozen-hero-primitive-hashes.json`.

`after/opening.png`, `reverse.png`, `close.png`, and `close-reverse.png` were rendered from the final GLB using the unchanged accepted offline fixture and were inspected against the original `before/` images. Composition, crown silhouettes, density, tip locations and substrate placement remain intact; the original stepped/pinched continuation joints are smoother. These are matched 1120 × 700 offline Cycles renders, 24 samples, denoising off. They are not browser screenshots and contain no runtime caustics or animation checks. The owner separately reported all guide/motion checks passed for the losslessly pruned deployment, whose active attribute/index/world-transform bytes match this authoritative candidate.

## Required reproducible inputs

Keep large inputs separate from the minimal script/proof bundle. Local copies are preserved for exact rebuild tests.

1. The earlier original full-scene `source-model.glb` (also retained locally as `baseline.glb`), SHA256 `deac6a8e6d2173fc649023b763264f3b195fc5c084bf5a2c58c3ca76c4abcb0e`, 30,471,852 bytes. It is available from prior Git commit `62473dab5d10d1c6673fd962a8dec224d3733bdc:source-model.glb`. Use that exact file, not the newly corrected candidate
2. `original_geometry_recipe.py`, the minimal unchanged geometry-function body and center list extracted from the original `rebuild_reference_reef.py`. Scene paths, dependencies and presentation setup are excluded. The seed/RNG prelude is reproduced in `replay_thickets.py`; no whole historical recipe-file hash is required. The exact baseline GLB position-set checks are definitive
3. For offline comparison only: the separate existing `lighting-fixture.blend`, SHA256 `f4ca30b9338ef08eeda09af95d94cee39508aa2eceb4eeaf9dd074bef58af55d`, 6,472,917 bytes. This fixture is not embedded in the clean editable scene
4. Blender 4.3.2 and Python with NumPy

## Portable commands

Run from a folder containing the scripts and original recipe. Replace `BASELINE` with the exact original GLB path; `OUT` is a new output directory. Copy the scripts/fingerprint file into OUT for the final standalone topology check.

```sh
blender -b -t 3 --python-exit-code 1 --python verify_replay.py -- BASELINE original_geometry_recipe.py OUT
blender -b -t 5 --python-exit-code 1 --python build_all.py -- BASELINE original_geometry_recipe.py OUT
python patch_all.py BASELINE OUT/replacement-thickets.glb OUT/candidate.glb
blender -b -t 4 --python-exit-code 1 --python make_full_editable.py -- OUT/candidate.glb OUT/full-scene-editable.blend
python OUT/check_exported_topology.py
blender -b -t 6 --python-exit-code 1 --python render_compare.py -- FIXTURE OUT/candidate.glb OUT/after --views opening,reverse,close,close-reverse
```

The final portable pipeline was run in a separate output folder with the minimal recipe and reproduced the complete frozen GLB byte-for-byte; see `portable-rebuild-proof.json`. The replay gate stops if the baseline hash is wrong or any original thicket cannot be matched exactly. The patch asserts the source hash and modifies only the 22 original mesh primitive references, keeping existing node placement and shared instances. The asset does not need the fixture to open or edit.

## Reference and provenance

Actual NOAA photograph pixels were inspected to diagnose discontinuity and branching hierarchy:

- https://www.fisheries.noaa.gov/species/staghorn-coral
- https://www.fisheries.noaa.gov/s3/styles/full_width/s3/2021-11/Acropora_cervicornis_staghorn_coral.jpg?itok=QRYoPThD

No NOAA image pixels, scans, meshes, or textures were copied into this correction. The photo remains local-only and is excluded from packages. This repair derives from the existing authored source geometry, colors and procedural maps. Rejected free-form redesigns and any separate scan research are excluded from this deliverable.

## Distributed-source compaction

The frozen repair output above is an intermediate archival candidate. The Site source repository rejected its 47 MB blob. From the project root, run:

    python compact_source_model.py candidate.glb source-model.glb
    python export-static-model.py

The compact source is 28,962,072 bytes, SHA-256 `ce6a7bc4d005ecd794d378c792d5d05d79f4683b10a2d3446333e6053ead4d21`. It removes 110 unreachable buffer views, not any active scene data. Every active attribute/index byte and world transform is verified against the same accepted model. The clean editable Blender file remains the same accepted geometry/material scene; its original import provenance points to the archival candidate. No visual or biological changes are made by compaction.
