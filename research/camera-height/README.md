# Observation-height research

Four controlled screenshots of production a18e1f7 / Site source 6750ba6. Only camera y changes; the scene is byte-identical. Fixed reduced-motion time zero, viewport 1120×700, target, x/z and FOV stay equal. This is a camera study, not a production candidate or scientific-accuracy claim. No route traversal or performance test. Static camera clearance excludes animated fish and complete paths.

Initial run 37610285974 was cancelled after the author found the proposed y=1.45 violated the unchanged OrbitControls polar-angle limit. The corrected frozen input uses y=1.7, verified against the real controls module and static triangle clearance. No control limits were relaxed; this is an input-validity correction before visual evaluation.

Run 37610541045 captured both midway images with zero runtime errors, then an exact x-coordinate comparison rejected roundoff (8.88e-16 versus 0). The test now uses the existing .001 coordinate tolerance; a bounded continuation captures only the missing route75 pair. The initial failure and images are retained unchanged.
