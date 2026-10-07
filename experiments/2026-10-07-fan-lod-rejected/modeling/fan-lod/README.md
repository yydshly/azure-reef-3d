**REJECTED after actual run37598309469. [Decision](../../LOD_DECISION.md).**

# Distant true-3D fan representation

This candidate addresses the measured render cost of the inhabited reef stage. It does not introduce a new organism or change the original high-detail shape. The original primary stem/vein paths and outer profile are reused; a480-site reticulate network replaces the2200-site fine network at distance. Tube radii scale by sqrt(2200/480) to approximate integrated far-view coverage. This is an artist's rendering approximation, not anatomical evidence or biological growth simulation.

Both representations remain real polygonal tubes with sides and backs. The close model remains the unchanged original component. Runtime THREE.LOD selects distance from the fan geometry center,9 scene units for main fans or5.5 for small fans, with15% hysteresis. These thresholds are render settings, not measured ecological dimensions. The small-fan quality control applies to the whole detail group.

## Rebuild

From the repository root, with Blender4.3.2:

    blender -b -t 2 --python-exit-code 1 --python experiments/2026-10-07-fan-lod-rejected/modeling/fan-lod/build_low_fans.py -- modeling/inhabited/editable.blend /tmp/reef-low-fans

The recipe reads the original packed master for its exact attachment and material, and fan-network-low.json. To regenerate that original network, run make_network_low.py with NumPy2.3.5/SciPy1.17.0 (seed71028). Unused master meshes/materials/images are removed from the output; the editable file is about1.96MB and GLB859,492 bytes.

Alternatively:

    blender -b -t 2 --python-exit-code 1 --python modeling/inhabited/export_frozen_editable.py -- experiments/2026-10-07-fan-lod-rejected/modeling/fan-lod/editable.blend /tmp/reef-low-fans.glb

Both a fresh recipe run and packed re-export reproduced the frozen GLB exactly in the tested environment: d11ef2d64a9258b12ae95a89bc1f7cdb74a96edfa18424f960846230083460e0. This is a tested result, not a guarantee across different Blender/platform versions. High-detail generation and its UV/bake limitations remain documented separately in modeling/inhabited.

## Completed acceptance gate

Actual browser technical checks passed; visual review failed due to coarse polygonal cells and visible density/brightness transition. The small software timing increase does not override that rejection. No candidate assets are deployed.
