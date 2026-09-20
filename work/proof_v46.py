#!/usr/bin/env python3
"""Crystal v4.6.0 proof mock — the left-panel text alignment/TLC pass.

Renders the PROPOSED v4.6.0 panel text (not the shipped v4.4.0 XML) over the
real backgrounds at 1280x960, so the unified vertical grid and per-console
title sizes can be inspected before any source edit.

v4.6.0 text design:
  - One shared vertical grid for 15 consoles: badge 0.195 / title 0.230 /
    desc 0.281 / count 0.354 / facts 0.415  (left edge 0.030 everywhere)
  - Per-background forced threading kept: gbc, nds, dreamcast, gc
  - Two-line consoles: nes (tightened grid), snes (kept)
  - Title sizes: measured DejaVu Sans Bold fit, capped 0.040, floored 0.026.
    Three unreadably-long fullnames become static short titles (badge keeps
    the manufacturer): gba "Game Boy Advance", gbc "Game Boy Color", psp "PSP".
  - gb countNum unified to 0.055 (drops the v4.0 0.042 exception); all box
    widths unified (title 0.24, desc/count/facts 0.20).

Usage: proof_v46.py <system> [<system> ...]  -> /tmp/proof_v46_<sys>.png
       proof_v46.py ALL -> all 21 systems + contact sheet
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

CRYSTAL = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal'
W, H = 1280, 960
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
ACCENT = (0xFF, 0xD6, 0x0A)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_v40 import SYSTEMS, TWO_LINE  # noqa: E402
from proof_v40 import wrap  # noqa: E402

# sys -> (static_title or None for systemdata fullname, fontSize)
V46_TITLE = {
    'dreamcast': ('Dreamcast', 0.040),
    'gb':        ('Game Boy', 0.040),
    'gba':       ('Game Boy Advance', 0.030),
    'gbc':       ('Game Boy Color', 0.036),
    'gc':        ('GameCube', 0.040),
    'genesis':   (None, 0.040),
    'megadrive': ('Mega Drive', 0.040),
    'n3ds':      (None, 0.040),
    'n64':       (None, 0.040),
    'nds':       (None, 0.040),
    'ps2':       ('PlayStation 2', 0.040),
    'psp':       ('PSP', 0.040),
    'psx':       ('PlayStation', 0.040),
    'steam':     (None, 0.040),
    'wii':       (None, 0.040),
    'wiiu':      (None, 0.038),
    'windows':   (None, 0.040),
    'xbox':      ('Xbox', 0.040),
    'xbox360':   ('Xbox 360', 0.040),
}
# sys -> (desc_y, count_y, facts_y); default is the unified grid
V46_LAYOUT = {
    'gbc':       (0.302, 0.358, 0.431),
    'nds':       (0.273, 0.344, 0.405),
    'dreamcast': (0.275, 0.350, 0.411),
    'gc':        (0.275, 0.350, 0.411),
    'nes':       (0.305, 0.375, 0.440),
    'snes':      (0.341, 0.397, 0.458),
}
GRID = (0.281, 0.354, 0.415)
ALL = ['dreamcast', 'gb', 'gba', 'gbc', 'gc', 'genesis', 'megadrive', 'n3ds',
       'n64', 'nds', 'nes', 'ps2', 'psp', 'psx', 'snes', 'steam', 'wii',
       'wiiu', 'windows', 'xbox', 'xbox360']


def draw_text_block(d, sys):
    """Proposed v4.6.0 panel text. Returns nothing; draws on d."""
    x = int(0.030 * W)
    desc_y, count_y, facts_y = V46_LAYOUT.get(sys, GRID)

    if sys in TWO_LINE:
        l1, l2, desc, facts = TWO_LINE[sys]
        mfr = 'NINTENDO'
        f1 = ImageFont.truetype(FB, int(0.040 * H if sys == 'nes' else 0.032 * H))
        f2 = ImageFont.truetype(FB, int(0.022 * H))
        d.text((x, int(0.226 * H)), l1, font=f1, fill='white', anchor='lt')
        d.text((x, int(0.266 * H)), l2, font=f2, fill='white', anchor='lt')
    else:
        mfr, desc, facts, full = SYSTEMS[sys]
        title, tsize = V46_TITLE[sys]
        f = ImageFont.truetype(FB, int(tsize * H))
        d.text((x, int(0.230 * H)), title or full, font=f, fill='white',
               anchor='lt')

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

    # count (unified 0.055)
    fc = ImageFont.truetype(FB, int(0.055 * H))
    d.text((x, int(count_y * H)), '42 GAMES', font=fc, fill='white',
           anchor='lt')

    # facts
    ff = ImageFont.truetype(FB, int(0.017 * H))
    d.text((x, int(facts_y * H)), facts.upper(), font=ff, fill=ACCENT,
           anchor='lt')


def render(sys, out):
    bg = Image.open(os.path.join(CRYSTAL, 'backgrounds', f'{sys}.webp'))
    bg = bg.convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')
    draw_text_block(ImageDraw.Draw(bg, 'RGBA'), sys)
    bg.convert('RGB').save(out)


if __name__ == '__main__':
    args = sys.argv[1:] or ['n64']
    targets = ALL if args == ['ALL'] else args
    outs = []
    for s in targets:
        out = f'/tmp/proof_v46_{s}.png'
        render(s, out)
        outs.append(out)
        print(out)
    if args == ['ALL']:
        thumbs = [Image.open(p).resize((320, 240), Image.LANCZOS) for p in outs]
        sheet = Image.new('RGB', (320 * 7, 240 * 3), 'black')
        for i, t in enumerate(thumbs):
            sheet.paste(t, ((i % 7) * 320, (i // 7) * 240))
        sheet.save('/tmp/proof_v46_sheet.png')
        print('/tmp/proof_v46_sheet.png')
