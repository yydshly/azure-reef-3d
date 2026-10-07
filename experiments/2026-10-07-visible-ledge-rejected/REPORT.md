# Visible folded reef edge — one sample, rejected

**Verdict: reject this candidate for both morphology and geometric validity.** The new edge is plainly visible in both target cameras and has an actual lateral return with downward-facing underside triangles. However, its broad cap and repeated folded section read as a coarse ribbon/ledge attached to the bank. The reverse view makes that manufactured-looking roof especially clear. It does not achieve the reference's varied exposed skeleton and unequal negative-space hierarchy. Independent exact testing also found **12 improper triangle intersections**, so this candidate is not a valid embedded closed surface despite its closed, consistently wound connectivity.

This is one deterministic structural experiment from the accepted source, not a refinement of the rejected Y-only candidate. The first 75% matched pair was reviewed and reported before the 92%/reverse samples. No shape parameter was changed after that first pair. No browser test, production edit, upload, publication, new noise/texture phase, or additional candidate was attempted.

## Review the actual evidence

- `grey/comparison-actual-route-75.png` — exact supplied 75% camera, before/after. The new upper-right recess is visible behind the unchanged landmark; the former experiment was nearly invisible here.
- `grey/comparison-actual-route-92.png` — exact 92% camera from the visibility diagnosis. The returning edge makes a dark recess beside/behind the landmark, but its folded strip remains too regular.
- `grey/comparison-neutral-reverse.png` — same geometry from the back. It exposes the broad, faceted roof and supports rejection.
- `grey/all-three-comparisons.png` — all three paired views on one sheet.
- `grey/render-manifest-*.json` — exact cameras, model hashes, resolution, sample count, and unchanged landmark pose.

Each single frame is an **OFFLINE Blender/Cycles** 800 × 500 render with 24 samples. Camera, neutral grey materials, illumination, and context pruning are fixed between before and after. Original pixel values are retained in the paired sheets; labels are outside the image frames. These are structural samples only, with no water, original textures, caustics, animation, browser appearance, performance, or habitat-science validation.

The exact landmark is `dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb`, at Y-up position `[3.5, -0.015196346640586854, -44]`, yaw `1.3`. Only `Attached_reticulate_fan_form` is omitted in the renders, and the small fan remains. The original asset and its pose are unmodified.

## Method and preservation

`fold_visible_ledge.py` byte-patches only the accepted terrain's positions and affected normals. Its existing 0.5-unit columns are redistributed laterally into an open returning profile: floor → recessed wall → underside → outer lip → roof → existing bank. Hand-authored longitudinal stations change crest height and lateral offset. The script uses no noise, appended ellipsoid, appended platform, new surface, index change, vertex addition, or triangle addition.

- Accepted source HEAD: `6750ba68bb139c85c4ed5ca77d8d109200358a53`
- Accepted source SHA-256: `c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd`
- Candidate SHA-256: `9e0cb3f417905582b7947e5fc4e239dbd6596e3bea6905921c177903356e4239`
- Landmark SHA-256: `d6377e6bcfc5145ef6da7c139de26772b6065b30fbe24c2d3180bcba9ae48cdf`
- File size unchanged: **29,534,488 bytes**
- Terrain budget unchanged: **10,190 vertices / 20,376 triangles**
- **220 positions** move; **286 incident normals** are recomputed
- Changed source vertices lie in `x=5.0…9.5`, `z=−53.5…−43.0`
- Candidate moved positions lie in `x=4.15…9.327`, `y=−0.295…1.9`, with all Z coordinates unchanged
- There are **116 genuinely downward-facing former top triangles**. This is intentional underside geometry, not an erroneous demand that the old heightfield remain upward facing
- Every terrain edge still has exactly two incident triangles with opposite edge directions; Euler characteristic remains 2
- Minimum triangle area is positive, and all positions/normals are finite; normal lengths remain within floating-point tolerance of 1
- All GLB JSON, indices, UVs, colors, material/texture/image data, nodes, transforms, unrelated mesh data, and other bytes are identical
- The thicket support disk centered at `(12,−44)`, radius `1.9`, is unchanged; its height remains `2.03999996`
- Sand-route terrain at `x=−3±4`, all bottom/perimeter geometry, and all other vertices are unchanged
- Deterministic replay gives exactly the same candidate positions

The base preservation proof is `visible-ledge-candidate.proof.json`; the independent results are `visible-ledge-independent-validation.json`, produced by `validate_folded_ledge.py`. Closed edge incidence alone is not treated as proof of no self-intersection or of a watertight terrain-to-landmark union.

The independent validator compared all 504 affected terrain faces against the full 20,376-face closed terrain. It tested 4,383 broad-phase pairs with exact integer/rational predicates, including shared-edge and shared-vertex pairs rather than blindly excluding them. The untouched source was separately verified to be a regular heightfield above its base with properly triangulated perimeter and bottom. It found 12 improper intersection pairs: 8 crossing segments and 4 nonadjacent boundary point contacts. Two of the 12 pairs share a vertex but overlap beyond that permitted common vertex. The crossing intervals occur near the far taper, `z≈−52.677…−51.898`, where the rising original floor and descending authored return collapse into one another. Exact face IDs and coordinates are retained in the JSON, with a concise independent summary in `visible-ledge-independent-validation.txt`. This is a specific failure of this authored/blended profile, not evidence that every redistribution under the same budget is impossible. The parameterized validator CLI was rerun successfully against actual input/candidate GLBs without the temporary NPZ bundle.

## Landmark contact, clearance, and stretching

The independent checker transforms the unchanged landmark to the exact accepted Y-up pose and tests its triangles against the terrain. Its 343 existing basal contact pairs remain unchanged. This candidate adds 35 upper-rear shoulder/terrain intersection pairs within `x=4.150…4.256`, `y=1.038…1.116`, `z=−44.611…−44.287`. These are interpenetrating contact surfaces, not a Boolean/manifold union. The unchanged small fan has no terrain contact before or after.

At the sampled `z=−45` cavity slice, the minimum distance between the changed terrain region and the landmark surface falls from about `0.9499` to `0.1555` scene units, remaining positive in that slice. At `z=−44.75` it falls to about `0.0770`; the new direct contact appears farther rearward, near `z=−44.5`. These are finite cross-section diagnostics, not a proof of unchanged clearances or camera-visible cavity openness. The report does not claim the original cavity clearance is preserved in size.

No perimeter or bottom surface is pulled into a vertical skirt. Interior surface stretching is nevertheless significant: the maximum corresponding edge stretch is `3.849×`, changed-region longest edge increases from `0.8041` to `2.4768`, and maximum triangle aspect (equilateral = 1) increases from `1.928` to `23.495`. Those figures support the visible coarse-roof problem and are not presented as a quality pass.

## Why this finite sample fails

1. **The fold has improper self-intersections.** Finite normals, preserved topology, and opposite edge winding pass, but they do not make this an embedded solid. The 12 exact crossing pairs independently disqualify the candidate.
2. **Visibility improved, morphology did not clear the quality bar.** Targeting the ray-confirmed edge solved the earlier framing mistake. The dark returning face is visible at 75% and 92%, but stronger visibility is not sufficient realism.
3. **A repeated section becomes a broad ribbon.** The authored crest stations vary its plan and height, yet the same sequence of floor, wall, lip and roof produces a mechanically continuous band. Uneven heights alone do not create varied skeleton masses.
4. **Redistributed columns leave a broad cap.** The existing rows are spent on a real return. The remaining span back to the unchanged bank has few transverse intervals and wide roof faces. In reverse, that roof still reads as a bank cap, with a noticeably regular contour.
5. **The original landmark has much richer local form.** A coarse folded strip does not bridge convincingly to the asset's irregular cavity and lobes, even when their silhouettes overlap. Visual continuity must not be conflated with a verified manifold union.
6. **Preserved UVs are a separate limitation.** UV bytes intentionally stay identical under lateral redistribution. Grey views cannot establish acceptable original-material distortion or shading, and none is claimed.

The sample demonstrates a visible lateral return and downward faces without growing the budget, but fails both the appearance and nonintersection requirements. It does **not** prove that the budget makes a credible final shape impossible, nor that this candidate should enter the browser or replace the accepted model. The experiment stops here rather than adding a second method or parameter sweep.

## Reference and limits

Both supplied current runtime images (`sampled-route-0.75.png`, `sampled-route-0.92.png`) and the NPS reference pixels were inspected before modeling. The source ray diagnosis informed the work's location, with visible edge hits around `x≈5–8`, `z≈−45…−54`.

Reference: [National Park Service, Dry Tortugas — Corals](https://www.nps.gov/drto/learn/nature/corals.htm), image `DRTO-DUW-046.jpg`, credit **NPS Submerged Resource Center**. Used only for macro irregular exposed skeleton and negative-space hierarchy. No photographic texture, species reconstruction, precise habitat coverage, or measured scale claim is made. The reference JPEG is not included in this output directory. All dimensions are **interpreted scene units**.

## Reproduce the single sample

```sh
python reef-visible-ledge-oct7/fold_visible_ledge.py \
  coral-3d/source-model.glb \
  coral-3d/dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb \
  reef-visible-ledge-oct7/visible-ledge-candidate.glb

blender -b -t 6 --python reef-visible-ledge-oct7/render_grey_comparison.py -- \
  coral-3d/source-model.glb \
  reef-visible-ledge-oct7/visible-ledge-candidate.glb \
  coral-3d/dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb \
  reef-visible-ledge-oct7/grey --view actual-route-75
```

Repeat the renderer with `--view actual-route-92` or `--view neutral-reverse` for the other fixed frames. Run `compare_renders.py <grey-folder> <view-name>` to assemble each labelled pair.
