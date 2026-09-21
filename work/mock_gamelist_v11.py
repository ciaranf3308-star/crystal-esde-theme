#!/usr/bin/env python3
"""PIL mock of the Crystal v11 gamelist visual-maturity pass, parsed from the
real theme XML. Mock only - not an ES-DE screenshot."""
import os, sys, glob, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 960
ROOT = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal")
OUT = os.path.expanduser("~/workspace/crystal-esde-theme/work/proofs/mock_v11_full.png")

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
place(base, "./art/lib_mod_masthead.png", el_box(get("image", "libModMasthead")))
place(base, "./art/rails/gba.png", el_box(get("image", "libRail")))

fb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fr = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
marker = os.path.join(ROOT, "fonts/PermanentMarker-Regular.ttf")

# ------------------------------------------------------- masthead module ---
mx, my, mw, mh = max_box(get("image", "libMarquee"))
f = ImageFont.truetype(marker, 44)
d.text((mx + mw / 2, my + mh / 2 - 8), "SUPER MARIO 64", font=f, fill=(255, 255, 255, 255), anchor="mm")
d.rectangle([mx + mw / 2 - 120, my + mh / 2 + 34, mx + mw / 2 + 120, my + mh / 2 + 40],
            fill=(255, 214, 10, 255))

# ---------------------------------------------------------- meta sheet ---
place(base, "./art/lib_mod_meta.png", el_box(get("image", "libModMeta")))

def fake_text(el, lines, size, color, font=fr):
    x, y, w, h = el_box(el)
    fnt = ImageFont.truetype(font, size)
    yy = y
    for ln in lines:
        d.text((x, yy), ln, font=fnt, fill=color)
        yy += size + 7

# description FIRST (editorial order)
desc = get("text", "libDesc")
fake_text(desc, ["A legendary platform adventure across", "painted worlds. Bowser has other plans",
                 "this time - 120 Power Stars await the", "brave. A landmark in 3D game design."], 16, (58, 74, 115))
place(base, "./art/lib_kicker_released.png", el_box(get("image", "libKickerReleased")))
year = get("datetime", "libYear"); fake_text(year, ["1996"], 58, (10, 47, 160), marker)
place(base, "./art/lib_kicker_rating.png", el_box(get("image", "libKickerRating")))
rx, ry, rw, rh = el_box(get("rating", "libRating"))
for i in range(4):
    star = Image.open(os.path.join(ROOT, "art/star_filled.png")).convert("RGBA").resize((26, 26))
    base.alpha_composite(star, (int(rx + i * 32), int(ry)))
place(base, "./art/lib_kicker_genre.png", el_box(get("image", "libKickerGenre")))
fake_text(get("text", "libGenre"), ["PLATFORMER"], 19, (10, 47, 160), fb)
place(base, "./art/lib_kicker_players.png", el_box(get("image", "libKickerPlayers")))
fake_text(get("text", "libPlayers"), ["1-2 PLAYERS"], 15, (58, 74, 115))
place(base, "./art/lib_kicker_developer.png", el_box(get("image", "libKickerDeveloper")))
fake_text(get("text", "libDev"), ["NINTENDO"], 15, (58, 74, 115))

# ------------------------------------------------------- screenshot ---
sx, sy, sw, sh = el_box(get("image", "libScreenshot"))
shot = Image.new("RGBA", (int(sw), int(sh)), (0, 0, 0, 0))
sd = ImageDraw.Draw(shot)
for yy in range(int(sh)):
    t = yy / sh
    col = (int(40 + 60 * t), int(90 + 70 * t), int(190 + 40 * t))
    sd.line([(0, yy), (sw, yy)], fill=col + (255,))
sd.ellipse([sw * 0.62, sh * 0.12, sw * 0.86, sh * 0.52], fill=(255, 236, 150, 255))  # sun
sd.polygon([(0, sh), (0, sh * 0.62), (sw * 0.4, sh * 0.5), (sw, sh * 0.72), (sw, sh)],
           fill=(36, 84, 60, 255))  # hills
base.alpha_composite(shot, (int(sx), int(sy)))
place(base, "./art/lib_mod_shot.png", el_box(get("image", "libModShot")))

# ------------------------------------------------------------ hero column ---
place(base, "./art/lib_glow_blue.png", el_box(get("image", "libSelectedGlowBlue")), 0.5)
place(base, "./art/lib_shadow_soft.png", el_box(get("image", "libSelectedShadow")), 0.85)
place(base, "./art/lib_hero_arc.png", el_box(get("image", "libHeroArc")))

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
        col = (int(104 + 72 * (1 - t)), int(124 + 66 * (1 - t)), int(186 + 44 * (1 - t)))
        rr = r * t
        dl.ellipse([cx_ - rr, cy_ - rr, cx_ + rr, cy_ + rr], fill=col + (255,))
    # label ring + thin yellow accent ring
    dl.ellipse([cx_ - r * 0.68, cy_ - r * 0.68, cx_ + r * 0.68, cy_ + r * 0.68],
               fill=(18, 58, 178, 255))
    dl.ellipse([cx_ - r * 0.60, cy_ - r * 0.60, cx_ + r * 0.60, cy_ + r * 0.60],
               fill=(232, 238, 252, 255))
    dl.ellipse([cx_ - r * 0.72, cy_ - r * 0.72, cx_ + r * 0.72, cy_ + r * 0.72],
               outline=(255, 214, 10, 255), width=max(2, int(r * 0.02)))
    # top-left sheen
    dl.arc([cx_ - r * 0.9, cy_ - r * 0.9, cx_ + r * 0.9, cy_ + r * 0.9],
           start=200, end=260, fill=(255, 255, 255, 110), width=max(3, int(r * 0.05)))
    # hub
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

# prev / next: real media, smaller, cropped by screen edges, dimmed
base = Image.alpha_composite(base, dim(disk_layer(cx, cy - pitch, iw / 2)))
base = Image.alpha_composite(base, dim(cart_layer(cx, cy + pitch, iw, ih)))
d = ImageDraw.Draw(base)
# selected hero disk, elevated
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
check(abs(sel - 520) < 2, f"selected hero {sel:.0f}px == 520")
check(abs(sel / iw - 2.8889) < 0.01, f"hero/neighbour ratio {sel/iw:.2f}x")
check(abs(pitch - 420) < 1, f"carousel pitch {pitch:.0f}px == 420")
prev_c = (cx, cy - pitch); next_c = (cx, cy + pitch)
check(abs(prev_c[0] - 900) < 2 and abs(prev_c[1] - 10) < 2, f"prev at ({prev_c[0]:.0f},{prev_c[1]:.0f}), cropped top")
check(abs(next_c[0] - 900) < 2 and abs(next_c[1] - 850) < 2, f"next at ({next_c[0]:.0f},{next_c[1]:.0f}), cropped bottom")
check(abs(cx - 900) < 2 and abs(cy - 430) < 2, "selected centre (900,430)")
check(ty + th <= next_c[1] - ih / 2 - 2, "title band clear above next disk")
check(ty >= cy + sel / 2 + 4, "title band below hero disk")
rbx, rby, rbw, rbh = el_box(get("image", "libRail"))
check(abs(rbx - 486) < 2 and abs(rbw - 76) < 2 and abs(rbh - 912) < 2, "rail 76x912 at x486 (footprint kept)")
check(cx - sel / 2 > rbx + rbw + 40, "hero clear of rail (>=40px)")
# left zone: three modules, breathing room between them, inside the zone
mods = {}
for nm, (ex, ey, ew, eh) in [("libModMasthead", (6, 10, 470, 300)),
                             ("libModMeta", (6, 322, 470, 346)),
                             ("libModShot", (6, 680, 470, 260))]:
    bx, by, bw, bh = el_box(get("image", nm))
    mods[nm] = (bx, by, bw, bh)
    check(abs(bx - ex) < 2 and abs(by - ey) < 2 and abs(bw - ew) < 2 and abs(bh - eh) < 2,
          f"{nm} module box {bx:.0f},{by:.0f} {bw:.0f}x{bh:.0f} (footprint kept)")
    check(bx >= 0 and bx + bw <= 486 and by >= 10 and by + bh <= 950, f"{nm} inside left zone")
check(mods["libModMasthead"][1] + mods["libModMasthead"][3] < mods["libModMeta"][1],
      "bg breathes between masthead and meta modules")
check(mods["libModMeta"][1] + mods["libModMeta"][3] < mods["libModShot"][1],
      "bg breathes between meta and shot modules")
# title positions
tbx, tby, tbw, tbh = el_box(get("image", "libTitleRule"))
check(abs(tby + tbh / 2 - 716) < 2, "title rule at Y716")
check(abs(ty + th / 2 - 736) < 2, "title at Y736")

# --- v11 visual-maturity specifics ---
paths = " ".join(all_paths())
for dead in ["lib_panel.png", "lib_marquee_back.png", "lib_strike_yellow.png",
             "lib_shot_frame.png", "lib_rule_yellow.png", "lib_glow_yellow.png"]:
    check(dead not in paths, f"retired asset not referenced: {dead}")
    check(not os.path.exists(os.path.join(ROOT, "art", dead)), f"retired asset deleted: {dead}")
check(not has("image", "libSelectedGlow"), "yellow halo element retired")
check(has("image", "libHeroArc"), "restrained rim-light arc present")
m = get("image", "libMarquee")
check(float(m.findtext("opacity")) >= 1.0, "marquee full opacity")
check(mw >= 360 and mh >= 150, f"marquee box {mw:.0f}x{mh:.0f} large, masthead feel")
check(has("image", "libModMasthead") and has("image", "libModMeta") and has("image", "libModShot"),
      "three left-zone modules present (no single white card)")
for k in ["libKickerReleased", "libKickerGenre", "libKickerPlayers", "libKickerDeveloper", "libKickerRating"]:
    check(has("image", k), f"tracked kicker present: {k}")
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
# metadata stacking, no overlaps (both axes)
boxes = []
for tag, name in [("text", "libDesc"), ("image", "libKickerReleased"),
                  ("datetime", "libYear"), ("image", "libKickerRating"),
                  ("rating", "libRating"), ("image", "libKickerGenre"),
                  ("text", "libGenre"), ("image", "libKickerPlayers"),
                  ("text", "libPlayers"), ("image", "libKickerDeveloper"),
                  ("text", "libDev")]:
    boxes.append((name, el_box(get(tag, name))))
ok = True
for i in range(len(boxes)):
    for j in range(i + 1, len(boxes)):
        (n1, (x1, y1, w1, h1)), (n2, (x2, y2, w2, h2)) = boxes[i], boxes[j]
        if x1 < x2 + w2 - 1 and x2 < x1 + w1 - 1 and y1 < y2 + h2 - 1 and y2 < y1 + h1 - 1:
            ok = False; print("  overlap:", n1, n2)
check(ok, "metadata stacked without overlaps")
# screenshot inside the print module window
check(abs(sw - 396) < 2 and abs(sh - 216) < 2, "screenshot 396x216")
shx, shy, shw, shh = mods["libModShot"]
check(sx >= shx and sy >= shy and sx + sw <= shx + shw and sy + sh <= shy + shh,
      "screenshot sits inside the print module")
rails = glob.glob(os.path.join(ROOT, "art/rails/*.png"))
check(len(rails) == 21, f"21 rail PNGs ({len(rails)})")
check(abs(fy + fh / 2 - 915) < 3, "footer at y915")
check(get("carousel", "gameCarousel").findtext("type") == "vertical", "carousel type vertical")

print("FAILURES:", len(fails))
sys.exit(1 if fails else 0)
