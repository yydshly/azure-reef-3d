# GitHub-hosted Pages rendering check

Manually run **Verify public Pages WebGL rendering** in GitHub Actions.
The ordinary Ubuntu runner installs pinned official Playwright/Chromium,
keeps Chromium sandboxing enabled and supplies no GPU-security bypass flags.

The first artifact records whether an actual WebGL2 context can clear/read a
pixel and reports its real vendor/renderer. If that is unavailable, the job
stops honestly; HTTP availability is not a rendering pass.

If the context works, the second phase loads the real public Pages website,
checks the served app/model-version against the checkout, waits for the real
model, captures UI-selected views with explicit camera snapping for software-renderer reproducibility and a short animation interval, and
records runtime errors, model state, marker positions (optional video with RECORD_VIDEO=true). Fixed cameras are explicitly recorded and do not validate transition smoothness. It neither
replaces the model nor mocks WebGL. Screenshots still require human inspection.

Software rendering, if reported by the actual context, can reveal shader,
appearance and UI faults. It does not establish user GPU frame rate, iPad
performance, biological realism, or final visual acceptance. Artifacts are
retained for seven days; the workflow has a twelve-minute maximum.

## Controlled candidate comparison

Use target_source=branch-preview only on an explicitly prepared QA branch. A loopback-only static server serves that checkout; it does not publish or replace Pages. view_set=passage captures the agreed departure, midway and look-back camera/target values via the existing app API. Actual coordinates are checked against requested coordinates, so constrained legacy cameras cannot be mislabelled as matching viewpoints. Native click/transition responsiveness is outside this fixed-camera test. The target is restricted to the project’s public Pages URL or runner loopback.
