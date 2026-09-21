#!/usr/bin/env python3
"""Crystal v17.6.0 asset generation: VISUAL MATURITY PASS on the locked
gamelist macro geometry (positions/sizes byte-identical to v17.5.0).

HARD SCOPES (non-negotiable):
- PHYSICAL MEDIA AND FALLBACK ART ARE OUT OF SCOPE. This script touches
  ONLY: lib_panel_main.png, art/rails/*.png (21), art/lib_title_rule.png,
  art/star_filled.png (yellow->royal recolor: rating is a small supporting
  indicator, not a yellow block). It does NOT touch media_fallbacks/*,
  lib_shadow_soft.png, lib_glow_blue.png, lib_plane_hero.png,
  lib_shard_prev/next.png, fonts (handled separately), or
  gamelist_generic_bg.png (all stay byte-identical to v17.5.0).
- PermanentMarker is gone everywhere: all baked panel type is
  DejaVuSans-Bold (tracked micro labels) / DejaVuSans (regular).

What changes (maturity only, no geometry):
1. TYPOGRAPHY: baked kickers in DejaVuSans-Bold tracked micro, quieter
   slate. No brush lettering anywhere on the shell.
2. YELLOW BUDGET: masthead keeps ONE tiny registration square; the
   rule at 425 loses its yellow square (plain rule); the screenshot keeps
   its ONE tiny registration corner; the yellow triangle at NOW SHOWING,
   the intrusion + its yellow leading edges, and the two micro ticks are
   DELETED. Title rule shrinks to one thin subtle rule (no end ticks).
   Spine keeps ONE thin 1px continuous yellow line (tab deleted).
3. LEFT PAGE: the blueprint fragment and the blue geometric intrusion are
   DELETED. One whisper-quiet halftone transition at the angular right
   edge is the single remaining halftone area. Open whitespace, sparse
   rules, generous alignment.
4. SPINE: deeper solid royal foundation, dotgrid further reduced
   (spacing 32, alpha 4 - one subtle area maximum), logo plate without
   the white outline (quieter mounting), one thin yellow line.
5. RATING STAR: filled star recolored yellow -> royal blue.
"""
import os, sys, json
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.expanduser("~/workspace/crystal-esde-theme/work"))
from gen_v15_assets import (halftone, dotgrid, grain, tracked_text_img,
                            tracked_text_v15, SYSTEMS, ROYAL, DEEP, NAVY,
                            INKDIM, YELLOW, WHITE, FB)
from PIL import ImageFilter

ART = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal/art")
RAILS = os.path.join(ART, "rails")
LOGOS = os.path.join(ART, "console_logos")
SLATE = (126, 138, 166)


# ----------------- the editorial left page (one composition) ------------
# 470x940, local coords (global origin 6,10). SAME angular white module
# silhouette (footprint locked). Marquee zone local (18,34)-(442,286)
# stays open white - no box, no frame, no container.
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
    ImageDraw.Draw(body).polygon(poly, fill=WHITE + (255,))
    d = ImageDraw.Draw(body, "RGBA")

    # crisp 1px light edge along the page's top edge (paper sharpness)
    d.line([(34, 1), (388, 1)], fill=WHITE + (130,), width=1)

    # ---- MARQUEE MASTHEAD: open white zone, designed anchor ----
    # tiny kicker, quieter than v17.5 (9px, alpha 130). NO yellow
    # triangle (decorative shape with no informational purpose).
    # The whisper royal hairline BELOW the marquee zone (local y=294)
    # with ONE tiny yellow registration square is the masthead baseline.
    kick = tracked_text_img("NOW SHOWING", 9, ROYAL, 4, alpha=130)
    body.alpha_composite(kick, (46, 12))
    d.line([(36, 294), (434, 294)], fill=ROYAL + (70,), width=1)
    d.rectangle([(36, 292), (42, 296)], fill=YELLOW + (200,))

    # the ONE structural rule: between description and facts. Plain now -
    # the v17.5 yellow square is deleted (yellow budget).
    d.line([(36, 425), (434, 425)], fill=ROYAL + (90,), width=1)

    # baked kickers: DejaVuSans-Bold tracked micro, quieter slate;
    # optically aligned to the value boxes (same x as the XML elements
    # they label). Brush lettering is gone everywhere.
    for text, xy in [("RELEASED", (42, 446)), ("RATING", (290, 446)),
                     ("GENRE", (42, 538)), ("PLAYERS", (42, 598)),
                     ("DEVELOPER", (234, 598)), ("SCREENSHOT", (36, 658))]:
        k = tracked_text_img(text, 9, SLATE, 4, alpha=130)
        body.alpha_composite(k, xy)

    # ---- SCREENSHOT: media, not a form field ----
    # no border box. One clean bottom-edge hairline, subtle depth, ONE
    # tiny yellow registration-mark corner crossing the screenshot's
    # top-right corner (screenshot element local box: (36,690)-(432,900)).
    fsh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fsh).rectangle([38, 694, 434, 902], fill=(6, 14, 44, 30))
    body = Image.alpha_composite(body, fsh.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(body, "RGBA")
    d.line([(36, 900), (432, 900)], fill=ROYAL + (110,), width=1)
    d.line([(424, 682), (424, 696)], fill=YELLOW + (220,), width=2)
    d.line([(424, 682), (438, 682)], fill=YELLOW + (220,), width=2)

    # --- one quiet graphic gesture only ---
    # a whisper of halftone fading into the page's angular right edge -
    # the single remaining halftone area. The v17.5 blueprint fragment,
    # the blue geometric intrusion, its yellow leading edges, and the two
    # yellow micro ticks are all DELETED.
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (430, 340, 458, 560), ROYAL, spacing=10, max_r=2.4,
             fade="left", alpha_max=22)

    body = Image.composite(body, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
    body = grain(body, mask)
    img = Image.alpha_composite(img, body)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    p = os.path.join(ART, "lib_panel_main.png")
    img.save(p)
    print("lib_panel_main.png", img.size)


# ------------------------------------------------- the console spine ---
# 60x912: DEEP SOLID royal-blue foundation, dotgrid further reduced
# (spacing 32, alpha 4 - the one subtle area maximum), ONE thin 1px
# continuous yellow structural line (the v17.5 top tab is deleted),
# supplied logos mounted with real breathing room (plate without the
# white outline - quieter). Premium publication spine.
RAIL_PARAMS = {}

def gen_rail(system, name):
    W, H = 60, 912
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    poly = [(0, 0), (42, 0), (60, 18), (60, 912), (18, 912), (0, 894)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    top = (20, 60, 168, 255)
    bot = (8, 30, 108, 255)
    dd = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / (H - 1)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(4))
        dd.line([(0, y), (W, y)], fill=col)
    # tonal variation: a softly lighter centre band within the royal blue
    tone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tone, "RGBA")
    for x in range(W):
        t = 1 - abs(x - W / 2) / (W / 2)
        td.line([(x, 0), (x, H)], fill=(110, 150, 250, int(18 * t)))
    img = Image.alpha_composite(img, Image.composite(tone, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    # dotgrid further reduced vs v17.5 (24px/alpha 7 -> 32px/alpha 4):
    # the ONE subtle texture area on the spine
    dotgrid(img, (6, 30, 54, 882), alpha=4, spacing=32)
    d = ImageDraw.Draw(img, "RGBA")
    # subtle inner edge, right side
    d.line([(54, 26), (54, 886)], fill=NAVY + (90,), width=1)

    # the branding, deliberately MOUNTED with real breathing room:
    # plate padding 22 per side, logo max length 560. Plate is quieter
    # than v17.5: fill only, no white outline.
    logo_path = os.path.join(LOGOS, f"{system}.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        rot = logo.rotate(90, expand=True)
        rw, rh = rot.size
        scale = min(36.0 / rw, 560.0 / rh)
        rot = rot.resize((max(1, int(rw * scale)), max(1, int(rh * scale))), Image.LANCZOS)
        ox, oy = (W - rot.width) // 2 + 2, (H - rot.height) // 2
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
                                   pad=pad, kind="logo")
        kind = "logo"
    else:
        size = 36
        font = ImageFont.truetype(FB, size)
        tw = tracked_text_v15(name, font, 8)
        while tw.width > 560 and size > 18:
            size -= 2
            font = ImageFont.truetype(FB, size)
            tw = tracked_text_v15(name, font, 8)
        vert = tw.rotate(90, expand=True)
        ox, oy = (W - vert.width) // 2 + 2, (H - vert.height) // 2
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
                                   pad=pad, kind="TEXT-FALLBACK")
        kind = "TEXT-FALLBACK"
    # ONE thin continuous yellow structural line, 1px (the v17.5 top tab
    # is deleted)
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(4, 44), (4, 888)], fill=YELLOW + (255,), width=1)
    img = Image.composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
    img.save(os.path.join(RAILS, f"{system}.png"))
    return kind


# --------------------------------- the game-identity pedestal rule ---
# lib_title_rule.png (300x10): ONE subtle thin yellow rule - a centered
# 120px bar, 2px tall, alpha 200. The v17.5 end-ticks are deleted.
def gen_title_rule():
    W, H = 300, 10
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([(90, 4), (210, 6)], fill=YELLOW + (200,))
    p = os.path.join(ART, "lib_title_rule.png")
    img.save(p)
    print("lib_title_rule.png", img.size)


# --------------------------------- the rating star (recolor) ----------
# star_filled.png 64x64: the filled star was solid yellow - a loud block
# on the quiet page. Recolored to royal blue: the rating is a small
# supporting indicator. Geometry (star path, white edge, 64x64 canvas)
# unchanged.
def gen_star_filled():
    import math
    S = 64
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cx, cy = S / 2, S / 2 + 2
    pts = []
    for k in range(10):
        r = 24 if k % 2 == 0 else 10
        a = -math.pi / 2 + k * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(pts, fill=ROYAL + (255,), outline=WHITE + (255,))
    p = os.path.join(ART, "star_filled.png")
    img.save(p)
    print("star_filled.png", img.size)


if __name__ == "__main__":
    gen_panel()
    gen_title_rule()
    gen_star_filled()
    kinds = {}
    for system, name in SYSTEMS:
        kind = gen_rail(system, name)
        kinds[kind] = kinds.get(kind, 0) + 1
    print("rails:", kinds)
    with open(os.path.expanduser("~/workspace/crystal-esde-theme/work/rail_params_v17_6.json"), "w") as f:
        json.dump(RAIL_PARAMS, f, indent=1)
    print("rail params -> work/rail_params_v17_6.json")
