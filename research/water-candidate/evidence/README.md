# Actual water-depth A/B evidence

Run37573369857: baseline rendered correctly; candidate shader compilation failed because a preprocessor directive followed a function closing brace without a newline. Failed frames are diagnostic, not accepted imagery.

Run37573741470, QA commit34702e6 / candidate sourcef4334d2: both versions passed actual Chromium153 / SwiftShader WebGL checks. Three camera positions, original model bytes and fixed fish states match. Reduced-motion preference and tour=false hold the animation at phase zero. This is fixed-frame visual comparison, not moving-light or device-performance validation.

Production main was unchanged during these tests. Visual acceptance is a separate review and will be recorded by the scene owner.

Visual review rejected candidate f4334d2 from run37573741470: near sand became flat and the distant fade remained insufficient despite a technical pass.

One bounded correction (source96bcb513 / QA54b0ede) restores nearer light detail and strengthens distance attenuation. Run37574417037 passes both arms: six images, identical camera positions and fixed fish states, no console errors. Final visual decision remains with the scene review; no production deployment occurred as part of this evidence commit.
