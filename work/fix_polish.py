#!/usr/bin/env python3
"""v6.0.3 polish sweep: thread each console's panel text between its own
baked white divider lines (detected from the background art, not eyeballed).

Groups (strong divider lines @ mult 2.2):
  A: dreamcast, gba, gc, genesis, megadrive, n3ds, n64, nds, ps2, psp,
     wii, wiiu, xbox  (~0.339 / ~0.493)
     desc 0.356 / count 0.511 / facts 0.594
  B: gbc (0.2965 / 0.4259)
     desc 0.312 / count 0.444 / facts 0.527
  C: snes (0.3353 / 0.3855 / 0.5115, two-line name)
     desc 0.404 / count 0.530 / facts 0.613
  D: gb, nes, psx, steam, windows, xbox360 (no mid dividers) -> unchanged

Also:
  - gb: remove leftover <size>0.228 0.140</size> sysDesc override
        (duplicate-element merge made wrap width inconsistent).
  - snes: sysName1 "SUPER NINTENDO" @0.032 overflows the 0.24 box
        (310px > 307px) -> 0.031.
"""
import os, re

ROOT = os.path.expanduser('~/workspace/crystal-esde-theme/theme-src/crystal')

GROUP_A = ['dreamcast', 'gba', 'gc', 'genesis', 'megadrive', 'n3ds', 'n64',
           'nds', 'ps2', 'psp', 'wii', 'wiiu', 'xbox']
POS = {}
for sd in GROUP_A:
    POS[sd] = {'sysDesc': '0.030 0.356', 'countNum': '0.030 0.511',
               'factsLine': '0.030 0.594'}
POS['gbc'] = {'sysDesc': '0.030 0.312', 'countNum': '0.030 0.444',
              'factsLine': '0.030 0.527'}
POS['snes'] = {'sysDesc': '0.030 0.404', 'countNum': '0.030 0.530',
               'factsLine': '0.030 0.613'}

THREAD_NOTE = ('            <!-- v6.0.3: threaded between this background\'s '
               'white divider lines (measured from the baked art) -->\n')

def set_pos(view, elem, pos):
    """Set <pos> on every <text name=elem> block in view (insert if absent)."""
    def repl(m):
        block = m.group(0)
        if re.search(r'<pos>.*?</pos>', block):
            return re.sub(r'<pos>.*?</pos>', f'<pos>{pos}</pos>', block, count=1)
        return block.replace(f'<text name="{elem}">',
                             f'<text name="{elem}">\n<pos>{pos}</pos>', 1)
    return re.sub(r'<text name="%s">.*?</text>' % elem, repl, view,
                  flags=re.DOTALL)

for sd, elems in POS.items():
    p = f'{ROOT}/{sd}/theme.xml'
    src = open(p).read()
    head, view = src.split('<view name="system">', 1)
    view, rest = view.split('</view>', 1)
    view = view.replace(
        "            <!-- panel threading: sits between this background's ruled lines -->\n",
        THREAD_NOTE)
    for elem, pos in elems.items():
        view = set_pos(view, elem, pos)
    open(p, 'w').write(head + '<view name="system">' + view + '</view>' + rest)
    print('threaded', sd)

# gb: drop the stray duplicate sysDesc size override
p = f'{ROOT}/gb/theme.xml'
src = open(p).read()
new = re.sub(
    r'        <text name="sysDesc">\n            <size>0\.228 0\.140</size>\n        </text>\n',
    '', src)
assert new != src
open(p, 'w').write(new)
print('gb: removed stray sysDesc size override')

# snes: sysName1 0.032 -> 0.031 (310px overflowed the 307px box)
p = f'{ROOT}/snes/theme.xml'
src = open(p).read()
new = src.replace(
    '<text name="sysName1">\n            <!-- two-line name mirrors the baked graffiti title -->\n'
    '            <pos>0.030 0.226</pos>\n            <size>0.24 0.05</size>\n'
    '            <fontSize>0.032</fontSize>',
    '<text name="sysName1">\n            <!-- two-line name mirrors the baked graffiti title -->\n'
    '            <pos>0.030 0.226</pos>\n            <size>0.24 0.05</size>\n'
    '            <fontSize>0.031</fontSize> <!-- v6.0.3: 0.032 overflowed the 0.24 box (310px) -->',
    1)
assert new != src
open(p, 'w').write(new)
print('snes: sysName1 0.032 -> 0.031')
