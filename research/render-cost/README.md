# QA-only renderer cost separation

Current production source 527ef99, public release 6f9dd123. This diagnostic follows rejection of the coarse fan LOD candidate; no lower-detail asset is used.

app-cost-probe.js preserves production app bytes and appends a small diagnostic API. Replace only app.js in an isolated QA snapshot of the current production dist. No production commit or deployment is authorized by a positive diagnostic result.

Use the same safe Chromium runner and a fixed departure camera, tour disabled and reduced motion enabled. Conditions: default, shadows disabled only, pixel ratio 0.5 only, then default again. Keep the same viewport/device scale and all original models/material inputs. For each condition, let three actual RAF callbacks complete after the mode change, record two approximately 15-second intervals of real wall time and RAF counts/intervals without screenshots, then save one clearly labeled diagnostic image and renderer/camera state. Assert camera and unchanged simulation phase, default drawing-buffer restoration, default shadow restoration, and zero runtime errors. Record actual canvas dimensions; do not assume pixel ratio 0.5 is half of an unknown baseline.

Interpretation: the shadow condition estimates the aggregate impact of disabling shadow generation and shadow sampling; it does not isolate either component alone. Reduced resolution estimates sensitivity to rasterization/fill and related per-pixel work. Neither measurement alone proves the bottleneck or predicts physical GPU FPS. The returning default measures gross within-run drift. Samples are small, and software rendering is exceptionally slow. No parameter sweep or automatic quality reduction follows this test.

A later production proposal requires a specific compatible optimization, preserved visual quality, and independent before/after checks. The existing world remains visually unfinished and real-time performance unaccepted.
