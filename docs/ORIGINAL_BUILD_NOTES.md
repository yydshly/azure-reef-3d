# 浅蓝 · 立体珊瑚礁

An independent, bounded real-3D reef sample. The earlier 2.5D Site and original ocean-world repository were not changed.

## Scene

All reefs, rocks, coral branches/mounds, sand and fish are actual polygonal geometry. GLB assets include sides and backs; Three.js performs depth testing and occlusion. There is no reef backdrop image or billboard replacing the geometry. Four modeled fish follow independent three-dimensional trajectories, with articulated tails and fins. OrbitControls supports continuous camera rotation, zoom and panning. Three fixed camera angles and optional automatic orbit are available.

## Provenance

Original procedural Blender geometry and vertex colors, generated specifically for this Site. Current model: rebuild_reference_reef.py, reference-audit.json, glb-validation.json and texture-provenance.json. Original-generation files are retained as earlier provenance. No third-party coral models, paid assets, generated scene photos, user data, keys or backend are needed. Three.js 0.186.1 is vendored locally under its included MIT license. Browser materials use PBR colors/roughness, cast/receive shadows, analytical animated caustics and distance fog. Offline renders show the same exported GLB reimported into Blender; renderer lighting differs from browser lighting.

## Honest verification boundaries

The actual GLB was parsed by the production GLTFLoader and its meshes, normals, vertex colors and fish hierarchy inspected. Raycast sampling checks fish clearance and whether a close reef camera can observe coral occlusion; it is not a proof of continuous collision avoidance. The missing-WebGL2 interface was exercised in a simulated DOM: it explicitly explains that 3D did not start and labels reference images as offline, noninteractive renders. Source modules pass syntax checks.

Offline front and reverse-angle renders were visually reviewed. These are rendered-model evidence, not browser screenshots. Live WebGL shader execution, browser CSS and real input devices could not be tested in the current restricted browser environment. We do not claim those tests passed. No browser restriction or Site privacy gate was bypassed. When WebGL2 is unavailable, the app does not silently substitute a 2D scene.

## Controls

Drag to orbit; wheel/pinch to zoom; right-drag/two-finger drag to pan. Arrow keys orbit; +/− zoom. Power-saving mode caps pixel ratio, reduces frames and disables shadows/particles. Reduced-motion preference suppresses ambient animation until automatic orbit is explicitly requested. Hidden tabs stop scene updates.

## Reference-guided revision, 2026-10-06

The first colorful miniature-like model was superseded by a reference-guided Florida/Caribbean staghorn patch-edge interpretation. We inspected the actual NOAA staghorn photograph and NOAA/FKNMS Cheeca Rocks photograph before rebuilding. See references.html in the app for public sources, source-to-model decisions, same-view comparison, and limitations.

Removed unsupported tiered plates, thick candy-colored branches, blue/gold spherical mounds, scattered grass and symmetrical rock islands. New geometry uses unequal thin tan/brown interlocking thickets with pale tips, irregular low earthy mounds and connected rough limestone hardbottom. Generic fish remain explicitly unidentified and unvalidated; their scale and saturation were reduced. No claim is made that two reference photographs document the same community.

Six original procedural normal/roughness maps are embedded in the GLB, with actual exported UV coordinates and vertex-color bindings. These are authored textures, not scanned coral tissue. Browser lighting, depth haze and analytic caustics were adjusted; those runtime shaders remain unverified in a live browser. Offline comparisons show final GLB geometry/materials reimported into Blender under offline lighting.

Fish use geometry-aware precomputed closed spline routes, smoother orientation and tail/fin beats. Clearance and occlusion are sampled geometrically, not claimed as continuous collision-proof or biological behavior. Runtime route data is shipped locally; there is no per-frame physics or external API.

The previous 2.5D Site and original ocean-world repository remain untouched. The result still has procedural/stylized limitations and should not be described as photorealistic or scientifically validated.

The final GLB is retained as source-model.glb and losslessly externalized by export-static-model.py into reef.gltf, reef.bin, and six PNG textures for the host per-file limit. Geometry and texture bytes are unchanged; the browser loads the external glTF representation.

## Bounded substrate-edge correction

Inspected actual mesh coordinates and the same-camera image: the hardbottom grid had a clipped, raised border. The correction lowers a narrow irregular boundary band below the sampled neighboring sand surface. Geometry proof records 620 boundary vertices at least 4 cm below sand, with coral/fish meshes and transforms unchanged. The existing four-vertex sand underlay was extended to move its finite boundary farther away without adding scene features. A distant flat ground/world horizon remains visible in offline evidence. Before/after views keep camera and offline lighting unchanged.

The app reference page now provides an active three-part judgment: source-supported features, clear remaining deviations, and unknowns. This is evidence-based assistant review, not scientific or NOAA certification. Generic fish identity, species co-occurrence and calibrated water conditions remain explicitly unknown.

## Beginner-guided exploration

Five short, source-linked stops now connect the camera to visible objects: patch context, sand/hardbottom, coral as a colonial animal, generic fish and habitat structure, and light/water relationships. The guide starts in manual advance mode, offers optional automatic advance with reading dwell, previous/next, pause, source-details pause, and free exploration with resume. A projected marker labels each target. The fish stop follows a generic model while explicitly declining species or behavioral identification. Reduced-motion preference makes guide camera moves instantaneous.

The exact same geometry/materials remain. Two guide cameras were checked by actual offline reimport renders at vertical FOV 47 degrees. Logic checks cover movement-vs-reading timing, pause/resume, free mode, completion, invalid steps, and target projection around the responsive guide card. Browser CSS, real input and live WebGL remain unverified due to existing environment restrictions.

Education sources: NOAA Florida Keys habitats, coral reef/coral anatomy page, Creature Feature, and NOAA National Ocean Service coral-water facts. Per-stop claims, visible targets, and modeling boundaries are in dist/guide-data.js; the wider accuracy audit remains in the app’s source page. The unmodeled mangrove/seagrass habitats are described as context only.

## Bounded spatial-depth continuation

The scene now adds a few low, closed hardbottom rises and linked instances of the same existing staghorn meshes around the middle/distance. All original meshes and transforms, fish routes, materials and image maps are preserved. The generated 2.5D image informed near/middle/far composition only; NOAA references continue to constrain habitat and morphology. Hidden geometry is procedural inference, not image-to-3D reconstruction or a surveyed location.

Depth renders reimport the final GLB. Paired before/after views use the same camera and exponential-squared depth fog (#086778, density .049) to make geometry comparison fair. Cycles lighting/tone mapping differs from live Three.js; these images remain offline evidence, not browser screenshots. No backdrop image represents the reef.
