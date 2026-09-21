#!/usr/bin/env python3
"""Crystal v17.5.0 asset generation: UI-SHELL finish pass on the LOCKED
gamelist macro geometry (positions/sizes byte-identical to v17.4.0).

HARD SCOPES (user's explicit order):
- PHYSICAL MEDIA AND FALLBACK ART ARE OUT OF SCOPE. This script touches
  ONLY: lib_panel_main.png, art/rails/*.png (21), art/lib_title_rule.png.
  It does NOT regenerate media_fallbacks/*, lib_shadow_soft.png,
  lib_glow_blue.png, lib_plane_hero.png, lib_shard_prev/next.png, fonts,
  or gamelist_generic_bg.png (all stay byte-identical to v17.4.0).
- The hero/marquee/screenshot are immutable live asset slots in the theme.

What changes (finish only, no geometry):
1. MARQUEE MASTHEAD: the open-white zone gains a designed masthead
   anchor - a whisper royal hairline below the zone with a yellow
   registration square, so the zone reads as a magazine masthead, not an
   empty white box. NOW SHOWING kicker smaller, wider-tracked, quieter.
2. TYPESET: baked kickers smaller (10px), wider tracking (4), quieter
   slate; the single description/facts hairline stays the only rule.
3. SCREENSHOT: registration-mark corner now CROSSES the screenshot's
   top-right corner; the intrusion's yellow leading edge extends down to
   meet it - one graphic gesture, slight editorial intersection.
4. SPINE: halftone mid-band REMOVED (one subtle area maximum: the sparse
   dotgrid), dotgrid sparser still (24px, alpha 7), deeper royal
   foundation. Yellow line + tab kept; logo plate breathing room kept.
5. TITLE RULE: redesigned as ONE clean yellow registration rule (no
   white hairline): centered 140px bar + tiny registration end-ticks.

Macro geometry untouched. System-view cards untouched."""
import os, sys, json
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.expanduser("~/workspace/crystal-esde-theme/work"))
from gen_v15_assets import (halftone, blueprint, dotgrid, grain,
                            tracked_text_img, SYSTEMS, tracked_text_v15,
                            ROYAL, DEEP, NAVY, INKDIM, YELLOW, WHITE, FB)
from PIL import ImageFilter

ART = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal/art")
RAILS = os.path.join(ART, "rails")
LOGOS = os.path.join(ART, "console_logos")
SLATE = (126, 138, 166)


# ----------------- the editorial left page (one composition) ---
# 470x940, local coords (global origin 6,10). SAME angular white module
# silhouette (footprint locked). Marquee zone local (18,34)-(442,286)
# stays open white - no box, no frame.
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
    # tiny kicker + yellow tick (quieter than v17.4), then a whisper
    # royal hairline BELOW the marquee zone (local y=294; the zone ends
    # at local 286, desc starts at local 302) with a yellow registration
    # square - the masthead baseline. The real scraped marquee mounts
    # above it on generous negative space.
    kick = tracked_text_img("NOW SHOWING", 10, ROYAL, 4, alpha=150)
    body.alpha_composite(kick, (46, 12))
    d.polygon([(28, 10), (35, 10), (28, 17)], fill=YELLOW + (255,))
    d.line([(36, 294), (434, 294)], fill=ROYAL + (70,), width=1)
    d.rectangle([(36, 292), (42, 296)], fill=YELLOW + (200,))

    # the ONE structural rule: between description and facts
    d.line([(36, 425), (434, 425)], fill=ROYAL + (90,), width=1)
    d.rectangle([(36, 423), (42, 427)], fill=YELLOW + (220,))

    # baked kickers: smaller, wider-tracked, quieter slate; optically
    # aligned to the value boxes (same x as the XML elements they label)
    for text, xy in [("RELEASED", (42, 446)), ("RATING", (290, 446)),
                     ("GENRE", (42, 538)), ("PLAYERS", (42, 598)),
                     ("DEVELOPER", (234, 598)), ("SCREENSHOT", (36, 658))]:
        k = tracked_text_img(text, 10, SLATE, 4, alpha=135)
        body.alpha_composite(k, xy)

    # ---- SCREENSHOT: media, not a form field ----
    # no border box. One clean bottom-edge hairline, subtle depth, ONE
    # tiny yellow registration-mark corner that CROSSES the screenshot's
    # top-right corner (screenshot element local box: (36,690)-(432,900)).
    fsh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fsh).rectangle([38, 694, 434, 902], fill=(6, 14, 44, 30))
    body = Image.alpha_composite(body, fsh.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(body, "RGBA")
    d.line([(36, 900), (432, 900)], fill=ROYAL + (110,), width=1)
    d.line([(424, 682), (424, 704)], fill=YELLOW + (220,), width=2)
    d.line([(424, 682), (446, 682)], fill=YELLOW + (220,), width=2)

    # --- restrained Nova craftsmanship ---
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # tiny halftone transition melting into the intrusion's leading edge
    halftone(deco, (398, 340, 420, 520), ROYAL, spacing=8, max_r=3.0,
             fade="left", alpha_max=34)
    # ONE subtle blueprint fragment (whisper-quiet, behind the facts)
    blueprint(deco, (340, 560, 460, 690), color=(16, 52, 160), step=15, alpha=16)
    # ONE clipped blue geometric intrusion: slimmer and lighter than v17,
    # hugging the page's angular right edge, hairline yellow leading edge.
    # v17.5: the yellow leading edge EXTENDS down past the intrusion to
    # meet the screenshot's registration corner - one continuous graphic
    # gesture (slight editorial intersection, controlled overlap).
    dd = ImageDraw.Draw(deco, "RGBA")
    dd.polygon([(422, 340), (445, 326), (446, 600), (422, 600)],
               fill=ROYAL + (130,))
    dd.line([(422, 340), (422, 600)], fill=YELLOW + (110,), width=1)
    dd.line([(422, 600), (422, 684)], fill=YELLOW + (90,), width=1)
    # sparse yellow micro-accents: two tiny ticks, nothing more
    dd.rectangle([(36, 908), (44, 916)], fill=YELLOW + (220,))
    dd.rectangle([(424, 648), (426, 662)], fill=YELLOW + (220,))

    body = Image.composite(body, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
    body = grain(body, mask)
    img = Image.alpha_composite(img, body)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    p = os.path.join(ART, "lib_panel_main.png")
    img.save(p)
    print("lib_panel_main.png", img.size)


# ------------------------------------------------- the console spine ---
# 60x912: deep royal-blue foundation (deeper, calmer gradient), NO
# halftone mid-band (one subtle area maximum: the sparse dotgrid),
# dotgrid sparser still (24px, alpha 7), ONE continuous thin yellow
# structural line + top tab, supplied logos MOUNTED with real breathing
# room. Premium publication spine, not a patterned separator.
RAIL_PARAMS = {}

def gen_rail(system, name):
    W, H = 60, 912
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    poly = [(0, 0), (42, 0), (60, 18), (60, 912), (18, 912), (0, 894)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    top = (26, 72, 186, 255)
    bot = (10, 34, 120, 255)
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
        td.line([(x, 0), (x, H)], fill=(110, 150, 250, int(22 * t)))
    img = Image.alpha_composite(img, Image.composite(tone, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    # controlled grid texture, sparser still than v17.4: spacing 24, alpha 7
    dotgrid(img, (6, 30, 54, 882), alpha=7, spacing=24)
    # (v17.5: the halftone mid-band is REMOVED - one subtle area maximum)
    d = ImageDraw.Draw(img, "RGBA")
    # subtle inner edge, right side
    d.line([(54, 26), (54, 886)], fill=NAVY + (110,), width=1)

    # the branding, deliberately MOUNTED with real breathing room:
    # plate padding 22 per side, logo max length 560
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
        pd.rounded_rectangle([0, 0, plate.width - 1, plate.height - 1], radius=8,
                             outline=(255, 255, 255, 30), width=1)
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
        pd.rounded_rectangle([0, 0, plate.width - 1, plate.height - 1], radius=8,
                             outline=(255, 255, 255, 30), width=1)
        img.alpha_composite(plate, (ox - pad, oy - pad))
        shade = Image.new("RGBA", vert.size, NAVY + (255,))
        shade.putalpha(vert.split()[3])
        img.alpha_composite(shade, (ox + 2, oy + 2))
        img.alpha_composite(vert, (ox, oy))
        RAIL_PARAMS[system] = dict(logo=(vert.width, vert.height), plate=(plate.width, plate.height),
                                   pad=pad, kind="TEXT-FALLBACK")
        kind = "TEXT-FALLBACK"
    # ONE continuous thin yellow structural line (+ top tab)
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(4, 44), (4, 888)], fill=YELLOW + (255,), width=2)
    d.rectangle([(2, 24), (7, 44)], fill=YELLOW + (255,))
    img.save(os.path.join(RAILS, f"{system}.png"))
    return kind


# --------------------------------- the game-identity pedestal rule ---
# lib_title_rule.png (300x10): ONE clean yellow registration rule - a
# centered 140px bar, 3px tall, with tiny registration end-ticks. No
# white hairline: the yellow accent IS the visual anchor.
def gen_title_rule():
    W, H = 300, 10
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([(80, 3), (220, 6)], fill=YELLOW + (255,))
    d.rectangle([(72, 1), (74, 8)], fill=YELLOW + (255,))
    d.rectangle([(226, 1), (228, 8)], fill=YELLOW + (255,))
    p = os.path.join(ART, "lib_title_rule.png")
    img.save(p)
    print("lib_title_rule.png", img.size)


if __name__ == "__main__":
    gen_panel()
    gen_title_rule()
    kinds = {}
    for system, name in SYSTEMS:
        kind = gen_rail(system, name)
        kinds[kind] = kinds.get(kind, 0) + 1
    print("rails:", kinds)
    with open(os.path.expanduser("~/workspace/crystal-esde-theme/work/rail_params_v17_5.json"), "w") as f:
        json.dump(RAIL_PARAMS, f, indent=1)
    print("rail params -> work/rail_params_v17_5.json")
