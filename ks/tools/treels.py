import subprocess, os, sys, math
sys.argv_saved = sys.argv; sys.argv = ['x']
import build as B
import toon as T
B.STEP_Y = 1540
from PIL import Image, ImageDraw
OUT = '/home/claude/ks/tout'; os.makedirs(OUT, exist_ok=True)
FPS = 30

_cache = {}
def ovl(kind, *a):
    key = (kind,) + tuple(str(x) for x in a)
    if key not in _cache:
        p = f'{OUT}/ov_{abs(hash(key))}.png'
        if kind == 'hook': B.ov_hook(p, *a)
        else: B.ov_step(p, *a)
        _cache[key] = Image.open(p).convert('RGBA')
    return _cache[key]

def with_alpha(im, a):
    if a >= 1: return im
    r, g, b, al = im.split(); al = al.point(lambda v: int(v * a)); return Image.merge('RGBA', (r, g, b, al))

def icon(kind, s):
    """cartoon icon on transparent canvas 600x600 scaled by s"""
    S = 2; c = Image.new('RGBA', (600 * S, 600 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    O = (40, 34, 30); G = (214, 160, 60); w = 8 * S
    def R(*b, **k): d.rounded_rectangle([v * S for v in b], k.get('r', 30) * S, fill=k['f'], outline=O, width=w)
    def L(pts, col, ww): d.line([(x * S, y * S) for x, y in pts], fill=col, width=ww * S, joint='curve')
    d.ellipse((20 * S, 20 * S, 580 * S, 580 * S), fill=(255, 255, 255, 235), outline=G, width=12 * S)
    if kind in ('smeta', 'dogovor'):
        R(170, 110, 430, 470, f=(250, 250, 245), r=20)
        for i in range(5): L([(210, 180 + i * 50), (390 - (i % 2) * 60, 180 + i * 50)], (170, 170, 170), 12)
        if kind == 'smeta':
            for i in range(3): L([(200, 185 + i * 50), (215, 200 + i * 50), (240, 168 + i * 50)], (60, 170, 80), 12)
        else:
            L([(220, 420), (260, 395), (290, 425), (330, 395), (370, 420)], (40, 80, 200), 8)
            d.polygon([(x * S, y * S) for x, y in [(380, 300), (470, 210), (495, 235), (405, 325)]], fill=G, outline=O)
    elif kind == 'photo':
        R(200, 90, 400, 500, f=(50, 50, 60), r=36)
        R(222, 140, 378, 430, f=(150, 210, 245), r=6)
        d.polygon([(x * S, y * S) for x, y in [(250, 330), (300, 285), (350, 330)]], fill=(176, 74, 52))
        d.rectangle((262 * S, 330 * S, 338 * S, 400 * S), fill=(236, 233, 224))
        d.rectangle((222 * S, 400 * S, 378 * S, 430 * S), fill=(98, 180, 80))
    elif kind == 'shield':
        d.polygon([(x * S, y * S) for x, y in [(300, 100), (470, 160), (450, 340), (300, 490), (150, 340), (130, 160)]], fill=G, outline=O)
        L([(220, 300), (280, 360), (390, 230)], (255, 255, 255), 30)
    c = c.resize((int(600 * s), int(600 * s)), Image.LANCZOS)
    return c

def render(name, dur, frame_fn, cover_t):
    out = f'{OUT}/{name}_video.mp4'; tmp = out[:-4] + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    n = int(dur * FPS)
    for i in range(n):
        t = i / FPS
        fr = frame_fn(t)
        if abs(t - cover_t) < 0.5 / FPS: fr.save(f'{OUT}/{name}_cover.jpg', quality=92)
        p.stdin.write(fr.tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    return out

def overlay(fr, ov, a):
    base = fr.convert('RGBA'); base.alpha_composite(with_alpha(ov, a)); return base.convert('RGB')

def build_timeline(style, dur, hook, steps):
    """steps: list of (p_start, label) ; label = (n, text) or 'hook'"""
    def f(t):
        p = min(1.0, t / (dur - 0.5))
        fr = T.scene(p, t, style)
        cur = None; start = 0
        for ps, lab in steps:
            if p >= ps: cur, start = lab, ps
        if cur is None: return fr
        a = min(1, (p - start) * dur / 0.25)
        ov = ovl('hook', *hook) if cur == 'hook' else ovl('step', cur[0], cur[1])
        return overlay(fr, ov, a)
    return f

def reel_c(dur_hook=2.5, per=2.8):
    items = [('smeta', 1, 'Смета до начала работ', ['без скрытых платежей']), ('dogovor', 2, 'Договор', ['и поэтапная оплата']),
             ('photo', 3, 'Фотоотчёты', ['с каждого этапа стройки']), ('shield', 4, 'Гарантия на работы', ['дом, в котором спокойно'])]
    hook = (['Боитесь, что стройка'], 'ВЫЙДЕТ ДОРОЖЕ?', 'вот как мы это исключаем ↓')
    def f(t):
        if t < dur_hook:
            p = 0.3 + 0.25 * t / dur_hook
            fr = T.scene(p, t, 'a'); return overlay(fr, ovl('hook', *hook), min(1, t / 0.25))
        k = min(3, int((t - dur_hook) / per)); tt = t - dur_hook - k * per
        p = 0.55 + 0.45 * (t - dur_hook) / (per * 4)
        fr = T.scene(min(1, p), t, 'a').convert('RGBA')
        kind, n, title, sub = items[k]
        sc = 0.3 + 0.7 * (1 - (1 - min(1, tt / 0.35)) ** 3) + 0.03 * math.sin(tt * 3)
        ic = icon(kind, 0.9 * sc)
        fr.alpha_composite(ic, (540 - ic.width // 2, 560 - ic.height // 2))
        return overlay(fr.convert('RGB'), ovl('step', n, title, None, sub), min(1, tt / 0.25))
    return f, dur_hook + 4 * per

REELS = {
 'k1_kak_stroitsya_dom': dict(style='a', dur=16.5, hook=(['Как строится дом?'], 'ЗА 15 СЕКУНД', 'смотри до конца ↓'),
     steps=[(0, 'hook'), (0.13, (1, 'Фундамент')), (0.28, (2, 'Стены из газоблока')), (0.53, (3, 'Кровля')),
            (0.67, (4, 'Окна и двери')), (0.8, (None, 'Ваш дом под ключ'))], end='Хотите такой же дом?'),
 'k2_odin_podryadchik': dict(style='b', dur=17.0, hook=(['Один подрядчик —'], 'ВЕСЬ ДОМ', 'от фундамента до ключей ↓'),
     steps=[(0, 'hook'), (0.12, (1, 'Земляные работы')), (0.16, (2, 'Фундамент')), (0.28, (3, 'Коробка дома')),
            (0.53, (4, 'Кровля')), (0.67, (5, 'Окна и двери')), (0.8, (6, 'Благоустройство'))], end='Строим дома под ключ'),
}

if __name__ == '__main__':
    which = sys.argv_saved[1:] or ['k1_kak_stroitsya_dom', 'k2_odin_podryadchik', 'k3_bez_skrytyh']
    for k in which:
        if k == 'k3_bez_skrytyh':
            fn, dur = reel_c(); render(k, dur, fn, 1.5); endt = 'Узнайте точную цену'
        else:
            c = REELS[k]; render(k, c['dur'], build_timeline(c['style'], c['dur'], c['hook'], c['steps']), 1.5); endt = c['end']
        end = f'{OUT}/{k}_end.png'; B.endcard(end, endt)
        B.OUT = OUT; e = B.still_seg(f'{k}_99', end, 4.0)
        lst = f'{OUT}/{k}_list.txt'; open(lst, 'w').write(f"file '{OUT}/{k}_video.mp4'\nfile '{e}'\n")
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', f'{OUT}/{k}_full.mp4'], check=True)
        print(k, 'ok')
