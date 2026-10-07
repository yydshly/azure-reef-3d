# Rejected visible-ledge experiment

**Do not promote this candidate.** One fixed lateral-fold method was tested and stopped. The 75% and 92% target views show a real visible underside, but the shape reads as a broad folded ribbon/cap. Exact geometry checks also found **12 improper terrain intersections**. See [REPORT.md](REPORT.md) and [the independent diagnostics](visible-ledge-independent-validation.json).

This archive contains the reproducible recipe, validator and offline evidence. It intentionally excludes the 29 MB reconstructed candidate, accepted source/landmark assets, render logs, caches, and original reference photograph. The candidate can be regenerated from the two exact input assets below.

## Inputs

- Accepted source GLB SHA-256: `c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd`
- Unmodified landmark GLB SHA-256: `d6377e6bcfc5145ef6da7c139de26772b6065b30fbe24c2d3180bcba9ae48cdf`
- Expected regenerated candidate SHA-256: `9e0cb3f417905582b7947e5fc4e239dbd6596e3bea6905921c177903356e4239`

The accepted source is `source-model.glb` at public release `a18e1f71455e76dd7a3bd8a1980a891228928a85` (Site source `6750ba68bb139c85c4ed5ca77d8d109200358a53`); the landmark is the accepted `dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb`. Supply their actual local paths as arguments. The scripts reject mismatched source hashes.

Dependencies: Python 3 with NumPy, Pillow for pair labels, and Blender with glTF import/Cycles for rendering. The exact geometric checker uses Python integer/rational predicates and NumPy; it does not require a mesh-repair tool or new geometry package.

## Reproduce

From the directory containing these scripts:

```sh
REEF_SOURCE_GLB=/absolute/path/to/accepted/source-model.glb
REEF_LANDMARK_GLB=/absolute/path/to/accepted/pilot.glb
mkdir -p output

python fold_visible_ledge.py \
  "$REEF_SOURCE_GLB" "$REEF_LANDMARK_GLB" \
  output/visible-ledge-candidate.glb

python validate_folded_ledge.py \
  "$REEF_SOURCE_GLB" output/visible-ledge-candidate.glb \
  "$REEF_LANDMARK_GLB" output/visible-ledge-independent-validation.json

blender -b -t 6 --python render_grey_comparison.py -- \
  "$REEF_SOURCE_GLB" output/visible-ledge-candidate.glb \
  "$REEF_LANDMARK_GLB" output/grey --view actual-route-75

python compare_renders.py output/grey actual-route-75
```

Repeat the last two commands with `actual-route-92` and `neutral-reverse` for the remaining fixed views. The exact camera and fixed illumination are encoded in the renderer, including the unchanged landmark pose and the requested reticulate-fan omission. The small fan remains.

The preservation-only patcher does not assert that its output is an embedded solid. Reproduction is expected to recover the same **failing** 12-pair intersection result. Changing parameters to eliminate those intersections would be a new experiment and is outside this stopped sample.

## Evidence

- [75% pair](grey/comparison-actual-route-75.png)
- [92% pair](grey/comparison-actual-route-92.png)
- [Reverse pair](grey/comparison-neutral-reverse.png)
- [All three pairs](grey/all-three-comparisons.png)
- [Full failure report](REPORT.md)
- [Preservation proof](visible-ledge-candidate.proof.json)
- [Independent intersection/contact diagnostics](visible-ledge-independent-validation.json)
- [Concise independent validation summary](visible-ledge-independent-validation.txt)

All images are offline grey structural comparisons, not browser/runtime validation. Reference use was limited to macro form study of [NPS Dry Tortugas corals](https://www.nps.gov/drto/learn/nature/corals.htm), image DRTO-DUW-046.jpg, credit NPS Submerged Resource Center. No reference pixels appear in the candidate or this archive. Dimensions are interpreted scene units.

## Archival and diagnostic scope

Production is unchanged. No WebGL run or new render was performed for this archive. A separate read-only visibility diagnostic is retained under diagnosis/:935 sampled rays at75%, only10 reached the previously modified bank. It explains the earlier grey experiment's weak visibility, not acceptance of this folded ledge. The candidate has12 improper intersections and35 new rear contacts; the prior cavity gap shrinks from.95 to.1555 and is not preserved.

Portable edits only: this README names the public input commit; diagnosis script imports/read paths now resolve against the repository and uses the existing @napi-rs/canvas package. Run from the repository root after npm ci: `node experiments/2026-10-07-visible-ledge-rejected/diagnosis/trace-visible-bank.mjs /tmp/reef-visible-bank-rays.json`. Original input-file hashes are preserved in archive-source-sha256.json; archive-file-sha256.json records these actual copied/adapted files.
