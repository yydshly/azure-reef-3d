# Portable measurement inputs

The original floating-point measurement/proof files are retained unchanged. Historical extract/project/offline scripts have only path references adapted to repository-relative assets and archived QA reports. The original source hashes are in portability-inputs.json. The small simplified support GLB is an input to the historical two-arm measurement only; the published runtime still uses the original high-resolution support.

Use an isolated copy of this repository with Blender4.3.2 (mathutils) and Python NumPy. Extraction writes generated geometry-input.npz and basal-rings.json; run it before analysis/project scripts. Preserve the archived originals when rerunning:

```sh
blender -b --python-exit-code 1 --python evidence/branch-grounding-oct7/measurement/extract_geometry.py
python3 evidence/branch-grounding-oct7/measurement/analyze_grounding.py
blender -b --python-exit-code 1 --python evidence/branch-grounding-oct7/measurement/project_roots.py
```

The original package_report.py is not included; the frozen annotated image/CSV are evidence artifacts, not a claim that every historical packaging tool is supplied. Offline comparison render scripts remain distinct from actual water-shader screenshots. All lengths are uncalibrated scene units, and float64 overlay tolerances are not an interval-arithmetic proof.

Publication validation ran the portable extraction in an isolated temporary copy: Blender exit0, all21 basal-ring JSON records reproduced exactly and geometry-input.npz generated. The slower full overlay analysis and rendering were not repeated.
