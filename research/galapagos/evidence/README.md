# Galápagos research viewer: actual browser evidence

This is an isolated research branch, not the deployed Caribbean reef or acceptance of a complete natural reef. The attributed CC BY 4.0 sample retains known holes, nonmanifold edges and orientation defects. No NC dataset is included.

- Initial commit e25f5ddd, run37571588719: four actual Chromium153/SwiftShader WebGL images; native point/surface mode buttons, identical front camera, reverse view and drag worked. Run failed because favicon.ico returned404. The initial failure is preserved.
- Correction commit7ab3025, run37571822547: explicit empty favicon, unchanged model/app logic. Retest succeeded; zero console/page/request/HTTP errors, GLerror0, no lost context, native drag changed camera.
- Both runs use Chromium sandbox without unsafe GPU switches. Software rendering is not user-device GPU/frame-rate validation. Screenshots are actual loopback-hosted research viewer frames, not production Pages.
- Human review accepted the research UI and visible form only. Production main/dist was not modified, no Site was created, and no hole-filling or final-scene acceptance is implied.
