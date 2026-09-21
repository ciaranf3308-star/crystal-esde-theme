#!/usr/bin/env python3
"""Detect horizontal ruled lines inside the baked panel band (x 0.02..0.27)
for each console background, and check every live text line against them."""
import os, re
from PIL import Image, ImageFont
import numpy as np

ROOT = os.path.expanduser('~/workspace/crystal-esde-theme/theme-src/crystal')
W, H = 1280, 960
FBB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
PX = 0.03 * W  # text left edge px

def lines_in_band(bg):
    """Return sorted list of y-fractions where a horizontal ruled line
    crosses the panel band. A ruled line = a row whose full-band mean
    brightness deviates sharply from the local neighbourhood."""
    g = np.asarray(bg.convert('L'), dtype=np.float32)
    x0, x1 = int(0.035 * bg.width), int(0.265 * bg.width)
    band = g[:, x0:x1].mean(axis=1)          # mean brightness per row
    k = 9                                    # neighbourhood
    pad = np.pad(band, k, mode='edge')
    neigh = (pad[:-2*k].cumsum() if False else
             np.convolve(pad, np.ones(2*k+1)/(2*k+1), mode='valid'))
    dev = np.abs(band - neigh)
    thresh = dev.mean() + 2.2 * dev.std()
    cand = [i for i, d in enumerate(dev) if d > thresh]
    # cluster adjacent rows, take cluster centres
    clusters, cur = [], []
    for i in cand:
        if cur and i - cur[-1] > 4:
            clusters.append(cur); cur = []
        cur.append(i)
    if cur: clusters.append(cur)
    out = []
    for c in clusters:
        y = sum(c) / len(c) / bg.height
        if 0.16 < y < 0.60:                  # panel text zone
            out.append(round(y, 4))
    return out

def wrap(text, font, maxw):
    words, lines, cur = text.split(' '), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if font.getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur); return lines

def fs(f): return round(float(f) * H)

def text_rows(sd):
    """Return list of (label, y_top_frac, y_bot_frac) for each rendered
    text line in the panel, mirroring theme positions."""
    src = open(f'{ROOT}/{sd}/theme.xml').read()
    sv = src[src.index('<view name="system">'):src.index('</view>')]
    def blk(name):
        m = re.search(r'<text name="%s">.*?</text>' % name, sv, re.DOTALL)
        return m.group(0) if m else ''
    def inner(b):
        ms = re.findall(r'(?<!name=)<text>(.*?)</text>', b, re.DOTALL)
        return ms[-1].strip() if ms else ''
    def prop(b, tag):
        m = re.search(r'<%s>(.*?)</%s>' % (tag, tag), b, re.DOTALL)
        return m.group(1).strip() if m else None
    rows = []
    btxt = inner(blk('mfrBadge')).upper()
    bf = ImageFont.truetype(FBB, fs(0.018))
    chip_h = fs(0.018) * 1.9 / H
    rows.append(('badge', 0.195, 0.195 + chip_h))
    if sd in ('nes', 'snes'):
        n1, n2 = inner(blk('sysName1')), inner(blk('sysName2'))
        rows.append(('name1', 0.226, 0.226 + 0.040 * 1.25))
        rows.append(('name2', 0.266, 0.266 + 0.022 * 1.25))
        dy, cy, fy = 0.315, 0.410, 0.488
    else:
        nb = blk('sysName')
        nfs = float(prop(nb, 'fontSize') or 0.040)
        rows.append(('name', 0.230, 0.230 + nfs * 1.25))
        dy = float((prop(blk('sysDesc'), 'pos') or '0.030 0.280').split()[1])
        cb = blk('countNum')
        cy = float((prop(cb, 'pos') if cb else None or '0.030 0.373').split()[1]) \
            if (prop(cb, 'pos') if cb else None) else 0.373
        fb = blk('factsLine')
        fy = float((prop(fb, 'pos') if fb else None or '0.030 0.451').split()[1]) \
            if (prop(fb, 'pos') if fb else None) else 0.451
    df = ImageFont.truetype(FBB, fs(0.019))
    db = blk('sysDesc')
    dsizex = float((prop(db, 'size') or '0.20 0.140').split()[0])
    for i, ln in enumerate(wrap(inner(db), df, dsizex * W)):
        yt = dy + i * 0.019 * 1.30
        rows.append((f'desc{i}', yt, yt + 0.019 * 1.30))
    rows.append(('count', cy, cy + 0.055 * 1.25))
    rows.append(('facts', fy, fy + 0.017 * 1.30))
    return rows, inner(blk('sysDesc'))

print(f'{"console":10} {"ruled lines (y)":55} collisions')
print('-' * 110)
all_hits = []
for sd in sorted(d for d in os.listdir(ROOT)
                 if os.path.isfile(os.path.join(ROOT, d, 'theme.xml'))):
    bg = f'{ROOT}/backgrounds/{sd}.webp'
    bg = bg if os.path.isfile(bg) else f'{ROOT}/backgrounds/_default.webp'
    rl = lines_in_band(Image.open(bg))
    rows, desc = text_rows(sd)
    hits = []
    for label, yt, yb in rows:
        for r in rl:
            if yt - 0.004 <= r <= yb + 0.004:
                hits.append(f'{label}@{r:.3f}')
                break
    all_hits.append((sd, rl, hits))
    flag = '  <-- COLLISION' if hits else ''
    print(f'{sd:10} {str(rl):55} {", ".join(hits)}{flag}')
