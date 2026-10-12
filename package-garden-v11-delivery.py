from pathlib import Path
import json,hashlib,shutil
root=Path(__file__).resolve().parent;out=root/'evidence/reef-garden-v11'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
local=read(out/'verification.json');hosted=read(out/'hosted-verification.json');receipt=read(out/'publication-receipt.json');release=read(root/'artifacts/garden-v11/release.json');run=read(root/'artifacts/garden-v11/release-status.json')
assert local['status']==hosted['status']=='PASS'and run['conclusion']=='success'
assert receipt['oldFileCount']==2304 and receipt['oldFilesChanged']==0 and not receipt['worldPointerChanged']
assert receipt['oldPublishedHashAggregate']==read(root/'evidence/reef-garden-v1/DELIVERY.json')['oldPublishedHashAggregate']
assert receipt['newFiles']=={'preview/reef-garden-v1/'+k:h for k,h in local['sourceHashes'].items()}
assert receipt['frozenFirstVersionFiles']=={'preview/reef-garden-v1-first/'+k:h for k,h in local['firstVersionHashes'].items()}
sha=hashlib.sha256(''.join(k+'\0'+receipt['newFiles'][k]+'\n'for k in sorted(receipt['newFiles'])).encode()).hexdigest()
delivery={'status':'COMPLETED_PUBLISHED','url':hosted['url'],'firstVersionUrl':hosted['url'].replace('/reef-garden-v1/','/reef-garden-v1-first/'),'sourceAndLocalEvidenceCommit':'348ead4995f21d5a595640165c3b10cc14b63219','publicationCommit':release['mainCommit'],'runId':run['id'],'runUrl':run['url'],'runtimeSourceHashes':receipt['newFiles'],'runtimeHashAggregate':sha,'aggregateAlgorithm':'SHA256 of sorted relative-path + NUL + file-SHA256 + LF','oldPublicFiles':2304,'oldFilesChanged':0,'oldPublishedHashAggregate':receipt['oldPublishedHashAggregate'],'worldPointerChanged':False,'firstVersionBytesPreserved':True,'firstVersionHashes':receipt['frozenFirstVersionFiles'],'localNaturalTourSeconds':local['checks']['naturalTour']['wallSeconds'],'localVerification':'PASS','publicHostedInteractions':'PASS','oldLinks':'HTTP 200 and native popup/UI checks PASS; old scan GPU completeness is not reaccepted.','remaining':['Distant reef shapes still repeat; some return headings remain sparse.','Physical phone performance and real multitouch are not tested.'],'blockers':[]}
(out/'DELIVERY.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copyfile(root/'artifacts/garden-v11/release.json',out/'release.json');shutil.copyfile(root/'artifacts/garden-v11/release-status.json',out/'release-status.json')
print(json.dumps(delivery,ensure_ascii=True))
