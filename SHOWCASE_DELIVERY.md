# 统一展示网页交付 · 2026-10-13

[打开统一首页](https://yydshly.github.io/azure-reef-3d/) · [保留原站](https://yydshly.github.io/azure-reef-3d/legacy.html)

本次完成中文版本展示网页：10个版本、7个已发布交互入口、9张各版本独立真实截图。LOD3明确无已核验预览；构图和海盆失败候选只查看证据。默认展示海庭01.2，页面和卡片明确标注“已发布技术原型，整体视觉未达标”。此次网页交付没有改变海域视觉结论。

源码提交：[b95b943](https://github.com/yydshly/azure-reef-3d/commit/b95b9430101a643bb712ba42554a8f0c1ea5b5e6)。[Pages运行38332197977](https://github.com/yydshly/azure-reef-3d/actions/runs/38332197977)成功。沿用原GitHub Pages环境、权限、Git凭据和公开地址，没有新服务或付款。

## 已完成验证

- Windows现有沙箱Edge，1280×820桌面及390×740手机：线上35项检查通过，零页面JavaScript错误。
- 首次打开没有iframe、video或海域资源请求；缩略图懒加载。按需进入只保留一个场景，切换替换旧iframe，返回卸载；录像与场景共用同一查看器。
- 版本筛选、失败候选没有交互入口、选择后的键盘焦点、窄屏无横向溢出通过。导览实际推进到5秒；126.56秒原实录元数据及实际播放推进通过。公开录像提供正确video/webm类型和206字节范围响应；首次播放可能需要网络缓冲。
- 全部7个公开入口通过首页查看器逐个打开。海庭三版、enriched、材质及LOD4已查看实际渲染；原站首次8秒检查仍在加载，补充一次35秒上限核验：19.61秒内ready，已查看实际渲染并成功返回。
- 首页HTML/CSS/JS/版本索引公开字节与部署回执哈希匹配。

## 旧资源保全

从最后已验证的完整Pages快照恢复旧站，仅替换根index.html。原2324个文件中的其余2323个逐文件哈希一致；其中2245个preview文件零改动，world指针未变。旧index.html逐字另存legacy.html，保留相同目录位置和相对资源路径。新代码未覆盖任何旧海庭、enriched、扫描或其他preview资源。

部署恢复脚本只在原Actions runner处理完整快照，没有把2.24GB快照下载到本机。[保全回执](evidence/showcase-launch/publication-receipt.json)记录全量保留摘要、入口哈希和源码提交；公开入口也重新校验了哈希。

## 真实证据

[桌面首屏](evidence/showcase-launch/public-desktop-home.png) · [完整版本卡](evidence/showcase-launch/public-desktop-full-page.png) · [手机版版本列表](evidence/showcase-launch/public-mobile-versions.png) · [手机内实际导览](evidence/showcase-launch/public-mobile-scene012-tour.png) · [线上操作实录](evidence/showcase-launch/public-interactions.webm)

[线上检查结果](evidence/showcase-launch/public-browser-results.json) · [七个入口及保留哈希](evidence/showcase-launch/public-preserved-and-links.json) · [发布状态](evidence/showcase-launch/run-status.json) · [图片/录像来源及许可](dist/showcase/media/sources.json)

## 范围与限制

没有重验收所有历史场景，也没有重跑完整72秒导览；已有原实录和未改动的源码继续保留。没有修旧场景、重新解码LOD3或下载大扫描。整体海域真实感、生物丰富度和空间连续性仍未达到项目目标。

本次恢复脚本是从固定旧快照首次落地首页的发布边界。后续再次更新首页需以新的完整已发布快照建立保留清单；不要直接把main的dist目录当成完整旧站覆盖发布。
