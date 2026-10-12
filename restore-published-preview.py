"""Keep the old site byte-identical; freeze V1 before updating its isolated preview."""
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
newRoot=site/'preview/reef-garden-v1';firstRoot=site/'preview/reef-garden-v1-first'
source=workspace/'dist/preview/reef-garden-v1';frozen=workspace/'dist/preview/reef-garden-v1-first';assert source.is_dir()and frozen.is_dir()
names={'index.html','style.css','app.js','world.js','navigation.js'}
assert {p.name for p in newRoot.iterdir()}==names and {p.name for p in frozen.iterdir()}==names
assert all(sha(newRoot/name)==sha(frozen/name)for name in names),'Only the exact verified first version may be replaced'
assert not firstRoot.exists(),'Frozen first version already exists; review before replacing anything'
shutil.copytree(newRoot,firstRoot)
for name in names:shutil.copyfile(source/name,newRoot/name)
prefix='preview/reef-garden-v1/'
protectedBefore={name:h for name,h in before.items()if not name.startswith(prefix)}
assert len(protectedBefore)==2304,'Unexpected original published-site boundary'
oldAggregate=hashlib.sha256(''.join(k+'\0'+protectedBefore[k]+'\n'for k in sorted(protectedBefore)).encode()).hexdigest()
assert oldAggregate=='01aad68d56b0aeab32c523df6110b002adfc399782722fd75976b105dfeb7461','Original publication no longer matches its accepted baseline'
assert all(sha(site/name)==h for name,h in protectedBefore.items()),'An original published file changed'
assert all(sha(firstRoot/name)==before[prefix+name]for name in names),'Frozen first-version bytes changed'
new={p.relative_to(site).as_posix():sha(p)for p in newRoot.rglob('*')if p.is_file()}
receipt={'status':'ORIGINAL_SITE_PRESERVED_FIRST_VERSION_FROZEN_PREVIEW_UPDATED','previousSiteFileCount':len(before),'oldFileCount':len(protectedBefore),'oldFilesChanged':0,'oldPublishedHashAggregate':hashlib.sha256(''.join(k+'\0'+protectedBefore[k]+'\n'for k in sorted(protectedBefore)).encode()).hexdigest(),'protectedPublicHashes':protected,'newFiles':new,'frozenFirstVersionFiles':{p.relative_to(site).as_posix():sha(p)for p in firstRoot.iterdir()},'updatedPreviewFiles':len(new),'frozenFirstVersionMatchesPrevious':True,'entry':'preview/reef-garden-v1/','artifactDigest':expected,'oldSnapshotBytes':received,'noScanDecoding':True,'worldPointerChanged':False}
(workspace/'publication-receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
