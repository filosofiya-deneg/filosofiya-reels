"""python3 reel.py spec.json -> klub/<out> (1080x1920 reel, ambient audio from clips)
spec: {"out":"05_x.mp4","hook":["ДРУЗЬЯ,","ЖДЁМ ВАС!"],"hook_tag":"🏡 Клуб Семейного Отдыха",
 "scenes":[{"clip":"sunset","start":0.2,"dur":3.4,"gain":12,"label":"💦 Бассейн","sub":"Тёплый бассейн"}],
 "final":{"photo":"p1","dur":4.8,"title":["ЖДЁМ ВАС","В ГОСТИ!"],"sub":["Приезжайте с семьёй и друзьями","Бронь — ссылка в профиле"],"cta":"📩 Бронь — группа в MAX"}}
clips: sunset pool_night banya chan_far chan_close cinema (cinema already has the film title blurred; never use cinema_orig)."""
import sys, json, glob, os, math, subprocess
import numpy as np
from PIL import Image, ImageFilter
from common import *
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
W,H,FPS,XF=1080,1920,30,0.3
spec=json.load(open(sys.argv[1]))
def photo(k): return Image.open(glob.glob(f'{ROOT}/src/photos/{k}_*.png')[0]).convert('RGB')
sc=[];t=0.0
for s in spec['scenes']:
    sc.append(dict(s,t0=t,t1=t+s['dur'],kind='v',path=f"{ROOT}/src/clips/{s['clip']}.mp4")); t+=s['dur']
fin=spec['final']; sc.append(dict(kind='p',t0=t,t1=t+fin['dur'],photo=fin['photo'])); DUR=t+fin['dur']
ov=[]
def add(im,t0,t1,y,x=None,pulse=False):
    mw=W-90-(60 if pulse else 0)
    if im.width>mw: im=im.resize((mw,int(im.height*mw/im.width)),Image.LANCZOS)
    ov.append(dict(im=im,t0=t0,t1=t1,y=y,x=x,pulse=pulse))
def sub(txt,t0,t1,size=68,y=1480):
    lines=wrap(txt,size,W-160); ims=[line(l,size,WH) for l in lines]
    h=sum(i.height for i in ims)+16*(len(ims)-1); w=max(i.width for i in ims)
    c=Image.new('RGBA',(w,h),(0,0,0,0)); yy=0
    for i in ims: c.alpha_composite(i,((w-i.width)//2,yy)); yy+=i.height+16
    add(pill(c,padx=36,pady=24,color=(0,0,0,140),radius=36),t0,t1,y)
s0=sc[0]
if spec.get('hook'):
    add(line(spec['hook'][0],140,WH),0.1,s0['t1'],200)
    if len(spec['hook'])>1: add(line(spec['hook'][1],210,YEL,sw=12),0.25,s0['t1'],350,pulse=True)
    if spec.get('hook_tag'): add(pill(line(spec['hook_tag'],56,WH),padx=32,pady=16,color=(200,60,0,215)),0.7,s0['t1'],640)
for i,s in enumerate(sc[:-1]):
    if s.get('label') and not (i==0 and spec.get('hook')): add(pill(line(s['label'],66,WH),padx=36,pady=20,color=(0,0,0,150)),s['t0']+0.1,s['t1'],190)
    if s.get('sub'): sub(s['sub'],s['t0']+0.1,s['t1'])
F=sc[-1]; t0=F['t0']
add(line(fin['title'][0],150,WH),t0+0.1,DUR,170)
if len(fin['title'])>1: add(line(fin['title'][1],190,YEL,sw=11),t0+0.25,DUR,320,pulse=True)
add(pill(line('Клуб Семейного Отдыха',68,WH),padx=40,pady=22,color=(200,60,0,215)),t0+0.6,DUR,1130)
add(line('📍 Горячий Ключ, пос. Первомайский',44,WH),t0+1.0,DUR,1300)
if fin.get('sub'):
    sub(fin['sub'][0],t0+0.2,t0+2.4,size=60,y=1400)
    if len(fin['sub'])>1: sub(fin['sub'][1],t0+2.4,DUR,size=60,y=1400)
if fin.get('cta'): add(pill(line(fin['cta'],54,(20,20,20)),padx=44,pady=24,color=(255,214,10,245),radius=60),t0+1.6,DUR,1650)
frames={}
for i,s in enumerate(sc):
    if s['kind']!='v': continue
    meta=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','csv=p=0',s['path']],capture_output=True,text=True).stdout.strip().split('\n')[0].split(',')
    w,h=int(meta[0]),int(meta[1]); dur=(s['t1']-s['t0'])+XF+0.1
    raw=subprocess.run(['ffmpeg','-v','error','-ss',str(s.get('start',0.3)),'-t',str(dur),'-i',s['path'],'-vf','fps=30','-pix_fmt','rgb24','-f','rawvideo','-'],capture_output=True).stdout
    n=len(raw)//(w*h*3); frames[i]=(np.frombuffer(raw,np.uint8)[:n*w*h*3].reshape(n,h,w,3),w,h)
def vframe(i,t):
    arr,w,h=frames[i]; s=sc[i]; idx=min(int(max(t-s['t0'],0)*FPS),len(arr)-1); im=Image.fromarray(arr[idx])
    k=max(W/w,H/h); bg=im.resize((int(w*k/8)+1,int(h*k/8)+1),Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize((int(w*k)+8,int(h*k)+8),Image.BILINEAR)
    l=(bg.width-W)//2;tp=(bg.height-H)//2; bg=bg.crop((l,tp,l+W,tp+H)); bg=Image.blend(bg,Image.new('RGB',(W,H),(0,0,0)),0.35)
    p=min(max((t-s['t0'])/(s['t1']-s['t0']),0),1); fw=int(W*(1.0+0.06*p)); fh=int(h*fw/w)
    bg.paste(im.resize((fw,fh),Image.LANCZOS),((W-fw)//2,(H-fh)//2)); return bg
def pframe(i,t):
    s=sc[i]; im=photo(s['photo']); w,h=im.size; p=min(max((t-s['t0'])/(s['t1']-s['t0']),0),1); z=1.12-0.12*p
    ch=h/z; cw=ch*9/16; cx=w/2; cy=ch/2+(h-ch)*(0.4+0.1*p)
    return im.resize((W,H),Image.BICUBIC,box=(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2))
sf=lambda i,t: pframe(i,t) if sc[i]['kind']=='p' else vframe(i,t)
g=np.zeros((H,W,4),np.uint8); y=np.arange(H)
g[...,3]=np.maximum(np.clip(1-y/900,0,1)**1.5*150,np.clip((y-(H-900))/900,0,1)**1.5*190)[:,None].astype(np.uint8); grad=Image.fromarray(g,'RGBA')
ease=lambda x: 1-(1-min(max(x,0),1))**3
def render(t):
    idx=max(i for i,s in enumerate(sc) if s['t0']<=t+1e-9); fr=sf(idx,t)
    if idx>0 and t-sc[idx]['t0']<XF: fr=Image.blend(sf(idx-1,t),fr,(t-sc[idx]['t0'])/XF)
    fr=fr.convert('RGBA'); fr.alpha_composite(grad)
    for o in ov:
        if o['t0']<=t<o['t1']:
            a=ease((t-o['t0'])/0.25)
            if o['t1']-t<0.15 and o['t1']<DUR-0.1: a*=max((o['t1']-t)/0.15,0)
            im=o['im']
            if o['pulse']:
                k=1+0.04*math.sin((t-o['t0'])*6); im=im.resize((int(im.width*k),int(im.height*k)),Image.BICUBIC)
            yoff=int((1-ease((t-o['t0'])/0.3))*40); x=(W-im.width)//2 if o['x'] is None else o['x']
            yy=o['y']+yoff-(im.height-o['im'].height)//2
            if a<1: im=im.copy(); im.putalpha(im.getchannel('A').point(lambda v:int(v*a)))
            fr.alpha_composite(im,(max(x,0),yy))
    return fr.convert('RGB')
inputs=[];flt=[];vs=[s for s in sc if s['kind']=='v']
for i,s in enumerate(vs):
    d=s['t1']-s['t0']; inputs+=['-ss',str(s.get('start',0.3)),'-t',str(d+XF),'-i',s['path']]
    flt.append(f"[{i}:a]volume={s.get('gain',8)}dB,afade=t=in:d=0.2,afade=t=out:st={max(d+XF-0.4,0.1)}:d=0.4,adelay={int(s['t0']*1000)}|{int(s['t0']*1000)}[a{i}]")
mix=''.join(f'[a{i}]' for i in range(len(vs)))
flt.append(f"{mix}amix=inputs={len(vs)}:normalize=0,apad=whole_dur={DUR},atrim=0:{DUR}[aout]")
amb='/tmp/reel_amb.m4a'
subprocess.run(['ffmpeg','-v','error','-y']+inputs+['-filter_complex',';'.join(flt),'-map','[aout]','-c:a','aac','-b:a','128k',amb],check=True)
out=f"{ROOT}/{spec['out']}"
pr=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',amb,'-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p','-c:a','copy','-t',str(DUR),'-movflags','+faststart',out],stdin=subprocess.PIPE)
for n in range(int(DUR*FPS)): pr.stdin.write(render(n/FPS).tobytes())
pr.stdin.close(); pr.wait(); print('done',out,DUR)
