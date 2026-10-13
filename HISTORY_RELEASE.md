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
