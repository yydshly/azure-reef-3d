"""Append restored experiments to the latest site, preserving all old scenes."""
from pathlib import Path
import hashlib,json,os,re,shutil,time,urllib.parse,urllib.request
from publish_showcase_import import sha,unpack

def main():
    workspace=Path(os.environ['GITHUB_WORKSPACE']).resolve();inputs=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())['inputs']
    url=inputs['snapshot_url'];parsed=urllib.parse.urlparse(url)
    assert parsed.scheme=='https' and parsed.hostname and (parsed.hostname.endswith('.blob.core.windows.net') or parsed.hostname.endswith('.actions.githubusercontent.com'))
    print('::add-mask::'+url,flush=True)
    expected=inputs['snapshot_digest'].removeprefix('sha256:');assert re.fullmatch('[a-f0-9]{64}',expected)
    protected=json.loads(inputs['protected_hashes']);manifest=json.loads((workspace/'history-release.json').read_text())
    site=workspace/'.published-site';assert not site.exists();site.mkdir();archive=Path(os.environ['RUNNER_TEMP'])/'existing-published.zip'
    start=time.monotonic();digest=hashlib.sha256();received=0;next_log=256*1024*1024
    with urllib.request.urlopen(url,timeout=30) as response,archive.open('wb') as out:
        while True:
            block=response.read(1024*1024)
            if not block:break
            out.write(block);digest.update(block);received+=len(block)
            if received>=next_log:print('PRESERVED_SNAPSHOT_BYTES',received,flush=True);next_log+=256*1024*1024
            assert time.monotonic()-start<480
    assert digest.hexdigest()==expected,'Latest published snapshot digest mismatch'
    before=unpack(archive,site)
    for name,h in protected.items():assert before.get(name)==h,'Current public hash mismatch: '+name
    assert sha(workspace/'dist/legacy.html')==before['legacy.html'],'Legacy entry must stay unchanged'
    added=[]
    for scene in manifest['scenes']:
        target=site/scene['path']
        if target.exists():
            assert all(before.get(scene['path']+'/'+name)==h for name,h in scene['overlayHashes'].items()),'An existing experiment differs from its frozen source'
            assert len([p for p in target.rglob('*') if p.is_file()])==scene['sourceFiles']
            continue
        if scene['base']=='@original-root':
            target.mkdir(parents=True)
            for name in before:
                if name.startswith(('preview/','showcase/')) or name in ['index.html','legacy.html']:continue
                dest=target/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(site/name,dest)
            shutil.copyfile(site/'legacy.html',target/'index.html')
        elif scene['base']:
            baseline=site/scene['base']
            for name,h in manifest['baseHashes'].items():assert before.get(scene['base']+'/'+name)==h,'Pinned enriched source differs: '+name
            target.mkdir(parents=True)
            for name in manifest['baseHashes']:
                dest=target/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(baseline/name,dest)
        else:target.mkdir(parents=True)
        for name,h in scene['overlayHashes'].items():
            source=workspace/'dist'/scene['path']/name;assert sha(source)==h
            dest=target/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        assert len([p for p in target.rglob('*') if p.is_file()])==scene['sourceFiles']
        added.append({'id':scene['id'],'entry':scene['path']+'/'+scene['entry'],'sourceCommit':scene['sourceCommit'],'files':scene['sourceFiles']})
    mutable={'index.html','showcase/app.js','showcase/style.css','showcase/versions.json','showcase/media/sources.json'}
    shutil.copyfile(workspace/'dist/index.html',site/'index.html')
    for source in (workspace/'dist/showcase').rglob('*'):
        if source.is_file():dest=site/source.relative_to(workspace/'dist');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    preserved={n:h for n,h in before.items() if n not in mutable}
    assert all(sha(site/n)==h for n,h in preserved.items()),'Existing scene/resource changed'
    assert all(sha(site/n)==h for n,h in before.items() if n.startswith('preview/'))
    aggregate=hashlib.sha256(''.join(k+'\0'+preserved[k]+'\n' for k in sorted(preserved)).encode()).hexdigest()
    receipt={'status':'HISTORICAL_EXPERIMENTS_APPENDED_ALL_OLD_SCENES_PRESERVED','sourceCommit':os.environ['GITHUB_SHA'],'previousSiteFileCount':len(before),'preservedExistingFiles':len(preserved),'preservedHashAggregate':aggregate,'previewFileCount':sum(n.startswith('preview/') for n in before),'previewFilesChanged':0,'worldPointerChanged':False,'legacyRootSha256':sha(site/'legacy.html'),'allowedChangedFiles':sorted(mutable),'addedScenes':added,'snapshotDigest':expected,'snapshotBytes':received,'previousPreviewEntrypoints':sorted(n for n in before if n.startswith('preview/') and (n.endswith('/index.html') or n.endswith('/scan-exhibit.html'))),'newRootSha256':sha(site/'index.html'),'newShowcaseFiles':{p.relative_to(site).as_posix():sha(p) for p in (site/'showcase').rglob('*') if p.is_file()}}
    (workspace/'publication-receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps({k:v for k,v in receipt.items() if k not in ['newShowcaseFiles','previousPreviewEntrypoints']}),flush=True)
if __name__=='__main__':main()
