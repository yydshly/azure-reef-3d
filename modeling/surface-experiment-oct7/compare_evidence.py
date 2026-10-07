"""Verify matched offline manifests and make labelled, unscaled comparison sheets."""
from pathlib import Path
import argparse,copy,hashlib,json
from PIL import Image,ImageDraw,ImageFont
import numpy as np
p=argparse.ArgumentParser();p.add_argument('folder',type=Path);a=p.parse_args();root=a.folder
modes=['baseline','fine','soft','normal-disabled'];views=['close','close-reverse','opening']
man={k:json.loads((root/k/'render-manifest.json').read_text())for k in modes}
b=man['baseline'];report={'disclosure':'OFFLINE comparisons only, not browser evidence. Comparison image areas contain unmodified original render pixels at 1:1 scale. Pixel differences are descriptive, not a realism metric.','matched_checks':{},'pixel_differences':{}}
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
try:font=ImageFont.truetype(fontpath,24)
except OSError:font=ImageFont.load_default()
def scrub(g):
 g=copy.deepcopy(g)
 for n in g['nodes']:
  if n['type']=='ShaderNodeTexImage':n['image']='MAP_SLOT'
  if n['type']=='ShaderNodeNormalMap':n['inputs']=[[k,'ALLOWED_CONTROL']if k=='Strength'else[k,v]for k,v in n['inputs']]
 return g
for k,d in man.items():
 assert d['settings']==b['settings'] and d['fixture_sha256']==b['fixture_sha256']
 assert d['assigned_only_to']==b['assigned_only_to']
 assert scrub(d['actual_assigned_graph'])==scrub(b['actual_assigned_graph'])
 for v in views:
  q=copy.deepcopy(d['views'][v]);r=copy.deepcopy(b['views'][v]);q.pop('sha256');r.pop('sha256');assert q==r
  assert hashlib.sha256((root/k/(v+'.png')).read_bytes()).hexdigest()==d['views'][v]['sha256']
 report['matched_checks'][k]={'same_fixture_settings':True,'same_camera_poses_and_lens':True,'same_target_only_assignment':True,'target_graph_identical_except_maps_and_control_strength':True,'render_hashes_verified':True,'actual_normal_strength':d['control_effective_scale'],'actual_maps':[n['image']for n in d['actual_assigned_graph']['nodes']if n['image']]}
 if k=='baseline':continue
 report['pixel_differences'][k]={}
 for v in views:
  aa=np.asarray(Image.open(root/'baseline'/(v+'.png')).convert('RGB')).astype(np.int16);bb=np.asarray(Image.open(root/k/(v+'.png')).convert('RGB')).astype(np.int16);dd=np.abs(aa-bb)
  report['pixel_differences'][k][v]={'mean_absolute_rgb_8bit':float(dd.mean()),'pixels_with_any_channel_difference_over_10':int((dd.max(-1)>10).sum()),'total_pixels':int(aa.shape[0]*aa.shape[1])}
  canvas=Image.new('RGB',(2240,748),(17,24,29));draw=ImageDraw.Draw(canvas)
  for i,mode in enumerate(['baseline',k]):
   canvas.paste(Image.open(root/mode/(v+'.png')).convert('RGB'),(i*1120,48));draw.text((i*1120+14,10),'OFFLINE | '+v+' | '+mode+' | fixed camera',font=font,fill='white')
  canvas.save(root/('OFFLINE-'+v+'-baseline-'+k+'.png'))
(root/'matched-evidence-proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
