"""Update the isolated garden after real checks, freeze V1, and preserve the old public site."""
from pathlib import Path
import importlib.util,json,base64,hashlib,urllib.request,urllib.error,urllib.parse
root=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reef_publish',root/'publish-api.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);api,repo=m.api,m.REPO
assert api('/user')['login']=='yydshly','Do not switch publishing identity'
views=json.loads((root/'artifacts/garden-v11/verification.json').read_text(encoding='utf8'));assert views['status']=='PASS'and len(views['views'])>=10
assert views['checks']['naturalTour']['passed']and views['checks']['previousLinksOpened']['passed']and views['checks']['mobileMenuCloseSwimAndOutsideDismiss']['passed']
page=root/'dist/preview/reef-garden-v1';assert all(hashlib.sha256((page/n).read_bytes()).hexdigest()==h for n,h in views['sourceHashes'].items()),'Source changed after real view verification'
current=api('/repos/'+repo+'/git/ref/heads/main')['object']['sha'];assert current=='c98fdcadd7f4d3d0676628ece4be242f4057938a','Main changed since release inspection; review before writing'
runs=api('/repos/'+repo+'/actions/workflows/pages.yml/runs?status=success&per_page=5')['workflow_runs'];artifact=None
runs=[r for r in runs if r['id']==38211492231];assert len(runs)==1,'Use the exact accepted first-version publication'
for run in runs:
 candidates=api('/repos/'+repo+'/actions/runs/'+str(run['id'])+'/artifacts')['artifacts'];candidate=next((a for a in candidates if a['name']=='github-pages'and not a['expired']),None)
 if candidate:artifact=candidate;previousRun=run;break
assert artifact and artifact.get('digest'),'An unexpired complete publication artifact is required'
public='https://yydshly.github.io/azure-reef-3d/';protected={}
for name in ['index.html','app.js','preview/world/index.html','preview/world/current-world.json','vendor/three.module.js','vendor/three.core.js']:
 data=urllib.request.urlopen(public+name,timeout=15).read();protected[name]=hashlib.sha256(data).hexdigest()
for dependency in ['vendor/three.module.js','vendor/three.core.js']:
 canonical=(root/'dist'/dependency).read_bytes().replace(b'\r\n',b'\n')
 assert protected[dependency]==hashlib.sha256(canonical).hexdigest(),'Live dependency program differs from verified runtime '+dependency
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
request=urllib.request.Request('https://api.github.com/repos/'+repo+'/actions/artifacts/'+str(artifact['id'])+'/zip',headers={'Authorization':'Bearer '+m.credential(),'User-Agent':'azure-preview-reuse','Accept':'application/vnd.github+json'})
try:urllib.request.build_opener(NoRedirect).open(request,timeout=20);raise RuntimeError('Expected existing artifact redirect')
except urllib.error.HTTPError as e:assert e.code==302;signed=e.headers['Location']
host=urllib.parse.urlparse(signed).hostname;assert host.endswith('.blob.core.windows.net')or host.endswith('.actions.githubusercontent.com')
base=api('/repos/'+repo+'/git/commits/'+current);files={p.relative_to(root).as_posix():p.read_bytes()for p in page.iterdir()if p.is_file()}
for p in (root/'dist/preview/reef-garden-v1-first').iterdir():
 assert p.is_file();files[p.relative_to(root).as_posix()]=p.read_bytes()
files['.github/workflows/pages.yml']=(root/'publisher/pages-preserved.yml').read_bytes()
for name in ['restore-published-preview.py','qa-garden.mjs']:files[name]=(root/name).read_bytes()
entries=[]
for name,data in files.items():
 blob=api('/repos/'+repo+'/git/blobs','POST',{'content':base64.b64encode(data).decode(),'encoding':'base64'});entries.append({'path':name,'mode':'100644','type':'blob','sha':blob['sha']})
tree=api('/repos/'+repo+'/git/trees','POST',{'base_tree':base['tree']['sha'],'tree':entries});commit=api('/repos/'+repo+'/git/commits','POST',{'message':'Improve Reef Garden vista and reconnect prior explorations; freeze V1 and preserve original site','tree':tree['sha'],'parents':[current]})
assert api('/repos/'+repo+'/git/ref/heads/main')['object']['sha']==current,'Main advanced during preparation'
api('/repos/'+repo+'/git/refs/heads/main','PATCH',{'sha':commit['sha'],'force':False})
safe={'status':'SOURCE_COMMITTED_DISPATCHING','oldMain':current,'mainCommit':commit['sha'],'oldSuccessfulRun':previousRun['id'],'oldArtifactId':artifact['id'],'oldArtifactDigest':artifact['digest'],'oldArtifactBytes':artifact['size_in_bytes'],'protectedPublicHashes':protected,'newEntry':public+'preview/reef-garden-v1/','newSourceFiles':list(files),'tokenPermissionsExpanded':False,'worldEntryChanged':False};out=root/'artifacts/garden-v11/release.json';out.write_text(json.dumps(safe,indent=2));print(json.dumps(safe),flush=True)
api('/repos/'+repo+'/actions/workflows/pages.yml/dispatches','POST',{'ref':'main','inputs':{'snapshot_url':signed,'snapshot_digest':artifact['digest'],'protected_hashes':json.dumps(protected,separators=(',',':'))}});safe['status']='DISPATCHED';out.write_text(json.dumps(safe,indent=2));print('EXISTING_PAGES_DISPATCHED',commit['sha'],flush=True)
