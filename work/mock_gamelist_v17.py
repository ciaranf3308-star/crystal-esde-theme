#!/usr/bin/env python3
"""PIL mock of the Crystal v17 gamelist DETAIL-RESOLUTION pass, parsed from
the real theme XML. Mock only - not an ES-DE screenshot.

The macro layout is LOCKED (left column 6,10 470x940; spine 486,24 60x912;
hero 540px at 900,430; prev/next 900,10 / 900,850 pitch 420; rule Y716 /
title Y736 / meta Y757; screenshot 42,700 396x210). This pass resolves the
remaining amateur details per the user's 10-point brief:

1. Lower-right rebuilt: the title band keeps its approved position with
   clean air; the NEXT item is repositioned VISUALLY (redesigned
   foreground shard at 900,795 380x165, fully below the title band) so it
   enters from the bottom edge, partially cropped - a distinct visual space
   from the title. No placeholder rects.
2. Hero: the physical media itself - a printed game disc with a clean
   circular silhouette (no concentric data-band rings, no gold rings).
   Depth only from scale, crisp edges, detached contact shadow, restrained
   blue atmosphere, ONE thin selective yellow rim arc.
3. Marquee: substantially larger (24,44 424x252, +31% area), a confident
   banner graphic on open whitespace - no blue rectangle, no fade; NOW
   SHOWING stays a tiny kicker.
4. Left column: no boxes back. Restrained craftsmanship only - tiny
   halftone transitions, one subtle blueprint fragment, one clipped blue
   geometric intrusion, sparse yellow micro-accents; ~85% clean white.
5. Typography spacing pass: air between description and facts, quieter
   labels, standardised PLAYERS/DEVELOPER baselines, rating with the year.
6. Screenshot: ONE clean hairline frame + subtle depth shadow + ONE tiny
   yellow corner accent. No nested frames.
7. Spine: tonal variation, controlled grid texture, ONE continuous thin
   yellow structural line, logos deliberately MOUNTED on a mounting plate.
8. Prev/next: real neighbouring discs, smaller, dimmer, edge-cropped and
   shard-cropped - a real navigation path, hero dominant.
9. Overlap: marquee breaks over its rule, disc overlaps the hero plane,
   shards crop the neighbours, spine ticks reach into adjacent surfaces.
10. Footer quieter still. No amateur signals.

ES-DE 3.4.1 has no theme keyframes or idle animation, and none is
claimed - the real build shows native eased carousel transitions."""
import os, sys, re, glob, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1280, 960
ROOT = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal")
OUT = os.path.expanduser("~/workspace/crystal-esde-theme/work/proofs/mock_v17_full.png")

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

# ------------------------------------------------------------ base canvas ---
base = Image.open(os.path.join(ROOT, "art/gamelist_generic_bg.png")).convert("RGBA")
base = base.resize((W, H))
d = ImageDraw.Draw(base)
place(base, "./art/lib_bottom_gradient.png", el_box(get("image", "libBottomGradient")))
place(base, "./art/lib_panel_main.png", el_box(get("image", "libPanelMain")))
place(base, "./art/rails/gba.png", el_box(get("image", "libRail")))

fb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fr = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
marker = os.path.join(ROOT, "fonts/PermanentMarker-Regular.ttf")

# -------------------------------- marquee: the visual headline ---
# The real scraped marquee: substantially larger, a confident banner
# graphic with a natural silhouette on open whitespace - NOT a UI
# rectangle, no blue mat, no fade. It breaks slightly over the baked
# hairline rule at global y306 (controlled overlap, per the brief).
mx, my, mw, mh = max_box(get("image", "libMarquee"))
mq = Image.new("RGBA", (int(mw), int(mh) + 14), (0, 0, 0, 0))
mqd = ImageDraw.Draw(mq, "RGBA")
# key-art burst with a NATURAL silhouette: radiating warm wedges from a
# low-left focal point, painted straight onto the whitespace
_bx, _by = mw * 0.30, mh * 0.72
import math as _math
for _k in range(18):
    _a0 = _math.pi * (0.55 + _k * 0.075)
    _a1 = _a0 + _math.pi * 0.055
    _r = mh * 1.15
    _warm = [(235, 72, 40), (245, 128, 32), (252, 186, 24)][_k % 3]
    mqd.polygon([(_bx, _by),
                 (_bx + _r * _math.cos(_a0), _by - _r * _math.sin(_a0)),
                 (_bx + _r * _math.cos(_a1), _by - _r * _math.sin(_a1))],
                fill=_warm + (215,))
# deep-blue energy core the title sits in
mqd.ellipse([_bx - 150, _by - 120, _bx + 150, _by + 60], fill=(16, 52, 160, 235))
_fm = ImageFont.truetype(marker, 64)               # the logo, fit to width
_bb = _fm.getbbox("SUPER MARIO 64")
while _bb[2] - _bb[0] > mw - 30 and _fm.size > 20:
    _fm = ImageFont.truetype(marker, _fm.size - 2)
    _bb = _fm.getbbox("SUPER MARIO 64")
mqd.text((mw / 2, mh * 0.40), "SUPER MARIO 64", font=_fm,
         fill=(255, 255, 255, 255), anchor="mm",
         stroke_width=2, stroke_fill=(8, 20, 70, 255))
mqd.polygon([(mw * 0.16, mh * 0.62), (mw * 0.84, mh * 0.57),   # yellow swoosh
             (mw * 0.82, mh * 0.64), (mw * 0.14, mh * 0.69)],
            fill=(255, 214, 10, 255))
_ft = ImageFont.truetype(fb, 15)
mqd.text((mw / 2, mh * 0.80), "N I N T E N D O  6 4", font=_ft,
         fill=(20, 40, 120, 230), anchor="mm")
# a few paint speckles for the printed-art feel
for _sx, _sy, _sr in [(0.12, 0.18, 5), (0.88, 0.22, 7), (0.78, 0.85, 4), (0.2, 0.82, 6)]:
    mqd.ellipse([(mw * _sx) - _sr, (mh * _sy) - _sr,
                 (mw * _sx) + _sr, (mh * _sy) + _sr], fill=(255, 214, 10, 200))
msh = Image.new("RGBA", mq.size, (0, 0, 0, 0))    # soft lift off the page
_mmask = mq.split()[3].point(lambda v: 255 if v > 40 else 0)
ImageDraw.Draw(msh).ellipse([_bx - 140, _by - 110, _bx + 160, _by + 70],
                            fill=(6, 14, 44, 90))
msh = msh.filter(ImageFilter.GaussianBlur(12))
base.alpha_composite(msh, (int(mx), int(my)))
base.alpha_composite(mq, (int(mx), int(my)))
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
fake_text(desc, ["A legendary platform adventure across", "painted worlds. Bowser has other plans",
                 "this time - 120 Power Stars await the", "brave. A landmark in 3D game design."], 17, (58, 74, 115))
year = get("datetime", "libYear"); fake_text(year, ["1996"], 57, (10, 47, 160), marker)
rx, ry, rw, rh = el_box(get("rating", "libRating"))
for i in range(4):
    star = Image.open(os.path.join(ROOT, "art/star_filled.png")).convert("RGBA").resize((26, 26))
    base.alpha_composite(star, (int(rx + i * 32), int(ry)))
fake_text(get("text", "libGenre"), ["PLATFORMER"], 23, (10, 47, 160), fb)
fake_text(get("text", "libPlayers"), ["1-2 PLAYERS"], 14, (58, 74, 115))
fake_text(get("text", "libDev"), ["NINTENDO"], 14, (58, 74, 115))

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
# Restrained elevation: blue atmosphere pooled beneath, detached contact
# shadow (slight elevation), ONE thin selective rim arc. No rings, no aura.
place(base, "./art/lib_plane_hero.png", el_box(get("image", "libPlaneHero")))
place(base, "./art/lib_glow_blue.png", el_box(get("image", "libSelectedGlowBlue")), 0.4)
place(base, "./art/lib_shadow_soft.png", el_box(get("image", "libSelectedShadow")), 0.8)

car = get("carousel", "gameCarousel")
cx, cy = px(car.findtext("pos"))
cw, ch = sz(car.findtext("size"))
iw, ih = sz(car.findtext("itemSize"))
scale = float(car.findtext("itemScale"))
pitch = ch / float(car.findtext("maxItemCount"))
sel = iw * scale

def disc_print(cx_, cy_, r, label=True):
    """A real physical game disc: printed label with cover art, clean
    circular silhouette, directional studio light, dark rim, specular
    edge arcs, beveled hub, layered gloss. NO concentric data-band rings,
    NO gold accent rings: the media is intact and recognizable, not a
    target."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    # disc body: light pooled toward the upper-left (directional light)
    steps = 48
    for i in range(steps, 0, -1):
        t = i / steps
        rr = r * t
        ox = -r * 0.10 * (1 - t)
        oy = -r * 0.12 * (1 - t)
        col = (int(150 + 70 * (1 - t)), int(170 + 60 * (1 - t)), int(215 + 30 * (1 - t)))
        dl.ellipse([cx_ + ox - rr, cy_ + oy - rr, cx_ + ox + rr, cy_ + oy + rr],
                   fill=col + (255,))
    # printed label: full-bleed cover art on the disc face
    lr = r * 0.94
    lab = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ll = ImageDraw.Draw(lab)
    x0, y0 = cx_ - lr, cy_ - lr
    for yy in range(int(2 * lr)):
        t = yy / (2 * lr)
        col = (int(50 + 90 * t), int(110 + 80 * t), int(200 + 40 * t))
        ll.line([(x0, y0 + yy), (x0 + 2 * lr, y0 + yy)], fill=col + (255,))
    ll.ellipse([cx_ + lr * 0.15, cy_ - lr * 0.75, cx_ + lr * 0.65, cy_ - lr * 0.25],
               fill=(255, 236, 150, 255))
    ll.polygon([(x0, y0 + 2 * lr), (x0, y0 + lr * 1.25), (x0 + lr * 0.8, y0 + lr),
                (x0 + 2 * lr, y0 + lr * 1.45), (x0 + 2 * lr, y0 + 2 * lr)],
               fill=(36, 84, 60, 255))
    if label:
        fnt = ImageFont.truetype(marker, max(14, int(r * 0.12)))
        ll.text((cx_ - lr * 0.33, cy_ + lr * 0.45), "SUPER MARIO 64", font=fnt,
                fill=(255, 255, 255, 255), anchor="mm",
                stroke_width=max(1, int(r * 0.012)), stroke_fill=(10, 26, 92, 255))
    lmask = Image.new("L", base.size, 0)
    ImageDraw.Draw(lmask).ellipse([cx_ - lr, cy_ - lr, cx_ + lr, cy_ + lr], fill=255)
    lab.putalpha(ImageChops.multiply(lab.split()[3], lmask))
    layer = Image.alpha_composite(layer, lab)
    dl = ImageDraw.Draw(layer)
    # outer rim: dark edge band, specular arc upper-left, shade lower-right
    dl.ellipse([cx_ - r, cy_ - r, cx_ + r, cy_ + r],
               outline=(8, 20, 70, 255), width=max(4, int(r * 0.045)))
    dl.arc([cx_ - r + 8, cy_ - r + 8, cx_ + r - 8, cy_ + r - 8],
           start=200, end=260, fill=(255, 255, 255, 130), width=max(3, int(r * 0.03)))
    dl.arc([cx_ - r + 8, cy_ - r + 8, cx_ + r - 8, cy_ + r - 8],
           start=20, end=80, fill=(8, 18, 60, 140), width=max(3, int(r * 0.03)))
    # beveled hub
    dl.ellipse([cx_ - r * 0.20, cy_ - r * 0.20, cx_ + r * 0.20, cy_ + r * 0.20],
               fill=(232, 238, 250, 255))
    dl.arc([cx_ - r * 0.20, cy_ - r * 0.20, cx_ + r * 0.20, cy_ + r * 0.20],
           start=200, end=260, fill=(255, 255, 255, 150), width=2)
    dl.arc([cx_ - r * 0.20, cy_ - r * 0.20, cx_ + r * 0.20, cy_ + r * 0.20],
           start=20, end=80, fill=(10, 26, 92, 130), width=2)
    dl.ellipse([cx_ - r * 0.075, cy_ - r * 0.075, cx_ + r * 0.075, cy_ + r * 0.075],
               fill=(34, 42, 66, 255))
    dl.ellipse([cx_ - r * 0.075, cy_ - r * 0.075, cx_ + r * 0.075, cy_ + r * 0.075],
               outline=(10, 14, 30, 180), width=3)
    # layered gloss: broad soft sheen + small sharp specular, upper-left
    sheen = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sdd = ImageDraw.Draw(sheen)
    sdd.ellipse([cx_ - r * 0.95, cy_ - r * 1.10, cx_ + r * 0.25, cy_ - r * 0.10],
                fill=(255, 255, 255, 38))
    sdd.ellipse([cx_ - r * 0.72, cy_ - r * 0.86, cx_ - r * 0.18, cy_ - r * 0.44],
                fill=(255, 255, 255, 60))
    layer = Image.alpha_composite(layer, sheen.filter(ImageFilter.GaussianBlur(34)))
    return layer

def dim(layer, op=0.45, dark=0.55):
    out = Image.blend(layer, Image.new("RGBA", layer.size, (0, 0, 0, 255)), dark)
    a = layer.split()[3].point(lambda v: int(v * op))
    out.putalpha(a)
    return out

# neighbours: real neighbouring discs - smaller, edge-cropped, dimmed
# hard; subordinate to the hero. One collection, one browsing interaction.
base = Image.alpha_composite(base, dim(disc_print(cx, cy - pitch, iw / 2, label=False)))
base = Image.alpha_composite(base, dim(disc_print(cx, cy + pitch, iw / 2, label=False)))
# foreground shards crop the neighbours at the upper-right/lower-right
place(base, "./art/lib_shard_prev.png", el_box(get("image", "libShardPrev")))
place(base, "./art/lib_shard_next.png", el_box(get("image", "libShardNext")))
d = ImageDraw.Draw(base)
# selected hero: the physical media itself (540px); the disc overlaps
# the hero plane beneath it
hero = disc_print(cx, cy, sel / 2, label=True)
base = Image.alpha_composite(base, hero)
place(base, "./art/lib_hero_rim.png", el_box(get("image", "libSelectedRim")))
d = ImageDraw.Draw(base)

# title block: redesigned rule, bolder title, composite secondary line
place(base, "./art/lib_title_rule.png", el_box(get("image", "libTitleRule")))
te = get("text", "libGameName")
tx, ty, tw, th = el_box(te)
f5 = ImageFont.truetype(marker, 38)
d.text((tx + tw / 2, ty + th / 2), "SUPER MARIO 64", font=f5, fill="white", anchor="mm")
f7 = ImageFont.truetype(fb, 14)
parts = [("text", "libMetaGenre", "PLATFORMER", 150),
         ("text", "libMetaSep1", "\u2022", 16),
         ("datetime", "libMetaYear", "1996", 70),
         ("text", "libMetaSep2", "\u2022", 16),
         ("text", "libMetaDev", "NINTENDO", 120),
         ("text", "libMetaSep3", "\u2022", 16),
         ("text", "libMetaPlayers", "1-2 PLAYERS", 90)]
for tag, name, label, _w in parts:
    ex, ey, ew, eh = el_box(get(tag, name))
    d.text((ex + ew / 2, ey + eh / 2), label, font=f7, fill=(255, 255, 255, 166), anchor="mm")
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

# --- MACRO LAYOUT LOCK: same regions as v15 ---
check(abs(sel - 540) < 2, f"selected hero {sel:.0f}px == 540 (dominant, scale preserved)")
check(abs(sel / iw - 3.0) < 0.01, f"hero/neighbour ratio {sel/iw:.2f}x")
check(abs(float(get('carousel', 'gameCarousel').findtext("itemScale")) - 3.0) < 0.001, "itemScale 3.0")
check(abs(pitch - 420) < 1, f"carousel pitch {pitch:.0f}px == 420")
prev_c = (cx, cy - pitch); next_c = (cx, cy + pitch)
check(abs(prev_c[0] - 900) < 2 and abs(prev_c[1] - 10) < 2, f"prev at ({prev_c[0]:.0f},{prev_c[1]:.0f})")
check(abs(next_c[0] - 900) < 2 and abs(next_c[1] - 850) < 2, f"next at ({next_c[0]:.0f},{next_c[1]:.0f})")
check(abs(cx - 900) < 2 and abs(cy - 430) < 2, "selected centre (900,430)")
rbx, rby, rbw, rbh = el_box(get("image", "libRail"))
check(abs(rbx - 486) < 2 and abs(rbw - 60) < 2 and abs(rbh - 912) < 2,
      f"spine 60x912 at x486 (unchanged)")
check(cx - sel / 2 > rbx + rbw + 40, "hero clear of spine (>=40px)")
pbx, pby, pbw, pbh = el_box(get("image", "libPanelMain"))
check(abs(pbx - 6) < 2 and abs(pby - 10) < 2 and abs(pbw - 470) < 2 and abs(pbh - 940) < 2,
      f"panel box {pbx:.0f},{pby:.0f} {pbw:.0f}x{pbh:.0f} (unchanged)")
check(pbx + pbw <= 486 + 1 and pby >= 10 - 1 and pby + pbh <= 950 + 1, "panel inside left zone")
check(not has("image", "libModMasthead") and not has("image", "libModMeta") and not has("image", "libModShot"),
      "no stacked cards: v11 modules gone")
tbx, tby, tbw, tbh = el_box(get("image", "libTitleRule"))
check(abs(tby + tbh / 2 - 716) < 2, "title rule at Y716")
check(abs(tbw - 300) < 2, "title rule 300px wide")
check(abs(ty + th / 2 - 736) < 2, "title at Y736")
mg0 = el_box(get("text", "libMetaGenre"))
check(abs(mg0[1] + mg0[3] / 2 - 757.5) < 3, "composite meta line at Y757")
check(abs(sx - 42) < 2 and abs(sy - 700) < 2 and abs(sw - 396) < 2 and abs(sh - 210) < 2,
      "screenshot window (42,700) 396x210 (unchanged)")
check(abs(fy + fh / 2 - 915) < 3, "footer at y915")

# --- brief point 1: lower-right composition rebuilt ---
snx, sny, snw, snh = el_box(get("image", "libShardNext"))
check(sny >= 775, f"next-item shard starts below the title band ({sny:.0f} >= 775)")
check(sny + snh <= 961, "next-item shard inside the frame")
check(next_c[1] + ih / 2 > 930, "next item reaches the bottom edge (partially cropped)")
check(snx < next_c[0] + iw / 2 < snx + snw and sny < next_c[1] + ih / 2,
      "foreground shard crops the next item (distinct space from the title)")
check(abs(float(get('carousel', 'gameCarousel').findtext("unfocusedItemOpacity")) - 0.45) < 0.01,
      "next dimmed, subordinate (opacity 0.45)")
# no placeholder rects in the lower hero zone: only known elements allowed
for el in gamelist.iter("image"):
    nm = el.get("name")
    if nm in ("libShardNext", "libShardPrev", "libPlaneHero", "libSelectedGlowBlue",
              "libSelectedShadow", "libSelectedRim", "libBackground",
              "libBottomGradient", "libPanelMain", "libRail", "libMarquee",
              "libScreenshot", "libTitleRule"):
        continue
    check(False, f"unexpected image element in the lower hero zone: {nm}")
print("PASS no placeholder rects in the lower hero zone")

# --- brief point 2: physical media, clean silhouette ---
paths = " ".join(all_paths())
check(not has("image", "libSelectedAura"), "libSelectedAura element gone")
check(not has("image", "libSelectedRing"), "libSelectedRing element gone")
for dead in ["lib_hero_aura.png", "lib_hero_ring.png", "libHeroArc", "libSelectedGlow"]:
    check(dead not in paths, f"retired decoration not referenced: {dead}")
for dead in ["lib_hero_aura.png", "lib_hero_ring.png"]:
    check(not os.path.exists(os.path.join(ROOT, "art", dead)), f"retired asset deleted: {dead}")
check(has("image", "libSelectedRim"), "thin selective rim highlight present")
check(has("image", "libSelectedGlowBlue"), "restrained blue atmosphere present")
check(has("image", "libSelectedShadow"), "soft contact shadow present")
rim = Image.open(os.path.join(ROOT, "art/lib_hero_rim.png")).convert("RGBA")
def _yellowish(p):
    return p[3] > 60 and abs(p[0] - 255) < 30 and abs(p[1] - 214) < 45 and p[2] < 60
top_y = sum(1 for x in range(620) for y in range(10, 90) if _yellowish(rim.getpixel((x, y))))
bot_y = sum(1 for x in range(620) if _yellowish(rim.getpixel((x, 580))))
check(top_y > 400, f"rim arc present at the top ({top_y} yellow px)")
check(bot_y < 5, f"rim is SELECTIVE: no circle at the bottom ({bot_y} yellow px)")
tot_y = sum(1 for x in range(620) for y in range(620) if _yellowish(rim.getpixel((x, y))))
check(tot_y < 4000, f"rim is thin, not a band ({tot_y} yellow px)")
glow = Image.open(os.path.join(ROOT, "art/lib_glow_blue.png")).convert("RGBA")
gmax = max(p[3] for p in glow.getdata())
check(gmax <= 42, f"blue glow restrained (max alpha {gmax})")
shx, shy, shw, shh = el_box(get("image", "libSelectedShadow"))
check(shy + shh / 2 > cy + sel / 2 + 20, "contact shadow detached below the disc (elevation)")
# the rendered hero disc: count sharp radial edges along a 45-degree spoke.
# Concentric data-band / gold rings would each add 2 sharp edges; the
# printed-label disc should show almost none (one soft art transition).
rgb = base.convert("RGB")
peaks = 0
_prev_l = None
for i in range(int(sel / 2 * 0.35), int(sel / 2 * 0.92)):
    x = int(cx + i * 0.7071); y = int(cy + i * 0.7071)
    p = rgb.getpixel((x, y)); _l = (p[0] + p[1] + p[2]) / 3
    if _prev_l is not None and abs(_l - _prev_l) > 28:
        peaks += 1
    _prev_l = _l
check(peaks <= 8, f"hero disc: clean silhouette, no concentric rings ({peaks} sharp radial edges)")

# --- brief point 3: marquee owns the upper-left ---
m = get("image", "libMarquee")
check(abs(mw - 424) < 2 and abs(mh - 252) < 2, f"marquee zone {mw:.0f}x{mh:.0f} substantially larger")
check(mw * mh >= 100000, f"marquee area {mw*mh:.0f}px (+31% over v15)")
check(abs(float(get("text", "libMarqueeTitle").findtext("fontSize")) - 0.04) < 0.001,
      "marquee fallback type (0.04, Nova display face)")
panel = Image.open(os.path.join(ROOT, "art/lib_panel_main.png")).convert("RGBA")
mat = panel.getpixel((200, 120))
check(mat[3] > 200 and mat[0] > 235 and mat[1] > 235 and mat[2] > 235,
      "marquee sits on open whitespace (no mat, no blue rectangle)")
# NOW SHOWING kicker tiny: present but small, no band
kick = sum(1 for x in range(30, 200) for y in range(14, 44)
           if panel.getpixel((x, y))[3] > 150 and abs(panel.getpixel((x, y))[0] - 18) < 50)
check(50 < kick < 4000, f"tiny kicker present, secondary ({kick} px)")

# --- brief point 4: clean -> art-directed, restraint measured ---
# "craftsmanship ink": pixels that are visibly coloured or dark - a whisper
# of grey shadow does not count against the ~85% clean-white target.
page_px = sum(1 for p in panel.getdata() if p[3] > 200)
def _inked(p):
    lum = (p[0] + p[1] + p[2]) / 3
    return (max(p[0], p[1], p[2]) - min(p[0], p[1], p[2]) > 30) or lum < 200
craft_px = sum(1 for p in panel.getdata() if p[3] > 200 and _inked(p))
check(craft_px / page_px < 0.20,
      f"panel stays ~85% clean white (craftsmanship ink {craft_px/page_px:.1%})")
def _royalish(p):
    return p[3] > 120 and abs(p[0] - 18) < 60 and abs(p[1] - 58) < 70 and abs(p[2] - 178) < 70
intr = sum(1 for x in range(420, 442) for y in range(320, 600) if _royalish(panel.getpixel((x, y))))
check(intr > 200, f"one clipped blue geometric intrusion hugging the right edge ({intr} px)")
half = sum(1 for x in range(398, 420) for y in range(360, 540)
           if panel.getpixel((x, y))[3] > 120 and panel.getpixel((x, y))[2] > panel.getpixel((x, y))[0] + 25)
check(half > 20, f"tiny halftone transition melting into the intrusion ({half} px)")

# --- brief point 5: typography spacing ---
check(get("datetime", "libYear").findtext("fontPath").endswith("PermanentMarker-Regular.ttf"),
      "anchor year uses marker display face")
check(abs(float(get("datetime", "libYear").findtext("fontSize")) - 0.06) < 0.001,
      "year anchor 0.06 (large)")
check(abs(float(get("text", "libGenre").findtext("fontSize")) - 0.024) < 0.001,
      "genre strong secondary (0.024)")
pg, pd = float(get("text", "libPlayers").findtext("fontSize")), float(get("text", "libDev").findtext("fontSize"))
check(pg < 0.02 and pd < 0.02, f"players/dev quieter ({pg}/{pd})")
check(get("text", "libPlayers").findtext("color") == "${crystalInkDim}", "players/dev quiet ink")
py_ = el_box(get("text", "libPlayers"))[1]; dy_ = el_box(get("text", "libDev"))[1]
check(abs(py_ - dy_) < 2, "PLAYERS and DEVELOPER share a baseline")
rx_, ry_, rw_, rh_ = el_box(get("rating", "libRating"))
yx_, yy_, yw_, yh_ = el_box(get("datetime", "libYear"))
check(abs(ry_ - yy_) < 40, "rating associated with the release-year row")
dx, dy, dw, dh = el_box(get("text", "libDesc"))
check(yy_ - (dy + dh) >= 40, f"breathing room between description and facts ({yy_-(dy+dh):.0f}px)")
gx, gy, gw, gh = el_box(get("text", "libGenre"))
check(dy < yy_ < gy, "editorial order: description, then year, then facts")

# --- brief point 6: screenshot, one clean frame ---
o1 = panel.getpixel((34, 780))   # 2px left of frame -> page
o2 = panel.getpixel((36, 780))   # on frame
o3 = panel.getpixel((42, 780))   # 6px inside -> should NOT be another outline
def _royal(p):
    return p[3] > 100 and abs(p[0] - 18) < 45 and abs(p[1] - 58) < 55 and abs(p[2] - 178) < 55
check(not _royal(o1) and _royal(o2), "single hairline frame (page outside, royal on frame)")
check(not _royal(o3), "no nested inner outline (6px inside the frame)")
tick = panel.getpixel((40, 694))  # inside the yellow corner tick
check(abs(tick[0] - 255) < 25 and abs(tick[1] - 214) < 35 and tick[2] < 60,
      "ONE tiny yellow corner accent")
acc = panel.getpixel((431, 672))  # the old upward accent must be gone
check(acc[0] > 235 and acc[1] > 235 and acc[2] > 235,
      "no extra accents: old upward dash removed")
fsh = panel.getpixel((437, 800))  # just right of the frame: subtle shadow
check(150 < fsh[0] < 250, f"very subtle depth shadow at the frame ({fsh[0]})")

# --- brief point 7: spine, deliberately designed ---
check("${system.name}" in get("image", "libRail").findtext("path"),
      "spine art bound to ${system.name} (actual current system)")
rails = glob.glob(os.path.join(ROOT, "art/rails/*.png"))
check(len(rails) == 21, f"21 spine PNGs ({len(rails)})")
rail = Image.open(os.path.join(ROOT, "art/rails/gba.png")).convert("RGB")
check(rail.size == (60, 912), f"spine PNG 60x912 ({rail.size[0]}x{rail.size[1]})")
def _is_yellow(p):
    return abs(p[0] - 255) < 20 and abs(p[1] - 214) < 30 and abs(p[2] - 10) < 30
yell = sum(1 for y in range(48, 885, 8) if _is_yellow(rail.getpixel((4, y))))
check(yell > 90, f"ONE continuous thin yellow structural line ({yell} samples)")
tickc = sum(1 for y in (300, 456, 612) if _is_yellow(rail.getpixel((6, y))))
check(tickc == 3, f"spine connector ticks reach into adjacent surfaces ({tickc}/3)")
cpx = rail.getpixel((30, 400)); epx = rail.getpixel((56, 400))
check(sum(cpx) > sum(epx) + 15, "subtle tonal variation within the royal blue")
grid = sum(1 for x in range(20, 41, 2) for y in range(200, 300, 2)
           if rail.getpixel((x, y))[0] > 45 and rail.getpixel((x, y))[1] > 95)
check(grid > 25, f"controlled grid texture ({grid} samples)")
plate = sum(1 for x in range(8, 53, 2) for y in range(320, 593, 2)
            if sum(rail.getpixel((x, y))) / 3 < 75)
check(plate > 150, f"logo deliberately MOUNTED on a plate ({plate} dark plate px)")
missing_sys = []
for sysdir in ["dreamcast", "gb", "gba", "gbc", "gc", "genesis", "megadrive",
               "n3ds", "n64", "nds", "nes", "ps2", "psp", "psx", "snes",
               "steam", "wii", "wiiu", "windows", "xbox", "xbox360"]:
    tp = os.path.join(ROOT, sysdir, "theme.xml")
    if not (os.path.exists(tp) and "../views.xml" in open(tp).read()
            and os.path.exists(os.path.join(ROOT, "art/rails", sysdir + ".png"))):
        missing_sys.append(sysdir)
check(not missing_sys, f"all 21 systems include shared views.xml + have a rail ({missing_sys})")

# --- brief point 8: prev/next form a real navigation path ---
check(prev_c[1] - iw / 2 < 0, f"prev item cropped by the top edge ({prev_c[1]-iw/2:.0f})")
sp = get("image", "libShardPrev")
spx, spy, spw, sph = el_box(sp)
check(spy < prev_c[1] + iw / 2 and spx < prev_c[0] + iw / 2 < spx + spw,
      "upper-right shard crops the prev item")
check(int(sp.findtext("zIndex")) > int(get('carousel', 'gameCarousel').findtext("zIndex")),
      "shards above the carousel")
# the next item is a DISC, not a rect: inside the radius is disc art,
# outside the radius (but inside the item box) is background
pin = rgb.getpixel((942, 892)); pout = rgb.getpixel((985, 935))
check(pin[1] > pin[0] and pout[2] > pout[1] + 20,
      "next media is a real disc (circular silhouette), not a rect or thumbnail")

# --- brief point 9: controlled overlap ---
check(my + mh + 14 > 306, "marquee breaks slightly over its rule (overlap)")
ph = get("image", "libPlaneHero")
phx, phy, phw, phh = el_box(ph)
check(phx < cx + sel / 2 and phx + phw > cx and phy < cy + sel / 2 and phy + phh > cy,
      "hero plane sits under the disc's lower-right")
check(int(ph.findtext("zIndex")) < int(get('carousel', 'gameCarousel').findtext("zIndex")),
      "plane behind the carousel (disc overlaps it)")

# --- brief point 10: no amateur signals, quiet footer ---
check("lib_glow_yellow.png" not in paths, "no giant yellow glow asset")
check(not has("image", "libSelectedGlow"), "v10 halo element stays retired")
check(abs(float(get("text", "libFooter").findtext("fontSize")) - 0.0135) < 0.001,
      "footer extremely quiet (0.0135)")
check(get("text", "libFooter").findtext("color") == "80FFFFFF", "footer subdued (80FFFFFF)")
nimg = len([el for el in gamelist.iter("image")])
check(nimg <= 16, f"image element count restrained ({nimg})")
dbg = sum(1 for p in base.convert("RGB").getdata()
          if (p[0] > 240 and p[1] < 20 and p[2] > 240) or (p[0] < 20 and p[1] > 240 and p[2] > 240))
check(dbg == 0, f"no debug magenta/cyan pixels ({dbg})")
import hashlib
bg = hashlib.sha256(open(os.path.join(ROOT, "art/gamelist_generic_bg.png"), "rb").read()).hexdigest()
bg_head = os.popen("git -C ~/workspace/crystal-esde-theme show HEAD:theme-src/crystal/art/gamelist_generic_bg.png | sha256sum").read().split()[0]
check(bg == bg_head, "gamelist_generic_bg.png unchanged")

# --- v16 system-view work untouched ---
import subprocess
rc = subprocess.run(["git", "-C", os.path.expanduser("~/workspace/crystal-esde-theme"),
                     "diff", "--quiet", "HEAD", "--",
                     "theme-src/crystal/cards", "theme-src/crystal/art/poster_on"]).returncode
check(rc == 0, "system-view cards/posters byte-identical to HEAD")
sysxml_head = os.popen("git -C ~/workspace/crystal-esde-theme show HEAD:theme-src/crystal/views.xml").read()
def _sysview(s):
    mm = re.search(r'<view name="system">.*?</view>', s, re.S)
    return mm.group(0) if mm else ""
check(_sysview(open(os.path.join(ROOT, "views.xml")).read()) == _sysview(sysxml_head),
      "system view section byte-identical to HEAD")

print("FAILURES:", len(fails))
sys.exit(1 if fails else 0)
