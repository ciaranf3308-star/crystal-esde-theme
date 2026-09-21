#!/usr/bin/env python3
"""Crystal v17.8.0 asset generation: RESPONSIVE ROBUSTNESS + FINAL COMPOSITION.

HARD SCOPES (non-negotiable):
- NO art-direction redesign. NO fallback artwork changes. NO new UI
  components. No brush typography, no decorative yellow, no cards, no
  heavy outlines. media_fallbacks/*, lib_shadow_soft.png,
  lib_glow_blue.png, lib_shard_prev/next.png, fonts,
  gamelist_generic_bg.png, star_filled.png, lib_title_rule.png stay
  byte-identical to v17.7.0.
- Macro geometry locked. The only geometric moves are composition
  refinements inside the locked footprints:
    * screenshot box shrinks 210 -> 170px tall and recentres lower
      (global 706-876); the baked hairline / registration corner /
      kicker follow. Recovered space becomes breathing room above.
    * spine logo caps 40/620 -> 44/680; dotgrid 40px/a3 -> 48px/a2.
    * hero wash regenerated softer (no rectangular read); hero plane
      edges feathered, alpha lowered.

What changes (precision only):
1. PANEL: screenshot box aligned to the text column (local x 36->42).
   Everything else on the page is byte-identical in drawing to v17.6.
2. SPINE: logo presence modestly increased (width cap 36->40,
   length cap 560->620), logo centred OPTICALLY (6px above the
   mathematical centre - the classic optical correction), dotgrid
   further reduced (32px/alpha 4 -> 40px/alpha 3). One thin yellow
   structural line kept. Everything else extremely quiet.
3. HERO PLANE: the yellow leading edge along the plane's top is
   DELETED (decorative yellow with no informational purpose - the
   v17.6 XML comment describing the tick was stale; the v17.6 yellow
   audit's kept-list never included it). The blue plane + blueprint
   stay.
4. HERO WASH (new asset lib_hero_wash.png): an extremely subtle
   neutral radial behind the hero region - faint white lift at the
   centre (dark discs / transparent cartridges read), faint navy
   deepening at the edge (bright white discs read). No container, no
   outline, no ring. The physical object remains the spectacle.
"""
import os, sys, json, math
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.expanduser("~/workspace/crystal-esde-theme/work"))
from gen_v15_assets import (halftone, dotgrid, grain, tracked_text_img,
                            tracked_text_v15, blueprint, SYSTEMS, ROYAL,
                            DEEP, NAVY, INKDIM, YELLOW, WHITE, FB)
from PIL import ImageFilter

ART = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal/art")
RAILS = os.path.join(ART, "rails")
LOGOS = os.path.join(ART, "console_logos")
SLATE = (126, 138, 166)


# ----------------- the editorial left page (one composition) ------------
# 470x940, local coords (global origin 6,10). Angular white module
# silhouette byte-identical to v17.6. The ONLY drawing change: the
# screenshot box moves +6px in x (local 36->42) so the placed image
# aligns exactly with the text column (all XML text sits at global
# x=48). Kicker, hairline, shadow and registration corner follow.
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

    d.line([(34, 1), (388, 1)], fill=WHITE + (130,), width=1)

    # ---- MARQUEE MASTHEAD: open white zone, designed anchor ----
    kick = tracked_text_img("NOW SHOWING", 9, ROYAL, 4, alpha=130)
    body.alpha_composite(kick, (46, 12))
    d.line([(36, 294), (434, 294)], fill=ROYAL + (70,), width=1)
    d.rectangle([(36, 292), (42, 296)], fill=YELLOW + (200,))

    # the ONE structural rule: between description and facts.
    d.line([(36, 425), (434, 425)], fill=ROYAL + (90,), width=1)

    # baked kickers: DejaVuSans-Bold tracked micro, quieter slate.
    # SCREENSHOT kicker follows the image to the text column (36->42).
    for text, xy in [("RELEASED", (42, 446)), ("RATING", (290, 446)),
                     ("GENRE", (42, 546)), ("PLAYERS", (42, 610)),
                     ("DEVELOPER", (234, 610)), ("SCREENSHOT", (42, 694))]:
        k = tracked_text_img(text, 9, SLATE, 4, alpha=130)
        body.alpha_composite(k, xy)

    # ---- SCREENSHOT: media, not a form field ----
    # image element local box: (42,714)-(438,884) - aligned with the
    # text column, height reduced 210 -> 170 so the lower-left column
    # breathes. Shifted down 18px to clear a two-line developer value.
    # No border box: one clean bottom-edge hairline, subtle depth,
    # ONE tiny yellow registration-mark corner crossing the
    # screenshot's top-right corner.
    fsh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fsh).rectangle([44, 718, 440, 886], fill=(6, 14, 44, 30))
    body = Image.alpha_composite(body, fsh.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(body, "RGBA")
    d.line([(42, 884), (438, 884)], fill=ROYAL + (110,), width=1)
    d.line([(430, 706), (430, 720)], fill=YELLOW + (220,), width=2)
    d.line([(430, 706), (444, 706)], fill=YELLOW + (220,), width=2)

    # --- one quiet graphic gesture only ---
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
# 60x912: deep solid royal foundation, dotgrid reduced again
# (48px/alpha 2 - the one subtle texture area), ONE thin 1px continuous
# yellow structural line, supplied logos at increased presence
# (width cap 40->44, length cap 620->680) centred OPTICALLY (6px above
# mathematical centre), plate without outline. Luxury publication
# spine, not a separator bar.
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
    tone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tone, "RGBA")
    for x in range(W):
        t = 1 - abs(x - W / 2) / (W / 2)
        td.line([(x, 0), (x, H)], fill=(110, 150, 250, int(18 * t)))
    img = Image.alpha_composite(img, Image.composite(tone, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    # the ONE subtle texture area: dotgrid sparser still (40px/alpha 3)
    dotgrid(img, (6, 30, 54, 882), alpha=2, spacing=48)
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(54, 26), (54, 886)], fill=NAVY + (90,), width=1)

    OPTICAL_LIFT = 6  # optical centre sits above mathematical centre
    logo_path = os.path.join(LOGOS, f"{system}.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        rot = logo.rotate(90, expand=True)
        rw, rh = rot.size
        scale = min(44.0 / rw, 680.0 / rh)
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
        while tw.width > 680 and size > 18:
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
    # ONE thin continuous yellow structural line, 1px
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(4, 44), (4, 888)], fill=YELLOW + (255,), width=1)
    img = Image.composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
    img.save(os.path.join(RAILS, f"{system}.png"))
    return kind


# --------------------------------- hero plane (tick removed) ----------
# 420x360: the soft blue plane behind the hero's lower-right. The
# v17.5/v17.6 yellow leading edge along the top is DELETED (decorative
# yellow with no informational purpose). Blue plane + faint blueprint
# stay.
def gen_plane_hero():
    W, H = 420, 360
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    poly = [(40, 0), (W, 60), (400, H), (0, 300)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(poly, fill=(18, 58, 178, 38))
    # feather the plane edges so it never reads as a rectangular slot
    mask = mask.filter(ImageFilter.GaussianBlur(5))
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    blueprint(deco, (30, 40, 390, 330), alpha=14)
    img = Image.alpha_composite(img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    img.save(os.path.join(ART, "lib_plane_hero.png"))
    print("lib_plane_hero.png", img.size)


# --------------------------------- hero wash (new) --------------------
# lib_hero_wash.png 760x760: an extremely subtle NEUTRAL radial behind
# the hero region so any real scraped object reads clearly - bright
# white discs, dark discs, transparent cartridges, small DS/3DS cards.
# Faint white lift at the centre, faint navy deepening at the edge.
# No container, no outline, no ring. Alpha peaks are whisper-quiet.
def gen_hero_wash():
    S = 760
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    px = img.load()
    c = S / 2
    for y in range(S):
        for x in range(S):
            r = math.hypot(x - c, y - c) / c  # 0 centre -> 1 edge
            if r > 0.98:
                continue                     # fully transparent at the rim
            if r < 0.5:
                t = 1 - r / 0.5
                a = int(12 * t * t)          # white lift, peak alpha 12
                px[x, y] = (235, 242, 255, a)
            elif r > 0.55:
                t = (r - 0.55) / 0.43
                a = int(16 * t * t)          # navy depth, peak alpha 16
                px[x, y] = (10, 24, 80, a)
    # heavy soften: the wash must read as open space, never a box
    img = img.filter(ImageFilter.GaussianBlur(44))
    p = os.path.join(ART, "lib_hero_wash.png")
    img.save(p)
    print("lib_hero_wash.png", img.size)


if __name__ == "__main__":
    gen_panel()
    gen_plane_hero()
    gen_hero_wash()
    kinds = {}
    for system, name in SYSTEMS:
        kind = gen_rail(system, name)
        kinds[kind] = kinds.get(kind, 0) + 1
    print("rails:", kinds)
    with open(os.path.expanduser("~/workspace/crystal-esde-theme/work/rail_params_v17_8.json"), "w") as f:
        json.dump(RAIL_PARAMS, f, indent=1)
    print("rail params -> work/rail_params_v17_8.json")
