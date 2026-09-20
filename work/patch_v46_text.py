#!/usr/bin/env python3
"""Crystal v4.6.0 text TLC — per-console title readability pass.

v4.5.0 measured each fullname to fill the 0.24 box (94-100%), which left
tiny titles (gc 0.028, gb 0.029, ps2/xbox360 0.030) looking lost next to
0.040 titles. v4.6.0 uses short static titles (manufacturer stays on the
badge) so most consoles get a consistent, bold 0.040 title.

Changes from v4.5.0:
  dreamcast: "Sega Dreamcast" 0.035 -> "Dreamcast" 0.040
  gb:        "Nintendo Game Boy" 0.029 -> "Game Boy" 0.040
  gc:        "Nintendo GameCube" 0.028 -> "GameCube" 0.040
  megadrive: "Sega Mega Drive" 0.034 -> "Mega Drive" 0.040
  ps2:       "Sony PlayStation 2" 0.030 -> "PlayStation 2" 0.040
  psx:       "Sony PlayStation" 0.034 -> "PlayStation" 0.040
  xbox:      "Microsoft Xbox" 0.038 -> "Xbox" 0.040
  xbox360:   "Microsoft Xbox 360" 0.030 -> "Xbox 360" 0.040
  Kept: gba "Game Boy Advance" 0.030, gbc "Game Boy Color" 0.036,
        psp "PSP" 0.040 (already short titles)

Vertical grid and per-background threading unchanged from v4.5.0.
"""
import os
import re

REPO = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal'

# sys -> (static_title, fontSize). None title = use systemdata fullname.
V46_TITLE = {
    'dreamcast': ('Dreamcast', 0.040),
    'gb':        ('Game Boy', 0.040),
    'gba':       ('Game Boy Advance', 0.030),
    'gbc':       ('Game Boy Color', 0.036),
    'gc':        ('GameCube', 0.040),
    'genesis':   (None, 0.040),  # "Sega Genesis" already 0.040
    'megadrive': ('Mega Drive', 0.040),
    'n3ds':      (None, 0.040),
    'n64':       (None, 0.040),
    'nds':       (None, 0.040),
    'ps2':       ('PlayStation 2', 0.040),
    'psp':       ('PSP', 0.040),
    'psx':       ('PlayStation', 0.040),
    'steam':     (None, 0.040),
    'wii':       (None, 0.040),
    'wiiu':      (None, 0.040),  # was 0.038, now 0.040 (fits at 99%? check)
    'windows':   (None, 0.040),
    'xbox':      ('Xbox', 0.040),
    'xbox360':   ('Xbox 360', 0.040),
}


def get_text_block(s, name):
    m = re.search(
        r'(<text name="%s">\n)(.*?)(\n        </text>)' % re.escape(name),
        s, re.DOTALL)
    if not m:
        return None, None
    inner = m.group(2)
    if not inner.endswith('\n'):
        inner += '\n'
    return m.group(0), inner


def patch_system(sys):
    p = os.path.join(REPO, sys, 'theme.xml')
    s = open(p).read()
    orig = s

    title, tsize = V46_TITLE[sys]
    full, inner = get_text_block(s, 'sysName')
    if full is None:
        # No override block: only OK if we want base (no static, 0.040)
        assert title is None and abs(tsize - 0.040) < 1e-9, \
            f'{sys}: missing sysName block but needs one'
    else:
        # set fontSize
        inner = re.sub(r'<fontSize>[\d.]+</fontSize>',
                       f'<fontSize>{tsize:.3f}</fontSize>', inner)
        # remove any <size> override
        inner = re.sub(r'            <size>[\d.]+ [\d.]+</size>\n', '', inner)
        # static title handling
        inner = re.sub(r'            <text>.*?</text>\n', '', inner)
        if title:
            inner += f'            <text>{title}</text>\n'
        s = s.replace(full, f'<text name="sysName">\n{inner}\n        </text>')

    if s != orig:
        open(p, 'w').write(s)
        print(f'patched {sys}: "{title or "fullname"}" at {tsize:.3f}')
    else:
        print(f'{sys}: no change')


if __name__ == '__main__':
    # wiiu was 0.038 in v4.5, check if 0.040 fits
    from PIL import Image, ImageDraw, ImageFont
    FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    img = Image.new('RGB', (100, 100))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FB, int(0.040 * 960))
    w = d.textlength('Nintendo Wii U', font=font)
    box = 0.24 * 1280
    print(f"wiiu 'Nintendo Wii U' at 0.040: {w:.0f}px vs {box:.0f}px - {'OK' if w <= box else 'OVERFLOW'}")
    if w > box:
        V46_TITLE['wiiu'] = (None, 0.038)
        print("  -> keeping 0.038 for wiiu")

    for sys in sorted(V46_TITLE.keys()):
        patch_system(sys)
    print('DONE')
