# Rejected, controlled coral-surface experiment

Neither candidate is used by the application. Both were rejected because fixed close/reverse/opening views did not show a convincing visible improvement. See ../../evidence/surface-oct7/EXPERIMENT.md for the observations, sources, and limits. Geometry, UVs, colors and light were fixed; target normal strength was 0.36, matching the application's 0.75 multiplier on the imported 0.48 value. These were offline material controls, not browser screenshots.

The code is original procedural work. No NOAA photograph or BCO-DMO scan pixels/geometry were copied into the maps. Planar UVs do not guarantee the tip-directed corallite orientation described by the NOAA review. No biological calibration is claimed.

Reproduction from a checkout of the public source repository (Python 3, NumPy, Pillow, Blender 4.3.2):

    mkdir -p /tmp/reef-surface-study
    git show 7d7ee8f4445f4c1fe9051637685ba322c1aaa57b:source-model.glb > /tmp/reef-surface-study/baseline.glb
    python modeling/surface-experiment-oct7/generate_surface.py --out /tmp/reef-surface-study/textures
    python modeling/surface-experiment-oct7/patch_material.py /tmp/reef-surface-study/baseline.glb --out /tmp/reef-surface-study
    blender -b -t 8 --python modeling/surface-experiment-oct7/render_surface.py -- modeling/immersive/offline/lighting-fixture.blend /tmp/reef-surface-study/baseline.glb /tmp/reef-surface-study/baseline --mode baseline

Render the generated fine.glb and soft.glb with their corresponding --mode and output folders, then the baseline GLB with --mode normal-disabled. Run compare_evidence.py against that temporary output folder. Large rejected candidate assets and images are intentionally kept outside the live application.
