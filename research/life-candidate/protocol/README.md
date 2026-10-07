# Route-wide life and motion candidate, 2026-10-07

Status: local geometry/clock checks pass; actual-browser visual and motion acceptance pending. Based on accepted source82f5c24 / public d0d5173. Main geometry, water, textures and camera journey are unchanged.

## Baseline evidence before implementation

The four saved fish routes occupy z=-4.55…3.75; the exploration route reaches z=-36. Actual current-water screenshots (run37574417037 candidate arm, identical to accepted source82f5c24) show fish near departure but none readily noticeable in the midpoint/look-back images. Independent ray/frustum sampling over90 nominal simulation seconds finds visible fish in0/30 midpoint samples and10/30 look-back samples, requiring at least8 pixels projected body height at1120×700. This is a visibility diagnostic, not a density or ecological metric.

The earlier actual browser video from run37561682524 was inspected at100s and112s; fish change position only slightly across12 video seconds. Those two extracted frames retain older lighting and are labelled old-motion evidence, not current visual A/B. The source explains a relevant mechanism: it advances the animal/caustic phase by a per-frame delta capped at.06 seconds, so the simulation slows whenever rendering falls below~16.7 updates/second. This does not establish the user's device performance.

## Intended product change

- Keep two fish near the original guide; redistribute two existing fish to middle and distant reef areas and add one shared-mesh companion to each. Six total, with three activity areas instead of all fish near the entrance. Low quality hides the two companions.
- Each pair follows independently spaced, geometry-sampled paths with distinct periods/phases; smooth phase warping introduces slow lingering and cruising. No synchronized uniform carousel, sudden spawning near the camera or teleport between areas.
- Tail/fin amplitude and beat progression respond to route speed. Orientation uses a local path chord rather than very sharp spline derivatives, with a small bounded illustrative bank.
- Initial QA caught rapid target-heading changes in legacy/first candidate height paths. A conservative slope-limited upper height envelope removes abrupt climbs while staying above the sampled reef; heading spikes decrease from~10–15rad/s in the baseline target orientation to<3rad/s in this candidate. This is a numerical target-orientation check, not a measured biological turning rate.
- Fish/water phase uses visible elapsed wall time, separately from capped camera damping. The existing visibility handler resets the timing origin; hidden tabs and reduced-motion pauses do not accrue a resume jump. No paid asset or service.

## References actually checked

- https://floridakeys.noaa.gov/education/creature-feature.html describes grunts in shoals along reef ledges.
- Its Romain Chaput photograph was viewed in the cloud browser: https://sanctuaries.noaa.gov/media/img/20171017-fknms-bluestripedgruntsatsnapperledge-romainchaput-1000.jpg . It shows varied relative depth/orientation; it does not calibrate spacing, density or movement speeds. The copyrighted photograph is linked, not copied into the app/repository.
- https://qrius.si.edu/taxonomy/term/12168 describes diverse uses of bodies, tails and pectoral fins among bony fish. It does not validate this generic model's exact fin mechanism.
- https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/french-grunt/ was checked for the distinction between daytime reef aggregations and nocturnal foraging. This candidate does not identify its fish as French grunts or claim that its slowing motion is feeding or a diel migration.

The six generic fish, scales, pair sizes, speeds and activity areas remain illustrative. No species identification or real co-occurrence/density claim; no behavior model or fluid dynamics. No author outreach or new license acceptance.

## Local verification

`node --import ./qa-register.mjs qa-life.mjs --baseline`
`node --import ./qa-register.mjs qa-life.mjs`
`node --import ./qa-register.mjs qa-motion.mjs`
`node --import ./qa-register.mjs qa-guide-integration.mjs`
`REEF_REDUCED_MOTION=1 node --import ./qa-register.mjs qa-guide-integration.mjs`

The new independent triangle index checks all six trajectories across164 seconds at.1-second kinematic steps, terrain footprints at.5-second intervals and pair separation. Minimum sampled pair-center distance.5756; footprint-center clearance>=.4049 scene units; maximum.1s displacement.0657. This is sampled clearance, not continuous collision detection. New midpoint/look-back visibility is30/30 sampled times; reef occlusion remains possible in departure/low free-orbit views. Detailed JSONs are retained. Local tests invoke the actual app loop at dropped-frame intervals, hidden/resumed states and reduced-motion states; five-stop/route/reverse/pause and quality regressions also pass.

Rebuild routes with `node --import ./qa-register.mjs build-life-routes.mjs`; input GLB remains the accepted source model. The original four route inputs and original motion sampler are retained here as baseline data. Canvas dependency paths are inherited from the Site workspace; the portable GitHub export owner replaces them with the existing package dependency.

## Finite acceptance gate

Actual software-WebGL three-view baseline/candidate t0 frames must make intermediate/distant activity legible while keeping original near-guide fish. Then a normal-motion midpoint capture over~36 real seconds must demonstrate positional change, changing heading/fin pose and nonconstant travel, with recorded wall-clock versus simulation time. No hidden-tab/reduced-motion catch-up jump. Keep runtime errors zero and model hashes unchanged. Do not claim physical GPU frame rate, ecological accuracy or completion of the whole world. If motion is visibly jerky or pairs intersect, correct that concrete failure before publication.
