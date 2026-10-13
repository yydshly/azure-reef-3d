"""Validate the showcase and the publication boundary without loading any scan."""
from pathlib import Path
import hashlib,json,sys
site=Path(sys.argv[1] if len(sys.argv)>1 else 'dist')
versions=json.loads((site/'showcase/versions.json').read_text(encoding='utf8'))
assert len(versions)>=12 and len({v['id'] for v in versions})==len(versions)
assert sum(bool(v['demo']) for v in versions)>=11
assert versions[0]['id']=='garden012' and '未达标' in versions[0]['state']
assert all(v['demo'] for v in versions if v['id'] in ['continuous','composition','basin-first','basin'])
assert len({v['image'] for v in versions if v['image']})==sum(bool(v['image']) for v in versions)
hashes=[]
for v in versions:
    if v['image']:
        image=site/'showcase/media'/v['image'];assert image.is_file();hashes.append(hashlib.sha256(image.read_bytes()).hexdigest())
    if len(sys.argv)>1 and v['demo']:
        entry=site/v['demo'];assert (entry/'index.html' if v['demo'].endswith('/') else entry).is_file(),v['demo']
assert len(set(hashes))==len(hashes),'Do not reuse one preview for different versions'
assert (site/'legacy.html').is_file()
html=(site/'index.html').read_text(encoding='utf8');js=(site/'showcase/app.js').read_text(encoding='utf8')
assert '<iframe' not in html and '<video' not in html,'Do not preload scenes or recordings'
assert 'loading="lazy"' in js and 'content.replaceChildren()' in js
assert hashlib.sha256((site/'showcase/media/complete-demo.webm').read_bytes()).hexdigest()=='2a9206d4b96ffa7e1ea8baa7f48ab3c7eb9839b1333364a51157fd5c71cd16fa'
print('SHOWCASE_OK:',len(versions),'versions /',sum(bool(v['demo']) for v in versions),'interactive entries / unique real images / no preloaded scene')
