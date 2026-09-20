#!/usr/bin/env python3
"""Crystal v4.0.0 proof mock — the process fix.

Renders the system view at the Nova's real 1280x960 and, critically,
SIMULATES THE ENGINE'S SCISSOR CLIP: carousel children are composited
onto a separate layer which is then masked to the carousel rect
(0, 672, 1280, 960) before compositing — exactly what
CarouselComponent::render's pushClipRect does on device. The v3 mocks
skipped this and shipped a clipped selected card.

Also reproduces: itemSize/itemScale/selectedItemOffset math, rounded
corners, unfocused saturation 0.55 / dimming 0.18 / opacity 0.90,
no reflections, stage z40 under cards z45, panel text at v4 sizes.

Usage: proof_v40.py <system> [<system> ...]  -> /tmp/proof_v40_<sys>.png
       proof_v40.py ALL -> all 21 systems + contact sheet
"""
import os
import sys
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageChops

CRYSTAL = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal'
W, H = 1280, 960
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
ACCENT = (0xFF, 0xD6, 0x0A)

# per-system content (mirrors work/build_v40.py)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from build_v40 import SYSTEMS, TWO_LINE, fit_size, TITLE_BOX, BASE_SIZE, LAYOUTS  # noqa: E402

ORDER = ['snes', 'genesis', 'ps2', 'dreamcast', 'megadrive', 'psx', 'n64']


def rounded(card, radius):
    mask = Image.new('L', card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.size[0], card.size[1]],
                                           radius, fill=255)
    card.putalpha(ImageChops.darker(card.getchannel('A'), mask))
    return card


def load_card(sys):
    p = os.path.join(CRYSTAL, 'cards', f'{sys}.png')
    if not os.path.exists(p):
        p = os.path.join(CRYSTAL, 'cards', '_default.png')
    return Image.open(p).convert('RGBA')


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    return lines


def draw_text_block(d, sys):
    """Panel text at the v4 positions/sizes. Returns nothing; draws on d."""
    x = int(0.030 * W)
    layout = LAYOUTS.get(sys)
    desc_y, count_y, facts_y = layout or (0.305, 0.460, 0.535)
    if sys in TWO_LINE:
        l1, l2, desc, facts = TWO_LINE[sys]
        mfr = 'NINTENDO'
        f1 = ImageFont.truetype(FB, int(fit_size(l1, TITLE_BOX) * H))
        f2 = ImageFont.truetype(FB, int(fit_size(l2, TITLE_BOX) * H))
        d.text((x, int(0.226 * H)), l1, font=f1, fill='white', anchor='lt')
        d.text((x, int(0.266 * H)), l2, font=f2, fill='white', anchor='lt')
    else:
        mfr, desc, facts, full = SYSTEMS[sys]
        s = fit_size(full, TITLE_BOX)
        f = ImageFont.truetype(FB, int(s * H))
        d.text((x, int(0.230 * H)), full, font=f, fill='white', anchor='lt')

    # badge pill
    fb = ImageFont.truetype(FB, int(0.018 * H))
    bx, by = x, int(0.195 * H)
    tw = d.textlength(mfr, font=fb)
    mx, my = int(0.010 * W), int(0.005 * H)
    d.rounded_rectangle([bx - mx, by - my, bx + tw + mx,
                         by + fb.size + my * 2], radius=int(0.007 * H),
                        fill='white')
    d.text((bx, by), mfr, font=fb, fill=(10, 47, 160), anchor='lt')

    # description (white, wrapped)
    fr = ImageFont.truetype(FR, int(0.019 * H))
    y = int(desc_y * H)
    lh = int(0.019 * H * 1.35)
    for line in wrap(d, desc, fr, int(0.20 * W)):
        d.text((x, y), line, font=fr, fill='white', anchor='lt')
        y += lh

    # count
    fc = ImageFont.truetype(FB, int(0.055 * H))
    d.text((x, int(count_y * H)), '42 GAMES', font=fc, fill='white', anchor='lt')

    # facts
    ff = ImageFont.truetype(FB, int(0.017 * H))
    d.text((x, int(facts_y * H)), facts.upper(), font=ff, fill=ACCENT, anchor='lt')


def render(sys, out):
    bg = Image.open(os.path.join(CRYSTAL, 'backgrounds', f'{sys}.webp'))
    bg = bg.convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

    # panel text
    draw_text_block(ImageDraw.Draw(bg, 'RGBA'), sys)

    # stage (z40)
    vig = Image.open(os.path.join(CRYSTAL, 'art', 'carousel_vignette.png'))
    vig = vig.convert('RGBA').resize((W, int(0.340 * H)), Image.LANCZOS)
    bg.alpha_composite(vig, (0, H - vig.size[1]))

    # carousel children on their own layer (z45) — clipped by the engine
    cy0, ch = int(0.700 * H), int(0.300 * H)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    iw, ih = int(0.130 * W), int(0.215 * H)   # 166 x 206
    slot = W / 7
    # the engine centers the selected item: rotate the ring so sys is at index 3
    ring = ORDER
    order = [ring[(ring.index(sys) + k - 3) % len(ring)] for k in range(7)] \
        if sys in ring else ring
    sel = order.index(sys) if sys in order else 3
    for i, s in enumerate(order):
        card = load_card(s).resize((iw, ih), Image.LANCZOS)
        card = rounded(card, int(0.008 * W))
        if i == sel:
            card = load_card(s).resize((int(iw * 1.25), int(ih * 1.25)),
                                       Image.LANCZOS)
            card = rounded(card, int(0.008 * W))
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
        # ascendingRaised: selected paints last (on top)
    # engine scissor: clip the whole carousel layer to the carousel rect
    clip = Image.new('L', (W, H), 0)
    ImageDraw.Draw(clip).rectangle([0, cy0, W, cy0 + ch], fill=255)
    layer.putalpha(ImageChops.darker(layer.getchannel('A'), clip))
    bg.alpha_composite(layer)

    bg.convert('RGB').save(out, quality=90)
    print('wrote', out)


def main():
    args = sys.argv[1:] or ['genesis']
    if args == ['ALL']:
        from build_v40 import SYSTEMS as S
        args = list(S.keys()) + ['nes', 'snes']
    outs = []
    for s in args:
        out = f'/tmp/proof_v40_{s}.png'
        render(s, out)
        outs.append(out)
    if len(outs) > 1:
        # contact sheet, 3 columns
        cols = 3
        cw, chh = W // 3, H // 3
        rows = (len(outs) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * cw, rows * chh), 'black')
        for i, o in enumerate(outs):
            im = Image.open(o).resize((cw, chh), Image.LANCZOS)
            sheet.paste(im, ((i % cols) * cw, (i // cols) * chh))
        sheet.save('/tmp/proof_v40_contact.png', quality=88)
        print('wrote /tmp/proof_v40_contact.png')


if __name__ == '__main__':
    main()
