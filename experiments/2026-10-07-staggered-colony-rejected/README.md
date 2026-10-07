# Staggered lateral colony: rejected new-topology study

**Rejected at both the visual gate and exported-triangle gate. Do not integrate or publish this mesh.** One authored construction was made. There was no parameter sweep, source-graph warp, envelope rescaling, second radius pass, or post-review geometry adjustment.

The central intercrossing improves: the earlier large basket opening largely disappears. But the new thin side branches and needle tips vanish at 280px, leaving a pointed shrub-like framework. Branch mass and blunt-tip readability regress against the inspected NOAA live photograph. The reverse view still shows lower gaps. More authored tips did not produce a more convincing dense live thicket. The parent separately inspected the normal and reverse images and agreed with rejection.

The exported GLB also contains **16 nonmanifold edges with four incident triangles and inconsistent edge orientation**. Its polygon-stage Blender mesh had zero boundary and nonmanifold edges. This discrepancy appears in the triangulated export of the boolean junction surfaces. The cause was not repaired or fully isolated after visual rejection. The saved export verifier intentionally exits with failure.

## What changed, and what did not

Target: node 78, `Corridor_Distant_Linked_03`, using source mesh 47, `Coral_Staghorn_Thicket_11`. Nodes 51 and 66 also use that source mesh. The comparison assigns the standalone replacement only to node 78 in memory; it never edits the source asset or other instances.

The new graph has 21 independent main axes, 95 staggered lateral axes and 32 secondary lateral axes, with 148 authored terminals. All 21 original basal rings remain exact, and the first two original root rings are retained in authoring. Side branches within each basal shoot use 127 exact boolean unions; there are 21 connected mesh components. Incidental crossings between independent roots remain overlapping surfaces. There is no shared central trunk, same-height hub, copied museum mesh, or recursive binary-fork rule.

- Triangle count: 22,168 source; **21,722 candidate**
- Exported vertices: 10,901; primitive/index bytes: 391,956
- Candidate GLB SHA256: `4a6f291b0ffad79a6b9d9fba581c9944ba3009f035f38b8642d09f766b579b28`
- Original local Blender XYZ box: `[2.2926516533, 0.5468685031, -0.0284643434]` to `[5.2841258049, 3.1850326061, 1.2817138433]`
- Candidate box: `[2.5842962265, 0.5752319098, -0.0284643434]` to `[4.9939785004, 2.9999816418, 1.2566231489]`
- All candidate positions are within that original box. X extent decreases 19.45%; Y extent decreases 8.09%; top decreases 0.025091 uncalibrated scene units
- One lateral is analytically shortened before construction to remain within the original box; no whole-colony scaling or deformation is applied
- Main-axis lengths range from approximately 0.760 to 1.374 uncalibrated scene units

The `source-root-direction-diagnostic.json` and SVG preserve the useful diagnosis: every one of the 21 old first-axis horizontal directions aligns outward from the source centre, with normalized dot products from 0.9427 to nearly 1. This supports the radial-basal-layout diagnosis; it does not prove a biological mechanism or imply that changing directions alone solves visual density.

All production assets, Site files, GitHub, fish routes and public deployments remain untouched. The actual runtime memory change is zero. No full-scene candidate GLB was generated. A smaller bounding box and unchanged roots **do not establish fish-path clearance** inside the denser interior. Full animated clearance was not run after rejection.

## Evidence and references

The images are **offline Blender 4.3.2 / Cycles neutral-gray geometry diagnostics**, with identical camera, light, world, exposure, 24 samples and no denoising across each pair. They are not browser screenshots or underwater rendering evidence. The imported source GLB is present in both full-scene images; runtime-added landmarks, water effects and animated fish are absent. Material and lighting changes cannot resolve this shape rejection.

`normal-midpoint` uses the actual normal midway camera: glTF position `[0,2.7,-18]`, target `[-1.5,1,-31]`, vertical FOV 47°, aspect 1.6. `normal-reverse` reflects this camera and aim horizontally around the same fixed scene reference while retaining distance and height. `front` and `reverse` match the older closer neutral fixture. All normal and reverse thumbnail PNGs are directly rendered at **280 × 175**, not magnified crops. Target-only black silhouettes use the same uncropped 1120 × 700 cameras. Camera coordinates and complete output inventory are in `neutral-render-manifest.json`.

Actually inspected before authoring:

- [NOAA live staghorn photograph](https://www.fisheries.noaa.gov/species/staghorn-coral): continuous side branching at staggered heights, uneven axes, overlapping centre and multiple bases. Used only for qualitative morphology
- [Smithsonian Acropora cervicornis, USNM 74016](https://3d.si.edu/object/3d/acropora-cervicornis:dd875177-c986-48e2-9468-8e58f01099d3), original front and reverse views: dry specimen, CC0 source media and metadata according to acquired official provenance. Used for lateral-junction morphology only, not living color, growth, community, tissue or whole-colony dimensions

No source-photo pixels or specimen mesh data are copied. Reference image hashes are in `provenance.json`; the photographs and museum GLB are excluded from the archive. Units are uncalibrated scene units. This is not a species-accurate measurement or ecological reconstruction.

## Portable reproduction

Requirements: already installed Blender 4.3.2, Python 3 and NumPy. No network, new package installation, external texture, or repository mutation is needed. The two small `inputs/` files recover the exact original basal rings; the source-position replay gate must pass before construction.

The sole external data input is the unchanged production source GLB:

- Filename: `source-model.glb`
- SHA256: `c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd`
- Recorded source commit in the parent identification evidence: `480d20f7e097e2bfd4719e3e700154f04d1cd025`

Run from the archive directory, using a new sibling output directory. The build emits the same construction, graph/proof, standalone GLB and editable BLEND. The supplied small `replacement.glb` is the exact failed artifact inspected here; an extra identical rebuild was not run merely to claim byte reproducibility.

```sh
REEF_SOURCE=/absolute/path/to/source-model.glb
REEF_OUT=/absolute/path/to/staggered-reproduce
sha256sum "$REEF_SOURCE"
blender -b -t 4 --python-exit-code 1 --python build_candidate.py -- --source "$REEF_SOURCE" --out "$REEF_OUT"
python verify_replacement.py --source "$REEF_SOURCE" --out "$REEF_OUT"
```

The last command is **expected to exit 1**, recording the known 16 exported nonmanifold edges. Do not mistake successful polygon-stage construction for acceptance. Render diagnostic evidence independently with:

```sh
blender -b -t 6 --python-exit-code 1 --python render_neutral.py -- --source "$REEF_SOURCE" --out "$REEF_OUT"
```

The archive's explicit `WHITELIST.txt` includes the small failed GLB, executable recipes, branch graph, proofs, diagnostic diagram, and necessary before/after images. It excludes the full production GLB, reference photographs, large BLEND, logs and unrelated prior attempts. `manifest.json` records payload hashes and byte counts. Verify the archive with `sha256sum -c SHA256SUMS`.
