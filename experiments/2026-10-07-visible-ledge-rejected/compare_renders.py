"""Presentation only: preserve render pixels and add labels outside each frame."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse
p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('view');a=p.parse_args()
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
images=[Image.open(a.folder/(label+'-'+a.view+'.png')).convert('RGB') for label in ['before','after']]
w,h=images[0].size
out=Image.new('RGB',(2*w,h+64),(237,237,237));d=ImageDraw.Draw(out)
d.text((14,8),'Accepted baseline | '+a.view,font=font,fill=(24,24,24))
d.text((w+14,8),'ONE folded-edge sample | '+a.view,font=font,fill=(24,24,24))
out.paste(images[0],(0,36));out.paste(images[1],(w,36))
d.text((14,h+40),'OFFLINE • Fixed grey / lighting / camera • No water, textures, animation or runtime validation',font=font,fill=(24,24,24))
out.save(a.folder/('comparison-'+a.view+'.png'))
