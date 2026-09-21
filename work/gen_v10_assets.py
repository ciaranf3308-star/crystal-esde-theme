#!/usr/bin/env python3
"""Crystal v10.0.0 asset generation: full ART DIRECTION skin pass on the v9
geometry. Same footprints everywhere; the wireframe/debug aesthetic is replaced
with the Nova hero visual language: angular white shards, royal-blue structural
pieces, halftone edges, blueprint fragments, paper grain, thin yellow strikes,
marker typography accents, sophisticated hero elevation (no yellow halo)."""
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ART = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal/art")
RAILS = os.path.join(ART, "rails")
LOGOS = os.path.join(ART, "console_logos")
os.makedirs(RAILS, exist_ok=True)

ROYAL = (18, 58, 178)
DEEP = (10, 32, 120)
NAVY = (10, 26, 92)
INK = (22, 32, 64)
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

def grain(img, mask, strength=16, alpha=12):
    n = Image.effect_noise(img.size, strength).convert("L")
    gr = Image.merge("RGBA", (n, n, n, Image.new("L", img.size, alpha)))
    return Image.alpha_composite(img, Image.composite(gr, Image.new("RGBA", img.size, (0, 0, 0, 0)), mask))

def shard_mask(size, poly):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    return m

# --------------------------------------------------- left info "panel" ---
# Angular white shard field replacing the rounded card. Same 480x940 box.
def gen_panel():
    W, H = 480, 940
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # baked drop shadow: shard silhouette offset + blurred
    poly = [(18, 12), (428, 2), (464, 44), (446, 180), (468, 250),
            (442, 430), (466, 540), (438, 710), (462, 810), (434, 928),
            (44, 920), (14, 838), (30, 600), (12, 420), (26, 220)]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 10, y + 14) for x, y in poly], fill=(6, 14, 44, 130))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img, sh)
    # white shard body
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(body).polygon(poly, fill=WHITE + (236,))
    mask = shard_mask((W, H), poly)
    # paper grain on the shard
    body = grain(body, mask, strength=14, alpha=10)
    img = Image.alpha_composite(img, body)
    d = ImageDraw.Draw(img, "RGBA")
    # blueprint fragments, clipped near edges (outside the content safe zone)
    bp1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    blueprint(bp1, (300, 640, 440, 900))
    blueprint(bp1, (24, 60, 150, 210))
    img = Image.alpha_composite(img, Image.composite(bp1, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    d = ImageDraw.Draw(img, "RGBA")
    # royal-blue structural pieces: top-left corner shard + thin angular rules
    d.polygon([(10, 10), (168, 4), (132, 74), (18, 86)], fill=ROYAL + (255,))
    d.polygon([(10, 10), (60, 8), (44, 40), (14, 44)], fill=NAVY + (255,))
    d.line([(300, 30), (452, 22)], fill=ROYAL + (255,), width=3)
    d.line([(306, 40), (448, 33)], fill=ROYAL + (110,), width=2)
    # halftone edges: right side fading left, bottom fading up (kept clear
    # of the content safe zone x50..430)
    halftone(img, (392, 120, 470, 900), ROYAL, spacing=10, max_r=3.6, fade="right", alpha_max=60)
    halftone(img, (40, 810, 440, 936), ROYAL, fade="down", alpha_max=70)
    # small yellow corner tick, bottom-left
    d.polygon([(30, 892), (64, 888), (40, 916)], fill=YELLOW + (255,))
    img.save(os.path.join(ART, "lib_panel.png"))
    print("panel", img.size)

# --------------------------------------------- marquee contrast shard ---
# Dark navy angular shard behind the dynamic marquee (contrast the marquee
# itself requires), torn edges + halftone + yellow strike along bottom.
def gen_marquee_back():
    W, H = 440, 220
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    poly = [(10, 8), (418, 0), (436, 44), (408, 170), (428, 212),
            (24, 206), (4, 158), (16, 62)]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 6, y + 8) for x, y in poly], fill=(6, 14, 44, 120))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(img, "RGBA").polygon(poly, fill=NAVY + (245,))
    halftone(img, (300, 10, 436, 120), WHITE, spacing=8, max_r=3.4, fade="right", alpha_max=46)
    blueprint(img, (18, 120, 150, 205), color=(120, 150, 255), step=12, alpha=34)
    d = ImageDraw.Draw(img, "RGBA")
    # thin yellow strike along the bottom edge (angled)
    d.polygon([(24, 196), (400, 188), (398, 198), (22, 206)], fill=YELLOW + (255,))
    img.save(os.path.join(ART, "lib_marquee_back.png"))
    print("marquee_back", img.size)

# ------------------------------------------------------- yellow strike ---
def gen_strike():
    W, H = 160, 12
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(img, "RGBA").polygon([(0, 10), (150, 0), (160, 2), (10, 12)], fill=YELLOW + (255,))
    img.save(os.path.join(ART, "lib_strike_yellow.png"))
    print("strike", img.size)

# ------------------------------------------------- screenshot frame ---
# Angular/asymmetric print frame for the 380x214 screenshot (shot at 10,10
# inside this 400x234 frame): offset white shard, blue pinstripe, yellow
# corner tick, soft baked shadow. No rounded mobile-card styling.
def gen_shot_frame():
    W, H = 400, 234
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    outer = [(2, 10), (390, 0), (399, 26), (393, 196), (398, 233),
             (8, 226), (0, 188)]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 9, y + 11) for x, y in outer], fill=(6, 14, 44, 125))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(outer, fill=WHITE + (255,))
    # punch the window the screenshot shows through (screenshot is z20 below)
    d.rectangle([10, 10, 390, 224], fill=(0, 0, 0, 0))
    # thin royal-blue pinstripe along the top edge
    d.polygon([(2, 10), (390, 0), (388, 7), (4, 17)], fill=ROYAL + (255,))
    # blue offset block bottom-right (print-stack feel)
    d.polygon([(398, 233), (398, 214), (372, 218), (376, 233)], fill=ROYAL + (255,))
    # small yellow corner tick top-right
    d.polygon([(368, 2), (392, 0), (380, 18)], fill=YELLOW + (255,))
    # faint halftone on the bottom white lip
    halftone(img, (30, 224, 360, 234), ROYAL, spacing=7, max_r=2.6, fade="down", alpha_max=60)
    img.save(os.path.join(ART, "lib_shot_frame.png"))
    print("shot_frame", img.size)

# ------------------------------------------------------------ rails ---
SYSTEMS = [
    ("dreamcast", "DREAMCAST"), ("gb", "GAME BOY"), ("gba", "GAME BOY ADVANCE"),
    ("gbc", "GAME BOY COLOR"), ("gc", "GAMECUBE"), ("genesis", "GENESIS"),
    ("megadrive", "MEGA DRIVE"), ("n3ds", "NINTENDO 3DS"), ("n64", "NINTENDO 64"),
    ("nds", "NINTENDO DS"), ("nes", "NES"), ("ps2", "PLAYSTATION 2"),
    ("psp", "PSP"), ("psx", "PLAYSTATION"), ("snes", "SNES"), ("steam", "STEAM"),
    ("wii", "WII"), ("wiiu", "WII U"), ("windows", "WINDOWS"), ("xbox", "XBOX"),
    ("xbox360", "XBOX 360"),
]
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def tracked_text(name, font, tracking):
    widths = []
    for ch in name:
        b = font.getbbox(ch)
        widths.append(b[2] - b[0])
    total = sum(widths) + tracking * (len(name) - 1)
    asc, desc = font.getmetrics()
    th = asc + desc
    img = Image.new("RGBA", (int(total) + 4, th + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = 2
    for ch, w in zip(name, widths):
        d.text((x, 2), ch, font=font, fill=(255, 255, 255, 255))
        x += w + tracking
    return img

def gen_rail(system, name):
    W, H = 76, 912
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # royal-blue body with an irregular (zigzag) right edge, drawn scanline
    # by scanline so the zigzag is baked in
    top = (32, 84, 208, 255)
    bot = (12, 40, 140, 255)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / (H - 1)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(4))
        phase = (y // 28) % 2
        xr = W - (5 if phase else 1)
        dd.line([(0, y), (xr, y)], fill=col)
    d = ImageDraw.Draw(img, "RGBA")
    # thin yellow strike: angled segments with breaks (not a full spine)
    for y0, y1 in [(36, 220), (260, 420), (470, 640), (690, 876)]:
        d.polygon([(2, y0), (7, y0 + 6), (7, y1), (2, y1 - 6)], fill=YELLOW + (255,))
    # halftone fields top/bottom
    halftone(img, (10, 8, 70, 90), WHITE, spacing=7, max_r=3.0, fade="down", alpha_max=50)
    halftone(img, (10, 822, 70, 904), WHITE, spacing=7, max_r=3.0, fade="up", alpha_max=50)
    # faint blueprint patch mid-strip
    blueprint(img, (14, 430, 62, 520), color=(140, 170, 255), step=10, alpha=26)
    # branding: supplied logo rotated CCW with a white sticker-offset behind it
    logo_path = os.path.join(LOGOS, f"{system}.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        rot = logo.rotate(90, expand=True)
        rw, rh = rot.size
        scale = min(58.0 / rw, 700.0 / rh)
        rot = rot.resize((max(1, int(rw * scale)), max(1, int(rh * scale))), Image.LANCZOS)
        ox, oy = (W - rot.width) // 2 + 4, (H - rot.height) // 2
        white = Image.new("RGBA", rot.size, WHITE + (255,))
        white.putalpha(rot.split()[3])
        img.alpha_composite(white, (ox + 3, oy + 3))
        img.alpha_composite(rot, (ox, oy))
    else:
        size = 44
        font = ImageFont.truetype(FB, size)
        tw = tracked_text(name, font, 10)
        while tw.width > 700 and size > 20:
            size -= 2
            font = ImageFont.truetype(FB, size)
            tw = tracked_text(name, font, 10)
        vert = tw.rotate(90, expand=True)
        ox, oy = (W - vert.width) // 2 + 4, (H - vert.height) // 2
        shade = Image.new("RGBA", vert.size, DEEP + (255,))
        shade.putalpha(vert.split()[3])
        img.alpha_composite(shade, (ox + 3, oy + 3))
        img.alpha_composite(vert, (ox, oy))
    img.save(os.path.join(RAILS, f"{system}.png"))
    return "logo" if os.path.exists(logo_path) else "TEXT-FALLBACK"

# --------------------------------------------- hero elevation ---
# Restrained royal-blue atmospheric glow (tighter + subtler than v9),
# soft contact shadow, and a very thin yellow arc catching only the
# upper-left of the hero silhouette. No yellow halo.
def gen_hero_blue():
    W, H = 640, 576
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy, R = W / 2, H / 2, 300
    for r in range(int(R), 0, -2):
        t = r / R
        a = int(64 * (1 - t) ** 1.6)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 96, 220, a))
    img.save(os.path.join(ART, "lib_glow_blue.png"))
    print("hero_blue", img.size)

def gen_hero_shadow():
    W, H = 560, 52
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([30, 6, W - 30, H - 6], fill=(8, 16, 52, 105))
    img = img.filter(ImageFilter.GaussianBlur(10))
    img.save(os.path.join(ART, "lib_shadow_soft.png"))
    print("hero_shadow", img.size)

def gen_hero_arc():
    # thin gold arc hugging the 520px hero (r260) at its upper-left only
    S = 560
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    c, R = S / 2, 268
    box = [c - R, c - R, c + R, c + R]
    # soft under-glow for the arc
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow, "RGBA").arc(box, start=206, end=260, fill=YELLOW + (70,), width=14)
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(img, "RGBA")
    d.arc(box, start=208, end=258, fill=YELLOW + (255,), width=5)
    # tiny secondary tick, lower-right, even thinner
    d.arc(box, start=38, end=54, fill=YELLOW + (220,), width=3)
    img.save(os.path.join(ART, "lib_hero_arc.png"))
    print("hero_arc", img.size)

# --------------------------------------------- bottom gradient ---
def gen_bottom_gradient():
    W, H = 1280, 270
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = (y / (H - 1)) ** 1.4
        d.line([(0, y), (W, y)], fill=(8, 20, 80, int(150 * t)))
    img.save(os.path.join(ART, "lib_bottom_gradient.png"))
    print("bottom_gradient", img.size)

if __name__ == "__main__":
    gen_panel()
    gen_marquee_back()
    gen_strike()
    gen_shot_frame()
    missing = []
    for system, name in SYSTEMS:
        if gen_rail(system, name) != "logo":
            missing.append(system)
    print("rails: 21 | text fallback:", missing if missing else "none")
    gen_hero_blue()
    gen_hero_shadow()
    gen_hero_arc()
    gen_bottom_gradient()
    # the v9 yellow halo is retired by this art direction
    halo = os.path.join(ART, "lib_glow_yellow.png")
    if os.path.exists(halo):
        os.remove(halo)
        print("retired lib_glow_yellow.png")
