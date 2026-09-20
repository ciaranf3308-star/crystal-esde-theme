#!/usr/bin/env python3
"""Crystal v3.5 carousel proof mock — FAITHFUL z-order simulation.

v3.3's mock composited background -> vignette -> cards and never painted the
carousel element's own background rect, so it could not catch the white-box
bug the Nova photo exposed. This mock simulates the true order:

  z1  sysBackground
  z40 carouselStage vignette
  z45 carousel background rect filled with the theme's <color>
  z45 cards (itemScale pop, selectedItemOffset lift, saturation, reflections)
  z50 panel text

Run with a carousel color hex (RRGGBBAA) to reproduce the bug (FFFFFFFF)
or verify the fix (00000000).
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

CRYSTAL = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal'
W, H = 1280, 960
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def rgba(h):
    if len(h) == 6:
        h += 'FF'
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))


def rounded(card, radius):
    mask = Image.new('L', card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.size[0], card.size[1]], radius, fill=255)
    card.putalpha(mask)
    return card


def render(carousel_color, out):
    bg = Image.open(os.path.join(CRYSTAL, 'backgrounds', 'genesis.webp')).convert('RGB')
    bg = bg.resize((W, H), Image.LANCZOS).convert('RGBA')

    # z40: vignette stage — pos (0,1), size (1,0.375), origin (0,1)
    vig = Image.open(os.path.join(CRYSTAL, 'art', 'carousel_vignette.png')).convert('RGBA')
    vig = vig.resize((W, int(0.375 * H)), Image.LANCZOS)
    bg.alpha_composite(vig, (0, H - vig.size[1]))

    # z45: the carousel's OWN background rect — pos (0,0.648), size (1,0.335)
    cx0, cy0 = 0, int(0.648 * H)
    cw, ch = W, int(0.335 * H)
    car_bg = Image.new('RGBA', (cw, ch), rgba(carousel_color))
    bg.alpha_composite(car_bg, (cx0, cy0))

    # z45: cards — 7 items, itemSize 0.092 x 0.160
    order = ['wii', 'wiiu', 'dreamcast', 'genesis', 'megadrive', 'psx', 'ps2']
    sel = order.index('genesis')
    iw, ih = int(0.092 * W), int(0.160 * H)
    slot = W / 7
    for i, s in enumerate(order):
        card = Image.open(os.path.join(CRYSTAL, 'cards', f'{s}.png')).convert('RGBA')
        card = card.resize((iw, ih), Image.LANCZOS)
        card = rounded(card, int(0.008 * W))
        lift = 0
        if i == sel:
            card = card.resize((int(iw * 1.28), int(ih * 1.28)), Image.LANCZOS)
            card = rounded(card, int(0.008 * W))
            lift = int(-0.018 * H)
        else:
            g = card.convert('L').convert('RGBA')
            card = Image.blend(card, g, 0.45)  # unfocusedItemSaturation 0.55
            a = card.getchannel('A').point(lambda v: int(v * 0.90))
            card.putalpha(a)
        x = int((i + 0.5) * slot - card.size[0] / 2)
        y = cy0 + (ch - card.size[1]) // 2 + lift
        bg.alpha_composite(card, (x, y))
        # reflection: flipped bottom 35%, faded
        rh = card.crop((0, 0, card.size[0], int(card.size[1] * 0.35))).transpose(Image.FLIP_TOP_BOTTOM)
        fade = Image.new('L', rh.size, 0)
        fd = ImageDraw.Draw(fade)
        for yy in range(rh.size[1]):
            fd.line([(0, yy), (rh.size[0], yy)], fill=int(0.35 * 255 * (1 - yy / rh.size[1]) ** 2.5))
        rha = rh.getchannel('A')
        from PIL import ImageChops
        rh.putalpha(ImageChops.darker(rha, fade))
        bg.alpha_composite(rh, (x, y + card.size[1]))

    # z50: panel text
    d = ImageDraw.Draw(bg, 'RGBA')
    X = int(0.028 * W)
    V = {'crystalDim': '8FA3C8', 'crystalText': 'FFFFFF', 'crystalAccent': 'FFD23F'}
    fB = lambda px: ImageFont.truetype(FB, px)
    fR = lambda px: ImageFont.truetype(FR, px)
    d.text((X, int(0.195 * H)), 'SEGA', font=fB(int(0.016 * H)), fill=rgba(V['crystalDim']), anchor='la')
    d.text((X, int(0.232 * H)), 'Sega Genesis', font=fB(int(0.030 * H)), fill=rgba(V['crystalText']), anchor='la')
    yy = int(0.300 * H)
    for ln in ["Blast-processing attitude. Sonic's", '16-bit battleground.']:
        d.text((X, yy), ln, font=fR(int(0.0155 * H)), fill=rgba(V['crystalDim']), anchor='la')
        yy += int(0.0155 * H * 1.35)
    d.text((X, int(0.475 * H)), '2 GAMES', font=fB(int(0.042 * H)), fill=rgba(V['crystalText']), anchor='la')
    d.text((X, int(0.545 * H)), '16-BIT \u2022 1989', font=fB(int(0.015 * H)), fill=rgba(V['crystalAccent']), anchor='la')

    bg.convert('RGB').save(out)
    print('wrote', out)


if __name__ == '__main__':
    color = sys.argv[1] if len(sys.argv) > 1 else '00000000'
    out = sys.argv[2] if len(sys.argv) > 2 else '/tmp/crystal_v35_genesis.png'
    render(color, out)
