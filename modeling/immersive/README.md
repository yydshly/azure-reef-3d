# Reproduce the immersive-layout revision

These deterministic scripts derive the final geometry from the exact preceding model. No proprietary asset, image-to-3D service, or new species is used.

Prerequisites: Python 3, NumPy; Blender 4.3+ only for the editable .blend import/packing step. The water pattern generator also needs Pillow.

Obtain `baseline.glb` from the preceding GitHub model:

    git show 3f25f8af77821d589f44c8a07732652b5c2ce3a6:source-model.glb > baseline.glb

Required SHA-256: `22978ea17f029220f439dfab68a616e2fa3135dd0bc58b465a735ac09a036094`.
The scripts reject an unexpected input hash.

    python modeling/immersive/portable_corridor_patch.py baseline.glb corridor.glb
    python modeling/immersive/portable_depth_patch.py corridor.glb depth.glb
    python modeling/immersive/portable_supported_final_patch.py depth.glb baseline.glb source-model.glb
    python export-static-model.py
    python generate_water_caustics.py
    node build-routes.mjs
    blender -b --python modeling/immersive/pack_editable.py -- source-model.glb reef-garden-final.blend

Expected final GLB SHA-256: `deac6a8e6d2173fc649023b763264f3b195fc5c084bf5a2c58c3ca76c4abcb0e`.

The intermediate depth model seats branches on sand; it is deliberately corrected by the support stage. Only the final supported model is published. Eight distant thickets use existing shared meshes. Their partially buried supports reuse the original pre-corridor limestone mesh so the central trench is not repeated under every colony. Only the new shared support perimeter is feathered below sand to remove a visible rectangular edge; its central attachment surface is retained. Core geometry and guide targets are preserved. This is inferred terrain composition, not a measured habitat reconstruction.

Offline evidence uses matched static fish poses and a separate Blender lighting setup; the clean editable import deliberately contains only the geometry and authored materials/maps. Browser caustics, directional water color and animated route poses live in JavaScript and are not embedded in the GLB. Re-exporting a Blender import need not be byte-identical; use the deterministic patch chain for exact artifact reproduction.
