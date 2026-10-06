import sys,json
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));from replay_thickets import replay
proof=json.loads((P/'all-geometry-proof.json').read_text());records={}
for m in replay(P/'original_geometry_recipe.py'):
 r=next(x for x in proof['meshes']if x['name']==m.name);records[m.name]={'height_scale':m.height_scale,'source_graph':m.tubes,'continuation_repairs':r['joints']}
(P/'all-branch-graphs.json').write_text(json.dumps(records,indent=2));print('GRAPHS',len(records))
