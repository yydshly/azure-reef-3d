# One branch-clump grounding repair

Baseline: private source 2372e912, public release a95871f. Only Corridor_Distant_Linked_03 moves, rigidly downward by 0.12711730762552115 uncalibrated scene units. Original detailed support, branch geometry, materials, textures, scale, rotation, counts and routes remain. No new pedestal, deformation skirt, reduced support or fan-motion experiment is included.

The original 21 basal caps comprise 11 entirely above the highest substrate, 8 intersecting it and 2 buried. The exhaustive projected-triangle overlay uses float64 clipping with a 1e-11 tolerance. Its maximum cap gap is 0.12211730762552115. This is neither interval arithmetic nor a physical survey. The translation places every cap below the surface with a 0.005 margin; the earliest primary-junction cross-section retains 0.2400835660 clearance. Annotated baseline frames identify visible detached ends. Not every dark end is floating.

The actual GLTF test verifies identical world-Y translation for all target vertices and unchanged other objects, geometry and materials. Repeat application is idempotent. Existing guide and no-WebGL simulations pass. Since X/Z remain fixed while the target moves down, its highest surface at every X/Z cannot rise. This preserves the existing sampled fish vertical-clearance check, not a new whole-body or free-camera collision certificate.

The owner inspected the fixed-light offline pose pairs and all four actual software-WebGL images from run 37677841832. An independent reviewer accepted the visible grounding repair in the same two fixed views. Main branches remain exposed. Read ACCEPTANCE.md for limitations. Publication uses the verified runtime placement rather than modifying the base GLB.

Measurement scripts retain local study references for traceability. The input model is the existing c12624b2 baseline. Reduced-support references belong only to the historical comparison. Portable archival path adjustments must be disclosed without changing computed reports.
