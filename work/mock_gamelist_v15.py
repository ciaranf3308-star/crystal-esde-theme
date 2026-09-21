#!/usr/bin/env python3
"""PIL mock of the Crystal v15 gamelist VISUAL MATURITY pass, parsed from
the real theme XML. Mock only - not an ES-DE screenshot.

The macro layout is LOCKED to the approved skeleton (left column 6,10
470x940; spine 486,24 60x912; hero 540px at 900,430; prev/next 900,10 /
900,850 pitch 420; rule Y716 / title Y736 / meta Y757; screenshot 42,700
396x210). What changed is the finish, per the user's 10-point brief:

1. Hero: concentric-ring / turntable decoration REMOVED (no aura, no
   layered ring). Depth from scale, a detached soft contact shadow, a
   restrained atmospheric blue glow, and ONE very thin selective yellow
   rim highlight (partial top arc).
2. Left column: ONE editorial composition - open whitespace, typography,
   a few graphic rules. No mats, no L-frames, no nested boxes.
3. Marquee dominates the upper-left on open whitespace; NOW SHOWING is a
   tiny kicker.
4. Metadata: oversized year anchor, strong genre, quiet players/dev,
   rating adjacent; tiny quiet labels, values carry the weight.
5. Screenshot: single hairline frame on the page, one corner tick, one
   accent breaking the frame upward.
6. Spine: refined 60px magazine spine, one yellow line + connector ticks,
   per-system binding via ${system.name}.
7. Title zone rebuilt: bolder title, redesigned rule, composite
   GENRE . YEAR . DEV . PLAYERS line.
8. Prev/next: dimmer, subordinate, cropped by the top edge and by the
   foreground shards at the upper-right / lower-right edges.
9. Controlled overlap: marquee breaks over its rule, screenshot accent
   breaks its frame, the disc overlaps the hero plane, shards crop the
   neighbours, spine ticks reach into adjacent surfaces.
10. No nested borders, no giant glows, no placeholder rects.

ES-DE 3.4.1 has no theme keyframes or idle animation, and none is
claimed - the real build shows native eased carousel transitions."""
import os, sys, glob, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 960
ROOT = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal")
OUT = os.path.expanduser("~/workspace/crystal-esde-theme/work/proofs/mock_v15_full.png")

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
# Open whitespace, no mat, no frame. Drawn large enough to break slightly
# over the baked hairline rule beneath the marquee zone (controlled
# overlap, per the brief).
mx, my, mw, mh = max_box(get("image", "libMarquee"))
# fit the fallback headline inside the marquee box (the real theme shows
# scraped marquee art scaled to this box; this stand-in keeps the scale)
_msize = 64
while _msize > 20:
    _f = ImageFont.truetype(marker, _msize)
    _bb = _f.getbbox("SUPER MARIO 64")
    if _bb[2] - _bb[0] <= mw - 18:
        break
    _msize -= 2
d.text((mx + mw / 2, my + 100), "SUPER MARIO 64", font=_f,
       fill=(10, 47, 160, 255), anchor="mm")
# the marquee art breaks slightly over the baked hairline rule at y272
d.rectangle([mx + 70, 268, mx + mw - 70, 274], fill=(255, 214, 10, 255))

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

def disk_layer(cx_, cy_, r):
    """The physical media itself, dimensionally lit (directional studio
    light, dark rim, specular edge arcs, data-band rings, layered gloss,
    beveled hub). No baked accent rings: the real theme shows the user's
    scanned media here; this stand-in proves the lighting treatment and
    keeps the media intact and recognizable."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    steps = 48
    for i in range(steps, 0, -1):
        t = i / steps
        rr = r * t
        ox = -r * 0.18 * (1 - t)
        oy = -r * 0.22 * (1 - t)
        col = (int(48 + 104 * (1 - t)), int(72 + 100 * (1 - t)), int(154 + 62 * (1 - t)))
        dl.ellipse([cx_ + ox - rr, cy_ + oy - rr, cx_ + ox + rr, cy_ + oy + rr],
                   fill=col + (255,))
    # dark blue data ring + pale inner label
    dl.ellipse([cx_ - r * 0.68, cy_ - r * 0.68, cx_ + r * 0.68, cy_ + r * 0.68],
               fill=(14, 48, 150, 255))
    dl.ellipse([cx_ - r * 0.60, cy_ - r * 0.60, cx_ + r * 0.60, cy_ + r * 0.60],
               fill=(226, 232, 246, 255))
    for rr in (0.78, 0.84, 0.90):
        dl.ellipse([cx_ - r * rr, cy_ - r * rr, cx_ + r * rr, cy_ + r * rr],
                   outline=(255, 255, 255, 22), width=max(1, int(r * 0.008)))
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

def cart_layer(cx_, cy_, w_, h_):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = cx_ - w_ / 2, cy_ - h_ / 2, cx_ + w_ / 2, cy_ + h_ / 2
    dl.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=(46, 54, 82, 255))
    dl.rounded_rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], radius=7,
                         outline=(20, 26, 52, 255), width=2)
    dl.line([(x0 + 8, y0 + 3), (x1 - 8, y0 + 3)], fill=(255, 255, 255, 70), width=2)
    dl.rounded_rectangle([x0 + 12, y0 + 12, x1 - 12, cy_ + h_ / 4], radius=5,
                         fill=(228, 234, 248, 255))
    dl.rectangle([x0 + 12, cy_ - h_ / 8, x1 - 12, cy_ - h_ / 8 + 10],
                 fill=(18, 58, 178, 255))
    dl.rectangle([x0 + 24, y0 + 24, x1 - 24, y0 + 34], fill=(10, 26, 92, 255))
    for gx in (cx_ - 22, cx_, cx_ + 22):
        dl.line([(gx, cy_ + h_ / 4 + 16), (gx, y1 - 12)], fill=(30, 36, 60, 255), width=4)
    return layer

# neighbours: real media, smaller relative to the hero, edge-cropped,
# dimmed hard; subordinate to the hero
base = Image.alpha_composite(base, dim(disk_layer(cx, cy - pitch, iw / 2)))
base = Image.alpha_composite(base, dim(cart_layer(cx, cy + pitch, iw, ih)))
# foreground shards crop the neighbours at the upper-right/lower-right
place(base, "./art/lib_shard_prev.png", el_box(get("image", "libShardPrev")))
place(base, "./art/lib_shard_next.png", el_box(get("image", "libShardNext")))
d = ImageDraw.Draw(base)
# selected hero disk, dimensionally lit (540px); the disc overlaps the
# hero plane beneath it
hero = disk_layer(cx, cy, sel / 2)
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
f6 = ImageFont.truetype(fr, 15)
d.text((fx + fw / 2, fy + fh / 2), "A PLAY \u2022 B BACK", font=f6, fill=(255, 255, 255, 166), anchor="mm")

base.convert("RGB").save(OUT)
print("mock ->", OUT)

# ------------------------------------------------------------- assertions ---
fails = []
def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)

# --- MACRO LAYOUT LOCK: same regions as v13 ---
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
mg0, mg1 = el_box(get("text", "libMetaGenre")), el_box(get("text", "libMetaPlayers"))
check(abs(mg0[1] + mg0[3] / 2 - 757.5) < 3, "composite meta line at Y757")
check(abs(sx - 42) < 2 and abs(sy - 700) < 2 and abs(sw - 396) < 2 and abs(sh - 210) < 2,
      "screenshot window (42,700) 396x210 (unchanged)")
check(abs(fy + fh / 2 - 915) < 3, "footer at y915")

# --- brief point 1: no decorative target ---
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

# --- brief point 2: one editorial composition, borders halved ---
panel = Image.open(os.path.join(ROOT, "art/lib_panel_main.png")).convert("RGBA")
def royal_px(img):
    return sum(1 for p in img.getdata()
               if p[3] > 100 and abs(p[0] - 18) < 40 and abs(p[1] - 58) < 50 and abs(p[2] - 178) < 50)
panel_royal = royal_px(panel)
v13 = os.popen("git -C ~/workspace/crystal-esde-theme show HEAD:theme-src/crystal/art/lib_panel_main.png > /tmp/panel_v13.png").close()
panel_v13 = Image.open("/tmp/panel_v13.png").convert("RGBA")
v13_royal = royal_px(panel_v13)
check(panel_royal < v13_royal * 0.5,
      f"borders reduced by more than half (royal px {panel_royal} vs v13 {v13_royal})")
# no L-frame where v13 had it (local 24..29, 58..258 -> global 30..35, 68..268)
lframe = sum(1 for x in range(30, 36) for y in range(68, 268)
             if panel.getpixel((x - 6, y - 10))[3] > 100 and abs(panel.getpixel((x - 6, y - 10))[0] - 18) < 40)
check(lframe < 20, f"v13 L-frame gone ({lframe} royal px in the old frame strip)")
# no heavy header band: v13's band filled local y0..58 (global 10..68) at x~240
band = sum(1 for x in range(220, 260) for y in range(14, 64)
           if panel.getpixel((x - 6, y - 10))[3] > 200 and panel.getpixel((x - 6, y - 10))[0] < 100
           and panel.getpixel((x - 6, y - 10))[2] > 120)
check(band < 100, f"v13 header band gone ({band} solid-blue px in the old band zone)")

# --- brief point 3: marquee dominates ---
m = get("image", "libMarquee")
check(mw >= 400 and mh >= 190, f"marquee box {mw:.0f}x{mh:.0f} dominates the upper-left")
check(abs(float(get("text", "libMarqueeTitle").findtext("fontSize")) - 0.04) < 0.001,
      "marquee fallback type larger (0.04)")
# no mat: the marquee zone on the panel art is plain white
mat = panel.getpixel((200, 120))
check(mat[3] > 200 and mat[0] > 235 and mat[1] > 235 and mat[2] > 235,
      "marquee sits on open whitespace (no mat)")
# NOW SHOWING kicker tiny: baked text present but small (check the kicker
# row has some royal pixels, but no band)
kick = sum(1 for x in range(30, 200) for y in range(14, 44)
           if panel.getpixel((x, y))[3] > 150 and abs(panel.getpixel((x, y))[0] - 18) < 50)
check(50 < kick < 4000, f"tiny kicker present, secondary ({kick} px)")

# --- brief point 4: metadata hierarchy ---
check(get("datetime", "libYear").findtext("fontPath").endswith("PermanentMarker-Regular.ttf"),
      "anchor year uses marker display face")
check(abs(float(get("datetime", "libYear").findtext("fontSize")) - 0.06) < 0.001,
      "year anchor 0.06 (large)")
check(abs(float(get("text", "libGenre").findtext("fontSize")) - 0.024) < 0.001,
      "genre strong secondary (0.024)")
check(get("text", "libGenre").findtext("color") == "${crystalDeep}", "genre carries weight (deep)")
pg, pd = float(get("text", "libPlayers").findtext("fontSize")), float(get("text", "libDev").findtext("fontSize"))
check(pg < 0.02 and pd < 0.02, f"players/dev quieter ({pg}/{pd})")
check(get("text", "libPlayers").findtext("color") == "${crystalInkDim}", "players/dev quiet ink")
rx_, ry_, rw_, rh_ = el_box(get("rating", "libRating"))
yx_, yy_, yw_, yh_ = el_box(get("datetime", "libYear"))
check(abs(ry_ - yy_) < 40, "rating adjacent to the year anchor")
dx, dy, dw, dh = el_box(get("text", "libDesc"))
gx, gy, gw, gh = el_box(get("text", "libGenre"))
check(dy < yy_ < gy, "editorial order: description, then year, then facts")

# --- brief point 5: screenshot, one frame ---
# single hairline: just outside the frame is white page, on the frame is
# royal, a few px inside is the screenshot art (no second outline)
o1 = panel.getpixel((34, 780))   # 2px left of frame -> page
o2 = panel.getpixel((36, 780))   # on frame
o3 = panel.getpixel((42, 780))   # 6px inside -> should NOT be another outline
def _royal(p):
    return p[3] > 100 and abs(p[0] - 18) < 45 and abs(p[1] - 58) < 55 and abs(p[2] - 178) < 55
check(not _royal(o1) and _royal(o2), "single hairline frame (page outside, royal on frame)")
check(not _royal(o3), "no nested inner outline (6px inside the frame)")
tick = panel.getpixel((40, 694))  # inside the yellow corner tick
check(abs(tick[0] - 255) < 25 and abs(tick[1] - 214) < 35 and tick[2] < 60,
      "one yellow corner tick")
acc = panel.getpixel((431, 672))  # accent above the frame's right edge
check(abs(acc[0] - 255) < 25 and abs(acc[1] - 214) < 35 and acc[2] < 60,
      "accent breaks the frame upward (controlled overlap)")

# --- brief point 6: spine, per-system binding ---
check("libRail" in [n for t, n in els if t == "image"], "libRail element present")
check("${system.name}" in get("image", "libRail").findtext("path"),
      "spine art bound to ${system.name} (actual current system)")
rails = glob.glob(os.path.join(ROOT, "art/rails/*.png"))
check(len(rails) == 21, f"21 spine PNGs ({len(rails)})")
rail = Image.open(os.path.join(ROOT, "art/rails/gba.png")).convert("RGB")
check(rail.size == (60, 912), f"spine PNG 60x912 ({rail.size[0]}x{rail.size[1]})")
def _is_yellow(p):
    return abs(p[0] - 255) < 20 and abs(p[1] - 214) < 30 and abs(p[2] - 10) < 30
yell = sum(1 for y in range(48, 885, 8) if _is_yellow(rail.getpixel((4, y))))
check(yell > 90, f"spine carries the thin yellow line ({yell} samples)")
tickc = sum(1 for y in (300, 456, 612) if _is_yellow(rail.getpixel((6, y))))
check(tickc == 3, f"spine connector ticks reach into adjacent surfaces ({tickc}/3)")
missing_sys = []
for sysdir in ["dreamcast", "gb", "gba", "gbc", "gc", "genesis", "megadrive",
               "n3ds", "n64", "nds", "nes", "ps2", "psp", "psx", "snes",
               "steam", "wii", "wiiu", "windows", "xbox", "xbox360"]:
    tp = os.path.join(ROOT, sysdir, "theme.xml")
    if not (os.path.exists(tp) and "../views.xml" in open(tp).read()
            and os.path.exists(os.path.join(ROOT, "art/rails", sysdir + ".png"))):
        missing_sys.append(sysdir)
check(not missing_sys, f"all 21 systems include shared views.xml + have a rail ({missing_sys})")

# --- brief point 7: title zone rebuilt ---
check(abs(float(get("text", "libGameName").findtext("fontSize")) - 0.04) < 0.001,
      "title bolder (0.04)")
check(get("text", "libGameName").findtext("color") == "FFFFFF", "title confident white")
rule = Image.open(os.path.join(ROOT, "art/lib_title_rule.png")).convert("RGBA")
check(rule.size == (300, 10), "title rule asset 300x10")
bar_end = rule.getpixel((200, 7))   # past the short yellow bar
bar_mid = rule.getpixel((60, 7))    # inside the short yellow bar
check(abs(bar_mid[0] - 255) < 25 and bar_mid[2] < 60, "short yellow bar present")
check(not (abs(bar_end[0] - 255) < 25 and bar_end[2] < 60), "yellow bar is SHORT (no full slab)")
segs = [("text", "libMetaGenre"), ("datetime", "libMetaYear"),
        ("text", "libMetaDev"), ("text", "libMetaPlayers"),
        ("text", "libMetaSep1"), ("text", "libMetaSep2"), ("text", "libMetaSep3")]
check(all(has(t, n) for t, n in segs), "composite secondary line: 4 values + 3 separators")
row = [el_box(get(t, n)) for t, n in segs]
row_l = min(b[0] for b in row); row_r = max(b[0] + b[2] for b in row)
check(abs((row_l + row_r) / 2 - 900) < 4, f"secondary line centered on the hero ({(row_l+row_r)/2:.0f})")
check(all(abs(b[1] + b[3] / 2 - 757.5) < 3 for b in row), "all segments on the Y757 line")
check(all(get(t, n).findtext("color") == "A6FFFFFF" for t, n in segs), "secondary line restrained")
# no placeholder rect between title and footer: no image element there
# except the intentional shard
for el in gamelist.iter("image"):
    nm = el.get("name")
    if nm in ("libShardNext", "libShardPrev", "libPlaneHero", "libSelectedGlowBlue",
              "libSelectedShadow", "libSelectedRim", "libBackground",
              "libBottomGradient", "libPanelMain", "libRail", "libMarquee",
              "libScreenshot", "libTitleRule"):
        continue
    check(False, f"unexpected image element in the title band: {nm}")
print("PASS no placeholder rects in the lower hero zone")

# --- brief point 8: prev/next subordinate, entering from the edges ---
c = get("carousel", "gameCarousel")
check(abs(float(c.findtext("unfocusedItemOpacity")) - 0.45) < 0.01, "neighbours opacity 0.45")
check(abs(float(c.findtext("unfocusedItemDimming")) - 0.55) < 0.01, "neighbours dimming 0.55")
check(abs(float(c.findtext("unfocusedItemSaturation")) - 0.5) < 0.01, "neighbours saturation 0.5")
sp = get("image", "libShardPrev"); sn = get("image", "libShardNext")
spx, spy, spw, sph = el_box(sp); snx, sny, snw, snh = el_box(sn)
check(spy < prev_c[1] + iw / 2 and spx < prev_c[0] + iw / 2 < spx + spw,
      "upper-right shard crops the prev item")
check(sny < next_c[1] + ih / 2 and snx < next_c[0] + iw / 2 < snx + snw,
      "lower-right shard crops the next item")
check(int(sp.findtext("zIndex")) > int(c.findtext("zIndex")), "shards above the carousel")
check(abs(prev_c[1] - iw / 2) < 100, "prev item cropped by the top edge")

# --- brief point 9: controlled overlap ---
# the marquee's region (bottom = 68+210 = 278) breaks over the baked
# hairline rule at y272
check(my + mh > 272, "marquee breaks slightly over its rule (overlap)")
ph = get("image", "libPlaneHero")
phx, phy, phw, phh = el_box(ph)
check(phx < cx + sel / 2 and phx + phw > cx and phy < cy + sel / 2 and phy + phh > cy,
      "hero plane sits under the disc's lower-right")
check(int(ph.findtext("zIndex")) < int(c.findtext("zIndex")), "plane behind the carousel (disc overlaps it)")

# --- brief point 10: no amateur signals ---
check("lib_glow_yellow.png" not in paths, "no giant yellow glow asset")
check(not has("image", "libSelectedGlow"), "v10 halo element stays retired")
nimg = len([el for el in gamelist.iter("image")])
check(nimg <= 16, f"image element count restrained ({nimg})")
# no debug/placeholder pixels in the final render
dbg = sum(1 for p in base.convert("RGB").getdata()
          if (p[0] > 240 and p[1] < 20 and p[2] > 240) or (p[0] < 20 and p[1] > 240 and p[2] > 240))
check(dbg == 0, f"no debug magenta/cyan pixels ({dbg})")
# gamelist background untouched
import hashlib
bg = hashlib.sha256(open(os.path.join(ROOT, "art/gamelist_generic_bg.png"), "rb").read()).hexdigest()
bg_head = os.popen("git -C ~/workspace/crystal-esde-theme show HEAD:theme-src/crystal/art/gamelist_generic_bg.png | sha256sum").read().split()[0]
check(bg == bg_head, "gamelist_generic_bg.png unchanged")

print("FAILURES:", len(fails))
sys.exit(1 if fails else 0)
