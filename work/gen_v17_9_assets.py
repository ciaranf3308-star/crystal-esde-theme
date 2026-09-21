#!/usr/bin/env python3
"""Crystal v17.9.0 asset generation: FULL CONVERGENCE PASS.

HARD SCOPES (non-negotiable):
- NO art-direction redesign. NO fallback artwork changes. NO new UI
  components. No brush typography, no decorative yellow, no cards, no
  heavy outlines. media_fallbacks/*, lib_shadow_soft.png,
  lib_glow_blue.png, lib_shard_prev.png, lib_plane_hero.png,
  lib_hero_wash.png, fonts, gamelist_generic_bg.png, star_filled.png,
  lib_title_rule.png, rails/* stay byte-identical to v17.8.0.
- Macro geometry locked. Only the whitelisted convergence moves below.

What changes (convergence only):
1. lib_shard_next.png REGENERATED as a 450x150 diagonal wedge (was a
   500x170 panel with hard edges): alpha ramps from 0 at the
   top-left corner to peak ~65 at the bottom-right corner, all four
   bitmap edges feathered to 0 - no flat interior, no hard edges
   anywhere. The next item reads as entering from the lower-right
   corner shadow instead of sitting inside a pale rectangle.
2. lib_panel_main.png: the baked screenshot frame/shadow/hairline/
   registration corner follow the screenshot +8px down; ONE new
   whisper element - a 2px #0A2FA0 diagonal hairline at alpha 8,
   local (294,0)->(470,180) - echoing the background's diagonal
   geometry at the page's quietest corner. Nothing else added.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.expanduser("~/workspace/crystal-esde-theme/work"))
from gen_v15_assets import (halftone, grain, tracked_text_img, ROYAL, WHITE,
                            YELLOW)

ART = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal/art")
NAVY = (10, 26, 92)
SLATE = (126, 138, 166)


# ----------------- the editorial left page (one composition) ------------
# 470x940, local coords (global origin 6,10). Angular white module
# silhouette byte-identical to v17.8. The ONLY drawing changes:
#   * screenshot box +8px y: local (42,714)-(438,884) ->
#     (42,722)-(438,892); baked soft shadow, bottom hairline and yellow
#     registration corner follow; SCREENSHOT kicker stays (the tightest
#     joint in the column gains the air).
#   * one whisper: a 2px #0A2FA0 diagonal hairline at alpha 8,
#     local (294,0)->(470,180), clipped by the page mask.
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
    for text, xy in [("RELEASED", (42, 446)), ("RATING", (290, 446)),
                     ("GENRE", (42, 546)), ("PLAYERS", (42, 610)),
                     ("DEVELOPER", (234, 610)), ("SCREENSHOT", (42, 694))]:
        k = tracked_text_img(text, 9, SLATE, 4, alpha=130)
        body.alpha_composite(k, xy)

    # ---- SCREENSHOT: media, not a form field ----
    # image element local box (v17.9): (42,722)-(438,892) - moved +8px
    # down so the column above breathes. No border box: one clean
    # bottom-edge hairline, subtle depth, ONE tiny yellow
    # registration-mark corner crossing the screenshot's top-right.
    fsh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fsh).rectangle([44, 726, 440, 894], fill=(6, 14, 44, 30))
    body = Image.alpha_composite(body, fsh.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(body, "RGBA")
    d.line([(42, 892), (438, 892)], fill=ROYAL + (110,), width=1)
    d.line([(430, 714), (430, 728)], fill=YELLOW + (220,), width=2)
    d.line([(430, 714), (444, 714)], fill=YELLOW + (220,), width=2)

    # ---- one whisper of Nova geometry: 2px diagonal hairline ----
    # #0A2FA0 at alpha 8, local (294,0)->(470,180); the page mask
    # clips it at the module edge. Drawn on its own layer and
    # alpha-composited (ImageDraw replaces RGBA pixels instead of
    # blending, which would stamp a dark hole through the white
    # body). Too faint to read as content.
    wh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(wh).line([(294, 0), (470, 180)], fill=(10, 47, 160, 8), width=2)
    body = Image.alpha_composite(body, wh)
    d = ImageDraw.Draw(body, "RGBA")

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


# ----------------- foreground shard: next enters bottom-right --------
# v17.9: the v17.2 500x170 panel had hard bitmap edges and read as a
# pale rectangle swallowing the next item. Regenerated as a 450x150
# diagonal wedge: alpha ramps 0 at the top-left corner -> peak ~65 at
# the bottom-right corner, ALL FOUR bitmap edges feathered to 0 - no
# flat interior, no hard edges anywhere. The next item's visible mass
# sits outside the wedge's diagonal cut, entering from the corner
# shadow. Navy (10,26,92) so it reads as environment, not chrome.
def gen_shard_next():
    W, H = 450, 150
    xs = np.arange(W, dtype=np.float64)[None, :].repeat(H, axis=0)
    ys = np.arange(H, dtype=np.float64)[:, None].repeat(W, axis=1)
    # diagonal parameter: 0 at top-left corner, 1 at bottom-right
    t = (xs + ys) / (W + H)
    alpha = 65.0 * np.power(np.clip(t, 0, 1), 1.2)
    # feather all four edges to 0 over ~24px (smoothstep)
    f = 24.0
    ex = np.minimum(np.minimum(xs, W - 1 - xs), f) / f
    ey = np.minimum(np.minimum(ys, H - 1 - ys), f) / f
    def smooth(a):
        a = np.clip(a, 0, 1)
        return a * a * (3 - 2 * a)
    alpha = alpha * smooth(ex) * smooth(ey)
    img = Image.new("RGBA", (W, H), NAVY + (0,))
    img.putalpha(Image.fromarray(np.clip(alpha, 0, 255).astype(np.uint8), "L"))
    img = img.filter(ImageFilter.GaussianBlur(2))  # kill banding
    p = os.path.join(ART, "lib_shard_next.png")
    img.save(p)
    print("lib_shard_next.png", img.size)


if __name__ == "__main__":
    gen_panel()
    gen_shard_next()
