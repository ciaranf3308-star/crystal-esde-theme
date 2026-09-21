#!/usr/bin/env python3
"""v18.2.0 FINAL ART-DIRECTION CONVERGENCE (target 9.5/10).

Macro layout LOCKED. This pass closes the visual-quality gap judged
against the VM-only proof harness (work/proof_assets/, never shipped).

ONLY these production assets change:
  1. art/lib_panel_main.png - the left editorial page. Same white
     silhouette (byte-identical poly). Two Nova gestures, structural
     not decorative:
       A. ANGULAR BLUE INTRUSION: a navy diagonal wedge rising behind
          the page's left edge (peeks ~12-30px, alpha 150), travelling
          partially behind the page from y~60 to y~680. Reads as the
          page being pinned into the Nova composition.
       B. REGISTRATION / BLUEPRINT MOTIF linking masthead, description
          and screenshot: three tiny "+" registration marks on one
          vertical column (masthead / description / screenshot corner)
          plus one quiet blueprint fragment (hairlines + ticks) in the
          right margin spanning the description and screenshot sections.
     Kept: NOW SHOWING kicker, all baked micro kickers, the designed
     anchor rule under the masthead, the inter-section rule, the
     screenshot frame/shadow/hairline + yellow corner accent, the
     diagonal whisper. ~90% of the page stays calm white.
  2. art/lib_plane_hero.png - hero environment as a museum/product-
     photography stage: the v18 radial wash (centre alpha 18) plus
     ultra-faint blueprint geometry: three concentric hairline circles,
     N/S/E/W crosshair ticks and four tiny corner registration marks,
     all alpha 8-20. The real physical media stays completely dominant.
  3. art/rails/*.png (21) - the spine as a CONNECTOR, not a wall:
       * dotgrid texture REMOVED (was 64px/alpha 1).
       * one porous "window" band: the royal body alpha dips to ~170
         across a feathered 90px band at y~600 so the Nova background
         collage visibly continues across/behind the spine - the two
         regions read as one spread.
       * the 1px yellow structural line keeps full crispness and gains
         two tiny connector ticks marking the window band's edges, so
         the window reads engineered, not accidental.
       * deep royal gradient, feathered left/right edges, optical lift
         and the per-system logo mounting plate: unchanged.

Fallback media, hero/marquee/screenshot bindings: untouched.
"""
import os, sys, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
sys.path.insert(0, os.path.join(REPO, "work"))
from gen_v15_assets import (ROYAL, DEEP, NAVY, INKDIM, YELLOW, WHITE,
                            SYSTEMS, dotgrid, halftone, grain, blueprint,
                            tracked_text_img, tracked_text_v15)
SLATE = (126, 138, 166)

ART = os.path.join(REPO, "theme-src/crystal/art")
RAILS = os.path.join(ART, "rails")
LOGOS = os.path.join(ART, "console_logos")
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def reg_mark(d, cx, cy, arm=7, color=None, width=1):
    """A tiny registration cross on the SAME layer (d is ImageDraw RGBA)."""
    color = color or ROYAL + (70,)
    d.line([(cx - arm, cy), (cx + arm, cy)], fill=color, width=width)
    d.line([(cx, cy - arm), (cx, cy + arm)], fill=color, width=width)


# ----------------------------- 1. left page ----------------------------
PANEL_POLY = [(34, 0), (388, 0), (452, 64), (446, 500), (458, 800),
              (446, 884), (410, 940), (46, 940), (16, 894), (24, 600),
              (12, 300), (22, 90)]

def gen_panel():
    W, H = 470, 940
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(PANEL_POLY, fill=255)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 10, y + 14) for x, y in PANEL_POLY],
                               fill=(6, 14, 44, 100))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(15)))

    # ---- gesture A: angular blue intrusion behind the page ----
    # A navy diagonal wedge, rising left-to-right, peeking out from
    # behind the page's left edge. Structural, not decorative.
    intr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(intr).polygon([(-60, 96), (34, 58), (52, 624),
                                 (-60, 690)], fill=(14, 40, 120, 150))
    ImageDraw.Draw(intr).line([(-60, 96), (34, 58)], fill=(120, 160, 235, 90),
                              width=1)
    img = Image.alpha_composite(img, intr)

    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(body).polygon(PANEL_POLY, fill=WHITE + (255,))
    d = ImageDraw.Draw(body, "RGBA")

    d.line([(34, 1), (388, 1)], fill=WHITE + (130,), width=1)

    # ---- MARQUEE MASTHEAD ----
    kick = tracked_text_img("NOW SHOWING", 9, ROYAL, 4, alpha=130)
    body.alpha_composite(kick, (46, 12))
    # designed anchor rule under the masthead (v18.2 zone: global 24..296)
    d.line([(36, 294), (434, 294)], fill=ROYAL + (70,), width=1)
    d.rectangle([(36, 292), (42, 296)], fill=YELLOW + (200,))

    # the ONE structural rule: between description and facts.
    # v18.4.4: 425 -> 390 - the metadata stack moved up for the 4:3
    # media stage; the rule still sits between desc bottom (local 380)
    # and the year value (local 400).
    d.line([(36, 390), (434, 390)], fill=ROYAL + (90,), width=1)

    # baked kickers
    # v18.4.4: shifted up with the metadata stack (uniform 12px above
    # each value top). x positions unchanged.
    for text, xy in [("RELEASED", (42, 388)), ("RATING", (290, 388)),
                     ("GENRE", (42, 479)), ("PLAYERS", (42, 526)),
                     ("DEVELOPER", (234, 526)), ("SCREENSHOT", (42, 590))]:
        k = tracked_text_img(text, 9, SLATE, 4, alpha=130)
        body.alpha_composite(k, xy)

    # ---- SCREENSHOT slot: local (42,609)-(413,888) ----
    # v18.4.4: rebuilt for the true-4:3 maxSize stage (was the
    # (42,722)-(438,892) 2.33:1 strip). Shadow/hairline/corner track
    # the new region, same treatment as before.
    fsh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fsh).rectangle([44, 613, 415, 892], fill=(6, 14, 44, 30))
    body = Image.alpha_composite(body, fsh.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(body, "RGBA")
    d.line([(42, 888), (413, 888)], fill=ROYAL + (110,), width=1)
    d.line([(405, 601), (405, 615)], fill=YELLOW + (220,), width=2)
    d.line([(405, 601), (419, 601)], fill=YELLOW + (220,), width=2)

    # ---- gesture B: registration / blueprint motif ----
    # three registration crosses on one column: masthead (30,64),
    # description (30,348), screenshot top-right corner (421,607).
    # v18.4.4: the screenshot corner moved with the 4:3 stage
    # (was (446,720) for the old strip).
    # Then a quiet blueprint fragment in the right margin spanning
    # the description and screenshot sections.
    reg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(reg, "RGBA")
    for cx, cy in [(30, 64), (30, 348), (421, 607)]:
        reg_mark(rd, cx, cy, arm=7, color=ROYAL + (64,))
    # blueprint fragment: fine hairlines + ticks, right margin
    rd.line([(452, 330), (452, 884)], fill=DEEP + (16,), width=1)
    for y in (360, 470, 620, 780, 860):
        rd.line([(452, y), (462, y)], fill=DEEP + (20,), width=1)
        reg_mark(rd, 447, y + 34, arm=4, color=DEEP + (22,))
    body = Image.alpha_composite(body, reg)

    # the diagonal whisper (v17.9, kept) on its own layer
    wh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(wh).line([(294, 0), (470, 180)], fill=(10, 47, 160, 8),
                            width=2)
    body = Image.alpha_composite(body, wh)

    # halftone fragment, right edge, extended to span description AND
    # screenshot sections (was 340-560, now 340-880)
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halftone(deco, (428, 340, 458, 880), ROYAL, spacing=10, max_r=2.4,
             fade="left", alpha_max=20)

    body = Image.composite(body, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
    body = grain(body, mask)
    img = Image.alpha_composite(img, body)
    img = Image.alpha_composite(
        img, Image.composite(deco, Image.new("RGBA", (W, H), (0, 0, 0, 0)),
                             mask))
    p = os.path.join(ART, "lib_panel_main.png")
    img.save(p)
    print("lib_panel_main.png", img.size)


# ------------------------- 2. hero museum stage ------------------------
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
    img = img.filter(ImageFilter.GaussianBlur(18))

    # ultra-faint museum blueprint: concentric hairline circles,
    # N/S/E/W crosshair ticks, four corner registration marks.
    bp = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bp, "RGBA")
    BC = (30, 70, 170)
    for r in (150, 210, 270):
        bd.ellipse([c - r, c - r, c + r, c + r], outline=BC + (10,), width=1)
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        x1, y1 = c + 285 * math.cos(a), c + 285 * math.sin(a)
        x2, y2 = c + 305 * math.cos(a), c + 305 * math.sin(a)
        bd.line([(x1, y1), (x2, y2)], fill=BC + (14,), width=1)
    for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        cx, cy = c + sx * 340, c + sy * 340
        bd.line([(cx - 8, cy), (cx + 8, cy)], fill=BC + (20,), width=1)
        bd.line([(cx, cy - 8), (cx, cy + 8)], fill=BC + (20,), width=1)
    img = Image.alpha_composite(img, bp.filter(ImageFilter.GaussianBlur(1)))
    p = os.path.join(ART, "lib_plane_hero.png")
    img.save(p)
    print("lib_plane_hero.png", img.size)


# --------------------------- 3. spine rails ----------------------------
RAIL_PARAMS = {}

def gen_rail(system, name):
    W, H = 60, 912
    poly = [(0, 0), (42, 0), (60, 18), (60, 912), (18, 912), (0, 894)]
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    # 6px feathered left/right edges (v18, kept)
    ramp = Image.new("L", (W, 1), 0)
    rp = ramp.load()
    for x in range(W):
        rp[x, 0] = int(255 * min(x, W - 1 - x, 6) / 6)
    ramp = ramp.resize((W, H))
    mask = ImageChops.multiply(mask, ramp)
    # v18.2: ONE porous "window" band - the royal body alpha dips so the
    # Nova background collage continues across/behind the spine.
    # Band centre y=600, width 90, feathered 40px, floor alpha 170.
    win = Image.new("L", (W, H), 255)
    wp = win.load()
    cy, hw, feather, floor = 600, 45, 40, 170
    for y in range(H):
        d = abs(y - cy) - hw
        if d < 0:
            a = floor
        elif d < feather:
            a = int(floor + (255 - floor) * d / feather)
        else:
            a = 255
        for x in range(W):
            wp[x, y] = a
    mask = ImageChops.multiply(mask, win)

    top = (20, 60, 168, 255)
    bot = (8, 30, 108, 255)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
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
    img = Image.alpha_composite(
        img, Image.composite(tone, Image.new("RGBA", (W, H), (0, 0, 0, 0)),
                             mask))
    # v18.2: dotgrid REMOVED - the spine binds, it no longer textures.
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(52, 26), (52, 886)], fill=NAVY + (90,), width=1)

    OPTICAL_LIFT = 6
    logo_path = os.path.join(LOGOS, f"{system}.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        rot = logo.rotate(90, expand=True)
        rw, rh = rot.size
        scale = min(48.0 / rw, 720.0 / rh)
        rot = rot.resize((max(1, int(rw * scale)), max(1, int(rh * scale))),
                         Image.LANCZOS)
        ox, oy = (W - rot.width) // 2 + 2, (H - rot.height) // 2 - OPTICAL_LIFT
        pad = 22
        plate = Image.new("RGBA", (rot.width + pad * 2, rot.height + pad * 2),
                          (0, 0, 0, 0))
        pd = ImageDraw.Draw(plate, "RGBA")
        pd.rounded_rectangle([0, 0, plate.width, plate.height], radius=8,
                             fill=(8, 20, 70, 60))
        img.alpha_composite(plate, (ox - pad, oy - pad))
        white = Image.new("RGBA", rot.size, WHITE + (255,))
        white.putalpha(rot.split()[3])
        img.alpha_composite(white, (ox + 2, oy + 2))
        img.alpha_composite(rot, (ox, oy))
        RAIL_PARAMS[system] = dict(logo=(rot.width, rot.height),
                                   plate=(plate.width, plate.height), pad=pad,
                                   optical_lift=OPTICAL_LIFT, kind="logo")
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
        plate = Image.new("RGBA", (vert.width + pad * 2, vert.height + pad * 2),
                          (0, 0, 0, 0))
        pd = ImageDraw.Draw(plate, "RGBA")
        pd.rounded_rectangle([0, 0, plate.width, plate.height], radius=8,
                             fill=(8, 20, 70, 60))
        img.alpha_composite(plate, (ox - pad, oy - pad))
        shade = Image.new("RGBA", vert.size, NAVY + (255,))
        shade.putalpha(vert.split()[3])
        img.alpha_composite(shade, (ox + 2, oy + 2))
        img.alpha_composite(vert, (ox, oy))
        RAIL_PARAMS[system] = dict(logo=(vert.width, vert.height),
                                   plate=(plate.width, plate.height), pad=pad,
                                   optical_lift=OPTICAL_LIFT,
                                   kind="TEXT-FALLBACK")
        kind = "TEXT-FALLBACK"
    # ONE thin continuous yellow structural line at x=8, crisp outside the
    # feather zone - plus two connector ticks marking the window band so
    # the transparency reads engineered.
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(8, 44), (8, 888)], fill=YELLOW + (255,), width=1)
    for ty in (cy - hw, cy + hw):
        d.line([(5, ty), (11, ty)], fill=YELLOW + (255,), width=1)
    img = Image.composite(img, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
    img.save(os.path.join(RAILS, f"{system}.png"))
    return kind


if __name__ == "__main__":
    gen_panel()
    gen_plane()
    kinds = {}
    for system, name in SYSTEMS:
        kind = gen_rail(system, name)
        kinds[kind] = kinds.get(kind, 0) + 1
    print("rails:", kinds)
    with open(os.path.join(REPO, "work/rail_params_v18_2.json"), "w") as f:
        import json
        json.dump(RAIL_PARAMS, f, indent=1)
    print("rail params -> work/rail_params_v18_2.json")
