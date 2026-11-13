# «Комплекс Строй» — 3D-мультсериал. Библия проекта

## Стиль (одинаковый для ВСЕХ генераций)
Референсы владельца: игрушечный 3D-домик из белых газоблоков с оранжевыми стропилами; плотный заказчик в синем; строитель в жёлтой каске и оранжевом жилете. Копировать стоковые картинки нельзя — только стиль и пропорции.
STYLE = "soft rounded clay-like 3D look, modern feature-length 3D animated film style, Pixar/DreamWorks-like quality, expressive stylized characters, soft cinematic lighting, warm rim light, saturated colors, detailed PBR materials, realistic soft shadows, shallow depth of field, comedic facial expressions, 8k render"
NEG = "realistic photo, live action, 2D, anime, sketch, text, watermark, logo distortion, extra fingers, deformed hands, different face, inconsistent outfit"

## Персонаж 1 — Прораб Михалыч (лицо «Комплекс Строй») — ОБНОВЛЕНО 13.11
Фиксируем навсегда:
- мужчина 40 лет, крепкое телосложение, широкие плечи, короткая аккуратная тёмная борода с проседью, короткая стрижка, карие глаза; уверенный и доброжелательный
- ЧЁРНАЯ фирменная футболка: на груди логотип «КС» (домик-крыша, серебро + золото) и крупная БЕЛАЯ надпись «КОМПЛЕКС СТРОЙ», под ней золотом «строительство полного цикла» — как на фирменной футболке владельца (фото в «мои фото (для двойника)»)
- на левом рукаве небольшой логотип «КС»
- тёмно-серые рабочие брюки, строительные ботинки
- жёлтая каска — только на стройплощадке, когда нужно по сцене
- выразительная мультяшная мимика; профессионал, с юмором объясняет ошибки заказчиков
- надпись на футболке после генерации ВСЕГДА заменяется на эталонный принт (photos/print_decal.png) при обработке кадров — генерация букв не используется

PROMPT_BUILDER = "a confident friendly 40-year-old construction foreman, strong stocky build, broad shoulders, short neat dark beard with a little grey, short haircut, brown eyes, plain black crew-neck t-shirt with a large white-and-gold company logo print on the chest and a small logo on the left sleeve, dark grey work trousers, sturdy work boots"
(для сцен на стройке добавлять: ", yellow hard hat")

## Персонаж 2 — Заказчик Вадим
- мужчина ~38 лет, плотный, с животиком, широкая шея, руки короткие (пропорции как в референсе владельца)
- круглое широкое лицо, большой нос, маленькие карие глаза, густые брови, тёмно-каштановые волосы с коком
- однотонная синяя футболка-поло, тёмно-синие брюки, коричневый ремень, коричневые туфли, на запястье смарт-часы
- в руке почти всегда смартфон
- характер: суетливый, хитрый «эконом», эмоции очень яркие

PROMPT_CLIENT = "a chubby 38-year-old man with a belly, wide neck, short arms, round wide face, big nose, small brown eyes, thick eyebrows, dark brown hair with a quiff, plain blue polo t-shirt, dark navy trousers, brown belt, brown shoes, smartwatch on wrist, holding a smartphone"

## Референсы (генерировать первыми, вертикально 9:16 или 1:1)
1. Михалыч — полный рост: "{PROMPT_BUILDER}, full body turnaround character sheet, front view, three-quarter view, side view, back view, neutral pose, plain light grey studio background, {STYLE}"
2. Михалыч — портрет: "{PROMPT_BUILDER}, close-up portrait, friendly confident smile, looking at camera, plain light grey background, {STYLE}"
3. Михалыч — лист эмоций: "{PROMPT_BUILDER}, character expression sheet, 6 head close-ups in a grid: happy laughing, confident smirk, surprised, disappointed facepalm, angry, thinking, plain light grey background, {STYLE}"
4–6. То же для Вадима (лист эмоций: proud, sly grin, shocked, panicked, guilty, relieved).
Окружение: "suburban building plot in southern Russia, flat field, distant green hills, bright summer day, few neighbouring houses, {STYLE}" + готовый дом: "modern one-storey house of white aerated concrete blocks with dark grey metal roof, large windows, neat lawn, {STYLE}"

## Сценарий «Сэкономил на строительстве» (30 с, 6 кадров по ~5 с)
| # | Время | Кадр | Реплика |
|---|---|---|---|
| 1 | 0–5 | Участок. Вадим гордо держит телефон, Михалыч рядом с рулеткой. | ВАДИМ: «Нашёл бригаду в два раза дешевле!» |
| 2 | 5–10 | Вадим довольный перед тонкой кривой плитой фундамента без арматуры, вдали уезжает старый фургон. | МИХАЛЫЧ (за кадром): «А арматуру они где оставили?» |
| 3 | 10–15 | Полгода спустя: по стене дома ползёт трещина, дверь перекошена. Вадим в шоке хватается за голову. | ВАДИМ: «Это что... трещина?!» |
| 4 | 15–20 | Вадим виновато звонит по телефону; сплит — Михалыч отвечает, улыбается. | ВАДИМ: «Алло... Вы переделываете?» |
| 5 | 20–25 | Михалыч у разбитого угла фундамента, поднимает палец. | МИХАЛЫЧ: «Экономия на фундаменте — самая дорогая экономия.» |
| 6 | 25–30 | Готовый красивый дом, оба жмут руки, Вадим счастлив. Финальная надпись: «КОМПЛЕКС СТРОЙ — строим дома от фундамента до газона». | МИХАЛЫЧ: «Посчитаем честно — пишите в директ!» |

## Голоса (Яндекс SpeechKit)
- Михалыч — низкий, спокойный: голос «Ермил» или «Филипп», скорость 0.95
- Вадим — выше, суетливый: голос «Антон» или «Кирилл», скорость 1.1
Липсинк — Kling Lip Sync по готовым видео кадров 1, 3, 4, 5, 6.
