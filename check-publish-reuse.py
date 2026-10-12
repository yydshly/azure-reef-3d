import importlib.util,pathlib
spec=importlib.util.spec_from_file_location('publish_api',pathlib.Path(__file__).with_name('publish-api.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);api,REPO=module.api,module.REPO
import json,urllib.request,urllib.error,urllib.parse
print('BRANCH_POLICIES',json.dumps(api('/repos/'+REPO+'/environments/github-pages/deployment-branch-policies')),flush=True)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
opener=urllib.request.build_opener(NoRedirect)
try:
 response=opener.open(urllib.request.Request('https://api.github.com/repos/'+REPO+'/actions/artifacts/11707935275/zip',headers={'User-Agent':'azure-preview-artifact-reuse'}),timeout=12)
 print('PUBLIC_ARTIFACT_READ',response.status,flush=True)
except urllib.error.HTTPError as e:print('PUBLIC_ARTIFACT_READ',e.code,'redirectHost',urllib.parse.urlparse(e.headers.get('Location','')).hostname,flush=True)
