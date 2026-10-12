from pathlib import Path
import json,hashlib,shutil,subprocess,cv2

root=Path(__file__).resolve().parent
art=root/'artifacts/basin-proof';out=root/'evidence/basin-proof'
base='3c00efbec735c7618c842edf3f5a0716e1147323'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
subprocess.run(['git','diff','--exit-code',base,'--','dist','.github/workflows'],cwd=root,check=True)
assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='candidate/reef-basin-proof'
assert subprocess.check_output(['git','rev-parse','reef-garden-01.2-stage^{}'],cwd=root,text=True).strip()==base
assert sha(root/'dist/preview/reef-basin-proof/navigation.js')==sha(root/'dist/preview/reef-garden-stage-012/navigation.js')
out.mkdir(parents=True,exist_ok=True)
for name in ['first-pass','final']:
 src=art/name;dest=out/name;dest.mkdir(exist_ok=True)
 for p in src.iterdir():
  if p.is_file()and p.suffix in ['.png','.json','.webm']:shutil.copyfile(p,dest/p.name)
 if name=='first-pass':shutil.copytree(src/'source',dest/'source',dirs_exist_ok=True)
shutil.copyfile(art/'cpu.json',out/'cpu.json')
final=read(out/'final/verification.json');first=read(out/'first-pass/verification.json')
assert first['technicalStatus']==final['technicalStatus']=='PASS'
for name,h in final['sourceHashes'].items():assert sha(root/'dist/preview/reef-basin-proof'/name)==h
assert final['positionInjectionDuringProof']is False and final['recordingUncut']is True
video=out/'final/uncut-proof.webm';capture=cv2.VideoCapture(str(video))
assert capture.isOpened()
fps=capture.get(cv2.CAP_PROP_FPS);count=capture.get(cv2.CAP_PROP_FRAME_COUNT);duration=count/fps
raw=out/'final/raw-video-frames';raw.mkdir(exist_ok=True)
for sec in [19,20,21,37,38,39]:
 capture.set(cv2.CAP_PROP_POS_MSEC,sec*1000);ok,frame=capture.read();assert ok
 assert cv2.imwrite(str(raw/f'{sec:02d}s.png'),frame)
capture.release()
report={
 'status':'VISUAL_GOAL_FAILED_STOPPED_UNPUBLISHED','sourceBranch':'candidate/reef-basin-proof','baseCommit':base,
 'visualCorrectionsUsed':1,'furtherVisualChangesStopped':True,'publicationPerformed':False,
 'scope':'One continuous reef-basin proof only; no six-station expansion, new assets, paid service, permissions, credentials or security changes.',
 'visualGates':[
  {'gate':'Still a pedestal/display scene?','result':'FAIL','evidence':['final/00-start-front.png','final/02-180-return-view.png','final/05-panorama-quarter-2.png'],'reason':'Grounding improved, but broad smooth elongated reef platforms and attached spherical/paper-like props still dominate.'},
  {'gate':'Does turning expose an empty scene?','result':'FAIL','evidence':['final/06-panorama-quarter-3.png'],'reason':'The southern direction still exposes a wide sparsely populated sand corridor and uniform empty water.'},
  {'gate':'Do near/mid/far layers persist throughout motion?','result':'FAIL','evidence':['final/01-advance-near-mid-far.png','final/04-panorama-quarter-1.png','final/08-return-through-same-world.png'],'reason':'Some views contain three physical distances, but close broad slopes hide depth in others and remote silhouettes remain flat; meaningful layers do not persist.'}
 ],
 'technicalStatus':'PASS_WITH_LIMITED_SCOPE','proofMovementSeconds':final['final']['guide']['elapsed'],
 'proofWallSeconds':final['proofWallSeconds'],'video':{'path':'final/uncut-proof.webm','sha256':sha(video),'bytes':video.stat().st_size,'durationSeconds':duration,'fps':fps,'frames':count,'uncut':True,'includesLoading':True},
 'firstVideo':{'path':'first-pass/uncut-proof.webm','sha256':sha(out/'first-pass/uncut-proof.webm')},
 'pixelReview':{'screenshots':'All ten final actual render images; first actual entrance/return/side images.','rawVideoSeconds':[19,20,21,37,38,39],'method':'Native browser recording preserved whole; adjacent frames decoded without enhancement. Not a claim to have watched every encoded frame or audited audio.'},
 'passed':['Scene construction and bounded geometry budget','Proof points remain open under existing collision proxies','61-degree FOV throughout the proof','Advance, 180-degree look back, lateral travel, 360-degree look around and actual return within 0.7m of the start','No position injection during proof','No WebGL/JavaScript/console/request errors','Old tracked dist files and workflows identical to the base; 01.2 tag and navigation source preserved'],
 'notTested':['Manual pause/resume/replay and free-controls regression outside the recorded proof','Exact geometric ledge collision and general exploration routes','Physical mobile and multitouch','RTX4070 and other GPU/device performance','Six-station tour and online publication'],
 'performance':{'gpu':final['gpu'],'viewport':[1280,820],'loadSeconds':final['loadSeconds'],**final['recordedPerformance']},
 'remaining':['The overall visual target is not reached; no publication is proposed.','Rounded massing, sparse coral attachment, flat fish/manta silhouettes and patterned sand remain visible.','Collision proxies are simplified and not an acceptance of geometric collision.'],
 'runtimeSourceHashes':final['sourceHashes'],'preservation':{'baselineCommit':base,'oldTrackedDistBytesChanged':0,'workflowsChanged':False,'tagRepointed':False,'onlinePointerChanged':False},
 'blockers':[]
}
(out/'ASSESSMENT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
manifest={p.relative_to(out).as_posix():sha(p)for p in out.rglob('*')if p.is_file()and p.name!='SHA256.json'}
(out/'SHA256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'status':report['status'],'proofSeconds':report['proofMovementSeconds'],'videoSeconds':duration,'videoBytes':video.stat().st_size,'runtimeHashesConfirmed':True,'oldTrackedDistBytesChanged':0}))
