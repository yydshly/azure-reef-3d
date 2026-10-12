"""Preserve every previously published byte and append the original V1 only."""
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
newRoot=site/'preview/reef-garden-v1';assert not newRoot.exists(),'Do not overwrite a prior publication'
source=workspace/'dist/preview/reef-garden-v1';assert source.is_dir();shutil.copytree(source,newRoot)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(site/name)==h for name,h in before.items()),'An old published file changed'
new={p.relative_to(site).as_posix():sha(p)for p in newRoot.rglob('*')if p.is_file()}
receipt={'status':'PRESERVED_SITE_PLUS_ISOLATED_PREVIEW','oldFileCount':len(before),'oldFilesChanged':0,'oldPublishedHashAggregate':hashlib.sha256(''.join(k+'\0'+before[k]+'\n'for k in sorted(before)).encode()).hexdigest(),'protectedPublicHashes':protected,'newFiles':new,'entry':'preview/reef-garden-v1/','artifactDigest':expected,'oldSnapshotBytes':received,'noScanDecoding':True,'worldPointerChanged':False}
(workspace/'publication-receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
