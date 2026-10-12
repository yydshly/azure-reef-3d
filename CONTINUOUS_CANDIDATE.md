# 连续海域候选 · 2026-10-12

这是一份独立、本地可完整演示的 enriched 候选；未覆盖已验证入口，未发布。

## 起点与实现

- 发布基线：`a1b2cae7e968ad383798a0ff15c87bfb0934d971`，不是 main 的 Gaussian 诊断。
- 149 份 enriched 源文件的固定 SHA256 总合同：`ca23bc664217879cd231db3a4f048f71ca2bf2bf0a038e9535e3d202b88e7db4`。
- 源输入来自发布脚本固定的 `acd6b3f9f287b8fa5b8e07e4ffddf3491668c92b` 归档；148 份可从既有 Git 对象恢复，`scan-assemblage.js` 从稳定发布页补齐并通过同一固定哈希。
- Library 原生物化在 Windows 的 `os.setxattr` 步骤失败；没有把未经成功物化的 Library 临时字节当作源码。没有新下载大型扫描、创建凭据、购买服务或改变安全设置。
- `dist` 与 `.github` 对基线无修改。原 enriched 导航控制器、六站、72 秒时长、所有原资产字节保留。

候选用现有 CC0 Poly Haven Boulder 01 的原贴图和三维网格，组成 17 个错落的礁体、34 个相交岩块；基座根据海床的低点嵌入。原作者珊瑚几何与新编写的褶皱片状群落、块状珊瑚、细海扇和中空海绵附着在实际岩体三角面。9 群、286 条新增鱼在固定世界位置的活动带游动并转向、摆尾。没有跟随摄像机的假生物或背景图。

新礁体代理参与原有碰撞解析；扫描和近岸原有障碍保持。水面覆盖到整条路线，太阳方向保持一致，阴影覆盖跟随观察范围。高度场仍只用于海床。

## 本地运行

从本候选分支检出后，在仓库目录运行（需要 Python 和 Node，既有 Git 网络访问）：

```powershell
git fetch --depth=1 origin acd6b3f9f287b8fa5b8e07e4ffddf3491668c92b
python -X utf8 restore-enriched.py
python -X utf8 recover-enriched-source.py
python -X utf8 build-continuous-candidate.py
node qa-continuous-contract.mjs
python -m http.server 4187 --bind 127.0.0.1
```

然后打开 `http://127.0.0.1:4187/artifacts/continuous-candidate/scan-exhibit.html`。

本次工作区已经恢复并构建完成，无须重新下载现有完整文件。`artifacts/enriched-baseline` 是精确原始源，`artifacts/continuous-candidate` 是可运行候选。`candidate-src` 和构建脚本是提交的开发源；生成目录不加入 Git，避免复制 208 MB 未变资产。完整候选源包另留在本地 artifacts 目录。

## 验证边界

实际 Chrome / Intel UHD / ANGLE Direct3D11 的固定视角，使用相同 1280×820 视口和同样相机：入口 `[4,5,10]`、中程 `[-1,3.1,-195.5]`、深处 `[8,-10,-393]`。看真实 PNG 后才判断效果。

自然导览使用真实按钮、真实经过时间和录像；没有注入时钟或通过测试调用跳站。暂停、重播、转身、前后游动、返回和碰撞另有真实输入证据。390×740 只做触控与减少动态效果模拟，不能作为实体手机性能/触控验收。

第一版的近距离胖鱼、过暗岩面被否决；首次碰撞断言误选空地，后续断言误把原扫描的较早阻挡判作失败。失败证据保留，没有据此修改导航器。最终验证结果和范围以 `evidence/continuous-20261012` 的报告为准。

CPU/static 检查覆盖 149 个基线哈希、145 个未改源/资产、1,440 个导览采样、六站可达、代理阻挡与释放输入。它不替代连续三角面碰撞、视觉验收或浏览器验证。原根站模型测试与旧固定几何预算没有被冒用为新场景通过证据。

## 剩余局限

整体纵深、礁脊接续和生物活动增加，但真实感尚未最终验收。海草叶片、片状/块状群落仍有程序化外观；岩体重复同一许可源，局部有采石层纹；回望原区域仍保留较空的边界。没有声称实地尺度、原位生态、照片级真实感或所有方向都连续饱满。新增几何约 309 万三角形，低端手机性能未测。

本候选供整体效果审查；若目标要求消除上述明显的程序化外观和回望边界，应暂不发布。记录一次明确的整体增量，不把功能通过写成视觉目标完成。

## 许可

新增地景复用 Poly Haven Boulder 01（CC0）：https://polyhaven.com/a/boulder_01 。原作者珊瑚和鱼的程序几何继续归本项目。C1/C4 的 Matan Yuval / Tali Treibitz / Reefs4D、CC BY-NC 2.0 信用与非商业展示边界保留在原入口源码中；Smithsonian CC0 与其他既有引用也保留。没有把陆地岩石声明为真实海底扫描。
