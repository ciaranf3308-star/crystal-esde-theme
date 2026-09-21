#!/usr/bin/env python3
"""PIL mock of the Crystal v12 gamelist visual-maturity pass, parsed from the
real theme XML. Mock only - not an ES-DE screenshot.

Animation-aware art direction is IMPLIED only: the static mock suggests
motion the engine could show (aura pulse layer, faint slide echoes on the
neighbours, sweep head on the title rule). ES-DE 3.4.1 has no theme
keyframes or idle animation, and none is claimed - the real build shows
native eased carousel transitions."""
import os, sys, glob, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 960
ROOT = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal")
OUT = os.path.expanduser("~/workspace/crystal-esde-theme/work/proofs/mock_v12_full.png")

def px(pair):
    x, y = pair.strip().split()
    return float(x) * W, float(y) * H

def sz(pair):
    x, y = pair.strip().split()
    return float(x) * W, float(y) * H

tree = ET.parse(os.path.join(ROOT, "views.xml"))
views = tree.getroot()
gamelist = None
for v in views.iter("view"):
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

# ----------------------------------------------- marquee: panel hero ---
# The marquee sits on the clean white/blue framed field (not a dark well).
mx, my, mw, mh = max_box(get("image", "libMarquee"))
f = ImageFont.truetype(marker, 40)
d.text((mx + mw / 2, my + mh / 2 - 10), "SUPER MARIO 64", font=f,
       fill=(10, 47, 160, 255), anchor="mm")
d.rectangle([mx + mw / 2 - 130, my + mh / 2 + 30, mx + mw / 2 + 130, my + mh / 2 + 36],
            fill=(255, 214, 10, 255))

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
                 "this time - 120 Power Stars await the", "brave. A landmark in 3D game design."], 16, (58, 74, 115))
year = get("datetime", "libYear"); fake_text(year, ["1996"], 56, (10, 47, 160), marker)
rx, ry, rw, rh = el_box(get("rating", "libRating"))
for i in range(4):
    star = Image.open(os.path.join(ROOT, "art/star_filled.png")).convert("RGBA").resize((26, 26))
    base.alpha_composite(star, (int(rx + i * 32), int(ry)))
fake_text(get("text", "libGenre"), ["PLATFORMER"], 19, (10, 47, 160), fb)
fake_text(get("text", "libPlayers"), ["1-2 PLAYERS"], 15, (58, 74, 115))
fake_text(get("text", "libDev"), ["NINTENDO"], 15, (58, 74, 115))

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
place(base, "./art/lib_glow_blue.png", el_box(get("image", "libSelectedGlowBlue")), 0.5)
# aura + a faint expanded copy to imply a gentle pulse (mock only)
ax, ay, aw, ah = el_box(get("image", "libSelectedAura"))
place(base, "./art/lib_hero_aura.png", (ax, ay, aw, ah), 0.55)
pulse = Image.open(os.path.join(ROOT, "art/lib_hero_aura.png")).convert("RGBA")
pulse = pulse.resize((int(aw * 1.045), int(ah * 1.045)), Image.LANCZOS)
a = pulse.split()[3].point(lambda v: int(v * 0.18))
pulse.putalpha(a)
base.alpha_composite(pulse, (int(ax + aw / 2 - pulse.width / 2), int(ay + ah / 2 - pulse.height / 2)))
place(base, "./art/lib_shadow_soft.png", el_box(get("image", "libSelectedShadow")), 0.85)
place(base, "./art/lib_hero_ring.png", el_box(get("image", "libSelectedRing")))

car = get("carousel", "gameCarousel")
cx, cy = px(car.findtext("pos"))
cw, ch = sz(car.findtext("size"))
iw, ih = sz(car.findtext("itemSize"))
scale = float(car.findtext("itemScale"))
pitch = ch / float(car.findtext("maxItemCount"))
sel = iw * scale

def disk_layer(cx_, cy_, r):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    steps = 40
    for i in range(steps, 0, -1):
        t = i / steps
        col = (int(64 + 92 * (1 - t)), int(88 + 84 * (1 - t)), int(168 + 52 * (1 - t)))
        rr = r * t
        dl.ellipse([cx_ - rr, cy_ - rr, cx_ + rr, cy_ + rr], fill=col + (255,))
    dl.ellipse([cx_ - r * 0.68, cy_ - r * 0.68, cx_ + r * 0.68, cy_ + r * 0.68],
               fill=(14, 48, 150, 255))
    dl.ellipse([cx_ - r * 0.60, cy_ - r * 0.60, cx_ + r * 0.60, cy_ + r * 0.60],
               fill=(226, 232, 246, 255))
    dl.ellipse([cx_ - r * 0.72, cy_ - r * 0.72, cx_ + r * 0.72, cy_ + r * 0.72],
               outline=(255, 214, 10, 255), width=max(2, int(r * 0.02)))
    dl.arc([cx_ - r * 0.9, cy_ - r * 0.9, cx_ + r * 0.9, cy_ + r * 0.9],
           start=200, end=260, fill=(255, 255, 255, 110), width=max(3, int(r * 0.05)))
    dl.ellipse([cx_ - r * 0.16, cy_ - r * 0.16, cx_ + r * 0.16, cy_ + r * 0.16],
               fill=(190, 198, 216, 255))
    dl.ellipse([cx_ - r * 0.06, cy_ - r * 0.06, cx_ + r * 0.06, cy_ + r * 0.06],
               fill=(40, 48, 72, 255))
    return layer

def dim(layer, op=0.55, dark=0.45):
    out = Image.blend(layer, Image.new("RGBA", layer.size, (0, 0, 0, 255)), dark)
    a = layer.split()[3].point(lambda v: int(v * op))
    out.putalpha(a)
    return out

def faint(layer, op=0.10):
    a = layer.split()[3].point(lambda v: int(v * op))
    layer.putalpha(a)
    return layer

def cart_layer(cx_, cy_, w_, h_):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    dl.rounded_rectangle([cx_ - w_ / 2, cy_ - h_ / 2, cx_ + w_ / 2, cy_ + h_ / 2],
                         radius=12, fill=(110, 130, 190, 255))
    dl.rounded_rectangle([cx_ - w_ / 2 + 14, cy_ - h_ / 2 + 14, cx_ + w_ / 2 - 14, cy_ + h_ / 4],
                         radius=6, fill=(232, 238, 252, 255))
    dl.rounded_rectangle([cx_ - w_ / 2 + 14, cy_ + h_ / 4 + 10, cx_ + w_ / 2 - 14, cy_ + h_ / 2 - 14],
                         radius=6, fill=(18, 58, 178, 255))
    return layer

# neighbours: real media, smaller, edge-cropped, dimmed; faint slide echoes
# (mock-only) imply carousel motion
base = Image.alpha_composite(base, faint(disk_layer(cx - 24, cy - pitch, iw / 2)))
base = Image.alpha_composite(base, dim(disk_layer(cx, cy - pitch, iw / 2)))
base = Image.alpha_composite(base, faint(cart_layer(cx + 24, cy + pitch, iw, ih)))
base = Image.alpha_composite(base, dim(cart_layer(cx, cy + pitch, iw, ih)))
d = ImageDraw.Draw(base)
# selected hero disk, elevated (540px)
hero = disk_layer(cx, cy, sel / 2)
base = Image.alpha_composite(base, hero)
d = ImageDraw.Draw(base)

# title block
place(base, "./art/lib_title_rule.png", el_box(get("image", "libTitleRule")))
te = get("text", "libGameName")
tx, ty, tw, th = el_box(te)
f5 = ImageFont.truetype(marker, 30)
d.text((tx + tw / 2, ty + th / 2), "SUPER MARIO 64", font=f5, fill="white", anchor="mm")
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

# --- approved skeleton: region preservation ---
check(abs(sel - 540) < 2, f"selected hero {sel:.0f}px == 540 (enlarged)")
check(abs(sel / iw - 3.0) < 0.01, f"hero/neighbour ratio {sel/iw:.2f}x")
check(abs(float(get('carousel', 'gameCarousel').findtext("itemScale")) - 3.0) < 0.001, "itemScale 3.0")
check(abs(pitch - 420) < 1, f"carousel pitch {pitch:.0f}px == 420")
prev_c = (cx, cy - pitch); next_c = (cx, cy + pitch)
check(abs(prev_c[0] - 900) < 2 and abs(prev_c[1] - 10) < 2, f"prev at ({prev_c[0]:.0f},{prev_c[1]:.0f}), cropped top")
check(abs(next_c[0] - 900) < 2 and abs(next_c[1] - 850) < 2, f"next at ({next_c[0]:.0f},{next_c[1]:.0f}), cropped bottom")
check(abs(cx - 900) < 2 and abs(cy - 430) < 2, "selected centre (900,430)")
check(ty + th <= next_c[1] - ih / 2 - 2, "title band clear above next disk")
check(ty >= cy + sel / 2 + 4, "title band below hero disk")
rbx, rby, rbw, rbh = el_box(get("image", "libRail"))
check(abs(rbx - 486) < 2 and abs(rbw - 76) < 2 and abs(rbh - 912) < 2, "spine 76x912 at x486 (footprint kept)")
check(cx - sel / 2 > rbx + rbw + 40, "hero clear of spine (>=40px)")
# left column: ONE integrated module inside the approved zone
pbx, pby, pbw, pbh = el_box(get("image", "libPanelMain"))
check(abs(pbx - 6) < 2 and abs(pby - 10) < 2 and abs(pbw - 470) < 2 and abs(pbh - 940) < 2,
      f"panel box {pbx:.0f},{pby:.0f} {pbw:.0f}x{pbh:.0f} (single integrated module)")
check(pbx + pbw <= 486 + 1 and pby >= 10 - 1 and pby + pbh <= 950 + 1, "panel inside left zone")
check(not has("image", "libModMasthead") and not has("image", "libModMeta") and not has("image", "libModShot"),
      "no stacked cards: v11 modules gone")
# title positions
tbx, tby, tbw, tbh = el_box(get("image", "libTitleRule"))
check(abs(tby + tbh / 2 - 716) < 2, "title rule at Y716")
check(abs(ty + th / 2 - 736) < 2, "title at Y736")

# --- v12 visual-maturity specifics ---
paths = " ".join(all_paths())
for dead in ["lib_mod_masthead.png", "lib_mod_meta.png", "lib_mod_shot.png",
             "lib_kicker_released.png", "lib_kicker_genre.png",
             "lib_kicker_players.png", "lib_kicker_developer.png",
             "lib_kicker_rating.png", "lib_hero_arc.png", "lib_glow_yellow.png",
             "libSelectedGlow"]:
    check(dead not in paths, f"retired asset/element not referenced: {dead}")
for dead in ["lib_mod_masthead.png", "lib_mod_meta.png", "lib_mod_shot.png",
             "lib_kicker_released.png", "lib_kicker_genre.png",
             "lib_kicker_players.png", "lib_kicker_developer.png",
             "lib_kicker_rating.png", "lib_hero_arc.png", "lib_glow_yellow.png"]:
    check(not os.path.exists(os.path.join(ROOT, "art", dead)), f"retired asset deleted: {dead}")
check(not has("image", "libSelectedGlow"), "yellow halo element retired")
check(not has("image", "libHeroArc"), "v11 rim arc retired")
check(has("image", "libPanelMain"), "integrated panel module present")
check(has("image", "libSelectedAura") and has("image", "libSelectedRing"),
      "restrained gold aura + ring present (no giant halo)")
m = get("image", "libMarquee")
check(float(m.findtext("opacity")) >= 1.0, "marquee full opacity")
check(mw >= 360 and mh >= 150, f"marquee box {mw:.0f}x{mh:.0f} large, panel-hero feel")
mt = get("text", "libMarqueeTitle")
check(mt.findtext("color") == "${crystalDeep}", "marquee fallback ink on the white field")
check(get("text", "libGameName").findtext("fontPath").endswith("PermanentMarker-Regular.ttf"),
      "title uses marker display face")
check(get("datetime", "libYear").findtext("fontPath").endswith("PermanentMarker-Regular.ttf"),
      "anchor year uses marker display face")
c = get("carousel", "gameCarousel")
check(abs(float(c.findtext("unfocusedItemOpacity")) - 0.55) < 0.01, "neighbours opacity 0.55")
check(abs(float(c.findtext("unfocusedItemDimming")) - 0.45) < 0.01, "neighbours dimming 0.45")
check(abs(float(c.findtext("unfocusedItemSaturation")) - 0.6) < 0.01, "neighbours saturation 0.6")
# editorial order: description FIRST, then anchor year, then grouped facts
dx, dy, dw, dh = el_box(get("text", "libDesc"))
yx, yy, yw, yh = el_box(get("datetime", "libYear"))
gx, gy, gw, gh = el_box(get("text", "libGenre"))
check(dy < yy < gy, "editorial order: description, then year, then facts")
boxes = []
for tag, name in [("text", "libDesc"), ("datetime", "libYear"),
                  ("rating", "libRating"), ("text", "libGenre"),
                  ("text", "libPlayers"), ("text", "libDev")]:
    boxes.append((name, el_box(get(tag, name))))
ok = True
for i in range(len(boxes)):
    for j in range(i + 1, len(boxes)):
        (n1, (x1, y1, w1, h1)), (n2, (x2, y2, w2, h2)) = boxes[i], boxes[j]
        if x1 < x2 + w2 - 1 and x2 < x1 + w1 - 1 and y1 < y2 + h2 - 1 and y2 < y1 + h1 - 1:
            ok = False; print("  overlap:", n1, n2)
check(ok, "metadata stacked without overlaps")
# screenshot inside the integrated panel, at the punched window
check(abs(sw - 396) < 2 and abs(sh - 210) < 2, "screenshot 396x210")
check(sx >= pbx and sy >= pby and sx + sw <= pbx + pbw and sy + sh <= pby + pbh,
      "screenshot sits inside the integrated panel")
check(abs(sx - 42) < 2 and abs(sy - 700) < 2, "screenshot at the punched window (42,700)")
# spine: one thin yellow separator line + supplied-logo rails
rails = glob.glob(os.path.join(ROOT, "art/rails/*.png"))
check(len(rails) == 21, f"21 spine PNGs ({len(rails)})")
rail = Image.open(os.path.join(ROOT, "art/rails/gba.png")).convert("RGB")
def _is_yellow(p):
    return abs(p[0] - 255) < 20 and abs(p[1] - 214) < 30 and abs(p[2] - 10) < 30
yell = sum(1 for y in range(24, 889, 8) if _is_yellow(rail.getpixel((5, y))))
check(yell > 90, f"spine carries the thin yellow separator line ({yell} samples)")
check(abs(fy + fh / 2 - 915) < 3, "footer at y915")
check(get("carousel", "gameCarousel").findtext("type") == "vertical", "carousel type vertical")
# hero aura/ring assets exist and are restrained (transparent cores)
aura = Image.open(os.path.join(ROOT, "art/lib_hero_aura.png")).convert("RGBA")
check(aura.getpixel((340, 340))[3] < 8, "aura core transparent (no blurry halo)")
ring = Image.open(os.path.join(ROOT, "art/lib_hero_ring.png")).convert("RGBA")
check(ring.getpixel((310, 310))[3] < 8, "ring core transparent")

print("FAILURES:", len(fails))
sys.exit(1 if fails else 0)
