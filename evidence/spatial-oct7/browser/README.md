# Actual browser candidate evidence

Run 37563565356 tested candidate source 000ea52 from an isolated loopback HTTP preview in a GitHub runner. Chromium 153 used ANGLE/Vulkan SwiftShader with browser and GPU sandboxes retained. These are actual WebGL screenshots, not Blender renders and not user-device GPU performance measurements. Fixed camera poses were set through the existing app API; this does not certify native input or the complete animated passage.

All three core positions exactly matched their requested coordinates. Model loading, shader rendering and an eight-second fish-position sample succeeded; recorded page, console and request errors were zero. The overall run failed at the later seabed-guide position assertion: the application clamped target.y=.02 up to .3. The failed report is retained unchanged. The source fix lowers the permitted target minimum to0 while keeping camera height above the floor. A strengthened source test now invokes the actual change handler and detects the previous failure. A separate return-trip pause/resume direction bug was also fixed.

Visual review accepts a bounded spatial improvement only: the sand passage is explorable and the original reef recedes across a larger scene. Sparse mound-like relief, repetitive branch forms, strong repetitive caustics and limited biological richness remain visible. The intended natural, expansive underwater world is not complete.

## Confirmed correction

Targeted run 37564502286 tested a19d100 and passed. It captured the opening and seabed guide, with target.y=0.019999999999999997, both ground markers visible, and zero console/page/request/HTTP errors. The owner inspected the actual guide screenshot. This bounded run intentionally skipped a new animation sample; the preceding run already supplies that evidence. The screenshots and full report are preserved in confirmation/. It does not certify native input, smooth travel on a physical GPU, or complete visual realism.
