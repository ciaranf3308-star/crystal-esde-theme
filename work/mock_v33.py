#!/usr/bin/env python3
"""Crystal v3.3 proof mock: composite the real 4:3 background + real text
positions + real carousel strip at the Nova's 1280x960, then LOOK at it."""
import os
import re
import sys
from PIL import Image, ImageDraw, ImageFont

CRYSTAL = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal'
W, H = 1280, 960
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

vars_txt = open(os.path.join(CRYSTAL, 'variables.xml')).read()
V = dict(re.findall(r'<(\w+)>([0-9a-fA-F]{6,8})</\1>', vars_txt))
print('vars:', V)


def rgba(h):
    if len(h) == 6:
        h += 'FF'
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))  # RRGGBBAA


def txt(draw, xy, s, px, color, anchor='la'):
    f = ImageFont.truetype(FB, px)
    draw.text(xy, s, font=f, fill=color, anchor=anchor)


def wrap(draw, s, px, max_w):
    f = ImageFont.truetype(FR, px)
    words, lines, cur = s.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if draw.textlength(t, font=f) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    lines.append(cur)
    return lines, f


NAMES = {
    'gbc': 'Nintendo Game Boy Color', 'gc': 'Nintendo GameCube',
    'dreamcast': 'Sega Dreamcast', 'psp': 'Sony PlayStation Portable',
    'snes': None,  # two-line static
}
NSIZE = {'gbc': 0.018, 'gc': 0.023, 'dreamcast': 0.028, 'psp': 0.018, 'snes': 0.028}
DESC = {
    'gbc': 'Color came to the brick. A pocket rainbow of classics.',
    'gc': "Nintendo's cube of joy. Smash, Sunshine and Wind Waker.",
    'dreamcast': "Sega's 128-bit swan song. Arcade soul with VMU dreams.",
    'psp': 'Console power in your pocket. UMD adventures.',
    'snes': 'The 16-bit golden age. Mode 7 magic and timeless RPGs.',
}
FACTS = {
    'gbc': '8-BIT \u2022 HANDHELD \u2022 1998', 'gc': '128-BIT \u2022 2001',
    'dreamcast': '128-BIT \u2022 1999', 'psp': 'HANDHELD \u2022 2005',
    'snes': '16-BIT \u2022 1991',
}
MFR = {'gbc': 'NINTENDO', 'gc': 'NINTENDO', 'dreamcast': 'SEGA',
       'psp': 'SONY', 'snes': 'NINTENDO'}


def render(sys, out):
    bg = Image.open(os.path.join(CRYSTAL, 'backgrounds', f'{sys}.webp')).convert('RGB')
    bg = bg.resize((W, H), Image.LANCZOS).convert('RGBA')
    d = ImageDraw.Draw(bg, 'RGBA')
    X = int(0.028 * W)

    txt(d, (X, int(0.195 * H)), MFR[sys], int(0.016 * H), rgba(V['crystalDim']))
    if sys == 'snes':
        txt(d, (X, int(0.228 * H)), 'SUPER NINTENDO', int(NSIZE['snes'] * H), rgba(V['crystalText']))
        txt(d, (X, int(0.264 * H)), 'ENTERTAINMENT SYSTEM', int(0.019 * H), rgba(V['crystalText']))
    else:
        txt(d, (X, int(0.232 * H)), NAMES[sys], int(NSIZE[sys] * H), rgba(V['crystalText']))
    lines, f = wrap(d, DESC[sys], int(0.0155 * H), 0.155 * W)
    yy = int(0.300 * H)
    for ln in lines[:6]:
        d.text((X, yy), ln, font=f, fill=rgba(V['crystalDim']), anchor='la')
        yy += int(0.0155 * H * 1.35)
    txt(d, (X, int(0.475 * H)), '6 GAMES', int(0.042 * H), rgba(V['crystalText']))
    txt(d, (X, int(0.545 * H)), FACTS[sys], int(0.015 * H), rgba(V['crystalAccent']))

    # vignette floor
    vig = Image.open(os.path.join(CRYSTAL, 'art', 'carousel_vignette.png')).convert('RGBA')
    vig = vig.resize((W, int(0.375 * H)), Image.LANCZOS)
    bg.alpha_composite(vig, (0, H - vig.size[1]))

    # carousel: 7 cards, selected pops 1.28x and lifts 19px
    order = ['gba', 'gbc', 'gc', 'n64', 'n3ds', 'snes', 'nes']
    sel = order.index(sys) if sys in order else 3
    cy = int((0.648 + 0.335 / 2) * H)
    slot = W / 7
    for i, s in enumerate(order):
        card = Image.open(os.path.join(CRYSTAL, 'cards', f'{s}.png')).convert('RGBA')
        iw, ih = int(0.092 * W), int(0.160 * H)
        card = card.resize((iw, ih), Image.LANCZOS)
        if i == sel:
            card = card.resize((int(iw * 1.28), int(ih * 1.28)), Image.LANCZOS)
            y = cy - int(0.018 * H) - card.size[1] // 2
        else:
            y = cy - card.size[1] // 2
            # desaturate neighbours (approx)
            g = card.convert('L').convert('RGBA')
            card = Image.blend(card, g, 0.45)
        x = int((i + 0.5) * slot - card.size[0] / 2)
        bg.alpha_composite(card, (x, y))
        # reflection hint
        rh = card.crop((0, 0, card.size[0], int(card.size[1] * 0.35))).transpose(Image.FLIP_TOP_BOTTOM)
        bg.alpha_composite(rh, (x, y + card.size[1]))

    bg.save(out)
    print('wrote', out)


if __name__ == '__main__':
    for s in sys.argv[1:] or ['gbc']:
        render(s, f'/tmp/crystal_v33_{s}.png')
