# Galápagos source-data research viewer

This standalone research candidate compares measured XYZ+RGB points with a small, constrained triangle reconstruction. It is separate from the existing Caribbean interpretive world and is not production acceptance of a realistic complete underwater experience.

Source: Galápagos_3D, Española, https://zenodo.org/records/14914807 . Creators: Matan Yuval, Inti Keith, Franklin Terán, William Bensted-Smith, Wilson Iñiguez; Charles Darwin Foundation / Research Station. Licensed CC BY 4.0: https://creativecommons.org/licenses/by/4.0/ . Full attribution, associated publication, changes and scale caveats are in dist/ATTRIBUTION.txt.

The original source PLY is a colored point cloud, not a supplied mesh. The research pipeline crops x[1,4], y[-2,1] in native coordinates, retains all 128,856 measured positions/colors, and infers short local triangles with a constrained ball-pivoting reconstruction. A single local PCA-normal correction reduces small processing gaps without moving points or adding hidden geometry. Both stages and error limits are recorded by the geometry recipe. The final 232,180 triangles still have open boundaries, residual holes, 2,081 nonmanifold vertices and a failed orientability check. No self-intersections or edges incident to more than two faces were detected. It is unsuitable as a production collision or closed navigation mesh. No unseen bottom, new coral, animation, background habitat or smoothing of measured positions is added.

Published methods describe 10×10 m plots, known-distance scale bars and 1 cm point sampling; the source values are consistent with metres. The native PLY has no unit declaration, and the original scale bars have not been independently remeasured. Dimensions are not presented as a new field measurement.

## Viewer

Serve `dist/` with an ordinary local HTTP server. It uses bundled Three.js and no remote API, account, CDN, analytics or persistent browser storage. The model is a single immutable GLB containing Source_points and Reconstructed_surface objects with shared position/color accessors. The controls display only one representation at a time. Front faces only are rendered for the surface; missing reverse surfaces remain missing. The original sRGB colors are correctly converted to linear vertex colors and displayed without tone mapping or added water effects. This is an unlit source-data inspection, not a calibrated PBR material.

The page declares its Galápagos provenance, inference and license. No noncommercial Reefs4D asset is included. No production Site or existing production page has been changed.

## Validation

`node --import ./qa-register.mjs qa-viewer.mjs dist/assets/espanola-ca165e9372276274.glb`

The loader resolves the exact bundled Three.js for Node, without an npm download. Node 24 was used. The test parses the actual GLB, checks shared positions/colors, verifies exclusive controls, camera changes, source-position preservation, explicit missing-WebGL handling and context loss. DOM and renderer are simulated; this is not a browser screenshot or physical GPU test.

A separate real-WebGL CI capture is the remaining research-viewer acceptance step. Inspect the surface against the original points from the same camera, retain failures, and do not hide gaps with double-sided rendering or fog.

For controlled QA, `window.reefResearch` exposes `setMode('points'|'surface')`, `setView('front'|'reverse'|'top')` and `getState()`. Fixed-camera/API checks are distinct from native pointer input acceptance.
