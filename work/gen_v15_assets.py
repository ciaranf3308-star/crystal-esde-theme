#!/usr/bin/env python3
"""Crystal v15.0.0 asset generation: VISUAL MATURITY pass on the approved
gamelist skeleton. MACRO LAYOUT LOCKED (left column 6,10 470x940; spine
486,24 60x912; hero 540px at 900,430; prev/next 900,10 / 900,850 pitch 420;
rule Y716 / title Y736 / meta Y757; screenshot 42,700 396x210).

What changes is the finish, per the user's 10-point brief:

1. Hero: the concentric-ring / turntable decoration is GONE. Depth comes
   only from scale, a soft contact shadow (now detached for slight
   elevation), a restrained atmospheric blue glow pooling beneath the disc,
   and ONE very thin selective yellow rim highlight (a partial top arc,
   fading at both ends - not a circle). lib_hero_aura.png and
   lib_hero_ring.png are retired.
2. Left column: same footprint, now ONE editorial composition. The big
   royal header band is gone; the marquee sits on open whitespace with a
   single hairline rule beneath it. No mats, no L-frames, no nested boxes.
   Content is separated by typography, whitespace and a few graphic rules.
3. Marquee: dominates the upper-left; NOW SHOWING is a tiny kicker.
4. Metadata: oversized year anchor, strong genre value, quiet players/dev,
   rating adjacent. Labels are tiny and quiet; values carry the weight.
5. Screenshot: single royal hairline frame on the white page (no mat),
   one yellow corner tick, one accent that breaks the frame upward into
   the panel (controlled overlap).
6. Spine: refined 60px magazine spine - cleaner edges, subtle halftone,
   ONE controlled yellow line with small connector ticks reaching into the
   adjacent surfaces, supplied logos rotated 90deg CCW; text fallbacks for
   nes/psp/steam/windows/xbox360.
7. Title zone: bolder title face, redesigned rule (white hairline + SHORT
   yellow bar with a sweep head), composite secondary line
   (genre - year - dev - players) built from inline elements.
8/9. Carousel depth + controlled overlap: neighbours smaller/dimmer; two
   subtle foreground shards at the upper-right and lower-right edges crop
   the prev/next items so they read as entering the frame; one soft
   graphic plane behind the hero's lower-right is overlapped BY the disc.
10. No nested borders, no giant glows, no placeholder rects.

ES-DE 3.4.1 has no theme keyframes/idle animation: the engine contributes
native eased carousel transitions; art implies motion only."""
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ART = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal/art")
RAILS = os.path.join(ART, "rails")
LOGOS = os.path.join(ART, "console_logos")
os.makedirs(RAILS, exist_ok=True)

ROYAL = (18, 58, 178)
DEEP = (10, 47, 160)
NAVY = (10, 26, 92)
INKDIM = (58, 74, 115)
YELLOW = (255, 214, 10)
WHITE = (255, 255, 255)

random.seed(20260921)

# ------------------------------------------------------------- helpers ---
def halftone(img, box, color, spacing=9, max_r=4.2, fade="right", alpha_max=95):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img, "RGBA")
    for yy in range(y0, y1, spacing):
        for xx in range(x0, x1, spacing):
            span = max(1, (x1 - x0) if fade in ("right", "left") else (y1 - y0))
            if fade == "right":
                t = (xx - x0) / span
            elif fade == "left":
                t = 1 - (xx - x0) / span
            elif fade == "down":
                t = (yy - y0) / span
            else:
                t = 1 - (yy - y0) / span
            t = max(0.0, min(1.0, t))
            r = max_r * t
            if r < 0.7:
                continue
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=color + (int(alpha_max * t),))

def blueprint(img, box, color=(16, 52, 160), step=14, alpha=30):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img, "RGBA")
    for xx in range(x0, x1 + 1, step):
        d.line([(xx, y0), (xx, y1)], fill=color + (alpha,), width=1)
    for yy in range(y0, y1 + 1, step):
        d.line([(x0, yy), (x1, yy)], fill=color + (alpha,), width=1)

def dotgrid(img, box, color=(255, 255, 255), spacing=13, alpha=45, r=1.6):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img, "RGBA")
    for yy in range(y0, y1, spacing):
        for xx in range(x0, x1, spacing):
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=color + (alpha,))

def grain(img, mask, strength=14, alpha=10):
    n = Image.effect_noise(img.size, strength).convert("L")
    gr = Image.merge("RGBA", (n, n, n, Image.new("L", img.size, alpha)))
    return Image.alpha_composite(img, Image.composite(gr, Image.new("RGBA", img.size, (0, 0, 0, 0)), mask))

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def tracked_text_img(text, size, color, tracking, alpha=255):
    font = ImageFont.truetype(FB, size)
    widths = []
    for ch in text:
        b = font.getbbox(ch)
        widths.append(b[2] - b[0])
    total = sum(widths) + tracking * (len(text) - 1)
    asc, desc = font.getmetrics()
    img = Image.new("RGBA", (int(total) + 6, asc + desc + 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = 3
    for ch, w in zip(text, widths):
        d.text((x, 3), ch, font=font, fill=color + (alpha,))
        x += w + tracking
    return img

# ----------------- the editorial left page (one composition) ---
# 470x940, local coords (global origin 6,10). The SAME angular white
# module silhouette (footprint locked), but de-boxed: no header band, no
# mats, no L-frames, no nested outlines. Typography + whitespace + a few
# graphic rules separate the content.
#   marquee zone (global 32,68 408x200) -> local (26,58,434,258)
#   screenshot  (global 42,700 396x210) -> local (36,690,432,900)
def gen_panel():
    W, H = 470, 940
    poly = [(34, 0), (388, 0), (452, 64), (446, 500), (458, 800),
            (446, 884), (410, 940), (46, 940), (16, 894), (24, 600),
            (12, 300), (22, 90)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 10, y + 14) for x, y in poly], fill=(6, 14, 44, 100))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(15)))

    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(body).polygon(poly, fill=WHITE + (240,))
    d = ImageDraw.Draw(body, "RGBA")

    # tiny editorial kicker (secondary) + one yellow tick: no band
    kick = tracked_text_img("NOW SHOWING", 13, ROYAL, 4, alpha=255)
    body.alpha_composite(kick, (44, 18))
    d.polygon([(28, 16), (38, 16), (28, 28)], fill=YELLOW + (255,))

    # marquee sits on OPEN WHITESPACE: no mat, no frame. One hairline rule
    # beneath the marquee zone; the marquee art may break over it.
    d.line([(36, 262), (434, 262)], fill=ROYAL + (140,), width=1)
    d.line([(36, 262), (96, 262)], fill=YELLOW + (255,), width=2)

    # quiet section label, no box
    lbl = tracked_text_img("GAME DETAILS", 11, ROYAL, 3, alpha=170)
    body.alpha_composite(lbl, (36, 290))

    # single hairline under the description (global y 435 -> local 425)
    d.line([(36, 425), (434, 425)], fill=ROYAL + (110,), width=1)
    d.rectangle([(36, 422), (44, 428)], fill=YELLOW + (255,))

    # baked kickers: tiny, quiet - the VALUES carry the weight
    for text, xy in [("RELEASED", (48, 438)), ("RATING", (296, 438)),
                     ("GENRE", (48, 538)), ("PLAYERS", (48, 598)),
                     ("DEVELOPER", (240, 598)), ("SCREENSHOT", (48, 658))]:
        k = tracked_text_img(text, 11, ROYAL, 3, alpha=165)
        body.alpha_composite(k, xy)

    # screenshot: ONE royal hairline frame straight on the white page -
    # no mat, no nested outlines. One yellow corner tick, and one accent
    # that breaks the frame upward into the panel (controlled overlap).
    d.rectangle([36, 690, 432, 900], outline=ROYAL + (255,), width=1)
    d.polygon([(36, 690), (60, 690), (36, 714)], fill=YELLOW + (255,))
    d.rectangle([430, 650, 432, 690], fill=YELLOW + (255,))   # accent above frame

    # restrained detailing: a whisper of halftone at the right edge only
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (448, 320, 462, 560), ROYAL, spacing=8, max_r=3.0, fade="left", alpha_max=38)

    body = Image.composite(body, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
    body = grain(body, mask)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    img = Image.alpha_composite(img, body)
    p = os.path.join(ART, "lib_panel_main.png")
    img.save(p)
    print("lib_panel_main.png", img.size)

# ------------------------------------ hero elevation (540px disc) ---
# NO concentric rings, NO aura, NO turntable decoration. Depth from:
# scale, a detached soft contact shadow (slight elevation), a restrained
# atmospheric blue glow pooling beneath the disc, and ONE very thin
# selective yellow rim highlight (partial top arc, faded ends).
def gen_hero_blue():
    # restrained atmospheric blue: pooled slightly below the disc centre
    W, H = 560, 500
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = W / 2, H / 2 + 46
    R = 250
    for r in range(int(R), 0, -2):
        t = r / R
        a = int(38 * (1 - t) ** 1.9)
        d.ellipse([cx - r * 1.10, cy - r * 0.92, cx + r * 1.10, cy + r * 0.92],
                  fill=(46, 96, 220, a))
    img.save(os.path.join(ART, "lib_glow_blue.png"))
    print("lib_glow_blue.png", img.size)

def gen_hero_rim():
    # ONE very thin selective yellow rim highlight: a partial top arc
    # hugging the 540px disc (r270 -> r273), 3px, fading at both ends.
    S = 620
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c, R = S / 2, 273
    d = ImageDraw.Draw(img, "RGBA")
    a0, a1 = 190.0, 350.0
    step = 1.0
    a = a0
    while a < a1:
        t = (a - a0) / (a1 - a0)
        edge = min(1.0, t / 0.16, (1.0 - t) / 0.16)
        alpha = int(235 * max(0.0, min(1.0, edge)))
        if alpha > 2:
            d.arc([c - R, c - R, c + R, c + R], start=a, end=a + step + 0.3,
                  fill=YELLOW + (alpha,), width=3)
        a += step
    img.save(os.path.join(ART, "lib_hero_rim.png"))
    print("lib_hero_rim.png", img.size)

def gen_hero_shadow():
    # soft contact shadow, detached below the disc: slight elevation
    W, H = 640, 72
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([70, 14, W - 70, H - 14], fill=(8, 16, 52, 100))
    img = img.filter(ImageFilter.GaussianBlur(12))
    img.save(os.path.join(ART, "lib_shadow_soft.png"))
    print("lib_shadow_soft.png", img.size)

# ------------------------------------------------- title rule ---
def gen_title_rule():
    # confident rule: white hairline full width + SHORT yellow bar with a
    # sweep head (deliberate, not a full-width slab)
    W, H = 300, 10
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 1, W, 3], fill=WHITE + (235,))      # white hairline
    for x in range(112):                                # short yellow bar
        t = x / 111.0
        col = (255, int(196 + 28 * t), int(10 + 40 * t))
        d.line([(x, 5), (x, 9)], fill=col + (255,))
    d.polygon([(112, 4), (130, 7), (112, 10)], fill=YELLOW + (255,))  # sweep head
    img.save(os.path.join(ART, "lib_title_rule.png"))
    print("lib_title_rule.png", img.size)

# ----------------- layered graphic planes / foreground shards ---
# Controlled overlap: one soft plane sits BEHIND the hero's lower-right
# (the disc overlaps it); two subtle foreground shards crop the prev/next
# items at the upper-right / lower-right edges so they read as entering
# the frame. All restrained: no giant glows, no pointless decoration.
def gen_plane_hero():
    W, H = 420, 360
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    poly = [(40, 0), (W, 60), (400, H), (0, 300)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(poly, fill=(18, 58, 178, 46))
    d.line([(40, 0), (W, 60)], fill=YELLOW + (120,), width=2)
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    blueprint(deco, (30, 40, 390, 330), alpha=14)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    img.save(os.path.join(ART, "lib_plane_hero.png"))
    print("lib_plane_hero.png", img.size)

def gen_shard_prev():
    W, H = 360, 180
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    poly = [(0, 0), (W, 0), (W, 150), (60, H)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(poly, fill=(10, 26, 92, 84))
    # short quiet tick at the top of the left edge (not a full scratch)
    d.line([(0, 0), (20, 60)], fill=YELLOW + (95,), width=2)
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (200, 20, 340, 140), (255, 255, 255), spacing=9, max_r=3.4,
             fade="left", alpha_max=30)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    img.save(os.path.join(ART, "lib_shard_prev.png"))
    print("lib_shard_prev.png", img.size)

def gen_shard_next():
    W, H = 360, 220
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    poly = [(60, 0), (W, 30), (W, H), (0, H)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(poly, fill=(10, 26, 92, 84))
    # short quiet tick at the top of the left edge (not a full scratch)
    d.line([(60, 0), (42, 66)], fill=YELLOW + (95,), width=2)
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (200, 60, 340, 190), (255, 255, 255), spacing=9, max_r=3.4,
             fade="left", alpha_max=30)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    img.save(os.path.join(ART, "lib_shard_next.png"))
    print("lib_shard_next.png", img.size)

# ------------------------------------------------- the console spine ---
# Refined magazine spine: 60x912, royal gradient, ONE thin yellow separator
# line with small connector ticks reaching into the adjacent surfaces,
# subtle halftone, supplied logo rotated 90deg CCW; text fallback for the
# five systems without a supplied logo.
SYSTEMS = [
    ("dreamcast", "DREAMCAST"), ("gb", "GAME BOY"), ("gba", "GAME BOY ADVANCE"),
    ("gbc", "GAME BOY COLOR"), ("gc", "GAMECUBE"), ("genesis", "GENESIS"),
    ("megadrive", "MEGA DRIVE"), ("n3ds", "NINTENDO 3DS"), ("n64", "NINTENDO 64"),
    ("nds", "NINTENDO DS"), ("nes", "NES"), ("ps2", "PLAYSTATION 2"),
    ("psp", "PSP"), ("psx", "PLAYSTATION"), ("snes", "SNES"), ("steam", "STEAM"),
    ("wii", "WII"), ("wiiu", "WII U"), ("windows", "WINDOWS"), ("xbox", "XBOX"),
    ("xbox360", "XBOX 360"),
]

def tracked_text_v15(name, font, tracking):
    widths = []
    for ch in name:
        b = font.getbbox(ch)
        widths.append(b[2] - b[0])
    total = sum(widths) + tracking * (len(name) - 1)
    asc, desc = font.getmetrics()
    img = Image.new("RGBA", (int(total) + 4, asc + desc + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = 2
    for ch, w in zip(name, widths):
        d.text((x, 2), ch, font=font, fill=(255, 255, 255, 255))
        x += w + tracking
    return img

def gen_rail(system, name):
    W, H = 60, 912
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    poly = [(0, 0), (42, 0), (60, 18), (60, 912), (18, 912), (0, 894)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    top = (32, 84, 208, 255)
    bot = (12, 40, 140, 255)
    dd = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / (H - 1)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(4))
        dd.line([(0, y), (W, y)], fill=col)
    img = Image.composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
    d = ImageDraw.Draw(img, "RGBA")
    # ONE thin yellow separator line, with a small accent head and tiny
    # connector ticks reaching into the adjacent surfaces
    d.line([(4, 44), (4, 888)], fill=YELLOW + (255,), width=2)
    d.rectangle([2, 24, 7, 44], fill=YELLOW + (255,))
    for ty in (300, 456, 612):
        d.line([(0, ty), (10, ty)], fill=YELLOW + (200,), width=2)
    # small dot-grid accents, top and bottom
    dotgrid(img, (12, 52, 50, 128), alpha=40, spacing=12)
    dotgrid(img, (12, 784, 50, 860), alpha=40, spacing=12)
    # subtle halftone mid-band
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (44, 340, 58, 572), (255, 255, 255), spacing=8, max_r=2.6,
             fade="left", alpha_max=26)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    d = ImageDraw.Draw(img, "RGBA")
    # subtle inner edge, right side
    d.line([(54, 26), (54, 886)], fill=NAVY + (120,), width=1)
    logo_path = os.path.join(LOGOS, f"{system}.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        rot = logo.rotate(90, expand=True)
        rw, rh = rot.size
        scale = min(40.0 / rw, 700.0 / rh)
        rot = rot.resize((max(1, int(rw * scale)), max(1, int(rh * scale))), Image.LANCZOS)
        ox, oy = (W - rot.width) // 2 + 2, (H - rot.height) // 2
        white = Image.new("RGBA", rot.size, WHITE + (255,))
        white.putalpha(rot.split()[3])
        img.alpha_composite(white, (ox + 2, oy + 2))
        img.alpha_composite(rot, (ox, oy))
        kind = "logo"
    else:
        size = 36
        font = ImageFont.truetype(FB, size)
        tw = tracked_text_v15(name, font, 8)
        while tw.width > 700 and size > 18:
            size -= 2
            font = ImageFont.truetype(FB, size)
            tw = tracked_text_v15(name, font, 8)
        vert = tw.rotate(90, expand=True)
        ox, oy = (W - vert.width) // 2 + 2, (H - vert.height) // 2
        shade = Image.new("RGBA", vert.size, NAVY + (255,))
        shade.putalpha(vert.split()[3])
        img.alpha_composite(shade, (ox + 2, oy + 2))
        img.alpha_composite(vert, (ox, oy))
        kind = "TEXT-FALLBACK"
    img.save(os.path.join(RAILS, f"{system}.png"))
    return kind

if __name__ == "__main__":
    gen_panel()
    gen_hero_blue()
    gen_hero_rim()
    gen_hero_shadow()
    gen_title_rule()
    gen_plane_hero()
    gen_shard_prev()
    gen_shard_next()
    # retire the concentric decoration: aura + layered ring
    for dead in ("lib_hero_aura.png", "lib_hero_ring.png"):
        p = os.path.join(ART, dead)
        if os.path.exists(p):
            os.remove(p)
            print("retired", dead)
    missing = []
    for system, name in SYSTEMS:
        if gen_rail(system, name) != "logo":
            missing.append(system)
    print("rails: 21 | text fallback:", missing if missing else "none")
