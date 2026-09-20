#!/usr/bin/env python3
"""Crystal v3.6.0 showpiece proof mock — faithful z-order simulation.

  z1  sysBackground (supplied 4:3 hero, fullscreen)
  z40 carouselStage (glossy stage w/ baked center spotlight + edge falloff)
  z45 carousel background rect (transparent) + cards:
      itemSize 0.092x0.160, itemScale 1.33, lift -0.018,
      unfocused: saturation 0.55, opacity 0.90, dimming 0.18
      + per-card mirror reflections
  z50 panel text (badge pill, name, desc, count, facts)
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageChops

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
    card.putalpha(ImageChops.darker(card.getchannel('A'), mask))
    return card


def tracked(d, xy, text, font, fill, tracking=2):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += int(font.getlength(ch)) + tracking


def render(out):
    bg = Image.open(os.path.join(CRYSTAL, 'backgrounds', 'genesis.webp')).convert('RGB')
    bg = bg.resize((W, H), Image.LANCZOS).convert('RGBA')

    # z40 stage
    vig = Image.open(os.path.join(CRYSTAL, 'art', 'carousel_vignette.png')).convert('RGBA')
    vig = vig.resize((W, int(0.375 * H)), Image.LANCZOS)
    bg.alpha_composite(vig, (0, H - vig.size[1]))

    # z45 cards
    cy0, ch = int(0.648 * H), int(0.335 * H)
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
            card = card.resize((int(iw * 1.33), int(ih * 1.33)), Image.LANCZOS)
            card = rounded(card, int(0.008 * W))
            lift = int(-0.018 * H)
        else:
            g = card.convert('L').convert('RGBA')
            card = Image.blend(card, g, 0.45)                      # saturation 0.55
            rgb = card.convert('RGB').point(lambda v: int(v * 0.82))  # dimming 0.18
            card = Image.merge('RGBA', (*rgb.split(), card.getchannel('A')))
            a = card.getchannel('A').point(lambda v: int(v * 0.90))   # opacity 0.90
            card.putalpha(a)
        x = int((i + 0.5) * slot - card.size[0] / 2)
        y = cy0 + (ch - card.size[1]) // 2 + lift
        bg.alpha_composite(card, (x, y))
        rh = card.crop((0, 0, card.size[0], int(card.size[1] * 0.35))).transpose(Image.FLIP_TOP_BOTTOM)
        fade = Image.new('L', rh.size, 0)
        fd = ImageDraw.Draw(fade)
        for yy in range(rh.size[1]):
            fd.line([(0, yy), (rh.size[0], yy)], fill=int(0.35 * 255 * (1 - yy / rh.size[1]) ** 2.5))
        rh.putalpha(ImageChops.darker(rh.getchannel('A'), fade))
        bg.alpha_composite(rh, (x, y + card.size[1]))

    # z50 text
    d = ImageDraw.Draw(bg, 'RGBA')
    X = int(0.028 * W)
    fB = lambda px: ImageFont.truetype(FB, px)
    fR = lambda px: ImageFont.truetype(FR, px)
    # badge pill: white bg, blue text, margins 0.010/0.005, radius 0.007
    bf = fB(int(0.016 * H))
    label = 'SEGA'
    twd = bf.getlength(label)
    px_, py_ = X, int(0.200 * H)
    mx, my = int(0.010 * W), int(0.005 * H)
    d.rounded_rectangle([px_ - mx, py_ - my, px_ + twd + mx, py_ + int(0.016 * H) + my],
                        int(0.007 * W), fill=(255, 255, 255, 255))
    d.text((px_, py_), label, font=bf, fill=rgba('0A2FA0'))
    d.text((X, int(0.232 * H)), 'Sega Genesis', font=fB(int(0.030 * H)), fill=rgba('FFFFFF'))
    yy = int(0.300 * H)
    for ln in ["Blast-processing attitude. Sonic's", '16-bit battleground.']:
        d.text((X, yy), ln, font=fR(int(0.0155 * H)), fill=rgba('BFD4FF'))
        yy += int(0.0155 * H * 1.35)
    d.text((X, int(0.475 * H)), '2 GAMES', font=fB(int(0.042 * H)), fill=rgba('FFFFFF'))
    d.text((X, int(0.545 * H)), '16-BIT \u2022 1989', font=fB(int(0.015 * H)), fill=rgba('FFD60A'))

    bg.convert('RGB').save(out)
    print('wrote', out)


if __name__ == '__main__':
    render('/tmp/crystal_v36_genesis.png')
