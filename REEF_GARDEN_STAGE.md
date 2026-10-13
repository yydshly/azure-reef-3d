# 阶段总结：技术原型与视觉目标差距

统一网页：[海底项目版本展示](https://yydshly.github.io/azure-reef-3d/)；含独立真实截图、状态与按需交互。原站保存在 [legacy.html](https://yydshly.github.io/azure-reef-3d/legacy.html)。这次完成的是展示网页，海庭01.2视觉未达标结论保持不变。

记录日期：2026-10-12。范围为 azure-reef-3d 海底项目；ocean-world / TIDAL 是独立项目，不合并计算成果。

**本阶段有可运行、可演示和可追溯的技术原型，但整体视觉目标未达成。** 用户于 2026-10-12 08:15 UTC 明确否定海庭 01.2 整体质量；42 秒盆地证明段随后仍失败。两者不能恢复为“待用户验收”。本次只收口总结与档案，产品代码、线上入口、工作流、标签和旧版本不动；技术通过、发布成功与归档不能替代项目目标完成。

## 原目标与风格化要求

目标是连贯、可探索的海底世界：入口有明显纵深；前进、横移、转身和返回时，近中远景持续有内容；各地段自然过渡；完整导览可演示；生物形态、群落布局、水下光色与动作共同建立可信的海域体验。用户后续同意风格化，但没有同意降低整体质量；台座、沙路走廊、重复摆件和空回望不能用风格解释。

## 已有入口、源码、标签和证据

入口存在只表示版本保留，不表示视觉通过。

| 版本 | 入口与固定记录 | 当前结论 |
| --- | --- | --- |
| 原始三维与教学 | [原站](https://yydshly.github.io/azure-reef-3d/)；[早期源码与归档](https://github.com/yydshly/azure-reef-3d/tree/acd6b3f9f287b8fa5b8e07e4ffddf3491668c92b) | 原模型、五站教学、鱼运动、局部支撑及扫描近看是技术积累，不是整体海域验收。 |
| enriched 基线 | [world](https://yydshly.github.io/azure-reef-3d/preview/world/)；[源码 a1b2cae](https://github.com/yydshly/azure-reef-3d/commit/a1b2cae7e968ad383798a0ff15c87bfb0934d971) | 三区探索、72 秒六站导览、碰撞、暂停重播与移动操作保留；真实感和连续性不足。 |
| 局部扫描探针 | [real-splats-probe](https://yydshly.github.io/azure-reef-3d/preview/real-splats-probe/) | 局部实验，不等于完整可探索海域。 |
| 海庭首版 | [固定首版](https://yydshly.github.io/azure-reef-3d/preview/reef-garden-v1-first/)；[发布 c98fdca](https://github.com/yydshly/azure-reef-3d/commit/c98fdcadd7f4d3d0676628ece4be242f4057938a) | 历史技术发布，不代表整体视觉完成。 |
| 海庭 01.1 | [固定 01.1](https://yydshly.github.io/azure-reef-3d/preview/reef-garden-v11/)；[源码与证据 348ead4](https://github.com/yydshly/azure-reef-3d/commit/348ead4995f21d5a595640165c3b10cc14b63219)；[发布 16d7abd](https://github.com/yydshly/azure-reef-3d/commit/16d7abd64716da68956eb637fa2732aa984fa56b) | 保留对照，不升级为当前视觉完成结论。 |
| 海庭 01.2 | [稳定技术入口](https://yydshly.github.io/azure-reef-3d/preview/reef-garden-v1/)；[固定 01.2](https://yydshly.github.io/azure-reef-3d/preview/reef-garden-stage-012/)；[发布 2442e73](https://github.com/yydshly/azure-reef-3d/commit/2442e73221615cff960e981e1504064b4b9e70b7)；[成功部署](https://github.com/yydshly/azure-reef-3d/actions/runs/38220531117) | 可运行且已发布，用户否定整体质量。 |
| 01.2 固定源码与证据 | [标签 reef-garden-01.2-stage](https://github.com/yydshly/azure-reef-3d/tree/reef-garden-01.2-stage)；[证据提交 3c00efb](https://github.com/yydshly/azure-reef-3d/commit/3c00efbec735c7618c842edf3f5a0716e1147323) | 标签保留，不重新解释为视觉通过。 |
| 盆地证明段 | [独立源码与证据 bef0b85](https://github.com/yydshly/azure-reef-3d/commit/bef0b8506b5e1b6726585722573014038bdc570a)；分支 `candidate/reef-basin-proof` | 三项视觉门槛全失败，已停止；只有独立备份，没有发布。 |

01.2 的[入口](https://github.com/yydshly/azure-reef-3d/blob/3c00efbec735c7618c842edf3f5a0716e1147323/evidence/reef-garden-stage/station-1-front.png)、[中程回望](https://github.com/yydshly/azure-reef-3d/blob/3c00efbec735c7618c842edf3f5a0716e1147323/evidence/reef-garden-stage/station-3-return.png)、[深处](https://github.com/yydshly/azure-reef-3d/blob/3c00efbec735c7618c842edf3f5a0716e1147323/evidence/reef-garden-stage/station-6-front.png)、[原始完整录像](https://github.com/yydshly/azure-reef-3d/blob/3c00efbec735c7618c842edf3f5a0716e1147323/evidence/reef-garden-stage/complete-demo.webm)及[全部六站与技术回执](https://github.com/yydshly/azure-reef-3d/tree/3c00efbec735c7618c842edf3f5a0716e1147323/evidence/reef-garden-stage)保留。

盆地的[入口](https://github.com/yydshly/azure-reef-3d/blob/bef0b8506b5e1b6726585722573014038bdc570a/evidence/basin-proof/final/00-start-front.png)、[180°回望](https://github.com/yydshly/azure-reef-3d/blob/bef0b8506b5e1b6726585722573014038bdc570a/evidence/basin-proof/final/02-180-return-view.png)、[环视空旷方向](https://github.com/yydshly/azure-reef-3d/blob/bef0b8506b5e1b6726585722573014038bdc570a/evidence/basin-proof/final/06-panorama-quarter-3.png)、[42.36 秒未剪辑录像](https://github.com/yydshly/azure-reef-3d/blob/bef0b8506b5e1b6726585722573014038bdc570a/evidence/basin-proof/final/uncut-proof.webm)和[失败评估](https://github.com/yydshly/azure-reef-3d/blob/bef0b8506b5e1b6726585722573014038bdc570a/evidence/basin-proof/ASSESSMENT.json)均已远端保存；首版和唯一一次纠正的过程都保留。

## 各路线结果与未闭环项

| 路线 | 结果与记录 |
| --- | --- |
| 材质候选、早期局部修正 | 只改材质的整体收益不足；局部形态、支撑和水色修正不能升级为整体完成。[早期迭代记录](https://github.com/yydshly/azure-reef-3d/blob/acd6b3f9f287b8fa5b8e07e4ffddf3491668c92b/ITERATION_LOG.md)与[实验归档](https://github.com/yydshly/azure-reef-3d/tree/acd6b3f9f287b8fa5b8e07e4ffddf3491668c92b/experiments)保留；本次未复核材质候选的独立发布回执。 |
| 连续谷地与构图候选 | 技术可运行，长直空床和深处空回望仍在，整体视觉失败，未发布。[连续候选 b92b8ac](https://github.com/yydshly/azure-reef-3d/commit/b92b8ac734973e2673f3f678f6d5f1241393373c)、[构图失败 0478d7a](https://github.com/yydshly/azure-reef-3d/commit/0478d7ab42eae11e65fc53f83b5253e9dcda9822)、[连续录像](https://github.com/yydshly/azure-reef-3d/blob/bef0b8506b5e1b6726585722573014038bdc570a/evidence/continuous-20261012/native-tour.webm)、[构图判定](https://github.com/yydshly/azure-reef-3d/blob/bef0b8506b5e1b6726585722573014038bdc570a/evidence/composition-20261012/VISUAL-VERDICT.json)。构图失败后没有新增连续录像或发布，不能补写通过。 |
| LOD4 局部扫描 | 仅有局部细节或探针，覆盖、完整性和探索连续性不足，不能外推为完整世界。本次没有重新解码或建立整体质量证明。 |
| LOD3 / Gaussian 诊断 | 证据未闭环，未发布为产品，也不是 enriched 基线。[历史诊断 dd6b671](https://github.com/yydshly/azure-reef-3d/commit/dd6b671461aa1a9ff2fb2287137ae7bbdea0da50)保留为来源；不重启该诊断，不以 CI 代替产品证据。 |
| 海庭 01.2 | 六站风格化演示和技术发布完成，整体质量被用户否定；不是待验收候选。 |
| 盆地证明段 | 连续礁脊、开放盆地经过一次纠正仍像长台摆件，环视仍空，层次不贯穿运动；三项门槛全失败。录像 42.36 秒，实际运动 38.34 秒，61°视角，真实前进、回望、横移、环视并返回，无中途重置位置。只备份，未发布，不再微调此路线。 |

## 功能、视觉与设备验收

保留可复用的自由移动、镜头与输入、碰撞接口、暂停重播、导览控制、移动端操作框架、资源加载和释放。新场景仍须重新标定尺度、出生点、站点与碰撞；不能把交互通过一并当作场景合格。

01.2 既有记录包含约 72.297 秒自然导览、自由移动、返回、碰撞与菜单回归。既有沙箱 Edge / Intel UHD / 1280×820 的不录像 15 秒运动段中，帧间隔中位数 17.6ms、P95 26.9ms。盆地同机含录像开销的运动段为中位数 21.8ms、P95 39.1ms，无脚本、渲染或请求错误。本次文档收口没有重跑这些产品测试，也不能将结果外推到 RTX 4070、真实手机、其他 GPU 或用户常用设备。

盆地的手动操作完整回归、准确礁体几何碰撞、真实手机及六站导览不在已测范围。**技术通过与用户否定、视觉失败并存，不互相抵消。**

## 未达标的原因

- 空间常是沙路走廊，两侧礁块围绕通道或固定目标布置；前进有内容，转身却露出大片无内容海床。
- 礁体仍有台座、圆滑长条和重复摆件感，群落与基底未形成自然连续礁壁；单值高度场变成沙丘，不能代替有体积、岩檐和空隙的礁体。
- 个别固定画面有近中远景，整段运动却没有持续层次；近景大坡面遮深度，远景又常是平淡轮廓。
- 均匀水色、强环境亮度、重复鱼形及简化动作不足以弥补形体与布局问题。
- 局部修正和功能检查屡次通过，整体体验却没有被实际运动证明明显改善。增加对象、只调材质或延长 CI 会重复同一低收益循环。

## 资源筛选与 TIDAL 边界

现有 enriched 的 149 份文件已核对哈希，均完整；其中礁块、博物馆骨架、局部扫描、旧珊瑚和动物不是隐藏的新完整海域。已有骨架的实际独立渲染及旧画面已查看；干标本、陆地礁块、旧失败素材不能换名作为活群落突破。

免费筛选没有找到足够的整体突破：PolyFish 的现有画面及迁移边界、3DAssets.dev underwater-reef-worlds 的长条墙/块拱门、Thalassa 的许可与性能不确定性均不足以支撑本轮接入；新查 Smithsonian 标本仍为干制骨架。专业付费资源只调研，未购买、未付费、未新增凭据；用户暂不购买。这是本轮有限筛选的结果，不宣称市场不存在合格资源。

TIDAL 属于独立仓库 [ocean-world](https://github.com/yydshly/ocean-world)。本轮读取到最新提交 [4749548](https://github.com/yydshly/ocean-world/commit/4749548bfa2216879315fb7b84ad6479cf3a940e)，[运行 38223039936](https://github.com/yydshly/ocean-world/actions/runs/38223039936) 成功，更新于 08:36:29 UTC。确实打开了[在线总览](https://yydshly.github.io/ocean-world/overview/)，保留[实际总览截图](evidence/stage-summary/tidal-overview.png)；其中样板图片是该站既有图片，不是本轮完成的独立 75 秒实时渲染证据。

本轮样板前进、回望、连续层次和性能的独立核验尚未完成，随后按用户文档收口要求停止。未判定该站样板画质失败，也未认定有可信、许可已完整核实的可移植突破。第三方资源逐项源站复核没有完成，不直接复制；293 个体、38 展示类别、67 章等文档数量不计入 azure-reef 成果。范围见[核查记录](evidence/stage-summary/tidal-check.json)。

## 保留范围与不可核实项

- 已远端保留：产品源码、01.2 标签、发布/验证回执、各固定入口、连续/构图候选，以及 bef0b85 的盆地首版、纠正版、原始录像、哈希和失败判定。本次不删旧版本、不改线上指针、不重写标签。
- 只有本地或外部归档：部分完整源包、生成目录、早期阶段索引压缩包和只读资产查看记录。本次不重复下载或物化外部源包，不把未提交的本地文件写成远端已有；已有 Git 归档与上表证据分别列出。
- 未闭环或本次未复核：LOD3 产品与视觉证据、LOD4 整体海域证明、材质候选独立发布回执、TIDAL 连续核验及逐项第三方许可、真实手机/其他 GPU/用户常用设备的达标证明。
- 历史文档、JSON 的 `COMPLETED_PUBLISHED`、`FINITE_STAGE_DELIVERED_PUBLISHED` 及旧“待验收”只反映当时技术发布或记录；当前整体结论以本总结为准。原始证据不篡改，先前整体视觉完成判断撤回。

## 后续重启条件

必须有新的有限路线：许可明确且允许目标用途；原始几何与贴图质量有实际像素证明；入口、中程、深处、转身与返回时有连续近中远景；目标设备真实连续运动与合理性能已有依据。局部扫描、材质候选、干骨架、灰墙模型和计数不能充当新路线。

未来可以沿用交互和资源管理边界，但不自动接入、不自动发布，不继续相同布局或 Gaussian 诊断的无效循环。本阶段收口完成的是总结与证据保存，不是原项目目标完成。

本次验证仅检查文档变更范围、固定提交/标签、文件链接和远端提交存在性，未重跑产品测试。部分 GitHub 页面首次 HEAD 返回临时 503 或传输错误，随后对应原始文件/提交 API 均核对成功；初次结果也保留在[链接核查记录](evidence/stage-summary/link-verification.json)。既有发布回执记录原站 2304 文件及旧入口的保留结果，本次不重新下载全部线上资产；本轮产品目录和工作流零变更。


## 本次main统一交付与源码位置

根README现为唯一展示入口：当前主展示是海庭01.2，已发布但整体视觉未达标。本总结与必要核查记录已从原7c59a653文档版本汇入main；原提交和候选分支保留。

海庭首版、01.1、01.2的实际运行源码在main四个预览目录，20个文件与固定来源逐一同blob。enriched完整149源、连续/构图候选、盆地及部分大包并未全部合入main；这些来源与未确认项见[源码位置索引](SOURCE_INDEX.md)和[机器可读版本索引](STAGE_INDEX.json)。发布恢复旧站快照，不表示main存有完整线上资产镜像。此次仅统一文档与轻量记录，没有把失败场景合到主展示，也没有产品变更或重新部署。


## main必要源码归档补充

用户要求在main统一保存和展示已有阶段内容。已确认的原enriched增量、连续/构图候选、盆地原源文件现按独立[archive目录](archive/)保存，原字节与原来源不变，失败标识保留；原分支、标签和证据不删除。此为源码归档，不将实验接入主展示或部署。共用资产、完整大包、原始录像不重复复制；材质/LOD4完整源链及LOD3证据仍存在未闭环项，不能说所有完整源码和素材都已合入。精确范围见[源码索引](SOURCE_INDEX.md)及各MANIFEST。


## 材质候选历史入口补记

材质/表面支撑候选确有[历史发布入口](https://yydshly.github.io/azure-reef-3d/preview/surface-grounding-candidate/scan-exhibit.html)，原发布main提交为[ef6a761](https://github.com/yydshly/azure-reef-3d/commit/ef6a7618ef02bdcf8134aa3f395be5e9d90e2f6f)，发布回执为[38147691994](https://github.com/yydshly/azure-reef-3d/actions/runs/38147691994)。当时局部法线和粗糙度略有收益，但整体目标仍未达，未提升为当前主展示。本轮只补齐既有索引，没有重新做视觉验收，也未将其完整运行源与素材搬入main；不能将此前“独立入口未复核”的范围说明理解为从未发布。
