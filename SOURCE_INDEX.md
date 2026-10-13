# 源码、源包与主线位置

统一首页实际源码在 [dist/index.html](dist/index.html) 和 [dist/showcase/](dist/showcase/)，原站HTML保存在 [dist/legacy.html](dist/legacy.html)。[网页交付与保全验证](SHOWCASE_DELIVERY.md)。原有场景和归档源码不因本次首页变更而合并。

**海庭首版、01.1、01.2的实际运行源码已经在main；已确认候选必要源文件也已归档main，但所有实验的完整源链与大源包没有全部合入。** 本次把权威总结、版本表、轻量记录和必要源文件统一到main，未将失败代码接入产品。核查基线为 `cc416bfc623db3b6d6171c9550c1386930ba0735`；当前入口以[根README](README.md)为准。

## main中确实存在什么

| 内容 | 实际路径 | 说明 |
| --- | --- | --- |
| 当前主展示01.2 | [固定源码](dist/preview/reef-garden-stage-012/)；[稳定入口源码](dist/preview/reef-garden-v1/) | 每处有app.js、index.html、navigation.js、style.css、world.js；是实际完整海庭运行源码，不只是工作流引用。几何与表现由world.js及共用Three.js模块构建。 |
| 海庭01.1/首版 | [01.1](dist/preview/reef-garden-v11/)；[首版](dist/preview/reef-garden-v1-first/) | 固定历史运行源码均在main；四目录共20个文件与固定证据来源`3c00efbec735c7618c842edf3f5a0716e1147323`逐一同blob。 |
| 共用浏览器模块 | [vendor](dist/vendor/)；[utils](dist/utils/) | 海庭运行所需共用模块在main。 |
| 早期原站 | [dist](dist/)；[source-model.glb](source-model.glb)；[原建模工程](modeling/editable/reef-garden-final.blend) | 这些原始模型/Blender文件属于早期原站，不是后来新海庭01.2的离线整景。 |
| 当前统一文档 | [阶段总结](REEF_GARDEN_STAGE.md)、[版本索引](STAGE_INDEX.json)、[核查记录](evidence/stage-summary/) | 从原总结`7c59a653e2f353df3b024458feadfbbda1ee383e`汇入文档及必要轻量记录。原提交/分支仍保留，未整体合并其代码。 |

[发布工作流](.github/workflows/pages.yml)确实检出main里的海庭源码；[恢复脚本](restore-published-preview.py)再恢复既有公开站点快照并叠加这些文件。因此，**main的dist不是整个线上站点所有资产的完整镜像**。enriched、扫描和其他历史网页可以在线保留，但不能由“Pages已上线”推断它们的所有源码/资产都在当前main。

## enriched完整源实际在哪里

- 发布基线为[提交a1b2cae](https://github.com/yydshly/azure-reef-3d/commit/a1b2cae7e968ad383798a0ff15c87bfb0934d971)。当前main没有enriched运行目录，也没有`dist/preview/world/`的源码镜像。
- [Git归档提交](https://github.com/yydshly/azure-reef-3d/tree/acd6b3f9f287b8fa5b8e07e4ffddf3491668c92b)中的[exploration-enriched-code.zip](https://github.com/yydshly/azure-reef-3d/blob/acd6b3f9f287b8fa5b8e07e4ffddf3491668c92b/exploration-enriched-code.zip)只有6个增量模块，现已按原字节存入[main增量归档](archive/enriched/)；[build-tools.zip](https://github.com/yydshly/azure-reef-3d/blob/acd6b3f9f287b8fa5b8e07e4ffddf3491668c92b/exploration-enriched-build-tools.zip)是组装/验证工具。不能把这两个小包称作完整149源和资产包。
- `exploration-demo-snapshot-b8c55275.zip`是9份浏览器证据文件的快照，不是完整源码包。完整149文件依赖多个既有归档及固定发布字节恢复；既有恢复已按固定哈希核对，完整运行目录保存在工作环境，没有复制进main。
- 已知完整enriched外部源包记录为190221239字节，SHA256 `8d218b937a33cdb2f6c6463e0dd05ff00d7266df108b86f24a3ca0ab6b6cceb0`。它不在main；本轮不重新物化/验包，不把外部临时路径当作本地存在。部分完整生成包和早期阶段索引仍仅在本地或外部归档。

## main源码归档与原分支/证据位置

| 内容 | 可追溯位置 | main状态 |
| --- | --- | --- |
| 连续候选 | [candidate/continuous-reef-20261012](https://github.com/yydshly/azure-reef-3d/tree/candidate/continuous-reef-20261012)里的[两份candidate-src模块](https://github.com/yydshly/azure-reef-3d/tree/0478d7ab42eae11e65fc53f83b5253e9dcda9822/candidate-src)，以及生成脚本和证据 | 必要源码已保存在[main归档](archive/continuous-candidate/)，未接入产品目录。 |
| 构图修正 | [0478d7a](https://github.com/yydshly/azure-reef-3d/commit/0478d7ab42eae11e65fc53f83b5253e9dcda9822)；[6文件增量包](https://github.com/yydshly/azure-reef-3d/blob/0478d7ab42eae11e65fc53f83b5253e9dcda9822/evidence/composition-20261012/composition-preview-delta.zip)；同分支的生成/组装脚本 | 必要源码已保存在[main归档](archive/composition-candidate/)，视觉失败且未发布；完整生成目录未放main。 |
| 盆地证明 | [bef0b85完整运行源码](https://github.com/yydshly/azure-reef-3d/tree/bef0b8506b5e1b6726585722573014038bdc570a/dist/preview/reef-basin-proof)；[证据](https://github.com/yydshly/azure-reef-3d/tree/bef0b8506b5e1b6726585722573014038bdc570a/evidence/basin-proof)，保留在candidate/reef-basin-proof | 5份源码已保存在[main归档](archive/basin-proof/)，三项失败；未接入主展示或发布。 |
| 01.2证据/标签 | [3c00efb证据](https://github.com/yydshly/azure-reef-3d/tree/3c00efbec735c7618c842edf3f5a0716e1147323/evidence/reef-garden-stage)；[标签](https://github.com/yydshly/azure-reef-3d/tree/reef-garden-01.2-stage)，原candidate/stylized-reef-v1保留 | 运行文件已复制入main；该证据提交本身未整体合并。大录像/全部图片仍用持久原证据链接，不重复复制。 |
| 原阶段总结 | [7c59a653](https://github.com/yydshly/azure-reef-3d/commit/7c59a653e2f353df3b024458feadfbbda1ee383e)及原candidate/reef-basin-proof保留 | 此次总结和必要记录内容已汇入main；失败代码没有随文档合并。 |
| 材质/LOD4/LOD3 | [阶段总结](REEF_GARDEN_STAGE.md)中的既有记录与链接 | 材质独立源链、LOD4完整源链本次未闭环确认；LOD3只有历史诊断，不列作main产品。 |

仅看提交祖先关系不能判断文件是否已经复制入main。上述6个历史/候选提交不是核查时main的祖先，但海庭20个运行文件确实同字节存在main；本次依据[树与blob核查记录](evidence/stage-summary/source-locations.json)分别说明文件与提交历史。

原分支、标签、旧入口和原始证据不删除。TIDAL是独立项目，记录不混算为本项目新效果；本轮不重新研究素材、不购买、不修改产品或触发Pages。

## 新增源码归档的精确范围

[archive总目录](archive/)保存原enriched 6增量模块、连续候选2作者模块与生成脚本、构图6实际源与组装脚本、盆地5份运行源码；各MANIFEST列固定来源、原路径和原字节SHA256。大模型/纹理、原始录像和全部截图不重复复制，共用资产去重引用。archive不是已接入的产品目录，未经还原依赖不宣称可直接打开运行。材质、LOD4完整源链及LOD3未闭环证据仍只按已知范围索引，不能称全部完整源已合入main。


## 已知材质候选发布来源

补齐[历史体验](https://yydshly.github.io/azure-reef-3d/preview/surface-grounding-candidate/scan-exhibit.html)、[原main发布提交ef6a761](https://github.com/yydshly/azure-reef-3d/commit/ef6a7618ef02bdcf8134aa3f395be5e9d90e2f6f)与[Actions38147691994](https://github.com/yydshly/azure-reef-3d/actions/runs/38147691994)。局部法线/粗糙度略有收益，整体目标未达，未提升主展示。本次没有重新验收画面；已知历史发布来源不等于本轮完整源码和素材已迁入当前main，原完整还原链仍按未迁移范围记录。
