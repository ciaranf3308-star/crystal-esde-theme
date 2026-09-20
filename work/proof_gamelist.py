#!/usr/bin/env python3
"""PIL proof of the Crystal physical-media gamelist view at 1280x960.

Renders the new views.xml gamelist geometry with stand-in scraped media:
  proof_full.png         - everything scraped (marquee, fanart, physical)
  proof_no_marquee.png   - marquee missing -> Nova-styled title fallback
  proof_no_fanart.png    - fanart/screenshot missing -> static canvas only
  proof_no_physical.png  - physical media missing -> silhouette fallbacks
"""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

W, H = 1280, 960
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "theme-src", "crystal")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proofs")
os.makedirs(OUT, exist_ok=True)

def font(sz, bold=True):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    return ImageFont.truetype(p, sz)

def nx(x): return int(x * W)
def ny(y): return int(y * H)

# ---------------------------------------------------------------- stand-in media
def make_fanart():
    """Colorful synthetic 'scraped fanart' collage."""
    im = Image.new("RGB", (W, H), (20, 90, 40))
    d = ImageDraw.Draw(im)
    d.ellipse([700, 100, 1200, 600], fill=(255, 200, 40))      # sun
    d.ellipse([150, 500, 700, 950], fill=(30, 140, 90))        # hills
    d.polygon([(0, 960), (0, 650), (400, 650), (640, 960)], fill=(60, 60, 160))
    d.ellipse([880, 620, 1120, 860], fill=(240, 240, 240))     # creature-ish blob
    d.ellipse([920, 660, 1000, 740], fill=(30, 30, 30))
    d.ellipse([1020, 660, 1100, 740], fill=(30, 30, 30))
    for i in range(30):                                        # confetti
        x, y = (i * 173) % W, (i * 211) % H
        d.rectangle([x, y, x + 26, y + 14], fill=(255, 90, 90) if i % 2 else (90, 200, 255))
    return im

def duotone_wash(bg, fanart, opacity=0.55, blue=(127, 178, 255)):
    """Grayscale + blue multiply + opacity blend over the background."""
    g = fanart.convert("L").convert("RGB")
    px = g.load()
    # multiply blend with blue tint
    tint = Image.new("RGB", g.size, blue)
    g = Image.blend(g, Image.new("RGB", g.size, (255, 255, 255)), 0.0)
    from PIL import ImageChops
    g = ImageChops.multiply(g, tint)
    g = g.resize((W, H))
    return Image.blend(bg, g, opacity)

def make_marquee():
    """Stand-in scraped marquee: logo-ish text treatment, transparent bg."""
    im = Image.new("RGBA", (640, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f1, f2 = font(96), font(72)
    d.text((320, 92), "Pok\u00e9mon", font=f1, anchor="mm", fill=(255, 255, 255, 255),
           stroke_width=4, stroke_fill=(10, 47, 160, 255))
    d.text((320, 188), "EMERALD", font=f2, anchor="mm", fill=(255, 214, 10, 255),
           stroke_width=3, stroke_fill=(10, 47, 160, 255))
    return im

def make_cart(label, body=(30, 80, 200), label_bg=(240, 240, 240)):
    """Stand-in scraped physical media: a GBA cart."""
    im = Image.new("RGBA", (340, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 20, 320, 280], radius=26, fill=body + (255,))
    for x in range(48, 300, 26):
        d.rectangle([x, 34, x + 12, 64], fill=(10, 47, 160, 255))
    d.rounded_rectangle([48, 92, 292, 240], radius=12, fill=label_bg + (255,))
    d.rounded_rectangle([48, 92, 292, 130], radius=12, fill=(10, 47, 160, 255))
    d.rectangle([48, 118, 292, 130], fill=(10, 47, 160, 255))
    d.text((170, 190), label, font=font(30), anchor="mm", fill=(10, 47, 160, 255))
    return im

# ---------------------------------------------------------------- text helpers
def wrapped(d, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            lines.append(cur); cur = w_
    lines.append(cur)
    return lines

def panel_text(d):
    X0, X1 = nx(0.032), nx(0.190)
    # system pill
    pill = font(int(0.019 * H))
    tw = d.textlength("GBA", font=pill)
    d.rounded_rectangle([X0, ny(0.200), X0 + tw + 26, ny(0.200) + 30], radius=12, fill="white")
    d.text((X0 + 13, ny(0.200) + 15), "GBA", font=pill, anchor="lm", fill=(10, 47, 160))
    # title
    y = ny(0.242)
    for line in wrapped(d, "Pok\u00e9mon Emerald", font(int(0.027 * H)), X1 - X0):
        d.text((X0, y), line, font=font(int(0.027 * H)), fill="white"); y += 32
    # desc
    y = ny(0.326); df = font(int(0.0145 * H), bold=False)
    for line in wrapped(d, "The Hoenn region awaits. Catch, train and battle across land and sea in the definitive third-generation Pok\u00e9mon adventure.", df, X1 - X0)[:5]:
        d.text((X0, y), line, font=df, fill=(191, 212, 255)); y += 19
    # rows
    rows = [("LAST PLAYED", "14 Sep 2026"), ("PLAY TIME", "26 hours"),
            ("PLAYERS", "1"), ("GENRE", "Role-playing"),
            ("RELEASE", "2004"), ("DEVELOPER", "Game Freak")]
    lf, vf = font(int(0.0125 * H)), font(int(0.014 * H))
    yy = 0.430
    for lab, val in rows:
        d.text((X0, ny(yy)), lab, font=lf, fill=(255, 214, 10))
        d.text((nx(0.104), ny(yy)), val, font=vf, fill="white")
        yy += 0.027
    # rating
    d.text((X0, ny(0.600)), "RATING", font=lf, fill=(255, 214, 10))
    fs = Image.open(os.path.join(ROOT, "art", "star_filled.png")).convert("RGBA").resize((26, 26))
    us = Image.open(os.path.join(ROOT, "art", "star_unfilled.png")).convert("RGBA").resize((26, 26))
    return fs, us

def draw_rating(base, d, fs, us):
    X0 = nx(0.104); y = ny(0.600)
    for i in range(5):
        if i < 4:
            base.paste(fs, (X0 + i * 28, y), fs)
        else:
            half = us.copy()
            half.paste(fs.crop((0, 0, 13, 26)), (0, 0), fs.crop((0, 0, 13, 26)))
            base.paste(half, (X0 + i * 28, y), half)
    cf = font(int(0.046 * H))
    d.text((nx(0.032), ny(0.646)), "37", font=cf, fill="white")
    d.text((nx(0.032), ny(0.700)), "GAMES", font=font(int(0.016 * H)), fill=(255, 214, 10))

# ---------------------------------------------------------------- compose
def compose(marquee=True, fanart=True, physical=True):
    bg = Image.open(os.path.join(ROOT, "backgrounds", "gba.webp")).convert("RGB").resize((W, H))
    im = bg
    if fanart:
        im = duotone_wash(bg, make_fanart())
    im = im.convert("RGBA")
    # stage
    stage = Image.open(os.path.join(ROOT, "art", "carousel_vignette.png")).convert("RGBA").resize((W, int(0.375 * H)))
    im.paste(stage, (0, ny(0.625)), stage)
    d = ImageDraw.Draw(im)

    # marquee slot: fallback title first (z20), then marquee art (z21)
    # (kept smaller than typical marquee art so any peek through transparent
    # wheels stays subtle; white keeps the no-marquee state confident)
    fb = font(int(0.034 * H))
    lines = wrapped(d, "Pok\u00e9mon Emerald", fb, nx(0.40))
    y0 = ny(0.22) - len(lines) * 20
    for line in lines:
        d.text((nx(0.52), y0), line, font=fb, anchor="ma", fill="white"); y0 += 40
    if marquee:
        mq = make_marquee()
        mq.thumbnail((nx(0.40), ny(0.24)), Image.LANCZOS)
        im.paste(mq, (nx(0.52) - mq.width // 2, ny(0.22) - mq.height // 2), mq)

    # hero cart (z25), rotated -8
    if physical:
        hero = make_cart("EMERALD")
    else:
        hero = Image.open(os.path.join(ROOT, "media_fallbacks", "gba.png")).convert("RGBA").resize((340, 340))
    hero.thumbnail((nx(0.30), ny(0.36)), Image.LANCZOS)
    hero = hero.rotate(-8, expand=True, resample=Image.BICUBIC)
    im.paste(hero, (nx(0.77) - hero.width // 2, ny(0.40) - hero.height // 2), hero)

    # carousel (z50): 7 items, selected = EMERALD (idx 2), 1.3x, neighbours dimmed/desat
    carts = [("RUBY", (200, 40, 40)), ("SAPPHIRE", (40, 90, 200)), ("EMERALD", (30, 150, 80)),
             ("FIRERED", (220, 80, 30)), ("LEAFGREEN", (60, 170, 60)),
             ("PINBALL", (120, 60, 180)), ("WARIO", (230, 200, 40))]
    cx = [0.5 + (i - 2) * 0.135 for i in range(7)]
    for i, (lab, col) in enumerate(carts):
        if physical:
            c = make_cart(lab, body=col)
        else:
            c = Image.open(os.path.join(ROOT, "media_fallbacks", "gba.png")).convert("RGBA")
        c.thumbnail((nx(0.13), ny(0.115)), Image.LANCZOS)
        if i == 2:
            c = c.resize((int(c.width * 1.3), int(c.height * 1.3)), Image.LANCZOS)
        else:
            # dim 0.5 + desaturate 0.7, alpha-aware
            alpha = c.split()[3]
            rgb = c.convert("RGB")
            g = rgb.convert("L").convert("RGB")
            rgb = Image.blend(rgb, g, 0.3)
            rgb = ImageEnhance.Brightness(rgb).enhance(0.5)
            c = rgb.convert("RGBA")
            c.putalpha(alpha)
        x, y = nx(cx[i]) - c.width // 2, ny(0.795) - c.height // 2
        im.paste(c, (x, y), c)

    # panel text (z10)
    fs, us = panel_text(d)
    draw_rating(im, d, fs, us)

    # baked footer on gba (live helpsystem hidden) - nothing to draw
    return im.convert("RGB")

# fix: panel_text references base_img wrongly; simplify by inlining rating paste there.
# (panel_text returns the star images; draw_rating pastes them.)
for name, kw in [("proof_full", {}),
                 ("proof_no_marquee", {"marquee": False}),
                 ("proof_no_fanart", {"fanart": False}),
                 ("proof_no_physical", {"physical": False})]:
    compose(**kw).save(os.path.join(OUT, name + ".png"))
    print("wrote", name)
