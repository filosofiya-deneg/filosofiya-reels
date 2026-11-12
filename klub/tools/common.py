import numpy as np
from PIL import Image, ImageDraw, ImageFont
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
EMO='/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
emo_font=ImageFont.truetype(EMO,109)
YEL=(255,214,10); WH=(255,255,255)
def is_emoji(c): return ord(c)>=0x1F000 or 0x2600<=ord(c)<=0x27BF or c in '⏳⏱⌛'
def emoji_img(c,size):
    im=Image.new('RGBA',(136,128),(0,0,0,0))
    ImageDraw.Draw(im).text((0,0),c,font=emo_font,embedded_color=True)
    im=im.crop(im.getbbox()); s=size*1.05/im.height
    return im.resize((max(1,int(im.width*s)),int(im.height*s)),Image.LANCZOS)
def line(text,size,fill=WH,stroke=None,sw=None):
    f=ImageFont.truetype(BOLD,size); sw=sw if sw is not None else max(3,size//14)
    stroke=stroke or (10,10,20); gap=int(size*0.25); toks=[];buf=''
    for c in text:
        if is_emoji(c):
            if buf: toks.append(('t',buf)); buf=''
            toks.append(('e',c))
        elif c=='️': continue
        else: buf+=c
    if buf: toks.append(('t',buf))
    items=[]
    for k,t in toks:
        if k=='t': items.append(('t',t,int(f.getlength(t))))
        else:
            e=emoji_img(t,int(size*0.95)); items.append(('e',e,e.width+gap))
    tw=sum(i[2] for i in items)+sw*2
    im=Image.new('RGBA',(tw+20,int(size*1.5)),(0,0,0,0)); d=ImageDraw.Draw(im); x=10+sw
    for k,v,w in items:
        if k=='t': d.text((x,int(size*0.15)),v,font=f,fill=fill,stroke_width=sw,stroke_fill=stroke)
        else: im.alpha_composite(v,(x,int(size*0.25)))
        x+=w
    return im.crop(im.getbbox())
def pill(content,padx=40,pady=22,color=(0,0,0,150),radius=40):
    im=Image.new('RGBA',(content.width+padx*2,content.height+pady*2),(0,0,0,0))
    ImageDraw.Draw(im).rounded_rectangle([0,0,im.width-1,im.height-1],radius=radius,fill=color)
    im.alpha_composite(content,(padx,pady)); return im
def wrap(text,size,maxw):
    f=ImageFont.truetype(BOLD,size); out=[];cur=''
    for w in text.split(' '):
        t=(cur+' '+w).strip()
        if f.getlength(t)>maxw and cur: out.append(cur);cur=w
        else: cur=t
    out.append(cur); return out
