# Rejected single-fan current study

See DECISION.md. Technical shader/phase/native-time checks passed, but the actual whole-view motion did not produce a sufficiently perceptible benefit. No runtime integration, amplitude scan or further test follows.

These are experiment source snapshots, not the repository root dist. To replay, use an isolated checkout of public a95871f3131f5c59ccfa17bbdd935de2455073c7; copy the two archived dist files and QA scripts into that isolated checkout, preserving all existing assets. Use the declared Three/canvas dependencies. The .mjs canvas dependency reference is normalized to @napi-rs/canvas; original input hashes remain in archive-manifest.json, final archive hashes in archive-file-sha256.json. The original candidate.patch and source-stage README are historical frozen records; final rejection supersedes their pending status.

Actual4 fixed frames, native video, raw reports and final rejection are permanently on qa/fan-current under evidence/fan-current-ci-37669614354. The first run37666030793 never reached WebGL because apt timed out. Recovery37669614354 used verified preinstalled libraries; missing CJK fonts mean its images do not validate Chinese UI. Fixed phases are test-driven, native observation is separate, and neither establishes user-device FPS or calibrated hydrodynamics.
