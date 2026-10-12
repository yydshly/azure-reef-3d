"""Prepare an isolated candidate from verified enriched bytes. Never publishes.

Call on an already-assembled stable distribution:
python stage-composition-preview.py --dist <existing-dist>
Then render preview/composition-candidate/scan-exhibit.html before publication.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,zipfile,shutil
root=Path(__file__).resolve().parent
args=argparse.ArgumentParser();args.add_argument('--dist',required=True);opt=args.parse_args()
dist=Path(opt.dist).resolve();base=dist/'preview/exploration-enriched-candidate';target=dist/'preview/composition-candidate'
assert dist.is_dir() and base.is_dir(),'An assembled stable enriched distribution is required'
assert not target.exists(),'Candidate path already exists; do not overwrite it'
assert target.resolve().is_relative_to(dist),'Candidate must stay inside the named distribution'
proof=json.loads((root/'evidence/composition-20261012/enriched-source-contract.json').read_text(encoding='utf-8'))
receipt=json.loads((root/'evidence/composition-20261012/DELIVERY.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in proof['sourceHashes'].items():assert sha(base/name)==digest,'Stable enriched source mismatch '+name
archive=root/'evidence/composition-20261012/composition-preview-delta.zip';assert sha(archive)==receipt['sha256']
before={p.relative_to(dist).as_posix():sha(p)for p in dist.rglob('*')if p.is_file()}
with zipfile.ZipFile(archive) as z:
 manifest=json.loads(z.read('COMPOSITION-MANIFEST.json'));assert len(manifest['changes'])==6
 assert set(z.namelist())==set(manifest['changes'])|{'COMPOSITION-MANIFEST.json'}
 delta={}
 for name,digest in manifest['changes'].items():
  rel=PurePosixPath(name);assert rel.name==name and '..'not in rel.parts
  data=z.read(name);assert hashlib.sha256(data).hexdigest()==digest;delta[name]=data
# Every check above precedes writing. Only this new directory is created.
for name in proof['sourceHashes']:
 p=target/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/name,p)
for name,data in delta.items():(target/name).write_bytes(data)
after={p.relative_to(dist).as_posix():sha(p)for p in dist.rglob('*')if p.is_file() and not p.is_relative_to(target)}
assert before==after,'Protected public files changed'
print(json.dumps({'status':'STAGED_UNVERIFIED_NOT_PUBLISHED','entry':str(target/'scan-exhibit.html'),'oldPublicFilesUnchanged':len(before),'worldPointerChanged':False,'visualGatePending':True}))
