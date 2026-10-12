from pathlib import Path, PurePosixPath
import subprocess, zipfile, hashlib, json
root=Path(__file__).resolve().parent
source=root.parent/'enriched-inputs'
source.mkdir(exist_ok=True)
ref='acd6b3f9f287b8fa5b8e07e4ffddf3491668c92b'
expected={'exploration-enriched-code.zip':'c57395ee44255cb22393cd84de5e077d5c788538953fa12e92c908733e2f8c1b','exploration-demo-snapshot-b8c55275.zip':'8d115206a4f30ffc248922f992af357b22b9b1b173084d4363ab059e76b01110','exploration-enriched-build-tools.zip':'79fabe59279fed96271d21da887050f210a86ac92fedadd32a0c5773d9848808'}
for name in ['exploration-enriched-code.zip','exploration-demo-snapshot-b8c55275.zip','exploration-enriched-build-tools.zip']:
    data=subprocess.check_output(['git','show',ref+':'+name],cwd=root)
    # Reject inconsistent pinned archive bytes before extracting any tools.
    assert hashlib.sha256(data).hexdigest()==expected[name], name
    target=source/name
    target.write_bytes(data)
    print(name,len(data),hashlib.sha256(data).hexdigest())
    with zipfile.ZipFile(target) as z:
        print('ENTRIES',z.namelist()[:45])
        if name=='exploration-enriched-build-tools.zip':
            for n in z.namelist():
                p=PurePosixPath(n)
                assert not p.is_absolute() and '..' not in p.parts
                dst=source/'tools'/p;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(z.read(n))
