#!/usr/bin/env python3
"""Console-by-console polish sweep: render each system's panel over its REAL
baked background (1448x1086 webp -> 1280x960 frame) with the live text
elements at their theme positions. Inspect for text-vs-art collisions."""
import os, re
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.expanduser('~/workspace/crystal-esde-theme/theme-src/crystal')
W, H = 1280, 960
FBB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FB  = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def fs(f):  # fraction-of-screen font size -> px at 1280x960 (ES-DE: fontSize*H)
    return max(8, round(float(f) * H))

def wrap(text, font, maxw):
    words, lines, cur = text.split(' '), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if font.getlength(t) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = wd
    lines.append(cur)
    return lines

def txt(d, xf, yf, s, sizef, fill, font=FBB):
    d.text((xf * W, yf * H), s, font=ImageFont.truetype(font, fs(sizef)), fill=fill)

# per-console parsed data
sysdirs = sorted(d for d in os.listdir(ROOT)
                 if os.path.isfile(os.path.join(ROOT, d, 'theme.xml')))
panels = []
for sd in sysdirs:
    src = open(f'{ROOT}/{sd}/theme.xml').read()
    sv = src[src.index('<view name="system">'):src.index('</view>')]
    def blk(name):
        m = re.search(r'<text name="%s">.*?</text>\s*(?=<text|</view>)' % name, sv, re.DOTALL)
        if not m:
            m = re.search(r'<text name="%s">.*?</text>' % name, sv, re.DOTALL)
        return m.group(0) if m else ''
    def inner(b):
        ms = re.findall(r'(?<!name=)<text>(.*?)</text>', b, re.DOTALL)
        return ms[-1].strip() if ms else ''
    def prop(b, tag):
        m = re.search(r'<%s>(.*?)</%s>' % (tag, tag), b, re.DOTALL)
        return m.group(1).strip() if m else None
    if sd in ('nes', 'snes'):
        name = (inner(blk('sysName1')), inner(blk('sysName2')))
        desc_pos, count_pos, facts_pos = (0.030, 0.315), (0.030, 0.410), (0.030, 0.488)
    else:
        nb = blk('sysName')
        name = inner(nb)
        name_fs = float(prop(nb, 'fontSize') or 0.040)
        desc_pos = tuple(float(v) for v in (prop(blk('sysDesc'), 'pos') or '0.030 0.280').split())
        count_pos = tuple(float(v) for v in (prop(blk('countNum'), 'pos') or '0.030 0.373').split())
        facts_pos = tuple(float(v) for v in (prop(blk('factsLine'), 'pos') or '0.030 0.451').split())
    panels.append(dict(
        sd=sd,
        badge=inner(blk('mfrBadge')),
        name=name,
        name_fs=None if sd in ('nes', 'snes') else name_fs,
        desc=inner(blk('sysDesc')),
        desc_pos=desc_pos,
        facts=inner(blk('factsLine')),
        count_pos=count_pos,
        facts_pos=facts_pos,
    ))

tiles = []
for p in panels:
    bg_path = f'{ROOT}/backgrounds/{p["sd"]}.webp'
    if not os.path.isfile(bg_path):
        bg_path = f'{ROOT}/backgrounds/_default.webp'
    img = Image.open(bg_path).convert('RGB').resize((W, H))
    d = ImageDraw.Draw(img)

    # mfrBadge: white chip
    bx, by = 0.030 * W, 0.195 * H
    bf = ImageFont.truetype(FBB, fs(0.018))
    bw = bf.getlength(p['badge'].upper()) + 0.020 * W
    bh = fs(0.018) * 1.9
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=round(0.007 * W), fill='white')
    d.text((bx + 0.010 * W, by + bh / 2), p['badge'].upper(),
           font=bf, fill='#0A2FA0', anchor='lm')

    # sysName
    if p['sd'] in ('nes', 'snes'):
        txt(d, 0.030, 0.226, p['name'][0], 0.040, 'white')
        txt(d, 0.030, 0.266, p['name'][1], 0.022, 'white')
    else:
        txt(d, 0.030, 0.230, p['name'], p['name_fs'], 'white')

    # sysDesc wrapped (ES-DE greedy, wrap width = size.x*W)
    df = ImageFont.truetype(FBB, fs(0.019))
    dx, dy = p['desc_pos']
    for i, ln in enumerate(wrap(p['desc'], df, 0.20 * W)):
        d.text((dx * W, (dy + i * 0.019 * 1.30) * H), ln, font=df, fill='white')

    # countNum + factsLine
    cx, cy = p['count_pos']
    txt(d, cx, cy, '128 GAMES', 0.055, 'white')
    fx, fy = p['facts_pos']
    txt(d, fx, fy, p['facts'], 0.017, '#FFD60A')

    # panel guide box (the baked panel region 0.013..0.28 / 0.17..0.97)
    d.rectangle([0.013 * W, 0.17 * H, 0.28 * W, 0.97 * H], outline=(255, 0, 0), width=2)

    tile = img.resize((W // 2, H // 2))
    td = ImageDraw.Draw(tile)
    td.text((10, 10), p['sd'], font=ImageFont.truetype(FBB, 22), fill='yellow')
    tiles.append(tile)

cols = 7
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new('RGB', (tiles[0].width * cols, tiles[0].height * rows), 'black')
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * t.width, (i // cols) * t.height))
sheet.save('/tmp/polish_sweep.png')
print('rendered', len(tiles), 'consoles -> /tmp/polish_sweep.png')
