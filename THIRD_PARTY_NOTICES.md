# Third-party notices and reference provenance

## Three.js

The browser bundle and helper modules under `dist/vendor/` and `dist/utils/` are from Three.js 0.186.1. The MIT license is retained verbatim at `dist/vendor/THREE-LICENSE.txt`. Development checks install the same pinned Three.js version.

## Development dependencies

`@napi-rs/canvas` 0.1.100 is used only by Node-side validation. Its package/license metadata is supplied through npm; it is not copied into the browser bundle. Python texture generation uses NumPy and Pillow under their respective upstream licenses. Dependency packages and caches are not included in this export.

## Original assets

Coral, substrate, sand, fish geometry and six procedural texture maps were authored for this project. The final GLB and editable Blender scene are included, with generation provenance and deterministic seeds. No purchased or externally scanned coral meshes are included.

## Scientific and photographic references

These sources informed modeling and beginner explanations. They are references, not endorsements or scientific validation of the model. The source pages retain their own image credits and terms; reference photographs are not redistributed here.

- NOAA Fisheries, staghorn coral morphology, color, growth forms and habitat: https://www.fisheries.noaa.gov/species/staghorn-coral
- NOAA/FKNMS, Mission: Iconic Reefs and Cheeca Rocks imagery: https://sanctuaries.noaa.gov/news/press/mission-iconic-reefs/
- Florida Keys connected habitats: https://floridakeys.noaa.gov/education/habitats.html
- Coral anatomy, reef structure and substrate: https://floridakeys.noaa.gov/corals/coralreefs.html
- Reef fauna: https://floridakeys.noaa.gov/education/creature-feature.html
- Light and water requirements: https://oceanservice.noaa.gov/facts/coralwaters.html

The app intentionally does not identify its generic fish to species or claim measured co-occurrence, depth, population density or water optics.
