"""Use the same existing Git credential as stage pushes; never print secrets."""
import subprocess,urllib.request,json,sys,os
REPO='yydshly/azure-reef-3d'
_token=None
def credential():
 global _token
 if _token:return _token
 result=subprocess.run(['git','-c','credential.interactive=never','credential','fill'],input='protocol=https\nhost=github.com\n\n',capture_output=True,text=True,timeout=20,env={**os.environ,'GIT_TERMINAL_PROMPT':'0'})
 if result.returncode:raise RuntimeError('Existing Git credential unavailable; do not create or switch credentials')
 fields=dict(line.split('=',1)for line in result.stdout.splitlines()if '='in line);_token=fields.get('password');assert _token;return _token
def api(path,method='GET',data=None):
 token=credential()
 request=urllib.request.Request('https://api.github.com'+path,data=json.dumps(data).encode()if data is not None else None,method=method,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'azure-reef-independent-preview'})
 with urllib.request.urlopen(request,timeout=25)as response:return json.loads(response.read())if response.status!=204 else {'status':204}
if __name__=='__main__':
 user=api('/user');assert user['login']=='yydshly','Existing Git identity does not match the authorized repository owner'
 repo=api('/repos/'+REPO)
 runs=api('/repos/'+REPO+'/actions/workflows/pages.yml/runs?per_page=12')
 summaries=[]
 for r in runs['workflow_runs'][:12]:
  artifacts=api('/repos/'+REPO+'/actions/runs/'+str(r['id'])+'/artifacts')if r['conclusion']=='success'else{'artifacts':[]}
  summaries.append({'id':r['id'],'sha':r['head_sha'],'status':r['status'],'conclusion':r['conclusion'],'created':r['created_at'],'artifacts':[{'id':a['id'],'name':a['name'],'bytes':a['size_in_bytes'],'expired':a['expired']}for a in artifacts['artifacts']]})
 env=api('/repos/'+REPO+'/environments/github-pages')
 print(json.dumps({'login':user['login'],'permissions':repo.get('permissions'),'main':api('/repos/'+REPO+'/git/ref/heads/main')['object']['sha'],'runs':summaries,'environmentBranchPolicy':env.get('deployment_branch_policy')},indent=2))
