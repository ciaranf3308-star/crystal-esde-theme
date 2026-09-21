#!/usr/bin/env python3
"""Crystal v9.0.0 asset generation: left panel, screenshot frame, console rails, hero ring."""
import math, os
from PIL import Image, ImageDraw, ImageFont

ART = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal/art")
RAILS = os.path.join(ART, "rails")
os.makedirs(RAILS, exist_ok=True)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
YELLOW = (255, 214, 10)

# ---------------------------------------------------------------- panel ---
def gen_panel():
    W, H = 480, 940
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # soft drop shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rounded_rectangle([26, 24, 470, 934], radius=30, fill=(8, 16, 40, 110))
    sh = sh.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(14))
    img = Image.alpha_composite(img, sh)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([18, 14, 462, 926], radius=30, fill=(255, 255, 255, 255),
                        outline=(226, 232, 242, 255), width=1)
    img.save(os.path.join(ART, "lib_panel.png"))
    print("panel", img.size)

# ------------------------------------------------------- screenshot frame ---
def gen_shot_frame():
    W, H = 380, 214
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=18, fill=(255, 255, 255, 255))
    d.rounded_rectangle([4, 4, W - 5, H - 5], radius=14, fill=(255, 255, 255, 0))
    d.rounded_rectangle([1, 1, W - 2, H - 2], radius=17, outline=(217, 224, 236, 255), width=3)
    img.save(os.path.join(ART, "lib_shot_frame.png"))
    print("shot frame", img.size)

# ------------------------------------------------------------------ rails ---
SYSTEMS = [
    ("dreamcast", "DREAMCAST"), ("gb", "GAME BOY"), ("gba", "GAME BOY ADVANCE"),
    ("gbc", "GAME BOY COLOR"), ("gc", "GAMECUBE"), ("genesis", "GENESIS"),
    ("megadrive", "MEGA DRIVE"), ("n3ds", "NINTENDO 3DS"), ("n64", "NINTENDO 64"),
    ("nds", "NINTENDO DS"), ("nes", "NES"), ("ps2", "PLAYSTATION 2"),
    ("psp", "PSP"), ("psx", "PLAYSTATION"), ("snes", "SNES"), ("steam", "STEAM"),
    ("wii", "WII"), ("wiiu", "WII U"), ("windows", "WINDOWS"), ("xbox", "XBOX"),
    ("xbox360", "XBOX 360"),
]

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
    # vertical navy gradient, near-opaque
    top = (24, 38, 88, 245)
    bot = (10, 18, 50, 245)
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        t = y / (H - 1)
        gd.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(4)))
    img = Image.alpha_composite(img, grad)
    d = ImageDraw.Draw(img)
    # yellow spine
    d.rectangle([0, 0, 6, H], fill=YELLOW + (255,))
    # faint right edge
    d.rectangle([W - 1, 0, W - 1, H], fill=(255, 255, 255, 36))
    # yellow diamonds top/bottom
    for cy in (30, H - 30):
        s = 9
        d.polygon([(41, cy - s), (41 + s, cy), (41, cy + s), (41 - s, cy)], fill=YELLOW + (255,))
    # vertical name, reads bottom-to-top
    size = 46
    font = ImageFont.truetype(FB, size)
    tw = tracked_text(name, font, 10)
    while tw.width > 780 and size > 20:
        size -= 2
        font = ImageFont.truetype(FB, size)
        tw = tracked_text(name, font, 10)
    vert = tw.rotate(90, expand=True)  # CCW -> reads bottom to top
    img.alpha_composite(vert, ((W - vert.width) // 2 + 3, (H - vert.height) // 2))
    img.save(os.path.join(RAILS, f"{system}.png"))

# ------------------------------------------------------------- hero ring ---
def gen_ring():
    S = 640
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    px = img.load()
    c = S / 2
    for y in range(S):
        for x in range(S):
            r = math.hypot(x - c + 0.5, y - c + 0.5)
            a = 0.0
            if r < 260:
                a = 0.0
            elif r < 270:
                a = 230 * (r - 260) / 10
            elif r < 278:
                a = 230.0
            elif r < 306:
                a = 230 * (1 - (r - 278) / 28)
            if a > 0:
                px[x, y] = (255, 214, 10, int(a))
    img.save(os.path.join(ART, "lib_glow_yellow.png"))
    print("ring", img.size, "core r260 for 520px disk")

if __name__ == "__main__":
    gen_panel()
    gen_shot_frame()
    for system, name in SYSTEMS:
        gen_rail(system, name)
    print("rails:", len(SYSTEMS))
    gen_ring()
