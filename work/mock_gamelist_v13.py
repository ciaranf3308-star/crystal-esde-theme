#!/usr/bin/env python3
"""PIL mock of the Crystal v13 gamelist premium-polish pass, parsed from the
real theme XML. Mock only - not an ES-DE screenshot.

Animation-aware art direction is IMPLIED only: the static mock suggests
motion the engine could show (aura pulse layer, faint slide echoes on the
neighbours, sweep head on the title rule). ES-DE 3.4.1 has no theme
keyframes or idle animation, and none is claimed - the real build shows
native eased carousel transitions.

v13 vs v12: the selected disc is dimensionally lit (directional studio
light, dark rim + specular edge arcs, data-band rings, layered gloss
sheen, beveled hub) instead of a flat vector circle; the next-item
stand-in is a proper mini cartridge; the left panel is de-boxed into an
editorial sidebar; the spine is a thinner 60px magazine spine."""
import os, sys, glob, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 960
ROOT = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal")
OUT = os.path.expanduser("~/workspace/crystal-esde-theme/work/proofs/mock_v13_full.png")

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

# ----------------------------------------------- marquee: headline block ---
mx, my, mw, mh = max_box(get("image", "libMarquee"))
f = ImageFont.truetype(marker, 46)
d.text((mx + mw / 2, my + mh / 2 - 12), "SUPER MARIO 64", font=f,
       fill=(10, 47, 160, 255), anchor="mm")
d.rectangle([mx + mw / 2 - 140, my + mh / 2 + 32, mx + mw / 2 + 140, my + mh / 2 + 38],
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
    """A dimensional physical disc: directional studio light from the
    upper-left, dark rim, specular edge arcs, data-band rings, layered
    gloss sheen, beveled hub. The real theme shows the user's scanned
    physical media here; this stand-in proves the lighting treatment."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    # base: concentric rings, light pooled toward the upper-left
    steps = 48
    for i in range(steps, 0, -1):
        t = i / steps
        rr = r * t
        ox = -r * 0.18 * (1 - t)
        oy = -r * 0.22 * (1 - t)
        col = (int(48 + 104 * (1 - t)), int(72 + 100 * (1 - t)), int(154 + 62 * (1 - t)))
        dl.ellipse([cx_ + ox - rr, cy_ + oy - rr, cx_ + ox + rr, cy_ + oy + rr],
                   fill=col + (255,))
    # dark blue data ring + pale inner disc
    dl.ellipse([cx_ - r * 0.68, cy_ - r * 0.68, cx_ + r * 0.68, cy_ + r * 0.68],
               fill=(14, 48, 150, 255))
    dl.ellipse([cx_ - r * 0.60, cy_ - r * 0.60, cx_ + r * 0.60, cy_ + r * 0.60],
               fill=(226, 232, 246, 255))
    # data-band rings on the blue area
    for rr in (0.78, 0.84, 0.90):
        dl.ellipse([cx_ - r * rr, cy_ - r * rr, cx_ + r * rr, cy_ + r * rr],
                   outline=(255, 255, 255, 22), width=max(1, int(r * 0.008)))
    # refined gold accent ring + tight soft accent
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        [cx_ - r * 0.72, cy_ - r * 0.72, cx_ + r * 0.72, cy_ + r * 0.72],
        outline=(255, 200, 60, 55), width=max(4, int(r * 0.035)))
    layer = Image.alpha_composite(layer, glow.filter(ImageFilter.GaussianBlur(6)))
    dl = ImageDraw.Draw(layer)
    dl.ellipse([cx_ - r * 0.72, cy_ - r * 0.72, cx_ + r * 0.72, cy_ + r * 0.72],
               outline=(255, 214, 10, 255), width=max(3, int(r * 0.018)))
    # outer rim: dark edge band, specular arc upper-left, shade arc lower-right
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
    """A proper mini cartridge stand-in (N64-style): dark slate body,
    grip ridges, pale label with a royal stripe and title bar, top-edge
    highlight. Dimmed in place it reads as real neighbouring media, not a
    placeholder tile."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = cx_ - w_ / 2, cy_ - h_ / 2, cx_ + w_ / 2, cy_ + h_ / 2
    dl.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=(46, 54, 82, 255))
    dl.rounded_rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], radius=7,
                         outline=(20, 26, 52, 255), width=2)
    dl.line([(x0 + 8, y0 + 3), (x1 - 8, y0 + 3)], fill=(255, 255, 255, 70), width=2)
    # label: pale panel, royal stripe, title bar
    dl.rounded_rectangle([x0 + 12, y0 + 12, x1 - 12, cy_ + h_ / 4], radius=5,
                         fill=(228, 234, 248, 255))
    dl.rectangle([x0 + 12, cy_ - h_ / 8, x1 - 12, cy_ - h_ / 8 + 10],
                 fill=(18, 58, 178, 255))
    dl.rectangle([x0 + 24, y0 + 24, x1 - 24, y0 + 34], fill=(10, 26, 92, 255))
    # grip ridges, lower half
    for gx in (cx_ - 22, cx_, cx_ + 22):
        dl.line([(gx, cy_ + h_ / 4 + 16), (gx, y1 - 12)], fill=(30, 36, 60, 255), width=4)
    return layer

# neighbours: real media, smaller, edge-cropped, dimmed; faint slide echoes
# (mock-only) imply carousel motion
base = Image.alpha_composite(base, faint(disk_layer(cx - 24, cy - pitch, iw / 2)))
base = Image.alpha_composite(base, dim(disk_layer(cx, cy - pitch, iw / 2)))
base = Image.alpha_composite(base, faint(cart_layer(cx + 24, cy + pitch, iw, ih)))
base = Image.alpha_composite(base, dim(cart_layer(cx, cy + pitch, iw, ih)))
d = ImageDraw.Draw(base)
# selected hero disk, dimensionally lit (540px)
hero = disk_layer(cx, cy, sel / 2)
base = Image.alpha_composite(base, hero)
d = ImageDraw.Draw(base)

# title block: wider rule, bolder title, refined genre line
place(base, "./art/lib_title_rule.png", el_box(get("image", "libTitleRule")))
te = get("text", "libGameName")
tx, ty, tw, th = el_box(te)
f5 = ImageFont.truetype(marker, 32)
d.text((tx + tw / 2, ty + th / 2), "SUPER MARIO 64", font=f5, fill="white", anchor="mm")
me = get("text", "libMetaGenre")
gx_, gy_, gw_, gh_ = el_box(me)
f7 = ImageFont.truetype(fb, 13)
# tracked small caps
ttext = "P L A T F O R M E R"
d.text((gx_ + gw_ / 2, gy_ + gh_ / 2), ttext, font=f7, fill=(255, 255, 255, 166), anchor="mm")
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
check(abs(sel - 540) < 2, f"selected hero {sel:.0f}px == 540 (dominant)")
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
check(abs(rbx - 486) < 2 and abs(rbw - 60) < 2 and abs(rbh - 912) < 2,
      f"spine 60x912 at x486 (thinner magazine spine, authorized refinement)")
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
check(abs(tbw - 300) < 2, "title rule widened to 300px")
check(abs(ty + th / 2 - 736) < 2, "title at Y736")
check(abs(gy_ + gh_ / 2 - 757.5) < 3, "genre line at Y757")
check(gy_ + gh_ / 2 > ty + th / 2, "genre line beneath the title")

# --- v13 premium-polish specifics ---
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
      "restrained gold aura + layered ring present (no giant halo)")
check(has("text", "libMetaGenre"), "refined genre line under the title")
mg = get("text", "libMetaGenre")
check(mg.findtext("metadata") == "genre", "genre line bound to genre metadata")
check(mg.findtext("letterCase") == "uppercase", "genre line uppercase")
check(mg.findtext("color") == "A6FFFFFF", "genre line subdued white")
check(abs(float(mg.findtext("fontSize")) - 0.0135) < 0.0005, "genre line small refined size")
m = get("image", "libMarquee")
check(float(m.findtext("opacity")) >= 1.0, "marquee full opacity")
check(mw >= 360 and mh >= 150, f"marquee box {mw:.0f}x{mh:.0f} large, headline-block feel")
mt = get("text", "libMarqueeTitle")
check(mt.findtext("color") == "${crystalDeep}", "marquee fallback ink on the white mat")
check(abs(float(mt.findtext("fontSize")) - 0.032) < 0.001, "marquee fallback type larger (0.032)")
check(abs(float(get("text", "libGameName").findtext("fontSize")) - 0.034) < 0.001,
      "title bolder (0.034)")
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
# spine: 21 rails, 60px wide, one thin yellow separator line
rails = glob.glob(os.path.join(ROOT, "art/rails/*.png"))
check(len(rails) == 21, f"21 spine PNGs ({len(rails)})")
rail = Image.open(os.path.join(ROOT, "art/rails/gba.png")).convert("RGB")
check(rail.size == (60, 912), f"spine PNG 60x912 ({rail.size[0]}x{rail.size[1]})")
def _is_yellow(p):
    return abs(p[0] - 255) < 20 and abs(p[1] - 214) < 30 and abs(p[2] - 10) < 30
yell = sum(1 for y in range(48, 885, 8) if _is_yellow(rail.getpixel((4, y))))
check(yell > 90, f"spine carries the thin yellow separator line ({yell} samples)")
check(abs(fy + fh / 2 - 915) < 3, "footer at y915")
check(get("carousel", "gameCarousel").findtext("type") == "vertical", "carousel type vertical")
# hero aura/ring assets exist and are restrained (transparent cores)
aura = Image.open(os.path.join(ROOT, "art/lib_hero_aura.png")).convert("RGBA")
check(aura.getpixel((340, 340))[3] < 8, "aura core transparent (no blurry halo)")
ring = Image.open(os.path.join(ROOT, "art/lib_hero_ring.png")).convert("RGBA")
check(ring.getpixel((310, 310))[3] < 8, "ring core transparent")
# layered ring: outer hairline + main gold band + inner light line
def _gold(p):
    return p[3] > 100 and abs(p[0] - 255) < 25 and abs(p[1] - 214) < 40 and p[2] < 60
check(_gold(ring.getpixel((32, 310))), "main gold band present")
ph = ring.getpixel((23, 310))
check(ph[3] > 60 and abs(ph[0] - 255) < 40 and abs(ph[1] - 226) < 40,
      "outer pale-gold hairline present")
il = ring.getpixel((38, 310))
check(il[3] > 100 and abs(il[0] - 255) < 30 and abs(il[1] - 240) < 30 and il[2] > 120,
      "inner light line present")

print("FAILURES:", len(fails))
sys.exit(1 if fails else 0)
