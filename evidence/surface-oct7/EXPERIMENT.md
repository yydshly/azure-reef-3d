# Single-colony surface test — 7 October 2026

Local material experiment only. These are OFFLINE Cycles CPU images, not browser captures. No caustics are present in this fixture. A still image cannot test moving shimmer. Nothing in this folder establishes species accuracy, full reef realism, browser performance, or user acceptance.

## Result: retain baseline

Both variants **failed the visible-improvement criterion**. All 12 rendered frames were inspected: baseline, fine, soft and normal-disabled, each at guide close, reverse-close and normal opening views. Soft produces faintly uneven shading on a few near branches; fine is harder to distinguish. Neither convincingly removes the smooth cylindrical appearance at the unchanged cameras, and neither gives a useful opening-view gain. Independent visual review reached the same result.

No obvious oversized craters, studs, recoloring or static glitter were seen. Motion shimmer remains untested. The normal-disabled control retains the broad smooth appearance. This is evidence about these two maps at these frozen views, not proof that all possible material work would fail. No candidate should be promoted on the basis of the passing preservation checks.

For review, use the `OFFLINE-*-baseline-soft.png` files and the normal-disabled comparisons. These place the original render pixels at 1:1 resolution under labels; the image areas are not retouched or rescaled. `visual-review.json` records the judgment, and `matched-evidence-proof.json` verifies equal camera poses, fixture settings and graph structure except the allowed maps/normal-strength control.

## Scope

Only `Coral_Staghorn_Thicket_01` receives a cloned material. Original geometry, normals, UVs, colors, indices, node transforms, and other material assignments are frozen. Both candidate GLBs append maps and one material to the compact source; they do not re-export its meshes. All original binary data remain an identical prefix. `asset-preservation-proof.json` records complete accessor preservation and counts.

- Source: `../coral-3d/source-model.glb`, SHA-256 `ce6a7bc4d005ecd794d378c792d5d05d79f4683b10a2d3446333e6053ead4d21`
- Fixture: `../reef-corridor-pass/offline-evidence-bundle/lighting-fixture.blend`
- Source size: 28,962,072 bytes; unique mesh triangles: 581,780; instanced scene triangles: 1,244,986; target: 20,088 triangles
- Fine variant: 30,137,252 bytes; adds 1,175,180 bytes
- Soft variant: 30,281,664 bytes; adds 1,319,592 bytes
- No source colors or base-color textures are changed

The source normal scale is 0.4799999893. The application multiplies imported normal scales by 0.75. For this isolated test, every target comparison uses the resulting 0.3599999920 strength. All other scene materials keep the frozen offline fixture values. This makes target relief strength comparable to runtime; it does not make the entire offline renderer equivalent to the application. The normal-disabled control keeps the original target roughness but sets the target normal strength to zero.

The actual material assigned to the target is audited after fixture remapping. Each render manifest records that assigned material, its connected images and graph, and its exclusive target ownership. It also asserts that the original fixture materials and the light/world/compositor/render settings remain unchanged.

## Evidence and limits

The current close/reverse images and the actual NOAA colony photo were inspected before choosing a texture direction. The scientific reference is the Acropora Biological Review Team's 2005 *Atlantic Acropora Status Review*, species diagnosis on printed page 13 (PDF page 28):
https://repository.library.noaa.gov/view/noaa/16200/noaa_16200_DS1.pdf#page=28

The current species page and this older status review give differing branch-diameter ranges, so neither is used to calibrate this model. That description identifies a prominent tip corallite and raised, bract-like side corallites pointing toward the branch tip. It gives branch diameter as 0.25–1.5 cm, which is not a corallite-size calibration and has not been imposed on this existing model. This supports exploring shallow raised features instead of exclusively depressed random holes, but does not validate the generated pattern.

The NOAA species page and existing colony photo provide a second, qualitative visual reference:
https://www.fisheries.noaa.gov/species/staghorn-coral

A NOAA-hosted Caribbean identification guide also describes small projecting tubular features (printed page 3, PDF page 7):
https://repository.library.noaa.gov/view/noaa/558/noaa_558_DS1.pdf#page=7

Critical constraint: the frozen UVs are per-face planar projections of scene coordinates. They do not follow each branch. Neither candidate can guarantee tip-directed orientation. The test uses softly raised, open rims at varied rotations and a shallow base, plus low-amplitude between-feature irregularity. Those are original qualitative surface cues, not a reconstructed corallite anatomy. Feature spacing and slope are bounded artistic parameters, not measurements. No scan data or photo pixels were used to generate these maps. BCO-DMO scan files were not imported or sampled.

## Reproduce

Requires Blender 4.3.2, Python 3, NumPy and Pillow. Run from the workspace root; paths may be moved together or replaced with explicit paths. Rendering is Cycles CPU and uses the fixture's original 1120 × 700 resolution, 24 samples, no denoising, world, compositor, lights and camera lens. The guide-close, reverse-close and opening camera poses are copied exactly from the earlier evidence script.

```sh
python reef-surface-test-oct7/generate_surface.py
python reef-surface-test-oct7/patch_material.py coral-3d/source-model.glb
blender -b -t 8 --python reef-surface-test-oct7/render_surface.py -- reef-corridor-pass/offline-evidence-bundle/lighting-fixture.blend coral-3d/source-model.glb reef-surface-test-oct7/baseline --mode baseline
blender -b -t 8 --python reef-surface-test-oct7/render_surface.py -- reef-corridor-pass/offline-evidence-bundle/lighting-fixture.blend reef-surface-test-oct7/fine.glb reef-surface-test-oct7/fine --mode fine
blender -b -t 8 --python reef-surface-test-oct7/render_surface.py -- reef-corridor-pass/offline-evidence-bundle/lighting-fixture.blend reef-surface-test-oct7/soft.glb reef-surface-test-oct7/soft --mode soft
blender -b -t 8 --python reef-surface-test-oct7/render_surface.py -- reef-corridor-pass/offline-evidence-bundle/lighting-fixture.blend coral-3d/source-model.glb reef-surface-test-oct7/normal-disabled --mode normal-disabled
```

Run `python reef-surface-test-oct7/compare_evidence.py reef-surface-test-oct7` after rendering to verify matches and regenerate labelled sheets. A second generator run is hash-identical; see `rebuild-determinism-proof.json`.

`--views close,close-reverse,opening` selects the frozen views. `--save-blend` optionally saves the final imported scene, without overwriting the source fixture. Image references in the candidate GLBs are embedded. Metallic/roughness maps use R=255, G=roughness, B=0. Normal maps use OpenGL tangent-space +Y. All maps are Non-Color data. No base-color map is introduced.

## Provenance and reuse

The texture formulas, generators, normal and roughness map pixels are original work made for this project. No externally licensed texture or scanned geometry is embedded in the new maps. The existing source scene and fixture retain their existing provenance and rights. NOAA references are linked for factual and visual study; no additional permission or image license is claimed for them, and no reference photographs are redistributed here. Do not describe the maps as NOAA or scan assets. No public upload, Site change, GitHub change, paid resource or contact with an author occurred.
