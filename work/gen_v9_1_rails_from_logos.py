#!/usr/bin/env python3
"""Crystal v9.0.1: rebuild console rails from the user's supplied console logos,
rotated 90 deg CCW (reads bottom-to-top, matching the v9 wireframe). Same rail
chrome (navy gradient, yellow spine, diamonds) as v9.0.0; only the branding
content changes. Systems with no supplied logo keep a tracked-text fallback
until the user sends the missing marks."""
import os
from PIL import Image, ImageDraw, ImageFont

ART = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal/art")
RAILS = os.path.join(ART, "rails")
LOGOS = os.path.join(ART, "console_logos")
os.makedirs(RAILS, exist_ok=True)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
YELLOW = (255, 214, 10)

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

def rail_chrome():
    W, H = 76, 912
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    top = (24, 38, 88, 245)
    bot = (10, 18, 50, 245)
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        t = y / (H - 1)
        gd.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(4)))
    img = Image.alpha_composite(img, grad)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 6, H], fill=YELLOW + (255,))
    d.rectangle([W - 1, 0, W - 1, H], fill=(255, 255, 255, 36))
    for cy in (30, H - 30):
        s = 9
        d.polygon([(41, cy - s), (41 + s, cy), (41, cy + s), (41 - s, cy)], fill=YELLOW + (255,))
    return img

def gen_rail(system, name):
    W, H = 76, 912
    img = rail_chrome()
    logo_path = os.path.join(LOGOS, f"{system}.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        # rotate 90 CCW -> reads bottom-to-top; scale so rotated mark fits the rail
        rot = logo.rotate(90, expand=True)
        rw, rh = rot.size
        scale = min(64.0 / rw, 740.0 / rh)
        rot = rot.resize((max(1, int(rw * scale)), max(1, int(rh * scale))), Image.LANCZOS)
        img.alpha_composite(rot, ((W - rot.width) // 2 + 3, (H - rot.height) // 2))
        kind = "logo"
    else:
        size = 46
        font = ImageFont.truetype(FB, size)
        tw = tracked_text(name, font, 10)
        while tw.width > 780 and size > 20:
            size -= 2
            font = ImageFont.truetype(FB, size)
            tw = tracked_text(name, font, 10)
        vert = tw.rotate(90, expand=True)
        img.alpha_composite(vert, ((W - vert.width) // 2 + 3, (H - vert.height) // 2))
        kind = "TEXT-FALLBACK"
    img.save(os.path.join(RAILS, f"{system}.png"))
    return kind

if __name__ == "__main__":
    missing = []
    for system, name in SYSTEMS:
        kind = gen_rail(system, name)
        if kind != "logo":
            missing.append(system)
        print(f"{system:10s} {kind}")
    print("rails:", len(SYSTEMS), "| missing logos:", missing if missing else "none")
