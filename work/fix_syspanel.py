#!/usr/bin/env python3
"""v6.0.2: system-view panel fix.
1. Base views.xml: remove systemdata=fullname from sysName (it overrode every
   per-system short name -> truncated "Nintendo Game Boy C..."); rebuild the
   panel rhythm with real clearance (desc 0.280 / count 0.373 / facts 0.451).
2. Per-system: static short names for all 21 (measured to fit the 0.24 box);
   drop per-system pos overrides (the fragile "threading" that collided)."""
import re, os

ROOT = os.path.expanduser('~/workspace/crystal-esde-theme/theme-src/crystal')

NAMES = {  # short name, measured fontSize (fraction of 960, DejaVu Sans Bold, fits 0.24 box)
 'dreamcast': ('Dreamcast', 0.0400), 'gb': ('Game Boy', 0.0400),
 'gba': ('Game Boy Advance', 0.0288), 'gbc': ('Game Boy Color', 0.0348),
 'gc': ('GameCube', 0.0400), 'genesis': ('Genesis', 0.0400),
 'megadrive': ('Mega Drive', 0.0400), 'n3ds': ('Nintendo 3DS', 0.0400),
 'n64': ('Nintendo 64', 0.0400), 'nds': ('Nintendo DS', 0.0400),
 'nes': None,  # two-line sysName1/2 kept
 'ps2': ('PlayStation 2', 0.0400), 'psp': ('PSP', 0.0400),
 'psx': ('PlayStation', 0.0400), 'snes': None,  # two-line sysName1/2 kept
 'steam': ('Steam', 0.0400), 'wii': ('Wii', 0.0400), 'wiiu': ('Wii U', 0.0400),
 'windows': ('Windows', 0.0400), 'xbox': ('Xbox', 0.0400),
 'xbox360': ('Xbox 360', 0.0400),
}
# nes/snes have two-line names ending at 0.302 -> lower panel block
PANEL = {'desc': 0.280, 'count': 0.373, 'facts': 0.451}
PANEL_TALL = {'desc': 0.315, 'count': 0.410, 'facts': 0.488}

def sysname_block(name, fs):
    return (f'        <text name="sysName">\n'
            f'            <!-- short name (base systemdata binding removed: it overrode this) -->\n'
            f'            <fontSize>{fs:.4f}</fontSize>\n'
            f'            <text>{name}</text>\n'
            f'        </text>')

def sub_elem_block(src, elem, new_block):
    pat = re.compile(r'        <text name="%s">.*?\n        </text>\n' % elem, re.DOTALL)
    assert pat.search(src), f'{elem} not found'
    return pat.sub(new_block + '\n', src, count=1)

def del_pos_in_elem(src, elem):
    """Remove the <pos> line inside a named element block (no-op if absent)."""
    def fix(m):
        inner = re.sub(r'            <pos>.*?</pos>\n', '', m.group(0))
        return inner
    pat = re.compile(r'        <text name="%s">.*?\n        </text>\n' % elem, re.DOTALL)
    if not pat.search(src):
        return src
    return pat.sub(fix, src, count=1)

def set_pos_in_elem(src, elem, pos):
    pat = re.compile(r'        <text name="%s">.*?\n        </text>\n' % elem, re.DOTALL)
    if not pat.search(src):
        return src
    def fix(m):
        inner = re.sub(r'            <pos>.*?</pos>\n', '', m.group(0))
        inner = inner.replace('        <text name="%s">\n' % elem,
                              '        <text name="%s">\n            <pos>%s</pos>\n' % (elem, pos), 1)
        return inner
    return pat.sub(fix, src, count=1)

changed = []
for sysdir in sorted(os.listdir(ROOT)):
    tpath = os.path.join(ROOT, sysdir, 'theme.xml')
    if not os.path.isfile(tpath) or sysdir not in NAMES:
        continue
    src = open(tpath).read()
    orig = src
    cfg = PANEL_TALL if sysdir in ('nes', 'snes') else PANEL

    entry = NAMES[sysdir]
    if entry is None:
        # nes/snes: drop the now-pointless sysName hide block, keep sysName1/2
        if '<text name="sysName">' in src:
            src = sub_elem_block(src, 'sysName', '        <!-- sysName: two-line sysName1/2 below -->')
    else:
        name, fs = entry
        if '<text name="sysName">' in src:
            src = sub_elem_block(src, 'sysName', sysname_block(name, fs))
        else:
            # insert after mfrBadge block
            anchor = re.compile(r'(        </text>\n)(        <text name="sysName1">|    </view>)')
            # simpler: insert before the view's closing of the system view mfrBadge end
            m = re.search(r'        <text name="mfrBadge">.*?\n        </text>\n', src, re.DOTALL)
            assert m, f'mfrBadge not found in {sysdir}'
            src = src[:m.end()] + sysname_block(name, fs) + '\n' + src[m.end():]

    for elem, key in (('sysDesc', 'desc'), ('countNum', 'count'), ('factsLine', 'facts')):
        if sysdir in ('nes', 'snes'):
            src = set_pos_in_elem(src, elem, f'0.030 {cfg[key]:.3f}')
        else:
            src = del_pos_in_elem(src, elem)

    if src != orig:
        open(tpath, 'w').write(src)
        changed.append(sysdir)

print('per-system files changed:', len(changed))
print(' '.join(changed))
