# Española: bounded measured-point surface reconstruction

Date: 2026-10-07. Research result only, separate from any production or Caribbean scene.

## Result

A 3 × 3 native-unit crop containing rounded real seabed outcrops was selected from the actual original RGB point preview. Full 3D ball pivoting retains the original point positions, including measured sides. One bounded correction to the estimated normals reduced small perforations. The final candidate contains **128,856 original vertices and 232,180 inferred triangles**, with 0.792304 native units of vertical relief.

**Accept for source-versus-derived research inspection. Do not accept as a finished production surface.** The two matched camera comparisons show better continuity than the original point splats and fewer small gaps than the first pass, but many genuine open boundaries remain. No bottom, back wall, missing coral, fauna, sand extension, or hidden geometry was invented. This is Española, Galápagos, eastern Pacific, not Caribbean habitat.

`matched-comparison-angle-a.png` and `matched-comparison-angle-b.png` show the original measured points at left and the derived triangles at right. Both use the same crop, camera, scale, background, original color interpretation and front-face-only triangle rendering. Source points are deliberately labeled as 2-pixel splats, not a solid measured surface. The images are deterministic offline CPU projections, not browser/WebGL screenshots.

## Source and exact crop

- Source: [Galapagos_3D, Zenodo record 14914807](https://zenodo.org/records/14914807)
- Original retained source: `../reef-underwater-assets-research/EspanolaFinalExperimentChunk.ply`
- Original file: 37,255,166 bytes; 1,284,651 XYZ + normal + RGB + class + confidence records; zero faces
- Original SHA-256: `f303f233dacb476de048555938ffe1feb0dfe8dc98cf35caacdf5c80eed05547`; rechecked unchanged after export
- Crop: X ∈ [1, 4], Y ∈ [-2, 1], all original Z; candidate B in `crop-selection-original.png`
- Measured crop bounds: [1.00003636, -1.99997568, -0.51924151] to [3.99999499, 0.99998516, 0.27306297]
- Original source-record indices: `crop-source-indices.npy`; no reordering or loss of the cropped source records
- Median nearest-neighbor spacing: 0.00871837 native units; p90 0.01083850; four exact duplicate XYZ records retained

The source paper, [Yuval et al. (2025), Remote Sensing 17(11), 1831](https://doi.org/10.3390/rs17111831), documents approximately 10 × 10 m plots, measured scale bars, and 1 cm point sampling. The full source extends almost exactly 10 × 10 native units. Interpreting one native unit as one metre is therefore well supported, but the PLY has no unit field and known-distance targets were not independently remeasured. All thresholds below are native units; millimetre equivalents are conditional on that interpretation. Neither the original photogrammetric accuracy nor the true unseen surface error is established by this test.

## Reconstruction recipe

One algorithm, Open3D ball pivoting, was tested twice. The sole correction changed the normal field; the crop, positions, colors, ball radii and triangle acceptance thresholds stayed fixed. No third reconstruction was run.

1. Read the original binary little-endian records and retain every point in the XY crop, with all Z values. Do not downsample, flatten to a DEM, reposition, denoise, smooth, or decimate points.
2. First pass: use the original supplied normals, normalized to unit length. This produced 234,896 raw and 211,289 accepted triangles. Keep its metrics, geometry and matched views in `attempt-original-normals/`.
3. Sole correction: calculate weighted local PCA directions from up to 24 measured points (including self) inside radius 0.025. Weights are exp(-(distance / 0.015)²). Require at least eight neighbors and smallest/middle covariance-eigenvalue ratio ≤ 0.5; otherwise keep the source normal. Orient each PCA direction toward the weighted mean of the original neighborhood normals, or toward the point's own source normal when the mean length is ≤ 0.25. No global +Z orientation is imposed. This re-estimates 120,696 normals and keeps 8,160 originals. Median angular change is 17.09°; 534 normals change sign relative to their source normal. The normal field remains an estimate, not measured truth.
4. Run `open3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting` with radii [0.010, 0.014, 0.018]. Final raw output: 239,640 triangles. Every mesh vertex is an unchanged source point.
5. Apply all of these fixed face filters: nonzero area (double area > 1e-10); every edge ≤ 0.025; each vertex's input normal within 75° of the oriented triangle normal; each pair of input normals no more than 90° apart; seven triangle probes each ≤ 0.010 from an original cropped point. The seven probes are the centroid, three edge midpoints, and barycentric weights (0.6, 0.2, 0.2) with all three permutations.
6. Remove rejected triangles only. Keep all source vertices in the output, including the 5,115 vertices not referenced by an accepted triangle. Never fill holes, connect to a bottom plane, extrude a crop boundary, add a shell, or increase the radii to bridge gaps.
7. Export binary PLY and one GLB. Preserve original coordinates and RGB values, with the explicit glTF color conversion below. The derived PLY stores corrected normals; the source PLY preserves original normals and all original vertex fields.

The correction reduced boundary edges from 49,767 to 26,190 (47.4%) and source points farther than 0.010 from the reconstructed mesh from 2,253 to 1,595. The two same-angle comparisons visibly improve small-gap continuity without changing the overall real outcrop relief or inventing a base.

Official method reference: [Open3D surface reconstruction](https://www.open3d.org/docs/release/tutorial/geometry/surface_reconstruction.html#ball-pivoting). Official installation reference: [Open3D getting started](https://www.open3d.org/docs/release/getting_started.html). The official PyPI binary package `open3d-cpu==0.19.0` was installed only inside this directory's virtual environment; no system settings were changed.

## Geometry preservation, support and topology

| Check | Final measured result |
|---|---:|
| Source position displacement / RGB8 difference | 0 / 0 |
| Source vertices referenced by triangles | 123,741 / 128,856 |
| Accepted triangles | 232,180 |
| Longest accepted edge | 0.02493817 |
| Largest of all seven-probe nearest-source distances | 0.00999059 |
| Conservative maximum distance from any triangle point to a source point | 0.01299754 |
| Source-to-mesh distance p50 / p90 / p99 / max | 0 / 0 / 0.01076719 / 0.03907854 |
| Connected components of referenced vertices | 82 |
| Triangles in largest component | 231,768 (99.8226%) |
| Edges used by more than two triangles | 0 |
| Open boundary edges | 26,190 |
| Boundary connected components / interior components | 3,606 / 3,455 |
| Surface area | 15.44447 native units² |
| Steep-side area (absolute triangle normal Z < 0.5) | 5.04613 (32.67%) |
| Downward-facing area (triangle normal Z < -0.5) | 0.43553 (2.82%) |

The all-triangle distance bound uses each acute triangle's circumradius, or half its longest edge for a right/obtuse triangle, then takes the maximum. Those vertices are source samples, so this bounds every interpolated point's distance to at least one source point. It is a support bound, not a claim of sub-centimetre ground-truth accuracy. Seven-probe checks are discrete supplementary tests and do not themselves prove an entire face is visible in original cameras.

BPA necessarily interpolates between neighboring samples. It can close sampling gaps below the permitted edge scale and cannot distinguish every real tiny cavity from a missing sample. Its empty-ball criterion, short edges, normal checks and source-distance limits constrain this inference; they do not prove all unseen sub-centimetre structure. Large unobserved regions have not been filled.

There are 2,697 simple interior boundary loops. Their bounding-box diagonal median is 0.02345, p90 0.03056, p99 0.04441, maximum 0.11251. Other boundary components branch and are not single physical holes: the largest interior boundary network spans 0.32699 in bounding-box diagonal. An interior boundary has no vertex within 0.035 of a crop edge. These sizes describe the mesh's open edges, not certified dimensions of natural holes. `hole-summary.json` and `metrics.json` retain the detailed definitions and data.

Final Open3D checks detect zero self-intersection triangle pairs and confirm edge-manifoldness when open boundaries are allowed. There remain 2,081 nonmanifold vertices; `is_orientable` is false, `is_vertex_manifold` is false, and `is_watertight` is false. The normal correction reduced nonmanifold vertices by 58.7%, but did not establish a globally consistent manifold. These remaining defects are a separate reason to reject production use, beyond the open holes. Exact results are recorded in `topology.json`. The sample must not be described as watertight or complete. The original-normal first attempt had zero detected self-intersection pairs but 5,034 nonmanifold vertices; see its separate audit. Further smoothing or patching has not been applied to hide this problem.

## Colors, material and coordinate convention

The original color has a strong cyan cast and underwater field illumination already baked in. Use it unlit for faithful inspection. It is not a calibrated albedo/PBR material and no new lighting, water fog, white balance, texture replacement, or normal map was added.

The source has RGB8 without an explicit color profile. Export treats these bytes conventionally as sRGB, converts them to linear float32 `COLOR_0` for glTF, and verifies an exact RGB8 round trip. PLY keeps original RGB8 bytes. Mesh interiors interpolate neighboring colors in linear space; they do not contain newly recovered image detail.

The GLB contains named `Source_points` (primitive mode 0) and `Reconstructed_surface` (mode 4) nodes sharing POSITION and COLOR_0 accessors. POSITION is original float32 XYZ. The root rotates -90° about X into glTF Y-up and translates X by -2.5 and Z by -0.5, centering the crop without scaling. `KHR_materials_unlit` and `doubleSided=false` are used. Both nodes exist in the default scene so a viewer can find them: hide Source_points initially and switch exclusively between them. Advisory `initialVisibility` extras are not standard glTF visibility. Use an sRGB output and no tone mapping. Back-face visibility must not be used as evidence of measured hidden surfaces.

## Deliverables and verification

- `espanola-measured-points-and-derived-surface.glb`: 5,881,608 bytes; SHA-256 `ca165e9372276274a625efa6f5b3b0fac0852ecf245fe4b9a525da3a1afcde99`
- `espanola-crop-derived-surface.ply`: all crop records with corrected normals, plus actual inferred triangle faces
- `espanola-crop-source-points.ply`: exact original cropped records, zero faces
- `matched-comparison-angle-a.png`, `matched-comparison-angle-b.png`: actual matched source/derived images
- `normal-correction-comparison-angle-a.png`: first pass versus sole normal correction at the exact same camera
- `original-points-angle-*.png`, `derived-surface-angle-*.png`: separate full-size panels
- `crop-selection-original.png`: selection evidence from the real plot
- `metrics.json`, `normal-correction.json`, `attempt-comparison.json`, `hole-summary.json`, `topology.json`: numerical audit
- `export-validation.json`: independent GLB buffer/face/color checks, both PLY round trips, original-file checksum recheck
- `render-settings.json`: exact camera directions, common target, panel scale and rendering convention
- `HASHES.json`: deliverable byte counts and SHA-256 checksums
- `ATTRIBUTION.txt`: full source credit, license, modifications and limitations

Exact core versions: Python 3.12.14; NumPy 2.3.5; SciPy 1.17.0; Open3D CPU 0.19.0; Pillow 12.3.0. `environment-freeze.txt` records the full environment. Main reproducible scripts are `prepare.py`, `reconstruct.py`, `export_glb.py`, `render_comparison.py`, `check_topology.py`, `validate_exports.py` and `summarize_holes.py`. They read the original file from the sibling research directory. The virtual environment is intentionally not a distributable artifact.

Export validation establishes correct local bytes, shared buffers, source-equal positions, valid index ranges, exact RGB8 color round trips and unchanged source hash. It does not substitute for the owner's separate real WebGL viewer check. No Site was published, no production checkout was edited, and no noncommercial Reefs4D data was used.

## Next concrete dependency

For a cleaner faithful production surface, obtain the higher-density photogrammetric cloud/mesh before 1 cm sampling, plus original calibrated cameras/images or depth/visibility confidence for this crop. That evidence can distinguish real small cavities from poorly observed samples and support reconstruction review. Simply increasing the ball radius or adding a Poisson shell would hide the missing-data question. No further reconstruction variants are part of this bounded test.

## Credit and license

Galapagos_3D (Española sample), Matan Yuval; Inti Keith; Franklin Terán; William Bensted-Smith; Wilson Iñiguez. Institutional provenance: Charles Darwin Research Station / Charles Darwin Foundation. [Source DOI](https://doi.org/10.5281/zenodo.14914807). [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). Modifications: crop, bounded PCA normal estimation, constrained BPA inferred triangles, coordinate/display transforms, color-space conversion, and labeled inspection images. Original XYZ and RGB retained. No endorsement is implied.
