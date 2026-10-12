from pathlib import Path
import json,hashlib,shutil,zipfile,difflib
root=Path(__file__).resolve().parent
evidence=root/'evidence/continuous-20261012';evidence.mkdir(parents=True,exist_ok=True)
for variant,label in [('enriched-baseline','baseline'),('continuous-candidate','candidate')]:
 src=root/'artifacts'/('render-'+variant)
 for name in ['entry','mid','deep']:shutil.copyfile(src/(name+'.png'),evidence/(label+'-'+name+'.png'))
 shutil.copyfile(src/'fixed-views.json',evidence/(label+'-fixed-views.json'))
motion=root/'artifacts/continuous-motion';r=json.loads((motion/'verification.json').read_text(encoding='utf-8'));assert r['status']=='PASS'
shutil.copyfile(motion/'verification.json',evidence/'native-verification.json')
shutil.copyfile(root/r['video'],evidence/'native-tour.webm')
for name in ['tour-near-moving','tour-mid-moving','tour-deep-moving','tour-completed','turned-back','reef-collision','mobile-390']:shutil.copyfile(motion/(name+'.png'),evidence/(name+'.png'))
for src,target in [('artifacts/enriched-recovery.json','enriched-source-recovery.json'),('artifacts/continuous-build.json','candidate-source-build.json'),('artifacts/continuous-contract-test.json','cpu-static-verification.json'),('artifacts/native-run1-preserved/verification.json','native-run1-failed.json'),('artifacts/compat-run2-preserved/verification.json','compat-run2-failed.json')]:shutil.copyfile(root/src,evidence/target)
patch=[]
for name in ['exploration-world-data.js','exploration-world.js','scan-exhibit.js','scan-ocean.js']:
 before=(root/'artifacts/enriched-baseline'/name).read_text(encoding='utf-8').splitlines(keepends=True)
 after=(root/'artifacts/continuous-candidate'/name).read_text(encoding='utf-8').splitlines(keepends=True)
 patch.extend(difflib.unified_diff(before,after,fromfile='enriched-baseline/'+name,tofile='continuous-candidate/'+name))
(evidence/'enriched-candidate.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
manifest={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in evidence.iterdir()if p.is_file() and p.name!='DELIVERY-MANIFEST.json'}
(evidence/'DELIVERY-MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>连续海域候选 · 实际证据</title><style>body{margin:0;padding:28px;background:#091e27;color:#def0ec;font:16px/1.65 system-ui}main{max-width:1300px;margin:auto}h1{font-size:30px}p{max-width:900px}section{margin:34px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}img,video{width:100%;border-radius:12px}figcaption{padding:8px 0;color:#a3c8c3}a{color:#bbddcf}button{background:#bbddcf;color:#12333c;border:0;border-radius:6px;padding:10px 16px;margin:8px}footer{color:#a3c8c3}@media(max-width:700px){body{padding:16px}.pair{grid-template-columns:1fr}}</style><main><h1>连续海域候选：看真实渲染</h1><p>这是本机 Chrome / Intel UHD 的实际 PNG 和原速录像。三个固定视角保持相同相机、同样视口。独立候选未覆盖线上入口，真实感仍待最终审查。</p><p><a href="../../artifacts/continuous-candidate/scan-exhibit.html">进入本地可漫游候选</a> · <a href="native-verification.json">浏览器核验报告</a> · <a href="../../CONTINUOUS_CANDIDATE.md">源码、范围与局限</a></p>'''
for name,label in [('entry','入口'),('mid','海草湾中程'),('deep','深水边缘')]:
 html+=f'<section><h2>{label}</h2><div class="pair"><figure><img src="baseline-{name}.png"><figcaption>稳定 enriched 原始渲染</figcaption></figure><figure><img src="candidate-{name}.png"><figcaption>连续礁脊候选</figcaption></figure></div></section>'
html+='''<section><h2>真实自然导览与自由操作</h2><p>从实际加载、按钮启动到 72 秒完成，随后重播暂停、转身、返回和碰撞。没有快进、注入时钟或跳站。窄屏另外核验。</p><video src="native-tour.webm" controls preload="metadata"></video><button onclick="document.querySelector('video').currentTime+=15">前进 15 秒</button><button onclick="document.querySelector('video').currentTime=Math.max(0,document.querySelector('video').currentTime-15)">返回 15 秒</button></section><section><h2>移动端模拟与限制</h2><img style="max-width:390px" src="mobile-390.png"><p>390×740、触控和减少动态效果模拟通过。尚未测试实体手机性能。海草和部分群落仍明显程序化，岩体复用同一许可源；回望原区域的空边界仍在。本候选有整体纵深增量，但不能把功能通过当作最终真实感验收。</p></section><footer><p>新地景：Poly Haven Boulder 01 / CC0；原作者珊瑚与鱼；原 C1/C4：Matan Yuval / Tali Treibitz / Reefs4D，CC BY-NC 2.0。全部为人工组成的示意海域，不是实地测绘还原。</p></footer></main></html>'''
(evidence/'review.html').write_text(html,encoding='utf-8')
archive=root/'artifacts/azure-reef-continuous-candidate-20261012-SOURCE.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
 for p in (root/'artifacts/continuous-candidate').rglob('*'):
  if p.is_file():z.write(p,'page/'+p.relative_to(root/'artifacts/continuous-candidate').as_posix())
 z.write(root/'CONTINUOUS_CANDIDATE.md','CONTINUOUS_CANDIDATE.md');z.write(root/'THIRD_PARTY_NOTICES.md','THIRD_PARTY_NOTICES.md');z.write(root/'artifacts/continuous-build.json','BUILD.json');z.write(root/'artifacts/enriched-recovery.json','BASELINE-RECOVERY.json')
summary={'sourceArchive':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'runtimeChanges':6,'baselineAssetsUnchanged':True,'browserStatus':r['status'],'checks':list(r['checks']),'performance':r['performance'],'publicSiteChanged':False,'visualFinalAcceptance':False,'visualDecision':'整体纵深和群落增量可审查；程序化外观与回望原边界仍未达到最终真实感目标，不建议直接覆盖稳定入口。'}
(evidence/'DELIVERY-SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summary,ensure_ascii=False))
