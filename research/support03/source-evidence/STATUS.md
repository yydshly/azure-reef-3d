# One support, runtime comparison pending

Baseline Site2372e912/publica95871f. Replace only Distant_Limestone_Support_03 geometry with the unchanged single QEM sample:48050→14760triangles. Reuse original object/material/maps/water shader/transform; other7supports and near hardbottom stay original. Adds432556-byte geometry asset while original shared mesh remains resident, so this is not a download/memory reduction and not a demonstratedFPSgain.

Initial conservative source screen failed with positionmax0.017351/P990.0078 uncalibrated scene units, plus normal/color/UV differences. Not user-mandated perceptual limits. Original terrain is illustrative, notsurveyed. Owner and independent reviewer saw no material visible degradation in4fixedoffline pairs; runtime visual pass still required. Sand-contact crossing3832faces remain exact; sourceworstpoint occluded bybranch atbothcameras, largestunoccludederror0.014519. Keep all these losses documented ratherthanclaimlossless.

Local actualGLTF decode test proves exactlyonegeometryswap; material/transform/all other objects unchanged. Existing simulatedguide normal wiring passed. NoWebGLimages or nativeperformance claimed yet.

ActualQA: normalmidpoint camera[0,2.7,-18]target[-1.5,1,-31]; close diagnostic camera[4.7,1.25,-21.7]target[1.8,0,-25.45],FOV47. The offlineclose targetwasY−.2; runtimeusesY0 torespectexistingtargetconstraint, identicalbetweenarms. Reducedmotion/t0forboth. Check contact/texture/shading andactualdraw/tri counts. Do notchangeconstraintsorcallclosecameraa productpreset. No production change.
