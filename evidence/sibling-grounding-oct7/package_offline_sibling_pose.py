from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);tiny=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
manifest=json.loads((P/'offline-sibling-pose-manifest.json').read_text());change=manifest['only_candidate_change'];change['nonuniform_scale_blender_preserved']=change.pop('nonuniform_scale_preserved',change.get('nonuniform_scale_blender_preserved'));change['source_nonuniform_scale_gltf']=[.722000002861023,.722000002861023,.6822900176048279];(P/'offline-sibling-pose-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for view in ['passage20','diagnostic']:
 for style in ['textured','gray']:
  im=Image.new('RGB',(2240,808),(235,235,230));dr=ImageDraw.Draw(im)
  for i,(pose,title)in enumerate([('before','BASELINE: node66 original pose'),('candidate','CANDIDATE: node66 world Y -0.102245 scene units')]):
   dr.text((18+1120*i,12),title,font=font,fill=(20,20,20));im.paste(Image.open(P/f'offline-{pose}-{view}-{style}.png').convert('RGB'),(1120*i,48))
  dr.text((18,758),f'{view.upper()} / {style.upper()} | Both arms preserve the published node78 grounding. Original high-detail ground and nonuniform node66 scale.',font=small,fill=(20,20,20));dr.text((18,783),'Offline fixed-light GLB-material preview; production water/substrate shader, browser behavior and performance are not reproduced.',font=small,fill=(20,20,20));im.save(P/f'offline-sibling-compare-{view}-{style}.png')
# Same fixed crop in both arms; no reframing or camera changes.
for style in ['textured','gray']:
 box=(380,220,705,450);scale=2;canvas=Image.new('RGB',(1300,534),(235,235,230));dr=ImageDraw.Draw(canvas)
 for i,(pose,title)in enumerate([('before','BASELINE node66'),('candidate','CANDIDATE node66')]):
  dr.text((16+i*650,10),title,font=font,fill=(20,20,20));crop=Image.open(P/f'offline-{pose}-diagnostic-{style}.png').crop(box).resize((650,460),Image.Resampling.NEAREST);canvas.paste(crop,(i*650,42))
 dr.text((16,509),f'{style.upper()}: fixed diagnostic pixel crop enlarged 2x; all other objects retain their matched world poses.',font=small,fill=(20,20,20));canvas.save(P/f'offline-sibling-diagnostic-crop-{style}.png')
oldP=P.parent;proof=json.loads((P/'measurement/node66-grounding-proof.json').read_text());frozen=json.loads((oldP/'branch-grounding-oct7/measurement/basal-rings.json').read_text());shift=.10224513179842109
lowest=min((j['minimum_vertical_gap_scene_units'],r['root'],j['child_segment'])for r in proof['roots']for j in r['primary_junction_cross_sections']);root=next(r for r in frozen['roots']if r['root']==lowest[1]);joint=next(j for j in root['primary_junction_rings']if j['child_segment']==lowest[2]);matrix=np.array(proof['full_world_matrix66'])@np.linalg.inv(np.array(frozen['node78_world_matrix']));ring=np.array(joint['world_ring'])@matrix[:3,:3].T+matrix[:3,3];cam=np.array([4.7,1.65,-8]);target=np.array([2.2,.9,-12.3]);f=target-cam;f/=np.linalg.norm(f);right=np.cross(f,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,f);tan=np.tan(np.deg2rad(47/2))
def project(p):
 d=p-cam;z=d@f;return np.c_[560+(d@right)/z/tan/1.6*560,350-(d@up)/z/tan*350]
for pose in ['before','candidate']:
 points=ring.copy()
 if pose=='candidate':points[:,1]-=shift
 pix=project(points);im=Image.open(P/f'offline-{pose}-diagnostic-gray.png').convert('RGB');dr=ImageDraw.Draw(im);coords=[tuple(v)for v in pix];dr.line(coords+[coords[0]],fill=(255,150,35),width=3);c=pix.mean(0);dr.line((c[0],c[1],740,470),fill=(255,150,35),width=2);dr.rectangle((734,452,1119,513),fill=(20,26,29));dr.text((742,458),'R08 first primary junction (projected)',font=tiny,fill=(255,190,80));clear=lowest[0]-(shift if pose=='candidate'else 0);dr.text((742,485),f'Min vertical clearance: {clear:.6f} scene units',font=tiny,fill='white');im.save(P/f'offline-{pose}-lowest-junction-projection.png')
review={'scope':'Independent offline pose preview for node66 only; prior node78 numerical audit and earlier simplification study remain unchanged.','distance_units':'Uncalibrated scene units','original_support_and_materials_used':True,'published_node78_shift_in_both_arms_scene_units':.12711730762552115,'only_candidate_node66_downshift_scene_units':shift,'candidate_basal_cap_maximum_signed_gap_from_prior_continuous_measurement_scene_units':proof['maximum_gap_any_basal_cap_scene_units']-shift,'candidate_deepest_basal_cap_burial_scene_units':shift-proof['minimum_gap_any_basal_cap_scene_units'],'controlling_first_primary_junction':{'root':lowest[1],'child_segment':lowest[2],'original_minimum_clearance_scene_units':lowest[0],'candidate_minimum_clearance_scene_units':lowest[0]-shift,'projection_disclosure':'Orange ring is the projected measured cross-section location; projection alone is not an occlusion or collision certificate.'},'requested_cameras_used_without_replacement':True,'all_camera_constraints_pass':all(v['position'][1]>=.4 and v['target'][1]>=0 and np.linalg.norm(np.array(v['position'])-np.array(v['target']))>=3.2 for v in manifest['views']),'qualitative_offline_review':{'status':'Limited offline visual pass for the specified pose change','reviewed':'All four normal/diagnostic textured/gray before-after pairs plus fixed diagnostic crop and controlling-junction projection','findings':['The candidate target stem bases visually enter the existing mound; the detached base-end impression is reduced.','The main branching structure remains exposed and legible in both requested views; no obvious swallowing of the first primary branches was seen.','No alternative camera was needed; the provided diagnostic view exposes the target.'],'boundary':'This visual reading supplements the prior continuous contact/junction calculation and is not a production-water-shader or browser acceptance result.'},'render_scope_limits':manifest['disclosure'],'no_runtime_or_CI_run':True}
(P/'offline-sibling-visual-review.json').write_text(json.dumps(review,indent=2)+'\n')
md=f'''# Node66 offline pose review

This is a new, separate pose preview. Both arms retain the published node78 world-Y drop of 0.12711730762552115. Only the candidate lowers node66 by **0.10224513179842109**. Original detailed terrain, source geometry/materials, all other objects and node66's nonuniform scale are preserved. No production files, source GLB, prior measurements or CI were changed by this preview.

Distances are uncalibrated scene units.

## Exact requested views

- Normal route view, samplePassage(.2): camera [0.29437670936632904, 2.364790323719224, −6.645862253821183], target [0.13504281746656863, 0.7, −21.069232030809317]
- Diagnostic: camera [4.7, 1.65, −8], target [2.2, 0.9, −12.3]
- Both use 47° vertical FOV, 1120×700. Both satisfy targetY ≥0, cameraY ≥0.4 and camera-target distance ≥3.2. Neither view was replaced or scanned

## Image pairs

- `offline-sibling-compare-passage20-textured.png`
- `offline-sibling-compare-passage20-gray.png`
- `offline-sibling-compare-diagnostic-textured.png`
- `offline-sibling-compare-diagnostic-gray.png`
- Fixed 2× enlarged diagnostic crops: `offline-sibling-diagnostic-crop-textured.png`, `offline-sibling-diagnostic-crop-gray.png`
- Measured lowest primary-junction projection: `offline-before-lowest-junction-projection.png`, `offline-candidate-lowest-junction-projection.png`

The normal view shows node66 in the right-hand rear part of the nearby branching group. The supplied diagnostic view exposes the target without requiring a new camera. Object-index visibility is recorded for every frame in `offline-sibling-pose-manifest.json`.

## Actual offline image review

All four paired normal/diagnostic textured/gray images were inspected, including the fixed diagnostic crop and the projected controlling junction. The target bases now visibly enter the existing mound and their detached-end impression is reduced. The first primary branches remain exposed; no obvious swallowing of the main branching was seen in either requested view. This is a **limited offline visual pass** for this pose change, not production water-shader or browser acceptance.

## Source measurement under the fixed translation

No contact geometry was retuned. The prior complete-cap continuous measurement had maximum positive gap 0.09724513179842109; subtracting the fixed shift leaves **−0.005**. Thus all 21 original basal caps are below their existing substrate. Deepest basal burial is **{review['candidate_deepest_basal_cap_burial_scene_units']:.14f}**.

The controlling primary junction is root R08, child segment56. Its original complete-cross-section minimum clearance was 0.21484597514086712; after the fixed shift it remains **0.11260084334244602**. The projection image identifies this measured cross-section. That bound concerns those first-primary-junction cross-sections, not all-world collision or perceptual approval.

## Limits

These are Cycles CPU, 20-sample, fixed-light original-GLB-material frames. The production world-space substrate shader, water/fog/caustics, browser output, fish motion and performance are not reproduced. Gray deliberately overrides materials for shape inspection. Exact source asset SHA-256 remains c12624b2f1da3add8f801421b161daaa5ef9177f7f6edf8ce1a3d1ae7caf66dd.

`render_offline_sibling_pose.py` reproduces the scene and only the two specified poses. `package_offline_sibling_pose.py` produces comparison layouts. `offline-sibling-pose-manifest.json` records cameras, visibility, renderer and isolation assertions; `offline-sibling-visual-review.json` records the analytically inherited contact/junction facts without changing the old audit.
'''
(P/'offline-sibling-review.md').write_text(md)
artifacts={f.name:{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in P.iterdir()if f.name.startswith('offline-') or f.name in ['render_offline_sibling_pose.py','package_offline_sibling_pose.py']}
artifacts.pop('offline-sibling-artifacts.json',None);(P/'offline-sibling-artifacts.json').write_text(json.dumps(artifacts,indent=2)+'\n')
