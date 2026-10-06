# Compact offline evidence renderer

This bundle reproduces the accepted supported-final opening/reverse views from an independently supplied GLB. It contains no reef geometry. The 6.47MB compressed lighting fixture retains the exact camera, two lights, world, compositor, render settings, and four material definitions actually assigned in the accepted evidence scene. Their six required authored maps are packed; no external image paths are needed. The accepted offline images have no projected caustic modulation; see the explicit correction below.

## Run

Requires Blender 4.3.2 (Cycles CPU available). No Python package installation is required inside Blender.

    blender -b -t 12 --python render_evidence.py -- lighting-fixture.blend /path/to/supported-final.glb /path/to/output

Output: opening.png, reverse.png, render-manifest.json. Input paths may be absolute or relative. The script has no workspace-specific paths. Thread count may be changed; small floating-point/noise differences may then occur.

Expected accepted GLB SHA-256:
`deac6a8e6d2173fc649023b763264f3b195fc5c084bf5a2c58c3ca76c4abcb0e`

The input hash is recorded, not enforced, so the same cameras can also inspect other candidate models sharing this material set. Missing materials cause an explicit error rather than a silent substitution.

## Meaning of these images

These are offline Cycles renders of a GLB reimport. They use identical static fish poses in both views and a saved offline lighting/compositing setup. They are not browser screenshots, runtime route verification, or evidence of runtime animated caustics. This fixture preserves the materials actually assigned in the accepted image scene rather than unused material datablocks from prior experiments.

`make_fixture.py` is also provided to reproduce the compact fixture from an accepted presentation .blend; it accepts source and output paths via CLI, removes all meshes/empties, preserves used materials with fake users, prunes unused datablocks, packs required images, and saves compressed. The source presentation scene is not bundled because it contains the full model.

`lighting-fixture.json` inventories retained objects, materials, and packed maps. Render Result is Blender's transient render buffer and is not a required external map.

## Verified reproduction

Both regenerated images were visually inspected and are visually indistinguishable from the accepted source images. They are not pixel-identical: sparse numeric differences are recorded in verification-comparison.json.

- opening: 27 of 784000 pixels differ; mean absolute channel error 0.00001180/255; maximum 3/255

- reverse: 56 of 784000 pixels differ; mean absolute channel error 0.00002519/255; maximum 5/255

For a compact GitHub supplement, include lighting-fixture.blend, lighting-fixture.json, render_evidence.py, make_fixture.py, README.md, verification-comparison.json, and verification/render-manifest.json. The verification PNGs are optional evidence; diagnostic logs need not be committed.

## Explicit caustic boundary correction

The accepted offline images DO NOT contain projected water-caustic modulation. An inspection of the actual final scene's assigned materials confirmed:

- Assigned Coral, Limestone, and Sand materials use only their authored normal and roughness maps
- Assigned Living coral.001 has no image textures
- Four unused suffixed material variants contain water-caustics.png, but none is assigned to rendered meshes

The earlier GLB reimport/remapping chose the unsuffixed/non-caustic materials rather than those caustic-bearing variants. Consequently, the accepted images show the saved warm/blue lighting, depth attenuation/compositing, and original PBR shading, without the experimental projected-caustic material effect. Earlier descriptions suggesting those accepted images contained projected caustics were inaccurate.

The compact fixture deliberately retains the materials actually rendered, so six packed maps is correct. It reproduces the accepted pixels and does not silently add the unused seventh image. No evidence image was changed to hide this mismatch. The separately implemented browser caustic shader remains unverified by this offline evidence.

`material-assignment-audit.json` records assigned and unused materials, their texture nodes, and the presence/absence of caustics. `inspect_materials.py` can reproduce that audit from the full accepted presentation scene using CLI source/output paths.

Export note: source-workspace prefixes in the recorded material texture paths were normalized to project-relative paths; assignments and measured values are unchanged.
