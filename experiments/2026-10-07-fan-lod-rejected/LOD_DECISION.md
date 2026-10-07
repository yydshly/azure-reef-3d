# Fan LOD experiment: rejected

Decision: 2026-10-07. Frozen source: 5ac7f68ffc3b141af92c41c39ab1cb15d9989245. Production remains source 527ef99 / public 6f9dd123. No candidate deployment is accepted.

## Evidence

GitHub Actions run 37598309469 completed successfully as a technical test. Baseline/candidate used the same runner, four fixed cameras, frozen animation phase, original lighting and rock/fish geometry. Four whole/close views, seven labeled test-driven approach/retreat frames and video, and two native tour intervals per arm were captured.

The near main fan retains the original high mesh. Distance sequence 12, 9.5, 8, 6, 8, 9.5, 12 selected LOD levels 1, 1, 1, 0, 0, 1, 1. This validates selection/hysteresis, not visual acceptance.

## Visual rejection

The departure view is broadly stable, and the close main fan is preserved. However, midway and look-back show an obvious change from fine translucent branching to coarse polygonal wire cells at normal full-image viewing size. Same-distance lod-step-2 (low) and lod-step-4 (high) expose a conspicuous change in cell scale and apparent density/brightness. Owner pixel review and independent reviewer agree this fails the no-visible-degradation gate. Hysteresis delays the transition but does not hide the representation change.

## Performance, with limits

Baseline native intervals: 15.1296 s / 5 RAF / 0.330478 Hz; 15.3974 s / 5 RAF / 0.324730 Hz.
Candidate: 17.2280 s / 6 RAF / 0.348270 Hz; 17.2201 s / 6 RAF / 0.348430 Hz.
Paired rates are approximately 5.4% and 7.3% higher. These tiny samples on sandboxed Chromium ANGLE/Vulkan SwiftShader do not establish hardware-device FPS, statistical confidence or usable real-time performance. Both arms remain extremely slow. Source-estimated visible triangle reductions of roughly 18–24% do not imply equivalent render-time savings.

## Disposition

Retain the candidate, deterministic original coarse-network recipe, exact exported asset checksum, local checks and actual browser evidence as an unsuccessful experiment. Do not merge its dist into production, change thresholds, or start a mesh-density parameter sweep. Any later performance work should first measure a separate cost center while preserving accepted visible structure. Overall naturalness and real-time performance remain unaccepted.
