#!/usr/bin/env python3
"""v4.2.0: Nova game-library view — Emerald on GBA.

Builds:
  --background : theme-src/crystal/art/gamelist_library.webp
                 Purpose-built 1280x960 library canvas. Royal-blue gradient,
                 Hoenn-evocative duotone seascape (abstract islands, dotted
                 routes, wave motifs), halftone, blueprint grid, faint GBA
                 technical diagrams (never competing), and the baked left
                 metadata slab chrome (empty system pill, hairline dividers).
                 This is NOT the GBA system hero: no giant system title, no
                 giant hardware render. The selected game owns the screen;
                 per-game fanart arrives via the dynamic fanart slot.
  --fade       : theme-src/crystal/art/gamelist_fade.png
                 Bottom-up blue gradient (transparent -> deep blue) with
                 halftone dots. Replaces the old solid carousel bar: the
                 carousel sits over a soft fade, integrated, never a footer.
  --mock       : /tmp/library_mock.png — full 1280x960 proof with live text,
                 marquee, cartridge hero and the 6-cart carousel.

Deterministic: fixed geometry, no randomness, no timestamps.
"""
import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(REPO, "theme-src", "crystal", "art")
W, H = 1280, 960
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

ROYAL = (18, 56, 184)       # royal blue
DEEP = (10, 36, 112)        # deep navy
DEEPER = (7, 24, 78)
INK = (6, 18, 60)
WHITE = (255, 255, 255)
DIM = (150, 170, 225)       # dim label blue-white
YELLOW = (255, 214, 10)
PANEL = (9, 30, 96)

# left slab chrome (shared by background painter and text layout)
PANEL_X0, PANEL_X1 = 24, 352
PANEL_Y0, PANEL_Y1 = 24, 936
PAD = 48  # text left edge inside panel


def vgrad(size, stops):
    """Vertical gradient. stops: [(0.0, rgb), (1.0, rgb), ...]."""
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                f = (t - t0) / max(1e-6, t1 - t0)
                px_y = tuple(int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3))
                break
        for x in range(w):
            px[x, y] = px_y
    return img


def halftone(base, x0, y0, x1, y1, spacing=14, rmax=3.2, color=(255, 255, 255),
             alpha=26, direction=1):
    """Dot field fading along x (direction=1: grows right, -1: grows left)."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(y0, y1, spacing):
        for x in range(x0, x1, spacing):
            fx = (x - x0) / max(1, x1 - x0)
            f = fx if direction == 1 else 1 - fx
            r = rmax * (0.25 + 0.75 * f)
            a = int(alpha * (0.3 + 0.7 * f))
            d.ellipse([x - r, y - r, x + r, y + r], fill=color + (a,))
    base.alpha_composite(layer)


def blueprint_grid(base, spacing=48, alpha=10):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in range(0, W + 1, spacing):
        d.line([x, 0, x, H], fill=(255, 255, 255, alpha), width=1)
    for y in range(0, H + 1, spacing):
        d.line([0, y, W, y], fill=(255, 255, 255, alpha), width=1)
    base.alpha_composite(layer)


def wave_arcs(d, cx, cy, n=3, gap=16, color=(255, 255, 255), alpha=40, width=100):
    for i in range(n):
        y = cy + i * gap
        a = int(alpha * (1 - i / (n + 0.5)))
        d.arc([cx - width // 2, y - 14, cx + width // 2, y + 14],
              start=200, end=340, fill=color + (a,), width=2)


def island(d, cx, cy, rx, ry, rot=0, color=(56, 104, 235), alpha=80):
    """Abstract island blob with white coastline + depth contour rings."""
    for ring, (rrx, rry, ra) in enumerate(
            ((1.0, 1.0, alpha), (1.28, 1.28, 34), (1.56, 1.56, 20))):
        pts = []
        for i in range(28):
            a = 2 * math.pi * i / 28
            wob = 1 + 0.22 * math.sin(3 * a + rot) + 0.10 * math.cos(5 * a - rot)
            x = cx + rx * rrx * wob * math.cos(a)
            y = cy + ry * rry * wob * math.sin(a)
            pts.append((x, y))
        if ring == 0:
            d.polygon(pts, fill=color + (alpha,))
            d.line(pts + [pts[0]], fill=(255, 255, 255, 80), width=2, joint="curve")
        else:
            d.line(pts + [pts[0]], fill=(255, 255, 255, ra), width=1, joint="curve")


def dotted_route(d, pts, color=(255, 255, 255), alpha=110, step=14, r=2.6):
    """Dotted path through points (catmull-ish: simple polyline walk)."""
    # resample polyline
    samples = []
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        dist = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(dist / step))
        for k in range(n):
            f = k / n
            samples.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
    samples.append(pts[-1])
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(layer)
    for x, y in samples:
        dd.ellipse([x - r, y - r, x + r, y + r], fill=color + (alpha,))
    d.bitmap((0, 0), layer)


def faint_gba_diagrams(img):
    """Supporting texture only: small technical line-art, ~10% opacity."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    A = 30
    f_small = ImageFont.truetype(FR, 13)

    # D-pad diagram, upper right
    cx, cy, s = 1150, 150, 26
    d.line([cx - s, cy - s // 3, cx + s, cy - s // 3], fill=(255, 255, 255, A), width=2)
    d.line([cx - s, cy + s // 3, cx + s, cy + s // 3], fill=(255, 255, 255, A), width=2)
    d.line([cx - s // 3, cy - s, cx - s // 3, cy + s], fill=(255, 255, 255, A), width=2)
    d.line([cx + s // 3, cy - s, cx + s // 3, cy + s], fill=(255, 255, 255, A), width=2)
    d.text((cx - 24, cy + s + 8), "D-PAD", font=f_small, fill=(255, 255, 255, A))

    # A/B button diagram, right edge
    for i, lab in enumerate(("B", "A")):
        bx, by = 1170 + i * 52, 300
        d.ellipse([bx - 18, by - 18, bx + 18, by + 18],
                  outline=(255, 255, 255, A), width=2)
        d.text((bx - 6, by - 10), lab, font=ImageFont.truetype(FB, 16),
               fill=(255, 255, 255, A))
    d.text((1150, 330), "ACTION", font=f_small, fill=(255, 255, 255, A))

    # cartridge schematic, parked in the quiet mid zone (faint texture)
    kx0, ky0, kx1, ky1 = 560, 545, 650, 655
    d.rounded_rectangle([kx0, ky0, kx1, ky1], radius=8,
                        outline=(255, 255, 255, A), width=2)
    d.line([kx0, ky1 + 14, kx1, ky1 + 14], fill=(255, 255, 255, A), width=1)
    d.line([kx0, ky1 + 9, kx0, ky1 + 19], fill=(255, 255, 255, A), width=1)
    d.line([kx1, ky1 + 9, kx1, ky1 + 19], fill=(255, 255, 255, A), width=1)
    d.text((kx0 - 8, ky1 + 22), "AGB-002", font=f_small, fill=(255, 255, 255, A))

    # tiny spec labels
    d.text((kx0 - 8, ky1 + 44), "240 x 160 TFT", font=f_small,
           fill=(255, 255, 255, A))
    d.text((kx0 - 8, ky1 + 64), "32-BIT HANDHELD", font=f_small,
           fill=(255, 255, 255, A))
    img.alpha_composite(layer)


def paint_background():
    img = vgrad((W, H), [(0.0, (24, 68, 200)), (0.45, ROYAL),
                         (0.75, DEEP), (1.0, DEEPER)]).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")

    # Hoenn-evocative seascape, right 2/3, duotone restrained
    island(d, 830, 300, 200, 120, rot=0.6)
    island(d, 1120, 480, 110, 80, rot=2.1)
    island(d, 620, 470, 90, 64, rot=4.0)
    dotted_route(d, [(700, 250), (830, 300), (950, 380), (1120, 480)])
    dotted_route(d, [(620, 470), (720, 420), (830, 300)])
    d.ellipse([826, 296, 834, 304], fill=(255, 214, 10, 200))  # route node tick
    d.ellipse([1116, 476, 1124, 484], fill=(255, 214, 10, 200))
    wave_arcs(d, 520, 700, n=3, color=(255, 255, 255), alpha=34)
    wave_arcs(d, 1000, 700, n=3, color=(255, 255, 255), alpha=34)
    wave_arcs(d, 760, 820, n=4, color=(255, 255, 255), alpha=26)

    blueprint_grid(img)
    halftone(img, 980, 40, 1260, 260, direction=1, alpha=30)
    halftone(img, 380, 640, 700, 920, direction=-1, alpha=22)
    faint_gba_diagrams(img)

    # soft edge darkening (keeps focus center, no muddy overlay)
    edge = Image.new("RGBA", (W, H), (4, 10, 40, 0))
    ed = ImageDraw.Draw(edge)
    for i, a in enumerate((26, 18, 12, 8, 5)):
        wdt = 26 - i * 5
        ed.rectangle([i * wdt, i * wdt, W - i * wdt, H - i * wdt],
                     outline=(4, 10, 40, a), width=wdt)
    img.alpha_composite(edge)

    paint_panel_chrome(img)
    return img


def paint_panel_chrome(img):
    """Baked left metadata slab: shape, empty system pill, hairline dividers."""
    d = ImageDraw.Draw(img, "RGBA")
    # slab with chamfered top-right corner (comic-panel cut)
    x0, y0, x1, y1 = PANEL_X0, PANEL_Y0, PANEL_X1, PANEL_Y1
    cut = 26
    pts = [(x0, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1), (x0, y1)]
    d.polygon(pts, fill=PANEL + (228,))
    d.line(pts + [pts[0]], fill=(255, 255, 255, 64), width=2, joint="curve")
    # top inner highlight
    d.line([(x0 + 10, y0 + 8), (x1 - cut - 6, y0 + 8)],
           fill=(255, 255, 255, 40), width=2)

    # empty system pill (live ${system.name} text goes on top)
    px0, py0, px1, py1 = PAD, 52, PAD + 100, 88
    d.rounded_rectangle([px0, py0, px1, py1], radius=18, fill=(255, 255, 255, 255))
    d.rounded_rectangle([px0, py0, px1, py1], radius=18,
                        outline=(10, 36, 112, 90), width=2)

    # hairline dividers bracketing the metadata group (no repetitive rules)
    for yy in (300, 610, 700):
        d.line([(PAD, yy), (x1 - 24, yy)], fill=(255, 255, 255, 30), width=1)

    # yellow tick under the title zone + panel bottom tag
    d.rectangle([PAD, 188, PAD + 48, 194], fill=YELLOW + (255,))
    f_tag = ImageFont.truetype(FR, 10)
    d.text((PAD, 900), "CRYSTAL \u00b7 NOVA", font=f_tag,
           fill=(120, 140, 200, 255))

# --------------------------------------------------------------------------
# GBA cartridge renderer — must read as REAL physical media, never an icon.
# Shape notes from the real object: the shell is wider than tall-ish
# (about 1 : 1.16), the top quarter carries horizontal grip ridges, the
# label sits in a recessed well covering the middle, and the bottom edge
# has the connector notch. Translucent colored plastic on the Pokemon
# carts: render as saturated body + lighter inner well + gloss stripe.
# --------------------------------------------------------------------------

def _shade(rgb, f):
    return tuple(max(0, min(255, int(c * f))) for c in rgb)


def draw_gba_cart(w, body, accent, title, subtitle, detail=True):
    """Render a front-facing GBA cartridge, RGBA. Returns (image, label_box)."""
    h = int(w * 1.16)
    pad = int(w * 0.35)
    img = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, y0 = pad, pad
    x1, y1 = pad + w, pad + h
    cx = pad + w / 2
    r = int(w * 0.10)

    # soft drop shadow
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rounded_rectangle([x0 + 6, y0 + 14, x1 + 6, y1 + 14], radius=r,
                         fill=(4, 8, 30, 110))
    img = Image.alpha_composite(img, sh.filter(
        __import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(10)))
    d = ImageDraw.Draw(img)

    # shell
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=body + (255,))
    # top grip-ridge band (the cart's signature)
    rh = int(h * 0.085)
    ry0 = y0 + int(h * 0.028)
    d.rounded_rectangle([x0 + int(w * 0.07), ry0,
                         x1 - int(w * 0.07), ry0 + rh],
                        radius=int(w * 0.035), fill=_shade(body, 0.82) + (255,))
    if detail:
        for i in range(4):
            rx = x0 + w * (0.24 + i * 0.17)
            d.line([rx, ry0 + rh * 0.22, rx, ry0 + rh * 0.78],
                   fill=(255, 255, 255, 80), width=max(2, int(w * 0.018)))
    # recessed label well (lighter = translucent plastic depth)
    wx0, wy0 = x0 + int(w * 0.055), y0 + int(h * 0.155)
    wx1, wy1 = x1 - int(w * 0.055), y1 - int(h * 0.055)
    d.rounded_rectangle([wx0, wy0, wx1, wy1], radius=int(w * 0.055),
                        fill=_shade(body, 1.14) + (255,))
    d.rounded_rectangle([wx0, wy0, wx1, wy1], radius=int(w * 0.055),
                        outline=_shade(body, 0.72) + (255,), width=max(2, int(w * 0.02)))

    # label
    lx0, ly0 = wx0 + int(w * 0.045), wy0 + int(h * 0.035)
    lx1, ly1 = wx1 - int(w * 0.045), wy1 - int(h * 0.045)
    d.rounded_rectangle([lx0, ly0, lx1, ly1], radius=int(w * 0.04),
                        fill=(246, 246, 242, 255))
    # label top banner
    bh = int((ly1 - ly0) * 0.15)
    d.rounded_rectangle([lx0, ly0, lx1, ly0 + bh], radius=int(w * 0.04),
                        fill=accent + (255,))
    d.rectangle([lx0, ly0 + bh - int(w * 0.04), lx1, ly0 + bh],
                fill=accent + (255,))
    if detail and w > 150:
        fb = ImageFont.truetype(FB, max(8, int(w * 0.052)))
        t = "GAME BOY ADVANCE"
        tw = d.textlength(t, font=fb)
        d.text((cx - tw / 2, ly0 + bh * 0.22), t, font=fb, fill=(255, 255, 255, 255))

    # label art: abstract burst (evokes key art without copying it)
    if detail:
        ctop = ly0 + bh
        carea = (ly1 - ly0 - bh)
        bcx, bcy = cx, ctop + carea * 0.22
        br = (lx1 - lx0) * 0.22
        pts = []
        for i in range(16):
            a = math.pi * i / 8
            rr = br * (1.0 if i % 2 == 0 else 0.62)
            pts.append((bcx + rr * math.cos(a), bcy + rr * math.sin(a)))
        d.polygon(pts, fill=accent + (44,))

    # title on label
    if detail:
        f1 = ImageFont.truetype(FB, int(w * (0.105 if len(title) < 12 else 0.088)))
        tw = d.textlength(title, font=f1)
        ty = ctop + carea * 0.52
        d.text((cx - tw / 2, ty), title, font=f1, fill=(30, 30, 34, 255))
        f2 = ImageFont.truetype(FB, int(w * 0.075))
        sw = d.textlength(subtitle, font=f2)
        d.text((cx - sw / 2, ty + int(w * 0.115)), subtitle, font=f2,
               fill=accent + (255,))
        # bottom row: rating box + publisher
        bw = int(w * 0.13)
        bx0, by0 = lx0 + int(w * 0.06), ly1 - int(w * 0.16)
        d.rectangle([bx0, by0, bx0 + bw, by0 + bw], outline=(30, 30, 34, 255),
                    width=max(2, int(w * 0.014)))
        fe = ImageFont.truetype(FB, int(w * 0.085))
        et = "E"
        d.text((bx0 + bw / 2 - d.textlength(et, font=fe) / 2, by0 + bw * 0.08),
               et, font=fe, fill=(30, 30, 34, 255))
        fn = ImageFont.truetype(FR, int(w * 0.048))
        nt = "Nintendo"
        d.text((lx1 - int(w * 0.06) - d.textlength(nt, font=fn),
                by0 + bw * 0.22), nt, font=fn, fill=(90, 90, 96, 255))

    # gloss: diagonal light stripe (the collectible shine)
    gw = int(w * 0.30)
    gloss = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dg = ImageDraw.Draw(gloss)
    dg.polygon([(x0 + w * 0.18, y0), (x0 + w * 0.18 + gw, y0),
                (x0 + w * 0.02 + gw, y1), (x0 + w * 0.02, y1)],
               fill=(255, 255, 255, 52))
    dg.polygon([(x0 + w * 0.18 + gw + 14, y0), (x0 + w * 0.18 + gw + 30, y0),
                (x0 + w * 0.02 + gw + 30, y1), (x0 + w * 0.02 + gw + 14, y1)],
               fill=(255, 255, 255, 26))
    # clip gloss to shell
    mask = Image.new("L", img.size, 0)
    dm = ImageDraw.Draw(mask)
    dm.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=255)
    img = Image.composite(Image.alpha_composite(img, gloss), img, mask)

    # top edge highlight
    d = ImageDraw.Draw(img)
    d.line([x0 + r, y0 + 2, x1 - r, y0 + 2], fill=(255, 255, 255, 90),
           width=max(2, int(w * 0.02)))
    return img


def paste_cart(base, cart_img, cx, cy, angle=0, glow=None):
    """Paste a cart centered at (cx, cy), rotated; optional glow color."""
    cart = cart_img.rotate(angle, resample=Image.BICUBIC, expand=True)
    if glow:
        g = Image.new("RGBA", cart.size, (0, 0, 0, 0))
        dg = ImageDraw.Draw(g)
        alpha = cart.split()[3].point(lambda v: 255 if v > 10 else 0)
        dg.rounded_rectangle([6, 6, cart.size[0] - 6, cart.size[1] - 6],
                             radius=24, outline=glow + (230,), width=7)
        from PIL.ImageFilter import GaussianBlur
        g = g.filter(GaussianBlur(9))
        base.alpha_composite(g, (int(cx - cart.size[0] / 2), int(cy - cart.size[1] / 2)))
    base.alpha_composite(cart, (int(cx - cart.size[0] / 2), int(cy - cart.size[1] / 2)))


def draw_marquee(d):
    """Pokémon Emerald hero title — typographic, integrated, no pasted logo."""
    # soft glow bed behind the title
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow)
    dg.ellipse([430, 40, 1010, 330], fill=(120, 160, 255, 46))
    d.bitmap((0, 0), glow)

    f_pre = ImageFont.truetype(FB, 52)
    pre = "Pok\u00e9mon"
    x = 424
    d.text((x + 3, 89), pre, font=f_pre, fill=(8, 26, 90, 255))
    d.text((x, 86), pre, font=f_pre, fill=(255, 255, 255, 255))

    # EMERALD — big, letterspaced, blue offset shadow
    f_big = ImageFont.truetype(FB, 96)
    word = "EMERALD"
    ls = 9
    widths = [d.textlength(ch, font=f_big) for ch in word]
    x = 420
    y = 148
    for ch, cw in zip(word, widths):
        d.text((x + 6, y + 7), ch, font=f_big, fill=(8, 26, 90, 255))
        x += cw + ls
    x = 420
    for ch, cw in zip(word, widths):
        d.text((x, y), ch, font=f_big, fill=(255, 255, 255, 255))
        x += cw + ls

    # tiny yellow sparkles (restrained)
    for sx, sy, s in ((990, 116, 9), (1022, 172, 6), (404, 246, 6)):
        d.polygon([(sx, sy - s), (sx + s * 0.35, sy - s * 0.35),
                   (sx + s, sy), (sx + s * 0.35, sy + s * 0.35),
                   (sx, sy + s), (sx - s * 0.35, sy + s * 0.35),
                   (sx - s, sy), (sx - s * 0.35, sy - s * 0.35)],
                  fill=YELLOW + (255,))
    # version tag
    f_tag = ImageFont.truetype(FB, 17)
    tag = "HOENN  \u00b7  2005"
    d.text((424, 286), tag, font=f_tag, fill=(255, 214, 10, 255))

# --------------------------------------------------------------------------
# Proof mock: full 1280x960 composition with live text.
# --------------------------------------------------------------------------

META_ROWS = [
    ("LAST PLAYED", "12 Sep 2026"),
    ("PLAY TIME", "48H 12M"),
    ("PLAYERS", "1"),
    ("GENRE", "RPG"),
    ("RELEASED", "2005"),
    ("DEVELOPER", "Game Freak"),
]

CAROUSEL_GAMES = [
    ("RUBY", (192, 39, 45), (150, 28, 34)),
    ("SAPPHIRE", (36, 86, 200), (24, 62, 150)),
    ("EMERALD", (31, 170, 107), (20, 120, 78)),
    ("FIRE RED", (192, 39, 45), (150, 28, 34)),
    ("LEAF GREEN", (46, 158, 91), (30, 112, 64)),
    ("PINBALL", (123, 79, 201), (88, 54, 150)),
]
SELECTED = 2


def draw_panel_text(d):
    f_pill = ImageFont.truetype(FB, 20)
    t = "GBA"
    tw = d.textlength(t, font=f_pill)
    d.text((PAD + 50 - tw / 2, 58), t, font=f_pill, fill=(10, 36, 112, 255))

    f_title = ImageFont.truetype(FB, 31)
    d.text((PAD, 104), "Pok\u00e9mon", font=f_title, fill=WHITE + (255,))
    d.text((PAD, 142), "Emerald", font=f_title, fill=WHITE + (255,))
    d.rectangle([PAD, 188, PAD + 48, 194], fill=YELLOW + (255,))

    f_desc = ImageFont.truetype(FR, 15)
    desc = ("Journey across Hoenn, complete\n"
            "the Pok\u00e9dex and stop Team Aqua\n"
            "and Team Magma.")
    d.multiline_text((PAD, 210), desc, font=f_desc, fill=(188, 202, 240, 255),
                     spacing=5)

    f_lab = ImageFont.truetype(FB, 11)
    f_val = ImageFont.truetype(FB, 18)
    y = 326
    for lab, val in META_ROWS:
        d.text((PAD, y), lab, font=f_lab, fill=DIM + (255,))
        vw = d.textlength(val, font=f_val)
        d.text((PANEL_X1 - 24 - vw, y - 4), val, font=f_val, fill=WHITE + (255,))
        y += 46

    d.text((PAD, 628), "RATING", font=f_lab, fill=DIM + (255,))
    sx = PAD
    for i in range(5):
        star(d, sx + 14, 668, 13, YELLOW + (255,))
        sx += 34

    f_count = ImageFont.truetype(FB, 56)
    d.text((PAD, 722), "248", font=f_count, fill=WHITE + (255,))
    f_clab = ImageFont.truetype(FB, 12)
    d.text((PAD, 788), "GAMES IN LIBRARY", font=f_clab, fill=YELLOW + (255,))
    f_tag = ImageFont.truetype(FR, 10)
    d.text((PAD, 900), "CRYSTAL \u00b7 NOVA", font=f_tag, fill=(120, 140, 200, 255))


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + math.pi * i / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def draw_carousel(base):
    # zone: right of the panel, over the fade
    zx0, zx1 = 400, 1240
    cy = 800
    slot = (zx1 - zx0) / 6
    f_name = ImageFont.truetype(FB, 13)
    for i, (short, body, accent) in enumerate(CAROUSEL_GAMES):
        cx = zx0 + slot * (i + 0.5)
        sel = (i == SELECTED)
        wcart = 148 if sel else 104
        cart = draw_gba_cart(wcart, body, accent, short,
                             "POK\u00c9MON" if detail_ok(wcart) else "",
                             detail=detail_ok(wcart))
        if not sel:
            # dim + desaturate the neighbours (what the engine does) —
            # gently: they must stay readable and collectible, not gray.
            g = cart.convert("L").convert("RGBA")
            cart = Image.blend(cart, g, 0.28)
            rgb = cart.convert("RGB").point(lambda v: int(v * 0.86))
            cart = Image.merge("RGBA", (*rgb.split(), cart.split()[3]))
        paste_cart(base, cart, cx, cy, angle=-6 if sel else 0,
                   glow=(255, 255, 255) if sel else None)
        # title beneath — short clean caps, never wider than the slot
        tw = base_draw.textlength(short, font=f_name)
        lx = cx - tw / 2
        col = WHITE + (255,) if sel else (170, 185, 225, 255)
        ly = cy + (102 if sel else 74)
        base_draw.text((lx, ly), short, font=f_name, fill=col)
        if sel:
            base_draw.rectangle([lx, ly + 20, lx + tw, ly + 23],
                                fill=YELLOW + (255,))


def detail_ok(wcart):
    return wcart > 120


def draw_footer(d):
    f_k = ImageFont.truetype(FB, 14)
    f_w = ImageFont.truetype(FR, 14)
    items = [("A", "Select"), ("B", "Back"), ("Y", "Options")]
    x = 1256
    for key, word in reversed(items):
        ww = d.textlength(word, font=f_w)
        kw = d.textlength(key, font=f_k)
        x -= ww
        d.text((x, 928), word, font=f_w, fill=(190, 200, 235, 255))
        x -= kw + 7
        d.text((x, 928), key, font=f_k, fill=YELLOW + (255,))
        x -= 26


def build_mock():
    img = paint_background()
    d = ImageDraw.Draw(img, "RGBA")
    global base_draw
    base_draw = d

    # fanart wash over the hero zone (duotone light bed)
    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dw = ImageDraw.Draw(wash)
    dw.ellipse([560, 330, 1120, 640], fill=(140, 175, 255, 52))
    img.alpha_composite(wash)
    d = ImageDraw.Draw(img, "RGBA")
    base_draw = d

    draw_panel_text(d)
    draw_marquee(d)

    # physical-media hero: Emerald cart, angled, glossy, premium
    hero = draw_gba_cart(300, (31, 170, 107), (22, 130, 84),
                         "EMERALD", "POK\u00c9MON", detail=True)
    paste_cart(img, hero, 1045, 445, angle=-8)

    # bottom fade is baked into the mock background already? No — composite
    # the fade asset so the mock matches the theme exactly.
    fade = Image.open(os.path.join(ART, "gamelist_fade.png")).convert("RGBA")
    img.alpha_composite(fade, (376, 600))

    draw_carousel(img)
    d = ImageDraw.Draw(img, "RGBA")
    draw_footer(d)
    img.convert("RGB").save("/tmp/library_mock.png", quality=92)
    print("wrote /tmp/library_mock.png")


def build_fade():
    # sized for the carousel zone (x 376-1280); the theme places it at
    # pos 0.294 0.625, size 0.706 0.375.
    fw, fh = 904, 360
    fade = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
    d = ImageDraw.Draw(fade, "RGBA")
    for y in range(fh):
        t = y / (fh - 1)
        a = int(232 * t ** 1.6)
        d.line([0, y, fw, y], fill=(7, 22, 80, a), width=1)
    halftone(fade, 0, 40, fw, fh, spacing=16, rmax=3.0,
             color=(255, 255, 255), alpha=20, direction=1)
    fade.save(os.path.join(ART, "gamelist_fade.png"))
    print("wrote", os.path.join(ART, "gamelist_fade.png"))


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "--mock"
    if arg == "--background":
        paint_background().convert("RGB").save(
            os.path.join(ART, "gamelist_library.webp"), quality=90)
        print("wrote", os.path.join(ART, "gamelist_library.webp"))
    elif arg == "--fade":
        build_fade()
    elif arg == "--mock":
        build_mock()
    else:
        print("usage: build_library.py [--background|--fade|--mock]")


if __name__ == "__main__":
    main()
