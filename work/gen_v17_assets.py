#!/usr/bin/env python3
"""Crystal v17.0.0 asset generation: DETAIL-RESOLUTION pass on the LOCKED
gamelist macro skeleton (left column 6,10 470x940; spine 486,24 60x912;
hero 540px at 900,430; prev/next 900,10 / 900,850 pitch 420; rule Y716 /
title Y736 / meta Y757; screenshot 42,700 396x210; footer y915).

Per the user's 10-point brief, what changes is the finish:
1. Lower-right rebuilt: title band keeps its approved position; the NEXT
   item is repositioned VISUALLY via a redesigned foreground shard so it
   enters from the bottom edge, partially cropped, occupying a distinct
   space from the title. No placeholder rects.
2. Hero treatment unchanged in XML (scale, crisp edges, contact shadow,
   blue atmosphere, ONE thin selective yellow rim arc) - no rings.
3. Marquee zone grows substantially (24,44 424x252, +31% area): open
   whitespace, no blue rectangle, no fade. NOW SHOWING stays a tiny kicker.
4. Left column: no boxes back. Restrained craftsmanship only - tiny
   halftone transitions, ONE subtle blueprint fragment, ONE clipped blue
   geometric intrusion, sparse yellow micro-accents. ~85% stays clean white.
5. Typography spacing pass: more air between description and facts, labels
   quieter, PLAYERS/DEVELOPER baselines standardised, rating with the year.
6. Screenshot: ONE clean hairline frame + subtle depth shadow + ONE tiny
   yellow corner accent. No nested frames.
7. Spine: tonal variation within the royal blue, controlled grid texture,
   ONE continuous thin yellow structural line, supplied logos deliberately
   MOUNTED (mounting plate), no extra text.
8. Prev/next: real media, smaller, dimmer, edge-cropped, shard-cropped -
   a real navigation path around the dominant hero.
9. Overlap: marquee breaks over its rule, disc overlaps the hero plane,
   shards crop neighbours, spine ticks reach into adjacent surfaces.
10. Footer quieter still (0.0135, 80FFFFFF).

ES-DE 3.4.1 has no theme keyframes/idle animation: native eased carousel
transitions only; none claimed."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.expanduser("~/workspace/crystal-esde-theme/work"))
from gen_v15_assets import (halftone, blueprint, dotgrid, grain,
                            tracked_text_img, SYSTEMS, tracked_text_v15,
                            ROYAL, DEEP, NAVY, INKDIM, YELLOW, WHITE, FB)

ART = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal/art")
RAILS = os.path.join(ART, "rails")
LOGOS = os.path.join(ART, "console_logos")

# ----------------- the editorial left page (one composition) ---
# 470x940, local coords (global origin 6,10). SAME angular white module
# silhouette (footprint locked), no mats, no L-frames, no nested boxes.
#   marquee zone (global 24,44 424x252) -> local (18,34,442,286)
#   baked marquee rule at local y296 (global 306)
#   screenshot (global 42,700 396x210) -> local (36,690,432,900)
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

    # marquee sits on OPEN WHITESPACE: no mat, no frame, no blue rectangle.
    # One hairline rule beneath the LARGER marquee zone; the marquee art may
    # break over it (controlled overlap).
    d.line([(18, 296), (442, 296)], fill=ROYAL + (140,), width=1)
    d.line([(18, 296), (78, 296)], fill=YELLOW + (255,), width=2)

    # single hairline under the description (global y 435 -> local 425)
    d.line([(36, 425), (434, 425)], fill=ROYAL + (110,), width=1)
    d.rectangle([(36, 422), (44, 428)], fill=YELLOW + (255,))

    # baked kickers: tiny and quiet (labels carry no weight) - VALUES rule.
    # Positions track the v17 spacing pass (year row moved to local y458).
    for text, xy in [("RELEASED", (48, 446)), ("RATING", (296, 446)),
                     ("GENRE", (48, 538)), ("PLAYERS", (48, 598)),
                     ("DEVELOPER", (240, 598)), ("SCREENSHOT", (48, 658))]:
        k = tracked_text_img(text, 11, ROYAL, 3, alpha=140)
        body.alpha_composite(k, xy)

    # screenshot: ONE clean royal hairline frame straight on the white
    # page + a very subtle depth shadow. ONE tiny yellow corner accent
    # intersecting the frame's top-left corner. No nested outlines.
    fsh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fsh).rectangle([39, 693, 435, 903], fill=(6, 14, 44, 30))
    body = Image.alpha_composite(body, fsh.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(body, "RGBA")
    d.rectangle([36, 690, 432, 900], outline=ROYAL + (255,), width=1)
    d.polygon([(36, 690), (60, 690), (36, 714)], fill=YELLOW + (255,))

    # --- restrained Nova craftsmanship (brief point 4) ---
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # tiny halftone transition melting into the intrusion's leading edge
    # (the page's right edge sits at local x~447-450 in this band)
    halftone(deco, (396, 340, 420, 560), ROYAL, spacing=8, max_r=3.0,
             fade="left", alpha_max=38)
    # ONE subtle blueprint fragment (whisper-quiet, behind the facts text)
    blueprint(deco, (340, 560, 460, 690), color=(16, 52, 160), step=15, alpha=16)
    # ONE clipped blue geometric intrusion: thin royal shard hugging the
    # page's angular right edge, with a hairline yellow leading edge
    dd = ImageDraw.Draw(deco, "RGBA")
    dd.polygon([(416, 310), (442, 292), (444, 626), (416, 626)],
               fill=ROYAL + (190,))
    dd.line([(416, 310), (416, 626)], fill=YELLOW + (160,), width=1)
    # sparse yellow micro-accents: two tiny ticks, nothing more
    dd.rectangle([(36, 908), (44, 916)], fill=YELLOW + (220,))
    dd.rectangle([(424, 648), (426, 662)], fill=YELLOW + (220,))

    body = Image.composite(body, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
    body = grain(body, mask)
    # craftsmanship sits ON the page (over the white), never buried under it
    img = Image.alpha_composite(img, body)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    p = os.path.join(ART, "lib_panel_main.png")
    img.save(p)
    print("lib_panel_main.png", img.size)

# ----------------- foreground shard: next item enters the frame ---
# Redesigned for the lower-right rebuild: the element sits at (900,795
# 380x165), BELOW the title band (ends y767). Its diagonal left edge crops
# the next disc's upper-right so the visible mass enters from the bottom
# edge, partially cropped - a distinct visual space from the title.
def gen_shard_next():
    W, H = 380, 165
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    poly = [(0, 0), (W, 30), (W, H), (120, H)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(poly, fill=(10, 26, 92, 84))
    # short quiet tick at the top of the left edge (not a scratch)
    d.line([(0, 0), (26, 54)], fill=YELLOW + (95,), width=2)
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (210, 30, 350, 140), (255, 255, 255), spacing=9, max_r=3.4,
             fade="left", alpha_max=30)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    img.save(os.path.join(ART, "lib_shard_next.png"))
    print("lib_shard_next.png", img.size)

# ------------------------------------------------- the console spine ---
# Refined magazine spine, 60x912: subtle tonal variation within the royal
# blue (lighter centre band), controlled grid texture, ONE continuous thin
# yellow structural line with small connector ticks, supplied logos
# deliberately MOUNTED on a mounting plate (not floating); text fallbacks
# for the five systems without a supplied logo.
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
    d = ImageDraw.Draw(img, "RGBA")
    # controlled grid texture across the spine
    dotgrid(img, (6, 30, 54, 882), alpha=16, spacing=11)
    # subtle halftone mid-band
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (44, 340, 58, 572), (255, 255, 255), spacing=8, max_r=2.6,
             fade="left", alpha_max=26)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    d = ImageDraw.Draw(img, "RGBA")
    # subtle inner edge, right side
    d.line([(54, 26), (54, 886)], fill=NAVY + (120,), width=1)

    # the branding, deliberately MOUNTED: a mounting plate sits behind the
    # rotated logo so it reads as fixed to the spine, never floating
    logo_path = os.path.join(LOGOS, f"{system}.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        rot = logo.rotate(90, expand=True)
        rw, rh = rot.size
        scale = min(40.0 / rw, 620.0 / rh)
        rot = rot.resize((max(1, int(rw * scale)), max(1, int(rh * scale))), Image.LANCZOS)
        ox, oy = (W - rot.width) // 2 + 2, (H - rot.height) // 2
        plate = Image.new("RGBA", (rot.width + 28, rot.height + 28), (0, 0, 0, 0))
        pd = ImageDraw.Draw(plate, "RGBA")
        pd.rounded_rectangle([0, 0, plate.width, plate.height], radius=8,
                             fill=(8, 20, 70, 90))
        pd.rounded_rectangle([0, 0, plate.width - 1, plate.height - 1], radius=8,
                             outline=(255, 255, 255, 50), width=1)
        img.alpha_composite(plate, (ox - 14, oy - 14))
        white = Image.new("RGBA", rot.size, WHITE + (255,))
        white.putalpha(rot.split()[3])
        img.alpha_composite(white, (ox + 2, oy + 2))
        img.alpha_composite(rot, (ox, oy))
        kind = "logo"
    else:
        size = 36
        font = ImageFont.truetype(FB, size)
        tw = tracked_text_v15(name, font, 8)
        while tw.width > 620 and size > 18:
            size -= 2
            font = ImageFont.truetype(FB, size)
            tw = tracked_text_v15(name, font, 8)
        vert = tw.rotate(90, expand=True)
        ox, oy = (W - vert.width) // 2 + 2, (H - vert.height) // 2
        plate = Image.new("RGBA", (vert.width + 28, vert.height + 28), (0, 0, 0, 0))
        pd = ImageDraw.Draw(plate, "RGBA")
        pd.rounded_rectangle([0, 0, plate.width, plate.height], radius=8,
                             fill=(8, 20, 70, 90))
        pd.rounded_rectangle([0, 0, plate.width - 1, plate.height - 1], radius=8,
                             outline=(255, 255, 255, 50), width=1)
        img.alpha_composite(plate, (ox - 14, oy - 14))
        shade = Image.new("RGBA", vert.size, NAVY + (255,))
        shade.putalpha(vert.split()[3])
        img.alpha_composite(shade, (ox + 2, oy + 2))
        img.alpha_composite(vert, (ox, oy))
        kind = "TEXT-FALLBACK"
    # ONE continuous thin yellow structural line, drawn LAST so it stays
    # continuous over the mounting plate; small connector ticks reach into
    # the adjacent surfaces
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(4, 44), (4, 888)], fill=YELLOW + (255,), width=2)
    d.rectangle([(2, 24), (7, 44)], fill=YELLOW + (255,))
    for ty in (300, 456, 612):
        d.line([(0, ty), (10, ty)], fill=YELLOW + (200,), width=2)
    img.save(os.path.join(RAILS, f"{system}.png"))
    return kind

if __name__ == "__main__":
    gen_panel()
    gen_shard_next()
    kinds = {}
    for system, name in SYSTEMS:
        kind = gen_rail(system, name)
        kinds[kind] = kinds.get(kind, 0) + 1
    print("rails:", kinds)
