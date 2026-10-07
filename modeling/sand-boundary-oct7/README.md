# Sand boundary continuity correction

**Review verdict: accept the narrow asset correction. Nothing was published.**

The source contains a 3.84–12.16 cm rectangular gap between the 32 m sand grid and the existing far floor. A reachable, normal eye-height orbit view shows the gap as a conspicuous dark cut across the foreground. This candidate closes that cut with a smooth sand transition. The opening and reverse corridor compositions stay visually unchanged, as intended.

## Exact deliverable and inputs

- `sand-continuous.glb`: compact patched asset, 28,962,080 bytes
- Output SHA-256: `a5d9412ede847ba165f1198967b487dd3787e3f71e5e25ed30831f40a7ac5a0b`
- `source-frozen.glb`: exact frozen input, SHA-256 `ce6a7bc4d005ecd794d378c792d5d05d79f4683b10a2d3446333e6053ead4d21`
- `lighting-fixture.blend`: exact portable evidence fixture, SHA-256 `f4ca30b9338ef08eeda09af95d94cee39508aa2eceb4eeaf9dd074bef58af55d`
- `patch_sand_boundary.py`: minimal editable, deterministic regeneration source; Python standard library only

## Bounded change

Only the existing `Sand_Rippled_32m` POSITION.y bytes and its affected NORMAL bytes change. The outer 2 m band blends down to the existing far floor at y = -0.2199999988079071 m. The product of two quintic smoothstep functions gives zero first and second derivatives at the boundary and at the inner transition, without a diagonal corner crease.

Normals are transformed using the differential of that height blend applied to the original smooth tangent planes. Perimeter normals are exactly [0,1,0], matching the existing far floor. No normals in the original core are changed.

The 10,000 core sand vertices retain exact position and normal bytes. All triangles, x/z coordinates, UVs, vertex colors, textures/images, material records, node transforms, coral/fish geometry, far-floor geometry, rocks, and support geometry remain unchanged. The only JSON changes are the main sand POSITION accessor bounds. No geometry is added or resized. No prior material experiments are integrated.

## Reviewed matched comparisons

All six final images are 1120×700 offline Cycles renders, Blender 4.3.2, 24 samples, no denoising. Each A/B pair uses identical cameras, lights, fog, PBR materials, world and rendering settings from the frozen fixture. Fish are in their exact static GLB poses. These are not browser captures; runtime motion and caustics are not present or verified.

1. **Reachable edge view: clear improvement.** [Before](before/edge.png) / [After](after/edge.png). The dark foreground cut disappears into continuous sand. There is no replacement trench, bright halo, or new floating rock edge. Camera in runtime coordinates: [-20.5,1.6,0], target [-6.9,.3,0]. Its full target radius is 6.906519 m, camera distance 13.661991 m, and polar angle 84.539787°, within the provided orbit limits. The cliff is visible without a microscope, zoom crop, or lighting/fog change.
2. **Opening corridor: preservation check passed.** [Before](before/opening.png) / [After](after/opening.png). The biological composition and primary ground appearance are essentially unchanged. This view alone does not establish the boundary improvement.
3. **Reverse corridor: preservation check passed.** [Before](before/reverse.png) / [After](after/reverse.png). The coral, fish, and rocks stay fixed. Again, the targeted reachable edge view supplies the visual evidence of the correction.

The earlier outward-looking edge diagnostic is retained separately in `diagnostic-outside-orbit/`; its target lay beyond the runtime target limits and it is excluded from the acceptance gate.

## Measured checks

- All 460 perimeter vertices match the far-floor height exactly: residual 0 m
- Maximum perimeter normal angle falls from 8.0179° to 0°
- 3,456 vertices affected; 10,000 core vertices unchanged
- Maximum lowering: 0.121615 m; no sand vertex goes below the far floor
- The first triangle row meets the floor with at most 0.5784° slope; all triangles keep positive upward area
- All eight distant support outer perimeters remain at least 0.297537 m below the far floor, so lowering the sand does not expose their open outer boundaries
- The separate nearby-support diagnostic shows a little more of an unchanged rock face where the sand is lower, without a floating base
- All 59 non-sand meshes retain identical geometry and shading hashes; all 91 nodes and their transforms remain identical
- Exact guide anchors at sand [-1.0108096,-.1403618,2.8146734] and hardbottom [-.3038789,-.00275017,3.6140898], plus their complete camera-to-anchor ray segments, lie inside the unchanged core
- Deterministic regeneration was repeated and yielded the exact output hash above

Detailed reports: `sand-continuous.proof.json` (all accessor hashes and binary/JSON preservation checks), `geometry-verification.json` (per-mesh hashes, edge measurements, profiles, and rock support checks), `json-byte-change-proof.json` (exact preservation of every JSON byte outside the main sand position accessor, excluding padding), `edge-camera-reachability.json`, and `image-comparison-metrics.json`. Render manifests are in `before/` and `after/`.

## Portable recipe

From this folder, with Python 3 and Blender 4.3.2 installed:

```sh
python patch_sand_boundary.py source-frozen.glb rebuilt.glb
python verify_geometry.py source-frozen.glb rebuilt.glb rebuilt-verification.json
blender -b -t 8 --python render_evidence.py -- lighting-fixture.blend source-frozen.glb rerender-before --view all
blender -b -t 8 --python render_evidence.py -- lighting-fixture.blend rebuilt.glb rerender-after --view all
```

The patch itself has no dependencies beyond Python's standard library. The independent verification script requires NumPy. The source hash is enforced before any edit. Use this frozen input; do not substitute a mutable project asset. Rendering imports the GLB and restores presentation materials by exact base name from the fixed fixture; it does not re-export the asset.

## Verification limit

WebGL2 creation was already blocked in the cloud browser. This work makes no browser-verification claim and uses no browser, socket, or security workaround. Site/GitHub and published assets were not edited. Integration remains a separate decision by the owning task.

## Repository reproduction layout

The files listed above describe the separate review bundle. In this repository, obtain the exact pre-fix GLB from published commit `7d7ee8f4445f4c1fe9051637685ba322c1aaa57b:source-model.glb`. Its required hash is `ce6a7bc4d005ecd794d378c792d5d05d79f4683b10a2d3446333e6053ead4d21`. The existing offline fixture is `modeling/immersive/offline/lighting-fixture.blend` in the portable GitHub package. Do not substitute the current, already-patched model as input.

    git show 7d7ee8f4445f4c1fe9051637685ba322c1aaa57b:source-model.glb > /tmp/reef-sand-before.glb
    python modeling/sand-boundary-oct7/patch_sand_boundary.py /tmp/reef-sand-before.glb /tmp/reef-sand-after.glb
    python modeling/sand-boundary-oct7/verify_geometry.py /tmp/reef-sand-before.glb /tmp/reef-sand-after.glb /tmp/reef-sand-proof.json
    blender -b -t 8 --python modeling/sand-boundary-oct7/render_evidence.py -- modeling/immersive/offline/lighting-fixture.blend /tmp/reef-sand-after.glb /tmp/reef-sand-render --view all

The accepted output is the root source-model.glb; detailed verification records are in evidence/sand-boundary-oct7. No biological mesh or material is changed.
