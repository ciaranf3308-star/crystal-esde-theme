#!/usr/bin/env python3
"""Crystal ES-DE v3.3.0: rewrite per-system theme.xml files for the 4:3 Nova.

The Nova is 1280x960 (4:3). All backgrounds are 4:3 with the blue info panel
at x ~0.013-0.28, so every system inherits the base text positions from
views.xml. Per-system files only override: static texts (mfrBadge/sysDesc/
factsLine) and sysName fontSize, measured with DejaVu Sans Bold so the
fullName fits one line inside the panel (box 0.22, target width <= 0.20).
snes keeps its two-line static name; nes is already 4:3-correct and untouched.
"""
import os

CRYSTAL = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal'

HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<theme>
    <!-- Crystal v3.3: 4:3 Nova layout. Text inherits the base panel positions
         from views.xml; only content and the measured name size are set here. -->
    <include>./../variables.xml</include>
    <include>./../views.xml</include>
    <view name="system">
"""

FOOTER = """    </view>
</theme>
"""

# sys -> (mfr, desc, facts, nameSize or None for base 0.030)
SYSTEMS = {
    'dreamcast': ('SEGA', "Sega's 128-bit swan song. Arcade soul with VMU dreams.",
                  '128-BIT \u2022 1999', 0.028),
    'gb': ('NINTENDO', 'The brick that built handheld gaming. Tetris forever.',
           '8-BIT \u2022 HANDHELD \u2022 1989', 0.023),
    'gba': ('NINTENDO', "Nintendo's 32-bit handheld brought iconic franchises and a massive 2D library to a new generation.",
            '32-BIT \u2022 HANDHELD \u2022 2001', 0.016),
    'gbc': ('NINTENDO', 'Color came to the brick. A pocket rainbow of classics.',
            '8-BIT \u2022 HANDHELD \u2022 1998', 0.018),
    'gc': ('NINTENDO', "Nintendo's cube of joy. Smash, Sunshine and Wind Waker.",
           '128-BIT \u2022 2001', 0.023),
    'genesis': ('SEGA', "Blast-processing attitude. Sonic's 16-bit battleground.",
                '16-BIT \u2022 1989', None),
    'megadrive': ('SEGA', "Europe's name for Sega's 16-bit speed machine.",
                  '16-BIT \u2022 1990', 0.027),
    'n3ds': ('NINTENDO', 'Glasses-free 3D in your pocket. StreetPass adventures.',
             'HANDHELD \u2022 2011', None),
    'n64': ('NINTENDO', 'Three-pronged pioneer of 3D. Mario 64 changed everything.',
            '64-BIT \u2022 1996', None),
    'nds': ('NINTENDO', 'Two screens, one stylus, endless touch-screen experiments.',
            'HANDHELD \u2022 2004', None),
    'ps2': ('SONY', 'The best-selling console ever. An endless library.',
            '128-BIT \u2022 2000', 0.025),
    'psp': ('SONY', 'Console power in your pocket. UMD adventures.',
            'HANDHELD \u2022 2005', 0.018),
    'psx': ('SONY', 'Where 3D grew up. Crash, Spyro, Final Fantasy VII.',
            '32-BIT \u2022 1995', 0.027),
    'steam': ('VALVE', "PC gaming's front door. Thousands of worlds await.",
              'PC \u2022 2003', None),
    'wii': ('NINTENDO', 'Motion controls for everyone. Bowling in living rooms.',
            '2006', None),
    'wiiu': ('NINTENDO', 'The GamePad experiment. Hidden gems await.',
             '2012', None),
    'windows': ('PC', 'PC classics, indie gems and emulation everything.',
                'PC', None),
    'xbox': ('MICROSOFT', "The green giant's first shot. Halo defined a generation.",
             '2001', None),
    'xbox360': ('MICROSOFT', 'HD-era pioneer. A legendary library.',
                '2005', 0.024),
}

SNES = """<?xml version="1.0" encoding="UTF-8"?>
<theme>
    <!-- Crystal v3.3: 4:3 Nova layout. Two-line static name mirrors the baked
         graffiti title; "SUPER NINTENDO" measured to fit the 4:3 panel. -->
    <include>./../variables.xml</include>
    <include>./../views.xml</include>
    <view name="system">
        <text name="mfrBadge">
            <text>NINTENDO</text>
        </text>
        <text name="sysName">
            <!-- base single-line name hidden: snes uses a two-line name below -->
            <pos>-1 -1</pos>
        </text>
        <text name="sysName1">
            <pos>0.028 0.228</pos>
            <size>0.22 0.05</size>
            <fontSize>0.028</fontSize>
            <color>${crystalText}</color>
            <horizontalAlignment>left</horizontalAlignment>
            <zIndex>50</zIndex>
            <text>SUPER NINTENDO</text>
        </text>
        <text name="sysName2">
            <pos>0.028 0.264</pos>
            <size>0.22 0.04</size>
            <fontSize>0.019</fontSize>
            <color>${crystalText}</color>
            <horizontalAlignment>left</horizontalAlignment>
            <zIndex>50</zIndex>
            <text>ENTERTAINMENT SYSTEM</text>
        </text>
        <text name="sysDesc">
            <text>The 16-bit golden age. Mode 7 magic and timeless RPGs.</text>
        </text>
        <text name="factsLine">
            <text>16-BIT \u2022 1991</text>
        </text>
    </view>
</theme>
"""


def body(mfr, desc, facts, name_size):
    parts = []
    parts.append('        <text name="mfrBadge">\n'
                 f'            <text>{mfr}</text>\n'
                 '        </text>\n')
    if name_size is not None:
        parts.append('        <text name="sysName">\n'
                     '            <!-- measured with DejaVu Sans Bold: fullName fits one line on the 4:3 panel -->\n'
                     f'            <fontSize>{name_size:.3f}</fontSize>\n'
                     '        </text>\n')
    parts.append('        <text name="sysDesc">\n'
                 f'            <text>{desc}</text>\n'
                 '        </text>\n')
    parts.append('        <text name="factsLine">\n'
                 f'            <text>{facts}</text>\n'
                 '        </text>\n')
    return ''.join(parts)


def main():
    for sys, (mfr, desc, facts, name_size) in SYSTEMS.items():
        path = os.path.join(CRYSTAL, sys, 'theme.xml')
        with open(path, 'w') as f:
            f.write(HEADER + body(mfr, desc, facts, name_size) + FOOTER)
        print('wrote', sys)
    with open(os.path.join(CRYSTAL, 'snes', 'theme.xml'), 'w') as f:
        f.write(SNES)
    print('wrote snes')
    print('nes left untouched (already 4:3-correct)')
    print('DONE')


if __name__ == '__main__':
    main()
