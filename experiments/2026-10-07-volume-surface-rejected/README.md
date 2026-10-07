# Volumetric surface sample — rejected layout and macro form

Authoring continues from the separately rejected straight-faced solid, without altering production. The input is an original invented form, not scanned data. A0.065-scene-unit voxel remesh creates evenly distributed topology, followed by two declared scales of bounded spatial geometry warp and a triangulation-aware18,000-triangle decimation budget. Buried points receive zero warp. This is a procedural surface treatment, not a physical erosion simulation or proof of biological plausibility.

Owner inspected all three actual offline pairs. The formerly broad planar faces now have visible geometric relief, and side recesses remain, but75% framing still clips much of the added body. The92% and reverse views remain recognizably authored rocks, not an established realistic reef. No browser or production acceptance. No new material/texture shader and no scene source edits.

The first budget calculation counted polygons before triangulation and gave26,816 triangles; that arithmetic was corrected by triangulating before decimation. The final export contains18,000 triangles, zero boundary/nonmanifold edges and no degenerate triangles, one connected component, positive signed volume. These do not certify self-intersection absence or full support-footprint burial. New footprint clearance and original fish/camera routes are not yet fully verified.

The exact viewed asset is volume-shoulder.glb and its editable volume-shoulder.blend. Retain their checksums. Fresh procedural re-execution has not been shown byte-identical; Blender voxel/remesh/noise ordering may differ, and the intermediate runs had different measured maximum warp. Do not claim exact reconstruction from recipe without verifying it. The packed authored final mesh is authoritative for these screenshots.

All gray PNGs use the same contextual source/landmark and camera/light setup as the prior solid comparison. Water, caustics, animation, other runtime-inserted landmarks, and current runtime fish surface are not included. They are local offline structural samples, not complete production A/B screenshots.


## Final visual decision

Owner and independent review reject this sample for browser integration. At92% the new forms still read as softened vertical block levels. The reverse view exposes a long single-row attachment with a near-upright endcap. At75% most added structure is outside the right frame. Genuine recesses and single-component topology do not compensate for this macro layout. No further noise or texture tuning of this layout is accepted.

The overall project continues through a separate footprint/shape construction: staggered unequal supports, visible shore-side occupancy, separated peaks and a sand-facing cleft. That future work is not evidence that this sample improved production. Production geometry and rendering remain unchanged.


## Replay and archival boundary

The archive recipe's three input/output paths were converted to explicit command-line arguments; geometry parameters were not tuned. The frozen-mesh.json recipe hash refers to the original pre-portability recipe. manifest.json records the actual archive bytes. The omitted blend is named in the original frozen-mesh record but is deliberately not part of this small archive; the exact viewed mesh is retained as volume-shoulder.glb.

    blender -b -t 4 --python-exit-code 1 --python rebuild_volume.py -- --source "$SOURCE" --input-solid input-rejected-solid.glb --out "$OUT"

SOURCE is the unchanged project source-model.glb with c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd. Fresh generation is not claimed byte-identical. To reproduce the pictured geometry, use the retained exact volume-shoulder.glb as --solid with render_comparison.py, rather than silently substituting fresh stochastic output. Its shader-free fixed views and landmark input use the same contract as the preceding solid experiment.
