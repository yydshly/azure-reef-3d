# Inhabited reef asset and composition provenance

The production candidate uses an original, interpreted reef skeleton with two attached reticulate fan forms. The same asset is reused with different rigid poses and visible fan counts; it is not a scan or a claim of three measured colonies. Current whole-route placements and nearby-material blending are in dist/inhabited-reef.js. Units are artistic scene units.

References inspected visually: NPS Dry Tortugas, https://www.nps.gov/drto/learn/nature/corals.htm and its photograph https://www.nps.gov/drto/learn/nature/images/DRTO-DUW-046.jpg (NPS Submerged Resource Center); NOAA/FKNMS, https://floridakeys.noaa.gov/corals/coralreefs.html and https://floridakeys.noaa.gov/media/img/2021-fknms-molassesreef-softcorals-rachelplunkett-1000.jpg (Rachel Plunkett). They informed unequal skeleton height, recesses and attached fan/cover relationships. The photos are linked, not copied into textures. Hidden surfaces and biological-looking details are original inference, not field data or anatomy validation. The weak massive-cap attempt was rejected and excluded.

## Exact asset re-export

With Blender4.3.2 installed, from the repository root:

    blender -b -t 2 --python-exit-code 1 --python modeling/inhabited/export_frozen_editable.py -- modeling/inhabited/editable.blend /tmp/reef-shoulder.glb

The editable file includes its baked2048px color and1024px roughness images. Re-export with all source image paths cleared reproduces the frozen12,701,472-byte GLB exactly: d6377e6bcfc5145ef6da7c139de26772b6065b30fbe24c2d3180bcba9ae48cdf. Image labels are normalized by the script because Blender otherwise derives them differently from empty paths. See editable-reexport-proof.json. The unchanged runtime copy is under dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb.

## Procedural editing and its limit

    blender -b -t 2 --python-exit-code 1 --python modeling/inhabited/build_pilot_v3.py

This regenerates geometry and bakes to modeling/inhabited/structure-v3/. It uses the frozen original generated PNG and fan-network.json. To regenerate the network, use Python with NumPy2.3.5 and SciPy1.17.0, then run make_fan_network.py (seed71028).

A fresh procedural run was tested. It produced matching counts and extremely close positions (maximum2.2e-6 scene units), but Smart-UV packing, some normals and baked PNGs differed. Therefore procedural rebuild is an editable recipe, not the exact frozen-byte reproduction route. Use the packed editable file above for exact re-export. Re-running image generation also does not promise identical pixels; the frozen PNG is the source input.

## Material

assets/limestone-encrusting-albedo-v1.png is the original built-in image-generation output. Its complete prompt is preserved; its stated physical-looking scales were artistic guidance, not measurements. It is not a photographed tissue atlas or measured PBR input. The authored matte roughness range is.70–.94. No grass, shells, leaves or identified organisms are in this material. Surface color is mapped to the rock and baked into UVs. The same original texture is used with triplanar sampling on nearby hardbottom; sand and accepted water lighting stay unchanged.

## Rejected integration methods

v3's first browser placement floated visibly. Extending bottom vertices (v4) created a vertical skirt and stretched texture; it was rejected. The retained v5 rigid pose passed the narrow actual-browser local gate. All whole-route placements must be checked again for terrain/fish/camera clearance and actual full-view quality. The main world realism target remains open. LOCAL_ITERATION_LOG.md and the QA branch record passed and rejected stages; technical pass alone is not visual acceptance.

The existing base-world editable file remains separate. This packed file is the new reusable component; browser composition in dist/inhabited-reef.js supplies its final poses and fan omissions. It is not a standalone complete-world Blender file.
