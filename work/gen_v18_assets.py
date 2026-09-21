#!/usr/bin/env python3
"""v18.0.0 art-direction pass: regenerate shell assets.

ONLY:
  1. art/lib_plane_hero.png - the old 420x360 asset read as a pale
     RECTANGLE behind the hero ("asset box"). Replaced with a 900x900
     fully-feathered radial wash (no edges at all): the hero reads as
     suspended over the Nova environment with subtle local contrast.
  2. art/rails/*.png (21) - the spine read as a blue bar SPLITTING the
     layout. Changes: left/right edges feathered 6px so the bar melts
     into the panel and the stage (binds instead of splits); dotgrid
     further reduced (48px/a2 -> 64px/a1); logo presence 44x680 -> 48x720
     (still optically lifted 6px); the 1px yellow structural line moved
     x=4 -> x=8 so it stays crisp outside the feather zone.

Fallback media, hero rendering, marquee/screenshot bindings: untouched.
"""
import os, sys, json, math
from PIL import Image, ImageDraw, ImageFont, ImageChops

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
sys.path.insert(0, os.path.join(REPO, "work"))
from gen_v15_assets import (ROYAL, DEEP, NAVY, INKDIM, YELLOW, WHITE,
                            SYSTEMS, dotgrid, tracked_text_v15)

ART = os.path.join(REPO, "theme-src/crystal/art")
RAILS = os.path.join(ART, "rails")
LOGOS = os.path.join(ART, "console_logos")
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# --------------------------------- hero plane ---------------------------
# 900x900 radial wash: cool white-blue, centre alpha 26, cosine falloff
# to 0 at the rim. NO rectangular footprint - the stage keeps the Nova
# background visible everywhere.
def gen_plane():
    S = 900
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    px = img.load()
    c = S / 2
    for y in range(S):
        for x in range(S):
            r = math.hypot(x - c, y - c) / c
            if r >= 1:
                continue
            a = 18 * (0.5 + 0.5 * math.cos(r * math.pi))
            px[x, y] = (214, 226, 248, int(a))
    img = img.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(18))
    p = os.path.join(ART, "lib_plane_hero.png")
    img.save(p)
    print("lib_plane_hero.png", img.size)

# --------------------------------- spine rails --------------------------
RAIL_PARAMS = {}

def gen_rail(system, name):
    W, H = 60, 912
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    poly = [(0, 0), (42, 0), (60, 18), (60, 912), (18, 912), (0, 894)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    # feather the left/right edges (6px) so the bar melts into the panel
    # (left) and the stage (right): it BINDS the page instead of splitting
    # it. The feather is a horizontal ramp multiplied into the mask.
    ramp = Image.new("L", (W, 1), 0)
    rp = ramp.load()
    for x in range(W):
        rp[x, 0] = int(255 * min(x, W - 1 - x, 6) / 6)
    ramp = ramp.resize((W, H))
    mask = ImageChops.multiply(mask, ramp)
    top = (20, 60, 168, 255)
    bot = (8, 30, 108, 255)
    dd = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / (H - 1)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(4))
        dd.line([(0, y), (W, y)], fill=col)
    tone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tone, "RGBA")
    for x in range(W):
        t = 1 - abs(x - W / 2) / (W / 2)
        td.line([(x, 0), (x, H)], fill=(110, 150, 250, int(18 * t)))
    img = Image.alpha_composite(img, Image.composite(tone, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    # texture: the last whisper of dotgrid (64px / alpha 1)
    dotgrid(img, (8, 30, 52, 882), alpha=1, spacing=64)
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(52, 26), (52, 886)], fill=NAVY + (90,), width=1)

    OPTICAL_LIFT = 6
    logo_path = os.path.join(LOGOS, f"{system}.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        rot = logo.rotate(90, expand=True)
        rw, rh = rot.size
        scale = min(48.0 / rw, 720.0 / rh)
        rot = rot.resize((max(1, int(rw * scale)), max(1, int(rh * scale))), Image.LANCZOS)
        ox, oy = (W - rot.width) // 2 + 2, (H - rot.height) // 2 - OPTICAL_LIFT
        pad = 22
        plate = Image.new("RGBA", (rot.width + pad * 2, rot.height + pad * 2), (0, 0, 0, 0))
        pd = ImageDraw.Draw(plate, "RGBA")
        pd.rounded_rectangle([0, 0, plate.width, plate.height], radius=8,
                             fill=(8, 20, 70, 60))
        img.alpha_composite(plate, (ox - pad, oy - pad))
        white = Image.new("RGBA", rot.size, WHITE + (255,))
        white.putalpha(rot.split()[3])
        img.alpha_composite(white, (ox + 2, oy + 2))
        img.alpha_composite(rot, (ox, oy))
        RAIL_PARAMS[system] = dict(logo=(rot.width, rot.height), plate=(plate.width, plate.height),
                                   pad=pad, optical_lift=OPTICAL_LIFT, kind="logo")
        kind = "logo"
    else:
        size = 36
        font = ImageFont.truetype(FB, size)
        tw = tracked_text_v15(name, font, 8)
        while tw.width > 720 and size > 18:
            size -= 2
            font = ImageFont.truetype(FB, size)
            tw = tracked_text_v15(name, font, 8)
        vert = tw.rotate(90, expand=True)
        ox, oy = (W - vert.width) // 2 + 2, (H - vert.height) // 2 - OPTICAL_LIFT
        pad = 22
        plate = Image.new("RGBA", (vert.width + pad * 2, vert.height + pad * 2), (0, 0, 0, 0))
        pd = ImageDraw.Draw(plate, "RGBA")
        pd.rounded_rectangle([0, 0, plate.width, plate.height], radius=8,
                             fill=(8, 20, 70, 60))
        img.alpha_composite(plate, (ox - pad, oy - pad))
        shade = Image.new("RGBA", vert.size, NAVY + (255,))
        shade.putalpha(vert.split()[3])
        img.alpha_composite(shade, (ox + 2, oy + 2))
        img.alpha_composite(vert, (ox, oy))
        RAIL_PARAMS[system] = dict(logo=(vert.width, vert.height), plate=(plate.width, plate.height),
                                   pad=pad, optical_lift=OPTICAL_LIFT, kind="TEXT-FALLBACK")
        kind = "TEXT-FALLBACK"
    # ONE thin continuous yellow structural line - at x=8, crisp outside
    # the 6px feather zone (was x=4, which would have faded).
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(8, 44), (8, 888)], fill=YELLOW + (255,), width=1)
    img = Image.composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
    img.save(os.path.join(RAILS, f"{system}.png"))
    return kind


if __name__ == "__main__":
    gen_plane()
    kinds = {}
    for system, name in SYSTEMS:
        kind = gen_rail(system, name)
        kinds[kind] = kinds.get(kind, 0) + 1
    print("rails:", kinds)
    with open(os.path.join(REPO, "work/rail_params_v18.json"), "w") as f:
        json.dump(RAIL_PARAMS, f, indent=1)
    print("rail params -> work/rail_params_v18.json")
