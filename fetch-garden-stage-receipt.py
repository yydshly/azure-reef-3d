from pathlib import Path
import importlib.util,json,urllib.request,urllib.error,zipfile,io
root=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('reef_publish',root/'publish-api.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);status=json.loads((root/'artifacts/garden-stage/release-status.json').read_text());artifacts=m.api('/repos/'+m.REPO+'/actions/runs/'+str(status['id'])+'/artifacts')['artifacts'];a=next(x for x in artifacts if x['name']=='reef-garden-publication-receipt')
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
request=urllib.request.Request('https://api.github.com/repos/'+m.REPO+'/actions/artifacts/'+str(a['id'])+'/zip',headers={'Authorization':'Bearer '+m.credential(),'User-Agent':'reef-publication-receipt'})
try:urllib.request.build_opener(NoRedirect).open(request,timeout=15);raise RuntimeError('Expected receipt redirect')
except urllib.error.HTTPError as e:assert e.code==302;url=e.headers['Location']
data=urllib.request.urlopen(url,timeout=15).read();assert len(data)<200000
with zipfile.ZipFile(io.BytesIO(data))as z:
 assert z.namelist()==['publication-receipt.json'];receipt=z.read('publication-receipt.json')
out=root/'evidence/reef-garden-stage/publication-receipt.json';out.write_bytes(receipt);r=json.loads(receipt);print(json.dumps({'oldFileCount':r['oldFileCount'],'oldFilesChanged':r['oldFilesChanged'],'worldPointerChanged':r['worldPointerChanged'],'newFiles':r['newFiles']}))
