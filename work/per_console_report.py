#!/usr/bin/env python3
"""Per-console receipt: for each of the 21 consoles, print the divider lines
measured from its OWN baked background, plus the sysDesc/countNum/factsLine
positions read from the REAL theme XML, plus the clearance to the nearest
divider. This is the console-by-console evidence for the v6.0.3 polish sweep.
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

def blk(sv, name):
    return re.findall(r'<text name="%s">.*?</text>' % name, sv, re.DOTALL)

def prop(b, tag):
    ms = re.findall(r'<%s>(.*?)</%s>' % (tag, tag), b, re.DOTALL)
    return ms[-1].strip() if ms else None

print(f"{'console':<10} {'dividers (y)':<38} {'desc':<7} {'count':<7} {'facts':<7} {'min clearance':<13}")
print('-' * 95)
worst = (None, 1.0)
for sd in sorted(d for d in os.listdir(ROOT)
                 if os.path.isfile(os.path.join(ROOT, d, 'theme.xml'))):
    src = open(f'{ROOT}/{sd}/theme.xml').read()
    sv = src[src.index('<view name="system">'):src.index('</view>')]
    # per-system pos, else base views.xml positions (Group D inherits these)
    dbs = blk(sv, 'sysDesc')
    dy = float((prop(dbs[0], 'pos') if dbs and prop(dbs[0], 'pos') else '0.030 0.280').split()[1])
    cbs = blk(sv, 'countNum')
    cy = float((prop(cbs[0], 'pos') if cbs and prop(cbs[0], 'pos') else '0.030 0.373').split()[1])
    fbs = blk(sv, 'factsLine')
    fy = float((prop(fbs[0], 'pos') if fbs and prop(fbs[0], 'pos') else '0.030 0.451').split()[1])
    bg_path = f'{ROOT}/backgrounds/{sd}.webp'
    bg_path = bg_path if os.path.isfile(bg_path) else f'{ROOT}/backgrounds/_default.webp'
    divs = strong_dividers(Image.open(bg_path))
    # clearance: nearest divider to any of the three text rows (desc block ~3 lines tall)
    rows = [(dy, dy + 3 * 0.019 * 1.30), (cy, cy + 0.055 * 1.25), (fy, fy + 0.017 * 1.30)]
    clr = min((abs(r - yt) if r < yt else abs(r - yb))
              for r in divs for yt, yb in rows) if divs else 9.9
    if clr < worst[1]: worst = (sd, clr)
    print(f"{sd:<10} {str(divs):<38} {dy:<7.3f} {cy:<7.3f} {fy:<7.3f} {clr*960:>6.0f}px")
print('-' * 95)
print(f"tightest clearance of all 21: {worst[0]} at {worst[1]*960:.0f}px from the nearest divider")
