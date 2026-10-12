"""Recover the exact 149-source enriched baseline from pinned repository objects.

This reads existing archives only; every installed byte is checked against the
published enriched contract. It leaves dist and all archive inputs unchanged.
"""
from pathlib import Path, PurePosixPath
import subprocess, zipfile, hashlib, json, io, urllib.request
root=Path(__file__).resolve().parent
ref='acd6b3f9f287b8fa5b8e07e4ffddf3491668c92b'
contract=json.loads((root.parent/'enriched-inputs/tools/enriched-contract.json').read_text(encoding='utf-8'))
target=root/'artifacts/enriched-baseline'
target.mkdir(parents=True,exist_ok=True)
wanted=contract['sourceHashes']
remaining=set(wanted)
provenance={}
by_hash={}
for name,digest in wanted.items():by_hash.setdefault(digest,[]).append(name)
def accept(data,source):
    digest=hashlib.sha256(data).hexdigest()
    for name in by_hash.get(digest,[]):
        if name in remaining:
            p=target/PurePosixPath(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            remaining.remove(name);provenance[name]=source
for name in wanted:
    p=target/PurePosixPath(name)
    if p.is_file():accept(p.read_bytes(),'previous verified repository recovery')
for p in (root/'dist').rglob('*'):
    if p.is_file(): accept(p.read_bytes(),'a1b2cae7:dist/'+p.relative_to(root/'dist').as_posix())
for gitref in ['a1b2cae7e968ad383798a0ff15c87bfb0934d971',ref]:
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',gitref],cwd=root,text=True).splitlines()
    for name in names:
        if PurePosixPath(name).name in {PurePosixPath(n).name for n in remaining}:
            accept(subprocess.check_output(['git','show',gitref+':'+name],cwd=root),gitref+':'+name)
archives=subprocess.check_output(['git','ls-tree','--name-only',ref],cwd=root,text=True).splitlines()
archives=[n for n in archives if n.endswith('.zip')]
archives.sort(key=lambda n:(0 if n.startswith('exploration-enriched') else 1 if n.startswith('exploration-demo-code') else 2 if n.startswith('grounded-code') else 3 if n.startswith('rear-layout-code') else 4,n))
for archive in archives:
    if not remaining:break
    needed_basenames={PurePosixPath(n).name for n in remaining}
    data=subprocess.check_output(['git','show',ref+':'+archive],cwd=root)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for member in z.infolist():
            if PurePosixPath(member.filename).name in needed_basenames and not member.is_dir():accept(z.read(member),ref+':'+archive+':'+member.filename)
    print('READ',archive,'remaining',len(remaining),flush=True)
for name in list(remaining):
    url='https://yydshly.github.io/azure-reef-3d/'+contract['candidatePath']+'/'+name
    data=urllib.request.urlopen(url,timeout=30).read()
    assert hashlib.sha256(data).hexdigest()==wanted[name], 'Published source mismatch '+name
    accept(data,'verified published '+url)
if remaining: raise RuntimeError('Missing exact source bytes: '+repr(sorted(remaining)))
assert len(provenance)==149
proof={'publicationCommit':'a1b2cae7e968ad383798a0ff15c87bfb0934d971','archiveCommit':ref,'sourceHashes':wanted,'sourceHashAggregate':contract['sourceHashAggregate'],'sourceProvenance':provenance,'fileCount':149}
(root/'artifacts/enriched-recovery.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
print('ENRICHED_EXACT_RECOVERED',len(provenance),contract['sourceHashAggregate'])
