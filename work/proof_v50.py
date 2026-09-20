#!/usr/bin/env python3
"""Proof mock for Crystal v5.0.0 napkin-sketch gamelist skeleton (1280x960).

Not a real ES-DE render — geometry proof only: marquee top-left with
blue/white wash, metadata top-right, disk carousel with yellow glow on
the selected slot, console name bottom-center.
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1280, 960
ART = os.path.expanduser('~/workspace/crystal-esde-theme/theme-src/crystal/art')

def f(size, bold=False):
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else ''), size)
    except Exception:
        return ImageFont.load_default()

img = Image.open(f'{ART}/gamelist_generic_bg.png').convert('RGBA')
# royal-blue wash (lib_blue_tint)
tint = Image.open(f'{ART}/lib_blue_tint.png').convert('RGBA').resize((W, H))
img = Image.alpha_composite(img, tint)
d = ImageDraw.Draw(img)
INK = (58, 74, 115, 255); DEEP = (10, 47, 160, 255)

# --- marquee slot top-left (0.055,0.055 0.30x0.15) with fake scraped logo + wash
mx, my, mw, mh = int(0.055*W), int(0.055*H), int(0.30*W), int(0.15*H)
d.rounded_rectangle([mx, my, mx+mw, my+mh], 10, fill=(255,255,255,235), outline=(10,47,160,90), width=2)
d.text((mx+18, my+mh//2-24), 'GAME LOGO', font=f(34, True), fill=DEEP)
d.text((mx+18, my+mh//2+16), 'scraped marquee', font=f(18), fill=INK)
wash = Image.open(f'{ART}/marquee_wash.png').convert('RGBA').resize((mw, mh))
img = Image.alpha_composite(img, Image.new('RGBA', img.size, (0,0,0,0)))
tmp = img.crop((mx, my, mx+mw, my+mh))
tmp = Image.alpha_composite(tmp, wash)
img.paste(tmp, (mx, my))
d = ImageDraw.Draw(img)
d.text((mx, my+mh+6), 'marquee + blue/white filter', font=f(14), fill=INK)

# --- metadata block top-right
bx = int(0.655*W)
d.text((bx, int(0.055*H)), 'A brave hero sets out across a vast\nblue region to become champion.\nScraped description lines live here.', font=f(17), fill=INK)
d.text((bx, int(0.203*H)-12), 'RPG  •  2002', font=f(19), fill=INK)
d.text((bx, int(0.231*H)-12), 'Game Freak  •  1 player', font=f(19), fill=INK)
for i in range(5):
    sx = bx + i*30
    d.text((sx, int(0.264*H)-14), '★' if i < 4 else '☆', font=f(26), fill=(255,190,10,255) if i < 4 else (160,170,200,255))

# --- yellow glow behind selected slot (0.5,0.60 0.46)
glow = Image.open(f'{ART}/lib_glow_yellow.png').convert('RGBA')
gs = int(0.46*W)
glow = glow.resize((gs, gs))
img = Image.alpha_composite(img, Image.new('RGBA', img.size, (0,0,0,0)))
layer = Image.new('RGBA', img.size, (0,0,0,0))
layer.alpha_composite(glow, (int(0.5*W-gs/2), int(0.60*H-gs/2)))
img = Image.alpha_composite(img, layer)
d = ImageDraw.Draw(img)

# --- disk carousel: 5 disks, selected 2.0x center
def disk(cx, cy, r, label, selected=False):
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(230,238,255,255), outline=(10,47,160,255) if selected else (120,140,190,255), width=4 if selected else 2)
    d.ellipse([cx-r*0.55, cy-r*0.55, cx+r*0.55, cy+r*0.55], outline=(10,47,160,120), width=2)
    d.ellipse([cx-r*0.16, cy-r*0.16, cx+r*0.16, cy+r*0.16], fill=(255,255,255,255), outline=(10,47,160,160), width=2)
    d.text((cx-28, cy-12), label, font=f(20, True), fill=DEEP)

cy = int(0.60*H)
r_sel = int(0.165*W*2.0/2)   # 211
r_nb = int(0.165*W/2)        # 106
disk(int(0.02*W), cy, r_nb, 'prev-2')
disk(int(0.185*W), cy, r_nb, 'prev')
disk(int(0.5*W), cy, r_sel, 'SELECTED', True)
disk(int(0.815*W), cy, r_nb, 'next')
disk(int(0.98*W), cy, r_nb, 'next+2')

# --- console name bottom-center
d.text((W//2, int(0.925*H)), 'Nintendo 64', font=f(33, True), fill=DEEP, anchor='mm')
# --- footer
d.text((60, int(0.955*H)), 'A SELECT   B BACK   Y OPTIONS', font=f(18, True), fill=DEEP, anchor='lm')

out = os.path.expanduser('~/workspace/crystal-esde-theme/work/proofs/proof_v50_skeleton.png')
img.convert('RGB').save(out)
print('wrote', out, img.size)
