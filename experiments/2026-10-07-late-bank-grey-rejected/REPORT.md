# Late-bank grey geometry experiment — rejected

The one bounded deformation is complete. It produces substantial negative gullies and unequal scarps without increasing the mesh budget, but it **does not meet the visual acceptance threshold**. The center still reads as a rounded, eroded hill. The fixed landmark's rear connection is too low and narrow to make a convincing continuous exposed reef mass. No further shape parameters were tried after the first comparison, and nothing was copied into the production checkout, published, or sent to GitHub/Sites.

## Evidence

- `grey/comparison-neutral-front.png`: matched before/after grey front view
- `grey/comparison-neutral-reverse.png`: matched before/after grey reverse view
- `grey/comparison-actual-route-75.png`: exact supplied 75% route camera and target, with the runtime's 47° vertical field of view
- `grey/all-three-comparisons.png`: the three pairs in one sheet
- `grey/render-manifest.json`: camera, input hashes, resolution, samples and limits

These are explicitly **OFFLINE** Blender/Cycles renders, 800 × 500 per view, 24 samples, fixed neutral grey materials and lighting. They contain the accepted FarRight landmark at its exact rigid pose, omit only its reticulate fan as instructed, and retain the small fan. They do not reproduce or verify browser materials, water, caustics, animation, performance, or habitat science. The grey lighting is deliberately identical between candidates; no contrast or geometry adjustments were applied to the rendered views.

## What changed and what did not

`late-bank-candidate.glb` is a byte patch of the accepted `source-model.glb`, not a re-export.

- Terrain topology remains 10,190 vertices and 20,376 triangles; total scene topology is consequently unchanged
- Only 305 terrain positions moved, exclusively along Y; 458 incident normals were recalculated
- Moved vertices lie in x = 4.5…16.5, z = −48.5…−38.5; the largest height decrease is 1.60417 and increase is 0.63147 interpreted scene units
- All GLB JSON, nodes, transforms, mesh definitions, materials, image data, textures, UVs, colors, index bytes, and unrelated binary data are exactly unchanged
- The original far-thicket support remains exactly 2.03999996 at (12, −44); all terrain positions within a 1.9-unit disk are unchanged
- The x ≈ −3 sand route, all bottom/perimeter positions, all other terrain positions, all biological geometry, and the accepted landmark file and rigid placement are unchanged
- Candidate and input have the same 29,534,488-byte length and exactly the same accessor bounds
- The closed terrain has edge incidence exactly 2; all top triangles retain upward winding; no degenerate triangle, non-finite position or non-finite normal was found
- Deterministic sculpt replay reproduces the candidate positions exactly

The complete numerical result is `late-bank-candidate.proof.json`. The source remains SHA-256 `c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd`. Candidate SHA-256 is `941e9fa1ca42b2918ff818a2f9f46aff1f948860d52d0dc836f1625b68947ed1`.

## Concrete limits exposed by this experiment

1. **This mesh is a single closed heightfield.** Y-only edits can make open troughs, unequal heights and steep slopes. A vertical line still intersects only one upper surface, so the topology cannot supply a genuine overhang, roofed recess, through-hole or broken skeleton arch. The NPS photo contains that kind of negative-space hierarchy. This experiment does not reconstruct it.
2. **The protected support is a circular cap.** Keeping the thicket's support untouched while cutting around it preserves a broad convex-to-flat mass. The surrounding incisions make its hill-like character more apparent. The result remains an eroded terrain feature despite its deeper gullies.
3. **The fixed 0.5-unit lattice limits fracture detail.** Incisions around one unit wide cross few samples. Their edges become low-resolution triangular scarps; narrowing them further would create grid artifacts rather than convincing broken hardbottom. Adding small noise would not solve the macro shape.
4. **Physical toe contact is insufficient visual continuity.** The landmark's maximum rear x is about 4.515. At (4.5, −43.5), ground rose from −0.32357 to −0.00814. That touches the low rear toe, while the landmark's maximum height is about 1.604. The connection remains far below the asset's main silhouette. Both before and after already contain low-toe surface intersections in the sampled area; the numerical test is not proof of a new watertight join. No bottom vertices or vertical skirts were pulled down, and the key cavity near z ≈ −45 was left unobstructed.
5. **The 75% route view exposes little of the changed bank.** Most of the sculpt is beyond or screened by the far-right landmark and frame edge. That matched pair is almost visually unchanged, so it supplies no basis for claiming a stronger runtime composition.

These results reject this particular bounded Y-only deformation. They do not prove that every design at the same triangle budget would fail: changing connectivity and redistributing the existing vertices would be a different, separately scoped modeling approach. No such work was started.

## Reproduction

From the public repository root:

```sh
python experiments/2026-10-07-late-bank-grey-rejected/sculpt_late_bank.py \
  source-model.glb \
  dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb \
  /tmp/reef-late-bank-rebuilt.glb

blender -b -t 6 --python experiments/2026-10-07-late-bank-grey-rejected/render_grey_comparison.py -- \
  source-model.glb \
  /tmp/reef-late-bank-rebuilt.glb \
  dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb \
  /tmp/reef-late-bank-grey
```

The extra low-toe test in the saved proof uses preserved-grid triangle interpolation at 584 original landmark vertices with world x > 4.0, −44.1 < z < −42.85 and y < 0.3. It is a diagnostic sample, not a full triangle intersection solver or a manifold union claim.

## Reference use

The NPS image pixels and both supplied actual runtime samples were viewed before modeling. Reference: [Dry Tortugas — Corals](https://www.nps.gov/drto/learn/nature/corals.htm), image DRTO-DUW-046.jpg, credit **NPS Submerged Resource Center**. Used only to study irregular exposed skeleton and the hierarchy of large recesses. The original photograph was not used as a texture and is not included in this experiment's output folder. Coordinates and heights throughout are **interpreted scene units**, never a measured survey or evidence of precise habitat/species coverage.

## Public archival note

This rejected experiment is recorded without changing production commit a18e1f7. The original29MB candidate GLB is intentionally omitted and is reproducible from the existing source model. Only reproduction paths and this archival note differ from the supplied REPORT; scripts and actual offline images are unchanged. artifact-sha256.json preserves the original worker checksums, including the omitted GLB and pre-edit REPORT. archive-file-sha256.json records the exact archived files after the portable-path edit. No new render or WebGL run was performed for archival.
