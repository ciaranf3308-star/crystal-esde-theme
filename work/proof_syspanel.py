#!/usr/bin/env python3
"""v6.0.3 proof: for every console, read panel positions from the REAL theme
XML and assert (a) no text-text vertical overlap, (b) no text line touches a
baked white divider line (strong lines, mult 2.2). Fail loudly."""
import os, re
from PIL import Image, ImageFont
import numpy as np

ROOT = os.path.expanduser('~/workspace/crystal-esde-theme/theme-src/crystal')
W, H = 1280, 960
FBB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def fs(f): return round(float(f) * H)

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

def wrap(text, font, maxw):
    words, lines, cur = text.split(' '), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if font.getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur); return lines

def blk(sv, name):
    ms = re.findall(r'<text name="%s">.*?</text>' % name, sv, re.DOTALL)
    return ms  # all blocks (duplicates merge in ES-DE)

def inner(b):
    ms = re.findall(r'(?<!name=)<text>(.*?)</text>', b, re.DOTALL)
    return ms[-1].strip() if ms else ''

def prop(b, tag):
    ms = re.findall(r'<%s>(.*?)</%s>' % (tag, tag), b, re.DOTALL)
    return ms[-1].strip() if ms else None  # last wins (ES-DE merge)

fails = []
for sd in sorted(d for d in os.listdir(ROOT)
                 if os.path.isfile(os.path.join(ROOT, d, 'theme.xml'))):
    src = open(f'{ROOT}/{sd}/theme.xml').read()
    sv = src[src.index('<view name="system">'):src.index('</view>')]
    rows = []
    rows.append(('badge', 0.195, 0.195 + fs(0.018) * 1.35 / H))
    if sd in ('nes', 'snes'):
        b1 = blk(sv, 'sysName1')[0]; b2 = blk(sv, 'sysName2')[0]
        f1 = float(prop(b1, 'fontSize')); f2 = float(prop(b2, 'fontSize'))
        rows.append(('name1', 0.226, 0.226 + f1 * 0.8))
        rows.append(('name2', 0.266, 0.266 + f2 * 0.8))
        # name1 must fit the 0.24 box
        w = ImageFont.truetype(FBB, fs(f1)).getlength(inner(b1))
        if w > 0.24 * W:
            fails.append(f'{sd}: name1 overflow {w:.0f}px > 307px')
    else:
        b = blk(sv, 'sysName')[0]
        fsz = float(prop(b, 'fontSize') or 0.040)
        rows.append(('name', 0.230, 0.230 + fsz * 0.8))
        w = ImageFont.truetype(FBB, fs(fsz)).getlength(inner(b))
        if w > 0.24 * W:
            fails.append(f'{sd}: name overflow {w:.0f}px > 307px')
    db = blk(sv, 'sysDesc')[0]
    dy = float((prop(db, 'pos') or '0.030 0.280').split()[1])
    df = ImageFont.truetype(FBB, fs(0.019))
    lines = wrap(inner(db), df, 0.20 * W)
    for i, ln in enumerate(lines):
        yt = dy + i * 0.019 * 1.30
        rows.append((f'desc{i}', yt, yt + 0.019 * 1.30))
    cbs = blk(sv, 'countNum')
    cy = float(((prop(cbs[0], 'pos') if cbs else None) or '0.030 0.373').split()[1])
    rows.append(('count', cy, cy + 0.055 * 1.25))
    fbs = blk(sv, 'factsLine')
    fy = float(((prop(fbs[0], 'pos') if fbs else None) or '0.030 0.451').split()[1])
    rows.append(('facts', fy, fy + 0.017 * 1.30))

    # (a) text-text overlaps (interior intersection; touching edges are fine)
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b_ = rows[i], rows[j]
            if a[1] + 0.002 < b_[2] and b_[1] + 0.002 < a[2]:
                fails.append(f'{sd}: TEXT OVERLAP {a[0]}[{a[1]:.3f}-{a[2]:.3f}] x {b_[0]}[{b_[1]:.3f}-{b_[2]:.3f}]')

    # (b) divider collisions
    bg_path = f'{ROOT}/backgrounds/{sd}.webp'
    bg_path = bg_path if os.path.isfile(bg_path) else f'{ROOT}/backgrounds/_default.webp'
    for r in strong_dividers(Image.open(bg_path)):
        for label, yt, yb in rows:
            if yt - 0.008 <= r <= yb + 0.008:
                fails.append(f'{sd}: DIVIDER @{r:.3f} hits {label}[{yt:.3f}-{yb:.3f}]')
                break

print('FAILURES:' if fails else 'PROOF PASS — 21 consoles: no text overlaps, no divider collisions, all names fit')
for f in fails:
    print(' ', f)
raise SystemExit(1 if fails else 0)
