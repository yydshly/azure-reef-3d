import json,struct,math,hashlib,argparse
from pathlib import Path
parser=argparse.ArgumentParser(description='Add distant shared-mesh instances to frozen accepted corridor.')
parser.add_argument('input',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
raw=args.input.read_bytes()
EXPECTED='fce96692e3f805edd4ac4cd4dc1380a20dd333f7978e5dc20d6d710afa4c9c02'
assert hashlib.sha256(raw).hexdigest()==EXPECTED,'Wrong corridor SHA-256; refusing to alter a different model'
n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);binary=raw[20+n:];before=json.loads(json.dumps(j));proof=[]
# Exact existing material/geometry instances. Centers in Three coordinates.
placements=[(-3.1,-12.1,13,1.20,.5,-.17),(3.6,-16.8,18,1.05,2.0,-.24),(-4.5,-21.1,3,1.30,-.8,-.24),(1.8,-26.0,11,1.16,1.3,-.24),(3.6,12.2,15,1.18,-.4,-.17),(-6.4,16.4,7,1.02,2.4,-.24),(4.2,21.3,12,1.27,.8,-.24),(-3.8,26.2,4,1.16,-1.4,-.24)]
for k,(cx,cz,source,sc,angle,base) in enumerate(placements):
 src=next(v for v in j['nodes']if v['name']==f'Coral_Staghorn_Thicket_{source:02d}');m=src['mesh'];a=j['accessors'][j['meshes'][m]['primitives'][0]['attributes']['POSITION']];mn=a['min'];mx=a['max'];x=(mn[0]+mx[0])/2;z=(mn[2]+mx[2])/2;cos=math.cos(angle);sin=math.sin(angle)
 t=[cx-sc*(cos*x+sin*z),base-sc*mn[1],cz-sc*(-sin*x+cos*z)]
 node={'name':f'Corridor_Distant_Linked_{k:02d}','mesh':m,'translation':t,'rotation':[0,math.sin(angle/2),0,math.cos(angle/2)],'scale':[sc,sc,sc]}
 idx=len(j['nodes']);j['nodes'].append(node);j['scenes'][j.get('scene',0)]['nodes'].append(idx)
 corners=[(cx+sc*(cos*(xx-x)+sin*(zz-z)),cz+sc*(-sin*(xx-x)+cos*(zz-z)))for xx in [mn[0],mx[0]]for zz in [mn[2],mx[2]]]
 zs=[p[1]for p in corners];assert min(zs)>10 or max(zs)<-10
 proof.append({'node':node,'source':src['name'],'center':[cx,base,cz],'z_bounds':[min(zs),max(zs)],'grounding':'Existing sand substrate; branch bases seated slightly below sand surface'})
jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);out=struct.pack('<4sII',b'glTF',2,20+len(jb)+len(binary))+struct.pack('<I4s',len(jb),b'JSON')+jb+binary;args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(out)
report={'source_sha256':hashlib.sha256(raw).hexdigest(),'output_sha256':hashlib.sha256(out).hexdigest(),'glb_bytes':len(out),'all_original_nodes_exactly_unchanged':j['nodes'][:len(before['nodes'])]==before['nodes'],'entire_original_binary_exactly_unchanged':True,'accessors_meshes_materials_images_unchanged':all(j[k]==before[k]for k in ['accessors','meshes','materials','images','bufferViews']),'added_nodes':proof};args.output.with_suffix('.proof.json').write_text(json.dumps(report,indent=2));print('DEPTH_READY',len(out))
