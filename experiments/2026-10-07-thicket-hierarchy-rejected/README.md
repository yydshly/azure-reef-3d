# One-thicket branching hierarchy: rejected sample

Status: **REJECTED at the normal-view and thumbnail visual gate. Do not integrate or publish this geometry.** This archive records one selected construction plus one explicitly authorized constraint-method correction. It contains reproducible scripts and matched offline evidence, not a replacement production scene.

## Result

The candidate creates an obvious asymmetric silhouette, but the lower right side becomes a sparse bent framework and the middle reads as an empty basket. It does not produce the thick, interwoven, multi-basal density hierarchy visible in the inspected NOAA reference. The owner independently inspected the 1120 × 700 normal images and 280 × 175 thumbnails and agreed to reject it. An independent reviewer reached the same conclusion: a central empty opening and a few parallel curved rods with fork tips read as a basket framework, not the requested thicket. The front and reverse images support that finding. Color changes would not address the geometry failure.

No full-scene GLB was patched. No Site checkout, runtime file, camera, guide, water, fish route, source mesh, material or production asset was changed. Runtime integration and full-period fish clearance were not attempted.

## Target and fixed limits

The right-side thicket at camera position `[0, 2.7, -18]`, target `[-1.5, 1, -31]`, vertical FOV 47°, aspect 1.6 is node 78, `Corridor_Distant_Linked_03`. It uses mesh 47, `Coral_Staghorn_Thicket_11`, also shared by nodes 51 and 66. Its center projects to approximately `[833.6, 467.8]` in the 1120 × 700 normal view.

The retained budget is 22,168 rendered triangles, 21 basal shoots, 171 source segments and 103 terminal tips. A single-user integration would have required one additional mesh definition and 984,848 bytes of attribute/index buffers (about 0.94 MiB) without increasing scene object, colony or drawn-triangle counts. Driver allocation and CPU object overhead are not measured. Because integration was rejected, the actual production data and memory increase is zero.

## Two recorded stages

1. The initial fixed construction deformed the retained graph into unequal branch masses and stronger taper. Its global envelope limiter returned zero: source terminal segment 13, rooted at root #1, moved its extreme tip 0.015116095542907715 m beyond the original local −Y boundary. Fifteen vertex coordinates on this single segment failed; the remaining 170 segments and 20 complete root subtrees were within the box. Exact source replay passed, so this was an authored-direction/constraint problem, not floating-point replay error. The original failure proof and recipe remain unchanged.
2. The one authorized constraint correction froze the complete root #1 subtree in its original accepted geometry and radii. The other 20 subtree specifications were unchanged. This passed the hard gates, then failed the visual gate. There was no parameter scan, second geometry revision, population expansion, texture replacement or global palette change.

## Verified hard gates

- All 11,290 used source positions replay exactly; 680 unused continuation-ring vertices are excluded from that comparison
- All 21 basal rings remain exact; the complete frozen subtree remains exact
- All exported vertices are within the original local envelope
- 22,168 triangles before and after; 103 independent closed source-style surface components
- Zero boundary, nonmanifold, inconsistent-orientation and degenerate triangles after exact-coordinate export validation
- Existing color samples retained; no source material or texture file changed
- The portable archived build reproduced the standalone replacement GLB byte for byte: `7012c9c0a502ff8fcbbca43b219d2c205bcfe11f20c8a61bbcf121312392964b`

Independent source roots and incidental crossing/side-shoot components remain independent. This was not a watertight biological network reconstruction, and no common root system was invented. Unchanged basal rings demonstrate that grounding was not moved; new fish-path clearance was not claimed.

## Evidence limitations

All eight PNGs are **offline Blender/Cycles neutral geometry renders**, not browser screenshots. They use matched cameras, gray material, lights, exposure, world and 24 samples, with denoising off. The normal-view source GLB geometry is present in both versions, but **runtime-generated new landmarks are absent**. Water, runtime caustics and fish animation are also absent. These images are not a complete production A/B and do not establish underwater appearance.

The actual NOAA photograph was inspected for qualitative branching hierarchy, uneven masses, multiple bases and openings. No exact size, cover or ecology was inferred, and no photograph pixels were copied. The rejected earlier twelve-axis sparse-tree images were also inspected. Reference: https://www.fisheries.noaa.gov/species/staghorn-coral . The original reference photo is deliberately outside this archive.

## Portable inputs and reproduction

Use the already installed Blender 4.3.2 and Python with NumPy. The only external data input is the exact current source GLB from coral-3d commit `480d20f7e097e2bfd4719e3e700154f04d1cd025`:

- Filename: `source-model.glb`
- SHA256: `c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd`

The source GLB, reference photograph, generated GLBs, redundant blend files and logs are excluded. The two files under `inputs/` deterministically replay the original graph; no separate large branch-graph JSON is required.

Run these complete commands from this archive directory. Set the source path to the exact authorized external GLB. Outputs go to a new sibling folder, so the archive stays unchanged.

```sh
REEF_SOURCE=/workspace/scratch/56bf13a306b9/coral-3d/source-model.glb
REEF_OUT=/workspace/scratch/56bf13a306b9/reef-thicket-hierarchy-oct7/reproduce
sha256sum "$REEF_SOURCE"
blender -b -t 4 --python-exit-code 1 --python build_candidate.py -- --source "$REEF_SOURCE" --out "$REEF_OUT"
python verify_replacement.py --source "$REEF_SOURCE" --out "$REEF_OUT"
blender -b -t 6 --python-exit-code 1 --python render_neutral.py -- --source "$REEF_SOURCE" --out "$REEF_OUT"
sha256sum "$REEF_OUT/replacement.glb"
```

To reproduce the preserved initial envelope failure separately, run the following command. Exit code 1 and `failure-proof.json` are the expected outcome; there must be no replacement GLB in that output folder.

```sh
blender -b -t 4 --python-exit-code 1 --python initial_failed_recipe.py -- --source /workspace/scratch/56bf13a306b9/coral-3d/source-model.glb --out /workspace/scratch/56bf13a306b9/reef-thicket-hierarchy-oct7/reproduce-initial-failure
```

`WHITELIST.txt` is the complete archive allowlist. `manifest.json` records payload byte counts and individual SHA256 values. `SHA256SUMS` includes every archive file except itself and can be checked with `sha256sum -c SHA256SUMS`. Do not include other files from the working folder when archiving.
