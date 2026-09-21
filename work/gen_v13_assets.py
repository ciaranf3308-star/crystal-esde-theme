#!/usr/bin/env python3
"""Crystal v13.0.0 asset generation: PREMIUM POLISH pass on the approved
gamelist skeleton. Base: the v12 mock. Regions preserved (left panel zone,
narrower system spine, hero right, title beneath hero). What changes is the
finish:

- Left column: same integrated module, but de-boxed into a Japanese
  magazine editorial sidebar - no heavy nested frames, no left-edge blue
  strip, typography-led hierarchy. Royal header band (taller, NOW SHOWING
  + yellow baseline), marquee on a clean white mat with a royal L-frame and
  yellow corner tick (headline block, not a box), editorial metadata with
  clean tracked kickers, screenshot as a hairline-framed print with one
  yellow tick. Fewer rules, more air.
- Central spine: thinner (76 -> 60px), cleaner magazine spine - royal
  gradient band, ONE thin yellow separator line, smaller dot-grid accents,
  supplied logos rotated 90deg CCW (tighter sticker offset);
  nes/psp/steam/windows/xbox360 keep text fallback.
- Hero: restrained but richer - asymmetric blue atmosphere, tighter gold
  aura, LAYERED gold ring (outer hairline + main band + inner light line +
  tight soft accent, all transparent-cored; the v10 halo stays retired),
  clean soft contact shadow.
- Title rule widened 240 -> 300 for confidence.

Geometry (1280x960): panel (6,10) 470x940; spine (486,24) 60x912; hero
540px at (900,430); prev/next (900,10)/(900,850); pitch 420; rule Y716 /
title Y736 / meta line Y757.
ES-DE 3.4.1 has no theme keyframes/idle animation: art direction only
implies motion (aura pulse layer, slide echoes in the mock); the engine
contributes native carousel transitions."""
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
PALE_GOLD = (255, 226, 120)
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

def tracked_text_img(text, size, color, tracking):
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
        d.text((x, 3), ch, font=font, fill=color + (255,))
        x += w + tracking
    return img

# ------------------------- the de-boxed editorial left panel ---
# 470x940, local coords (global origin 6,10). One continuous angular white
# module, typography-led: no heavy nested frames, no left-edge strip.
# Punched windows stay where the dynamic art lands:
#   marquee  (global 36,74 404x188) -> local (30,64,434,252)
#   screenshot (global 42,700 396x210) -> local (36,690,432,900)
# Both are clean white mats; the dynamic art renders on top via zIndex.
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

    # header band: royal, taller, angular cut, yellow baseline
    d.polygon([(26, 0), (390, 0), (420, 30), (424, 58), (18, 58)], fill=ROYAL + (255,))
    d.line([(18, 58), (424, 58)], fill=YELLOW + (255,), width=2)
    kick = tracked_text_img("NOW SHOWING", 16, WHITE, 4)
    body.alpha_composite(kick, (32, 15))
    d.polygon([(404, 18), (426, 16), (414, 34)], fill=YELLOW + (255,))  # band tick

    # marquee headline block: clean white mat, royal L-frame, yellow tick.
    # The dynamic marquee art lands on the mat via zIndex (above the panel).
    d.rectangle([30, 64, 434, 252], fill=(250, 252, 255, 255))  # white mat
    d.rectangle([24, 58, 29, 258], fill=ROYAL + (255,))      # L-frame: left
    d.rectangle([24, 252, 440, 257], fill=ROYAL + (255,))    # L-frame: bottom
    d.polygon([(24, 58), (48, 58), (24, 82)], fill=YELLOW + (255,))  # corner tick

    # section label, editorial: small caps + one tick, no box
    d.rectangle([30, 280, 35, 294], fill=YELLOW + (255,))
    lbl = tracked_text_img("GAME DETAILS", 13, ROYAL, 3)
    body.alpha_composite(lbl, (52, 279))

    # single hairline under the description (global y 432 -> local 422)
    d.line([(36, 422), (436, 422)], fill=ROYAL + (110,), width=1)
    d.rectangle([(36, 419), (44, 425)], fill=YELLOW + (255,))

    # baked kickers (dynamic values land via XML) - clean tracked caps
    for text, xy in [("RELEASED", (48, 428)), ("RATING", (296, 428)),
                     ("GENRE", (48, 534)), ("PLAYERS", (48, 592)),
                     ("DEVELOPER", (240, 592)), ("SCREENSHOT", (48, 656))]:
        k = tracked_text_img(text, 12, ROYAL, 3)
        body.alpha_composite(k, xy)

    # single separator before the screenshot zone
    d.line([(28, 648), (170, 648)], fill=YELLOW + (255,), width=2)
    d.line([(170, 648), (446, 648)], fill=ROYAL + (140,), width=1)

    # screenshot print: ONE royal hairline + yellow corner tick (no nested
    # boxes). The dynamic screenshot art lands on the white mat via zIndex.
    d.rectangle([36, 690, 432, 900], fill=(250, 252, 255, 255))  # white mat
    d.rectangle([34, 688, 434, 902], outline=ROYAL + (255,), width=1)
    d.polygon([(34, 688), (58, 688), (34, 712)], fill=YELLOW + (255,))  # tick

    # refined detailing: halftone right edge, small blueprint print marks
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (446, 320, 462, 860), ROYAL, spacing=8, max_r=3.0, fade="left", alpha_max=45)
    blueprint(deco, (44, 912, 190, 930), alpha=18)

    body = Image.composite(body, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
    body = grain(body, mask)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    img = Image.alpha_composite(img, body)
    p = os.path.join(ART, "lib_panel_main.png")
    img.save(p)
    print("lib_panel_main.png", img.size)

# --------------------------------------------- hero elevation (540px) ---
def gen_hero_blue():
    # asymmetric blue atmosphere: light biased up-left of the hero
    W, H = 640, 576
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = W / 2 - 90, H / 2 - 100
    R = 300
    for r in range(int(R), 0, -2):
        t = r / R
        a = int(54 * (1 - t) ** 1.8)
        d.ellipse([cx - r * 1.12, cy - r * 0.95, cx + r * 1.12, cy + r * 0.95],
                  fill=(46, 96, 220, a))
    img.save(os.path.join(ART, "lib_glow_blue.png"))
    print("lib_glow_blue.png", img.size)

def gen_hero_aura():
    # tighter restrained golden aura: soft falloff just outside the ring,
    # transparent core (no halo)
    S = 680
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    c = S / 2
    for r in range(344, 282, -2):
        t = (344 - r) / 62.0
        a = int(40 * (1 - t) ** 1.7)
        d.ellipse([c - r, c - r, c + r, c + r], fill=(255, 196, 44, a))
    img.save(os.path.join(ART, "lib_hero_aura.png"))
    print("lib_hero_aura.png", img.size)

def gen_hero_ring():
    # LAYERED premium ring hugging the 540px hero (disc r270 -> ring r278):
    # tight soft accent + outer hairline + main gold band + inner light line.
    S = 620
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c, R = S / 2, 278
    soft = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(soft, "RGBA").ellipse([c - R - 8, c - R - 8, c + R + 8, c + R + 8],
                                        outline=(255, 200, 60, 42), width=12)
    img = Image.alpha_composite(img, soft.filter(ImageFilter.GaussianBlur(5)))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([c - R - 9, c - R - 9, c + R + 9, c + R + 9],
              outline=PALE_GOLD + (110,), width=1)          # outer hairline
    d.ellipse([c - R, c - R, c + R, c + R],
              outline=YELLOW + (255,), width=3)              # main gold band
    d.ellipse([c - R + 6, c - R + 6, c + R - 6, c + R - 6],
              outline=(255, 240, 180, 170), width=1)         # inner light line
    img.save(os.path.join(ART, "lib_hero_ring.png"))
    print("lib_hero_ring.png", img.size)

def gen_hero_shadow():
    W, H = 600, 56
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([50, 10, W - 50, H - 10], fill=(8, 16, 52, 115))
    img = img.filter(ImageFilter.GaussianBlur(10))
    img.save(os.path.join(ART, "lib_shadow_soft.png"))
    print("lib_shadow_soft.png", img.size)

# ------------------------------------------------- title double rule ---
def gen_title_rule():
    # widened 240 -> 300 for a more confident title block
    W, H = 300, 10
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 1, W, 3], fill=WHITE + (235,))      # white hairline
    for x in range(W):                                  # yellow bar, sweep head
        t = x / (W - 1)
        col = (255, int(196 + 28 * t), int(10 + 40 * t))
        d.line([(x, 5), (x, 9)], fill=col + (255,))
    img.save(os.path.join(ART, "lib_title_rule.png"))
    print("lib_title_rule.png", img.size)

# --------------------------------------------- the console spine ---
# Thinner magazine spine: 60x912, royal gradient, ONE thin yellow separator
# line, small dot-grid accents, supplied logo rotated 90deg CCW with a tight
# sticker offset; text fallback for the five systems without a supplied logo.
SYSTEMS = [
    ("dreamcast", "DREAMCAST"), ("gb", "GAME BOY"), ("gba", "GAME BOY ADVANCE"),
    ("gbc", "GAME BOY COLOR"), ("gc", "GAMECUBE"), ("genesis", "GENESIS"),
    ("megadrive", "MEGA DRIVE"), ("n3ds", "NINTENDO 3DS"), ("n64", "NINTENDO 64"),
    ("nds", "NINTENDO DS"), ("nes", "NES"), ("ps2", "PLAYSTATION 2"),
    ("psp", "PSP"), ("psx", "PLAYSTATION"), ("snes", "SNES"), ("steam", "STEAM"),
    ("wii", "WII"), ("wiiu", "WII U"), ("windows", "WINDOWS"), ("xbox", "XBOX"),
    ("xbox360", "XBOX 360"),
]

def tracked_text_v13(name, font, tracking):
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
    # ONE thin yellow separator line, left edge, with a small accent head
    d.line([(4, 44), (4, 888)], fill=YELLOW + (255,), width=2)
    d.rectangle([2, 24, 7, 44], fill=YELLOW + (255,))
    # small dot-grid accents, top and bottom
    dotgrid(img, (12, 52, 50, 128), alpha=40, spacing=12)
    dotgrid(img, (12, 784, 50, 860), alpha=40, spacing=12)
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
        tw = tracked_text_v13(name, font, 8)
        while tw.width > 700 and size > 18:
            size -= 2
            font = ImageFont.truetype(FB, size)
            tw = tracked_text_v13(name, font, 8)
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
    gen_hero_aura()
    gen_hero_ring()
    gen_hero_shadow()
    gen_title_rule()
    missing = []
    for system, name in SYSTEMS:
        if gen_rail(system, name) != "logo":
            missing.append(system)
    print("rails: 21 | text fallback:", missing if missing else "none")
