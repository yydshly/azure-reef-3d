# One-fish surface prototype

This is an original, isolated appearance candidate for the existing generic `fish_03`. The isolated candidate passed a bounded six-frame actual software WebGL review before integration. See evidence/fish-surface-oct7/DECISION.md; this does not establish species realism or device performance. The source model is the accepted `coral-3d/source-model.glb`, SHA-256 `c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd`.

## What changes

`dist/fish-surface.js` replaces the hard vertex-level pigment selection on one body with a continuous object-coordinate material field. The original phase `x*34 + height*3` and its threshold `.56` remain. Pale and dark colors are fitted from that fish's existing subdued linear vertex colors, including the existing dorsal-to-ventral variation. Pixel derivatives antialias the band boundary. There are no new species markings, glitter, texture photographs, normal-map scales, or a replacement body shape.

The five existing fins keep their original outline, node names, node transforms, and animation interface. Their closed shallow prisms become closed, tessellated membranes, generally 12–34% of the original depth. Short collars preserve only support points needed for the exact whole-fish local/source-world bounds. Low-contrast procedural fan rays suggest membrane structure. This is a generic visual treatment, not an anatomical reconstruction, ray-count identification, or biomechanical validation. The tail's few required support tips necessarily retain original depth; the main membrane is thinner. Geometry remains real and visible from either side.

The fin volumes are 19.97–24.24% of their originals. Fin triangles rise from 44 to 1,024 in total, an increase of 980 on one fish only. Mesh/object counts, draw-mesh count, routes, time handling, and the six-fish population are unchanged. Two extra material program variants are expected; runtime GPU cost has not been measured.

## Integration contract

Import `refineFish03` from this module using the app's existing `three` import map. Place the call immediately after `addCompanionFish(root)` and before the existing fish traversal registers motion and applies its tail pivot:

```js
addCompanionFish(root);
refineFish03(root, {
  configureMaterial(material) {
    applyWaterLight(material, waterPattern, shaders);
    applySubstrateLink(material, substrateTexture);
  }
});
// Existing motion registration and tail pivot follow, unchanged.
```

The callback is required because Three.js material cloning does not retain the original shader hook. Surface code chains after the callback and adds only albedo treatment. Existing water attenuation, caustics, direct-light handling, roughness, depth testing, and shadow flags remain. Body and fin geometry/material resources are independent before mutation; `fish_05`, which shares `fish_03` resources immediately after cloning, remains untouched. Eye resources remain untouched too. Calls on the same fish are idempotent. Calling before companion creation or after the original tail pivot throws.

Do not apply the shader before adding the companion, replace the shared material globally, translate the tail here, change the fish population, or regenerate routes for this prototype.

## Verification

Run from the repository root:

```sh
node --import ./qa-register.mjs qa-fish-surface.mjs
python3 modeling/fish-surface-oct7/check-containment.py
```

`source-checks.json` records actual GLTFLoader-based checks:

- Exactly the `fish_03` body and five fins receive independent resources; all other object, geometry and material identities remain
- Every source resource stays byte-identical, including all attributes and indices of the cloned body; the companion remains exact
- All object names, parents, children, position/quaternion/scale values, shadow flags and object counts remain
- Whole-fish local and source-world bounds are identical before and after, including all six extrema
- All five fins have finite attributes, positive signed volume, no zero-area triangles, and exactly two consistently oriented faces per edge
- New materials retain the existing water shader sequence and no duplicate fog; the existing tail pivot leaves ray coordinates stable

`containment-checks.json` independently checks every new fin point against the original convex hull and the stronger original cap-triangle prism union, including the concave tail outline. Float32 edge interpolation has a maximum hull-plane roundoff of 1.5e-8 local units; tolerance is explicitly 4e-8. There is no measured enlargement at 625 articulated/headed support samples per fin. The construction uses only interior interpolation of the original paired depth layers. Applying the same rigid fin pivot/rotation and the same whole-fish affine transform preserves the conservative convex containment at all phases; this is not a claim of ecological or collision-system validation.

These are meaningful source/geometry/shader-assembly checks. They do not compile WebGL or establish browser appearance/performance. The subsequent actual browser gate passed at run 37616743352: unchanged midpoint and two labeled diagnostic fish views, using matched t0/camera/light conditions. Source tests and actual-browser results remain separate evidence.

## Offline specimen images

`render-offline.py` uses the actual exported JavaScript geometry and colors from `preview-input.json`. It renders matching baseline/candidate side and reverse-quarter views with the same fixed Cycles CPU camera and lighting. Candidate body pigment and fin rays use equivalent procedural Blender nodes without runtime pixel derivatives. The renders do not include the production water/caustic shader, do not test animation, and are not browser screenshots. See `offline-render-disclosure.json`.

```sh
blender -b -t 4 --python modeling/fish-surface-oct7/render-offline.py
```

## Visual references and limits

- [Florida Museum, sergeant major profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/sergeant-major/): the provided © George Ryschkewitsch image was viewed to observe how pigment follows a continuous curved surface. It is a reference to a real fish, not an identification of this generic asset. We do not inherit species colors, stripe counts, size, range, abundance, or ecology from it
- [Florida Museum, spines, rays and caudal fins](https://www.floridamuseum.ufl.edu/discover-fish/fish/anatomy/spines-rays-caudal-fins/): the provided anatomy diagram was viewed for the distinction between a membrane and supporting rays. The diagram is not copied into the model and does not certify this fish's topology or ray count
- The provided distant reef photograph credited to NOAA was viewed, but it is not detailed fin evidence and did not determine fin construction
- The actual accepted midpoint image was viewed to judge the existing color blocks and visible fin sheets

All shading and geometry changes are original procedural work. Reference photographs and the anatomy diagram remain outside this prototype directory and are not redistributed in the deliverable. No paid assets, accounts, installations, or external messages were used.

The generated specimen input is evidence/fish-surface-oct7/preview-input.json. The Python scripts now read that project-relative location; geometry and shading formulas are unchanged. The source checker uses the same existing canvas dependency convention as other project checks; GitHub portability normalization is recorded by the publisher.
