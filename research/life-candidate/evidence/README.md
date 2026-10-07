# Route-wide life: real browser evidence

Source candidate e37dd1a, QA79d8b6e, actual run37577405341. Baseline is accepted public d0d5173. Geometry, textures and water-light bytes are unchanged.

Both reduced-motion fixed-view arms and the normal-motion arm passed sandboxed Chromium153 / SwiftShader checks. Three controlled cameras establish visibility, not native route navigation acceptance. Normal-motion samples cover51.2862 wall seconds and51.3146 simulation seconds (ratio1.00055); position, orientation and fin transforms all change. Screenshot capture overhead makes this longer than the planned36-second wait. The actual recording is included unchanged. No console errors were recorded.

At the fixed t0 midpoint, part of the nearer pair falls behind the bottom controls; later frames show the pair at mid-right. Pixel and full-motion review remains separate from technical assertions. These results do not measure a user's GPU FPS or prove ecological behavior. Hidden-tab recovery and clearance were local numerical/source tests, not an actual browser hidden-tab acceptance claim. Production was not changed by this QA branch.
