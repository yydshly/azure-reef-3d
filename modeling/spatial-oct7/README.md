# Explorable reef spatial candidate

This candidate preserves the accepted foreground and adds a coherent extension along negative Z. A roughly 41 m camera passage moves from the original coral corridor through a wider sand opening, then looks back toward the original reef. This is an inferred shallow Caribbean-style reef composition, not a measured site or a new biome.

## Frozen artifact

- `spatial-candidate.glb`: 29,534,488 bytes
- SHA-256: `c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd`
- Required accepted input SHA-256: `a5d9412ede847ba165f1198967b487dd3787e3f71e5e25ed30831f40a7ac5a0b`
- No original checkout files, runtime files, publications, or remotes were modified by this geometry task

The input includes the accepted sand-boundary correction. All its original 91 nodes, geometry buffers, accessors, materials, images, textures, transforms and five guide anchors remain exact. The candidate appends one terrain mesh and four linked instances of different existing staghorn meshes. There are no new biological morphologies or species claims, assets, textures, or material experiments.

## Spatial composition

The added limestone spans x = -24 to 24 m and z = -61 to -11 m, with visible relief up to 2.04 m above the scene datum. Unequal elongated shelves form two interrupted reef margins around an open sand corridor. A few broad eroded recesses and asymmetric saddles break the long crests; two flanks have modest geometric roughness. Existing nearby thickets and support surfaces are kept clear.

The new mesh contains 10,190 vertices and 20,376 triangles. Its outer rectangular boundary is entirely buried at y = -0.4 m, below the existing sand floor at -0.22 m. Closed sides and a closed underside extend to -0.86 m. Independent edge checks found zero nonmanifold edges and zero inconsistent edge orientations, with positive outward signed volume.

Four coral occurrences reuse existing source meshes with differing scale/orientation. Their bases attach to modest local parts of the continuous limestone. A first visual pass caught a distant isolated platform in the sand channel; that placement was removed and the colony moved to the adjacent low ridge. The final asset has no such central platform. The four attachment checks measured every basal vertex below its actual triangulated rock surface by at least 1.50 cm.

The spatial motif is consistent with NOAA's description of reefs with sediment-filled channels and patch reefs, without claiming to reproduce any surveyed location: https://floridakeys.noaa.gov/corals/coralreefs.html

## Camera route in runtime / glTF coordinates

| View | Camera | Target |
| --- | --- | --- |
| Departure | [1.5, 2.1, 4.8] | [-0.5, 0.8, -6] |
| Mid passage | [0, 2.7, -18] | [-1.5, 1, -31] |
| Far opening | [-3.8, 3.6, -36] | [0, 1.2, -50] |
| Look back | [-3.8, 3.6, -36] | [0, 0.9, -8] |

The centripetal Catmull–Rom path uses [1.5,2.1,4.8], [0.2,2.4,-8], [0,2.7,-18], [-1.5,3.1,-27], [-3.8,3.6,-36]. `spatial-route.json` and `route-samples.json` contain the full data.

Against the final reimported GLB, 1,001 arc-length route samples have a minimum static-mesh clearance of 1.020679 m. The nearest object is an original distant thicket near z = -12.15 m. After half the largest sample spacing plus a 1 cm curve allowance, the clearance estimate is 0.989979 m. A 0.45 m camera sphere remains clear. Animated fish are excluded from this static geometry measurement.

## Reproduction and validation

The patch requires Python 3 and NumPy. It refuses an unexpected input hash.

```sh
python extend_spatial_relief.py accepted-sand.glb rebuilt-spatial.glb
python verify_spatial_asset.py accepted-sand.glb rebuilt-spatial.glb asset-verification.json
blender -b -t 8 --python verify_spatial_collision.py -- rebuilt-spatial.glb route-samples.json route-clearance.json
blender -b -t 8 --python render_spatial_evidence.py -- lighting-fixture.blend rebuilt-spatial.glb offline
```

`asset-verification.json` independently checks the actual exported bytes, preservation, bounds, triangle degeneracy, normal lengths and closed outward topology. `route-clearance.json` measures nearest static geometry and added colony support contact through Blender BVH queries. `spatial-candidate.proof.json` describes the added terrain and instances.

The fixed offline lighting fixture is the accepted sand-repair fixture, SHA-256 `f4ca30b9338ef08eeda09af95d94cee39508aa2eceb4eeaf9dd074bef58af55d`. The final `offline/` folder contains departure, mid, far-open, far-look-back and diagnostic overhead views. `offline-v1/` and `offline-v2/` are earlier diagnostic iterations and must not be used as final evidence or published assets.

## Verification limits

The images are Blender Cycles reimports with 24 samples and the prior offline fixture. They show real geometry from multiple views but do not reproduce browser lighting, caustics, water color, UI, fish motion, or the final runtime turn. The orthographic overhead image additionally omits depth fog. Actual webpage CI renders remain the final visual gate.

Only `spatial-candidate.glb`, the small deterministic recipe/verification files, route JSON and final evidence should be integrated. Do not copy earlier candidate renders or intermediate GLB variants into the publication package.

## Integrated repository layout

The root source-model.glb is the final spatial candidate. First regenerate the required sand input from published 7d7ee8f using modeling/sand-boundary-oct7/patch_sand_boundary.py, then run this folder’s extend_spatial_relief.py. The lighting fixture is modeling/immersive/offline/lighting-fixture.blend in the portable GitHub source. Proofs and route sample JSON are in evidence/spatial-oct7. The runtime route is dist/passage.js. Original historical fixtures and inputs must remain available; no source scan is used.

All dimensions follow the authored glTF metre convention. They are scene dimensions, not biological-size calibration or measurements of a real reef.
