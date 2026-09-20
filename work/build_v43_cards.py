#!/usr/bin/env python3
"""Crystal v4.3.0 — "Spotlight" carousel cards (v5).

One texture per system (stock ES-DE 3.4.1 has no per-state carousel images),
so the OFF look is baked into the card itself:

  black rounded box + the system's art as a faint dark texture inside
  + the console name in big white hero-style text (DejaVu Sans Bold, like the
  panel sysName) + a small yellow tick.

The user's poster/trading-card art is NOT removed — it lives on as a dark
whisper (~20%) inside the box. The box + name dominate.

  in : work/cards_v41_backup/<sys>.png   (v4.1.0 cards, incl. user posters)
  out: theme-src/crystal/cards/<sys>.png  (240x320)
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'cards_v41_backup')
DST = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal/cards'

NAMES = {
    'dreamcast': 'Sega Dreamcast',
    'gb': 'Nintendo Game Boy',
    'gba': 'Nintendo Game Boy Advance',
    'gbc': 'Nintendo Game Boy Color',
    'gc': 'Nintendo GameCube',
    'genesis': 'Sega Genesis',
    'megadrive': 'Sega Mega Drive',
    'n3ds': 'Nintendo 3DS',
    'n64': 'Nintendo 64',
    'nds': 'Nintendo DS',
    'nes': 'Nintendo Entertainment System',
    'ps2': 'Sony PlayStation 2',
    'psp': 'Sony PlayStation Portable',
    'psx': 'Sony PlayStation',
    'snes': 'Super Nintendo',
    'steam': 'Steam',
    'wii': 'Nintendo Wii',
    'wiiu': 'Nintendo Wii U',
    'windows': 'Windows',
    'xbox': 'Xbox',
    'xbox360': 'Xbox 360',
    '_default': 'Crystal',
}

W, H = 240, 320
YELLOW = (255, 217, 74)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def balanced_wrap(draw, text, font, max_w):
    words = text.split()
    if len(words) == 1:
        return [text]
    best, best_cost = None, None
    for i in range(1, len(words)):
        l1, l2 = ' '.join(words[:i]), ' '.join(words[i:])
        w1 = draw.textlength(l1, font=font)
        w2 = draw.textlength(l2, font=font)
        if w1 <= max_w and w2 <= max_w:
            cost = abs(w1 - w2)
            if best_cost is None or cost < best_cost:
                best, best_cost = (l1, l2), cost
    return list(best) if best else [text]


def fit_font(draw, text, max_w, start=40):
    size = start
    while size > 14:
        font = ImageFont.truetype(FONT, size)
        lines = balanced_wrap(draw, text, font, max_w)
        if len(lines) <= 2 and all(draw.textlength(l, font=font) <= max_w
                                  for l in lines):
            return font, lines
        size -= 1
    font = ImageFont.truetype(FONT, 14)
    return font, balanced_wrap(draw, text, font, max_w)


# hand-tuned line breaks where the balanced splitter reads awkwardly
BREAKS = {
    'gba': ['Nintendo', 'Game Boy Advance'],
    'gbc': ['Nintendo', 'Game Boy Color'],
    'psp': ['Sony', 'PlayStation Portable'],
    'nes': ['Nintendo', 'Entertainment System'],
}


def build(sys, name):
    # black box with a soft top sheen
    card = Image.new('RGBA', (W, H), (10, 12, 22, 255))
    sheen = Image.new('L', (1, H))
    for y in range(H):
        t = y / H
        sheen.putpixel((0, y), int(34 * (1 - t) ** 2))
    sheen = sheen.resize((W, H))
    white = Image.new('RGBA', (W, H), (255, 255, 255, 255))
    card = Image.composite(white, card, sheen)

    # the system's art as a faint dark texture inside the box
    art_path = os.path.join(SRC, f'{sys}.png')
    if os.path.exists(art_path):
        art = Image.open(art_path).convert('RGBA')
        # cover-crop to the card
        s = max(W / art.width, H / art.height)
        art = art.resize((int(art.width * s) + 1, int(art.height * s) + 1),
                         Image.LANCZOS)
        x = (art.width - W) // 2
        y = (art.height - H) // 2
        art = art.crop((x, y, x + W, y + H))
        art = art.filter(ImageFilter.GaussianBlur(1.2))
        dark = art.convert('RGB').point(lambda v: int(v * 0.35))
        art = Image.merge('RGBA', (*dark.split(), art.getchannel('A')))
        a = art.getchannel('A').point(lambda v: int(v * 0.20))
        art.putalpha(a)
        card.alpha_composite(art)

    d = ImageDraw.Draw(card, 'RGBA')

    # hairline border
    d.rounded_rectangle([1, 1, W - 2, H - 2], radius=16,
                        outline=(255, 255, 255, 36), width=2)

    # console name, hero-style: big white DejaVu Bold, centered
    if sys in BREAKS:
        font = ImageFont.truetype(FONT, 40)
        lines = BREAKS[sys]
        while any(d.textlength(l, font=font) > W - 44 for l in lines):
            font = ImageFont.truetype(FONT, font.size - 1)
    else:
        font, lines = fit_font(d, name, W - 44)
    asc, desc = font.getmetrics()
    lh = asc + desc
    total = lh * len(lines)
    y0 = (H - total) // 2 - 8
    for i, line in enumerate(lines):
        lw = d.textlength(line, font=font)
        d.text(((W - lw) / 2, y0 + i * lh), line, font=font,
               fill=(255, 255, 255, 255))

    # yellow tick under the name
    ty = y0 + total + 14
    tw, th = 30, 5
    d.rounded_rectangle([(W - tw) / 2, ty, (W + tw) / 2, ty + th],
                        radius=th // 2, fill=YELLOW + (255,))

    return card


def main():
    os.makedirs(DST, exist_ok=True)
    for sys, name in sorted(NAMES.items()):
        card = build(sys, name)
        card.save(os.path.join(DST, f'{sys}.png'))
        print('wrote', sys)


if __name__ == '__main__':
    main()
