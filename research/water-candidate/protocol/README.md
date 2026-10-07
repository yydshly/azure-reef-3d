# Water-depth candidate, 2026-10-07

Status: candidate awaiting actual-browser A/B. Not accepted or deployed.
Baseline Site source: 117079e416ec2f7bf8438074fc2bda772590afe4. Production application remains the spatial release. No geometry, textures, fish trajectories, camera routes, exposure, or species labels were changed.

## Observed problem and bounded change

Actual software-WebGL midpoint evidence shows a nearly uniform gray-green seabed, strong regular white caustic cells at every distance, and dark sawtooth coral shadows. This stage changes water transport and readability across the whole existing space, not the world dimensions.

- Replaces a single post-output RGB fog mixture on standard materials with illustrative RGB exponential extinction by actual camera-to-surface distance, in linear radiance before tone mapping. Red coefficient .065, green .035, blue .025 per scene unit.
- Uses the same directional water-radiance function and tone mapping for surface haze and the enclosing water field, avoiding unrelated horizon color pipelines.
- Applies the caustic contribution to direct diffuse light after shadow evaluation, instead of multiplying albedo/ambient light. Two rotated texture scales reduce identical overlapping cells. Focus fades with distance and with depth below an illustrative y=8 surface.
- Direct downward light attenuation coefficients (.020,.008,.004) decrease light toward deeper model positions. The old height expression attenuated light in the opposite direction.
- Ambient hemisphere intensity 1.8→2.2, shadow intensity .72→.45. Sun intensity and exposure remain unchanged. This is an intentional readability adjustment, not measured underwater illumination or physically accurate shadow softness.

## Sources and limits

Read 2026-10-07:
- NOAA, https://oceanservice.noaa.gov/facts/oceanblue.html: wavelength-dependent absorption and the influence of suspended material; this supports the qualitative direction, not numerical coefficients.
- NOAA, https://oceanservice.noaa.gov/facts/light_travel.html: decreasing sunlight with depth; the large ocean light-zone depths are not used to assign this scene a measured depth.
- Pharr, Jakob, Humphreys, https://www.pbr-book.org/4ed/Volume_Scattering/Transmittance: homogeneous-medium exponential transmittance. This implementation is original simplified shader code, not the book's volumetric integrator.

RGB attenuation, water surface height, ambient/scattering field and caustic strength are artistic parameters in uncalibrated scene units. There is no wavelength-resolved integration, multiple scattering, measured turbidity, or wave-surface ray tracing. No new model, third-party image, or scientific species claim is introduced.

## Acceptance protocol

Same browser/renderer, viewport, model hashes and camera for each pair. Use reducedMotion:'reduce', leaveGuide(), setTour(false), then direct public camera/controls poses; both animation clocks stay at zero. Capture departure [1.5,2.1,4.8]→[-.5,.8,-6], midway [0,2.7,-18]→[-1.5,1,-31], look-back [-3.8,3.6,-36]→[0,.9,-8]. Record actual positions and assert no clamp. Confirm two spaced fish-state samples remain equal. Fixed-time screenshots do not prove motion.

Accept only if actual images show clearer near/mid/far underwater separation, readable near-reef detail/shadows, and less dominant far-ground light cells without a global black wash or shader failures. Retain naturalness limitations of repeated coral and sparse terrain. If this does not clearly help, reject it rather than publishing a color change as a realism achievement.

## Local checks

Passed shader injection/order and shared-radiance checks, attenuation direction, no duplicate standard fog, missing-WebGL behavior, five-stop guide/state and source-control simulation in normal/reduced-motion modes, forward/reverse/pause camera route and guide target-height regression. These are not actual WebGL shader compilation or user-input performance checks. Actual CI A/B remains pending.

Run tests using the bundled Three module without external installation:
`node --import ./qa-register.mjs qa-water-light.mjs`
`node --import ./qa-register.mjs qa-no-webgl.mjs`
`node --import ./qa-register.mjs qa-guide.mjs`
`node --import ./qa-register.mjs qa-guide-integration.mjs`
`REEF_REDUCED_MOTION=1 node --import ./qa-register.mjs qa-guide-integration.mjs`

## First actual-WebGL result and correction

Run37573369857: baseline rendered successfully, but candidate GPU shader compilation failed because the injected shared function ended immediately before `#define STANDARD` without a newline. Candidate screenshots from that run are invalid as visual evidence. Fixed only the shader-prefix separator and added an explicit preprocessor-line regression assertion. Both arms did confirm identical fixed-time fish positions. Actual rerender is required before visual acceptance.
