#!/usr/bin/env python3
"""v6.0.4 per-console polish: each console's panel text gets positions
computed from ITS OWN measured divider lines (not 4 shared groups), with
uniform optical clearance on every page:
    desc_y  = upper_divider + 0.022   (~21px below the upper rule)
    count_y = lower_divider + 0.028   (~27px below the lower rule)
    facts_y = count_y + 0.083         (count block 0.069 + ~14px gap)
Group D (gb, nes, psx, steam, windows, xbox360): no middle dividers on
their backgrounds -> keep their established positions.
"""
import os, re
from PIL import Image
import numpy as np

ROOT = os.path.expanduser('~/workspace/crystal-esde-theme/theme-src/crystal')

def strong_dividers(bg):
    g = np.asarray(bg.convert('L'), dtype=np.float32)
    x0, x1 = int(0.035 * bg.width), int(0.265 * bg.width)
    band = g[:, x0:x1].mean(axis=1)
    k = 9
    pad = np.pad(band, k, mode='edge')
    neigh = np.convolve(pad, np.ones(2 * k + 1) / (2 * k + 1), mode='valid')
    dev = np.abs(band - neigh)
    t = dev.mean() + 2.2 * dev.std()
    cand = [i for i, d in enumerate(dev) if d > t]
    clusters, cur = [], []
    for i in cand:
        if cur and i - cur[-1] > 4:
            clusters.append(cur); cur = []
        cur.append(i)
    if cur: clusters.append(cur)
    return sorted(round(sum(c) / len(c) / bg.height, 4) for c in clusters
                  if 0.16 < sum(c) / len(c) / bg.height < 0.62)

def set_pos(view, elem, pos):
    def repl(m):
        block = m.group(0)
        if re.search(r'<pos>.*?</pos>', block):
            return re.sub(r'<pos>.*?</pos>', f'<pos>{pos}</pos>', block, count=1)
        return block.replace(f'<text name="{elem}">',
                             f'<text name="{elem}">\n<pos>{pos}</pos>', 1)
    return re.sub(r'<text name="%s">.*?</text>' % elem, repl, view,
                  flags=re.DOTALL)

OLD_NOTE = ("            <!-- v6.0.3: threaded between this background's "
            "white divider lines (measured from the baked art) -->\n")

UNCHANGED = {'gb', 'nes', 'psx', 'steam', 'windows', 'xbox360'}

print(f"{'console':<10} {'upper':<7} {'lower':<7} {'desc':<7} {'count':<7} {'facts':<7}")
for sd in sorted(d for d in os.listdir(ROOT)
                 if os.path.isfile(os.path.join(ROOT, d, 'theme.xml'))):
    if sd in UNCHANGED:
        print(f"{sd:<10} no middle dividers -> unchanged")
        continue
    bg = Image.open(f'{ROOT}/backgrounds/{sd}.webp')
    divs = strong_dividers(bg)
    if sd == 'snes':
        upper, lower = divs[2], divs[3]
    elif sd == 'gbc':
        upper, lower = divs[1], divs[2]
    else:
        assert len(divs) == 3, (sd, divs)
        upper, lower = divs[1], divs[2]
    desc_y = float(f"{upper + 0.022:.3f}")
    count_y = float(f"{lower + 0.028:.3f}")
    facts_y = float(f"{count_y + 0.083:.3f}")

    p = f'{ROOT}/{sd}/theme.xml'
    src = open(p).read()
    head, view = src.split('<view name="system">', 1)
    view, rest = view.split('</view>', 1)
    new_note = (f"            <!-- v6.0.4: per-console polish — divider lines "
                f"measured {upper:.3f}/{lower:.3f} from this background; "
                f"desc {desc_y:.3f} / count {count_y:.3f} / facts {facts_y:.3f} -->\n")
    if OLD_NOTE in view:
        view = view.replace(OLD_NOTE, new_note)
    else:
        # nes-style files never had the note; anchor after sysName block
        view = view.replace('<text name="sysDesc">',
                            new_note + '        <text name="sysDesc">', 1)
    for elem, y in (('sysDesc', desc_y), ('countNum', count_y),
                    ('factsLine', facts_y)):
        view = set_pos(view, elem, f"0.030 {y:.3f}")
    open(p, 'w').write(head + '<view name="system">' + view + '</view>' + rest)
    print(f"{sd:<10} {upper:<7.3f} {lower:<7.3f} {desc_y:<7.3f} "
          f"{count_y:<7.3f} {facts_y:<7.3f}")
