#!/usr/bin/env python3
"""Crystal v4.1.0 proof mock — system view WITHOUT the carousel stage.

Mirrors work/proof_v40.py exactly (scissor clip, item math, dimming) but
omits the z40 carousel_vignette composite, because v4.1.0 removed the blue
bar under the carousel at the user's request. Also picks up the restored
user-poster cards for the 7 poster systems.

Usage: proof_v41.py <system> [<system> ...] -> /tmp/proof_v41_<sys>.png
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proof_v40 as p40  # noqa: E402

W, H = p40.W, p40.H
CRYSTAL = p40.CRYSTAL


def render(sys, out):
    bg = Image.open(os.path.join(CRYSTAL, 'backgrounds', f'{sys}.webp'))
    bg = bg.convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

    # panel text (same as v4.0.0)
    p40.draw_text_block(ImageDraw.Draw(bg, 'RGBA'), sys)

    # v4.1.0: NO stage. The carousel floats directly over the background.

    # carousel children on their own layer (z45) — clipped by the engine
    cy0, ch = int(0.700 * H), int(0.300 * H)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    iw, ih = int(0.130 * W), int(0.215 * H)   # 166 x 206
    slot = W / 7
    ring = p40.ORDER
    order = [ring[(ring.index(sys) + k - 3) % len(ring)] for k in range(7)] \
        if sys in ring else ring
    sel = order.index(sys) if sys in order else 3
    for i, s in enumerate(order):
        card = p40.load_card(s).resize((iw, ih), Image.LANCZOS)
        card = p40.rounded(card, int(0.008 * W))
        if i == sel:
            card = p40.load_card(s).resize((int(iw * 1.25), int(ih * 1.25)),
                                           Image.LANCZOS)
            card = p40.rounded(card, int(0.008 * W))
            lift = int(-0.010 * H)
        else:
            g = card.convert('L').convert('RGBA')
            card = Image.blend(card, g, 0.45)          # saturation 0.55
            rgb = card.convert('RGB').point(lambda v: int(v * 0.82))  # dim 0.18
            card = Image.merge('RGBA', (*rgb.split(), card.getchannel('A')))
            a = card.getchannel('A').point(lambda v: int(v * 0.90))
            card.putalpha(a)
            lift = 0
        cx = int((i + 0.5) * slot - card.size[0] / 2)
        cyy = cy0 + (ch - card.size[1]) // 2 + lift
        layer.alpha_composite(card, (cx, cyy))
    clip = Image.new('L', (W, H), 0)
    ImageDraw.Draw(clip).rectangle([0, cy0, W, cy0 + ch], fill=255)
    layer.putalpha(ImageChops.darker(layer.getchannel('A'), clip))
    bg.alpha_composite(layer)

    bg.convert('RGB').save(out, quality=90)
    print('wrote', out)


if __name__ == '__main__':
    args = sys.argv[1:] or ['genesis']
    for s in args:
        render(s, f'/tmp/proof_v41_{s}.png')
