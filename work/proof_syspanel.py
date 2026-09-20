#!/usr/bin/env python3
"""Proof: render all 21 system-view panels from the REAL theme XML with
ES-DE-style greedy word wrap. Fail loudly on any vertical overlap."""
import re, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.expanduser('~/workspace/crystal-esde-theme/theme-src/crystal')
W, H = 1280, 960
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def elem_block(src, name):
    m = re.search(r'        <text name="%s">.*?\n        </text>\n' % name, src, re.DOTALL)
    return m.group(0) if m else None

def prop(block, tag):
    m = re.search(r'<%s>(.*?)</%s>' % (tag, tag), block or '', re.DOTALL)
    return m.group(1).strip() if m else None

def inner_text(block):
    # last <text>..</text> that is NOT the element tag itself: the content text
    ms = re.findall(r'<text>(.*?)</text>', block or '', re.DOTALL)
    return ms[-1].strip() if ms else ''

base = open(f'{ROOT}/views.xml').read()
base_view = base[base.index('<view name="system">'):base.index('</view>')]

def base_pos(name):
    return prop(elem_block(base_view, name), 'pos')

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

fails = []
tiles = []
for sysdir in sorted(os.listdir(ROOT)):
    tp = os.path.join(ROOT, sysdir, 'theme.xml')
    if not os.path.isfile(tp):
        continue
    src = open(tp).read()
    sv = src[src.index('<view name="system">'):src.index('</view>')]

    # name: per-system static text (or nes/snes two-line)
    nb = elem_block(sv, 'sysName')
    name_txt, name_fs = inner_text(nb), 0.040
    if name_txt:
        name_fs = float(prop(nb, 'fontSize') or 0.040)
    else:
        n1 = inner_text(elem_block(sv, 'sysName1'))
        n2 = inner_text(elem_block(sv, 'sysName2'))
        name_txt = (n1 + ' ' + n2).strip()

    db = elem_block(sv, 'sysDesc')
    desc_txt = inner_text(db)
    desc_pos = prop(db, 'pos') or base_pos('sysDesc')
    cb = elem_block(sv, 'countNum')
    count_pos = (prop(cb, 'pos') if cb else None) or base_pos('countNum')
    fb = elem_block(sv, 'factsLine')
    facts_txt = inner_text(fb)
    facts_pos = (prop(fb, 'pos') if fb else None) or base_pos('factsLine')

    img = Image.new('RGB', (W // 3, 300), (10, 47, 160))
    d = ImageDraw.Draw(img)
    sx = W / 3 / W  # scale: tile is 1/3 width; draw at 1/3 scale
    sc = 1 / 3

    def draw_text(xf, yf, s, fsf, fill):
        d.text((xf * W * sc, yf * H * sc), s,
               font=ImageFont.truetype(FB, max(6, round(fsf * H * sc))), fill=fill)

    # name (single line, may be two-part for nes/snes)
    ny = 0.230 if sysdir not in ('nes', 'snes') else 0.226
    draw_text(0.030, ny, name_txt, name_fs if sysdir not in ('nes', 'snes') else 0.040, 'white')

    # desc wrapped
    dx, dy = [float(v) for v in desc_pos.split()]
    fs = 0.019
    font = ImageFont.truetype(FB, round(fs * H))
    lines = wrap(desc_txt, font, 0.20 * W)
    lh = fs * 1.28
    for i, ln in enumerate(lines):
        draw_text(dx, dy + i * lh, ln, fs, 'white')
    desc_bottom = dy + len(lines) * lh

    # count + facts
    cx, cy = [float(v) for v in count_pos.split()]
    draw_text(cx, cy, '0 GAMES', 0.055, 'white')
    count_bottom = cy + 0.055 * 1.2
    fx, fy = [float(v) for v in facts_pos.split()]
    draw_text(fx, fy, facts_txt, 0.017, (255, 210, 60))

    if not (desc_bottom + 0.008 <= cy):
        fails.append(f'{sysdir}: desc bottom {desc_bottom:.3f} vs countNum {cy:.3f}')
    if not (count_bottom <= fy):
        fails.append(f'{sysdir}: count bottom {count_bottom:.3f} vs facts {fy:.3f} ({len(lines)} desc lines)')

    d.text((8, 8), sysdir, font=ImageFont.truetype(FB, 14), fill=(255, 255, 0))
    tiles.append(img)

cols = 7
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new('RGB', (tiles[0].width * cols, tiles[0].height * rows), 'black')
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * t.width, (i // cols) * t.height))
sheet.save('/tmp/proof_syspanel_all.png')
print('tiles:', len(tiles))
print('FAILURES:' if fails else 'NO OVERLAPS — all 21 panels clear')
for f in fails:
    print(' ', f)
