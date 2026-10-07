# Reef iteration record

## 2026-10-06 · Immersive first-version visual pass (checked revision)

### User-facing goal

Build a complete spatial scene first, then improve believability: tranquil breadth, blue depth, layered life, moving underwater light, and the feeling of being surrounded by water. Keep the source-grounded beginner guide.

### Concrete acceptance checks

1. Opening view feels inside a continuous reef environment, not above a tabletop patch
2. Foreground, middle and distant terrain remain distinct, with clear near details and natural-looking distance attenuation
3. Underwater light has visible, restrained movement; rigid hard coral does not wave like vegetation
4. Fish turn and move through real depth without obvious route jumps; generic identity remains explicit
5. Five guide stops and correct sand/hardbottom pointers still work
6. Geometry, material provenance, source-to-model limits and tests are recorded

### Baseline assessment

The current model has real middle/distant geometry, but the high opening camera and flat presentation still read as a model display. The existing staghorn form remains visibly procedural. A generated earlier image is useful for composition only; NOAA references continue to govern biological claims.

### First planned change

Evaluate an eye-level opening camera and stronger directional light/depth separation against the unchanged GLB before adding more geometry. This isolates whether framing and light improve the stated experience. Offline render evidence will be labelled as such; it cannot prove live WebGL appearance.

### Validation boundary

The cloud browser has previously reported unavailable WebGL2, and the private Site also has a sign-in gate. Neither is bypassed. Browser rendering remains unverified until a supported actual rendering route is available. No photorealism or scientific validation is claimed.

### Changes selected after actual image review

- Lowered the opening view to a swimmer-like observation height, retaining unrestricted orbit controls within the existing bounds
- Opened a winding sand gap by translating ten existing thickets and smoothly lowering the existing hardbottom below the unchanged sand mesh; no new coral species or morphology was inferred
- Preserved the original sand and hardbottom guide anchor geometry and first-hit visibility, and the main coral teaching specimen
- Added an original deterministic wave-slope caustic texture, a moving material-light approximation, and a directional water-color field; these are artistic optics rather than measured water parameters
- Rebuilt swim routes after the changed thicket layout exposed a clearance failure; increased route sampling and body-width footprint sampling rather than weakening the clearance check

The same-view opening and reverse offline images visibly establish that the prior branch wall is broken into readable banks around real intervening space. Independent image review still found the flat sand-to-water horizon insufficiently immersive; this prompted a further middle/distant layout pass rather than declaring the visual target complete.

### Habitat attachment check

A further audit caught a distinction between numerical grounding and ecological plausibility: new distant thickets could be physically seated on sand yet lack a hard attachment substrate. The final asset must expose existing-form limestone beneath those new patches or relocate them onto existing hardbottom. Geometry clearance alone is not evidence of a supported habitat relationship. This issue is corrected before publication, rather than leaving it for the viewer to diagnose.

### Checks and remaining limits

- Reimported and inspected same-camera opening and reverse images of the final geometry; intermediate layouts are retained in the reproducible patch chain
- Five-stop guide logic, actual app wiring under a simulated renderer, low-performance distant-object toggles, and reduced-motion wiring pass
- Shader insertion, uniforms, caustic-image dimensions and water-envelope settings pass structural checks; actual GPU compilation, realtime color appearance, input feel and frame rate remain unverified
- Sand/hardbottom guide rays hit the correct first surfaces at all three tested viewport sizes
- Full-period route samples pass: minimum center-to-top-surface clearance about 0.40m; several fish show depth occlusion across the tested presets and lateral orbit view. This is not a continuous body-collision or behavioral simulation
- Normal quality now includes extra distant instances. Low-performance mode hides these added distant thickets and their supports, as well as its existing shadow/particle/resolution reductions. No device performance guarantee is made

Decision: publish this checked improvement and retain the first-version visual goal as open. The readable sand passage is a meaningful advance, but branch morphology still looks procedural, the horizon transition is simple, and offline images do not establish the intended live flowing-water experience. Further presentation work requires actual GPU-rendered review to close that gap responsibly.

Final geometry SHA-256: `deac6a8e6d2173fc649023b763264f3b195fc5c084bf5a2c58c3ca76c4abcb0e`. The last reverse-view check caught rectangular support edges; the new support perimeter was lowered below sand and re-rendered before release. All eight sampled basal attachment sets hit their corresponding limestone supports, with positive gaps below 8mm. Original core bytes and anchors remain preserved.

The portable three-step patch chain was rerun independently from the preceding baseline and reproduced the final GLB byte-for-byte. Static deployment keeps its largest file, reef.bin, at 24,041,060 bytes. Final checks also retain explicit WebGL failure handling without a misleading interactive-2D substitution.

## Evidence boundary correction

Material-assignment audit established that the accepted offline comparison images contain no projected caustic modulation. Unused suffixed material variants had the water texture; actual rendered materials did not. No image was replaced to conceal the discrepancy. Browser water-light code has structural checks only. The compact, geometry-free fixture under modeling/immersive/offline reproduces the pixels actually inspected and records the numerical comparison.

## 2026-10-06 · Preserve original growth layout, repair junction artifacts

Actual NOAA staghorn pixels were compared with fixed close and neutral views. Two replacement-colony designs passed numerical geometry checks but failed visual review: they imposed a sparse connected framework on an originally multi-stem thicket. Neither was deployed. Their rejection and the corrected scope are recorded in evidence/junctions/EXPERIMENT_LOG.md.

The accepted approach reproduces every original thicket's vertices exactly from the original seed and only removes the artificial nonterminal narrowing/continuation discontinuity. All 22 source thickets pass exact replay; 1,155 recorded continuation joins are corrected. Axes, terminal tips, basal networks, envelopes, transforms and materials remain intact. Owner and independent review inspected before/after front/back neutral views and full opening/reverse images. This is a narrow visible defect correction, not a claim that the complete scene now meets the realism target.

A too-small spatial seam-merge tolerance initially reported false export boundaries. Exact float32 coordinate equality resolved the diagnostic: only duplicated UV/normal attribute vertices were collapsed for counting, with no change to the asset. Reimport topology, source preservation and final scene checks were then repeated.

The earlier offline comparison did not contain projected caustics. Actual assigned materials were audited; caustic-bearing material variants were unused. The evidence and reference page now state this explicitly. Runtime WebGL, motion appearance and device performance remain unverified.

Release integrity: observed Pages cache headers were max-age=600 on independently cached model resources. The runtime now selects one immutable versioned glTF package with all dependencies under the same directory; previous fixed URLs are preserved for cached clients. Deployment pruning reduces active binary data to 22,531,288 bytes without changing any live attribute/index byte or world transform. Final full-period routes, anchor rays, five-stop app wiring, reduced motion, low mode, explicit WebGL failure and structural water-light checks pass; no live browser GPU claim is added.

The first source push was rejected with `artifacts_git_receive_pack_object_too_large` because the archival 47 MB model retained old unreferenced geometry. No failed build was deployed. A deterministic compaction step reduced the distributed GLB to 28,962,072 bytes, SHA-256 `ce6a7bc4d005ecd794d378c792d5d05d79f4683b10a2d3446333e6053ead4d21`; loaded active geometry/index bytes and world transforms remain identical. The unpublished local commit was amended, and the immutable model directory was regenerated from this accepted-size source. Prior released baselines and the archival candidate hash are preserved.

## 2026-10-07 · Surface experiment and current review access

The existing cloud-browser tab was reloaded through the supported browser controls. It still reports that a WebGL2 context cannot be created. No blocked local browser launch, flag change or security workaround was retried. Real-time water, animation and device performance remain unverified.

Two original coral normal/roughness variants were compared on one thicket, with geometry, UVs, vertex colors, base color, cameras and lighting fixed. The actual assigned material was inspected, and target normal strength was held at the runtime-equivalent 0.36. Close, reverse, opening and normal-disabled controls showed no convincing visible gain. Both variants were rejected; neither is in the published model. This prevents a numerical-only or imperceptible change being presented as visual progress.

The new NOAA status-review reference describes tip-directed, bract-like radial corallites; the current planar UVs do not reproduce that orientation. Its 0.25–1.5 cm branch-diameter range also differs from the current NOAA species page's 1–3 inches. The reference page now exposes that disagreement and stops treating the model dimensions as calibrated. No arbitrary rescaling was applied.

### Accepted sand continuity test

The 32 m ripple grid's perimeter was 3.84–12.16 cm above the existing far floor. Fixed corridor views barely exposed it, so they were used as preservation checks. A reachable low orbit view, camera [-20.5,1.6,0] toward [-6.9,.3,0], visibly showed a dark cut across the foreground. Blending only the outer 2 m band removes that cut without a new trench or halo. All 460 boundary vertices now meet the far-floor height/normals exactly; 10,000 core sand vertices and all 59 other meshes retain their original data. Existing support perimeters remain buried. Owner and asset review both inspected the actual matched images.

The final candidate is 28,962,080 bytes, SHA-256 a5d9412ede847ba165f1198967b487dd3787e3f71e5e25ed30831f40a7ac5a0b. Guide anchor visibility, full fish routes, active-scene externalization, five-stop wiring, reduced motion and explicit WebGL failure checks pass. These checks do not claim a live browser-render pass. Publication is held while the coordinated GitHub/desktop baseline review establishes the exact version under test.

The beginner guide now describes larval settlement on hard surfaces, rather than implying every adult coral must be firmly attached. The current NOAA page and status review remain linked; the latter explicitly allows staghorn colonies that are not firmly attached.

### First real runtime evidence (baseline only)

GitHub Actions run 37561682524 created a WebGL2 context with Chromium 153 and ANGLE/Vulkan SwiftShader while retaining browser and GPU sandboxes. The public baseline model loaded, four fish changed positions across the eight-second sample, and recorded console/page/request errors were zero. Three opening screenshots were obtained; a later camera-settle timeout does not invalidate those captures. This establishes actual software-rendered browser/shader evidence, not user-device GPU performance. The source owner inspected the free opening screenshot: overly dark, hard-edged shadows, repetitive branch silhouettes, a simple water horizon and coarse fish remain visible limitations. Sand caustics are visible in the still; their natural motion is not established by that image. The sand candidate has not yet been tested by this route.

## 2026-10-07 · Spatial composition candidate following actual browser review

The first real browser image established that the current composition still reads as a small, dense foreground exhibit. The user explicitly rejected that scale and asked for an expansive, quiet, deep-blue experience. The sand-edge correction is retained inside this candidate rather than released as a standalone answer to that request.

The new composed route moves from the original reef edge through an open sand ribbon toward distant, irregular low limestone relief, then turns back toward the original coral. It preserves the original biological meshes and five teaching stops. The route is about forty scene units long, not a surveyed transect or certified dive route. NOAA's Florida Keys coral-reef description supports alternating reef relief and sediment channels; the exact geometry and placement remain original interpretation, not a Looe Key reconstruction. No additional species or new biome is claimed.

Runtime changes add a controllable forward/return passage, three spatial viewpoints and a larger free-camera target area. The last part rotates the view at a safe nonzero look distance instead of passing the target through the camera. Direct light is reduced and diffuse fill increased to address the black shadow blanket in the actual baseline; the shadow map follows the camera so distant terrain does not abruptly lose shadows. Slightly cooler water and lower artistic fog density are candidates for distant-layer readability, not calibrated underwater optics.

Acceptance gates: inspect actual WebGL departure, midway and look-back views; demonstrate continuous terrain and distinct near/mid/far silhouettes; retain a clear camera corridor without new floating joints; preserve biological geometry, complete fish routes, five-stop guide, pause/return and reduced-motion behavior. Source tests and offline images alone cannot accept the visual result. Whole-scene realism remains open until those images are reviewed.

A separate user-requested link presents the earlier private image-animation Site. It is labeled “图片动画展示（2.5D）” with a login/owner-only hint. It is not a scientific or modeling reference, and its audience and assets are unchanged.

### Actual candidate browser result and control fixes

Run 37563565356 captured departure, midway and look-back using the exact requested cameras in Chromium/SwiftShader. The source owner inspected all three. The route and larger terrain provide real spatial depth, but the middle is visually sparse and repeated rounded relief/branch forms still resemble a staged scene. This is accepted as an incremental spatial improvement, not completion of the overall experience. The full run failed at a later guide-camera assertion: the existing target-height clamp contradicted the seabed guide’s y=.02 target. Lowering the allowed target minimum to0 resolves that concrete conflict. Source regression now invokes the actual change handler and checks the intended target. Return-trip pause/resume also preserves travel direction. Both normal and reduced-motion source tests pass. A final bounded browser recheck remains pending before publication.

### Confirmed bounded release

Run 37564502286 passed the opening and corrected seabed-guide checks on source a19d100. Actual target.y was0.019999999999999997; both labels and the guide card were visible, and all recorded runtime/request error lists were empty. The owner reviewed the screenshot. This closes the known guide-coordinate defect, not the whole visual goal. The next evidence-based weakness is disconnected, mound-like hardbottom: two inspected NOAA aerial views show connected irregular reef masses separated by winding sediment channels. Future terrain work must improve that structural relationship before adding more colonies. No new geometry was introduced after this browser confirmation.

## 2026-10-07 · 连通硬底结构实验：拒绝集成

[完整实验记录](experiments/2026-10-07-connected-hardbottom-rejected/README.md)。固定已发布空间版与离线灯光，检验不规则连通母体、砂湾和错落立面；几何保留与路径检查通过，但视觉仍像裸露人工台地，因此拒绝上线。此次仅归档配方、证明及离线对照图，不更换生产模型或网页。提交前独立重跑配方得到候选 SHA256 `75a181a1fea752a05792a055cc2fad2a42c0d0516f42ed9ae64a3d8300f64265`；这不是实际浏览器或实时焦散验收。

## 2026-10-07 · 局部礁肩与材质输入：拒绝集成

[礁肩实验](experiments/2026-10-07-shoulder-sample-rejected/README.md)保留一次设计和一次修正的离线图与复现配方；仍有人工板层与平滑倒角感，视觉拒绝。独立重生成匹配候选SHA256 `1d0b54fb008b205a102a88c682636cad827114aeb2d0234f2752d57158b31b22`。

[材质输入审查](experiments/2026-10-07-substrate-input-rejected/README.md)：Coral Ground 02 实图含草叶与陆地碎屑，未应用于水下场景；仅归档出处和原文件哈希，不含114MB地图。生产网页与模型保持不变。另澄清当前软件WebGL验证范围、独立2.5D展示入口和公开重建输入提交。

## 2026-10-07 · Bounded water-depth and light transport increment

Source5596e8b introduced linear-radiance distance/depth attenuation and direct-light-only caustics. Actual run37573369857 caught a missing newline before a GLSL preprocessor directive; sourcef4334d2 fixed it and added a regression assertion. Run37573741470 then passed technically, but its effect was visually rejected: removing too much local light pattern made the seabed flatter. One correction96bcb513 restored local light variation, increased distant attenuation, and lifted ambient shadow readability.

Actual same-runner baseline/candidate run37574417037 passed all three equal cameras with identical fixed-time fish and zero reported runtime/request errors. Owner pixel review accepts the limited improvement to underwater distance layers, not the overall realism goal. Geometry, textures, fish routes, guide and exposure are unchanged. Numerical optical coefficients, assumed water height and scattering color remain illustrative rather than measured. NOAA absorption guidance and PBR transmittance principles are linked from the reference page. Test history and original screenshots are in evidence/water-oct7. Query-versioned app/water imports prevent stale fixed-name module caches. No new scientific species or co-occurrence claim.

## 2026-10-07 · Fish activity across the exploration route

Baseline source82f5c24 places all four fish in z=-4.55…3.75, leaving the middle of the expanded world inactive. Sourcee37dd1a retains two near the guide and places paired activity at middle/far reef areas using two shared-mesh companions. Differently paced, conservative geometry-sampled paths add cruising/lingering and speed-linked fins, with generic/unidentified labels retained. The GLB stays at four authored assemblies; runtime has six instances.

The animal/water phase clock now follows visible wall time separately from capped camera damping. Hidden/resumed and reduced-motion source checks pass without catch-up jumps. Actual run37577405341 passed all three fixed views and51.2862/51.3146 wall/scene seconds, but owner review found a middle pair clipped under the preset control strip. Source895d2b6 moved only that nearby path segment and recomputed conservative body/terrain/controls checks. Targeted run37578356621 passed the corrected midpoint and actual motion (56.1103/56.0977s), with changed positions/headings/fins and no reported runtime/request errors. Owner reviewed screenshots and chronological video frames. No claimed physical-GPU or complete native-input verification.

Accepted as a visible route-activity and timing improvement; coarse fish, repetitive coral and sparse terrain still prevent the whole visual target. See evidence/life-oct7 for actual baseline sources, retained flaw, corrections, sampling limits and references. The final import/fetch selectors version all mutually dependent fish resources together.

## 2026-10-07 · Inhabited reef structure across the route

Dense paired rows of identical branch forms obscured the route while broad smooth banks lacked legible reef structure. NPS/NOAA photographs informed unequal hard skeleton, negative spaces and fan attachment. Three original-asset compositions now present different orientations and partial burial; five near branch groups remain, including the guide target. Local triplanar color blending relates the new body to existing hardbottom while preserving sand, accepted water and all fish routes. Asset reuse and inferred generated material are explicit, not a scan or ecological certification.

Offline v1/v2 shapes and the browser v4 stretched skirt were rejected. Original v3 shape was retained; a bounded rigid-placement search and actual37588768850 local review passed. Full a62df54 static comparison37590596619 and targeted route37592002958 support only the visible structural increment. The locator timeout, software native-tour slowness and test-driven nature of13 full-route poses remain recorded. Independent review accepted static composition and sampled spatial continuity, not overall naturalness.

Same-runner37593200908 observed5 RAF in15.6155s baseline versus17.5007s candidate:10.8% lower candidate rate in this single pair. Neither is smooth, equivalent-performance evidence or a physical-GPU benchmark. The next optimization must address geometry/fine-net cost without adding more scenery or hiding this observation. Current repeated/rounded shape and bare forward end also keep the whole-world goal open. Evidence, limits and exact source reproduction are under evidence/inhabited-oct7 and modeling/inhabited.

## 2026-10-07 · Fan LOD rejected

[Experiment and actual evidence](experiments/2026-10-07-fan-lod-rejected/README.md). The distant3D fan retained close geometry and passed selection/hysteresis tests, but coarse cells and density jumps fail visual review. Two small software timing intervals showed5–7% higher RAF rate, not robust performance acceptance. Production assets remain unchanged; no threshold/density sweep follows this candidate.

## 2026-10-07 · Late-route rebalance

The existing near-right shoulder moves rigidly to the late right bank. Total geometry, textures, three structures/four fan meshes, water, six fish, route and teaching flow are preserved. Material influence follows its position. Actual run37602816684 compares four matched t0 views and six labeled test-driven late-route poses; owner and independent review accepted only this limited composition/space increment. Departure remains framed and late travel gains a landmark. Isolated-rock appearance, broad texture patches and empty banks remain. This does not accept full realism, native tour smoothness or physical GPU performance.

The preceding coarse fan LOD was rejected for visible polygonal cells and density changes despite small software-frame gains. Shadow/resolution cost separation is diagnostic only; neither low-resolution nor shadow-disabled settings were adopted. See ROUTE_REBALANCE.md and evidence/route-rebalance-oct7. The original packed modeling/inhabited/editable.blend and exact asset export are unchanged.

Source6750ba68 / measured candidate73f334e / run37602816684. Original four-view comparisons and labelled six-pose recordings are preserved on QA branch qa/route-rebalance. This changes placement, not total assets or performance acceptance.

## 2026-10-07 · Late-bank grey deformation rejected

[Offline grey experiment](experiments/2026-10-07-late-bank-grey-rejected/REPORT.md):305 terrain positions and458 normals changed with no added triangles. Gullies are real, but the rounded cap and isolated-mass character remain; the actual75% camera changes almost imperceptibly. Rejected before WebGL, without modifying production. Independent portable replay reproduced SHA256941e9fa1ca42b2918ff818a2f9f46aff1f948860d52d0dc836f1625b68947ed1. Recipe/proof/images are retained; the29MB generated GLB and original reference photograph are excluded.

## 2026-10-07 · Visible folded ledge rejected

[Rejected structure record](experiments/2026-10-07-visible-ledge-rejected/README.md). Offline75%/92%/reverse views show a broad cap/ribbon and loss of the old reef layering. Independent diagnostics find12 improper intersections and35 new rear contacts; cavity gap shrinks from.95 to.1555, so preservation is explicitly not claimed. A prior935-ray visibility diagnostic explains why the earlier bank edit barely affected the view, not why this candidate should pass. Portable recipe replay exactly matches9e0cb3f4… . No new geometry deployment, WebGL run, or parameter repair.

## 2026-10-07 · Bounded source-asset research

[Two source-chain findings](docs/asset-research-20261007/SOURCE_ASSET_CHECKS.md): the inspected Bremen archive exposes orthomosaic TIFFs rather than3D geometry; the NAUTILUS portal and18 relevant linked-map entries did not establish a reusable current-Caribbean mesh. The portal was readable; temporary cancelled/502 reads are not generalized access prohibitions. These findings close only those leads, not all asset sources or all design approaches. No downloaded scene asset, production change, or new rendering follows this record. The folded-ledge archive also includes its final22-item source whitelist.

## 2026-10-07 · Low observation route rejected

[Static study and rejected continuous-path record](experiments/2026-10-07-low-camera-path-rejected/README.md). Four real images support a limited midway benefit; the late view is neutral to slightly improved. The initial descent failed branch clearance (.2841); one constraint repair reached 1.020598 static clearance but fish_06 posed triangles approach the camera to .1605277, below the unchanged .45 observation buffer. This is not proof of center penetration or inevitable clipping: the closest case is outside the frustum, with neighboring visible cases. The phase-independent buffer check remains failed. No fish tuning, height sweep, new route CI, or deployment followed.


## 2026-10-07 · Single illustrative fish surface repair


Accepted as a bounded visual repair, not biological or whole-scene realism acceptance.

Frozen runtime candidate: 3c853a6ba5f3d3ab6740f669a808de36945e4943. Actual software WebGL run: https://github.com/yydshly/azure-reef-3d/actions/runs/37616743352 . Original six images/reports: https://github.com/yydshly/azure-reef-3d/tree/qa/fish-surface/evidence/fish-surface-ci-37616743352 (archived at f705f067b1620ab650ce7473a810f7cc0f3eb1b0).

Both arms passed, zero GL/console/page/HTTP errors. Actual camera, target, FOV and six fish transforms/t0 matched. Only fish_03 body/five fins refined; fish_05 and all other fish preserved. Closeups use 20-degree diagnostic FOV; normal midpoint uses the production 47-degree FOV.

Owner and independent pixel reviews inspected all six frames. Accepted: removal of stair-stepped pigment discontinuities on both flanks, lighter fin appearance, no normal-distance readability loss or new visible seam/outline tear. Limit: very straight regularly spaced hard pigment edges, old eyes and illustrative body remain; no species/photoreal or ecological claim. Static evidence does not establish motion or device performance. Source-level full-cycle geometry/motion, containment and guide checks cover the unchanged interfaces but are not actual-device motion evidence.

One fish only. +980 fin triangles; body attribute/index bytes unchanged. Closed fins remain contained in original geometry under the existing affine fin motion. No new textures; original procedural shaders only. Reference images were privately viewed and not redistributed. See reference-audit.json.

Release-only changes after captured candidate: app/module query versioning, evidence/source page and documentation. Runtime algorithm and geometry remain the captured bytes apart from the module import query. No new camera path or other-fish refinement adopted.
