from pathlib import Path
import json,hashlib,shutil,zipfile,subprocess
root=Path(__file__).resolve().parent;out=root/'evidence/composition-20261012';out.mkdir(parents=True,exist_ok=True)
inspection=root/'artifacts/composition-inspection'
for p in inspection.iterdir():
 if p.is_file():shutil.copyfile(p,out/p.name)
for src,dst in [('artifacts/enriched-recovery.json','enriched-source-contract.json'),('artifacts/composition-build.json','composition-source-build.json'),('artifacts/composition-contract-test.json','cpu-static-verification.json')]:shutil.copyfile(root/src,out/dst)
for name in ['entry','mid','deep']:shutil.copyfile(root/'evidence/continuous-20261012'/('candidate-'+name+'.png'),out/('b92b8ac-'+name+'.png'))
failure={'status':'BLOCKED_BEFORE_VISUAL_GATE','implementationComplete':True,'runtimePixelVerification':False,'affectedOperationRegressionRun':False,'newVideoRecorded':False,'firstAttempt':{'waitUntil':'domcontentloaded','timeoutMs':30000,'error':'Page.goto: Timeout 30000ms exceeded. http://127.0.0.1:63577/artifacts/composition-candidate/scan-exhibit.html'},'singleShortRetry':{'localDocumentReadBytes':12124,'localReadTimeoutMs':3000,'waitUntil':'commit','timeoutMs':15000,'error':'Page.goto: Timeout 15000ms exceeded. http://127.0.0.1:56398/artifacts/composition-candidate/scan-exhibit.html'},'processesEnded':True,'furtherRenderRetries':0,'networkOrSecuritySettingsChanged':False,'lastSuccessfulReadUtc':'2026-10-12 04:14:33','baselineFilesVerified':149,'staticTourSamplesPassed':1440,'formationCountBefore':17,'formationCountAfter':17,'fishCountBefore':286,'fishCountAfter':286,'waterTransmissionCoefficientsChanged':False,'visualClaims':['Only the original b92b8ac alpha-plane hide comparison has real pixels; it supports the horizontal-step cause.','The new staggered formations and rear seabed extension remain visually unverified.'],'publishDecision':'Do not publish or replace the stable entry until the six requested views and affected native movements have actual rendering evidence.'}
(out/'render-blocker.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2),encoding='utf-8')
build=json.loads((out/'composition-source-build.json').read_text(encoding='utf-8'))
delta=root/'artifacts/composition-preview-delta.zip'
with zipfile.ZipFile(delta,'w',zipfile.ZIP_DEFLATED) as z:
 for name,digest in build['changes'].items():
  p=root/'artifacts/composition-candidate'/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==digest;z.write(p,name)
 z.writestr('COMPOSITION-MANIFEST.json',json.dumps(build,indent=2))
shutil.copyfile(delta,out/'composition-preview-delta.zip')
receipt={'file':delta.name,'bytes':delta.stat().st_size,'sha256':hashlib.sha256(delta.read_bytes()).hexdigest(),'sourceFiles':list(build['changes']),'publicationBase':'a1b2cae7e968ad383798a0ff15c87bfb0934d971','previousCandidate':'b92b8ac734973e2673f3f678f6d5f1241393373c','status':failure['status'],'candidatePath':'preview/composition-candidate','candidateEntry':'preview/composition-candidate/scan-exhibit.html','visualVerified':False}
(out/'DELIVERY.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt))
