# Azure Reef 3D · 海底项目统一入口

**统一网页入口：[打开海底项目版本展示](https://yydshly.github.io/azure-reef-3d/)** · [本次网页交付与验证](SHOWCASE_DELIVERY.md)

[历史场景恢复与发布清单](HISTORY_RELEASE.md)。连续首候选、构图修正版、海盆首版/修正版和LOD4/LOD3对照恢复为独立实验入口；原效果和历史视觉结论保留。

各版本有独立真实预览图、完成状态和交互入口；可在网页内返回或切换。页面首次打开只加载图片，进入后只运行一个场景。原站移至 [保留入口](https://yydshly.github.io/azure-reef-3d/legacy.html)，原资源及历史预览继续保留。

**当前主展示：海庭01.2，已发布但整体视觉未达标。** 用户已否定01.2整体质量，盆地证明段也失败；没有最终合格效果或项目目标完成结论。

[![已发布海庭01.2真实截图；点击打开统一展示网页](https://raw.githubusercontent.com/yydshly/azure-reef-3d/3c00efbec735c7618c842edf3f5a0716e1147323/evidence/reef-garden-stage/live-entry.png)](https://yydshly.github.io/azure-reef-3d/)

[查看当前主展示 / 实时72秒导览](https://yydshly.github.io/azure-reef-3d/preview/reef-garden-stage-012/) · [完整实录：下载后播放](https://raw.githubusercontent.com/yydshly/azure-reef-3d/3c00efbec735c7618c842edf3f5a0716e1147323/evidence/reef-garden-stage/complete-demo.webm) · [阶段总结](REEF_GARDEN_STAGE.md)

图片为真实静态截图。进入主展示页面后点击“开始72秒导览”实时观看；原实录约126.56秒，含72秒自然导览与操作核验，链接用于下载播放，未宣称README内嵌自动播放。

## 版本差异与采用状态

| 版本/路线 | 做成什么与差异 | 未做成；采用/停止 | 体验 | 源码与证据 |
| --- | --- | --- | --- | --- |
| 早期原站 | 原始三维模型、五站教学及局部运动/支撑修正 | 仅历史参考，不是当前主展示 | [原站](https://yydshly.github.io/azure-reef-3d/legacy.html) | [main原源码](dist/)；[源模型](source-model.glb) |
| 原enriched | 三区探索、72秒六站、自由移动/碰撞/暂停重播 | 真实感、丰富度和连续性不足；保留旧基线 | [旧world](https://yydshly.github.io/azure-reef-3d/preview/world/) | [基线a1b2cae](https://github.com/yydshly/azure-reef-3d/commit/a1b2cae7e968ad383798a0ff15c87bfb0934d971)；[main增量归档](archive/enriched/)；[完整源位置](SOURCE_INDEX.md) |
| 材质候选 | 局部法线/粗糙度略有收益 | 整体目标未达，未提升为主展示；本轮未重新做视觉验收 | [历史发布入口](https://yydshly.github.io/azure-reef-3d/preview/surface-grounding-candidate/scan-exhibit.html) | [原发布ef6a761](https://github.com/yydshly/azure-reef-3d/commit/ef6a7618ef02bdcf8134aa3f395be5e9d90e2f6f)；[发布回执](https://github.com/yydshly/azure-reef-3d/actions/runs/38147691994)；完整源链未在本轮迁入 |
| LOD4局部扫描 | 局部扫描探针 | 覆盖/完整性不足；不作完整海域，完整源链未确认 | [扫描探针](https://yydshly.github.io/azure-reef-3d/preview/real-splats-probe/) | [局限与未闭环项](REEF_GARDEN_STAGE.md) |
| LOD3/Gaussian | 诊断实现与记录 | 未闭环、未发布；停止，不作基线 | 无产品入口 | [历史诊断dd6b671](https://github.com/yydshly/azure-reef-3d/commit/dd6b671461aa1a9ff2fb2287137ae7bbdea0da50) |
| 海庭首版 | 第一份独立风格化演示 | 历史已发布；由01.2替代主展示，整体质量未达 | [固定首版](https://yydshly.github.io/azure-reef-3d/preview/reef-garden-v1-first/) | [main源码](dist/preview/reef-garden-v1-first/) |
| 海庭01.1 | 调整视野层次、衔接此前探索入口 | 历史已发布；整体视觉未完成 | [固定01.1](https://yydshly.github.io/azure-reef-3d/preview/reef-garden-v11/) | [main源码](dist/preview/reef-garden-v11/)；[348ead4证据](https://github.com/yydshly/azure-reef-3d/commit/348ead4995f21d5a595640165c3b10cc14b63219) |
| **海庭01.2** | 六地段、72秒导览及操作技术原型 | **当前主展示；用户否定整体质量，不是待验收** | [固定01.2](https://yydshly.github.io/azure-reef-3d/preview/reef-garden-stage-012/) | [main实际源码](dist/preview/reef-garden-stage-012/)；[固定标签](https://github.com/yydshly/azure-reef-3d/tree/reef-garden-01.2-stage)；[全部证据](https://github.com/yydshly/azure-reef-3d/tree/3c00efbec735c7618c842edf3f5a0716e1147323/evidence/reef-garden-stage) |
| 连续谷地/构图 | 连续布局尝试、消除局部水面/床面断层 | 空走廊、空回望仍在；视觉失败、未发布、停止 | 无新线上入口 | [main连续归档](archive/continuous-candidate/) / [main构图归档](archive/composition-candidate/)；[失败记录](https://github.com/yydshly/azure-reef-3d/blob/0478d7ab42eae11e65fc53f83b5253e9dcda9822/evidence/composition-20261012/VISUAL-VERDICT.json) |
| 盆地证明段 | 42.36秒实录，前进/回望/横移/环视/返回，经过一次纠正 | 台座感、空方向、持续层次三项失败；未发布、停止 | [失败实录](https://github.com/yydshly/azure-reef-3d/blob/bef0b8506b5e1b6726585722573014038bdc570a/evidence/basin-proof/final/uncut-proof.webm) | [main源码归档](archive/basin-proof/)；[原判定](https://github.com/yydshly/azure-reef-3d/tree/bef0b8506b5e1b6726585722573014038bdc570a/evidence/basin-proof)；[源码目录](https://github.com/yydshly/azure-reef-3d/tree/bef0b8506b5e1b6726585722573014038bdc570a/dist/preview/reef-basin-proof) |

## 源码是否都在main

**当前海庭运行源码在main；已确认候选的必要源文件也已放入main的独立archive目录。** 海庭四个目录及共用模块是实际源码，enriched增量、连续/构图、盆地原源码分别归档，失败代码未接入主展示。完整149基线、大资产/大源包和部分未确认源链没有全部搬入main；线上旧站还依赖发布时恢复的完整快照。

[main源码归档](archive/) · [源码、源包实际位置](SOURCE_INDEX.md) · [机器可读版本索引](STAGE_INDEX.json) · [树与源码核对记录](evidence/stage-summary/source-locations.json)

本次把总结、必要记录和已确认候选源文件统一保存到main，没有把失败代码接入主展示，也没有重复复制大源包、全站资产、原始录像或全部截图。原分支、标签、旧入口及原始证据保留。

## 阶段结论与阅读顺序

1. 看当前展示：使用上方01.2入口；其他体验均为已标明的历史参考。
2. 看做成/未做成：阅读版本表及[权威阶段总结](REEF_GARDEN_STAGE.md)。技术通过、部署成功与视觉失败分别记录。
3. 查代码/源包：[源码位置索引](SOURCE_INDEX.md)明确main实际文件、独立分支、只在本地/外部的大包与未确认项。

本项目仍缺自然连续空间、持续近中远景、可信群落及光水/动作整体质量。免费/现有资源筛选未证实足够突破，付费仅调研未购买；TIDAL核查未完成独立75秒连续验证，不混算成果。后续须有新许可明确、实际质量证明与合理性能依据，停止同路线无效循环；此次没有额外研发或Pages部署。

[统一前的README原文](https://github.com/yydshly/azure-reef-3d/blob/cc416bfc623db3b6d6171c9550c1386930ba0735/README.md)作为历史保留；[原阶段总结提交](https://github.com/yydshly/azure-reef-3d/commit/7c59a653e2f353df3b024458feadfbbda1ee383e)也保留。当前结论以本main入口与阶段总结为准。
