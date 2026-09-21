#!/usr/bin/env python3
"""Crystal v17.3.0 asset generation: PREMIUM POLISH pass on the LOCKED
gamelist macro layout (left column 6,10 470x940; spine 486,24 60x912;
hero 540px at 900,430; title rule Y716 / title Y736 / meta Y757;
screenshot 42,700 396x210; footer y915).

Per the user's 10-point brief ("do not redesign the screen from scratch;
make a serious polish pass"), what changes is the finish:

1. MARQUEE HEADER (the priority): the marquee zone was reading as a
   foggy/frosted weak blur - the 240-alpha page let the dark blueprint
   bleed through, so the "white" header was really a washed gray. The
   top section of the left panel is rebuilt as a proper feature banner:
     - a SOLID fully-opaque white banner behind the marquee zone
       (local (10,30)-(452,308), clipped to the page silhouette)
     - a clean royal-blue frame around the banner (2px, following the
       page's angular edges)
     - ONE restrained yellow accent segment on the frame's bottom edge
   The marquee element geometry is untouched (24,44 424x252); the real
   scraped marquee now lands on solid white inside blue framing - bold,
   legible, confident. No frost, no haze.
2. HERO IMPACT: the generic contact shadow becomes a deeper two-layer
   treatment (tight dark core + wide soft falloff, still shape-neutral);
   the blue atmosphere gets a slightly deeper pooled core with a tighter
   falloff. No cheesy glows, no outlines, no circular frames - the
   v17.2 shape-awareness (native silhouette for cartridges, cards,
   UMDs, discs) is fully retained. Per-shape material quality
   (cartridge tactility, card edge light, disc sheen) is mock-level
   art-direction intent; the real theme stays generic by construction.
3. TITLE RULE: the yellow bar moves to the TOP of the rule art, well
   clear of the title glyphs (it was colliding with the title); white
   hairline full width beneath it. Clean air between rule and title.
4. Left panel maturity: crisp 1px light edge along the page's top edge;
   the screenshot's yellow corner accent is slightly more deliberate.
   Kickers, description rule, metadata zone, craftsmanship, intrusion,
   halftone, blueprint and micro-accents are byte-identical in spirit
   (same code, same positions).

Macro geometry untouched. System-view cards untouched.
gamelist_generic_bg.png untouched."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.expanduser("~/workspace/crystal-esde-theme/work"))
from gen_v15_assets import (halftone, blueprint, dotgrid, grain,
                            tracked_text_img, SYSTEMS, tracked_text_v15,
                            ROYAL, DEEP, NAVY, INKDIM, YELLOW, WHITE, FB)

ART = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal/art")


# ----------------- the editorial left page (one composition) ---
# 470x940, local coords (global origin 6,10). SAME angular white module
# silhouette (footprint locked), no mats, no nested boxes.
#   marquee zone (global 24,44 424x252) -> local (18,34,442,286)
#   v17.3: the header is a SOLID white feature banner (local
#   (10,30)-(452,308), clipped to the page) with a royal frame and one
#   restrained yellow accent - no frost, no haze.
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

    # crisp 1px light edge along the page's top edge (paper sharpness)
    d.line([(34, 1), (388, 1)], fill=WHITE + (130,), width=1)

    # ---- v17.3 MARQUEE HEADER: a solid feature banner ----
    # Fully opaque white - the frosted look came from the 240-alpha page
    # letting the dark blueprint bleed through. Clipped to the page by
    # the mask at the end.
    d.rectangle([10, 30, 452, 308], fill=WHITE + (255,))
    # clean royal frame around the banner, following the page's angular
    # edges (every vertex verified inside the page silhouette)
    frame = [(44, 32), (404, 32), (440, 70), (440, 300), (28, 300),
             (32, 184), (40, 88)]
    d.line(frame + [frame[0]], fill=ROYAL + (255,), width=2)
    # ONE restrained yellow accent: a segment of the frame's bottom edge
    d.line([(28, 300), (88, 300)], fill=YELLOW + (255,), width=2)

    # tiny editorial kicker (secondary) + one yellow tick: no band.
    # Moved up so it sits clear above the solid banner.
    kick = tracked_text_img("NOW SHOWING", 13, ROYAL, 4, alpha=255)
    body.alpha_composite(kick, (44, 10))
    d.polygon([(28, 8), (38, 8), (28, 20)], fill=YELLOW + (255,))

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
    # page + a very subtle depth shadow. ONE deliberate yellow corner
    # accent intersecting the frame's top-left corner. No nested outlines.
    fsh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fsh).rectangle([39, 693, 435, 903], fill=(6, 14, 44, 30))
    body = Image.alpha_composite(body, fsh.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(body, "RGBA")
    d.rectangle([36, 690, 432, 900], outline=ROYAL + (255,), width=1)
    d.polygon([(36, 690), (72, 690), (36, 726)], fill=YELLOW + (255,))

    # --- restrained Nova craftsmanship (unchanged from v17) ---
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


# --------------------------------------------- hero contact shadow ---
# v17.3: deeper two-layer treatment - a tight dark core for material
# weight plus a wide soft falloff. Still a plain ellipse: shape-neutral,
# so cartridges, cards, UMDs and discs all sit on it honestly.
def gen_hero_shadow():
    W, H = 640, 72
    fall = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fall).ellipse([50, 8, W - 50, H - 8], fill=(10, 20, 60, 80))
    fall = fall.filter(ImageFilter.GaussianBlur(20))
    core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(core).ellipse([110, 22, W - 110, H - 22], fill=(6, 12, 40, 165))
    core = core.filter(ImageFilter.GaussianBlur(9))
    img = Image.alpha_composite(fall, core)
    img.save(os.path.join(ART, "lib_shadow_soft.png"))
    print("lib_shadow_soft.png", img.size)


# ------------------------------------------- blue atmosphere ---
# v17.3: slightly deeper pooled core with a tighter falloff - clearer
# foreground separation, still restrained (no cheesy glow).
def gen_glow_blue():
    W, H = 560, 500
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = W / 2, H / 2 + 52
    R = 250
    for r in range(int(R), 0, -2):
        t = r / R
        a = int(46 * (1 - t) ** 2.2)
        d.ellipse([cx - r * 1.10, cy - r * 0.92, cx + r * 1.10, cy + r * 0.92],
                  fill=(44, 94, 218, a))
    img.save(os.path.join(ART, "lib_glow_blue.png"))
    print("lib_glow_blue.png", img.size)


# ------------------------------------------------- title rule ---
# v17.3: the yellow bar moves to the TOP of the art, well clear of the
# title glyphs (it was colliding with the title). White hairline full
# width beneath it. Clean air between rule and title.
def gen_title_rule():
    W, H = 300, 10
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # short centered yellow bar, top-weighted (art y0-2 -> global 711-713)
    for x in range(114, 186):
        t = abs(x - 150) / 36.0
        a = int(255 * max(0.0, 1 - t * t))
        d.line([(x, 0), (x, 2)], fill=YELLOW + (a,))
    # white hairline full width (art y5-6)
    d.rectangle([0, 5, W, 6], fill=WHITE + (235,))
    img.save(os.path.join(ART, "lib_title_rule.png"))
    print("lib_title_rule.png", img.size)


if __name__ == "__main__":
    gen_panel()
    gen_hero_shadow()
    gen_glow_blue()
    gen_title_rule()
