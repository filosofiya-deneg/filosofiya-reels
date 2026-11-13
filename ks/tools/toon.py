"""Flat cartoon construction scene renderer. scene(p, t, style) -> PIL RGB 1080x1920.
p: build progress 0..1, t: time seconds (for idle motion)."""
import math
from PIL import Image, ImageDraw

W, H = 1080, 1920
S = 2  # supersampling
GY = 1380  # ground line

def lerp(a, b, x): return a + (b - a) * x
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(p, a, b): return clamp((p - a) / (b - a))
def mix(c1, c2, x): return tuple(int(lerp(c1[i], c2[i], x)) for i in range(3))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)

STYLES = {
    'a': dict(wall=(236, 233, 224), roof=(176, 74, 52), roof2=(150, 60, 42), trim=(120, 82, 56), floors=1, door=(150, 98, 58)),
    'b': dict(wall=(245, 240, 228), roof=(60, 72, 92), roof2=(44, 54, 72), trim=(214, 160, 60), floors=2, door=(90, 62, 44)),
}

class Pen:
    def __init__(self, im): self.d = ImageDraw.Draw(im)
    def rect(self, x0, y0, x1, y1, fill, r=0, outline=None, w=0):
        b = (x0 * S, y0 * S, x1 * S, y1 * S)
        if r: self.d.rounded_rectangle(b, r * S, fill=fill, outline=outline, width=w * S)
        else: self.d.rectangle(b, fill=fill, outline=outline, width=w * S)
    def ell(self, x0, y0, x1, y1, fill, outline=None, w=0): self.d.ellipse((x0 * S, y0 * S, x1 * S, y1 * S), fill=fill, outline=outline, width=w * S)
    def poly(self, pts, fill, outline=None): self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill, outline=outline)
    def line(self, pts, fill, w): self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(w * S), joint='curve')

OUT = (40, 34, 30)

def sky(pen, dusk):
    top = mix((96, 178, 240), (60, 60, 120), dusk); bot = mix((196, 230, 252), (250, 170, 110), dusk)
    for i in range(0, GY, 8):
        pen.rect(0, i, W, i + 8, mix(top, bot, i / GY))

def sun(pen, dusk, t):
    y = lerp(260, 900, dusk); c = mix((255, 214, 80), (255, 140, 60), dusk)
    r = 70 + 4 * math.sin(t * 2)
    pen.ell(820 - r - 20, y - r - 20, 820 + r + 20, y + r + 20, mix(c, (255, 255, 255), 0.5))
    pen.ell(820 - r, y - r, 820 + r, y + r, c)

def cloud(pen, x, y, s, col=(255, 255, 255)):
    for dx, dy, r in [(0, 0, 50), (55, -25, 60), (115, 0, 48), (60, 15, 50)]:
        pen.ell(x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s, col)

def hills(pen, dusk):
    c1 = mix((134, 196, 110), (90, 120, 90), dusk); c2 = mix((110, 176, 92), (70, 100, 74), dusk)
    pen.ell(-300, GY - 260, 600, GY + 300, c1); pen.ell(400, GY - 200, 1400, GY + 300, c2)

def ground(pen, grass, dusk):
    dirt = mix((176, 130, 86), (130, 96, 66), dusk)
    g = mix(mix((98, 180, 80), (70, 120, 64), dusk), dirt, 1 - grass)
    pen.rect(0, GY, W, H, g)
    pen.rect(0, GY, W, GY + 14, mix(g, (0, 0, 0), 0.12))

def tree(pen, x, y, s, dusk):
    pen.rect(x - 12 * s, y - 90 * s, x + 12 * s, y, (120, 80, 50))
    c = mix((70, 160, 70), (50, 100, 60), dusk)
    for dx, dy, r in [(0, -150, 70), (-45, -110, 55), (45, -110, 55)]:
        pen.ell(x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s, c, OUT, 3)

def worker(pen, x, y, t, s=1.0, ph=0, hat=(255, 200, 40)):
    b = 6 * math.sin(t * 6 + ph) * s
    pen.rect(x - 18 * s, y - 60 * s, x - 4 * s, y, (60, 70, 100), r=4)  # legs
    pen.rect(x + 4 * s, y - 60 * s, x + 18 * s, y, (60, 70, 100), r=4)
    pen.rect(x - 28 * s, y - 130 * s + b, x + 28 * s, y - 55 * s, (255, 120, 30), r=12, outline=OUT, w=3)  # vest
    pen.rect(x - 28 * s, y - 100 * s + b, x + 28 * s, y - 92 * s + b, (230, 230, 230))
    pen.ell(x - 26 * s, y - 182 * s + b, x + 26 * s, y - 128 * s + b, (250, 210, 170), OUT, 3)  # head
    pen.ell(x - 8 * s, y - 160 * s + b, x - 2 * s, y - 154 * s + b, OUT); pen.ell(x + 6 * s, y - 160 * s + b, x + 12 * s, y - 154 * s + b, OUT)
    pen.line([(x - 6 * s, y - 143 * s + b), (x + 2 * s, y - 140 * s + b), (x + 10 * s, y - 143 * s + b)], OUT, 3)
    pen.poly([(x - 32 * s, y - 166 * s + b), (x + 32 * s, y - 166 * s + b), (x + 24 * s, y - 192 * s + b), (x - 24 * s, y - 192 * s + b)], hat, OUT)
    a = math.sin(t * 5 + ph) * 0.6
    pen.line([(x + 26 * s, y - 120 * s + b), (x + 26 * s + 40 * s * math.cos(a), y - 120 * s + b + 40 * s * math.sin(a))], (255, 120, 30), 12 * s)

def excavator(pen, x, y, t, arm):
    pen.rect(x - 130, y - 50, x + 110, y, (60, 60, 64), r=24)  # tracks
    for i in range(5): pen.ell(x - 115 + i * 52, y - 42, x - 85 + i * 52, y - 12, (120, 120, 126))
    pen.rect(x - 110, y - 150, x + 90, y - 50, (255, 196, 30), r=14, outline=OUT, w=3)
    pen.rect(x - 90, y - 230, x - 10, y - 150, (255, 196, 30), r=10, outline=OUT, w=3)
    pen.rect(x - 78, y - 218, x - 22, y - 168, (170, 220, 250), r=6)
    a = -0.6 + 0.5 * math.sin(arm)
    jx, jy = x + 70 + 170 * math.cos(a), y - 140 + 170 * math.sin(a)
    pen.line([(x + 70, y - 140), (jx, jy)], (255, 196, 30), 26)
    b = a + 1.7 + 0.4 * math.sin(arm)
    kx, ky = jx + 120 * math.cos(b), jy + 120 * math.sin(b)
    pen.line([(jx, jy), (kx, ky)], (255, 196, 30), 20)
    pen.poly([(kx - 30, ky - 10), (kx + 30, ky - 10), (kx + 20, ky + 30), (kx - 25, ky + 25)], (80, 80, 84), OUT)

def mixer(pen, x, y, t):
    pen.rect(x - 160, y - 130, x + 160, y - 30, (230, 230, 236), r=10, outline=OUT, w=3)
    pen.rect(x + 80, y - 190, x + 170, y - 30, (220, 60, 50), r=12, outline=OUT, w=3)
    pen.rect(x + 100, y - 175, x + 155, y - 130, (170, 220, 250), r=6)
    rot = t * 3
    pen.ell(x - 150, y - 230, x + 60, y - 110, (255, 160, 40), OUT, 3)
    for k in range(3):
        a = rot + k * 2.1
        pen.line([(x - 45 + 80 * math.cos(a), y - 170 + 40 * math.sin(a)), (x - 45 - 80 * math.cos(a), y - 170 - 40 * math.sin(a))], (230, 120, 30), 8)
    for wx in (x - 110, x - 10, x + 120):
        pen.ell(wx - 34, y - 64, wx + 34, y + 4, (50, 50, 54)); pen.ell(wx - 14, y - 44, wx + 14, y - 16, (160, 160, 166))

def house(pen, p, st, dusk, t):
    X0, X1 = 200, 880
    floors = st['floors']; FH = 300 if floors == 1 else 230
    WH = FH * floors; top = GY - 30 - WH
    # pit
    dig = seg(p, 0.02, 0.14)
    if 0 < dig and p < 0.2:
        pen.rect(X0 - 40, GY, X0 - 40 + (X1 - X0 + 80) * dig, GY + 90, (120, 84, 54))
    # gravel + rebar + slab
    gr = seg(p, 0.13, 0.17); rb = seg(p, 0.17, 0.21); sl = seg(p, 0.21, 0.27)
    if gr > 0:
        pen.rect(X0 - 40, GY + 90 - 90 * gr, X1 + 40, GY + 90, (150, 150, 156))
        for i in range(int(40 * gr)):
            xx = X0 - 30 + (i * 97) % (X1 - X0 + 60); yy = GY + 20 + (i * 53) % 60
            pen.ell(xx, yy, xx + 14, yy + 10, (120, 120, 126))
    if rb > 0 and sl < 1:
        n = int(18 * rb)
        for i in range(n):
            xx = X0 - 30 + i * (X1 - X0 + 60) / 17
            pen.line([(xx, GY - 6), (xx, GY + 40)], (90, 60, 50), 5)
        pen.line([(X0 - 30, GY), (X0 - 30 + (X1 - X0 + 60) * rb, GY)], (90, 60, 50), 5)
    if sl > 0:
        h = 40 * sl
        pen.rect(X0 - 40, GY + 10 - h, X1 + 40, GY + 10, (190, 190, 196), outline=OUT, w=3)
    if p < 0.27: return
    # walls by rows
    wl = seg(p, 0.28, 0.52)
    rows = int(WH / 30); shown = int(rows * wl + 0.999)
    win_y = [(top + f * FH + FH * 0.28, top + f * FH + FH * 0.72) for f in range(floors)]
    wins = [(260, 400), (680, 820)] if floors == 1 else [(250, 380), (475, 605), (700, 830)]
    door = (480, 600)
    for r in range(shown):
        y = GY - 30 - (r + 1) * 30
        off = 0 if r % 2 == 0 else 30
        x = X0 - off
        c = st['wall'] if p > 0.7 else (232, 232, 226)
        while x < X1:
            xa, xb = max(x, X0), min(x + 60, X1)
            pen.rect(xa, y, xb, y + 30, c, outline=(200, 196, 186) if p < 0.7 else None, w=2)
            x += 60
    ytop_built = GY - 30 - shown * 30
    hole = (70, 62, 58)
    for f, (a, b) in enumerate(win_y):
        for wa, wb in wins:
            ya = max(a, ytop_built)
            if ya < b: pen.rect(wa, ya, wb, b, hole)
    ya = max(GY - 230, ytop_built)
    if ya < GY - 30: pen.rect(door[0], ya, door[1], GY - 30, hole)
    if wl < 1: return
    # roof
    rf = seg(p, 0.53, 0.66)
    apex = top - 220
    if rf > 0:
        n = int(9 * min(1, rf * 2))
        for i in range(n):
            xx = X0 - 60 + i * (X1 - X0 + 120) / 8
            ax = 540
            pen.line([(xx, top), (lerp(xx, ax, 0.95), lerp(top, apex, 0.95))], (170, 120, 70), 10)
        pen.line([(X0 - 60, top), (540, apex), (X1 + 60, top)], (170, 120, 70), 12)
        cov = seg(rf, 0.4, 1)
        if cov > 0:
            yb = top; yt = lerp(top, apex, cov)
            xl = lerp(X0 - 60, 540, (yb - yt) / (top - apex)); xr = lerp(X1 + 60, 540, (yb - yt) / (top - apex))
            pen.poly([(X0 - 60, top), (X1 + 60, top), (xr, yt), (xl, yt)] if cov < 1 else [(X0 - 70, top + 6), (X1 + 70, top + 6), (540, apex - 10)], st['roof'], OUT)
            for k in range(1, 6):
                yy = lerp(top, apex, k / 6)
                if yy >= yt:
                    xa = lerp(X0 - 60, 540, k / 6); xb = lerp(X1 + 60, 540, k / 6)
                    pen.line([(xa, yy), (xb, yy)], st['roof2'], 4)
            if cov >= 1:
                pen.rect(700, apex + 70, 750, apex + 150, (150, 80, 60), outline=OUT, w=3)  # chimney
    # windows/door
    wd = seg(p, 0.67, 0.78)
    if wd > 0:
        k = 0
        for f, (a, b) in enumerate(win_y):
            for wa, wb in wins:
                k += 1
                if wd * (len(wins) * floors + 1) < k: continue
                if floors == 1 or True:
                    if f == floors - 1 and floors > 1 and False: continue
                if not (door[0] <= wa < door[1] and f == floors - 1 and floors == 1):
                    glass = mix((150, 210, 245), (255, 214, 120), dusk)
                    pen.rect(wa, a, wb, b, glass, outline=st['trim'], w=8)
                    pen.line([((wa + wb) / 2, a), ((wa + wb) / 2, b)], st['trim'], 6)
                    pen.line([(wa, (a + b) / 2), (wb, (a + b) / 2)], st['trim'], 6)
        if wd > 0.8:
            pen.rect(door[0], GY - 230, door[1], GY - 30, st['door'], outline=OUT, w=3)
            pen.ell(door[1] - 30, GY - 140, door[1] - 16, GY - 126, (255, 214, 80))
    # porch
    if p > 0.78:
        pen.rect(440, GY - 30, 640, GY + 6, (200, 196, 190), outline=OUT, w=2)

def fence_path(pen, g, dusk):
    if g <= 0: return
    pen.poly([(470, GY + 6), (610, GY + 6), (700 + 200 * g, H), (380 - 200 * g, H)], mix((214, 200, 176), (170, 150, 130), dusk))
    for i in range(int(8 * g)):
        x = 30 + i * 30
        pen.rect(x, GY - 70, x + 18, GY + 10, (230, 230, 230), outline=OUT, w=2)
    for i in range(int(8 * g)):
        x = W - 48 - i * 30
        pen.rect(x, GY - 70, x + 18, GY + 10, (230, 230, 230), outline=OUT, w=2)

def scene(p, t, style='a', workers=True):
    st = STYLES[style]
    im = Image.new('RGB', (W * S, H * S)); pen = Pen(im)
    dusk = ease(seg(p, 0.86, 1.0)) * 0.8
    sky(pen, dusk); sun(pen, dusk, t)
    for i, (cx, cy, s) in enumerate([(80, 300, 1.0), (520, 200, 0.8), (300, 520, 0.7)]):
        cloud(pen, (cx + t * 18 * (1 + i * 0.3)) % (W + 300) - 150, cy, s, mix((255, 255, 255), (255, 210, 190), dusk))
    hills(pen, dusk)
    grass = ease(seg(p, 0.8, 0.92))
    ground(pen, grass, dusk)
    if p < 0.02:  # stakes & string
        for x in (160, 920):
            pen.rect(x, GY - 60, x + 12, GY + 10, (170, 120, 70))
        pen.line([(166, GY - 50), (926, GY - 50)], (240, 80, 60), 3)
    house(pen, p, st, dusk, t)
    fence_path(pen, ease(seg(p, 0.82, 0.95)), dusk)
    tg = ease(seg(p, 0.86, 0.96))
    if tg > 0:
        tree(pen, 110, GY + 40, 1.1 * tg, dusk); tree(pen, 980, GY + 60, 1.2 * tg, dusk)
    # machines & workers
    if p < 0.16:
        ex = lerp(-200, 840, ease(seg(p, 0.0, 0.05))) if p < 0.05 else 840
        excavator(pen, ex, GY + 150, t, t * 3)
    if 0.19 < p < 0.29:
        mixer(pen, lerp(1300, 900, ease(seg(p, 0.19, 0.22))), GY + 170, t)
    if workers and 0.12 < p < 0.8:
        worker(pen, 140, GY + 260, t, 1.4, 0)
        if p > 0.27: worker(pen, 950, GY + 280, t, 1.4, 1.7, hat=(255, 255, 255))
    return im.resize((W, H), Image.LANCZOS)

if __name__ == '__main__':
    import sys
    ims = [scene(p, p * 10, sys.argv[1] if len(sys.argv) > 1 else 'a') for p in (0.0, 0.08, 0.18, 0.24, 0.4, 0.6, 0.72, 0.9, 1.0)]
    sheet = Image.new('RGB', (9 * 240, 427))
    for i, im in enumerate(ims): sheet.paste(im.resize((240, 427)), (i * 240, 0))
    sheet.save('/home/claude/ks/sheets/toon.png')
