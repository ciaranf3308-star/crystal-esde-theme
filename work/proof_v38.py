#!/usr/bin/env python3
"""Crystal v3.8.0 proof mock: animated cards composited at 1280x960.

Same z-order/geometry as the v3.6 proof (bg z1, glossy stage z40,
cards z45 with itemSize 0.092x0.160, selected 1.33x + 19px lift,
unfocused saturation 0.55 / dimming 0.18 / opacity 0.90, reflections,
rounded corners). Cards are sampled at DIFFERENT animation phases, as
they appear on device (per-system phase jitter). Panel text unchanged
from v3.6 (already proofed) so it is omitted here.
"""
import os
from PIL import Image, ImageDraw, ImageChops

CRYSTAL = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal'
W, H = 1280, 960


def rounded(card, radius):
    mask = Image.new('L', card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.size[0], card.size[1]],
                                          radius, fill=255)
    card.putalpha(ImageChops.darker(card.getchannel('A'), mask))
    return card


def gif_frame(system, idx):
    im = Image.open(os.path.join(CRYSTAL, 'cards_anim', f'{system}.gif'))
    im.seek(idx % im.n_frames)
    return im.convert('RGBA')


def render(out):
    bg = Image.open(os.path.join(CRYSTAL, 'backgrounds', 'genesis.webp'))
    bg = bg.convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

    vig = Image.open(os.path.join(CRYSTAL, 'art', 'carousel_vignette.png'))
    vig = vig.convert('RGBA').resize((W, int(0.375 * H)), Image.LANCZOS)
    bg.alpha_composite(vig, (0, H - vig.size[1]))

    cy0, ch = int(0.648 * H), int(0.335 * H)
    # (system, animation frame) - phases scattered like on-device
    order = [('snes', 3), ('genesis', 0), ('ps2', 5), ('dreamcast', 2),
             ('megadrive', 7), ('psx', 4), ('n64', 0)]
    sel = 1
    iw, ih = int(0.092 * W), int(0.160 * H)
    slot = W / 7
    for i, (s, fi) in enumerate(order):
        card = gif_frame(s, fi).resize((iw, ih), Image.LANCZOS)
        card = rounded(card, int(0.008 * W))
        lift = 0
        if i == sel:
            card = card.resize((int(iw * 1.33), int(ih * 1.33)),
                               Image.LANCZOS)
            card = rounded(card, int(0.008 * W))
            lift = int(-0.018 * H)
        else:
            g = card.convert('L').convert('RGBA')
            card = Image.blend(card, g, 0.45)
            rgb = card.convert('RGB').point(lambda v: int(v * 0.82))
            card = Image.merge('RGBA', (*rgb.split(), card.getchannel('A')))
            a = card.getchannel('A').point(lambda v: int(v * 0.90))
            card.putalpha(a)
        x = int((i + 0.5) * slot - card.size[0] / 2)
        y = cy0 + (ch - card.size[1]) // 2 + lift
        bg.alpha_composite(card, (x, y))
        rh = card.crop((0, 0, card.size[0], int(card.size[1] * 0.35)))
        rh = rh.transpose(Image.FLIP_TOP_BOTTOM)
        fade = Image.new('L', rh.size, 0)
        fd = ImageDraw.Draw(fade)
        for yy in range(rh.size[1]):
            fd.line([(0, yy), (rh.size[0], yy)],
                    fill=int(0.35 * 255 * (1 - yy / rh.size[1]) ** 2.5))
        rh.putalpha(ImageChops.darker(rh.getchannel('A'), fade))
        bg.alpha_composite(rh, (x, y + card.size[1]))

    bg.convert('RGB').save(out, quality=90)
    print('wrote', out)


if __name__ == '__main__':
    render('/tmp/proof_v38_carousel.jpg')
