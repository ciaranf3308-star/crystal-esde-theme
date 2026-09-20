#!/usr/bin/env python3
"""v5.5.0 proof mock: straight bottom-flush disk row per the napkin.
1280x960. Selected disk 0.468h (449px), neighbours 0.223h (214px),
bottoms flush at 0.81h (778px), equal 0.40w spacing, centres 0.10/0.50/0.90.
Yellow glow behind selected. Console name below row. NOT an ES-DE render."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 960
img = Image.new("RGB", (W, H), (16, 42, 148))
px = img.load()
# subtle vertical gradient
for y in range(H):
    t = y / H
    r, g, b = int(16+20*t), int(42+30*t), int(148+40*t)
    for x in range(0, W, 8):
        for dx in range(8):
            if x+dx < W: px[x+dx, y] = (r, g, b)
d = ImageDraw.Draw(img, "RGBA")

# marquee zone (top-left, tilted, blue/white)
d.rectangle([60, 60, 420, 220], fill=(185, 201, 255, 255), outline=(255,255,255), width=3)
d.text((90, 120), "MARQUEE", fill=(10, 30, 120))
# metadata zone (top-right)
d.rectangle([810, 50, 1220, 330], fill=(255, 255, 255, 220))
d.text((830, 70), "Game metadata", fill=(20, 20, 60))

BASE = int(0.81 * H)          # 778 flush baseline
SEL_D = int(0.468 * H)        # 449
NB_D = int(0.223 * H)         # 214
SP = int(0.40 * W)            # 512

def disk(cx, bottom, dia, fill, outline, width=4, label=""):
    x0, x1 = cx - dia//2, cx + dia//2
    y0, y1 = bottom - dia, bottom
    d.ellipse([x0, y0, x1, y1], fill=fill, outline=outline, width=width)
    if label: d.text((cx-40, bottom-dia//2-10), label, fill=(10,10,40))

# glow behind selected
gcx, gcy = W//2, BASE - SEL_D//2
gr = 258
d.ellipse([gcx-gr, gcy-gr, gcx+gr, gcy+gr], fill=(255, 210, 40, 90))

# neighbours + selected, bottoms flush
disk(W//2 - SP, BASE, NB_D, (225, 232, 255), (255,255,255), 3, "prev")
disk(W//2 + SP, BASE, NB_D, (225, 232, 255), (255,255,255), 3, "next")
disk(W//2, BASE, SEL_D, (235, 240, 255), (255, 210, 60), 6, "SELECTED")
# edge partials (off-screen neighbours mid-scroll-in)
disk(W//2 - 2*SP, BASE, NB_D, (225, 232, 255), (255,255,255), 3)
disk(W//2 + 2*SP, BASE, NB_D, (225, 232, 255), (255,255,255), 3)

# baseline guide (thin, to show flush)
d.line([40, BASE, W-40, BASE], fill=(255, 210, 60, 160), width=2)
d.text((46, BASE+8), "bottoms flush @ 0.81h", fill=(255, 220, 90))

# console name below row
d.text((W//2-110, int(0.865*H)-12), "CONSOLE NAME", fill=(255,255,255))
# footer
d.text((60, int(0.955*H)-12), "A SELECT   B BACK   Y OPTIONS", fill=(255,255,255))

img.save("/home/hatch/workspace/crystal-esde-theme/work/proofs/proof_v55_gamelist.png")
print("wrote proof_v55_gamelist.png")
