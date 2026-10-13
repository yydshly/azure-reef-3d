# 历史场景恢复与独立展示 · 2026-10-13

唯一入口：[海底项目版本展示](https://yydshly.github.io/azure-reef-3d/)。用户已授权把历史尝试恢复为独立实验预览。旧视觉评审结论继续保留，不能据此拒绝展示；这些入口不表示整体海域目标已完成。

## 首批五个新增入口

| 场景 | 独立入口 | 原始来源 |
| --- | --- | --- |
| 连续礁岛首候选 | [体验](https://yydshly.github.io/azure-reef-3d/preview/continuous-candidate/scan-exhibit.html) | b92b8ac；151文件组装版，6份增量复用固定enriched基线 |
| 连续礁岛构图修正版 | [体验](https://yydshly.github.io/azure-reef-3d/preview/composition-candidate/scan-exhibit.html) | 0478d7a；151文件组装版，6份增量复用相同基线 |
| 海盆证明段首版 | [体验](https://yydshly.github.io/azure-reef-3d/preview/reef-basin-first/) | bef0b85的first-pass/source，5份原始运行源码 |
| 海盆证明段修正版 | [体验](https://yydshly.github.io/azure-reef-3d/preview/reef-basin-proof/) | bef0b85的最终dist，5份原始运行源码 |
| LOD4/LOD3真实扫描对照 | [体验](https://yydshly.github.io/azure-reef-3d/preview/real-splats-lod-compare/) | f436dd8中的既有STATIC-WEB源包，16个文件；进入后可选择LOD3 |

四个海域原始源码和素材未改美化。已有库、模型、纹理和署名继续保留。LOD3恢复包17,831,987字节，Git对象哈希已验证；原始135,471点数据31,972,633字节，SHA256 `85c0f7b5bdae524c47fb91dbafcfefa5365186f0be75fba52c01923f547f9b67`匹配。

## 当前实际核验

现有Windows沙箱Edge真实WebGL运行。连续两版和海盆两版分别通过ready、实际渲染、键盘前进；各自截图位于[evidence/history-release](evidence/history-release/)。未重跑全部72秒导览。

LOD3仅做一次有界恢复核验：LOD4加载后切换LOD3，135,471点已解析并参与绘制，数据哈希匹配，基本移动通过；[实际截图](evidence/history-release/lod3-rendered.png)已查看。旧decoder完成证据未闭环记录仍作为历史记录保留，本次结果不表示完整海域或所有设备验收。

部署使用最新完整已发布Pages快照恢复站点，再追加这五个独立目录。现有全部preview文件及旧资源逐字保全，当前首页仅更新版本索引、导航和新增真实截图；原站legacy.html和world指针不得改变。准确源码增量、固定基线149文件哈希见[history-release.json](history-release.json)。main并非完整旧站镜像，不能直接覆盖发布其dist目录。

## 有具体阻塞的档案

**谷地高度场**：Library解析出的实际源包名称为 `azure-reef-continuous-valley-REJECTED-SOURCE.zip`，186,792,652字节；记录的预期SHA256为 `9c30a416c6725bee9411afde1b47352ff246c2af6cbd00276cd4ef0527fe22ca`。已按当前Library技能请求物化并运行官方下载助手，但助手在保存文件身份属性时调用Windows Python不支持的`os.setxattr`，未安装本地文件。当前没有已物化源包，不能声称完成哈希核验、恢复或发布。没有绕过该流程或放宽权限；[具体结果](evidence/history-release/valley-blocker.json)已保存。

首页将此项单独标为待恢复，不混入连续首候选，也不冒充已发布。现有旧站其他场景目录将在完整快照恢复清单中继续核对，已发布版本不会重复覆盖。


## 已成功发布的首批

源码提交 `47252721826b2ce635cd0d9b2ecc55be6b28bc6c`，[Pages运行38345275535](https://github.com/yydshly/azure-reef-3d/actions/runs/38345275535)成功。前述五个入口已追加上线；此前2339个文件中的2334个保持一致，2245个旧preview文件零改动，world指针及legacy原站未变。

## 既有14个历史入口

这14项已经在旧Pages快照中，原场景及资源保持不变。本次补回各自首页卡片、差异和原始真实截图，没有把它们混成一个版本。各卡片“截图/证据”链接直接指向该版本的current-scene.html，截图来源和字节哈希见showcase/media/sources.json。

## 三项早期运行增量

单海扇流动、远景海扇LOD、低机位路线分别恢复原运行上下文。单海扇基线为a95871f，低机位基线为a18e1f7，海扇LOD使用真实Git QA提交3de9e11（旧记录的Site短版本5ac7f68并非可查询的Git提交）。复用保全快照的原模型/素材和归档中的原增量；未改原视觉、波形、LOD或路线。

本机Chrome直接检查ready、模型mesh存在和真实相机转向，三项均通过；[记录](evidence/history-release/early-runtime-local-check.json)。低机位旧路线的近鱼问题及海扇的历史视觉退化结论继续保留。未重跑100秒旧路线或所有72秒导览。

## 全量场景索引

| 名称 | 入口/当前恢复状态 | 证据 |
| --- | --- | --- |
| 海庭 01.2 | [打开](https://yydshly.github.io/azure-reef-3d/preview/reef-garden-stage-012/) | [源码/原效果](https://raw.githubusercontent.com/yydshly/azure-reef-3d/3c00efbec735c7618c842edf3f5a0716e1147323/evidence/reef-garden-stage/live-entry.png) |
| 海庭 01.1 | [打开](https://yydshly.github.io/azure-reef-3d/preview/reef-garden-v11/) | [源码/原效果](https://raw.githubusercontent.com/yydshly/azure-reef-3d/3c00efbec735c7618c842edf3f5a0716e1147323/evidence/reef-garden-v11/live-entry.png) |
| 海庭首版 | [打开](https://yydshly.github.io/azure-reef-3d/preview/reef-garden-v1-first/) | [源码/原效果](https://raw.githubusercontent.com/yydshly/azure-reef-3d/3c00efbec735c7618c842edf3f5a0716e1147323/evidence/reef-garden-v1/live-entry.png) |
| 原 enriched | [打开](https://yydshly.github.io/azure-reef-3d/preview/world/) | [源码/原效果](showcase/media/enriched.webp) |
| 浅蓝原站 | [打开](https://yydshly.github.io/azure-reef-3d/legacy.html) | [源码/原效果](showcase/media/original.webp) |
| 材质候选 | [打开](https://yydshly.github.io/azure-reef-3d/preview/surface-grounding-candidate/scan-exhibit.html) | [源码/原效果](showcase/media/material.webp) |
| LOD4 局部扫描 | [打开](https://yydshly.github.io/azure-reef-3d/preview/real-splats-probe/) | [源码/原效果](showcase/media/lod4.webp) |
| 连续礁岛 · 首候选 | [打开](https://yydshly.github.io/azure-reef-3d/preview/continuous-candidate/scan-exhibit.html) | [源码/原效果](https://github.com/yydshly/azure-reef-3d/tree/b92b8ac734973e2673f3f678f6d5f1241393373c/evidence/continuous-20261012) |
| 连续礁岛 · 构图修正版 | [打开](https://yydshly.github.io/azure-reef-3d/preview/composition-candidate/scan-exhibit.html) | [源码/原效果](https://github.com/yydshly/azure-reef-3d/blob/0478d7ab42eae11e65fc53f83b5253e9dcda9822/evidence/composition-20261012/VISUAL-VERDICT.json) |
| 海盆证明段 · 首版 | [打开](https://yydshly.github.io/azure-reef-3d/preview/reef-basin-first/) | [源码/原效果](https://github.com/yydshly/azure-reef-3d/tree/bef0b8506b5e1b6726585722573014038bdc570a/evidence/basin-proof/first-pass) |
| 海盆证明段 · 修正版 | [打开](https://yydshly.github.io/azure-reef-3d/preview/reef-basin-proof/) | [源码/原效果](https://github.com/yydshly/azure-reef-3d/tree/bef0b8506b5e1b6726585722573014038bdc570a/evidence/basin-proof) |
| LOD4 / LOD3 真实扫描对照 | [打开](https://yydshly.github.io/azure-reef-3d/preview/real-splats-lod-compare/) | [源码/原效果](https://github.com/yydshly/azure-reef-3d/blob/main/HISTORY_RELEASE.md) |
| 圆润群落形态 | [打开](https://yydshly.github.io/azure-reef-3d/preview/colony-form-candidate/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/colony-form-candidate/current-scene.html) |
| 馆藏珊瑚中景 | [打开](https://yydshly.github.io/azure-reef-3d/preview/coral-midground-candidate/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/coral-midground-candidate/current-scene.html) |
| Darwin surfel扫描 | [打开](https://yydshly.github.io/azure-reef-3d/preview/darwin-surfel-candidate/index.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/darwin-surfel-candidate/current-scene.html) |
| 自由探索初版 | [打开](https://yydshly.github.io/azure-reef-3d/preview/exploration-demo-candidate/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/exploration-demo-candidate/current-scene.html) |
| 原地环顾实验 | [打开](https://yydshly.github.io/azure-reef-3d/preview/full-turn-candidate/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/full-turn-candidate/current-scene.html) |
| 局部接地实验 | [打开](https://yydshly.github.io/azure-reef-3d/preview/grounded-integration-candidate/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/grounded-integration-candidate/current-scene.html) |
| 生态衔接实验 | [打开](https://yydshly.github.io/azure-reef-3d/preview/habitat-enrichment-candidate/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/habitat-enrichment-candidate/current-scene.html) |
| 独立真实扫描场景 | [打开](https://yydshly.github.io/azure-reef-3d/preview/independent-scan/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/independent-scan/current-scene.html) |
| 层次礁区实验 | [打开](https://yydshly.github.io/azure-reef-3d/preview/layered-reef-candidate/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/layered-reef-candidate/current-scene.html) |
| 自然岩基实验 | [打开](https://yydshly.github.io/azure-reef-3d/preview/natural-rock-candidate/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/natural-rock-candidate/current-scene.html) |
| 后方礁群实验 | [打开](https://yydshly.github.io/azure-reef-3d/preview/rear-habitat-candidate/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/rear-habitat-candidate/current-scene.html) |
| 后方布局实验 | [打开](https://yydshly.github.io/azure-reef-3d/preview/rear-layout-candidate/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/rear-layout-candidate/current-scene.html) |
| 连续礁区场实验 | [打开](https://yydshly.github.io/azure-reef-3d/preview/reef-field-candidate/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/reef-field-candidate/current-scene.html) |
| 可见坡面生态实验 | [打开](https://yydshly.github.io/azure-reef-3d/preview/visible-habitat-candidate/scan-exhibit.html) | [源码/原效果](https://yydshly.github.io/azure-reef-3d/preview/visible-habitat-candidate/current-scene.html) |
| 单海扇流动实验 | [打开](https://yydshly.github.io/azure-reef-3d/preview/history-fan-current/) | [源码/原效果](https://github.com/yydshly/azure-reef-3d/blob/main/HISTORY_RELEASE.md) |
| 远景海扇LOD实验 | [打开](https://yydshly.github.io/azure-reef-3d/preview/history-fan-lod/) | [源码/原效果](https://github.com/yydshly/azure-reef-3d/blob/main/HISTORY_RELEASE.md) |
| 低机位路线实验 | [打开](https://yydshly.github.io/azure-reef-3d/preview/history-low-camera/) | [源码/原效果](https://github.com/yydshly/azure-reef-3d/blob/main/HISTORY_RELEASE.md) |
| 谷地高度场 · 历史实验 | 源包转移受阻，未发布 | [源码/原效果](https://github.com/yydshly/azure-reef-3d/blob/main/HISTORY_RELEASE.md) |

## 早期形态实验与明确缺口

以下12项已在既有源码档案逐项核对。前三项已恢复为独立运行目录。剩余项目没有保存完整独立交互海域，不能因一张离线图片就冒充已部署场景；这是运行文件/工具缺口，不是以视觉失败拒绝展示。原脚本、几何及离线证据仍保留在[固定档案](https://github.com/yydshly/azure-reef-3d/tree/acd6b3f9f287b8fa5b8e07e4ffddf3491668c92b/experiments)。

| 原实验 | 保存内容与明确限制 |
| --- | --- |
| 单海扇受流 | 原app与shader增量、专用QA原图；恢复独立实验入口 |
| 远景海扇LOD | 原运行增量、low-fans.glb和QA上下文；恢复独立实验入口 |
| 低机位路线 | 原candidate-passage.js及固定基线；恢复独立实验入口 |
| 连接硬底 | 原脚本/离线证据；30,515,244字节候选GLB未收入档案，需按原脚本重导出 |
| 局部肩部 | 原脚本/离线证据；30,455,516字节输出GLB被明确排除，需原脚本重导出 |
| 可见岩檐 | 原重建脚本/离线证据；29MB完整候选被明确排除，需重导出 |
| 后段灰模 | 离线Cycles灰模比对；不是网页材料/水体/动画结果，未存独立网页运行包 |
| 分枝层级 | 仅局部样本配方和离线证据；原记录明确没有补成整场景GLB或运行接入 |
| 交错侧枝 | replacement.glb、配方及离线证据；局部替换在离线内存场景中完成，没有完整独立网页包，导出非流形记录保留 |
| 实体肩部 | 377KB局部GLB、脚本与离线证据；未形成完整网页接入/相机与鱼路线运行包 |
| 体积表面 | volume-shoulder.glb及离线证据；未形成完整网页运行接入，保留原形态结论 |
| 地表纹理输入 | 仅输入筛选记录，纹理从未应用到模型或场景；不存在待恢复的历史场景 |

可重建项的原source-model.glb已在本机，SHA256 c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd匹配。但本机未发现已可调用的Blender（PATH及现有常用软件目录均未发现），不安装新工具或重新研发几何。本次以原离线证据和上述具体缺口列清，未假称互动上线。

## 验收边界与遗留问题

- 首批四海域及LOD3本机实际渲染/移动通过；三个早期增量本机ready/模型/相机移动通过。各自原始真实截图已查看。
- 已发布HTML、入口和依赖在公开地址返回200，部署及逐字保全回执成功。
- 当前Windows浏览器直连新场景ready超时；Edge与Chrome的静态首页截图接口也超时。安全curl读取公开字节的适配尝试又遇到部分TLS握手错误，已停止重试。不能把本地运行或这种适配尝试冒充线上实测通过。
- 手机版只属于390×740尺寸模拟，当前新截屏未通过，不能声称真实手机验证。完整72/100秒流程未重跑。
- 谷地高度场依旧受官方Library助手Windows身份属性接口阻塞；没有已物化源包，未验SHA、未发布。
- 整体海域真实感、生物丰富度、空间连续性仍未达到项目目标；局部真实模型和发布数量不能替代该结论。
