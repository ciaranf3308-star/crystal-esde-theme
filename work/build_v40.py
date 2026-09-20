#!/usr/bin/env python3
"""Crystal ES-DE v4.0.0 build script.

1. STAGE — rebuild theme-src/crystal/art/carousel_vignette.png with the
   baked spotlight recentered on the v4 selected slot
   (screen x 0.5, y 0.85 -> 0.558 of the 0.66..1.00 stage height).
2. NAMES — measure every system's fullName with DejaVu Sans Bold at the
   v4 base size (0.040) against the v4 title box (0.24), then rewrite the
   per-system theme.xml files with the measured sizes. nes/snes keep
   their two-line static names (repositioned for the v4 text layout).
   gb's narrower panel is measured from its background art and gets
   matching width overrides.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

REPO = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal'
ART_DIR = os.path.join(REPO, 'art')
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

W, H = 1280, 960
BASE_SIZE = 0.040          # v4 sysName base fontSize (fraction of H)
TITLE_BOX = 0.24           # v4 sysName box width (fraction of W)

# sys -> (mfr, desc, facts, fullName or None for two-line systems)
SYSTEMS = {
    'dreamcast': ('SEGA', "Sega's 128-bit swan song. Arcade soul, VMU dreams.",
                  '128-BIT \u2022 1999', 'Sega Dreamcast'),
    'gb': ('NINTENDO', 'The brick that built handhelds. Tetris forever.',
           '8-BIT \u2022 HANDHELD \u2022 1989', 'Nintendo Game Boy'),
    'gba': ('NINTENDO', "Nintendo's 32-bit handheld. A massive 2D library.",
            '32-BIT \u2022 HANDHELD \u2022 2001', 'Nintendo Game Boy Advance'),
    'gbc': ('NINTENDO', 'Color came to the brick. A pocket rainbow of classics.',
            '8-BIT \u2022 HANDHELD \u2022 1998', 'Nintendo Game Boy Color'),
    'gc': ('NINTENDO', "Nintendo's cube of joy. Smash and Sunshine.",
           '128-BIT \u2022 2001', 'Nintendo GameCube'),
    'genesis': ('SEGA', "Blast-processing attitude. Sonic's 16-bit battleground.",
                '16-BIT \u2022 1989', 'Sega Genesis'),
    'megadrive': ('SEGA', "Europe's name for Sega's 16-bit speed machine.",
                  '16-BIT \u2022 1990', 'Sega Mega Drive'),
    'n3ds': ('NINTENDO', 'Glasses-free 3D in your pocket. StreetPass fun.',
             'HANDHELD \u2022 2011', 'Nintendo 3DS'),
    'n64': ('NINTENDO', 'The 3D pioneer. Mario 64 changed everything.',
            '64-BIT \u2022 1996', 'Nintendo 64'),
    'nds': ('NINTENDO', 'Two screens, one stylus, endless experiments.',
            'HANDHELD \u2022 2004', 'Nintendo DS'),
    'ps2': ('SONY', 'The best-selling console ever. An endless library.',
            '128-BIT \u2022 2000', 'Sony PlayStation 2'),
    'psp': ('SONY', 'Console power in your pocket. UMD adventures.',
            'HANDHELD \u2022 2005', 'Sony PlayStation Portable'),
    'psx': ('SONY', 'Where 3D grew up. Crash, Spyro, Final Fantasy VII.',
            '32-BIT \u2022 1995', 'Sony PlayStation'),
    'steam': ('VALVE', "PC gaming's front door. Thousands of worlds await.",
              'PC \u2022 2003', 'Steam'),
    'wii': ('NINTENDO', 'Motion gaming for all. Wii Bowling nights.',
            '2006', 'Nintendo Wii'),
    'wiiu': ('NINTENDO', 'The GamePad experiment. Hidden gems await.',
             '2012', 'Nintendo Wii U'),
    'windows': ('PC', 'PC classics, indie gems and emulation everything.',
                'PC', 'Windows'),
    'xbox': ('MICROSOFT', "The green giant's first shot. Halo defined a generation.",
             '2001', 'Microsoft Xbox'),
    'xbox360': ('MICROSOFT', 'HD-era pioneer. A legendary library.',
                '2005', 'Microsoft Xbox 360'),
}

TWO_LINE = {
    'nes': ('NINTENDO', 'ENTERTAINMENT SYSTEM',
            'The gray box that saved gaming. 8-bit legends.',
            '8-BIT \u2022 1985'),
    'snes': ('SUPER NINTENDO', 'ENTERTAINMENT SYSTEM',
             'The 16-bit golden age. Mode 7 magic.',
             '16-BIT \u2022 1991'),
}

# Panel text threading (v4.0.0): the 4:3 panel art is deliberately ruled —
# bright horizontal rules baked into the design (the 324/472 grid and its
# variants). Text crossing a rule mid-glyph reads as a strikethrough, so
# each system's desc/count/facts y-positions thread the gaps between ITS
# background's detected strong rules (delta > 40). Title/badge zone
# (0.195..0.270) is rule-free on all 21 backgrounds and stays global.
# sys -> (desc_y, count_y, facts_y) as fractions of H; None = base positions.
LAYOUTS = {
    # 324/472 grid: desc 270..318, count 340..393, facts 398..414
    'gba': (0.281, 0.354, 0.415),
    'genesis': (0.281, 0.354, 0.415),
    'megadrive': (0.281, 0.354, 0.415),
    'n3ds': (0.281, 0.354, 0.415),
    'n64': (0.281, 0.354, 0.415),
    'ps2': (0.281, 0.354, 0.415),
    'psp': (0.281, 0.354, 0.415),
    'wii': (0.281, 0.354, 0.415),
    'wiiu': (0.281, 0.354, 0.415),
    'xbox': (0.281, 0.354, 0.415),
    # 320/474 + 320/489 grids: desc 264..312, count 336..389, facts 395..411
    'dreamcast': (0.275, 0.350, 0.411),
    'gc': (0.275, 0.350, 0.411),
    # 284/408 grid: desc 290..338, count 344..397, facts 414..430
    'gbc': (0.302, 0.358, 0.431),
    # 315/460 grid: desc 262..310, count 330..383, facts 389..405
    'nds': (0.273, 0.344, 0.405),
    # 321/491 grid, two-line name: desc 327..375, count 381..434, facts 440..456
    'snes': (0.341, 0.397, 0.458),
    # clean panels (no strong rules): gb, nes, psx, steam, windows, xbox360
}

HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<theme>
    <!-- Crystal v4.0: 4:3 Nova layout. Text inherits the base panel
         positions from views.xml; only content and the measured name size
         are set here (DejaVu Sans Bold, title box 0.24). -->
    <include>./../variables.xml</include>
    <include>./../views.xml</include>
    <view name="system">
"""

FOOTER = """    </view>
</theme>
"""


def text_width(text, px):
    return ImageFont.truetype(FB, px).getlength(text)


def fit_size(text, box_frac, base=BASE_SIZE):
    """Largest fontSize (fraction of H) fitting text in box_frac of W."""
    box_px = box_frac * W
    w = text_width(text, int(base * H))
    size = base * min(1.0, box_px / w)
    return math.floor(size * 1000) / 1000  # round DOWN: stay inside the box


def measure_gb_panel():
    """gb's supplied hero has a narrower blue panel; measure its width."""
    bg = Image.open(os.path.join(REPO, 'backgrounds', 'gb.webp')).convert('RGB')
    bw, bh = bg.size
    y = int(0.30 * bh)
    row = [bg.getpixel((x, y)) for x in range(bw)]
    # panel color: median of the left region (inside the panel)
    sample = row[int(0.03 * bw):int(0.10 * bw)]
    pr = sum(c[0] for c in sample) // len(sample)
    pg = sum(c[1] for c in sample) // len(sample)
    pb = sum(c[2] for c in sample) // len(sample)
    edge = bw
    for x in range(int(0.05 * bw), bw):
        r, g, b = row[x]
        if abs(r - pr) + abs(g - pg) + abs(b - pb) > 90:
            edge = x
            break
    frac = edge / bw
    print(f'gb panel right edge: {frac:.3f} (px {edge} of {bw})')
    return frac


def build_stage():
    W2, H2 = 1920, 360
    img = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    px = img.load()
    stops = [(0.0, (34, 76, 196)), (0.45, (16, 48, 138)), (1.0, (5, 13, 48))]
    for y in range(H2):
        t = y / (H2 - 1)
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                k = (t - t0) / max(t1 - t0, 1e-6)
                col = tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
                break
        for x in range(W2):
            px[x, y] = col + (255,)
    # v4.0.0: baked center spotlight on the v4 selected slot
    # (screen y 0.85 -> (0.85-0.66)/0.34 = 0.559 of stage height)
    gc_x, gc_y, gc_r = W2 / 2, H2 * 0.559, W2 * 0.28
    for y in range(H2):
        for x in range(W2):
            r = math.hypot(x - gc_x, y - gc_y) / gc_r
            if r < 1:
                k = (1 - r) ** 2.6
                lift = int(52 * k)
                pr, pg, pb, _ = px[x, y]
                px[x, y] = (min(255, pr + lift), min(255, pg + lift),
                            min(255, pb + int(lift * 1.25)), 255)
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, W2, 3], fill=(235, 244, 255, 160))
    for y in range(4, 40):
        a = int(60 * (1 - y / 40) ** 1.8)
        d.line([0, y, W2, y], fill=(150, 190, 255, a))
    row = 0
    for yy in range(120, H2, 24):
        off = 12 if row % 2 else 0
        for xx in range(12 + off, W2, 24):
            depth = 1 - yy / H2
            r = 2 + 2 * depth
            d.ellipse([xx - r, yy - r, xx + r, yy + r],
                      fill=(255, 255, 255, int(5 + 12 * depth)))
        row += 1
    alpha = img.getchannel('A')
    rgb = img.convert('RGB')
    arr = bytearray(rgb.tobytes())
    for x in range(W2):
        edge = abs(x / W2 - 0.5) * 2
        k = 1.0 - 0.45 * max(0.0, (edge - 0.45) / 0.55) ** 1.6
        for y in range(H2):
            o = (y * W2 + x) * 3
            arr[o] = int(arr[o] * k)
            arr[o + 1] = int(arr[o + 1] * k)
            arr[o + 2] = int(arr[o + 2] * k)
    img = Image.frombytes('RGB', (W2, H2), bytes(arr)).convert('RGBA')
    img.putalpha(alpha)
    img.save(os.path.join(ART_DIR, 'carousel_vignette.png'))
    print('stage carousel_vignette.png', img.size)


def body_single(mfr, desc, facts, name_size, box=TITLE_BOX, layout=None):
    parts = []
    parts.append('        <text name="mfrBadge">\n'
                 f'            <text>{mfr}</text>\n'
                 '        </text>\n')
    if abs(name_size - BASE_SIZE) > 1e-9 or box != TITLE_BOX:
        parts.append('        <text name="sysName">\n'
                     '            <!-- measured with DejaVu Sans Bold: fullName fits one line on the 4:3 panel -->\n')
        if box != TITLE_BOX:
            parts.append(f'            <size>{box:.3f} 0.055</size>\n')
        parts.append(f'            <fontSize>{name_size:.3f}</fontSize>\n'
                     '        </text>\n')
    desc_y, count_y, facts_y = layout or (None, None, None)
    parts.append('        <text name="sysDesc">\n')
    if desc_y:
        parts.append(f'            <!-- panel threading: sits between this background\'s ruled lines -->\n'
                     f'            <pos>0.030 {desc_y:.3f}</pos>\n')
    parts.append(f'            <text>{desc}</text>\n'
                 '        </text>\n')
    if count_y:
        parts.append('        <text name="countNum">\n'
                     f'            <pos>0.030 {count_y:.3f}</pos>\n'
                     '        </text>\n')
    parts.append('        <text name="factsLine">\n')
    if facts_y:
        parts.append(f'            <pos>0.030 {facts_y:.3f}</pos>\n')
    parts.append(f'            <text>{facts}</text>\n'
                 '        </text>\n')
    return ''.join(parts)


def body_two_line(line1, line2, desc, facts, mfr, layout=None):
    s1 = fit_size(line1, TITLE_BOX)
    s2 = fit_size(line2, TITLE_BOX)
    desc_y, count_y, facts_y = layout or (0.305, 0.460, 0.535)
    return (f'''        <text name="mfrBadge">
            <text>{mfr}</text>
        </text>
        <text name="sysName">
            <!-- base single-line name hidden: two-line name below -->
            <pos>-1 -1</pos>
        </text>
        <text name="sysName1">
            <!-- two-line name mirrors the baked graffiti title -->
            <pos>0.030 0.226</pos>
            <size>0.24 0.05</size>
            <fontSize>{s1:.3f}</fontSize>
            <color>${{crystalText}}</color>
            <horizontalAlignment>left</horizontalAlignment>
            <zIndex>50</zIndex>
            <text>{line1}</text>
        </text>
        <text name="sysName2">
            <pos>0.030 0.266</pos>
            <size>0.24 0.036</size>
            <fontSize>{s2:.3f}</fontSize>
            <color>${{crystalText}}</color>
            <horizontalAlignment>left</horizontalAlignment>
            <zIndex>50</zIndex>
            <text>{line2}</text>
        </text>
        <text name="sysDesc">
            <!-- panel threading: sits between this background's ruled lines -->
            <pos>0.030 {desc_y:.3f}</pos>
            <text>{desc}</text>
        </text>
        <text name="countNum">
            <pos>0.030 {count_y:.3f}</pos>
        </text>
        <text name="factsLine">
            <pos>0.030 {facts_y:.3f}</pos>
            <text>{facts}</text>
        </text>
''')


def main():
    build_stage()
    gb_edge = measure_gb_panel()
    gb_box = math.floor((gb_edge - 0.030 - 0.015) * 1000) / 1000  # margin inside panel

    for sys, (mfr, desc, facts, full) in SYSTEMS.items():
        box = gb_box if sys == 'gb' else TITLE_BOX
        size = fit_size(full, box)
        layout = LAYOUTS.get(sys)
        xml = HEADER + body_single(mfr, desc, facts, size, box, layout) + FOOTER
        # gb also needs narrower desc/count boxes to stay inside its panel
        if sys == 'gb':
            extra = (f'        <text name="sysDesc">\n'
                     f'            <size>{gb_box:.3f} 0.140</size>\n'
                     f'        </text>\n'
                     f'        <text name="countNum">\n'
                     f'            <fontSize>0.042</fontSize>\n'
                     f'            <size>{gb_box:.3f} 0.07</size>\n'
                     f'        </text>\n')
            xml = xml.replace('    </view>', extra + '    </view>')
        path = os.path.join(REPO, sys, 'theme.xml')
        with open(path, 'w') as f:
            f.write(xml)
        flag = '' if abs(size - BASE_SIZE) < 1e-9 and box == TITLE_BOX else f' <- size {size:.3f} box {box:.3f}'
        print(f'wrote {sys}{flag}')

    for sys, (l1, l2, desc, facts) in TWO_LINE.items():
        mfr = 'NINTENDO'
        xml = HEADER + body_two_line(l1, l2, desc, facts, mfr, LAYOUTS.get(sys)) + FOOTER
        path = os.path.join(REPO, sys, 'theme.xml')
        with open(path, 'w') as f:
            f.write(xml)
        print('wrote', sys, '(two-line)')
    print('DONE')


if __name__ == '__main__':
    main()
