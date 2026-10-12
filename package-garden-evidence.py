from pathlib import Path
import json,hashlib,shutil
root=Path(__file__).resolve().parent;out=root/'evidence/reef-garden-v1';out.mkdir(parents=True,exist_ok=True)
qa=root/'artifacts/garden-qa';final=json.loads((qa/'FINAL.json').read_text(encoding='utf-8'));assert final['status']=='PASS'
for src,dst in [('FINAL.json','verification.json'),('native-tour-first.json','first-run-preserved.json'),('compat.json','collision-touch-retest.json'),('cpu.json','cpu.json')]:shutil.copyfile(qa/src,out/dst)
shutil.copyfile(root/final['video'],out/'natural-tour.webm')
for name in ['tour-portal','tour-meadow','tour-moon-arc','tour-completed','free-through-portal','portal-collision','mobile-390']:
 p=qa/(name+'.png')
 if p.is_file():shutil.copyfile(p,out/p.name)
manifest={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in out.iterdir()if p.is_file()and p.name!='MANIFEST.json'};(out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'status':final['status'],'naturalSeconds':final['nativeTourSeconds'],'videoBytes':(out/'natural-tour.webm').stat().st_size,'evidenceFiles':len(manifest)}))
