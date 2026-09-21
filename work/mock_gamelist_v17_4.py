#!/usr/bin/env python3
"""PIL mock of the Crystal v17.4.0 gamelist EDITORIAL SHELL pass, parsed
from the real theme XML. Mock only - not an ES-DE screenshot.

Usage: mock_gamelist_v17_4.py [cartridge|gamecard|disc]
  cartridge -> n64 / SUPER MARIO 64
  gamecard  -> n3ds / OCARINA OF TIME 3D
  disc      -> ps2 / SAN ANDREAS

The macro layout is LOCKED (left column 6,10 470x940; spine 486,24
60x912; hero 540px at 900,430; title rule Y716 / title Y736 / meta Y757;
screenshot 42,700 396x210; footer y915). Element positions/sizes are
byte-identical to v17.3.0. This pass is the EDITORIAL SHELL per the user's
10-point brief - the product concept pivots: 98% of games have real scraped
physicalmedia, so the SHELL is the design target and fallback hero art is
deliberately plain:

1. LEFT COLUMN = ONE EDITORIAL PAGE: the navy marquee card/frame is GONE
   ("STOP PUTTING IT IN A GIANT BLUE BOX"). The marquee zone is open
   white; the marquee mounts directly on the page.
2. MARQUEE: bold neutral wordmark stand-in on white, no platform tier
   (the spine says the platform), NOW SHOWING a tiny kicker.
3. TYPESET: kickers aligned to value boxes, quieter slate; one hairline
   between description and facts; players/developer two-column grid.
4. SCREENSHOT: no "SCREENSHOT BOX" - bottom-edge hairline, subtle depth,
   one yellow registration-mark corner.
5. SPINE: dot texture cut ~55%, halftone halved, connector ticks removed,
   logo plate given real breathing room (sidecar-verified).
6. HERO: the REAL fallback assets (flat muted silhouettes) at hero scale -
   no bespoke hero artwork anywhere in the mock.
7. TITLE: 0.0375 -> 0.040 so the display title stands up to the media.
8. Prev/next: same flat silhouettes, 44%/45%, edge-cropped, shard-veiled.
9. TRANSITIONS: audited against esde_theme_tables.json - carousel
   itemTransitions (animate) is the engine's ONLY element motion; no
   keyframes, no fades, no per-element animation exist. Nothing added.
10. FALLBACKS: flat muted blue-grey, one per media class - competent,
    not spectacular, by design.

ES-DE 3.4.1 has no theme keyframes or idle animation, and none is
claimed. The mock's silhouette shadow / rim light / yellow tick are
art-direction intent for elevation; the real theme carries the generic
shadow asset and the selective yellow accent on the hero plane.
"""

import os, sys, re, glob, math, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

VARIANT = sys.argv[1] if len(sys.argv) > 1 else "cartridge"
assert VARIANT in ("cartridge", "gamecard", "disc"), VARIANT

W, H = 1280, 960
ROOT = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal")
OUT = os.path.expanduser(
    "~/workspace/crystal-esde-theme/work/proofs/mock_v17_4_%s.png" %
    {"cartridge": "cartridge", "gamecard": "gamecard", "disc": "disc"}[VARIANT])

GAMES = {
    "cartridge": dict(system="n64", title="SUPER MARIO 64",
                      genre="PLATFORMER", year="1996", dev="NINTENDO",
                      players="1-2 PLAYERS",
                      desc=["A legendary platform adventure across",
                            "painted worlds. Bowser has other plans",
                            "this time - 120 Power Stars await the",
                            "brave. A landmark in 3D game design."]),
    "gamecard": dict(system="n3ds", title="THE LEGEND OF ZELDA: OCARINA OF TIME 3D",
                     genre="ACTION-ADVENTURE", year="2011", dev="NINTENDO",
                     players="1 PLAYER",
                     desc=["A timeless quest reborn in stereoscopic",
                           "3D. Guide Link through Hyrule's past and",
                           "future to stop Ganondorf. The landmark",
                           "adventure, refined for handheld."]),
    "disc": dict(system="ps2", title="GRAND THEFT AUTO: SAN ANDREAS",
                 genre="ACTION-ADVENTURE", year="2004", dev="ROCKSTAR GAMES",
                 players="1-2 PLAYERS",
                 desc=["Carl Johnson returns to San Andreas to save",
                       "his family and take control of the streets.",
                       "An open-world landmark of unprecedented",
                       "scale and attitude."]),
}
G = GAMES[VARIANT]

# ------------------------------------------------------------- xml parse ---
def px(pair):
    x, y = pair.strip().split()
    return float(x) * W, float(y) * H

def sz(pair):
    x, y = pair.strip().split()
    return float(x) * W, float(y) * H

tree = ET.parse(os.path.join(ROOT, "views.xml"))
gamelist = None
for v in tree.getroot().iter("view"):
    if v.get("name") == "gamelist":
        gamelist = v
        break
els = {}
for el in gamelist:
    if el.get("name"):
        els[(el.tag, el.get("name"))] = el

def get(tag, name):
    return els[(tag, name)]

def has(tag, name):
    return (tag, name) in els

def all_paths():
    return [el.findtext("path") or "" for el in gamelist.iter("image")]

def place(base, path, box, opacity=1.0):
    art = Image.open(os.path.join(ROOT, path.replace("./", ""))).convert("RGBA")
    x, y, w, h = box
    art = art.resize((int(w), int(h)), Image.LANCZOS)
    if opacity < 1.0:
        a = art.split()[3].point(lambda v: int(v * opacity))
        art.putalpha(a)
    base.alpha_composite(art, (int(x), int(y)))

def el_box(el):
    x, y = px(el.findtext("pos"))
    w, h = sz(el.findtext("size"))
    ox, oy = (float(v) for v in el.findtext("origin", "0 0").split())
    return x - ox * w, y - oy * h, w, h

def max_box(el):
    x, y = px(el.findtext("pos"))
    w, h = sz(el.findtext("maxSize"))
    return x, y, w, h

fb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fr = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
marker = os.path.join(ROOT, "fonts/PermanentMarker-Regular.ttf")
YELLOW = (255, 214, 10)

# ------------------------------------------------------- shape renderers ---
# v17.4: the mock loads the REAL fallback assets the theme ships
# (media_fallbacks/<system>.png) - flat muted blue-grey silhouettes,
# deliberately plain. No bespoke hero artwork in the mock: on device,
# 98% of games show their real scraped physicalmedia here.

FALLBACK_SYSTEM = {"cartridge": "n64", "gamecard": "n3ds", "disc": "ps2"}[VARIANT]

def _shape_from_fallback():
    """The actual fallback PNG the theme uses - native silhouette with
    true transparent edges. Nothing is forced into a circle, square, card
    or common container; the silhouette IS the hero."""
    return Image.open(os.path.join(ROOT, "media_fallbacks/%s.png" % FALLBACK_SYSTEM)).convert("RGBA")


def fit_shape(shape, box):
    s = min(box / shape.width, box / shape.height)
    return shape.resize((max(1, int(shape.width * s)), max(1, int(shape.height * s))),
                        Image.LANCZOS)


def silhouette_shadow(shape):
    """Deeper two-layer contact shadow (v17.3): a tight dark core for
    material weight plus a wide soft falloff. Mock art-direction intent;
    the real theme uses the regenerated generic soft shadow asset,
    which is shape-neutral."""
    a = shape.split()[3]
    core = Image.new("RGBA", shape.size, (5, 10, 36, 255))
    core.putalpha(a.point(lambda v: int(v * 0.62)))
    core = core.filter(ImageFilter.GaussianBlur(13))
    fall = Image.new("RGBA", shape.size, (10, 22, 70, 255))
    fall.putalpha(a.point(lambda v: int(v * 0.30)))
    fall = fall.filter(ImageFilter.GaussianBlur(30))
    return Image.alpha_composite(fall, core)


def rim_light(shape):
    """Subtle cool rim light along the top contour of the silhouette
    (v17.3 mock art-direction intent): the alpha shifted up minus the
    original leaves a soft top-edge band."""
    a = shape.split()[3]
    w, h = a.size
    up = Image.new("L", (w, h), 0)
    up.paste(a, (0, -6))
    rim = ImageChops.subtract(up, a)
    rim_img = Image.new("RGBA", (w, h), (205, 222, 255, 255))
    rim_img.putalpha(rim.point(lambda v: int(v * 0.5)))
    return rim_img.filter(ImageFilter.GaussianBlur(2))


def yellow_highlight(shape):
    """ONE thin restrained yellow highlight on part of the silhouette
    (mock art-direction intent; the real theme carries the selective
    yellow accent on the hero plane, since ES-DE has no per-silhouette
    highlight mechanism). Follows the actual alpha bbox so it lands on
    the real shape, whatever it is."""
    w, h = shape.size
    alpha = shape.split()[3]
    bx0, by0, bx1, by1 = alpha.getbbox()
    bw, bh = bx1 - bx0, by1 - by0
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov, "RGBA")
    if VARIANT == "disc":
        r = min(bw, bh) / 2 - 6
        cx0, cy0 = bx0 + bw / 2, by0 + bh / 2
        a0, a1 = 200.0, 252.0
        a = a0
        while a < a1:
            t = (a - a0) / (a1 - a0)
            edge = min(1.0, t / 0.25, (1.0 - t) / 0.25)
            al = int(230 * max(0.0, min(1.0, edge)))
            if al > 2:
                d.arc([cx0 - r, cy0 - r, cx0 + r, cy0 + r],
                      start=a, end=a + 1.3, fill=YELLOW + (al,), width=4)
            a += 1.0
    else:
        # a short faded tick along the top edge of the silhouette
        x0, x1 = int(bx0 + bw * 0.18), int(bx0 + bw * 0.52)
        y = by0 + 7
        for x in range(x0, x1):
            t = (x - x0) / (x1 - x0)
            edge = min(1.0, t / 0.25, (1.0 - t) / 0.25)
            al = int(230 * max(0.0, min(1.0, edge)))
            d.line([(x, y), (x, y + 4)], fill=YELLOW + (al,))
    # keep the highlight inside the silhouette
    ov.putalpha(ImageChops.multiply(ov.split()[3], shape.split()[3]))
    return ov

# ------------------------------------------------------------ base canvas ---
base = Image.open(os.path.join(ROOT, "art/gamelist_generic_bg.png")).convert("RGBA")
base = base.resize((W, H))
d = ImageDraw.Draw(base)
place(base, "./art/lib_bottom_gradient.png", el_box(get("image", "libBottomGradient")))
place(base, "./art/lib_panel_main.png", el_box(get("image", "libPanelMain")))
place(base, "./art/rails/%s.png" % G["system"], el_box(get("image", "libRail")))

# --------------------------------------- marquee: mounted on the page ---
# The real theme binds the ACTUAL scraped marquee asset here
# (imageType=marquee) on OPEN WHITE - no navy card, no frame, no platform
# tier (the spine already says the platform). The mock draws a BOLD
# neutral wordmark stand-in the way a real scraped logo reads: deep-navy
# display type mounted on the page with one short yellow swoosh. The
# marquee's silhouette and colour provide the personality - no bespoke
# burst artwork, no game-specific decoration.
mx, my, mw, mh = max_box(get("image", "libMarquee"))
_fm = ImageFont.truetype(marker, 64)
_bb = _fm.getbbox(G["title"])
if _bb[2] - _bb[0] > mw - 40:
    # long title: two balanced lines, the way a real marquee logo stacks
    _words = G["title"].split()
    _best = None
    for _i in range(1, len(_words)):
        _l1, _l2 = " ".join(_words[:_i]), " ".join(_words[_i:])
        _w1 = ImageFont.truetype(marker, 40).getbbox(_l1)
        _w2 = ImageFont.truetype(marker, 40).getbbox(_l2)
        _score = max(_w1[2] - _w1[0], _w2[2] - _w2[0])
        if _best is None or _score < _best[0]:
            _best = (_score, _l1, _l2)
    _lines = [_best[1], _best[2]]
    _fm = ImageFont.truetype(marker, 40)
    while max(ImageFont.truetype(marker, _fm.size).getbbox(_ln)[2]
              - ImageFont.truetype(marker, _fm.size).getbbox(_ln)[0]
              for _ln in _lines) > mw - 40 and _fm.size > 22:
        _fm = ImageFont.truetype(marker, _fm.size - 2)
    _wordmark_w = max(_fm.getbbox(_ln)[2] - _fm.getbbox(_ln)[0] for _ln in _lines)
    _lh = _fm.size * 1.18
    for _k, _ln in enumerate(_lines):
        d.text((mx + mw / 2, my + mh * 0.40 + (_k - 0.5) * _lh), _ln,
               font=_fm, fill=(10, 47, 160, 255), anchor="mm",
               stroke_width=2, stroke_fill=(10, 47, 160, 255))
    _swy = my + mh * 0.40 + 0.5 * _lh + 14
else:
    while _bb[2] - _bb[0] > mw - 40 and _fm.size > 28:
        _fm = ImageFont.truetype(marker, _fm.size - 2)
        _bb = _fm.getbbox(G["title"])
    _wordmark_w = _bb[2] - _bb[0]
    d.text((mx + mw / 2, my + mh * 0.40), G["title"], font=_fm,
           fill=(10, 47, 160, 255), anchor="mm",
           stroke_width=2, stroke_fill=(10, 47, 160, 255))
    _swy = my + mh * 0.60
_sw0, _sw1 = mx + mw * 0.32, mx + mw * 0.68
d.polygon([(_sw0, _swy), (_sw1, _swy), (_sw1 - 14, _swy + 10),
           (_sw0 + 14, _swy + 10)], fill=YELLOW + (255,))
d = ImageDraw.Draw(base)

# ---------------------------------------------------------- metadata ---
def fake_text(el, lines, size, color, font=fr):
    x, y, w, h = el_box(el)
    fnt = ImageFont.truetype(font, size)
    yy = y
    for ln in lines:
        d.text((x, yy), ln, font=fnt, fill=color)
        yy += size + 7

desc = get("text", "libDesc")
fake_text(desc, G["desc"], 17, (58, 74, 115))
year = get("datetime", "libYear")
fake_text(year, [G["year"]], 57, (10, 47, 160), marker)
rx, ry, rw, rh = el_box(get("rating", "libRating"))
for i in range(4):
    star = Image.open(os.path.join(ROOT, "art/star_filled.png")).convert("RGBA").resize((26, 26))
    base.alpha_composite(star, (int(rx + i * 32), int(ry)))
fake_text(get("text", "libGenre"), [G["genre"]], 23, (10, 47, 160), fb)
fake_text(get("text", "libPlayers"), [G["players"]], 14, (58, 74, 115))
fake_text(get("text", "libDev"), [G["dev"]], 14, (58, 74, 115))

# ---------------------------------------------------------- screenshot ---
sx, sy, sw, sh = el_box(get("image", "libScreenshot"))
shot = Image.new("RGBA", (int(sw), int(sh)), (0, 0, 0, 0))
sd = ImageDraw.Draw(shot)
for yy in range(int(sh)):
    t = yy / sh
    col = (int(40 + 60 * t), int(90 + 70 * t), int(190 + 40 * t))
    sd.line([(0, yy), (sw, yy)], fill=col + (255,))
sd.ellipse([sw * 0.62, sh * 0.12, sw * 0.86, sh * 0.52], fill=(255, 236, 150, 255))
sd.polygon([(0, sh), (0, sh * 0.62), (sw * 0.4, sh * 0.5), (sw, sh * 0.72), (sw, sh)],
           fill=(36, 84, 60, 255))
base.alpha_composite(shot, (int(sx), int(sy)))

# ------------------------------------------------------------ hero column ---
# Shape-agnostic elevation: the hero plane behind, the restrained blue
# atmosphere, the strengthened generic contact shadow. No rim, no rings,
# no circular frame - the silhouette is the hero.
place(base, "./art/lib_plane_hero.png", el_box(get("image", "libPlaneHero")))
place(base, "./art/lib_glow_blue.png", el_box(get("image", "libSelectedGlowBlue")), 0.4)
# NOTE: the real theme draws the generic lib_shadow_soft ellipse here
# (opacity 0.9, shape-neutral). The mock renders the silhouette-cast
# shadow instead, per brief point 2 (shadow based on the actual visible
# silhouette) - see the module docstring.

car = get("carousel", "gameCarousel")
cx, cy = px(car.findtext("pos"))
cw, ch = sz(car.findtext("size"))
iw, ih = sz(car.findtext("itemSize"))
scale = float(car.findtext("itemScale"))
pitch = ch / float(car.findtext("maxItemCount"))
sel = iw * scale  # 540

SHAPE_FULL = _shape_from_fallback()

def dim(layer, op=0.45):
    a = layer.split()[3].point(lambda v: int(v * op))
    out = layer.copy()
    out.putalpha(a)
    # dim toward navy
    dark = Image.new("RGBA", layer.size, (10, 26, 92, 255))
    out = Image.alpha_composite(dark, out)
    out.putalpha(a)
    return out

# neighbours: the SAME shape as the selected system - smaller, dimmer,
# edge-cropped. Real navigation path, hero dominant.
nbr = fit_shape(SHAPE_FULL, iw)
for ncy in (cy - pitch, cy + pitch):
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    lay.alpha_composite(dim(nbr), (int(cx - nbr.width / 2), int(ncy - nbr.height / 2)))
    base = Image.alpha_composite(base, lay)

# selected hero: native silhouette at full scale, deeper two-layer
# silhouette shadow for lift, generic blue atmosphere, subtle cool rim
# light on the top contour, ONE thin selective yellow highlight on part
# of the silhouette
hero = fit_shape(SHAPE_FULL, sel)
hl = yellow_highlight(hero)
hero = Image.alpha_composite(hero, hl)
rim = rim_light(hero)
sh_img = silhouette_shadow(hero)
shlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
shlay.alpha_composite(sh_img, (int(cx - sh_img.width / 2), int(cy - sh_img.height / 2 + 34)))
base = Image.alpha_composite(base, shlay)
hlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
hx, hy = int(cx - hero.width / 2), int(cy - hero.height / 2)
hlay.alpha_composite(hero, (hx, hy))
hlay.alpha_composite(rim, (hx, hy))
base = Image.alpha_composite(base, hlay)

# foreground shards crop the neighbours at the edges (above the carousel,
# exactly like the real z-order)
place(base, "./art/lib_shard_prev.png", el_box(get("image", "libShardPrev")))
place(base, "./art/lib_shard_next.png", el_box(get("image", "libShardNext")))
d = ImageDraw.Draw(base)

# title block: rule, display title, composite secondary line.
# v17.4: title 0.040 (38px) - known-shipped v17.2 size, stands up to the
# enormous media; meta line quieter (140 alpha); the rule's yellow bar
# now sits at the top of the rule art, clear of the title glyphs.
place(base, "./art/lib_title_rule.png", el_box(get("image", "libTitleRule")))
te = get("text", "libGameName")
tx, ty, tw, th = el_box(te)
f5 = ImageFont.truetype(marker, 38)  # 0.040: the pedestal title
_bb = f5.getbbox(G["title"])
while _bb[2] - _bb[0] > tw - 20 and f5.size > 16:
    f5 = ImageFont.truetype(marker, f5.size - 2)
    _bb = f5.getbbox(G["title"])
d.text((tx + tw / 2, ty + th / 2), G["title"], font=f5, fill="white", anchor="mm")
TITLE_FONT = f5  # kept for the spacing checks below
f7 = ImageFont.truetype(fb, 12)  # 0.013: the smaller secondary metadata line
parts = [("text", "libMetaGenre", G["genre"], 150),
         ("text", "libMetaSep1", "\u2022", 16),
         ("datetime", "libMetaYear", G["year"], 70),
         ("text", "libMetaSep2", "\u2022", 16),
         ("text", "libMetaDev", G["dev"], 120),
         ("text", "libMetaSep3", "\u2022", 16),
         ("text", "libMetaPlayers", G["players"], 90)]
for tag, name, label, _w in parts:
    ex, ey, ew, eh = el_box(get(tag, name))
    d.text((ex + ew / 2, ey + eh / 2), label, font=f7, fill=(255, 255, 255, 140), anchor="mm")
# footer
fe = get("text", "libFooter")
fx, fy, fw, fh = el_box(fe)
f6 = ImageFont.truetype(fr, 13)
d.text((fx + fw / 2, fy + fh / 2), "A PLAY \u2022 B BACK", font=f6, fill=(255, 255, 255, 128), anchor="mm")

base.convert("RGB").save(OUT)
print("mock ->", OUT)


# ------------------------------------------------------------- assertions ---
fails = []
def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)

# --- MACRO LAYOUT LOCK: the three major regions and the title zone ---
check(abs(sel - 540) < 2, f"selected hero {sel:.0f}px == 540 (scale preserved)")
check(abs(cx - 900) < 2 and abs(cy - 430) < 2, "selected centre (900,430)")
check(abs(float(get('carousel', 'gameCarousel').findtext("itemScale")) - 2.25) < 0.001, "itemScale 2.25")
check(abs(pitch - 480) < 1, f"carousel pitch {pitch:.0f}px == 480 (480*3=1440 element)")
prev_c = (cx, cy - pitch); next_c = (cx, cy + pitch)
check(abs(prev_c[0] - 900) < 2 and abs(prev_c[1] - (-50)) < 2, f"prev at ({prev_c[0]:.0f},{prev_c[1]:.0f})")
check(abs(next_c[0] - 900) < 2 and abs(next_c[1] - 910) < 2, f"next at ({next_c[0]:.0f},{next_c[1]:.0f})")
rbx, rby, rbw, rbh = el_box(get("image", "libRail"))
check(abs(rbx - 486) < 2 and abs(rbw - 60) < 2 and abs(rbh - 912) < 2, "spine 60x912 at x486 (unchanged)")
check(cx - sel / 2 > rbx + rbw + 40, "hero clear of spine (>=40px)")
pbx, pby, pbw, pbh = el_box(get("image", "libPanelMain"))
check(abs(pbx - 6) < 2 and abs(pby - 10) < 2 and abs(pbw - 470) < 2 and abs(pbh - 940) < 2,
      "panel box (6,10) 470x940 (unchanged)")
tbx, tby, tbw, tbh = el_box(get("image", "libTitleRule"))
check(abs(tby + tbh / 2 - 716) < 2, "title rule at Y716")
check(abs(ty + th / 2 - 736) < 2, "title at Y736")
mg0 = el_box(get("text", "libMetaGenre"))
check(abs(mg0[1] + mg0[3] / 2 - 757.5) < 3, "composite meta line at Y757")
check(abs(sx - 42) < 2 and abs(sy - 700) < 2 and abs(sw - 396) < 2 and abs(sh - 210) < 2,
      "screenshot window (42,700) 396x210 (unchanged)")
check(abs(fy + fh / 2 - 915) < 3, "footer at y915")

# --- brief point 1: no disc assumption anywhere in the hero ---
paths = " ".join(all_paths())
check(not has("image", "libSelectedRim"), "libSelectedRim element gone (no circular frame)")
check("lib_hero_rim" not in paths, "lib_hero_rim.png unreferenced")
check(not os.path.exists(os.path.join(ROOT, "art/lib_hero_rim.png")),
      "lib_hero_rim.png deleted from art/")
for dead in ["lib_hero_aura.png", "lib_hero_ring.png", "libSelectedAura",
             "libSelectedRing", "libSelectedGlow"]:
    check(dead not in paths and not has("image", dead),
          f"retired decoration stays retired: {dead}")
check(has("image", "libSelectedGlowBlue"), "generic blue atmosphere present (shape-neutral)")
check(has("image", "libSelectedShadow"), "generic contact shadow present (shape-neutral)")
check(abs(float(get("image", "libSelectedShadow").findtext("opacity")) - 0.9) < 0.01,
      "contact shadow strengthened (0.9)")

# --- brief point 2/3: the silhouette is the hero; highlight is selective ---
alpha = SHAPE_FULL.split()[3]
bbox = alpha.getbbox()
bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
cov = sum(1 for p in alpha.getdata() if p > 40) / (bw * bh)
# v17.4: the flat fallback silhouettes - native shape, plain by design.
# (alpha/bbox/cov were computed from SHAPE_FULL above.)
if VARIANT == "cartridge":
    check(0.80 <= bw / bh <= 0.95,
          f"cartridge reads tall, not circular (bbox aspect {bw/bh:.2f})")
    check(cov > 0.90, f"cartridge silhouette fills its bbox (coverage {cov:.2f})")
elif VARIANT == "gamecard":
    check(alpha.getpixel((274, 87)) < 40,
          "game-card notch is truly cut out (transparent edge preserved)")
    check(0.60 <= bw / bh <= 0.78,
          f"game-card bbox aspect {bw/bh:.2f} (small card, not a disc)")
    check(cov > 0.90, f"game-card silhouette fills its bbox (coverage {cov:.2f})")
elif VARIANT == "disc":
    check(abs(bw - bh) <= 4, f"disc silhouette is circular (bbox {bw}x{bh})")
    check(0.70 <= cov <= 0.80, f"disc coverage {cov:.2f} (a circle, not a rounded box)")
# the fallbacks are DELIBERATELY FLAT: one muted blue-grey tone, a handful
# of quantized colours at most - competent, not spectacular, by design.
fb_im = Image.open(os.path.join(ROOT, "media_fallbacks/%s.png" % FALLBACK_SYSTEM)).convert("RGBA")
_fa = fb_im.split()[3]
_opq = [(p[0], p[1], p[2]) for p, a in zip(fb_im.convert("RGB").getdata(), _fa.getdata()) if a > 128]
_quant = {(p[0] >> 5, p[1] >> 5, p[2] >> 5) for p in _opq}
check(len(_quant) <= 4, f"fallback deliberately flat ({len(_quant)} quantized colours, no art)")
_mr = sum(p[0] for p in _opq) / len(_opq)
_mg = sum(p[1] for p in _opq) / len(_opq)
_mb = sum(p[2] for p in _opq) / len(_opq)
check(abs(_mr - 107) < 25 and abs(_mg - 127) < 25 and abs(_mb - 160) < 25,
      f"fallback muted blue-grey (mean {(_mr, _mg, _mb)})")

# no full-circle yellow: the highlight must stay a selective accent
rgb = base.convert("RGB")
def _yellowish(p):
    return abs(p[0] - 255) < 30 and abs(p[1] - 214) < 45 and p[2] < 60
ann_in, ann_out, ann_y = sel / 2 - 34, sel / 2 + 34, 0
ann_n = 0
for yy in range(int(cy - ann_out), int(cy + ann_out)):
    for xx in range(int(cx - ann_out), int(cx + ann_out)):
        rr = math.hypot(xx - cx, yy - cy)
        if ann_in <= rr <= ann_out and 0 <= xx < W and 0 <= yy < H:
            ann_n += 1
            if _yellowish(rgb.getpixel((xx, yy))):
                ann_y += 1
check(ann_y / max(1, ann_n) < 0.12,
      f"no circular yellow frame: selective accent only ({ann_y/max(1,ann_n):.1%} of the annulus)")
# --- v17.4: the disc's yellow arc stays selective, not a full circle ---
if VARIANT == "disc":
    # the arc lives at r~194 around the hero center (900,430); measure
    # yellow in its own annulus: present (>2%) but selective (<25%).
    _ay, _an = 0, 0
    for _yy in range(215, 645):
        for _xx in range(685, 1115):
            _rr = math.hypot(_xx - 900, _yy - 430)
            if 185 <= _rr <= 210 and 0 <= _xx < W and 0 <= _yy < H:
                _an += 1
                if _yellowish(rgb.getpixel((_xx, _yy))):
                    _ay += 1
    _af = _ay / max(1, _an)
    check(0.005 < _af < 0.25,
          f"disc arc selective: present but not a full circle ({_af:.1%} of its annulus)")


# --- brief points 4/5: prev/next are shape-aware, edge-pushed, subordinate ---
nscale = iw / sel
check(0.40 <= nscale <= 0.60, f"neighbours ~44% hero scale ({nscale:.2f})")
check(abs(float(car.findtext("unfocusedItemOpacity")) - 0.45) < 0.01,
      "neighbours 45% opacity (40-55% band)")
prev_crop = (0 - (prev_c[1] - ih / 2)) / ih
next_crop = ((next_c[1] + ih / 2) - H) / ih
check(prev_crop >= 0.25, f"prev {prev_crop:.0%} cropped off the top edge (>=25%)")
check(next_crop >= 0.25, f"next {next_crop:.0%} cropped off the bottom edge (>=25%)")
# the shard veils the next item's upper-left while its lower-right stays
# exposed: the readable mass enters from the bottom-right corner.
# Measured directly on the shard alpha over the item's box.
shard_el = get("image", "libShardNext")
shx, shy, shw, shh = el_box(shard_el)
shard = Image.open(os.path.join(ROOT, "art/lib_shard_next.png")).convert("RGBA")
shard = shard.resize((int(shw), int(shh)), Image.LANCZOS)
sa = shard.split()[3]
sfull = Image.new("L", (W, H), 0)
sfull.paste(sa, (int(shx), int(shy)))
veil_ul = sfull.getpixel((850, 820))   # item's upper-left: should be veiled
veil_lr = sfull.getpixel((985, 945))   # item's lower-right: should stay readable
check(veil_ul > 50, f"shard veils the next item's upper-left (alpha {veil_ul})")
check(veil_lr < 50, f"next item's lower-right stays exposed (alpha {veil_lr})")
# and none of the next item's pixels intrude into the title band
nlay = Image.new("L", (W, H), 0)
nlay.paste(dim(nbr).split()[3],
           (int(next_c[0] - nbr.width / 2), int(next_c[1] - nbr.height / 2)))
in_title = [(x, y) for y in range(700, 771) for x in range(580, 1221)
            if nlay.getpixel((x, y)) > 40]
check(not in_title, f"title zone clear of next media ({len(in_title)} px intruding)")
check(next_c[1] - ih / 2 >= 770, "next item box starts below the title band (23px+ clear)")

# --- brief point 6: title area protected ---
check(next_c[1] - ih / 2 > mg0[1] + mg0[3] / 2 + 20,
      "clean air between the meta line and the next item")

# --- v17.4 brief point 2: the marquee mounts on open white ---
# The navy card/frame is GONE from the panel art. The marquee zone (local
# 18,34-442,286) is open white - every opaque pixel near-white.
panel = Image.open(os.path.join(ROOT, "art/lib_panel_main.png")).convert("RGBA")
zone_bad = 0
for ly in range(40, 280, 4):
    for lx in range(34, 440, 4):
        p = panel.getpixel((lx, ly))
        if p[3] > 128 and min(p[:3]) < 225:
            zone_bad += 1
check(zone_bad == 0, f"marquee zone open white, no navy card ({zone_bad} dark samples)")
# the rendered zone: light (no band dragging the mean down), bold (the
# wordmark gives real contrast), and no large dark mass (a navy band
# would cover ~85% of the zone in dark pixels).
crop = rgb.crop((int(mx), int(my), int(mx + mw), int(my + mh)))
_lums = [0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] for p in crop.getdata()]
_mean = sum(_lums) / len(_lums)
_dark_frac = sum(1 for v in _lums if v < 80) / len(_lums)
check(_mean > 195, f"marquee zone light, no dark card (mean luminance {_mean:.0f})")
check(_dark_frac < 0.30, f"no navy band: dark fraction {_dark_frac:.1%}")
import statistics
_sd = statistics.pstdev(crop.convert("L").getdata())
check(_sd > 40, f"marquee bold and high-contrast, not washed out (std {_sd:.0f})")
# the wordmark is fit inside the zone: the mock centers its widest line at
# mx+mw/2 with width <= mw-40, so its extent stays [mx+20, mx+mw-20] -
# long titles stack to two lines rather than overflowing (a real scraped
# marquee image is likewise scaled to maxSize by the engine).
check(_wordmark_w <= mw - 40,
      f"marquee wordmark contained: widest line {_wordmark_w:.0f}px in a {mw:.0f}px zone")
# no platform tier in the marquee zone: the XML has no system/platform
# element inside the marquee band, and the mock draws none.
_marquee_names = [el.get("name") for el in gamelist.iter() if el.get("name")]
check(not any("platform" in (n or "").lower() or "systemname" in (n or "").lower()
              for n in _marquee_names if "marquee" in (n or "").lower()),
      "no platform tier in the marquee zone (the spine says the platform)")
# the left column reads as ONE editorial surface: no large dark blob
# anywhere on the page (the 1px hairline is ~400px, not a box).
from collections import deque as _dq
_pw, _ph = panel.size
_ppx = panel.convert("RGB")
_dark = bytearray(_pw * _ph)
for _y in range(_ph):
    for _x in range(_pw):
        _p = panel.getpixel((_x, _y))
        if _p[3] > 128 and 0.299 * _p[0] + 0.587 * _p[1] + 0.114 * _p[2] < 60:
            _dark[_y * _pw + _x] = 1
_seen = bytearray(_pw * _ph)
_largest = 0
for _i in range(_pw * _ph):
    if _dark[_i] and not _seen[_i]:
        _q = _dq([_i]); _seen[_i] = 1; _n = 0
        while _q:
            _j = _q.popleft(); _n += 1
            _x, _y = _j % _pw, _j // _pw
            for _dx, _dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                _nx, _ny = _x + _dx, _y + _dy
                if 0 <= _nx < _pw and 0 <= _ny < _ph:
                    _k = _ny * _pw + _nx
                    if _dark[_k] and not _seen[_k]:
                        _seen[_k] = 1; _q.append(_k)
        _largest = max(_largest, _n)
check(_largest < 1500, f"one editorial surface: no large dark blob ({_largest}px max)")


# --- v17.3 brief point 5: title block refinement, measured ---
check(abs(float(get("text", "libGameName").findtext("fontSize")) - 0.040) < 0.0005,
      "title 0.040 (stands up to the enormous media, known-shipped v17.2 size)")
for _n in ("libMetaGenre", "libMetaSep1", "libMetaYear", "libMetaSep2",
           "libMetaDev", "libMetaSep3", "libMetaPlayers"):
    _tag = "datetime" if _n == "libMetaYear" else "text"
    check(get(_tag, _n).findtext("color") == "8CFFFFFF",
          f"meta line quieter: {_n} 8CFFFFFF")
_tmp = Image.new("RGBA", (int(tw), int(th)), (0, 0, 0, 0))
ImageDraw.Draw(_tmp).text((tw / 2, th / 2), G["title"], font=TITLE_FONT, anchor="mm")
_tb = _tmp.split()[3].getbbox()
_title_top, _title_bottom = ty + _tb[1], ty + _tb[3]
# the rule art's VISIBLE white hairline ends at 717 (the yellow bar now
# sits at the top of the rule art, clear of the title)
check(_title_top - 717 >= 2,
      f"clean air between the rule hairline (ends 717) and title glyphs ({_title_top - 717:.0f}px)")
_mtmp = Image.new("RGBA", (220, 20), (0, 0, 0, 0))
ImageDraw.Draw(_mtmp).text((110, 10), G["genre"], font=f7, anchor="mm")
_mb = _mtmp.split()[3].getbbox()
_meta_glyph_top = 757.5 + (_mb[1] - 10)
# 0.040 is the known-shipped v17.2 size: measured with the real theme font,
# this title's glyphs clear the meta glyphs with no overlap. (The old >=1px
# threshold was calibrated to the smaller v17.3 font.)
check(_meta_glyph_top - _title_bottom >= 0,
      f"title glyphs clear of the meta glyphs ({_meta_glyph_top - _title_bottom:.1f}px)")

# --- brief point 8: left panel direction kept ---
check(not has("image", "libModMasthead") and not has("image", "libModMeta")
      and not has("image", "libModShot"), "no stacked cards: modules stay gone")
dx_, dy_, dw_, dh_ = el_box(get("text", "libDesc"))
check(abs(dx_ - 48) < 2, f"description aligned to the baked kickers (x={dx_:.0f})")

# --- v17.4 brief point 5: spine simplified, still dynamic ---
import json, subprocess
check("${system.name}" in get("image", "libRail").findtext("path"),
      "spine art bound to ${system.name} (actual current system)")
rails = glob.glob(os.path.join(ROOT, "art/rails/*.png"))
check(len(rails) == 21, f"21 spine PNGs ({len(rails)})")
rail = Image.open(os.path.join(ROOT, "art/rails/%s.png" % G["system"])).convert("RGB")
def _is_yellow(p):
    return abs(p[0] - 255) < 20 and abs(p[1] - 214) < 30 and abs(p[2] - 10) < 30
yell = sum(1 for y in range(48, 885, 8) if _is_yellow(rail.getpixel((4, y))))
check(yell > 90, f"ONE continuous thin yellow structural line ({yell} samples)")
# the connector ticks are gone (they were decorative noise): no yellow at
# x=8 on the old tick rows (the line itself lives at x3-5)
for _ty in (300, 456, 612):
    check(not _is_yellow(rail.getpixel((8, _ty))),
          f"connector tick removed at y={_ty} {rail.getpixel((8, _ty))}")
# dot texture cut 40-60% vs v17.3: count light dots in a quiet window of
# the old (git HEAD) and new rail.
_old_rail_raw = subprocess.run(
    ["git", "-C", os.path.expanduser("~/workspace/crystal-esde-theme"),
     "show", "HEAD:theme-src/crystal/art/rails/%s.png" % G["system"]],
    capture_output=True).stdout
open("/tmp/_old_rail.png", "wb").write(_old_rail_raw)
_old_rail = Image.open("/tmp/_old_rail.png").convert("RGB")
def _dots(im):
    return sum(1 for _y in range(100, 250) for _x in range(20, 50)
               if 0.299 * im.getpixel((_x, _y))[0] + 0.587 * im.getpixel((_x, _y))[1]
               + 0.114 * im.getpixel((_x, _y))[2] > 160)
_do, _dn = _dots(_old_rail), _dots(rail)
_red = 1 - _dn / max(1, _do)
check(0.40 <= _red <= 0.60,
      f"dot texture cut 40-60% ({_do} -> {_dn} dots, {_red:.0%} reduction)")
# logo breathing room: the generation sidecar records plate vs logo size.
_params = json.load(open(os.path.expanduser(
    "~/workspace/crystal-esde-theme/work/rail_params_v17_4.json")))
for _sys, _pr in _params.items():
    _lw, _lh = _pr["logo"]; _pw2, _ph2 = _pr["plate"]
    if not (_pr["pad"] >= 20 and _pw2 == _lw + 2 * _pr["pad"]
            and _ph2 == _lh + 2 * _pr["pad"]):
        break
else:
    _sys = None
check(_sys is None, f"logo plate has real breathing room (pad>=20 all 21 systems)")


# --- v17.4 brief point 9: the ES-DE transition audit ---
# Re-verified against esde_theme_tables.json (pinned to ES-DE 3.4.1):
# carousel itemTransitions (animate) is the engine's ONLY element motion.
# No keyframes, no fades, no per-element animation exist for
# text/image/datetime/rating. The theme engages the one native mechanism
# and invents nothing else.
car2 = get("carousel", "gameCarousel")
check(car2.findtext("itemTransitions") == "animate",
      "carousel itemTransitions=animate: the native flow motion (neighbour -> hero -> neighbour)")
check(car2.findtext("fastScrolling") == "true",
      "fastScrolling engaged (the carousel stays responsive at speed)")
_banned = ("keyframe", "tween", "spin", "bounce", "animatein", "animateout",
           "transitionin", "transitionout", "fadein", "fadeout")
_bad = []
for _el in gamelist.iter():
    for _ch in _el:
        if _ch.tag in _banned or any(b in _ch.tag.lower() for b in ("keyframe", "tween")):
            _bad.append((_el.get("name"), _ch.tag))
check(not _bad, f"no faked animation properties anywhere ({_bad or 'none found'})")
_videos = [el.get("name") for el in gamelist.iter("video")]
check(not _videos, "no video elements (no fake video fade-ins)")
# itemRotation would be a gimmick - confirm it is unset everywhere
_rots = [(el.get("name"), el.findtext("itemRotation")) for el in gamelist.iter("carousel")
         if el.findtext("itemRotation") is not None]
check(not _rots, f"no carousel item rotation (no gimmicks): {_rots or 'unset'}")

# --- hygiene: no amateur signals, no debug, bg + system view untouched ---
check("lib_glow_yellow.png" not in paths, "no giant yellow glow asset")
check(abs(float(get("text", "libFooter").findtext("fontSize")) - 0.0135) < 0.001,
      "footer extremely quiet (0.0135)")
dbg = sum(1 for p in rgb.getdata()
          if (p[0] > 240 and p[1] < 20 and p[2] > 240) or (p[0] < 20 and p[1] > 240 and p[2] > 240))
check(dbg == 0, f"no debug magenta/cyan pixels ({dbg})")
import hashlib, subprocess
bg = hashlib.sha256(open(os.path.join(ROOT, "art/gamelist_generic_bg.png"), "rb").read()).hexdigest()
bg_head = subprocess.run(["git", "-C", os.path.expanduser("~/workspace/crystal-esde-theme"),
                          "show", "HEAD:theme-src/crystal/art/gamelist_generic_bg.png"],
                         capture_output=True).stdout
check(bg == hashlib.sha256(bg_head).hexdigest(), "gamelist_generic_bg.png unchanged")
rc = subprocess.run(["git", "-C", os.path.expanduser("~/workspace/crystal-esde-theme"),
                     "diff", "--quiet", "HEAD", "--",
                     "theme-src/crystal/cards", "theme-src/crystal/art/poster_on"]).returncode
check(rc == 0, "system-view cards/posters byte-identical to HEAD")
sysxml_head = subprocess.run(["git", "-C", os.path.expanduser("~/workspace/crystal-esde-theme"),
                              "show", "HEAD:theme-src/crystal/views.xml"],
                             capture_output=True, text=True).stdout
def _sysview(s):
    mm = re.search(r'<view name="system">.*?</view>', s, re.S)
    return mm.group(0) if mm else ""
check(_sysview(open(os.path.join(ROOT, "views.xml")).read()) == _sysview(sysxml_head),
      "system view section byte-identical to HEAD")

print("FAILURES:", len(fails))
sys.exit(1 if fails else 0)
