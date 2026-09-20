#!/usr/bin/env python3
"""Crystal v4.3.0 proof mock — "Spotlight" system carousel.

Mirrors the new views.xml geometry:
  - sys_vignette.png at y 0.600 (z39), carousel_glow.png centered (z40)
  - carousel zone y 0.640-1.0, items 122x162, selected 2x = 243x324,
    lift -8px, gentle unfocused treatment (sat 0.85 / dim 0.22 / op 0.92),
    scissor-clipped to the carousel rect.

Usage: proof_v43.py <system> [<system> ...] -> /tmp/proof_v43_<sys>.png
"""
import os
import sys
from PIL import Image, ImageDraw, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proof_v40 as p40  # noqa: E402

W, H = p40.W, p40.H
CRYSTAL = p40.CRYSTAL


def load_card(sys):
    return Image.open(os.path.join(CRYSTAL, 'cards', f'{sys}.png')).convert('RGBA')


def render(sys, out):
    bg = Image.open(os.path.join(CRYSTAL, 'backgrounds', f'{sys}.webp'))
    bg = bg.convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')
    p40.draw_text_block(ImageDraw.Draw(bg, 'RGBA'), sys)

    # z39 vignette
    vig = Image.open(os.path.join(CRYSTAL, 'art', 'sys_vignette.png')).convert('RGBA')
    bg.alpha_composite(vig, (0, int(0.600 * H)))

    # z40 glow (pos 0.5 0.812, size 0.438, origin center)
    glow = Image.open(os.path.join(CRYSTAL, 'art', 'carousel_glow.png')).convert('RGBA')
    gw, gh = int(0.484 * W), int(0.479 * H)
    glow = glow.resize((gw, gh), Image.LANCZOS)
    bg.alpha_composite(glow, (int(W / 2 - gw / 2), int(0.812 * H - gh / 2)))

    # z45 carousel, clipped to its rect
    cy0, ch = int(0.640 * H), int(0.360 * H)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    iw, ih = int(0.095 * W), int(0.169 * H)          # 122 x 162
    siw, sih = iw * 2, ih * 2                        # 244 x 324 (2x)
    slot = W / 7
    ring = p40.ORDER
    order = [ring[(ring.index(sys) + k - 3) % len(ring)] for k in range(7)] \
        if sys in ring else ring
    sel = order.index(sys) if sys in order else 3

    def place(i, card, lift):
        cx = int((i + 0.5) * slot - card.size[0] / 2)
        cyy = cy0 + (ch - card.size[1]) // 2 + lift
        layer.alpha_composite(card, (cx, cyy))

    # unfocused first (selected is raised above via ascendingRaised)
    for i, s in enumerate(order):
        if i == sel:
            continue
        card = load_card(s).resize((iw, ih), Image.LANCZOS)
        card = p40.rounded(card, int(0.008 * W))
        g = card.convert('L').convert('RGBA')
        card = Image.blend(card, g, 0.15)            # saturation 0.85
        rgb = card.convert('RGB').point(lambda v: int(v * 0.78))  # dim 0.22
        card = Image.merge('RGBA', (*rgb.split(), card.getchannel('A')))
        a = card.getchannel('A').point(lambda v: int(v * 0.92))
        card.putalpha(a)
        place(i, card, 0)

    sel_card = load_card(sys).resize((siw, sih), Image.LANCZOS)
    sel_card = p40.rounded(sel_card, int(0.008 * W))
    place(sel, sel_card, int(-0.008 * H))

    clip = Image.new('L', (W, H), 0)
    ImageDraw.Draw(clip).rectangle([0, cy0, W, cy0 + ch], fill=255)
    layer.putalpha(ImageChops.darker(layer.getchannel('A'), clip))
    bg.alpha_composite(layer)

    bg.convert('RGB').save(out, quality=90)
    print('wrote', out)


if __name__ == '__main__':
    args = sys.argv[1:] or ['gba']
    for s in args:
        render(s, f'/tmp/proof_v43_{s}.png')
