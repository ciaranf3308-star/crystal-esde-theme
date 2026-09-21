#!/usr/bin/env python3
"""VM-ONLY visual proof assets for the v18.0.0 review harness.

Abstract, neutral, deliberately unlabeled proxies so the SHELL is what
gets judged — NOT fake game labels, NOT illustrated fallback art.
These live ONLY in work/proof_assets/ and must NEVER ship in the
production ZIP (build.sh zips theme-src/ only; the final QA pass
verifies the exclusion).

Set:
  marquee_wide.png   800x250  wide abstract wordmark bars (navy on transparent)
  marquee_square.png 420x420  squarish abstract emblem
  marquee_tall.png   280x560  narrow/tall abstract stack
  screenshot_a.png   792x340  warm dusk landscape (racing-ish)
  screenshot_b.png   792x340  blue sky + green hills (platformer-ish)
  screenshot_c.png   792x340  teal night + stars (3DS-ish)
  disc_hero.png      640x640  dark disc, hub ring, highlight
  cart_hero.png      520x560  dark grey cartridge silhouette, grip notch
  card_hero.png      360x420  small game card
  *_prev.png / *_next.png     0.55-scale dimmer silhouettes
"""
import os, math
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.expanduser("~/workspace/crystal-esde-theme"),
                   "work/proof_assets")
os.makedirs(OUT, exist_ok=True)

NAVY = (10, 47, 160)
GREY = (70, 74, 82)

def save(im, name):
    im.save(os.path.join(OUT, name))
    print("wrote", name, im.size)

# ------------------------- marquee proxies ------------------------------
def marquee_wide():
    im = Image.new("RGBA", (800, 250), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # bold abstract wordmark: chunky bars of decreasing width, navy
    widths = [560, 470, 620, 380]
    y = 30
    for w in widths:
        d.rounded_rectangle([ (800 - w) / 2, y, (800 + w) / 2, y + 46 ],
                            radius=23, fill=NAVY + (255,))
        y += 54
    # one accent dot
    d.ellipse([700 - 20, 190 - 20, 700 + 20, 190 + 20], fill=NAVY + (255,))
    save(im, "marquee_wide.png")

def marquee_square():
    im = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([40, 40, 380, 380], fill=NAVY + (255,))
    d.ellipse([110, 110, 310, 310], fill=(255, 255, 255, 255))
    d.polygon([(210, 140), (290, 280), (130, 280)], fill=NAVY + (255,))
    d.rounded_rectangle([120, 330, 300, 372], radius=21, fill=NAVY + (255,))
    save(im, "marquee_square.png")

def marquee_tall():
    im = Image.new("RGBA", (280, 560), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([40, 20, 240, 220], fill=NAVY + (255,))
    d.ellipse([100, 80, 180, 160], fill=(255, 255, 255, 255))
    y = 260
    for w in (200, 160, 180, 120):
        d.rounded_rectangle([(280 - w) / 2, y, (280 + w) / 2, y + 34],
                            radius=17, fill=NAVY + (255,))
        y += 52
    save(im, "marquee_tall.png")

# ------------------------- screenshot proxies ---------------------------
def _soft_edge(im, r=3):
    return im.filter(ImageFilter.GaussianBlur(r))

def screenshot_a():  # warm dusk landscape
    w2, h2 = 792, 340
    base = Image.new("RGB", (w2, h2))
    px = base.load()
    for y in range(h2):
        t = y / h2
        # sky: amber -> rose -> slate
        r = int(244 - t * 150); g = int(150 - t * 60); b = int(110 - t * 30)
        for x in range(w2):
            px[x, y] = (max(r, 0), max(g, 0), max(b, 0))
    d = ImageDraw.Draw(base)
    # sun
    d.ellipse([330, 90, 462, 222], fill=(255, 236, 190))
    # far ridge
    d.polygon([(0, 250)] + [(x, 250 - 60 * abs(math.sin(x / 90))) for x in range(0, w2 + 1, 20)] + [(w2, 340), (0, 340)],
              fill=(74, 58, 78))
    # near ground
    d.polygon([(0, 300)] + [(x, 300 - 25 * abs(math.sin(x / 60 + 1))) for x in range(0, w2 + 1, 20)] + [(w2, 340), (0, 340)],
              fill=(38, 34, 44))
    # road sweep
    d.polygon([(330, 340), (430, 340), (400, 268), (370, 268)], fill=(120, 112, 128))
    save(_soft_edge(base.convert("RGBA"), 2), "screenshot_a.png")

def screenshot_b():  # blue sky, green hills
    w2, h2 = 792, 340
    base = Image.new("RGB", (w2, h2))
    px = base.load()
    for y in range(h2):
        t = y / h2
        px2 = (int(112 + t * 40), int(168 + t * 30), int(232 + t * 10))
        for x in range(w2):
            px[x, y] = px2
    d = ImageDraw.Draw(base)
    for cx, cy, cw in ((150, 80, 90), (420, 60, 130), (650, 95, 80)):
        d.ellipse([cx - cw / 2, cy - 20, cx + cw / 2, cy + 20], fill=(255, 255, 255))
    d.polygon([(0, 220)] + [(x, 220 - 70 * abs(math.sin(x / 120))) for x in range(0, w2 + 1, 20)] + [(w2, 340), (0, 340)],
              fill=(74, 140, 84))
    d.polygon([(0, 280)] + [(x, 280 - 35 * abs(math.sin(x / 80 + 2))) for x in range(0, w2 + 1, 20)] + [(w2, 340), (0, 340)],
              fill=(52, 112, 66))
    # path
    d.polygon([(360, 340), (440, 340), (410, 250), (390, 250)], fill=(214, 196, 160))
    save(_soft_edge(base.convert("RGBA"), 2), "screenshot_b.png")

def screenshot_c():  # teal night + stars
    w2, h2 = 792, 340
    base = Image.new("RGB", (w2, h2))
    px = base.load()
    for y in range(h2):
        t = y / h2
        for x in range(w2):
            px[x, y] = (int(16 + t * 30), int(60 + t * 50), int(96 + t * 60))
    d = ImageDraw.Draw(base)
    import random
    random.seed(7)
    for _ in range(90):
        x, y = random.randrange(w2), random.randrange(h2)
        d.point((x, y), fill=(255, 255, 255))
    d.ellipse([600, 40, 700, 140], fill=(232, 244, 240))
    d.polygon([(0, 290)] + [(x, 290 - 40 * abs(math.sin(x / 100))) for x in range(0, w2 + 1, 20)] + [(w2, 340), (0, 340)],
              fill=(12, 42, 50))
    save(_soft_edge(base.convert("RGBA"), 2), "screenshot_c.png")

# ------------------------- physical-media proxies -----------------------
def _shadow(im):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 110), mask=im.split()[3])
    return sh.filter(ImageFilter.GaussianBlur(14))

def disc_hero():
    s = 640
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s // 2
    d.ellipse([10, 10, s - 10, s - 10], fill=(46, 52, 62, 255))
    # brushed-metal radial bands
    for r in range(60, 300, 14):
        d.ellipse([c - r, c - r, c + r, c + r], outline=(120, 130, 148, 70), width=6)
    d.ellipse([c - 70, c - 70, c + 70, c + 70], fill=(200, 206, 216, 255))
    d.ellipse([c - 30, c - 30, c + 30, c + 30], fill=(0, 0, 0, 0))
    d.ellipse([c - 30, c - 30, c + 30, c + 30], outline=(230, 236, 244, 255), width=6)
    # highlight arc
    d.arc([60, 60, s - 60, s - 60], start=200, end=300, fill=(255, 255, 255, 90), width=26)
    save(im, "disc_hero.png")

def cart_hero():
    w2, h2 = 520, 560
    im = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 10, w2 - 10, h2 - 10], radius=28, fill=GREY + (255,))
    # grip notches at top
    d.rounded_rectangle([60, -30, 200, 90], radius=20, fill=(0, 0, 0, 0))
    d.rounded_rectangle([320, -30, 460, 90], radius=20, fill=(0, 0, 0, 0))
    # label panel (abstract)
    d.rounded_rectangle([60, 150, w2 - 60, h2 - 70], radius=16, fill=(120, 128, 140, 255))
    d.rounded_rectangle([90, 190, w2 - 90, 250], radius=14, fill=(46, 52, 62, 255))
    for y in range(300, h2 - 100, 26):
        d.line([90, y, w2 - 90, y], fill=(150, 158, 172, 255), width=8)
    save(im, "cart_hero.png")

def card_hero():
    w2, h2 = 360, 420
    im = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 8, w2 - 8, h2 - 8], radius=18, fill=(88, 94, 104, 255))
    d.rounded_rectangle([30, 30, w2 - 30, 150], radius=10, fill=(140, 148, 162, 255))
    d.rounded_rectangle([30, 175, w2 - 30, 210], radius=10, fill=(52, 58, 70, 255))
    for y in range(240, h2 - 40, 24):
        d.line([30, y, w2 - 30, y], fill=(150, 158, 172, 255), width=7)
    save(im, "card_hero.png")

def small_versions():
    import math as _m
    for name, base in (("disc_hero", "disc"), ("cart_hero", "cart"), ("card_hero", "card")):
        im = Image.open(os.path.join(OUT, f"{base if base != 'card' else 'card'}_hero.png"))
        sc = 0.55
        im2 = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
        # dim slightly for prev/next quietness
        px = im2.load()
        for y in range(im2.height):
            for x in range(im2.width):
                r, g, b, a = px[x, y]
                px[x, y] = (int(r * 0.82), int(g * 0.82), int(b * 0.82), a)
        save(im2, f"{base}_prev.png")
        save(im2.copy(), f"{base}_next.png")

if __name__ == "__main__":
    marquee_wide(); marquee_square(); marquee_tall()
    screenshot_a(); screenshot_b(); screenshot_c()
    disc_hero(); cart_hero(); card_hero(); small_versions()
    print("done:", len(os.listdir(OUT)), "assets")
