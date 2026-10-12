"""Preserve the original site and first version; freeze 01.1 and the final stage."""
from pathlib import Path,PurePosixPath
import json,os,hashlib,time,urllib.request,urllib.parse,zipfile,tarfile,shutil
workspace=Path(os.environ['GITHUB_WORKSPACE']).resolve()
event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text());inputs=event['inputs'];url=inputs['snapshot_url'];parsed=urllib.parse.urlparse(url)
assert parsed.scheme=='https'and(parsed.hostname.endswith('.blob.core.windows.net')or parsed.hostname.endswith('.actions.githubusercontent.com')),'Unexpected existing artifact host'
print('::add-mask::'+url,flush=True)
expected=inputs['snapshot_digest'].removeprefix('sha256:');assert len(expected)==64
protected=json.loads(inputs['protected_hashes']);assert set(protected)>={'index.html','app.js','preview/world/index.html','preview/world/current-world.json'}
site=workspace/'.published-site';assert site.is_relative_to(workspace)and not site.exists();site.mkdir()
archive=Path(os.environ['RUNNER_TEMP'])/'reef-existing-published.zip';begin=time.monotonic();digest=hashlib.sha256();received=0;nextLog=256*1024*1024
with urllib.request.urlopen(url,timeout=30)as response,archive.open('wb')as out:
 while True:
  block=response.read(1024*1024)
  if not block:break
  out.write(block);digest.update(block);received+=len(block)
  if received>=nextLog:print('PUBLISHED_SNAPSHOT_BYTES',received,flush=True);nextLog+=256*1024*1024
  assert time.monotonic()-begin<480,'Existing snapshot transfer exceeded bounded deadline'
assert digest.hexdigest()==expected,'Existing published artifact digest mismatch'
before={}
with zipfile.ZipFile(archive)as z:
 files=[i for i in z.infolist()if not i.is_dir()];assert len(files)==1 and files[0].filename=='artifact.tar','Unexpected Pages artifact layout'
 with z.open(files[0])as stream,tarfile.open(fileobj=stream,mode='r|*')as tar:
  for member in tar:
   name=PurePosixPath(member.name);assert not name.is_absolute()and'..'not in name.parts
   target=site/name;assert target.resolve().is_relative_to(site)
   if member.isdir():target.mkdir(parents=True,exist_ok=True);continue
   assert member.isreg(),'Only regular published files are supported'
   target.parent.mkdir(parents=True,exist_ok=True);source=tar.extractfile(member);h=hashlib.sha256()
   with target.open('wb')as out:
    while True:
     block=source.read(1024*1024)
     if not block:break
     out.write(block);h.update(block)
   before[name.as_posix()]=h.hexdigest()
for name,h in protected.items():assert before[name]==h,'Snapshot does not match the current public entry '+name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
newRoot=site/'preview/reef-garden-v1';firstRoot=site/'preview/reef-garden-v1-first';v11Root=site/'preview/reef-garden-v11';stageRoot=site/'preview/reef-garden-stage-012'
source=workspace/'dist/preview/reef-garden-v1';frozen=workspace/'dist/preview/reef-garden-v11';stageSource=workspace/'dist/preview/reef-garden-stage-012'
names={'index.html','style.css','app.js','world.js','navigation.js'}
assert source.is_dir()and frozen.is_dir()and stageSource.is_dir()
assert {p.name for p in newRoot.iterdir()}==names and {p.name for p in frozen.iterdir()}==names
assert all(sha(newRoot/name)==sha(frozen/name)for name in names),'Only the exact accepted 01.1 preview may be replaced'
assert all(sha(source/name)==sha(stageSource/name)for name in names),'Stage snapshot must exactly match the verified final source'
assert firstRoot.is_dir()and not v11Root.exists()and not stageRoot.exists(),'Do not overwrite preserved versions'
shutil.copytree(newRoot,v11Root);shutil.copytree(source,stageRoot)
for name in names:shutil.copyfile(source/name,newRoot/name)
prefix='preview/reef-garden-v1/';firstPrefix='preview/reef-garden-v1-first/'
protectedBefore={name:h for name,h in before.items()if not name.startswith(prefix)}
originalBefore={name:h for name,h in protectedBefore.items()if not name.startswith(firstPrefix)}
assert len(protectedBefore)==2309 and len(originalBefore)==2304,'Unexpected existing publication boundary'
oldAggregate=hashlib.sha256(''.join(k+'\0'+originalBefore[k]+'\n'for k in sorted(originalBefore)).encode()).hexdigest()
assert oldAggregate=='01aad68d56b0aeab32c523df6110b002adfc399782722fd75976b105dfeb7461','Original site differs from accepted baseline'
assert all(sha(site/name)==h for name,h in protectedBefore.items()),'An old file or first-version file changed'
assert all(sha(v11Root/name)==before[prefix+name]for name in names),'01.1 archive changed'
new={p.relative_to(site).as_posix():sha(p)for p in newRoot.iterdir()}
receipt={'status':'ORIGINAL_SITE_AND_FIRST_PRESERVED_01_1_FROZEN_STAGE_01_2_PUBLISHED','previousSiteFileCount':len(before),'oldFileCount':len(originalBefore),'oldFilesChanged':0,'preservedExistingFiles':len(protectedBefore),'oldPublishedHashAggregate':oldAggregate,'protectedPublicHashes':protected,'newFiles':new,'frozenV11Files':{p.relative_to(site).as_posix():sha(p)for p in v11Root.iterdir()},'frozenStageFiles':{p.relative_to(site).as_posix():sha(p)for p in stageRoot.iterdir()},'firstVersionFiles':{k:h for k,h in before.items()if k.startswith(firstPrefix)},'firstVersionBytesPreserved':True,'v11BytesPreserved':True,'stageSnapshotMatchesCurrent':True,'entry':'preview/reef-garden-v1/','frozenStageEntry':'preview/reef-garden-stage-012/','artifactDigest':expected,'oldSnapshotBytes':received,'noScanDecoding':True,'worldPointerChanged':False}
(workspace/'publication-receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
