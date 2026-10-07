from pathlib import Path
import bpy,json,numpy as np
P=Path(__file__).resolve().parent;old=json.loads((P/'measurement/node66-grounding-proof.json').read_text());im=bpy.data.images.load(str(P/'offline-before-diagnostic-textured-index-0001.exr'));a=np.flipud(np.array(im.pixels[:]).reshape(700,1120,4)[:,:,0]);cam=np.array([4.7,1.65,-8]);target=np.array([2.2,.9,-12.3]);f=target-cam;f/=np.linalg.norm(f);r=np.cross(f,[0,1,0]);r/=np.linalg.norm(r);u=np.cross(r,f);tan=np.tan(np.deg2rad(47/2));out=[]
for root in old['roots']:
 q=np.array(root['center_world'])-cam;depth=q@f;x=560+(q@r)/depth/tan/1.6*560;y=350-(q@u)/depth/tan*350;ix=int(round(x));iy=int(round(y));val=float(a[iy,ix]);near=a[max(0,iy-1):min(700,iy+2),max(0,ix-1):min(1120,ix+2)];out.append({'root':root['root'],'state':root['state'],'pixel':[float(x),float(y)],'object_index_at_projection':val,'target_node66_present_in_3x3':bool((near>1.5).any())})
(P/'offline-requested-diagnostic-base-visibility.json').write_text(json.dumps({'method':'Actual source-frame object-index pass at projected original basal-ring centers; coarse evidence of external obstruction only. Seeing index2 does not exclude self-occlusion by another branch of node66. Candidate cap centers are deliberately buried and are not used for this visibility check.','roots':out},indent=2)+'\n');print(json.dumps(out,indent=2))

for pose in ['before','candidate']:
 im=bpy.data.images.load(str(P/f'offline-{pose}-passage20-textured-index-0001.exr'));mask=np.flipud(np.array(im.pixels[:]).reshape(700,1120,4)[:,:,0]>1.5);np.save(P/f'offline-{pose}-passage20-node66-mask.npy',mask)
