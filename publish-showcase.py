"""Restore a pinned published snapshot, preserving every file except its root HTML."""
from pathlib import Path,PurePosixPath
import hashlib,json,os,re,shutil,tarfile,time,urllib.parse,urllib.request,zipfile

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def unpack(archive,site):
    before={}
    with zipfile.ZipFile(archive) as z:
        files=[i for i in z.infolist() if not i.is_dir()]
        assert len(files)==1 and files[0].filename=='artifact.tar','Unexpected Pages artifact layout'
        with z.open(files[0]) as stream,tarfile.open(fileobj=stream,mode='r|*') as tar:
            for member in tar:
                name=PurePosixPath(member.name)
                assert not name.is_absolute() and '..' not in name.parts,'Unsafe snapshot path'
                target=site/name;assert target.resolve().is_relative_to(site)
                if member.isdir():target.mkdir(parents=True,exist_ok=True);continue
                assert member.isreg(),'Snapshot links and special files are unsupported'
                assert name.as_posix() not in before,'Duplicate published path'
                target.parent.mkdir(parents=True,exist_ok=True)
                with tar.extractfile(member) as source,target.open('wb') as out:shutil.copyfileobj(source,out,1024*1024)
                before[name.as_posix()]=sha(target)
    return before

def overlay(workspace,site,before,protected):
    for name,h in protected.items():assert before.get(name)==h,'Snapshot/current public mismatch: '+name
    assert 'legacy.html' not in before and not any(n.startswith('showcase/') for n in before),'Do not overwrite an existing showcase'
    assert sha(workspace/'dist/legacy.html')==before['index.html'],'Committed legacy HTML must equal the previous public root'
    shutil.copyfile(site/'index.html',site/'legacy.html')
    shutil.copyfile(workspace/'dist/index.html',site/'index.html')
    shutil.copytree(workspace/'dist/showcase',site/'showcase')
    preserved={n:h for n,h in before.items() if n!='index.html'}
    assert all(sha(site/n)==h for n,h in preserved.items()),'An existing asset or preview changed'
    assert sha(site/'legacy.html')==before['index.html'],'Original homepage not preserved'
    aggregate=lambda values:hashlib.sha256(''.join(k+'\0'+values[k]+'\n' for k in sorted(values)).encode()).hexdigest()
    return {'status':'UNIFIED_HOMEPAGE_PUBLISHED_ALL_PREVIOUS_ASSETS_AND_PREVIEWS_PRESERVED','previousSiteFileCount':len(before),'preservedExistingFiles':len(preserved),'existingFilesChanged':['index.html'],'previousRootSha256':before['index.html'],'legacyRootSha256':sha(site/'legacy.html'),'newRootSha256':sha(site/'index.html'),'preservedHashAggregate':aggregate(preserved),'previewFileCount':sum(n.startswith('preview/') for n in before),'previewFilesChanged':0,'worldPointerChanged':False,'legacyEntry':'legacy.html','newEntry':'index.html','protectedPublicHashes':protected,'newShowcaseFiles':{p.relative_to(site).as_posix():sha(p) for p in (site/'showcase').rglob('*') if p.is_file()},'scanDecoding':False}

def main():
    workspace=Path(os.environ['GITHUB_WORKSPACE']).resolve();inputs=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())['inputs']
    url=inputs['snapshot_url'];parsed=urllib.parse.urlparse(url)
    assert parsed.scheme=='https' and parsed.hostname and (parsed.hostname.endswith('.blob.core.windows.net') or parsed.hostname.endswith('.actions.githubusercontent.com')),'Unexpected artifact host'
    print('::add-mask::'+url,flush=True)
    expected=inputs['snapshot_digest'].removeprefix('sha256:');assert re.fullmatch('[a-f0-9]{64}',expected)
    protected=json.loads(inputs['protected_hashes']);assert set(protected)>={'index.html','app.js','preview/world/index.html','preview/world/current-world.json','preview/reef-garden-stage-012/index.html'}
    site=workspace/'.published-site';assert not site.exists();site.mkdir()
    archive=Path(os.environ['RUNNER_TEMP'])/'existing-published.zip';begin=time.monotonic();digest=hashlib.sha256();received=0;next_log=256*1024*1024
    with urllib.request.urlopen(url,timeout=30) as response,archive.open('wb') as out:
        while True:
            block=response.read(1024*1024)
            if not block:break
            out.write(block);digest.update(block);received+=len(block)
            if received>=next_log:print('PRESERVED_SNAPSHOT_BYTES',received,flush=True);next_log+=256*1024*1024
            assert time.monotonic()-begin<480,'Snapshot transfer exceeded bounded deadline'
    assert digest.hexdigest()==expected,'Published artifact digest mismatch'
    before=unpack(archive,site);assert len(before)==2324,'Unexpected pinned publication file count'
    receipt=overlay(workspace,site,before,protected)
    receipt.update(snapshotArtifactId=11733044606,snapshotRun=38220531117,snapshotDigest=expected,snapshotBytes=received,sourceCommit=os.environ['GITHUB_SHA'])
    (workspace/'publication-receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['newShowcaseFiles','protectedPublicHashes']}),flush=True)
if __name__=='__main__':main()
