import os, glob, json, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import numpy as np
P = '/home/claude/ks/photos'
OUT = '/home/claude/ks/pub'
FB = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
FX = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
FS = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
GOLD = (214, 160, 60); WH = (255, 255, 255); BK = (12, 12, 14)
def F(p, s): return ImageFont.truetype(p, s)

def photo(k):
    return Image.open(glob.glob(f'{P}/{k}.*')[0]).convert('RGB')

def cover(im, W, H, oy=0.5, ox=0.5):
    sc = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * sc + 1), int(im.height * sc + 1)), Image.LANCZOS)
    x = int((im.width - W) * ox); y = int((im.height - H) * oy)
    return im.crop((x, y, x + W, y + H))

def grad(W, H, start, amax, top=200):
    g = np.zeros((H, W, 4), np.uint8); y = np.arange(H)
    a = np.clip((y - start) / (H - start), 0, 1) ** 1.2 * amax
    a = np.maximum(a, np.clip(1 - y / top, 0, 1) * 140)
    g[..., 3] = a[:, None].astype(np.uint8)
    return Image.fromarray(g, 'RGBA')

def wrap(d, text, font, maxw):
    out = []
    for para in text.split('\n'):
        words = para.split(); cur = ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if d.textlength(t, font=font) <= maxw: cur = t
            else: out.append(cur); cur = w
        out.append(cur)
    return out

def brand(d, x, y, size=34):
    f = F(FX, size); t = 'КОМПЛЕКС СТРОЙ'; w = d.textlength(t, font=f); a, de = f.getmetrics()
    d.rounded_rectangle((x, y, x + w + 48, y + a + de + 24), 28, fill=GOLD)
    d.text((x + 24, y + 10), t, font=f, fill=BK)

def text_block(d, lines_spec, x, ybottom, maxw):
    # lines_spec: list of (text, font, color, gap_after)
    rendered = []
    for text, font, col, gap in lines_spec:
        for ln in wrap(d, text, font, maxw):
            a, de = font.getmetrics(); rendered.append((ln, font, col, a + de));
        rendered.append((None, None, None, gap))
    total = sum(r[3] for r in rendered)
    y = ybottom - total
    for ln, font, col, h in rendered:
        if ln: d.text((x, y), ln, font=font, fill=col, stroke_width=3, stroke_fill=(0, 0, 0))
        y += h

def slide(spec, i, n, path):
    W, H = 1080, 1350
    im = cover(photo(spec['photo']), W, H, spec.get('oy', 0.5), spec.get('ox', 0.5))
    im = ImageEnhance.Contrast(im).enhance(1.06).convert('RGBA')
    cov = spec.get('cover', False)
    im.alpha_composite(grad(W, H, 380 if cov else 520, 240))
    d = ImageDraw.Draw(im)
    brand(d, 50, 50)
    if not cov:
        f = F(FX, 34); t = f'{i}/{n}'; w = d.textlength(t, font=f)
        d.rounded_rectangle((W - 50 - w - 48, 50, W - 50, 50 + 70), 28, fill=(0, 0, 0, 170))
        d.text((W - 50 - w - 24, 60), t, font=f, fill=WH)
    L = []
    L.append((spec['title'], F(FB, 92 if cov else 70), GOLD, 22))
    if spec.get('body'): L.append((spec['body'], F(FS, 46), WH, 16))
    if spec.get('foot'): L.append((spec['foot'], F(FX, 40), (235, 235, 235), 0))
    text_block(d, L, 70, H - 70, W - 140)
    im.convert('RGB').save(path, quality=92)

def story(spec, path):
    W, H = 1080, 1920
    im = cover(photo(spec['photo']), W, H, spec.get('oy', 0.5), spec.get('ox', 0.5))
    im = ImageEnhance.Contrast(im).enhance(1.06).convert('RGBA')
    im.alpha_composite(grad(W, H, 700, 235, top=300))
    d = ImageDraw.Draw(im)
    brand(d, 60, 250, 38)
    L = [(spec['title'], F(FB, 96), WH, 26)]
    if spec.get('body'): L.append((spec['body'], F(FS, 52), (235, 235, 235), 40))
    text_block(d, L, 70, 1330, W - 140)
    # CTA box
    f1 = F(FB, 58); f2 = F(FX, 44)
    cta = spec.get('cta', 'СМЕТА И ПРОСЧЁТ — БЕСПЛАТНО'); sub = spec.get('sub', 'Пишите в директ «СМЕТА»')
    d.rounded_rectangle((70, 1380, W - 70, 1600), 36, fill=GOLD)
    for k, (t, f, y) in enumerate([(cta, f1, 1410), (sub, f2, 1500)]):
        while d.textlength(t, font=f) > W - 200: f = ImageFont.truetype(f.path, f.size - 2)
        w = d.textlength(t, font=f); d.text(((W - w) / 2, y), t, font=f, fill=BK)
    f3 = F(FS, 40); t = 'Краснодар • Горячий Ключ'; w = d.textlength(t, font=f3)
    d.text(((W - w) / 2, 1630), t, font=f3, fill=WH, stroke_width=2, stroke_fill=(0, 0, 0))
    im.convert('RGB').save(path, quality=92)

END = {'title': 'Посчитаем ваш дом бесплатно', 'body': 'Пришлите проект или идею — подготовим смету и ответим на вопросы.', 'foot': 'Пишите в директ «СМЕТА»  •  Краснодар и Горячий Ключ'}

CAROUSELS = {
 'c1_etapy': [
  dict(photo='a_house', cover=True, title='Как строится дом под ключ', body='7 этапов — от участка до ключей. Листайте →'),
  dict(photo='a_excav', title='1. Земляные работы', body='Разметка участка, планировка и подготовка основания под фундамент.'),
  dict(photo='r_pour', title='2. Фундамент', body='Подушка из щебня, утеплитель, армирование в два слоя и заливка бетона.'),
  dict(photo='r_walls', title='3. Стены', body='Гидроизоляция цоколя, первый ряд строго по уровню, кладка газоблока на клей.'),
  dict(photo='a_roof', title='4. Кровля', body='Стропильная система, утепление и кровельное покрытие.'),
  dict(photo='a_window', title='5. Окна, двери, фасад', body='Закрываем контур и делаем дом красивым снаружи.'),
  dict(photo='a_final', oy=0.6, **END)],
 'c2_fundament': [
  dict(photo='r_mesh2', cover=True, title='5 правил фундамента, который не треснет', body='Сохраните, пригодится →'),
  dict(photo='r_geotex', title='1. Геотекстиль', body='Не даёт грунту смешиваться со щебнем — основание не «плывёт».'),
  dict(photo='r_gravel', title='2. Щебёночная подушка', body='Ровное и прочное основание под плиту.'),
  dict(photo='r_tramb', title='3. Трамбовка', body='Уплотняем каждый слой виброплитой, чтобы потом ничего не просело.'),
  dict(photo='r_mesh', title='4. Армирование в 2 слоя', body='Плита работает на изгиб сверху и снизу — поэтому арматура в два слоя.'),
  dict(photo='r_pour', title='5. Выдержка 3–4 недели', body='Бетон набирает прочность. Только после этого начинаем стены.'),
  dict(photo='r_hydro', **END)],
 'c3_smeta': [
  dict(photo='a_plans', cover=True, title='Из чего складывается смета на дом', body='Разбираем по статьям →'),
  dict(photo='a_excav', title='Подготовка участка', body='Земляные работы, разметка, подъезд техники.'),
  dict(photo='r_pour', title='Фундамент', body='Тип фундамента зависит от грунта и проекта — его считаем первым.'),
  dict(photo='a_mason', title='Коробка дома', body='Стены, перегородки, перемычки, армопояс.'),
  dict(photo='a_roof', title='Кровля', body='Стропила, утепление, покрытие, водосток.'),
  dict(photo='a_window', title='Контур и инженерия', body='Окна, двери, фасад и инженерные сети.'),
  dict(photo='a_house', title='Без скрытых платежей', body='Смета до начала работ, договор и поэтапная оплата.', foot='Пишите в директ «СМЕТА» — посчитаем бесплатно')],
 'c4_gazoblok': [
  dict(photo='r_walls2', cover=True, title='Почему мы строим из газоблока', body='4 причины →'),
  dict(photo='r_first', title='Тёплый', body='Пористая структура хорошо держит тепло — зимой теплее, летом прохладнее.'),
  dict(photo='a_mason', title='Быстрый', body='Крупные ровные блоки — стены растут быстрее, чем из кирпича.'),
  dict(photo='r_walls3', title='Ровный', body='Кладка на тонкий слой клея: меньше мостиков холода и ровные стены под отделку.'),
  dict(photo='a_box', title='Не горит', body='Газобетон — негорючий минеральный материал.'),
  dict(photo='a_aerial', title='Дом из газоблока под ключ', body='От фундамента до готового дома — одной командой.'),
  dict(photo='a_final', oy=0.6, **END)],
 'c5_oshibki': [
  dict(photo='a_aerial2', cover=True, title='5 ошибок при строительстве дома', body='Которые потом стоят дороже всего →'),
  dict(photo='r_strip', title='1. Экономить на фундаменте', body='Трещины в стенах почти всегда начинаются снизу.'),
  dict(photo='r_pour', title='2. Торопиться со стенами', body='Бетону нужно 3–4 недели, чтобы набрать прочность.'),
  dict(photo='r_hydro', title='3. Забыть про гидроизоляцию', body='Без неё влага из фундамента уходит в стены.'),
  dict(photo='a_plans', title='4. Строить без сметы', body='Без расчёта бюджет «растёт» на каждом этапе.'),
  dict(photo='a_brick', title='5. Нанимать разные бригады', body='Когда за дом отвечает один подрядчик — не на кого перекладывать ответственность.'),
  dict(photo='a_house', **END)],
 'c6_kak_rabotaem': [
  dict(photo='a_plans', cover=True, title='Как мы работаем: от заявки до ключей', body='5 шагов →'),
  dict(photo='a_aerial2', title='1. Заявка и выезд', body='Обсуждаем идею, смотрим участок.'),
  dict(photo='a_plans', ox=0.3, title='2. Смета бесплатно', body='Считаем стоимость до начала работ — без скрытых платежей.'),
  dict(photo='a_mason', title='3. Договор', body='Фиксируем сроки, состав работ и поэтапную оплату.'),
  dict(photo='r_walls', title='4. Стройка с фотоотчётами', body='Видите каждый этап, даже если не на месте.'),
  dict(photo='a_land', title='5. Сдача и гарантия', body='Принимаете готовый дом, а мы даём гарантию на работы.'),
  dict(photo='a_final', oy=0.6, **END)],
}

STORIES = {
 's1': dict(photo='a_house', title='Строим дома под ключ', body='Фундамент, стены, кровля, фасад — одной командой.'),
 's2': dict(photo='r_pour', title='Как мы заливаем фундамент', body='Новый ролик уже в профиле — посмотрите до конца.'),
 's3': dict(photo='a_plans', title='Сколько будет стоить ваш дом?', body='Пришлите проект или идею — посчитаем.'),
 's4': dict(photo='r_walls2', title='Дом из газоблока', body='Тёплый, ровный и быстрый в строительстве.'),
 's5': dict(photo='a_final', oy=0.6, title='Мечтаете о своём доме?', body='Начните с бесплатного расчёта.'),
 's6': dict(photo='r_walls', title='Стройка с фотоотчётами', body='Каждый этап — у вас в телефоне.'),
 's7': dict(photo='a_land', title='От участка до ключей', body='Работаем в Краснодаре и Горячем Ключе.'),
}

if __name__ == '__main__':
    for cid, slides in CAROUSELS.items():
        os.makedirs(f'{OUT}/carousels/{cid}', exist_ok=True)
        for i, s in enumerate(slides, 1): slide(s, i, len(slides), f'{OUT}/carousels/{cid}/{i:02d}.jpg')
    os.makedirs(f'{OUT}/stories', exist_ok=True)
    for sid, s in STORIES.items(): story(s, f'{OUT}/stories/{sid}.jpg')
    print('ok')
