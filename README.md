# 浅蓝 · 立体珊瑚礁 / Azure Reef 3D

## 项目简介与在线体验

一个可自由旋转、缩放的真实三维浅海珊瑚礁场景，包含五站中文初学者导览、四条泛化鱼类的三维运动路线，以及新增的中远景起伏与珊瑚层次。支持手动推进、自动讲解、暂停与自由探索。

在线体验：[GitHub Pages · 浅蓝三维珊瑚礁](https://yydshly.github.io/azure-reef-3d/)（公开网页）。本仓库及完整建模源码现已按项目所有者授权公开。`main` 上的 `dist/` 或部署工作流变更会通过 GitHub Actions 更新 Pages；工作流仅发布 `dist/`，不把 Blender 工程或开发依赖作为网页发布。

[原来的独立 Site](https://azure-reef-3d.yydshly.chatgpt.site) 保留原有私有访问设置，它与 GitHub Pages 分别部署。

快速运行：在仓库根目录执行 `python3 -m http.server 8000 --directory dist`，然后打开 http://localhost:8000 。运行网页无需安装 npm、登录或填写 API 密钥。模型、纹理与 Three.js 已随项目提供。

这是参考资料引导的程序化场景，不是实测珊瑚礁扫描，也不构成科学验证。鱼类为未识别的泛化模型。NOAA 来源与制作边界见界面来源页、下文及 THIRD_PARTY_NOTICES.md。离线模型和逻辑验证已完成；真实浏览器 WebGL、CSS 与真实设备输入未宣称完成验证。

A static, genuine-3D reef scene with a five-stop Chinese beginner guide. The guide connects camera positions and visible labels to explanations of reef context, sand/hardbottom, coral animals, generic fish, and light/water. Sources and modeling limits are available in the interface.

This export includes source commit `adcab74aed75f8186f73b94b5f55eaa9a19171e3`. Every file under `dist/` is byte-identical to that scene snapshot; see `docs/source-baseline-sha256.json` and `docs/export-changes.json`.

## Run the exact snapshot

No build step, API key, backend, account or npm installation is required to run it.

```sh
python3 -m http.server 8000 --directory dist
```

Open http://localhost:8000 in a browser with WebGL2. Do not open index.html directly through `file://`: module loading and model requests need HTTP. Any static host can serve `dist/`; keep its directory structure and all `.gltf`, `.bin`, texture and module files. The host must permit the 22.68 MB `reef.bin` file.

The browser uses its locally bundled Three.js; it does not load a CDN dependency. Existing links to the earlier private 2.5D Site are optional reference links and may not be accessible to another account. The guide itself is self-contained apart from optional public NOAA source links.

## Controls

The guide starts in manual-next mode. Use previous/next, optional automatic advance, pause, source details, and free exploration/resume. Drag to orbit; wheel/pinch zooms. Right-drag/two-finger drag pans. Arrow keys orbit, +/− zoom. Power-saving mode reduces rendering cost. Reduced-motion preference suppresses ambient animation and makes guide camera jumps immediate.

## What is included

- `dist/`: complete browser app, five-stop guide, evidence/source page, model and assets
- `source-model.glb`: authoritative final model, retained before its lossless static-host conversion
- `modeling/editable/reef-garden-final.blend`: final editable Blender scene, with all six image maps packed
- `modeling/inputs/seed-reef.blend`: the exact earlier seed needed by the reference-led generator
- `modeling/inputs/textures/`: six original normal/roughness maps
- `rebuild_reference_reef.py`, `blend_boundary.py`, `build_depth.py`: reference → edge → depth pipeline
- `generate_textures.py`: optional deterministic texture generation
- `export-static-model.py`: lossless GLB → external glTF/binary/PNG conversion
- `build-routes.mjs`: geometry-aware fish-route generation
- `qa-*.mjs`: checks; see limitations below
- `docs/`: baseline hashes, export changes, packed-image validation and historical build notes

## Optional JavaScript checks

Use Node 22+ (validated here with Node 24), then:

```sh
npm ci --ignore-scripts
npm test
npm run test:motion
```

Pinned development dependencies are Three.js 0.186.1 and `@napi-rs/canvas` 0.1.100. The latter uses platform-specific optional native packages, so installation/availability depends on the OS and CPU. It is used only for Node-side embedded-image decoding, not by the website. `qa-occlusion.mjs` is an earlier ellipse-path diagnostic retained as history; it is not part of the current aggregate tests. Current spline checks are in `qa-motion.mjs`.

These tests cover model parsing/material references, guide-state logic, simulated DOM/renderer integration and sampled geometric clearance. They do **not** prove live WebGL shader execution, browser layout, device input or continuously collision-free fish behavior.

## Edit the final model

Open `modeling/editable/reef-garden-final.blend` in Blender 4.3.2. The image maps are packed, so the scene does not depend on the original machine’s filesystem. Source dimensions use meters; Blender Z-up is converted to glTF Y-up. Camera/light presentation in Blender differs from browser rendering.

If exporting a changed model, preserve mesh names and `fish_01`…`fish_04` parent names used by app animation. Export meshes and fish parent empties as glTF binary, including vertex colors, UVs, normals and materials; do not export offline cameras/lights. Replace `source-model.glb`, then run `python3 export-static-model.py` and `npm run build:routes`. Recheck guide focus points after geometry changes.

## Historical reference → edge → depth pipeline

Run all commands from the repository root. Texture regeneration requires Python 3.11 or newer. Install Blender 4.3.2 from its official distribution. The six original maps are supplied; regeneration is optional.

```sh
# Optional: regenerate the supplied surface maps
python3 -m venv .venv
# Activate the environment for your shell, then:
python3 -m pip install -r requirements-modeling.txt
python3 generate_textures.py

# Generate into artifacts/, preserving the shipped snapshot
blender -b --factory-startup --python rebuild_reference_reef.py
blender -b --factory-startup --python blend_boundary.py
blender -b --factory-startup --python build_depth.py
```

This produces the reference stage, the corrected edge stage, and finally `artifacts/depth/reef-garden-spatial-depth.glb`. Inspect that candidate before replacing shipped files. To promote it deliberately:

```sh
python3 -c "import shutil; shutil.copy2('artifacts/depth/reef-garden-spatial-depth.glb','source-model.glb')"
python3 export-static-model.py
npm run build:routes
npm test
npm run test:motion
```

`build_reef.py` and `extend_sand.py` reconstruct an older exploratory model under `artifacts/legacy-base/`; they are provenance, **not** the approved current rebuild route. The supplied seed blend is the authoritative input for the current generator because the historical chain included separately verified normal/material corrections.

## Offline camera evidence (legacy views)

```sh
blender -b --factory-startup --python render_evidence.py
```

The script reimports `source-model.glb` and supplied `modeling/inputs/previous-edge.glb` into the final blend’s offline setup and writes matched before/after front/reverse images under `artifacts/comparison/`, using identical distance fog. The earlier simple render_reimport_evidence.py route remains available. It never substitutes a render for the interactive 3D scene. These are offline rendered-model checks, not browser screenshots.

## Reproducibility and accuracy limits

The shipped static app and model are the exact deployable snapshot. Rebuild scripts use fixed seeds and supplied inputs, but bit-identical Blender/glTF output is not promised across versions, export options, floating-point implementations, texture-library versions or OSes. The portable scripts were path-adjusted and checked; a complete from-seed geometry regeneration is not claimed as rerun for this export unless recorded in validation notes. Compare geometry, materials and rendered output after rebuilding.

The scene is a reference-guided Florida/Caribbean staghorn patch-edge interpretation, not a scan of a named reef or a scientifically validated ecosystem. Coral color/growth-form direction is source-grounded, but repeated procedural branching and stylized terrain/water remain. Generic fish are explicitly unidentified. Lighting, visibility, route timing and microscopic textures are artistic/educational approximations. The app source page provides the supported/deviating/unknown audit.

Live browser/WebGL behavior and CSS were not fully verified in the original restricted environment. Guide cameras were checked with actual same-model offline renders; state and interaction wiring were checked in simulation. No blocked browser route was bypassed.

## Sources and licensing

See `THIRD_PARTY_NOTICES.md`. NOAA photographs were inspected for reference and linked, not bundled as scene imagery. The geometry and procedural textures are original project assets. No project-wide open-source license is imposed by this export; the owner can choose one separately.

## Spatial-depth revision

Nine closed low hardbottom rises and twelve linked instances of existing staghorn geometry extend the middle/distance. Core geometry, transforms, fish, maps and guide remain intact. The older generated 2.5D image informed composition only; unseen structure is inferred, not automatically reconstructed or field-measured. The final editable blend packs six maps. The previous edge GLB is supplied for comparison only. The a9dfa703 export remains separate and unchanged.

## Guide anchor correction / 导览标记修正

海床站改为两个经过当前模型射线验证的独立标记：砂底、坚硬礁面。修复圆点中心与投影点的对齐，并检查手机视口的导览卡片避让；模型几何不变。`npm test` 现在包含真实模型表面与标记检查。模拟测试和几何投影检查不等同于真实浏览器截图验证。

Source revision: `515811ecbb536d5e78a5aa4010d9ef789672cfb7`.

## Current exact model reproduction

Use the deterministic three-stage chain in `modeling/immersive/README.md` for the current immersive model. The historical pipeline above produces the earlier depth revision. The final editable Blender file contains packed geometry/materials; runtime water lighting remains in JavaScript. `modeling/inputs/offline-lighting.blend` preserves the older offline camera/light rig for historical render scripts. Those legacy views do not reproduce the new evidence camera/lighting exactly.

## Immersive view and water-light pass

The opening camera is now inside the reef rather than looking down at a miniature. Ten existing thickets move aside around an uneven sand opening, and eight shared-mesh instances continue the existing form into the middle/distance. Exact source-accessor checks preserve all other core geometry, fish, materials and image maps. The sand/hardbottom guide anchors retain first-hit visibility. Layout and concealed geometry are artistic inference, not a survey or ecological density measurement.

A new original wave-slope caustic texture and restrained runtime light modulation replace the earlier banded analytical effect. The surrounding water field varies with viewing direction; there is no background picture replacing terrain. Runtime shader insertion is structurally tested, but no actual browser GPU compile/render is claimed. The offline before/after images use matching cameras and lighting; their light renderer and static fish poses differ from live runtime.

Fish routes were rebuilt with denser body-footprint sampling after the moved thickets exposed a clearance issue. QA now samples full route periods and four camera positions, including a low lateral orbit view. These checks demonstrate sampled clearance/occlusion, not continuous collision safety or validated biological behavior.

The first-version visual target is still open: the corridor and layered depth are clearer, but regular branch morphology, simple distant transitions, and unverified realtime water appearance prevent claiming photorealistic or completed immersion. See ITERATION_LOG.md for rationale and evidence/immersive for numerical proof.
