#!/usr/bin/env python3
"""Crystal v17.7.0 gamelist mock + verification (PIL renders, never ES-DE).

PRECISION PASS mock. The VM carries NO scraped artwork, so hero /
marquee / screenshot / prev / next are rendered as CLEAN NEUTRAL SLOT
FILLS - no dashed borders, no labels, no debug treatment - because
on-device with real assets they have no visible treatment either. The
marquee slot draws ONLY the maxSize-fitted rect (the zone itself is
invisible open white). The proofs assess the UI SHELL around the slots.

6 variants cover the responsive extremes: ps2 (wide marquee, disc,
long dev name), n64 (tall marquee, cartridge), gba (long description),
longtitle (overflowing title -> native scroll), tallmarquee (very tall
marquee, tiny DS-card hero, 1-8 players), nodesc (missing description).

Font convention: ES-DE fontSize is height-relative (0.040 -> 38px at
960p) - this matches every approved proof render. The title/meta
clearance check additionally runs at width-relative sizes (51px/18px)
as a worst-case safety margin.
"""
import os, sys, json, hashlib, subprocess, math, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
sys.path.insert(0, os.path.join(REPO, "work"))
from gen_v15_assets import ROYAL, DEEP, NAVY, INKDIM, YELLOW, WHITE, SYSTEMS

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ART = os.path.join(REPO, "theme-src/crystal/art")
FONTS = os.path.join(REPO, "theme-src/crystal/fonts")
VIEWS = os.path.join(REPO, "theme-src/crystal/views.xml")
PROOFS = os.path.join(REPO, "work/proofs")
BASELINE = os.path.join(REPO, "work/baseline_media_fallbacks_v17_4.sha256")
W, H = 1280, 960
CHECK_LOG = []

def check(name, ok, detail=""):
    CHECK_LOG.append((name, ok, detail))
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""))

def px(v): return v * W
def sz(v): return v * H
def fs(v): return v * H          # fontSize is height-relative in ES-DE
def lum(p): return 0.299*p[0] + 0.587*p[1] + 0.114*p[2]
def is_yellow(p): return p[0] > 200 and p[1] > 160 and p[2] < 110

def parse_view(xml, name):
    start = xml.index(f'<view name="{name}">')
    return xml[start:xml.index("</view>", start)]

def el_box(view, ename):
    tag = ename.split()[0]
    start = view.index("<" + ename)
    return view[start:view.index("</" + tag + ">", start)]

def el_val(blk, tag):
    return blk.split(f"<{tag}>")[1].split(f"</{tag}>")[0]

def el_geom(blk):
    g = {}
    for t in ("pos", "size", "origin", "zIndex", "maxSize"):
        if f"<{t}>" in blk:
            g[t] = el_val(blk, t)
    return g

def geom_dict(view):
    d = {}
    for m in re.finditer(r'<(image|text|datetime|rating|carousel) name="([^"]+)"', view):
        blk = el_box(view, f"{m.group(1)} name=\"{m.group(2)}\"")
        d[m.group(2)] = el_geom(blk)
    return d

# ---------------- clean neutral slots (no borders, no text) -------------
SLOT_PAGE = (233, 237, 244, 255)   # on the white editorial page
SLOT_STAGE = (226, 231, 240, 255)  # on the blue hero stage

def fit_rect(zone, aspect):
    """maxSize fit: largest rect of `aspect` (w/h) inside zone, centred."""
    zx0, zy0, zx1, zy1 = zone
    zw, zh = zx1 - zx0, zy1 - zy0
    fw = min(zw, zh * aspect)
    fh = fw / aspect
    cx, cy = (zx0 + zx1) / 2, (zy0 + zy1) / 2
    return (cx - fw / 2, cy - fh / 2, cx + fw / 2, cy + fh / 2)

def hero_footprint(kind):
    if kind == "disc":
        return (900 - 240, 430 - 240, 900 + 240, 430 + 240)
    if kind == "cartridge":
        return (900 - 190, 430 - 250, 900 + 190, 430 + 250)
    return (900 - 150, 430 - 170, 900 + 150, 430 + 170)  # dscard

def fill_box(layer, box, color):
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    ImageDraw.Draw(layer, "RGBA").rectangle([(x0, y0), (x1, y1)], fill=color)

def wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if font.getlength(t) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

# ------------------------------- render ---------------------------------
def render(v):
    xml = open(VIEWS, encoding="utf-8").read()
    view = parse_view(xml, "gamelist")
    base = Image.open(os.path.join(ART, "gamelist_generic_bg.png")).convert("RGBA").resize((W, H))
    grad = Image.open(os.path.join(ART, "lib_bottom_gradient.png")).convert("RGBA")
    g = el_box(view, 'image name="libBottomGradient"')
    gx, gy = [float(x) for x in el_val(g, "pos").split()]
    gw, gh = [float(x) for x in el_val(g, "size").split()]
    base.alpha_composite(grad.resize((int(px(gw)), int(sz(gh)))), (int(px(gx)), int(sz(gy))))
    base.alpha_composite(Image.open(os.path.join(ART, "lib_panel_main.png")).convert("RGBA"), (6, 10))
    base.alpha_composite(Image.open(os.path.join(ART, "rails", f"{v['system']}.png")).convert("RGBA"), (486, 24))

    # marquee: fitted rect only - the zone is invisible
    m = el_box(view, 'image name="libMarquee"')
    mx, my = [float(x) for x in el_val(m, "pos").split()]
    mw, mh = [float(x) for x in el_val(m, "maxSize").split()]
    zone = (px(mx), sz(my) - sz(mh) / 2, px(mx) + px(mw), sz(my) + sz(mh) / 2)
    mrect = fit_rect(zone, v["marquee_aspect"])
    fill_box(base, mrect, SLOT_PAGE)

    # left-column text at real XML geometry (height-relative fonts)
    d = ImageDraw.Draw(base, "RGBA")
    f_desc = ImageFont.truetype(REG, int(round(fs(0.0175))))
    y = 312
    for line in wrap(v["desc"], f_desc, px(0.2984375))[:6]:
        d.text((48, y), line, font=f_desc, fill=INKDIM + (255,))
        y += 26
    d.text((48, 468), v["year"], font=ImageFont.truetype(BOLD, int(round(fs(0.050)))),
           fill=NAVY + (255,))
    # rating stars in the XML box (296,470 140x28)
    for i in range(5):
        cx, cy = 296 + 14 + i * 28, 470 + 14
        pts = []
        for k in range(10):
            r = 11 if k % 2 == 0 else 4.6
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, fill=ROYAL + (255,) if i < v["stars"] else (255, 255, 255, 140),
                  outline=NAVY + (255,))
    d.text((48, 566), v["genre"].upper(), font=ImageFont.truetype(BOLD, int(round(fs(0.022)))),
           fill=NAVY + (255,))
    f_micro = ImageFont.truetype(REG, int(round(fs(0.015))))
    d.text((48, 626), v["players"].upper(), font=f_micro, fill=INKDIM + (255,))
    d.text((240, 626), v["dev"].upper(), font=f_micro, fill=INKDIM + (255,))

    # screenshot slot: fixed box at the XML position
    s = el_box(view, 'image name="libScreenshot"')
    sx, sy = [float(x) for x in el_val(s, "pos").split()]
    sw, sh = [float(x) for x in el_val(s, "size").split()]
    sbox = (px(sx), sz(sy), px(sx) + px(sw), sz(sy) + sz(sh))
    fill_box(base, sbox, SLOT_PAGE)

    # hero stage: plane, wash, glow (0.28), shadow, hero slot, prev/next
    pl = el_box(view, 'image name="libPlaneHero"')
    px0, py0 = [float(x) for x in el_val(pl, "pos").split()]
    pw, ph = [float(x) for x in el_val(pl, "size").split()]
    base.alpha_composite(Image.open(os.path.join(ART, "lib_plane_hero.png")).convert("RGBA"),
                         (int(px(px0)), int(sz(py0))))
    hw = el_box(view, 'image name="libHeroWash"')
    hx, hy = [float(x) for x in el_val(hw, "pos").split()]
    hww, hwh = [float(x) for x in el_val(hw, "size").split()]
    base.alpha_composite(Image.open(os.path.join(ART, "lib_hero_wash.png")).convert("RGBA")
                         .resize((int(px(hww)), int(sz(hwh)))),
                         (int(px(hx) - px(hww) / 2), int(sz(hy) - sz(hwh) / 2)))
    gl = el_box(view, 'image name="libSelectedGlowBlue"')
    gx2, gy2 = [float(x) for x in el_val(gl, "pos").split()]
    gw2, gh2 = [float(x) for x in el_val(gl, "size").split()]
    glow = Image.open(os.path.join(ART, "lib_glow_blue.png")).convert("RGBA") \
        .resize((int(px(gw2)), int(sz(gh2))))
    glow.putalpha(glow.split()[3].point(lambda a: int(a * 0.28)))
    base.alpha_composite(glow, (int(px(gx2) - px(gw2) / 2), int(sz(gy2) - sz(gh2) / 2)))
    sh2 = el_box(view, 'image name="libSelectedShadow"')
    qx, qy = [float(x) for x in el_val(sh2, "pos").split()]
    qw, qh = [float(x) for x in el_val(sh2, "size").split()]
    shadow = Image.open(os.path.join(ART, "lib_shadow_soft.png")).convert("RGBA") \
        .resize((int(px(qw)), int(sz(qh))))
    shadow.putalpha(shadow.split()[3].point(lambda a: int(a * 0.9)))
    base.alpha_composite(shadow, (int(px(qx) - px(qw) / 2), int(sz(qy) - sz(qh) / 2)))

    hb = hero_footprint(v["hero"])
    fill_box(base, hb, SLOT_STAGE)
    # prev/next: same media class, 240px bounding, 45% opacity, cropped
    dim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for cy in (-50, 910):
        x0, y0, x1, y1 = hb
        bw, bh = x1 - x0, y1 - y0
        sc = 240 / max(bw, bh)
        nw, nh = bw * sc / 2, bh * sc / 2
        fill_box(dim, (900 - nw, cy - nh, 900 + nw, cy + nh), SLOT_STAGE)
    dim.putalpha(dim.split()[3].point(lambda a: int(a * 0.45)))
    base.alpha_composite(dim)

    # foreground shards at real XML geometry
    for ename in ('image name="libShardPrev"', 'image name="libShardNext"'):
        b = el_box(view, ename)
        bx, by = [float(x) for x in el_val(b, "pos").split()]
        bw2, bh2 = [float(x) for x in el_val(b, "size").split()]
        aname = "lib_shard_prev.png" if "Prev" in ename else "lib_shard_next.png"
        sh = Image.open(os.path.join(ART, aname)).convert("RGBA").resize((int(px(bw2)), int(sz(bh2))))
        base.alpha_composite(sh, (int(px(bx)), int(sz(by))))

    # title block: rule asset, title (scroll-pos-0 if overflowing), rail
    rule = Image.open(os.path.join(ART, "lib_title_rule.png")).convert("RGBA")
    base.alpha_composite(rule, (int(900 - rule.width / 2), 711))
    t = el_box(view, 'text name="libGameName"')
    tx, ty = [float(x) for x in el_val(t, "pos").split()]
    tw, th = [float(x) for x in el_val(t, "size").split()]
    tbox = (px(tx) - px(tw) / 2, sz(ty) - sz(th) / 2, px(tx) + px(tw) / 2, sz(ty) + sz(th) / 2)
    f_title = ImageFont.truetype(BOLD, int(round(fs(0.040))))
    title = v["title"].upper()
    if f_title.getlength(title) <= px(tw):
        d.text((px(tx), sz(ty)), title, font=f_title, fill=(255, 255, 255, 255),
               anchor="mm")
    else:
        # overflowing: engine scrolls; rest position shows the head,
        # left-aligned and clipped to the box
        tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(tl, "RGBA").text((tbox[0], sz(ty)), title, font=f_title,
                                        fill=(255, 255, 255, 255), anchor="lm")
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).rectangle([int(v) for v in tbox], fill=255)
        base.alpha_composite(Image.composite(tl, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    f_rail = ImageFont.truetype(REG, int(round(fs(0.0145))))
    rail = [("libMetaGenre", v["genre"].upper()), ("libMetaSep1", "\u2022"),
            ("libMetaYear", v["year"]), ("libMetaSep2", "\u2022"),
            ("libMetaDev", v["dev"].upper()), ("libMetaSep3", "\u2022"),
            ("libMetaPlayers", v["players"].upper())]
    for ename, txt in rail:
        tag = "datetime" if "Year" in ename else "text"
        b = el_box(view, f'{tag} name="{ename}"')
        bx, by = [float(x) for x in el_val(b, "pos").split()]
        d.text((px(bx), sz(by)), txt, font=f_rail, fill=(255, 255, 255, 140), anchor="mm")
    f_foot = ImageFont.truetype(REG, int(round(fs(0.0135))))
    d.text((640, 915), "A PLAY \u2022 B BACK", font=f_foot, fill=(255, 255, 255, 128), anchor="mm")
    return base.convert("RGB"), {"mrect": mrect, "zone": zone, "sbox": sbox,
                                 "tbox": tbox, "hero": hb}

# ------------------------------- variants -------------------------------
VARIANTS = {
    "ps2": dict(system="ps2", title="GRAN TURISMO 4", genre="RACING", year="2004",
                 dev="POLYPHONY DIGITAL", players="1\u20132 PLAYERS", stars=5,
                 hero="disc", marquee_aspect=16 / 5,
                 desc="The definitive driving simulator: over 700 cars and 50 tracks. Polyphony Digital's obsessive attention to vehicle dynamics, now sharper than ever."),
    "n64": dict(system="n64", title="SUPER MARIO 64", genre="PLATFORMER", year="1996",
                 dev="NINTENDO", players="1 PLAYER", stars=5,
                 hero="cartridge", marquee_aspect=1 / 1.5,
                 desc="Mario's groundbreaking leap into 3D. Explore 15 courses inside Princess Peach's castle, collecting 120 Power Stars to confront Bowser."),
    "gba": dict(system="gba", title="MARIO GOLF: ADVANCE TOUR", genre="SPORTS", year="2004",
                 dev="CAMELOT", players="1\u20134 PLAYERS", stars=4,
                 hero="cartridge", marquee_aspect=3 / 1,
                 desc="Camelot's beloved handheld golf RPG returns. Train your rookie from a raw beginner into a championship contender across varied courses, mastering topspin, backspin and the psychological duel of match play against seasoned rivals."),
    "longtitle": dict(system="n3ds", title="THE LEGEND OF ZELDA: OCARINA OF TIME 3D",
                       genre="ACTION-ADVENTURE", year="2011", dev="NINTENDO EAD",
                       players="1 PLAYER", stars=5, hero="disc", marquee_aspect=2 / 1,
                       desc="Link sails the Great Sea in search of his kidnapped sister. A cel-shaded epic of exploration, dungeon-crawling and unforgettable music."),
    "tallmarquee": dict(system="gb", title="TETRIS", genre="PUZZLE", year="1989",
                         dev="NINTENDO", players="1\u20138 PLAYERS", stars=4,
                         hero="dscard", marquee_aspect=1 / 2,
                         desc="The timeless falling-block puzzler. Stack, clear lines, survive."),
    "nodesc": dict(system="genesis", title="PONG", genre="SPORTS", year="1972",
                    dev="ATARI", players="1\u20132 PLAYERS", stars=3,
                    hero="cartridge", marquee_aspect=16 / 5, desc=""),
}

# ------------------------------- checks ---------------------------------
def check_macro_lock():
    head = subprocess.run(["git", "-C", REPO, "show", "HEAD:theme-src/crystal/views.xml"],
                          capture_output=True, text=True).stdout
    a, b = geom_dict(parse_view(head, "gamelist")), geom_dict(parse_view(open(VIEWS).read(), "gamelist"))
    whitelist = {"libMarquee": {"pos", "origin"},
                 "libGameName": {"size"},
                 "libMetaGenre": {"pos", "size"}, "libMetaSep1": {"pos"},
                 "libMetaYear": {"pos", "size"}, "libMetaSep2": {"pos"},
                 "libMetaDev": {"pos", "size"}, "libMetaSep3": {"pos"},
                 "libMetaPlayers": {"pos", "size"},
                 "libScreenshot": {"pos"},
                 "libHeroWash": set()}
    ok, detail = True, ""
    if set(a) | {"libHeroWash"} != set(b):
        ok, detail = False, "element set changed"
    else:
        for k in a:
            wa = whitelist.get(k, set())
            for f, val in a[k].items():
                if f not in wa and b[k].get(f) != val:
                    ok, detail = False, f"{k}.{f}: {val} -> {b[k].get(f)}"
    check("macro-lock vs v17.6.0 (whitelisted precision moves only)", ok,
          detail or f"{len(a)}+1 elements")

def check_marquee_xml():
    xml = open(VIEWS).read()
    m = el_box(parse_view(xml, "gamelist"), 'image name="libMarquee"')
    check("marquee: maxSize invisible region, vertically centred",
          el_val(m, "origin") == "0 0.5" and el_val(m, "pos") == "0.01875 0.1770833"
          and el_val(m, "maxSize") == "0.33125 0.2625"
          and el_val(m, "imageType") == "marquee",
          f"pos={el_val(m,'pos')} origin={el_val(m,'origin')}")

def check_title_xml():
    xml = open(VIEWS).read()
    t = el_box(parse_view(xml, "gamelist"), 'text name="libGameName"')
    need = {"container": "true", "containerType": "scroll",
            "containerScrollSpeed": "36", "containerScrollGap": "90",
            "containerStartDelay": "2.0", "containerResetDelay": "2.5"}
    ok = all(f"<{k}>{v}</{k}>" in t for k, v in need.items())
    check("title: native scroll container engaged (36px/s, 2.0s/2.5s delays)",
          ok and el_val(t, "fontSize") == "0.040" and el_val(t, "size") == "0.58 0.0375")

def check_rail_xml():
    xml = open(VIEWS).read()
    g = parse_view(xml, "gamelist")
    names = ["libMetaGenre", "libMetaSep1", "libMetaYear", "libMetaSep2",
             "libMetaDev", "libMetaSep3", "libMetaPlayers"]
    spans = []
    ok = True
    for n in names:
        tag = "datetime" if n == "libMetaYear" else "text"
        b = el_box(g, f'{tag} name="{n}"')
        x = float(el_val(b, "pos").split()[0])
        w = float(el_val(b, "size").split()[0])
        spans.append((x - w / 2, x + w / 2))
    spans.sort()
    for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
        if b0 < a1 - 1e-9:
            ok = False
    inside = spans[0][0] >= 0.413 and spans[-1][1] <= 0.993
    check("rail: 7 slots no-overlap, inside hero identity width (0.413-0.993)",
          ok and inside, f"span={spans[0][0]:.3f}-{spans[-1][1]:.3f}")

def check_screenshot_xml():
    xml = open(VIEWS).read()
    s = el_box(parse_view(xml, "gamelist"), 'image name="libScreenshot"')
    check("screenshot x aligned with text column (x=48)",
          el_val(s, "pos") == "0.0375 0.7291667", el_val(s, "pos"))

def check_typography():
    xml = open(VIEWS).read()
    g = re.sub(r"<!--.*?-->", "", parse_view(xml, "gamelist"), flags=re.S)
    check("no PermanentMarker anywhere in gamelist XML/fonts",
          "PermanentMarker" not in g
          and not os.path.exists(os.path.join(FONTS, "PermanentMarker-Regular.ttf")))

def check_fallbacks():
    base = {l.split()[1]: l.split()[0] for l in open(BASELINE) if l.strip()}
    bad = [n for n, h in base.items()
           if hashlib.sha256(open(os.path.join(REPO, n), "rb").read()).hexdigest() != h]
    check("all 22 media_fallbacks byte-identical to frozen baseline", not bad,
          f"changed={bad}" if bad else f"{len(base)} files")

def check_plane():
    im = Image.open(os.path.join(ART, "lib_plane_hero.png")).convert("RGBA")
    yel = sum(1 for q in im.getdata()
              if q[0] > 200 and q[1] > 170 and q[2] < 110 and q[3] > 40)
    check("hero plane: yellow leading edge deleted", yel == 0, f"yellow_px={yel}")

def check_wash():
    p = os.path.join(ART, "lib_hero_wash.png")
    im = Image.open(p).convert("RGBA")
    alphas = [q[3] for q in im.getdata()]
    check("hero wash: exists, extremely subtle (peak alpha <= 30)",
          os.path.isfile(p) and max(alphas) <= 30 and im.size == (760, 760),
          f"peak_alpha={max(alphas)}")
    xml = open(VIEWS).read()
    hw = el_box(parse_view(xml, "gamelist"), 'image name="libHeroWash"')
    check("hero wash element: centred (900,430), z46, no container/ring",
          el_val(hw, "pos") == "0.703125 0.4479167"
          and el_val(hw, "size") == "0.59375 0.7916667"
          and el_val(hw, "zIndex") == "46")

def check_rails():
    n = sum(1 for s, _ in SYSTEMS
            if os.path.exists(os.path.join(ART, "rails", f"{s}.png")))
    check("all 21 rails regenerated", n == 21, str(n))
    head = subprocess.run(["git", "-C", REPO,
                           "show", "HEAD:theme-src/crystal/art/rails/ps2.png"],
                          capture_output=True).stdout
    src7 = open(os.path.join(REPO, "work/gen_v17_7_assets.py")).read()
    src6 = open(os.path.join(REPO, "work/gen_v17_6_assets.py")).read()
    check("spine dotgrid quieter: 32px/alpha4 -> 40px/alpha3 in generator",
          "dotgrid(img, (6, 30, 54, 882), alpha=3, spacing=40)" in src7
          and "dotgrid(img, (6, 30, 54, 882), alpha=4, spacing=32)" in src6)
    # sanity: the regenerated rail really differs in the dot band
    import io
    old = Image.open(io.BytesIO(head)).convert("RGB")
    new = Image.open(os.path.join(ART, "rails/ps2.png")).convert("RGB")
    diff = sum(1 for x in range(6, 54, 3) for y in range(30, 882, 3)
               if abs(lum(old.getpixel((x, y))) - lum(new.getpixel((x, y)))) > 2)
    check("rails regenerated (pixel delta vs v17.6)", diff > 50, f"delta_px={diff}")
    prm = json.load(open(os.path.join(REPO, "work/rail_params_v17_7.json")))
    check("rails: optical lift + increased logo presence recorded",
          all(v.get("optical_lift") == 6 for v in prm.values()) and len(prm) == 21)

def check_motion():
    xml = open(VIEWS).read()
    g = re.sub(r"<!--.*?-->", "", parse_view(xml, "gamelist"), flags=re.S)
    i = g.index('<carousel name="gameCarousel"')
    check("gameCarousel itemTransitions=animate present and engaged",
          "itemTransitions" in g[i:i + 1200] and "animate" in g[i:i + 1200])
    check("no unsupported motion constructs",
          not any(b in g for b in ("<storyboard", "<animation ", "crossfade", "duration")))

def check_hygiene():
    head = subprocess.run(["git", "-C", REPO, "show", "HEAD:theme-src/crystal/views.xml"],
                          capture_output=True, text=True).stdout
    xml = open(VIEWS).read()
    check("system view byte-identical",
          parse_view(head, "system") == parse_view(xml, "system"))
    for f in ("gamelist_generic_bg.png", "lib_shadow_soft.png", "lib_glow_blue.png",
              "lib_shard_prev.png", "lib_shard_next.png", "lib_title_rule.png",
              "star_filled.png"):
        h1 = subprocess.run(["git", "-C", REPO, "show", f"HEAD:theme-src/crystal/art/{f}"],
                            capture_output=True).stdout
        h2 = open(os.path.join(ART, f), "rb").read()
        if hashlib.sha256(h1).hexdigest() != hashlib.sha256(h2).hexdigest():
            check(f"asset unchanged: {f}", False)
            return
    check("shell assets unchanged (bg/shadow/glow/shards/rule/star)", True)

def check_proof(name, v, img, info):
    mrect, zone = info["mrect"], info["zone"]
    # marquee fit: inside zone, aspect preserved, vertically centred
    zx0, zy0, zx1, zy1 = zone
    x0, y0, x1, y1 = mrect
    ar = (x1 - x0) / (y1 - y0)
    check(f"[{name}] marquee maxSize-fit: aspect preserved, centred, in-zone",
          abs(ar - v["marquee_aspect"]) / v["marquee_aspect"] < 0.02
          and x0 >= zx0 - 1 and x1 <= zx1 + 1 and y0 >= zy0 - 1 and y1 <= zy1 + 1
          and abs((y0 + y1) / 2 - (zy0 + zy1) / 2) < 2,
          f"aspect={ar:.2f} rect={[int(q) for q in mrect]}")
    # zone outside the fitted rect is clean: no visible container. The
    # "NOW SHOWING" kicker is baked page furniture (y<60), excluded.
    pxa = img.load()
    outside = [pxa[x, y] for x in range(int(zx0), int(zx1), 7)
               for y in range(max(int(zy0), 60), int(zy1), 7)
               if not (x0 <= x <= x1 and y0 <= y <= y1)]
    clean = sum(1 for q in outside if lum(q) > 235)
    check(f"[{name}] marquee zone: no visible container around asset",
          len(outside) > 50 and clean / len(outside) > 0.97,
          f"clean={clean}/{len(outside)}")
    # slot interiors uniform: no borders, no text, no debug treatment
    for label, box in (("marquee", mrect), ("screenshot", info["sbox"]), ("hero", info["hero"])):
        ix0, iy0, ix1, iy1 = [int(q) + 4 for q in box[:2]] + [int(q) - 4 for q in box[2:]]
        vals = [lum(pxa[x, y]) for x in range(ix0, ix1, 5) for y in range(iy0, iy1, 5)]
        mean = sum(vals) / len(vals)
        var = sum((q - mean) ** 2 for q in vals) / len(vals)
        check(f"[{name}] {label} slot: flat neutral fill, no border/text",
              var < 4, f"var={var:.1f}")
    # screenshot aligned with text column
    check(f"[{name}] screenshot x == text column x (48)",
          abs(info["sbox"][0] - 48) < 1, f"x={info['sbox'][0]:.0f}")
    # description behaviour
    desc_box = (48, 312, 48 + px(0.2984375), 312 + sz(0.1125))
    region = img.crop([int(q) for q in desc_box])
    ink = sum(1 for q in region.getdata() if lum(q) < 150)
    if v["desc"]:
        check(f"[{name}] description rendered, inside its box", ink > 200, f"ink={ink}")
    else:
        check(f"[{name}] missing description: clean collapse, no hole", ink < 40, f"ink={ink}")
    # title: clean above the title-rule/title box (no stray glyphs)
    band = img.crop((550, 688, 1250, 714))
    stray = sum(1 for q in band.getdata() if lum(q) > 210)
    check(f"[{name}] above-title band: no stray glyphs", stray < 400, f"bright={stray}")
    # rail strings fit their slots (height-relative fonts)
    xml = open(VIEWS).read()
    g = parse_view(xml, "gamelist")
    f_rail = ImageFont.truetype(REG, int(round(fs(0.0145))))
    fit_ok, worst = True, ""
    for ename, txt in (("libMetaGenre", v["genre"].upper()), ("libMetaYear", v["year"]),
                       ("libMetaDev", v["dev"].upper()), ("libMetaPlayers", v["players"].upper())):
        tag = "datetime" if "Year" in ename else "text"
        b = el_box(g, f'{tag} name="{ename}"')
        sw = float(el_val(b, "size").split()[0]) * W
        tw = f_rail.getlength(txt)
        if tw > sw:
            fit_ok, worst = False, f"{ename} {tw:.0f}>{sw:.0f}"
    check(f"[{name}] rail values fit their slots (no overlap/overflow)", fit_ok, worst or "all fit")
    # hero dominant; prev/next smaller, dimmer (45%), cropped by screen edge
    prev_hit = sum(1 for x in range(780, 1020, 6) for y in range(0, 60, 6)
                   if 90 < lum(pxa[x, y]) < 210)
    next_hit = sum(1 for x in range(780, 1020, 6) for y in range(900, 960, 6)
                   if 90 < lum(pxa[x, y]) < 210)
    check(f"[{name}] prev/next read as cropped incoming objects",
          prev_hit > 20 and next_hit > 20, f"prev={prev_hit} next={next_hit}")
    # yellow budget
    yel = sum(1 for q in img.getdata() if is_yellow(q))
    share = yel / (W * H) * 100
    check(f"[{name}] yellow pixel-share <= 5%", share <= 5.0, f"{share:.2f}%")

def check_clearance_worst_case():
    # worst case: width-relative fonts (51px title / 18px rail)
    xml = open(VIEWS).read()
    g = parse_view(xml, "gamelist")
    tb = el_box(g, 'text name="libGameName"')
    tcy = float(el_val(tb, "pos").split()[1]) * H
    mb = el_box(g, 'text name="libMetaGenre"')
    mcy = float(el_val(mb, "pos").split()[1]) * H
    c = Image.new("RGB", (900, 220), "white")
    d = ImageDraw.Draw(c)
    d.text((450, 90), "GRAN TURISMO 4", font=ImageFont.truetype(BOLD, 51), fill="black", anchor="mm")
    d.text((450, 90 + (mcy - tcy)), "RACING \u2022 2004 \u2022 TEST \u2022 1-2",
           font=ImageFont.truetype(REG, 18), fill="red", anchor="mm")
    pxx = c.load()
    t_rows = [y for y in range(220) for x in range(900) if pxx[x, y] == (0, 0, 0)]
    m_rows = [y for y in range(220) for x in range(900) if pxx[x, y][0] > 200 and pxx[x, y][1] < 100]
    gap = min(m_rows) - max(t_rows)
    check("title/meta clearance at worst-case (width-relative) sizes", gap >= 0, f"gap={gap}px")

if __name__ == "__main__":
    os.makedirs(PROOFS, exist_ok=True)
    check_macro_lock(); check_marquee_xml(); check_title_xml(); check_rail_xml()
    check_screenshot_xml(); check_typography(); check_fallbacks(); check_plane()
    check_wash(); check_rails(); check_motion(); check_hygiene()
    check_clearance_worst_case()
    for name, v in VARIANTS.items():
        img, info = render(v)
        p = os.path.join(PROOFS, f"mock_v17_7_{name}.png")
        img.save(p)
        print("saved", p)
        check_proof(name, v, img, info)
    fails = sum(1 for _, ok, _ in CHECK_LOG if not ok)
    print(f"\n{'ALL CHECKS PASS' if fails == 0 else str(fails) + ' CHECKS FAILED'} "
          f"({len(CHECK_LOG)} checks)")
    sys.exit(1 if fails else 0)
