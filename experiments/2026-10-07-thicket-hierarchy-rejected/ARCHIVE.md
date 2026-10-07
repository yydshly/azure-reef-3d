# Rejected thicket experiment archive

All 25 original allowlisted files are preserved byte for byte; SHA256SUMS and the original manifest remain valid. The README is the original author record, including its historical workspace examples. No candidate geometry was integrated. Production stays at public commit db1f92122b39ba67cf0ec1d468bc89b7c09bd516 (Site source 480d20f7).

For a portable replay, start in this directory in a clone of the public repository. The existing root source-model.glb has SHA256 c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd. With the documented Blender/Python dependencies:

```sh
REEF_SOURCE="$(realpath ../../source-model.glb)"
REEF_OUT="$(mktemp -d)"
sha256sum -c SHA256SUMS
blender -b -t 4 --python-exit-code 1 --python build_candidate.py -- --source "$REEF_SOURCE" --out "$REEF_OUT"
python verify_replacement.py --source "$REEF_SOURCE" --out "$REEF_OUT"
sha256sum "$REEF_OUT/replacement.glb"
```

Expected replacement SHA256: 7012c9c0a502ff8fcbbca43b219d2c205bcfe11f20c8a61bbcf121312392964b. The author independently reproduced this hash; publication validation checked all allowlisted bytes and Python syntax, without another build or render. The optional render command and intentionally failing initial recipe are documented in the original README; use these same variables and a separate new output directory.

The 8 images are offline neutral geometry views lacking runtime-generated landmarks. They are not a complete production comparison. The normal view and thumbnail show a central empty basket and parallel curved rods, so the shape was rejected despite its envelope/topology checks. No browser test, deployment or new parameter search followed.
