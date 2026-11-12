"""python3 carousel.py spec.json  -> klub/carousels/<id>/NN.jpg (1080x1350)
spec: {"id":"c2_chan","slides":[{"photo":"p4","oy":0.5,"title":"...","body":"...","foot":"...","cover":false}]}
photo = prefix of a file in ../src/photos (p1..p5)."""
import sys, json, glob, os
import numpy as np
from PIL import Image
from common import *
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
CW,CH=1080,1350
def photo(k): return Image.open(glob.glob(f'{ROOT}/src/photos/{k}_*.png')[0]).convert('RGB')
def cover(im,oy):
    w,h=im.size; sc=CW/w; im2=im.resize((CW,int(h*sc)),Image.LANCZOS); top=int((im2.height-CH)*oy); return im2.crop((0,top,CW,top+CH))
def grad(h0,amax):
    g=np.zeros((CH,CW,4),np.uint8); y=np.arange(CH)
    g[...,3]=(np.clip((y-(CH-h0))/h0,0,1)**1.3*amax)[:,None].astype(np.uint8)
    g[...,3]=np.maximum(g[...,3],(np.clip(1-y/260,0,1)*120)[:,None].astype(np.uint8)); return Image.fromarray(g,'RGBA')
def slide(n,total,s,fname):
    cs=s.get('cover',False)
    fr=cover(photo(s['photo']),s.get('oy',0.5)).convert('RGBA'); fr.alpha_composite(grad(800 if cs else 900,235))
    fr.alpha_composite(pill(line('🏡 Клуб Семейного Отдыха',38,WH),padx=24,pady=12,color=(200,60,0,225),radius=30),(50,50))
    if not cs:
        c=pill(line(f'{n}/{total}',38,WH),padx=24,pady=12,color=(0,0,0,150),radius=30); fr.alpha_composite(c,(CW-c.width-50,50))
    blocks=[]; ts=96 if cs else 74
    for l in wrap(s['title'],ts,CW-140): blocks.append((line(l,ts,YEL,sw=7),14))
    if s.get('body'):
        blocks.append((None,26))
        for l in wrap(s['body'],50,CW-140): blocks.append((line(l,50,WH,sw=4),10))
    if s.get('foot'):
        blocks.append((None,20))
        for l in wrap(s['foot'],34,CW-140): blocks.append((line(l,34,(230,230,230),sw=3),6))
    y=CH-70-sum((b[0].height if b[0] else 0)+b[1] for b in blocks)
    for im,gap in blocks:
        if im: fr.alpha_composite(im,(70,y)); y+=im.height
        y+=gap
    fr.convert('RGB').save(fname,quality=93)
if __name__=='__main__':
    spec=json.load(open(sys.argv[1])); out=f"{ROOT}/carousels/{spec['id']}"; os.makedirs(out,exist_ok=True)
    for i,s in enumerate(spec['slides'],1): slide(i,len(spec['slides']),s,f'{out}/{i:02d}.jpg')
    print(out,len(spec['slides']))
