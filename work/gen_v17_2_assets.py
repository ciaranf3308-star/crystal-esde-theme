#!/usr/bin/env python3
"""Crystal v17.2.0 asset generation: PHYSICAL-MEDIA SHAPE-AWARENESS pass.

The hero must stop assuming a disc. Real theme changes behind this:
  - lib_hero_rim.png (a partial arc hugging a 540px disc) is RETIRED and
    deleted: a fixed circular highlight cannot be universal across
    cartridges, game cards, UMDs and discs. Depth now comes only from
    scale, the generic soft contact shadow, the generic blue atmosphere,
    and the small compositional yellow tick baked into the hero plane
    (ES-DE 3.4.1 cannot draw per-silhouette edge highlights; the mock
    illustrates that art-direction intent per shape).
  - The next-item foreground shard is redesigned for the re-pitched
    carousel (next now at (900,910), 240px, 29% cropped off the bottom
    edge): it occludes the item's upper-left so the visible mass reads as
    entering from the bottom-right corner, clear of the title zone.
  - Spine rails: decorative noise reduced slightly (quieter grid +
    halftone); the continuous yellow structural line and mounted branding
    stay.

Macro geometry untouched: left column (6,10 470x940), spine (486,24
60x912), hero 540px at (900,430), title rule Y716 / title Y736 / meta
Y757, screenshot (42,700 396x210), footer y915."""
import os, sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.expanduser("~/workspace/crystal-esde-theme/work"))
from gen_v15_assets import (halftone, blueprint, dotgrid, grain,
                            tracked_text_img, SYSTEMS, tracked_text_v15,
                            ROYAL, DEEP, NAVY, INKDIM, YELLOW, WHITE, FB)
from gen_v17_assets import gen_panel  # left page already mature; kept byte-identical
from PIL import ImageFont

ART = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal/art")
RAILS = os.path.join(ART, "rails")
LOGOS = os.path.join(ART, "console_logos")


# ----------------- foreground shard: prev enters top-right -----------
# v17.2: height trimmed to 160 so the shard never dims the hero's top
# edge (hero top at y160); it frames only the prev item's visible sliver.
def gen_shard_prev():
    W, H = 360, 160
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    poly = [(0, 0), (W, 0), (W, 130), (60, H)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(poly, fill=(10, 26, 92, 84))
    d.line([(0, 0), (20, 60)], fill=YELLOW + (95,), width=2)
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (200, 20, 340, 130), (255, 255, 255), spacing=9,
             max_r=3.4, fade="left", alpha_max=30)
    img = Image.alpha_composite(
        img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    p = os.path.join(ART, "lib_shard_prev.png")
    img.save(p)
    print("lib_shard_prev.png", img.size)


# ----------------- foreground shard: next enters bottom-right --------
# Redesigned for the re-pitched carousel: the next item sits at (900,910),
# 240px, its box (780,790)-(1020,1030) - 29% cropped off the bottom edge.
# The shard box (780,790 500x170) occludes the item's upper-left along a
# diagonal, so the visible mass reads as entering from the bottom-right
# corner. The title zone (ends y767) stays clear: the shard starts at
# y790, 23px below the meta line.
def gen_shard_next():
    W, H = 500, 170
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # opaque region: full top band falling along a diagonal to the
    # bottom-left, so the next item's readable mass is the lower-right -
    # entering from the bottom-right corner, clear of the title zone
    poly = [(0, 0), (W, 0), (W, 50), (0, H)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(poly, fill=(10, 26, 92, 80))
    # short quiet tick riding the diagonal
    d.line([(70, 138), (118, 118)], fill=YELLOW + (95,), width=2)
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (330, 10, 480, 60), (255, 255, 255), spacing=9,
             max_r=3.4, fade="left", alpha_max=28)
    img = Image.alpha_composite(
        img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    p = os.path.join(ART, "lib_shard_next.png")
    img.save(p)
    print("lib_shard_next.png", img.size)


# ------------------------------------------------- the console spine ---
# v17.2: decorative noise reduced slightly - quieter grid texture and
# halftone. The royal gradient, tonal centre band, ONE continuous thin
# yellow structural line, connector ticks and the deliberately MOUNTED
# branding are unchanged.
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
    tone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tone, "RGBA")
    for x in range(W):
        t = 1 - abs(x - W / 2) / (W / 2)
        td.line([(x, 0), (x, H)], fill=(120, 160, 255, int(26 * t)))
    img = Image.alpha_composite(
        img, Image.composite(tone, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    # quieter grid texture (was alpha 16)
    dotgrid(img, (6, 30, 54, 882), alpha=12, spacing=11)
    # quieter halftone mid-band (was alpha_max 26)
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (44, 340, 58, 572), (255, 255, 255), spacing=8, max_r=2.6,
             fade="left", alpha_max=20)
    img = Image.alpha_composite(
        img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))

    logo_path = os.path.join(LOGOS, f"{system}.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        rot = logo.rotate(90, expand=True)
        rw, rh = rot.size
        scale = min(40.0 / rw, 620.0 / rh)
        rot = rot.resize((max(1, int(rw * scale)), max(1, int(rh * scale))),
                         Image.LANCZOS)
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
    # continuous over the mounting plate; connector ticks reach out
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(4, 44), (4, 888)], fill=YELLOW + (255,), width=2)
    d.rectangle([(2, 24), (7, 44)], fill=YELLOW + (255,))
    for ty in (300, 456, 612):
        d.line([(0, ty), (10, ty)], fill=YELLOW + (200,), width=2)
    img.save(os.path.join(RAILS, f"{system}.png"))
    return kind


if __name__ == "__main__":
    # the disc-specific rim is retired: a fixed circular highlight cannot
    # be universal across cartridges, game cards, UMDs and discs
    rim = os.path.join(ART, "lib_hero_rim.png")
    if os.path.exists(rim):
        os.remove(rim)
        print("retired lib_hero_rim.png")
    gen_shard_prev()
    gen_shard_next()
    kinds = {}
    for system, name in SYSTEMS:
        kind = gen_rail(system, name)
        kinds[kind] = kinds.get(kind, 0) + 1
    print("rails:", kinds)
