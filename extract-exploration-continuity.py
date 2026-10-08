import hashlib, json, pathlib, zipfile
root=pathlib.Path('.')
def sha(data):return hashlib.sha256(data).hexdigest()
old=root/'azure-reef-reefs4d-candidate-delta.zip'
assert sha(old.read_bytes())=='6621e03fe42110a070eeb49be69403b29a6d5d0e9be6031865e1491764a83463'
model='dist/assets/reefs4d/C12019-web.glb'
with zipfile.ZipFile(old)as z:
 data=z.read(model)
 assert sha(data)=='975228622829cb715ba9b48c0c5cc45c92e8b79d6689102cf188479318362502'
 p=root/model;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
archive=root/'exploration-continuity-delta.zip'
assert sha(archive.read_bytes())=='f2c31016e7413c4ea1bb1576133c8aae9b3b4f07ec8bd217cb643ce3f861be61'
with zipfile.ZipFile(archive)as z:
 names=z.namelist();assert len(names)==len(set(names))==49
 for name in names:
  p=pathlib.PurePosixPath(name)
  assert not p.is_absolute() and '..'not in p.parts and '\\'not in name
 manifest=json.loads(z.read('WORLD-MANIFEST.json'))
 assert manifest['base']=='498cc09acda8b7d4609ee2dc863e01e6712c790c'
 files=manifest['files'];assert len(files)==48
 assert set(names)=={f['path']for f in files}|{'WORLD-MANIFEST.json'}
 for f in files:
  data=z.read(f['path']);assert len(data)==f['bytes'] and sha(data)==f['sha256'],f['path']
 for f in files:
  p=root/f['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(f['path']))
 out=root/'render-evidence';out.mkdir(exist_ok=True)
 (out/'underwater-archive-verification.json').write_text(json.dumps({'candidate':'connected synthetic worlds','archiveSHA256':'f2c31016e7413c4ea1bb1576133c8aae9b3b4f07ec8bd217cb643ce3f861be61','files':files,'modelSHA256':'975228622829cb715ba9b48c0c5cc45c92e8b79d6689102cf188479318362502','stack':'accepted baseline core restored; only unchanged scan model extracted from candidate1; no candidate2 extraction'},indent=2))
print('Verified independent exhibit delta plus unchanged source model; no mixed-world runtime extracted.')
