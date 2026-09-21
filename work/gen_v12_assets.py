#!/usr/bin/env python3
"""Crystal v12.0.0 asset generation: VISUAL MATURITY pass on the approved
gamelist skeleton. Regions unchanged; the treatment is rebuilt for a premium,
editorial, collectible feel:

- Left column: ONE integrated white module (not three stacked cards) -
  angular clipped silhouette, royal-blue structural header band with the
  marquee mounted as the panel hero on a clean white/blue framed field,
  editorial metadata zone (description first, one large marker anchor year,
  grouped facts with baked tracked kickers), integrated screenshot print
  module at the bottom, blue spine, small sharp yellow accents, halftone /
  blueprint detailing, subtle baked shadow.
- Central spine: proper visual spine - royal band, angular clips, dot-grid
  accents, ONE thin yellow separator line, supplied logos rotated 90deg CCW
  (sticker offset); nes/psp/steam/windows/xbox360 keep text fallback.
- Hero: enlarged to 540px, restrained gold aura + thin gold ring (no giant
  halo), tighter blue atmosphere, cleaner contact shadow.
- Title: double rule (white hairline + yellow bar with a sweep gradient).

Geometry (1280x960): panel (6,10) 470x940; spine (486,24) 76x912; hero 540px
at (900,430); prev/next (900,10)/(900,850); pitch 420; rule Y716/title Y736.
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

# --------------------------------- the integrated left panel ---
# 470x940, local coords (global origin 6,10). One continuous angular white
# module: blue structural header band (marquee hero), editorial metadata
# zone, integrated screenshot print. Baked kickers/rules; dynamic text and
# art land on the framed wells via XML.
def gen_panel():
    W, H = 470, 940
    poly = [(34, 0), (386, 0), (448, 62), (458, 150), (446, 430), (460, 700),
            (450, 878), (414, 940), (46, 940), (16, 894), (22, 640), (12, 300),
            (26, 58)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 10, y + 13) for x, y in poly], fill=(6, 14, 44, 100))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(14)))

    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(body).polygon(poly, fill=WHITE + (238,))
    d = ImageDraw.Draw(body, "RGBA")

    # blue structural spine along the left edge
    d.polygon([(24, 60), (38, 60), (34, 930), (20, 930)], fill=ROYAL + (255,))
    d.line([(36, 64), (32, 926)], fill=NAVY + (255,), width=2)
    d.polygon([(23, 468), (37, 466), (30, 482)], fill=YELLOW + (255,))  # spine tick

    # header band: royal, follows the clipped top
    d.polygon([(26, 0), (388, 0), (420, 32), (424, 52), (18, 52)], fill=ROYAL + (255,))
    d.line([(18, 52), (424, 52)], fill=NAVY + (255,), width=2)
    kick = tracked_text_img("NOW SHOWING", 16, WHITE, 4)
    body.alpha_composite(kick, (30, 13))
    d.polygon([(404, 16), (426, 14), (414, 32)], fill=YELLOW + (255,))  # band tick

    # marquee hero: clean white field, royal frame, punched window
    d.rectangle([22, 56, 442, 256], fill=(250, 252, 255, 255))
    d.rectangle([22, 56, 442, 256], outline=ROYAL + (255,), width=3)
    d.line([(28, 62), (436, 62)], fill=NAVY + (160,), width=1)
    d.rectangle([30, 64, 434, 248], fill=(250, 252, 255, 255))  # clean white mat for the marquee art
    d.polygon([(22, 56), (44, 56), (22, 78)], fill=YELLOW + (255,))  # corner tick

    # separator: sharp yellow strike + royal hairline
    d.line([(28, 272), (190, 272)], fill=YELLOW + (255,), width=2)
    d.line([(190, 272), (446, 272)], fill=ROYAL + (140,), width=1)

    # section label
    d.rectangle([28, 279, 33, 293], fill=YELLOW + (255,))
    lbl = tracked_text_img("GAME DETAILS", 13, ROYAL, 3)
    body.alpha_composite(lbl, (52, 278))

    # hairline under the description (global y 432 -> local 422)
    d.line([(36, 422), (436, 422)], fill=ROYAL + (110,), width=1)
    d.rectangle([(36, 419), (44, 425)], fill=YELLOW + (255,))

    # baked kickers (dynamic values land via XML)
    for text, xy in [("RELEASED", (48, 428)), ("RATING", (296, 428)),
                     ("GENRE", (48, 534)), ("PLAYERS", (48, 592)),
                     ("DEVELOPER", (240, 592)), ("SCREENSHOT", (48, 656))]:
        k = tracked_text_img(text, 12, ROYAL, 3)
        body.alpha_composite(k, xy)

    # separator before the screenshot zone
    d.line([(28, 648), (170, 648)], fill=YELLOW + (255,), width=2)
    d.line([(170, 648), (446, 648)], fill=ROYAL + (140,), width=1)

    # screenshot print: framed well, punched window (local 36,690 396x210,
    # matching the dynamic libScreenshot box at global 42,700)
    d.rectangle([28, 682, 440, 908], fill=(250, 252, 255, 255))
    d.rectangle([28, 682, 440, 908], outline=ROYAL + (255,), width=3)
    d.rectangle([34, 688, 434, 902], outline=NAVY + (120,), width=1)
    d.rectangle([36, 690, 432, 900], fill=(0, 0, 0, 0))  # window for dynamic art
    d.polygon([(414, 902), (440, 900), (428, 908)], fill=YELLOW + (255,))  # lip tick

    # refined detailing: halftone right edge, blueprint print-mark zone
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (444, 300, 462, 880), ROYAL, spacing=8, max_r=3.2, fade="left", alpha_max=55)
    blueprint(deco, (44, 912, 200, 932), alpha=20)
    blueprint(deco, (250, 300, 300, 340), alpha=16)

    body = Image.composite(body, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
    body = grain(body, mask)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    img = Image.alpha_composite(img, body)
    p = os.path.join(ART, "lib_panel_main.png")
    img.save(p)
    print("lib_panel_main.png", img.size)

# --------------------------------------------- hero elevation (540px) ---
# Restrained gold aura hugging the hero (transparent core), a thin gold
# ring, tighter asymmetric blue atmosphere, cleaner contact shadow.
def gen_hero_blue():
    W, H = 640, 576
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy, R = W / 2 - 50, H / 2 - 60, 300
    for r in range(int(R), 0, -2):
        t = r / R
        a = int(52 * (1 - t) ** 1.8)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 96, 220, a))
    img.save(os.path.join(ART, "lib_glow_blue.png"))
    print("lib_glow_blue.png", img.size)

def gen_hero_aura():
    # restrained golden aura: soft falloff outside r=282, transparent core
    S = 680
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    c = S / 2
    for r in range(348, 280, -2):
        t = (348 - r) / 68.0
        a = int(44 * (1 - t) ** 1.6)
        d.ellipse([c - r, c - r, c + r, c + r], fill=(255, 196, 44, a))
    img.save(os.path.join(ART, "lib_hero_aura.png"))
    print("lib_hero_aura.png", img.size)

def gen_hero_ring():
    # thin gold ring hugging the 540px hero (r270)
    S = 620
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c, R = S / 2, 278
    box = [c - R, c - R, c + R, c + R]
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow, "RGBA").ellipse(box, outline=YELLOW + (45,), width=8)
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(5)))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse(box, outline=YELLOW + (255,), width=3)
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
    W, H = 240, 10
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
# A proper visual spine: royal band with angular clips, dot-grid accents,
# ONE thin yellow separator line, supplied logo rotated 90deg CCW with a
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

def tracked_text_v12(name, font, tracking):
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
    W, H = 76, 912
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    poly = [(0, 0), (56, 0), (76, 20), (76, 912), (20, 912), (0, 892)]
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
    # ONE thin yellow separator line, left edge
    d.line([(5, 24), (5, 888)], fill=YELLOW + (255,), width=3)
    dotgrid(img, (14, 44, 64, 150), alpha=45)
    dotgrid(img, (14, 762, 64, 868), alpha=45)
    # subtle inner edge, right side
    d.line([(70, 26), (70, 886)], fill=NAVY + (140,), width=1)
    logo_path = os.path.join(LOGOS, f"{system}.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        rot = logo.rotate(90, expand=True)
        rw, rh = rot.size
        scale = min(56.0 / rw, 690.0 / rh)
        rot = rot.resize((max(1, int(rw * scale)), max(1, int(rh * scale))), Image.LANCZOS)
        ox, oy = (W - rot.width) // 2 + 3, (H - rot.height) // 2
        white = Image.new("RGBA", rot.size, WHITE + (255,))
        white.putalpha(rot.split()[3])
        img.alpha_composite(white, (ox + 3, oy + 3))
        img.alpha_composite(rot, (ox, oy))
        kind = "logo"
    else:
        size = 40
        font = ImageFont.truetype(FB, size)
        tw = tracked_text_v12(name, font, 9)
        while tw.width > 690 and size > 20:
            size -= 2
            font = ImageFont.truetype(FB, size)
            tw = tracked_text_v12(name, font, 9)
        vert = tw.rotate(90, expand=True)
        ox, oy = (W - vert.width) // 2 + 3, (H - vert.height) // 2
        shade = Image.new("RGBA", vert.size, NAVY + (255,))
        shade.putalpha(vert.split()[3])
        img.alpha_composite(shade, (ox + 3, oy + 3))
        img.alpha_composite(vert, (ox, oy))
        kind = "TEXT-FALLBACK"
    img.save(os.path.join(RAILS, f"{system}.png"))
    return kind

# ------------------------------------------------------------ retire ---
RETIRED = ["lib_mod_masthead.png", "lib_mod_meta.png", "lib_mod_shot.png",
           "lib_kicker_released.png", "lib_kicker_genre.png",
           "lib_kicker_players.png", "lib_kicker_developer.png",
           "lib_kicker_rating.png", "lib_hero_arc.png"]

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
    for name in RETIRED:
        p = os.path.join(ART, name)
        if os.path.exists(p):
            os.remove(p)
            print("retired", name)
