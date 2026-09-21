#!/usr/bin/env python3
"""v7 flagship gamelist mock — renders the REAL views.xml gamelist geometry
at 1280x960 with stand-in scraped media. The layout numbers come from the
XML itself; only the media artwork and metadata VALUES are stand-ins.

Variants:
  mock_v7_full.png      - marquee scraped
  mock_v7_no_marquee.png - marquee missing -> big fallback title
"""
import os, math, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops

W, H = 1280, 960
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "theme-src", "crystal")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proofs")
os.makedirs(OUT, exist_ok=True)

VARS = {"crystalText": "FFFFFF", "crystalDim": "BFD4FF", "crystalAccent": "FFD60A",
        "crystalDeep": "0A2FA0", "crystalInkDim": "3A4A73"}

def resolve(v):
    v = v.strip()
    if v.startswith("${") and v.endswith("}"):
        return VARS[v[2:-1]]
    return v

def rgb(h):
    h = resolve(h)
    h = h[-6:]
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def parse_view():
    tree = ET.parse(os.path.join(ROOT, "views.xml"))
    els = {}
    for view in tree.getroot().iter("view"):
        if view.get("name") == "gamelist":
            for el in view:
                if "name" in el.attrib:
                    d = {"tag": el.tag}
                    for child in el:
                        d[child.tag] = (child.text or "").strip()
                    els[el.get("name")] = d
    return els

ELS = parse_view()

def nx(x): return x * W
def ny(y): return y * H
def pair(s): return tuple(float(v) for v in s.split())

def elpos(name):
    e = ELS[name]
    x, y = pair(e["pos"])
    ox, oy = pair(e.get("origin", "0 0"))
    if "size" in e:
        w, h = pair(e["size"]); w, h = nx(w), ny(h)
    elif "maxSize" in e:
        w, h = pair(e["maxSize"]); w, h = nx(w), ny(h)
    else:
        w = h = 0
    return (nx(x) - ox * w, ny(y) - oy * h, w, h)

def font(sz, bold=True):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    return ImageFont.truetype(p, max(8, int(sz)))

# ---------------------------------------------------------------- stand-ins
def make_marquee():
    im = Image.new("RGBA", (760, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((380, 105), "LORD OF THE RINGS", font=font(64), anchor="mm",
           fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(10, 47, 160, 255))
    d.text((380, 205), "THE THIRD AGE", font=font(48), anchor="mm",
           fill=(255, 214, 10, 255), stroke_width=3, stroke_fill=(10, 47, 160, 255))
    return im

def make_disc(label, accent):
    S = 340
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([8, 8, S-8, S-8], fill=(232, 236, 244, 255), outline=(160, 170, 190, 255), width=3)
    d.ellipse([28, 28, S-28, S-28], fill=accent + (255,))
    d.ellipse([60, 60, S-60, S-60], fill=(240, 244, 252, 255), outline=(160, 170, 190, 255), width=2)
    d.text((S/2, 70), label, font=font(26), anchor="ma", fill=(255, 255, 255, 255))
    d.text((S/2, S/2 - 46), "GAME BOY ADVANCE", font=font(17), anchor="mm", fill=(90, 100, 130, 255))
    d.ellipse([S/2-28, S/2+2, S/2+28, S/2+58], fill=(250, 250, 252, 255), outline=(150, 160, 180, 255), width=2)
    return im

def wrapped(d, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            lines.append(cur); cur = w_
    lines.append(cur)
    return lines

def apply_image_fx(im, opacity=1.0, saturation=1.0, color=None):
    """Replicate ES-DE image pipeline: saturation, color multiply, opacity."""
    im = im.copy()
    alpha = im.split()[3]
    rgb_im = im.convert("RGB")
    if saturation < 1.0:
        g = rgb_im.convert("L").convert("RGB")
        rgb_im = Image.blend(rgb_im, g, 1.0 - saturation)
    if color:
        c = Image.new("RGB", im.size, rgb(color))
        rgb_im = ImageChops.multiply(rgb_im, c)
    im = rgb_im.convert("RGBA")
    im.putalpha(alpha.point(lambda v: int(v * opacity)))
    return im

# ---------------------------------------------------------------- compose
GAMES = [
    ("MARIO KART", (200, 60, 60)),
    ("POKEMON EMERALD", (30, 150, 80)),
    ("THE THIRD AGE", (40, 80, 200)),
    ("METROID FUSION", (230, 140, 20)),
    ("ARIA OF SORROW", (120, 60, 180)),
]
META = dict(year="2004", genre="Role-playing", players="1-2",
            dev="Griptonite Games",
            desc=("The War of the Ring comes to Game Boy Advance. Lead the "
                  "fellowship through the Mines of Moria in this turn-based "
                  "tactical retelling of the epic trilogy."))

def compose(with_marquee=True):
    im = Image.open(os.path.join(ROOT, "art", "gamelist_generic_bg.png")).convert("RGB").resize((W, H))
    im = im.convert("RGBA")
    d = ImageDraw.Draw(im)

    # ---- marquee hero (z19 fallback, z20 art)
    if with_marquee:
        e = ELS["libMarquee"]
        mq = make_marquee()
        mw, mh = pair(e["maxSize"]); mw, mh = nx(mw), ny(mh)
        mq.thumbnail((int(mw), int(mh)), Image.LANCZOS)
        mq = apply_image_fx(mq, opacity=float(e["opacity"]),
                            saturation=float(e["saturation"]), color=e["color"])
        mq = mq.rotate(-float(e["rotation"]), expand=True, resample=Image.BICUBIC)
        cx, cy = pair(e["pos"]); cx, cy = nx(cx), ny(cy)
        im.paste(mq, (int(cx - mq.width / 2), int(cy - mq.height / 2)), mq)
    else:
        e = ELS["libMarqueeTitle"]
        x, y, w, h = elpos("libMarqueeTitle")
        f = font(ny(float(e["fontSize"])))
        a = Image.new("RGBA", im.size, (0, 0, 0, 0))
        da = ImageDraw.Draw(a)
        lines = wrapped(da, META_TITLE.upper(), f, w)
        yy = y + h / 2 - len(lines) * ny(float(e["fontSize"])) * 0.62
        for line in lines:
            da.text((x, yy), line, font=f, fill=rgb(e["color"]) + (255,))
            yy += ny(float(e["fontSize"])) * 1.15
        a.putalpha(a.split()[3].point(lambda v: int(v * float(e["opacity"]))))
        im = Image.alpha_composite(im, a)
        d = ImageDraw.Draw(im)

    # ---- editorial metadata block (z60)
    e = ELS["libYear"]; x, y, w, h = elpos("libYear")
    d.text((x, y), META["year"], font=font(ny(float(e["fontSize"]))), fill=rgb(e["color"]))
    e = ELS["libGenre"]; x, y, w, h = elpos("libGenre")
    d.text((x, y), META["genre"].upper(), font=font(ny(float(e["fontSize"]))), fill=rgb(e["color"]))
    e = ELS["libPlayers"]; x, y, w, h = elpos("libPlayers")
    d.text((x, y), META["players"] + " PLAYERS", font=font(ny(float(e["fontSize"]))), fill=rgb(e["color"]))
    e = ELS["libDev"]; x, y, w, h = elpos("libDev")
    d.text((x, y), META["dev"].upper(), font=font(ny(float(e["fontSize"])), bold=False), fill=rgb(e["color"]))
    e = ELS["libRating"]; x, y, w, h = elpos("libRating")
    fs = Image.open(os.path.join(ROOT, "art", "star_filled.png")).convert("RGBA")
    fs.thumbnail((26, 26), Image.LANCZOS)
    for i in range(4):
        im.paste(fs, (int(x + i * 30), int(y - 13)), fs)
    e = ELS["libDesc"]; x, y, w, h = elpos("libDesc")
    df = font(ny(float(e["fontSize"])), bold=False)
    yy = y
    for line in wrapped(d, META["desc"], df, w)[:8]:
        d.text((x, yy), line, font=df, fill=rgb(e["color"])); yy += ny(float(e["fontSize"])) * 1.28

    # ---- atmosphere: blue glow, yellow glow, shadow (z47-49)
    for name in ["libSelectedGlowBlue", "libSelectedGlow", "libSelectedShadow"]:
        e = ELS[name]
        x, y, w, h = elpos(name)
        g = Image.open(os.path.join(ROOT, "art", e["path"].replace("./art/", ""))).convert("RGBA")
        g = g.resize((int(w), int(h)), Image.LANCZOS)
        op = float(e.get("opacity", "1"))
        if op < 1.0:
            g.putalpha(g.split()[3].point(lambda v, o=op: int(v * o)))
        im = Image.alpha_composite(im, _place(g, int(x), int(y)))
    d = ImageDraw.Draw(im)

    # ---- carousel (z50)
    c = ELS["gameCarousel"]
    cx, cy = pair(c["pos"]); cw, ch = pair(c["size"])
    box_x, box_y = nx(cx) - nx(cw) / 2, ny(cy) - ny(ch) / 2
    box_w, box_h = nx(cw), ny(ch)
    iw, ih = pair(c["itemSize"]); iw, ih = nx(iw), ny(ih)
    scale = float(c["itemScale"])
    spacing = nx(cw) / float(c["maxItemCount"])
    lift = ny(float(c["selectedItemOffset"].split()[1]))
    uo, us, ud = float(c["unfocusedItemOpacity"]), float(c["unfocusedItemSaturation"]), float(c["unfocusedItemDimming"])
    for i, (lab, accent) in enumerate(GAMES):
        dist = i - 2
        disc = make_disc(lab, accent)
        if dist == 0:
            disc = disc.resize((int(iw * scale), int(ih * scale)), Image.LANCZOS)
        else:
            disc.thumbnail((int(iw), int(ih)), Image.LANCZOS)
            a = disc.split()[3].point(lambda v: int(v * uo))
            rgb_im = disc.convert("RGB")
            g = rgb_im.convert("L").convert("RGB")
            rgb_im = Image.blend(rgb_im, g, 1.0 - us)
            rgb_im = ImageEnhance.Brightness(rgb_im).enhance(1.0 - ud)
            disc = rgb_im.convert("RGBA"); disc.putalpha(a)
        x = nx(cx) + dist * spacing - disc.width / 2
        y = box_y + box_h - disc.height + (lift if dist == 0 else 0)
        im.paste(disc, (int(x), int(y)), disc)
    d = ImageDraw.Draw(im)

    # ---- title block (z60)
    e = ELS["libTitleRule"]; x, y, w, h = elpos("libTitleRule")
    rule = Image.open(os.path.join(ROOT, "art", "lib_rule_yellow.png")).convert("RGBA")
    rule = rule.resize((int(w), max(4, int(h))), Image.LANCZOS)
    im.paste(rule, (int(x), int(y)), rule)
    e = ELS["libGameName"]; x, y, w, h = elpos("libGameName")
    tf = font(ny(float(e["fontSize"])))
    title = "THE LORD OF THE RINGS: THE THIRD AGE"
    lines = wrapped(d, title, tf, w)
    yy = y + h / 2 - len(lines) * ny(float(e["fontSize"])) * 0.60
    for line in lines:
        d.text((x + w / 2, yy), line, font=tf, anchor="ma", fill=(255, 255, 255)); yy += ny(float(e["fontSize"])) * 1.12
    # kicker
    kf = font(ny(0.018))
    kc = rgb(VARS["crystalDim"]); ac = rgb(VARS["crystalAccent"])
    yk = ny(0.814)
    gtxt, ytxt, ptxt = META["genre"].upper(), META["year"], META["players"] + " PLAYERS"
    d.text((nx(0.44), yk), gtxt, font=kf, anchor="ra", fill=kc)
    d.text((nx(0.462), yk), "•", font=kf, anchor="ma", fill=ac)
    d.text((nx(0.50), yk), ytxt, font=kf, anchor="ma", fill=kc)
    d.text((nx(0.538), yk), "•", font=kf, anchor="ma", fill=ac)
    d.text((nx(0.56), yk), ptxt, font=kf, anchor="la", fill=kc)

    # ---- logo (z60)
    logo = Image.open(os.path.join(ROOT, "art", "console_logos", "gba.png")).convert("RGBA")
    e = ELS.get("libConsoleLogo")  # per-system override lives in gba/theme.xml
    lw, lh = nx(0.34), ny(0.060)
    logo.thumbnail((int(lw), int(lh)), Image.LANCZOS)
    im.paste(logo, (int(nx(0.5) - logo.width / 2), int(ny(0.880) - logo.height / 2)), logo)

    # ---- footer (z60): quiet single row
    ff = font(ny(0.016), bold=False)
    d.text((nx(0.5), ny(0.952)), "A SELECT      B BACK      Y OPTIONS      START MENU",
           font=ff, anchor="mm", fill=(255, 255, 255, 166))
    return im.convert("RGB")

def _place(im2, x, y):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(im2, (x, y), im2)
    return layer

META_TITLE = "The Lord of the Rings: The Third Age"

for name, kw in [("mock_v7_full", {"with_marquee": True}),
                 ("mock_v7_no_marquee", {"with_marquee": False})]:
    compose(**kw).save(os.path.join(OUT, name + ".png"))
    print("wrote", name)
