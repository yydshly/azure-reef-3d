# New solid shoulder — rejected macro form

This is a different topology construction from the previously rejected folded heightfield and bent thicket. Four unequal leaning five-sided convex solids are combined with exact Boolean unions; three oblique side cavities are subtracted; short edge bevels soften intersections. This remains an original inferred construction, not a scan, biological reconstruction or surveyed location.

Owner inspected matched75%,92% and reverse neutral renders. REJECT: the new parts appear as straight-faced blocks with cut holes, especially from92% and the back. At75% much of the new shape also falls outside the right frame edge. Negative volume and closed topology alone do not produce a believable coral-limestone skeleton. No runtime integration, material fix, browser test or production publication is accepted. No second parameter variant was made. The broader project continues independently.

Hard checks:3,764 added triangles,377,428-byte standalone GLB; positive signed volume, zero boundary/nonmanifold edges and zero degenerate triangles. The original terrain and landmark files were not modified. Four support-center heights were sampled against actual original terrain and the authored bottoms placed below those centers. This is not a proof that every support footprint is buried, a self-intersection certificate, or a full fish/camera clearance pass; those gates were not pursued after visual rejection. Units are uncalibrated scene units.

Evidence: six800x500 offline Cycles neutral frames, matched cameras/lights/materials. Context includes original source terrain with runtime near-thicket pruning and the exact FarRight landmark at its accepted pose; the other runtime-inserted landmarks and current fish refinement are omitted. Water/caustics/animation are omitted. These are local structural comparisons, not full production screenshots or performance evidence.

Reference actually viewed: NPS Dry Tortugas https://www.nps.gov/drto/learn/nature/corals.htm ; original photo https://www.nps.gov/drto/learn/nature/images/DRTO-DUW-046.jpg (NPS Submerged Resource Center). It supports qualitative irregular skeletal relief and cavities, not these invented dimensions or colony coverage. Photo pixels are not copied or redistributed.

Use installed Blender4.3.2. From this archive, set SOURCE to the project's unchanged source-model.glb (SHA c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd), LANDMARK to dist/assets/inhabited/bf93ec504f8f2fc3/pilot.glb (SHA d6377e6bcfc5145ef6da7c139de26772b6065b30fbe24c2d3180bcba9ae48cdf), OUT to a fresh directory.

    blender -b -t 4 --python-exit-code 1 --python build_solid.py -- --source "$SOURCE" --out "$OUT"
    blender -b -t 4 --python-exit-code 1 --python render_comparison.py -- "$SOURCE" "$SOURCE" "$LANDMARK" "$OUT/grey" --solid "$OUT/solid-shoulder.glb" --view actual-route-75

Repeat the same render command with actual-route-92 or neutral-reverse for the other fixed views. The build recipe was made portable after the original render; geometry parameters are unchanged. Original render-manifest paths are historical evidence, not portable inputs. No paid source, photograph texture, software install or third-party communication used.
