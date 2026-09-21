#!/usr/bin/env python3
"""PIL mock of the Crystal v10 gamelist art-direction pass, parsed from the
real theme XML. Mock only - not an ES-DE screenshot."""
import os, sys, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 960
ROOT = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal")
OUT = os.path.expanduser("~/workspace/crystal-esde-theme/work/proofs/mock_v10_full.png")

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
place(base, "./art/lib_panel.png", el_box(get("image", "libPanel")))
place(base, "./art/rails/gba.png", el_box(get("image", "libRail")))

fb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fr = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
marker = os.path.join(ROOT, "fonts/PermanentMarker-Regular.ttf")

# ------------------------------------------------------- panel contents ---
# marquee contrast shard + stand-in marquee art (no blue rectangle)
place(base, "./art/lib_marquee_back.png", el_box(get("image", "libMarqueeBack")))
mx, my, mw, mh = max_box(get("image", "libMarquee"))
f = ImageFont.truetype(marker, 52)
d.text((mx + mw / 2, my + mh / 2), "MARQUEE", font=f, fill=(255, 255, 255, 255), anchor="mm")
# yellow strike
place(base, "./art/lib_strike_yellow.png", el_box(get("image", "libPanelStrike")))

def fake_text(el, lines, size, color, font=fr):
    x, y, w, h = el_box(el)
    fnt = ImageFont.truetype(font, size)
    yy = y
    for ln in lines:
        d.text((x, yy), ln, font=fnt, fill=color)
        yy += size + 6

year = get("datetime", "libYear"); fake_text(year, ["1996"], 54, (10, 47, 160), marker)
genre = get("text", "libGenre"); fake_text(genre, ["PLATFORMER"], 19, (10, 47, 160), fb)
players = get("text", "libPlayers"); fake_text(players, ["1-2 PLAYERS"], 16, (58, 74, 115))
dev = get("text", "libDev"); fake_text(dev, ["NINTENDO"], 16, (58, 74, 115))
rx, ry, rw, rh = el_box(get("rating", "libRating"))
for i in range(4):
    star = Image.open(os.path.join(ROOT, "art/star_filled.png")).convert("RGBA").resize((26, 26))
    base.alpha_composite(star, (int(rx + i * 32), int(ry)))
desc = get("text", "libDesc")
fake_text(desc, ["A legendary platform adventure.", "Bowser has other plans this", "time - 120 stars await."], 17, (58, 74, 115))
sl = get("text", "libShotLabel"); fake_text(sl, ["SCREENSHOT"], 14, (58, 74, 115), marker)
sx, sy, sw, sh = el_box(get("image", "libScreenshot"))
d.rectangle([sx, sy, sx + sw, sy + sh], fill=(90, 130, 220, 255))
f2 = ImageFont.truetype(fb, 24)
d.text((sx + sw / 2, sy + sh / 2), "SCREENSHOT", font=f2, fill="white", anchor="mm")
place(base, "./art/lib_shot_frame.png", el_box(get("image", "libShotFrame")))

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

def dimmed_media(draw_base, cx_, cy_, w_, h_, kind):
    """Stand-in for real scraped physical media, dimmed like ES-DE's
    unfocused items (no debug circles)."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    if kind == "disk":
        r = w_ / 2
        dl.ellipse([cx_ - r, cy_ - r, cx_ + r, cy_ + r], fill=(120, 140, 200, 255))
        dl.ellipse([cx_ - r * 0.28, cy_ - r * 0.28, cx_ + r * 0.28, cy_ + r * 0.28],
                   fill=(200, 210, 235, 255))
    else:
        dl.rounded_rectangle([cx_ - w_ / 2, cy_ - h_ / 2, cx_ + w_ / 2, cy_ + h_ / 2],
                             radius=10, fill=(120, 140, 200, 255), outline=(200, 210, 235, 255), width=3)
    a = layer.split()[3].point(lambda v: int(v * 0.55))
    layer.putalpha(a)
    return Image.alpha_composite(draw_base, layer)

base = dimmed_media(base, cx, cy - pitch, iw, ih, "disk")     # prev, cropped top
base = dimmed_media(base, cx, cy + pitch, iw, ih, "cart")     # next, cropped bottom
d = ImageDraw.Draw(base)
# selected hero disk
r = sel / 2
d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 170, 220, 255), outline=(255, 255, 255, 255), width=4)
f4 = ImageFont.truetype(fb, 30)
d.text((cx, cy), "SELECTED\n520px", font=f4, fill="white", anchor="mm", align="center")

# title block
place(base, "./art/lib_rule_yellow.png", el_box(get("image", "libTitleRule")))
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

check(abs(sel - 520) < 2, f"selected hero {sel:.0f}px == 520")
check(abs(sel / iw - 2.8889) < 0.01, f"hero/neighbour ratio {sel/iw:.2f}x")
check(abs(pitch - 420) < 1, f"carousel pitch {pitch:.0f}px == 420")
prev_c = (cx, cy - pitch); next_c = (cx, cy + pitch)
check(abs(prev_c[0] - 900) < 2 and abs(prev_c[1] - 10) < 2, f"prev at ({prev_c[0]:.0f},{prev_c[1]:.0f}), cropped top")
check(abs(next_c[0] - 900) < 2 and abs(next_c[1] - 850) < 2, f"next at ({next_c[0]:.0f},{next_c[1]:.0f}), cropped bottom")
check(abs(cx - 900) < 2 and abs(cy - 430) < 2, "selected centre (900,430)")
check(ty + th <= next_c[1] - ih / 2 - 2, "title band clear above next disk")
check(ty >= cy + r + 4, "title band below hero disk")
pbx, pby, pbw, pbh = el_box(get("image", "libPanel"))
check(abs(pbx - 6) < 2 and abs(pbw - 480) < 2, "panel zone 480x940 at x6 (footprint kept)")
rbx, rby, rbw, rbh = el_box(get("image", "libRail"))
check(abs(rbx - 486) < 2 and abs(rbw - 76) < 2, "rail 76x912 at x486 (footprint kept)")
check(cx - r > rbx + rbw + 40, "hero clear of rail (>=40px)")
# v10 art-direction specifics
check(not has("image", "libSelectedGlow"), "yellow halo element retired")
check(has("image", "libHeroArc"), "gold arc highlight present")
check(has("image", "libMarqueeBack"), "marquee contrast shard present")
check(has("image", "libPanelStrike"), "yellow strike present")
m = get("image", "libMarquee")
check(float(m.findtext("opacity")) >= 1.0, "marquee full opacity")
check(mw >= 360 and mh >= 150, f"marquee box {mw:.0f}x{mh:.0f} large")
check(get("text", "libGameName").findtext("fontPath").endswith("PermanentMarker-Regular.ttf"),
      "title uses marker display face")
check(get("datetime", "libYear").findtext("fontPath").endswith("PermanentMarker-Regular.ttf"),
      "year uses marker display face")
c = get("carousel", "gameCarousel")
check(abs(float(c.findtext("unfocusedItemOpacity")) - 0.55) < 0.01, "neighbours opacity 0.55")
check(abs(float(c.findtext("unfocusedItemDimming")) - 0.45) < 0.01, "neighbours dimming 0.45")
check(abs(float(c.findtext("unfocusedItemSaturation")) - 0.6) < 0.01, "neighbours saturation 0.6")
# metadata stacking, no overlaps (new editorial order)
boxes = []
for tag, name in [("datetime","libYear"),("text","libGenre"),("text","libPlayers"),
                  ("text","libDev"),("rating","libRating"),("text","libDesc")]:
    boxes.append((name, el_box(get(tag, name))))
ok = True
for i in range(len(boxes) - 1):
    if boxes[i][1][1] + boxes[i][1][3] > boxes[i+1][1][1] + 1:
        ok = False; print("  overlap:", boxes[i][0], boxes[i+1][0])
check(ok, "metadata stacked without overlaps")
# screenshot + angular frame
check(abs(sw - 380) < 2 and abs(sh - 214) < 2, "screenshot 380x214")
fbx, fby, fbw, fbh = el_box(get("image", "libShotFrame"))
check(abs(fbw - 400) < 2 and abs(fbh - 234) < 2, "angular frame 400x234")
check(abs(sy + sh - 854) < 2, "screenshot bottom 854, inside panel zone")
import glob
rails = glob.glob(os.path.join(ROOT, "art/rails/*.png"))
check(len(rails) == 21, f"21 rail PNGs ({len(rails)})")
check(not os.path.exists(os.path.join(ROOT, "art/lib_glow_yellow.png")), "halo asset deleted")
check(abs(fy + fh/2 - 915) < 3, "footer at y915")
check(get("carousel","gameCarousel").findtext("type") == "vertical", "carousel type vertical")

print("FAILURES:", len(fails))
sys.exit(1 if fails else 0)
