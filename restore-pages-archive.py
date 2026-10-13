"""Restore the exact Pages ZIP and site files from persistent Release byte slices.

Python 3.10+ standard library only. No artifact endpoint, credentials, software
installation or deployment is involved. Outputs must not already exist.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,os,re,tarfile,urllib.parse,urllib.request,zipfile

BLOCK=1024*1024
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(BLOCK),b''):h.update(b)
    return h.hexdigest()

def fs(path):
    value=str(Path(path).resolve())
    return '\\\\?\\'+value if os.name=='nt' and not value.startswith('\\\\?\\') else value

def safe_relative(name):
    p=PurePosixPath(name)
    assert not p.is_absolute() and '..' not in p.parts and '\\' not in name,name
    assert p.parts and ':' not in name,name
    return p

def load_manifest(path,expected_sha256=None):
    path=Path(path).resolve();raw=path.read_bytes()
    if expected_sha256:assert hashlib.sha256(raw).hexdigest()==expected_sha256,'Archive manifest SHA256 differs'
    m=json.loads(raw);assert m['format']=='azure-reef-pages-split-v1'
    assert re.fullmatch('[a-f0-9]{64}',m['source']['sha256'])
    assert len(m['parts'])<=1000 and sum(p['bytes'] for p in m['parts'])==m['source']['bytes']
    assert len({p['name'] for p in m['parts']})==len(m['parts'])
    for p in m['parts']:
        assert safe_relative(p['name']).name==p['name'] and re.fullmatch('[a-f0-9]{64}',p['sha256'])
        assert 0<p['bytes']<2*1024**3
    assert safe_relative(m['siteManifest']).name==m['siteManifest']
    return m

def download_parts(manifest,manifest_url):
    """Public same-repository download for a future Pages preparation."""
    manifest=Path(manifest).resolve();m=load_manifest(manifest);parsed=urllib.parse.urlparse(manifest_url)
    assert parsed.scheme=='https' and parsed.hostname=='github.com'
    assert parsed.path.startswith('/yydshly/azure-reef-3d/releases/download/') and not parsed.query
    base=manifest_url.rsplit('/',1)[0]+'/'
    records=m['parts']+[{'name':m['siteManifest'],'sha256':m['siteManifestSha256']}]
    for record in records:
        target=manifest.parent/record['name'];assert not target.exists()
        url=base+urllib.parse.quote(record['name'],safe='');h=hashlib.sha256();received=0
        with urllib.request.urlopen(url,timeout=30) as response,target.open('xb') as out:
            for block in iter(lambda:response.read(BLOCK),b''):
                out.write(block);h.update(block);received+=len(block)
                if received%(128*BLOCK)==0:print('PERSISTENT_RELEASE_BYTES',record['name'],received,flush=True)
        assert h.hexdigest()==record['sha256'] and ('bytes' not in record or received==record['bytes'])

def restore(manifest,output,site_dir=None,expected_manifest_sha256=None):
    manifest=Path(manifest).resolve();output=Path(output).resolve();m=load_manifest(manifest,expected_manifest_sha256)
    files_raw=(manifest.parent/m['siteManifest']).read_bytes()
    assert hashlib.sha256(files_raw).hexdigest()==m['siteManifestSha256']
    files=json.loads(files_raw)
    assert len(files)==m['siteFileCount'] and len({v['path'] for v in files})==len(files)
    assert not output.exists(),'Refusing to overwrite an existing ZIP'
    output.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();written=0
    with open(fs(output),'xb') as out:
        for part in m['parts']:
            source=manifest.parent/part['name'];bh=hashlib.sha256();length=0
            with open(fs(source),'rb') as f:
                for b in iter(lambda:f.read(BLOCK),b''):
                    out.write(b);h.update(b);bh.update(b);length+=len(b);written+=len(b)
            assert length==part['bytes'] and bh.hexdigest()==part['sha256'],part['name']
            print('RESTORED_SOURCE_BYTES',written,flush=True)
    assert written==m['source']['bytes'] and h.hexdigest()==m['source']['sha256'],'Exact source artifact differs'
    result={'status':'EXACT_SOURCE_ARTIFACT_RESTORED','manifestSha256':sha(fs(manifest)),
            'sourceZipSha256':h.hexdigest(),'sourceZipBytes':written,'siteFileCount':len(files)}
    if site_dir:
        root=Path(site_dir).resolve();assert not root.exists(),'Refusing to overwrite an existing site directory'
        root.mkdir(parents=True);expected={v['path']:v for v in files};seen={}
        with zipfile.ZipFile(fs(output)) as z:
            entries=z.infolist();assert len(entries)==1 and entries[0].filename=='artifact.tar'
            with z.open(entries[0]) as stream,tarfile.open(fileobj=stream,mode='r|*') as tar:
                for member in tar:
                    if member.isdir() and member.name in ['.','./','']:continue
                    relative=safe_relative(member.name);name=relative.as_posix();target=(root/relative).resolve()
                    assert target.is_relative_to(root)
                    if member.isdir():os.makedirs(fs(target),exist_ok=True);continue
                    assert member.isreg() and name in expected and name not in seen,name
                    assert member.size==expected[name]['bytes']
                    os.makedirs(fs(target.parent),exist_ok=True);fh=hashlib.sha256();length=0
                    with tar.extractfile(member) as source,open(fs(target),'xb') as out:
                        for b in iter(lambda:source.read(BLOCK),b''):out.write(b);fh.update(b);length+=len(b)
                    assert length==member.size and fh.hexdigest()==expected[name]['sha256'],name
                    seen[name]=fh.hexdigest()
        assert set(seen)==set(expected),'Site file inventory differs'
        aggregate=hashlib.sha256(''.join(k+'\0'+seen[k]+'\n' for k in sorted(seen)).encode()).hexdigest()
        assert aggregate==m['siteHashAggregate']
        result.update(status='EXACT_ARTIFACT_AND_ALL_SITE_FILES_RESTORED',restoredFiles=len(seen),siteHashAggregate=aggregate)
    print(json.dumps(result),flush=True);return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--site-dir',type=Path);p.add_argument('--expected-manifest-sha256');p.add_argument('--receipt',type=Path)
    a=p.parse_args();r=restore(a.manifest,a.output,a.site_dir,a.expected_manifest_sha256)
    if a.receipt:a.receipt.write_text(json.dumps(r,indent=2)+'\n','utf8')
