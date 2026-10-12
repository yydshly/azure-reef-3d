"""One bounded probe: blank, verified b92, candidate in one server/context."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json,threading,functools,urllib.request,time,subprocess,traceback
root=Path(__file__).resolve().parent;out=root/'artifacts/navigation-pipeline';out.mkdir(parents=True,exist_ok=True)
report={'startedUtc':time.strftime('%Y-%m-%d %H:%M:%S UTC',time.gmtime()),'pythonPid':__import__('os').getpid(),'http':[],'browserEvents':[],'cases':[],'scope':'one HTTP server and one browser context; no system settings or user browser touched'}
lock=threading.Lock()
def save():
 with lock:(out/'probe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,fmt,*args):
  report['http'].append({'wall':time.time(),'thread':threading.get_ident(),'message':fmt%args});save()
 def do_GET(self):
  if self.path=='/blank.html':
   data=b'<!doctype html><meta charset="utf-8"><title>Reef blank probe</title><h1>Local navigation works</h1>'
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  else:super().do_GET()
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_address[1]);report['base']=base
for name,path in [('blank','/blank.html'),('b92','/artifacts/continuous-candidate/scan-exhibit.html'),('candidate','/artifacts/composition-candidate/scan-exhibit.html')]:
 begin=time.monotonic()
 with urllib.request.urlopen(base+path,timeout=3) as r:report['cases'].append({'name':name,'url':base+path,'localHttp':{'status':r.status,'bytes':len(r.read()),'seconds':time.monotonic()-begin}})
save();print('HTTP_VERIFIED',base,flush=True)
with sync_playwright() as p:
 browser=None
 try:
  begin=time.monotonic();browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True,chromium_sandbox=True,timeout=20000,ignore_default_args=['--enable-unsafe-swiftshader','--disable-gpu-sandbox','--ignore-gpu-blocklist'])
  report['launchSeconds']=time.monotonic()-begin
  context=browser.new_context(viewport={'width':1280,'height':820});page=context.new_page()
  for event in ['request','requestfailed','response']:
   if event=='response':page.on(event,lambda r:report['browserEvents'].append({'type':'response','url':r.url,'status':r.status,'wall':time.time()}))
   else:page.on(event,lambda r,event=event:report['browserEvents'].append({'type':event,'url':r.url,'failure':r.failure if event=='requestfailed' else None,'wall':time.time()}))
  page.on('console',lambda m:report['browserEvents'].append({'type':'console','level':m.type,'text':m.text,'wall':time.time()}))
  page.on('pageerror',lambda e:report['browserEvents'].append({'type':'pageerror','text':str(e),'wall':time.time()}))
  page.on('crash',lambda:report['browserEvents'].append({'type':'crash','wall':time.time()}))
  cdp=context.new_cdp_session(page)
  try:report['browserCommand']=cdp.send('Browser.getBrowserCommandLine')['arguments']
  except Exception as e:report['browserCommandError']=str(e)
  # List only task Chrome processes whose command contains this returned profile.
  profile=next((a.split('=',1)[1]for a in report.get('browserCommand',[])if a.startswith('--user-data-dir=')),None)
  if profile:
   query="$p='"+profile.replace("'","''")+"'; Get-CimInstance Win32_Process -Filter \"Name = 'chrome.exe'\" | Where-Object { $_.CommandLine -like ('*'+$p+'*') } | Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Depth 3"
   proc=subprocess.run(['pwsh','-NoProfile','-Command',query],capture_output=True,text=True,timeout=6);report['taskChromeProcesses']=proc.stdout;report['processReadError']=proc.stderr
  for case in report['cases']:
   begin=time.monotonic()
   try:
    r=context.request.get(case['url'],timeout=3000);case['browserApiHttp']={'status':r.status,'bytes':len(r.body())}
   except Exception as e:case['browserApiHttp']={'error':str(e)}
   try:
    response=page.goto(case['url'],wait_until='commit',timeout=10000)
    case['navigation']={'status':response.status if response else None,'actualUrl':page.url,'seconds':time.monotonic()-begin}
    if case['name']=='blank':
     page.wait_for_function("() => document.title==='Reef blank probe'",timeout=3000);case['domTitle']=page.title();page.screenshot(path=str(out/'blank.png'),timeout=5000)
    else:
     try:page.wait_for_function('() => window.reefExhibit?.getState().ready',timeout=35000);case['ready']=True
     except Exception as e:case['ready']=False;case['readyError']=str(e)
     case['state']=page.evaluate('() => ({title:document.title,exhibit:window.reefExhibit?.getState(),error:document.querySelector("#scanError")?.hidden})');page.screenshot(path=str(out/(case['name']+'.png')),timeout=8000)
   except Exception as e:case['navigation']={'error':str(e),'actualUrl':page.url,'seconds':time.monotonic()-begin}
   save();print('CASE',case['name'],json.dumps(case.get('navigation')),flush=True)
  report['status']='PASS'if all('error'not in c.get('navigation',{})and c.get('ready',True) for c in report['cases'])else'FAIL'
 except Exception as e:report['status']='FAIL';report['error']=str(e);report['traceback']=traceback.format_exc()
 finally:
  if browser:browser.close()
  save()
server.shutdown();server.server_close();print(json.dumps({'status':report.get('status'),'cases':[{k:c.get(k)for k in ['name','navigation','browserApiHttp','ready']}for c in report['cases']],'error':report.get('error')}),flush=True)
