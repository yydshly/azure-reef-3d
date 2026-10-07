# Native reef tour clock — limited acceptance

Accepted as a timing correctness repair, not an FPS, smoothness or reef-realism improvement. Tested runtime candidate28c0859f269cb294d620ba6fced54f879d521672; actual safe Chromium / SwiftShader run https://github.com/yydshly/azure-reef-3d/actions/runs/37645150947 .

Same runner native-button observations: baseline18.5081s,5RAF, progress .0006 to .0036; candidate17.7594s,5RAF, progress0 to .176659. Candidate rendered simulation time increased17.6659s, matching17.6659% of the100-second path. Neither arm had GL/console/page/request/HTTP errors. Initial images and final paused images were personally inspected. Candidate uses the original route and reaches an expected later position without a rendering failure.

Native pause takes additional wall time in this software renderer. The candidate final screenshot is at .212824 after pause, not the earlier measurement endpoint .176659. Both states are retained. No full100-second native tour, hidden-tab native behavior, or device performance is claimed. Source tests separately cover full forward/reverse,60/15/1/.3Hz, exact manual pause/resume, hidden return,20-second foreground interruption, reset and guide behavior. Actual OrbitControls source moves the integrated camera by less than1.1e-14 under its original constraints.

At .3Hz the full-route source check has up to about1.95 scene units between shown frames. Correct wall-time progression cannot create missing frames; extremely slow rendering remains jerky. A gap exceeding8s explicitly pauses native travel rather than catching up; restart clears elapsed debt. The original five-stop guide timing remains unchanged. Fish/water, geometry, textures, camera path and quality settings remain unchanged.

Release changes after captured runtime are import/app cache-query versioning and documentation only. The implementation remains the tested algorithm. This stage does not close the larger believable-underwater-world goal; separate structural studies remain under visual review.
