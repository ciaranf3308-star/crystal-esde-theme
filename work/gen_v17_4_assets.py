#!/usr/bin/env python3
"""Crystal v17.4.0 asset generation: EDITORIAL SHELL pass on the LOCKED
gamelist macro layout (left column 6,10 470x940; spine 486,24 60x912;
hero 540px at 900,430; title rule Y716 / title Y736 / meta Y757;
screenshot 42,700 396x210; footer y915).

The product concept pivots: 98% of games have real scraped physicalmedia,
so the UI SHELL is the design target and fallback hero art is deliberately
plain. Per the user's 10-point brief:

1. LEFT COLUMN = ONE EDITORIAL PAGE. The navy marquee card/frame is GONE
   (the user: "STOP PUTTING IT IN A GIANT BLUE BOX"). The marquee zone is
   open white with generous negative space; the marquee's own artwork
   provides the personality. No enclosing regions: kickers + hairline +
   slimmer intrusion + whisper blueprint carry the hierarchy.
2. MARQUEE: no blue box, no platform tier (the spine says the platform).
   NOW SHOWING stays a tiny kicker. Fallback = game title (XML, unchanged).
3. TYPESET: kickers optically aligned to the value boxes (same x), quieter
   slate, consistent spacing; the hairline between description and facts
   is the ONE structural rule; players/developer stay a two-column grid.
4. SCREENSHOT: no "SCREENSHOT BOX" - no full border. One clean bottom-edge
   hairline, subtle depth, one tiny yellow registration-mark corner.
5. SPINE: dot texture cut ~55% (fewer, quieter), halftone mid-band halved,
   connector ticks removed (ONE continuous yellow line + top tab only),
   mounting plate given real breathing room (padding 14 -> 22/side).
6. HERO: unchanged assets (shadow 0.9, blue atmosphere) - the real
   physicalmedia is the spectacle. No new decoration.
7. TITLE: 0.0375 -> 0.040 (a known-shipped size) so the display title
   stands up to the media; the rule/meta rail geometry is unchanged.
8/9. Prev/next + transitions: carousel-native (itemTransitions animate is
   ES-DE's only element motion; re-verified in esde_theme_tables.json -
   no keyframes, no fades, no per-element animation exist). Nothing to add.
10. FALLBACKS: regenerated as flat muted blue-grey silhouettes - one per
   media class, deliberately plain (disc / cartridge / game card / UMD /
   mini-disc / digital). No label art, no rings, no screws, no contacts.

Macro geometry untouched. System-view cards untouched.
gamelist_generic_bg.png untouched."""
import os, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.expanduser("~/workspace/crystal-esde-theme/work"))
from gen_v15_assets import (halftone, blueprint, dotgrid, grain,
                            tracked_text_img, SYSTEMS, tracked_text_v15,
                            ROYAL, DEEP, NAVY, INKDIM, YELLOW, WHITE, FB)

ART = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal/art")
RAILS = os.path.join(ART, "rails")
LOGOS = os.path.join(ART, "console_logos")
SLATE = (126, 138, 166)


# ----------------- the editorial left page (one composition) ---
# 470x940, local coords (global origin 6,10). SAME angular white module
# silhouette (footprint locked). The marquee zone (local 18,34-442,286)
# is open white - no frame, no navy card, no platform tier.
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

    # fully opaque white: the marquee mounts on a clean page
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(body).polygon(poly, fill=WHITE + (255,))
    d = ImageDraw.Draw(body, "RGBA")

    # crisp 1px light edge along the page's top edge (paper sharpness)
    d.line([(34, 1), (388, 1)], fill=WHITE + (130,), width=1)

    # ---- MARQUEE ZONE: open white, no box, no frame ----
    # tiny editorial kicker + one yellow micro-tick; the real scraped
    # marquee lands on generous negative space (its silhouette and colour
    # provide the game personality)
    kick = tracked_text_img("NOW SHOWING", 11, ROYAL, 4, alpha=170)
    body.alpha_composite(kick, (44, 10))
    d.polygon([(28, 8), (35, 8), (28, 15)], fill=YELLOW + (255,))

    # the ONE structural rule: between description and facts
    d.line([(36, 425), (434, 425)], fill=ROYAL + (90,), width=1)
    d.rectangle([(36, 423), (42, 427)], fill=YELLOW + (220,))

    # baked kickers: quiet slate, optically aligned to the value boxes
    # (same x as the XML elements they label). Values carry the weight.
    for text, xy in [("RELEASED", (42, 446)), ("RATING", (290, 446)),
                     ("GENRE", (42, 538)), ("PLAYERS", (42, 598)),
                     ("DEVELOPER", (234, 598)), ("SCREENSHOT", (36, 658))]:
        k = tracked_text_img(text, 11, SLATE, 3, alpha=150)
        body.alpha_composite(k, xy)

    # ---- SCREENSHOT: media, not a form field ----
    # no border box. One clean bottom-edge hairline, subtle depth, one
    # tiny yellow registration-mark corner offset outside the image.
    fsh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fsh).rectangle([38, 694, 434, 902], fill=(6, 14, 44, 30))
    body = Image.alpha_composite(body, fsh.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(body, "RGBA")
    d.line([(36, 900), (432, 900)], fill=ROYAL + (110,), width=1)
    d.line([(444, 672), (444, 688)], fill=YELLOW + (220,), width=2)
    d.line([(428, 672), (444, 672)], fill=YELLOW + (220,), width=2)

    # --- restrained Nova craftsmanship ---
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # tiny halftone transition melting into the intrusion's leading edge
    halftone(deco, (398, 340, 420, 520), ROYAL, spacing=8, max_r=3.0,
             fade="left", alpha_max=34)
    # ONE subtle blueprint fragment (whisper-quiet, behind the facts)
    blueprint(deco, (340, 560, 460, 690), color=(16, 52, 160), step=15, alpha=16)
    # ONE clipped blue geometric intrusion: slimmer and lighter than v17,
    # hugging the page's angular right edge, hairline yellow leading edge
    dd = ImageDraw.Draw(deco, "RGBA")
    dd.polygon([(422, 340), (445, 326), (446, 600), (422, 600)],
               fill=ROYAL + (130,))
    dd.line([(422, 340), (422, 600)], fill=YELLOW + (110,), width=1)
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
# 60x912: deep royal blue, ONE continuous thin yellow structural line
# (+ top tab, ticks removed), dot texture cut ~55%, halftone halved,
# supplied logos deliberately MOUNTED with real breathing room.
RAIL_PARAMS = {}

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
    # tonal variation: a softly lighter centre band within the royal blue
    tone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tone, "RGBA")
    for x in range(W):
        t = 1 - abs(x - W / 2) / (W / 2)
        td.line([(x, 0), (x, H)], fill=(120, 160, 255, int(26 * t)))
    img = Image.alpha_composite(img, Image.composite(tone, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    # controlled grid texture, cut ~55%: spacing 11 -> 17, alpha 16 -> 10
    dotgrid(img, (6, 30, 54, 882), alpha=10, spacing=17)
    # subtle halftone mid-band, halved
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (44, 340, 58, 572), (255, 255, 255), spacing=8, max_r=2.6,
             fade="left", alpha_max=13)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    d = ImageDraw.Draw(img, "RGBA")
    # subtle inner edge, right side
    d.line([(54, 26), (54, 886)], fill=NAVY + (120,), width=1)

    # the branding, deliberately MOUNTED with real breathing room:
    # plate padding 14 -> 22 per side, logo max length 620 -> 560
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
    # ONE continuous thin yellow structural line (+ top tab); the three
    # connector ticks are removed as decorative noise
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(4, 44), (4, 888)], fill=YELLOW + (255,), width=2)
    d.rectangle([(2, 24), (7, 44)], fill=YELLOW + (255,))
    img.save(os.path.join(RAILS, f"{system}.png"))
    return kind


if __name__ == "__main__":
    gen_panel()
    kinds = {}
    for system, name in SYSTEMS:
        kind = gen_rail(system, name)
        kinds[kind] = kinds.get(kind, 0) + 1
    print("rails:", kinds)
    with open(os.path.expanduser("~/workspace/crystal-esde-theme/work/rail_params_v17_4.json"), "w") as f:
        json.dump(RAIL_PARAMS, f, indent=1)
    print("rail params -> work/rail_params_v17_4.json")
