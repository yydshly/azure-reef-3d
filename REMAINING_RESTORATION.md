# 原始实验补全 — 2026-10-13

统一入口：[项目版本展示](https://yydshly.github.io/azure-reef-3d/)。本轮在原有 29 个交互入口之外补充七个原模型查看器；总览为 37 项、36 个可打开入口、1 个谷地待恢复项。**模型查看器明确标为样本，不代表完整网页海域，也不改变原来视觉未达标的结论。**

## 原始模型样本

| 实验 | 新查看入口 | 恢复方式 | 原模型 SHA256 |
| --- | --- | --- | --- |
| 实体肩部 | [查看样本](https://yydshly.github.io/azure-reef-3d/preview/sample-solid-shoulder/) | 归档 GLB 原样复制 | `7472155ab3be14c310eb0865093397b1906d759b6a40a79af6ebbe885ab0ce40` |
| 交错侧枝 | [查看样本](https://yydshly.github.io/azure-reef-3d/preview/sample-staggered-colony/) | 归档 GLB 原样复制，保留原 16 条非流形边问题 | `4a6f291b0ffad79a6b9d9fba581c9944ba3009f035f38b8642d09f766b579b28` |
| 体积表面 | [查看样本](https://yydshly.github.io/azure-reef-3d/preview/sample-volume-shoulder/) | 归档 GLB 原样复制 | `f77845ac5a06c872e9821aab6e097c91cf8c2f071a2692774770d8d7d0c6d9fc` |
| 连续硬底 | [查看样本](https://yydshly.github.io/azure-reef-3d/preview/sample-connected-hardbottom/) | 原 `replace_hardbottom.py`、原输入、默认参数重建，历史输出字节一致 | `75a181a1fea752a05792a055cc2fad2a42c0d0516f42ed9ae64a3d8300f64265` |
| 局部肩部 | [查看样本](https://yydshly.github.io/azure-reef-3d/preview/sample-shoulder-sample/) | 原 `shape_shoulder.py`、原输入、默认参数重建，历史输出字节一致 | `1d0b54fb008b205a102a88c682636cad827114aeb2d0234f2752d57158b31b22` |
| 可见折叠 | [查看样本](https://yydshly.github.io/azure-reef-3d/preview/sample-visible-ledge/) | 原 `fold_visible_ledge.py`、原模型及 landmark 输入重建，历史输出字节一致 | `9e0cb3f417905582b7947e5fc4e239dbd6596e3bea6905921c177903356e4239` |
| 晚位灰模 | [查看样本](https://yydshly.github.io/azure-reef-3d/preview/sample-late-bank-grey/) | 原 `sculpt_late_bank.py`、原模型及 landmark 输入重建，历史输出字节一致 | `941e9fa1ca42b2918ff818a2f9f46aff1f948860d52d0dc836f1625b68947ed1` |

原脚本均来自固定归档提交 `acd6b3f9f287b8fa5b8e07e4ffddf3491668c92b`，未调整配方或参数。现有 NumPy/SciPy 足以生成后四个模型，Blender 并非它们模型重建的必要条件。原输入 `source-model.glb` SHA256 `c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd`，原 landmark SHA256 `d6377e6bcfc5145ef6da7c139de26772b6065b30fbe24c2d3180bcba9ae48cdf`，均已核对。

查看器使用已发布的 Three.js/GLTFLoader/OrbitControls。保留原模型几何、材质、坐标与根变换，只提供中性照明和查看相机。四个原场景模型的初始相机框定原有 `Spatial_Continuous_Weathered_Limestone` 地形，避免被原模型的大沙地缩成小点。它们没有新增水体、鱼群、导览或美术方案。后四项每个约 30 MB，按需打开，首页不预载。

## 仍待补全的两项

- **谷地高度场：工具兼容性阻塞。** 官方 Library 当前流程仅返回带身份元数据的签名转移，没有直接放置到当前 Windows 工作区；官方 helper 在 Windows Python 3.10 调用 `os.setxattr` 失败。重新读取的官方 helper 逻辑未改变；本轮没有重复相同的大文件下载。此机 WSL 组件存在但没有 Linux 发行版，也未找到其他兼容 Python。源包尚未成功物化、未验 SHA256、未恢复、未发布。需要用户许可在同一电脑安装官方 Ubuntu WSL 发行版，并在 Linux 文件系统运行不改动的官方 helper；或者由官方提供受支持的 Windows 文件标识写入流程。未绕过 Library 身份标识。
- **疏枝层级：原构建脚本依赖 Blender。** `build_candidate.py` 使用 `bpy`/`bmesh`，此机没有 Blender。原输入已具备；原脚本预期 replacement SHA256 `7012c9c0a502ff8fcbbca43b219d2c205bcfe11f20c8a61bbcf121312392964b`。需用户许可下载官方 Blender 4.3.2 Windows 便携 ZIP，解压到当前工作区 `.tools/blender`，仅按原脚本执行，之后核对原输出哈希。尚未安装或执行构建。

**地表照片输入仅保留证据。** 原记录明确没有应用到模型或场景，因此不存在可恢复的历史交互场景；不会据此制造一个新场景。

用户本轮明确回复“不安装”。Ubuntu WSL、Blender 和替代新软件均不安装，不再重复询问。这两项保持未完成；此前已用现有工具完成的七项独立交付。Microsoft 的安装说明：[官方 WSL 文档](https://learn.microsoft.com/en-us/windows/wsl/install)。Blender 版本必须与原构建记录一致，使用官方发布包，不修改系统安全设置、关联或凭据。

## 验证证据与范围

指定 Windows 电脑的 Chrome WebGL2 实际像素探针通过，使用 Intel UHD / Direct3D11，读取到红色像素且 GL error 为 0；未加入绕过 GPU 安全的启动参数。

七个样本本地实际绘制、视角变化、原模型根变换保持均通过。原始截图像素已逐项查看，保存在 [证据目录](evidence/remaining-restoration/)。后四个重建输出全部通过历史 SHA256 一致校验；[重建记录](evidence/remaining-restoration/original-script-rebuild-check.json)、[现成模型运行记录](evidence/remaining-restoration/samples-local-check.json)、[重建模型运行记录](evidence/remaining-restoration/rebuilt-samples-local-check.json)区分保存。PNG 是真实 WebGL 画布像素导出，首页 WebP 仅缩放压缩，来源及哈希登记在 `showcase/media/sources.json`。

公开部署后的实际渲染、移动和返回核验另行记录；本地通过不能替代线上通过。完整 72/100 秒历史导览、真实手机和所有历史海域全量渲染不在本次复测范围。恢复与发布不会使海底项目的真实感、生物丰富度、景观连续性自动达标。


## 实际发布与公开核验

源码提交 `5a9c61c64b4734e38d09e6fc6c80d708a5152d16`， [Pages 运行 38385076150](https://github.com/yydshly/azure-reef-3d/actions/runs/38385076150) 成功。发布从上一份完整快照恢复，原有 2,927 个文件中的 2,922 个逐字节保留；仅五个自有总览文件允许更新。原有 2,812 个 preview 文件零改动，world 指针与 legacy 原站未变。七个新样本各五个文件。[保全回执](evidence/remaining-restoration/publication-receipt.json)已保存。

指定 Windows Chrome 在公开 GitHub Pages 地址完成三个现成局部 GLB 的真实渲染与视角变化，截图像素已实际查看：[实体肩部](evidence/remaining-restoration/public-solid-shoulder.png)、[交错侧枝](evidence/remaining-restoration/public-staggered-colony.png)、[体积表面](evidence/remaining-restoration/public-volume-shoulder.png)。公开总览中八步连续拖动产生八个不同相机位置，切换第二个样本并返回后 iframe 释放；390×740 模拟尺寸无横向溢出。[连续运动真实像素](evidence/remaining-restoration/continuous-drag-public.png)、[公开运行记录](evidence/remaining-restoration/samples-public-check.json)、[公开入口操作记录](evidence/remaining-restoration/portal-public-check.json)分别保留。

37 项总览、36 个可打开入口的 HTTP 200 和发布回执/保护入口哈希核验通过。[公开 HTTP 与哈希记录](evidence/remaining-restoration/public-http-and-hash-check.json)不等同于 36 个场景全部渲染验收。四个原脚本重建模型已经本地真实渲染通过及字节一致，未追加公开全模型渲染复测；完整历史导览、所有历史海域全量渲染和真实手机未测。

最新完整 Pages 包 artifact `11805017825`，2,904,694,811 字节，SHA256 `2812632b4fb83d41fa39e1b9afb73c46157eda4d80f31ec18d8b63f395aeec1f`。保留现有临时 artifact 到期规则，2026-10-14 10:43:45 UTC 到期，未声称永久备份；已发布完整站点和旧入口继续存在。[快照及部署记录](evidence/remaining-restoration/deployment-and-snapshot.json)。

最终状态：七项原模型样本完成；谷地与疏枝层级因用户本轮不安装且当前工具不支持而未完成；照片输入原未形成场景，仅作证据。没有安装任何新软件，未绕过官方 Library 身份元数据流程。海底项目整体视觉目标仍未达标。


完整当前站点的持久备份已补齐：原ZIP字节三卷、全站2,969文件清单、远端回读与逐文件恢复校验、main索引见 [PAGES_ARCHIVE.md](PAGES_ARCHIVE.md)。不再依赖上文短期artifact到期前才能恢复；原artifact照常保留，网站未再次发布。
