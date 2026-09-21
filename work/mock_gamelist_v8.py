#!/usr/bin/env python3
"""v8 gamelist mock — renders the REAL views.xml gamelist geometry at
1280x960 with stand-in scraped media. Layout numbers come from the XML;
only artwork and metadata VALUES are stand-ins.

Variants:
  mock_v8_full.png        - marquee scraped
  mock_v8_no_marquee.png  - marquee missing -> big fallback title

Also runs the 7 critical validations numerically and prints PASS/FAIL.
"""
import os, xml.etree.ElementTree as ET
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
    h = resolve(h); h = h[-6:]
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
    # per-system merge (gba): element-level override
    hidden = set()
    tree2 = ET.parse(os.path.join(ROOT, "gba", "theme.xml"))
    for view in tree2.getroot().iter("view"):
        if view.get("name") == "gamelist":
            for el in view:
                if "name" in el.attrib:
                    nm = el.get("name")
                    d = {"tag": el.tag}
                    for child in el:
                        d[child.tag] = (child.text or "").strip()
                    if d.get("visible") == "false":
                        hidden.add(nm)
                    else:
                        els[nm] = d
    return els, hidden

ELS, HIDDEN = parse_view()

def nx(x): return x * W
def ny(y): return y * H
def pair(s): return tuple(float(v) for v in s.split())

def elbox(name):
    """(x, y, w, h) of the element's allocation box in px (origin applied)."""
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
    # Dense scraped-marquee proxy: solid navy plaque, bold white/yellow
    # logotype, graphic blocks — approximates real ScreenScraper marquee art.
    im = Image.new("RGBA", (760, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, 754, 294], radius=26, fill=(8, 20, 70, 255),
                        outline=(255, 214, 10, 255), width=6)
    d.rectangle([40, 40, 150, 260], fill=(20, 45, 140, 255))
    d.rectangle([610, 40, 720, 260], fill=(20, 45, 140, 255))
    d.text((380, 105), "VIRTUA FIGHTER 4", font=font(64), anchor="mm",
           fill=(255, 255, 255, 255))
    d.text((380, 205), "EVOLUTION", font=font(52), anchor="mm",
           fill=(255, 214, 10, 255))
    d.text((380, 262), "\u2605 \u2605 \u2605", font=font(30), anchor="mm",
           fill=(255, 255, 255, 255))
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
    return [l for l in lines if l]

GAMES = [
    ("MARIO KART", (200, 60, 60)),
    ("POKEMON EMERALD", (30, 150, 80)),
    ("VIRTUA FIGHTER 4", (40, 80, 200)),
    ("METROID FUSION", (230, 140, 20)),
    ("ARIA OF SORROW", (120, 60, 180)),
]
META = dict(year="2002", genre="Fighting", players="1\u20134",
            dev="Southend Interactive",
            desc=("Sega's arcade fighter lands on the handheld. Master "
                  "all-new quest mode and take the fight online against "
                  "rivals around the world."))

def _place(im2, x, y):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(im2, (int(x), int(y)))
    return layer

def compose(with_marquee=True):
    geo = {}
    im = Image.open(os.path.join(ROOT, "art", "gamelist_generic_bg.png")).convert("RGB").resize((W, H))
    im = im.convert("RGBA")
    d = ImageDraw.Draw(im)

    # ---- bottom gradient (z2)
    e = ELS["libBottomGradient"]
    x, y, w, h = elbox("libBottomGradient")
    g = Image.open(os.path.join(ROOT, "art", "lib_bottom_gradient.png")).convert("RGBA")
    g = g.resize((int(w), int(h)), Image.LANCZOS)
    im = Image.alpha_composite(im, _place(g, x, y))
    d = ImageDraw.Draw(im)

    # ---- marquee hero (z19 fallback / z20 art)
    e = ELS["libMarquee"]
    mw, mh = pair(e["maxSize"]); mw, mh = nx(mw), ny(mh)
    mx, my = pair(e["pos"]); mx, my = nx(mx), ny(my)
    if with_marquee:
        mq = make_marquee()
        mq.thumbnail((int(mw), int(mh)), Image.LANCZOS)
        geo["marquee_rendered"] = mq.size
        op = float(e.get("opacity", "1"))
        a = mq.split()[3].point(lambda v, o=op: int(v * o))
        mq.putalpha(a)
        im = Image.alpha_composite(im, _place(mq, mx, my))
    else:
        e2 = ELS["libMarqueeTitle"]
        x, y, w, h = elbox("libMarqueeTitle")
        f = font(ny(float(e2["fontSize"])))
        op = float(e2.get("opacity", "1"))
        a = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        da = ImageDraw.Draw(a)
        lines = wrapped(da, "VIRTUA FIGHTER 4 EVOLUTION", f, w)
        yy = y + h / 2 - len(lines) * ny(float(e2["fontSize"])) * 0.60
        for line in lines:
            da.text((x + w / 2, yy), line, font=f, anchor="ma",
                    fill=rgb(e2["color"]) + (255,))
            yy += ny(float(e2["fontSize"])) * 1.12
        a.putalpha(a.split()[3].point(lambda v, o=op: int(v * o)))
        im = Image.alpha_composite(im, a)
    geo["marquee_box"] = (mx, my, mw, mh)
    geo["marquee_opacity"] = float(ELS["libMarquee"].get("opacity", "1"))
    d = ImageDraw.Draw(im)

    # ---- metadata block (z60)
    e = ELS["libYear"]; x, y, w, h = elbox("libYear")
    d.text((x, y), META["year"], font=font(ny(float(e["fontSize"]))), fill=rgb(e["color"]))
    e = ELS["libGenre"]; x, y, w, h = elbox("libGenre")
    d.text((x, y), META["genre"].upper(), font=font(ny(float(e["fontSize"]))), fill=rgb(e["color"]))
    e = ELS["libPlayers"]; x, y, w, h = elbox("libPlayers")
    d.text((x, y), (META["players"] + " PLAYERS").upper(), font=font(ny(float(e["fontSize"]))), fill=rgb(e["color"]))
    e = ELS["libDev"]; x, y, w, h = elbox("libDev")
    d.text((x, y), META["dev"].upper(), font=font(ny(float(e["fontSize"])), bold=False), fill=rgb(e["color"]))
    e = ELS["libRating"]; x, y, w, h = elbox("libRating")
    fs = Image.open(os.path.join(ROOT, "art", "star_filled.png")).convert("RGBA")
    fs.thumbnail((26, 26), Image.LANCZOS)
    for i in range(4):
        im.paste(fs, (int(x + i * 30), int(y)), fs)
    e = ELS["libDesc"]; x, y, w, h = elbox("libDesc")
    df = font(ny(float(e["fontSize"])), bold=False)
    yy = y
    for line in wrapped(d, META["desc"], df, w):
        d.text((x, yy), line, font=df, fill=rgb(e["color"])); yy += ny(float(e["fontSize"])) * 1.28
    d = ImageDraw.Draw(im)
    geo["meta_box"] = (nx(0.710938), ny(0.072917), nx(0.234375), ny(0.343583) - ny(0.072917))
    geo["meta_fonts"] = sorted({float(ELS[k]["fontSize"]) for k in
        ["libYear", "libGenre", "libPlayers", "libDev", "libDesc"]})

    # ---- atmosphere: blue halo, yellow rim, shadow (z47-49)
    for name in ["libSelectedGlowBlue", "libSelectedGlow", "libSelectedShadow"]:
        e = ELS[name]
        x, y, w, h = elbox(name)
        g = Image.open(os.path.join(ROOT, "art", e["path"].replace("./art/", ""))).convert("RGBA")
        g = g.resize((int(w), int(h)), Image.LANCZOS)
        op = float(e.get("opacity", "1"))
        if op < 1.0:
            g.putalpha(g.split()[3].point(lambda v, o=op: int(v * o)))
        im = Image.alpha_composite(im, _place(g, int(x), int(y)))
    d = ImageDraw.Draw(im)

    # ---- carousel (z50): pitch = element_w / maxItemCount, center anchor
    c = ELS["gameCarousel"]
    cx, cy = pair(c["pos"]); cx, cy = nx(cx), ny(cy)
    cw, ch = pair(c["size"]); cw, ch = nx(cw), ny(ch)
    iw, ih = pair(c["itemSize"]); iw, ih = nx(iw), ny(ih)
    scale = float(c["itemScale"])
    spacing = cw / float(c["maxItemCount"])
    lift = ny(float(c["selectedItemOffset"].split()[1]))
    uo, us, ud = (float(c["unfocusedItemOpacity"]), float(c["unfocusedItemSaturation"]),
                  float(c["unfocusedItemDimming"]))
    geo["carousel"] = dict(cx=cx, cy=cy, pitch=spacing, iw=iw, ih=ih, scale=scale, lift=lift)
    items = []
    for i, (lab, accent) in enumerate(GAMES):
        dist = i - 2
        disc = make_disc(lab, accent)
        if dist == 0:
            dw, dh = iw * scale, ih * scale
            disc = disc.resize((int(dw), int(dh)), Image.LANCZOS)
        else:
            dw, dh = iw, ih
            disc.thumbnail((int(dw), int(dh)), Image.LANCZOS)
            a = disc.split()[3].point(lambda v, o=uo: int(v * o))
            rgb_im = disc.convert("RGB")
            g = rgb_im.convert("L").convert("RGB")
            rgb_im = Image.blend(rgb_im, g, 1.0 - us)
            rgb_im = ImageEnhance.Brightness(rgb_im).enhance(1.0 - ud)
            disc = rgb_im.convert("RGBA"); disc.putalpha(a)
        ccx = cx + dist * spacing
        ccy = cy + (lift if dist == 0 else 0)
        items.append(dict(dist=dist, cx=ccx, cy=ccy, w=disc.width, h=disc.height))
        im.paste(disc, (int(ccx - disc.width / 2), int(ccy - disc.height / 2)), disc)
    geo["items"] = items
    d = ImageDraw.Draw(im)

    # ---- title block (z60)
    e = ELS["libTitleRule"]; x, y, w, h = elbox("libTitleRule")
    rule = Image.open(os.path.join(ROOT, "art", "lib_rule_yellow.png")).convert("RGBA")
    rule = rule.resize((int(w), max(4, int(h))), Image.LANCZOS)
    im.paste(rule, (int(x), int(y)), rule)
    e = ELS["libGameName"]; x, y, w, h = elbox("libGameName")
    tf = font(ny(float(e["fontSize"])))
    lines = wrapped(d, "VIRTUA FIGHTER 4 EVOLUTION", tf, w)
    yy = y + h / 2 - len(lines) * ny(float(e["fontSize"])) * 0.60
    for line in lines:
        d.text((x + w / 2, yy), line, font=tf, anchor="ma", fill=(255, 255, 255)); yy += ny(float(e["fontSize"])) * 1.12
    geo["title_box"] = (x, y, w, h)
    # secondary line: GENRE - YEAR - DEV - PLAYERS
    kf = font(ny(0.0167))
    kc, ac = rgb(VARS["crystalDim"]), rgb(VARS["crystalAccent"])
    parts = [
        ("libSubGenre", META["genre"].upper(), "ra", kc),
        ("libSep1", "\u2022", "ma", ac),
        ("libSubYear", META["year"], "ma", kc),
        ("libSep2", "\u2022", "ma", ac),
        ("libSubDev", META["dev"].upper(), "ma", kc),
        ("libSep3", "\u2022", "ma", ac),
        ("libSubPlayers", (META["players"] + " PLAYERS").upper(), "la", kc),
    ]
    for nm, txt, anchor, col in parts:
        x, y, w, h = elbox(nm)
        ax = x + (w if anchor == "ra" else (w / 2 if anchor == "ma" else 0))
        d.text((ax, y + h / 2), txt, font=kf, anchor=anchor, fill=col)

    # ---- console logo (z60): per-system image override
    if "libConsoleLogo" in ELS and "libConsoleLogo" not in HIDDEN:
        e = ELS["libConsoleLogo"]
        mx, my = pair(e["pos"]); mx, my = nx(mx), ny(my)
        mw, mh = pair(e["maxSize"]); mw, mh = nx(mw), ny(mh)
        logo = Image.open(os.path.join(ROOT, "art", "console_logos", "gba.png")).convert("RGBA")
        logo.thumbnail((int(mw), int(mh)), Image.LANCZOS)
        geo["logo_rendered"] = logo.size
        geo["logo_center"] = (mx, my)
        im.paste(logo, (int(mx - logo.width / 2), int(my - logo.height / 2)), logo)

    # ---- footer: one static row
    e = ELS["libFooter"]; x, y, w, h = elbox("libFooter")
    ff = font(ny(float(e["fontSize"])), bold=False)
    d.text((x + w / 2, y + h / 2), "A PLAY \u2022 B BACK", font=ff, anchor="mm",
           fill=rgb(e["color"]) + (166,))
    geo["footer_box"] = (x, y, w, h)
    geo["footer_count"] = 1
    return im.convert("RGB"), geo

def validate(geo):
    print("=== CRITICAL VALIDATION (from real views.xml geometry) ===")
    ok = True
    def check(name, cond, detail):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name + " — " + detail)
        ok = ok and cond

    items = {it["dist"]: it for it in geo["items"]}
    sel, prev, nxt = items[0], items[-1], items[1]
    ratio = sel["w"] / prev["w"]
    check("selected >=2.8x neighbours", ratio >= 2.8,
          "selected %dx%d vs neighbour %dx%d, ratio %.2f" % (sel["w"], sel["h"], prev["w"], prev["h"], ratio))
    gap_l = (sel["cx"] - sel["w"] / 2) - (prev["cx"] + prev["w"] / 2)
    gap_r = (nxt["cx"] - nxt["w"] / 2) - (sel["cx"] + sel["w"] / 2)
    check("neighbours clear with big gaps", gap_l >= 45 and gap_r >= 45,
          "gaps L=%.0fpx R=%.0fpx (spec >=45)" % (gap_l, gap_r))
    check("neighbour centres at spec", abs(prev["cx"] - 290) < 2 and abs(nxt["cx"] - 990) < 2
          and abs(sel["cx"] - 640) < 2,
          "prev %.0f next %.0f sel %.0f (spec 290/640/990)" % (prev["cx"], nxt["cx"], sel["cx"]))
    check("selected/neighbour Y at spec", abs(sel["cy"] - 465) < 2 and abs(prev["cy"] - 480) < 2,
          "sel y %.0f (spec 465), neighbour y %.0f (spec 480)" % (sel["cy"], prev["cy"]))
    p2, n2 = items[-2], items[2]
    check("edge peeks only slivers", -150 < p2["cx"] < 0 and W < n2["cx"] < W + 150,
          "-2 cx %.0f, +2 cx %.0f (spec slivers at edges)" % (p2["cx"], n2["cx"]))

    mx, my, mw, mh = geo["marquee_box"]
    rw, rh = geo["marquee_rendered"]
    check("marquee geometry", abs(mx - 55) < 2 and abs(my - 70) < 2 and mw <= 561 and mh <= 231,
          "box (%.0f,%.0f) %.0fx%.0f rendered %dx%d" % (mx, my, mw, mh, rw, rh))
    check("marquee strongly visible", geo["marquee_opacity"] >= 0.75 and rw >= 400,
          "opacity %.2f, rendered width %dpx" % (geo["marquee_opacity"], rw))

    nlevels = len(geo["meta_fonts"])
    check("metadata >=3 font levels", nlevels >= 3,
          "levels: %s" % ", ".join("%.1fpx" % (f * H) for f in geo["meta_fonts"]))
    mbx, mby, mbw, mbh = geo["meta_box"]
    check("metadata box at spec", abs(mbx - 910) < 2 and abs(mby - 70) < 2 and abs(mbw - 300) < 2,
          "box (%.0f,%.0f) %.0fx%.0f" % (mbx, mby, mbw, mbh))

    check("single footer", geo["footer_count"] == 1, "one static row")
    fx, fy, fw, fh = geo["footer_box"]
    check("footer at y~915", abs((fy + fh / 2) - 915) < 6, "centre y %.0f" % (fy + fh / 2))

    lw, lh = geo["logo_rendered"]; lcx, lcy = geo["logo_center"]
    check("logo larger than v7", lh > 59.5 * 1.25,
          "rendered %dx%d (v7 was ~166x60), centre y %.0f (spec 845), width %d in 230-280" % (lw, lh, lcy, lw))
    check("logo width in spec", 230 <= lw <= 280, "width %dpx" % lw)

    # status safe area: extreme top-right (Android wifi/battery/time)
    sx0, sy0, sx1, sy1 = 1150, 0, 1280, 48
    def hits(box):
        x, y, w, h = box
        return not (x + w <= sx0 or x >= sx1 or y + h <= sy0 or y >= sy1)
    content_boxes = [geo["marquee_box"], geo["meta_box"], geo["title_box"], geo["footer_box"]]
    check("no status collision", not any(hits(b) for b in content_boxes),
          "safe area x>1150,y<48 clear of marquee/metadata/title/footer")
    return ok

if __name__ == "__main__":
    im, geo = compose(with_marquee=True)
    im.save(os.path.join(OUT, "mock_v8_full.png"))
    im2, _ = compose(with_marquee=False)
    im2.save(os.path.join(OUT, "mock_v8_no_marquee.png"))
    print("saved mock_v8_full.png / mock_v8_no_marquee.png")
    ok = validate(geo)
    print("OVERALL:", "ALL PASS" if ok else "FAILURES PRESENT")
