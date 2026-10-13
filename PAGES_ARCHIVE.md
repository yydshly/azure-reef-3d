# 完整已发布站点的持久归档

归档对象是源码 `5a9c61c64b4734e38d09e6fc6c80d708a5152d16` 对应的 [Pages 发布 38385076150](https://github.com/yydshly/azure-reef-3d/actions/runs/38385076150)，包含当时整个站点、所有旧 preview、原站及公共资产，不是当前 Git `dist` 的局部副本。

持久载体使用**同一个现有仓库的 GitHub Release**：[pages-snapshot-20261013-5a9c61c](https://github.com/yydshly/azure-reef-3d/releases/tag/pages-snapshot-20261013-5a9c61c)。三卷是原 ZIP 的连续字节切片，没有改动压缩方式、模型、网页或其他文件。Release 资产不采用 Actions artifact 的到期规则；仓库所有者仍可管理或删除，哈希用于检测改动。

| 项目 | 固定记录 |
| --- | --- |
| 原完整 ZIP 大小 | 2,904,694,811 字节 |
| 原 ZIP SHA256 | `2812632b4fb83d41fa39e1b9afb73c46157eda4d80f31ec18d8b63f395aeec1f` |
| 完整文件清单 | 2,969 项，文件字节合计 4,139,910,115 |
| 清单 SHA256 | `c721e397eac186b74e6cadf3fc68a664dc5d91f4fdaf02918b9c69a86fd07338` |
| 分卷 manifest SHA256 | `87f15f64e8c1bdf41e14308e1ad0668fc75d5007689afabd842aba05d734b679` |
| 全站路径/文件哈希汇总 | `a26bf5bb525f5835f5fc7f085dccd58dee3629208dbe11cc2a99dda470405d91` |

三卷分别为 1,073,741,824、1,073,741,824、757,211,163 字节。精确顺序、每卷 SHA256 和原包来源保存在 [pages-archive.json](archive/published-pages/2026-10-13/pages-archive.json)；[site-files.json](archive/published-pages/2026-10-13/site-files.json)保存每个文件的完整路径、字节数与 SHA256。

## 无需原 artifact 的复原步骤

1. 从上述 Release 下载三个 `.zip.part001`、`.zip.part002`、`.zip.part003` 资产，以及 `pages-archive.json`、`site-files.json`、`restore-pages-archive.py`，放在同一个新目录。GitHub 自动生成的 Source code ZIP/TAR **不是完整 Pages 备份**。
2. 使用已有 Python 3.10+，仅需要标准库。输出 ZIP 和输出目录均须尚不存在：

   ```text
   python restore-pages-archive.py --manifest pages-archive.json --expected-manifest-sha256 87f15f64e8c1bdf41e14308e1ad0668fc75d5007689afabd842aba05d734b679 --output recovered-pages.zip --site-dir recovered-site --receipt recovery-receipt.json
   ```

3. 脚本核验每卷、拼回原始 ZIP 并核验原包哈希，再安全展开 `artifact.tar`。它逐一核验全部文件与路径集合，生成恢复回执；不需要 GitHub 凭据，不访问 Actions artifact，不覆盖已有目录，不自动发布。

脚本也在 main：[restore-pages-archive.py](restore-pages-archive.py)。恢复目录就是完整站点，可独立本地保存或供后续已授权发布使用。[SHA256SUMS](archive/published-pages/2026-10-13/SHA256SUMS)还记录恢复脚本及说明文件的哈希。

## 后续保全发布输入

[publish-history.py](publish-history.py)和现有 Pages workflow 支持同仓库 Release manifest URL 作为 `snapshot_url`，`snapshot_digest` 使用 manifest SHA256。它会获取并校验三卷、还原原 ZIP，然后执行现有旧文件保全检查和追加逻辑。保留原来直接使用已授权 artifact ZIP 的方式；没有扩大 workflow 权限。

当前固定输入为：

```text
snapshot_url: https://github.com/yydshly/azure-reef-3d/releases/download/pages-snapshot-20261013-5a9c61c/pages-archive.json
snapshot_digest: sha256:87f15f64e8c1bdf41e14308e1ad0668fc75d5007689afabd842aba05d734b679
```

保全发布仍要求 `protected_hashes` 与选定快照/当前站点吻合；未来网站变化后应建立对应新快照，不能盲用旧版本覆盖更新。本次不触发 Pages 发布，也不延长 artifact 保留期。最终远端资产和全量恢复回执登记在此归档目录的验证记录中。


## 已完成的实际验证

三卷及五个说明/校验资产均已上传，并从 Release 实际完整回读，全部 SHA256 与上传前一致。恢复使用回读下来的三卷、manifest、逐文件清单和恢复脚本，没有使用原 Actions artifact 地址；拼回的 ZIP 原哈希一致，完整展开的 2,969 个文件及其路径集合、大小、逐文件 SHA256 和全站汇总全部一致。

[远端回读记录](archive/published-pages/2026-10-13/release-readback-check.json)、[全站恢复回执](archive/published-pages/2026-10-13/remote-recovery-check.json)、[无凭据公开读取记录](archive/published-pages/2026-10-13/public-release-check.json)、[固定归档索引](archive/published-pages/2026-10-13/index.json)均保存在 main。原 artifact 和在线网站未改动，未安装软件、购买服务或扩大 workflow 权限。后续 workflow 的持久源分支已加入并通过语法检查；本次没有再触发部署运行。
