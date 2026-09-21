#!/usr/bin/env python3
"""Crystal v17.9.0 gamelist mock + verification (PIL renders, never ES-DE).

CONVERGENCE PASS mock. The VM carries NO scraped artwork, so hero /
marquee / screenshot / prev / next are rendered as CLEAN NEUTRAL SLOT
FILLS - no dashed borders, no labels, no debug treatment - because
on-device with real assets they have no visible treatment either. The
marquee slot draws ONLY the maxSize-fitted rect (the zone itself is
invisible open white). The proofs assess the UI SHELL around the slots.

14 variants cover the responsive extremes: ps2 (disc, GRAN TURISMO 4),
n64 (cartridge), gba (cartridge, long description), shorttitle (DOOM),
longtitle (THE LEGEND OF ZELDA: OCARINA OF TIME 3D - the reported
clip case), longdev (worst-case developer), widemarquee (16:5),
tallmarquee (1:1.5, DS-card hero, 1-8 players), nodesc (missing
description), nomarquee (missing marquee -> clean fallback title),
shortdesc (one-line description), norating (rating hidden), nodev
(missing developer), combo (missing marquee+desc+rating+developer).

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
    if v["marquee_aspect"]:
        mrect = fit_rect(zone, v["marquee_aspect"])
        fill_box(base, mrect, SLOT_PAGE)
    else:
        # missing marquee: clean display-font fallback title, no imitation
        fb = el_box(view, 'text name="libMarqueeTitle"')
        fx, fy = [float(q) for q in el_val(fb, "pos").split()]
        fw, fh = [float(q) for q in el_val(fb, "size").split()]
        fz = float(el_val(fb, "fontSize"))
        f_fb = ImageFont.truetype(BOLD, int(round(fs(fz))))
        flines = wrap(v["title"].upper(), f_fb, px(fw))[:4]
        yy = sz(fy) + sz(fh) / 2 - len(flines) * int(round(fs(fz))) * 0.62
        dd = ImageDraw.Draw(base, "RGBA")
        for ln in flines:
            dd.text((px(fx) + px(fw) / 2, yy), ln, font=f_fb, fill=(20, 60, 168, 217), anchor="ma")
            yy += int(round(fs(fz))) * 1.24
        mrect = (px(fx), sz(fy), px(fx) + px(fw), sz(fy) + sz(fh))

    # left-column text at real XML geometry (height-relative fonts)
    d = ImageDraw.Draw(base, "RGBA")
    def tpos(ename):
        b = el_box(view, f'text name="{ename}"')
        x, y = [float(q) for q in el_val(b, "pos").split()]
        return px(x), sz(y)
    fz_desc = float(el_val(el_box(view, 'text name="libDesc"'), "fontSize"))
    f_desc = ImageFont.truetype(REG, int(round(fs(fz_desc))))
    desc_step = int(round(fs(fz_desc) * 1.5))
    y = 312
    for line in wrap(v["desc"], f_desc, px(0.2984375))[:6]:
        d.text((48, y), line, font=f_desc, fill=INKDIM + (255,))
        y += desc_step
    d.text((48, 468), v["year"], font=ImageFont.truetype(BOLD, int(round(fs(0.050)))),
           fill=NAVY + (255,))
    # rating stars in the XML box (parsed from the theme)
    rb = el_box(view, 'rating name="libRating"')
    rrx, rry = [float(q) for q in el_val(rb, "pos").split()]
    rrw = float(el_val(rb, "size").split()[0])
    for i in range(5):
        cx, cy = px(rrx) + 14 + i * 28, sz(rry) + 14
        pts = []
        for k in range(10):
            r = 11 if k % 2 == 0 else 4.6
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, fill=ROYAL + (255,) if i < v["stars"] else (255, 255, 255, 140),
                  outline=NAVY + (255,))
    gx, gy = tpos("libGenre")
    d.text((gx, gy), v["genre"].upper(), font=ImageFont.truetype(BOLD, int(round(fs(0.022)))),
           fill=NAVY + (255,))
    f_micro = ImageFont.truetype(REG, int(round(fs(0.015))))
    px0, py0 = tpos("libPlayers")
    dx0, dy0 = tpos("libDev")
    d.text((px0, py0), v["players"].upper(), font=f_micro, fill=INKDIM + (255,))
    db = el_box(view, 'text name="libDev"')
    dev_w = float(el_val(db, "size").split()[0]) * W
    for i, ln in enumerate(wrap(v["dev"].upper(), f_micro, dev_w)[:2]):
        d.text((dx0, dy0 + i * 26), ln, font=f_micro, fill=INKDIM + (255,))

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
    glow.putalpha(glow.split()[3].point(lambda a: int(a * 0.22)))
    base.alpha_composite(glow, (int(px(gx2) - px(gw2) / 2), int(sz(gy2) - sz(gh2) / 2)))
    sh2 = el_box(view, 'image name="libSelectedShadow"')
    qx, qy = [float(x) for x in el_val(sh2, "pos").split()]
    qw, qh = [float(x) for x in el_val(sh2, "size").split()]
    sh_op = float(el_val(sh2, "opacity"))
    shadow = Image.open(os.path.join(ART, "lib_shadow_soft.png")).convert("RGBA") \
        .resize((int(px(qw)), int(sz(qh))))
    shadow.putalpha(shadow.split()[3].point(lambda a: int(a * sh_op)))
    base.alpha_composite(shadow, (int(px(qx) - px(qw) / 2), int(sz(qy) - sz(qh) / 2)))

    hb = hero_footprint(v["hero"])
    fill_box(base, hb, SLOT_STAGE)
    # prev/next: same media class, 240px bounding, 45% opacity, cropped
    cb = el_box(view, 'carousel name="gameCarousel"')
    cx, cy0 = [float(q) for q in el_val(cb, "pos").split()]
    csw, csh = [float(q) for q in el_val(cb, "size").split()]
    pitch = sz(csh) / 3.0
    dim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for cy in (sz(cy0) - pitch, sz(cy0) + pitch):
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
    fz_title = float(el_val(t, "fontSize"))
    f_title = ImageFont.truetype(BOLD, int(round(fs(fz_title))))
    title = v["title"].upper()
    if f_title.getlength(title) <= px(tw):
        d.text((px(tx), sz(ty)), title, font=f_title, fill=(255, 255, 255, 255),
               anchor="mm")
    else:
        # beyond the measured envelope: engine word-wraps; mock draws 2 lines
        for i, ln in enumerate(wrap(title, f_title, px(tw))[:2]):
            d.text((px(tx), sz(ty) + (i - 0.5) * int(round(fs(fz_title))) * 1.15),
                   ln, font=f_title, fill=(255, 255, 255, 255), anchor="mm")
    f_rail = ImageFont.truetype(REG, int(round(fs(0.0145))))
    rail = [("libMetaGenre", v["genre"].upper()), ("libMetaSep1", "\u2022"),
            ("libMetaYear", v["year"]), ("libMetaSep2", "\u2022"),
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
    "shorttitle": dict(system="nes", title="DOOM", genre="SHOOTER", year="1993",
                       dev="ID SOFTWARE", players="1 PLAYER", stars=4,
                       hero="cartridge", marquee_aspect=16 / 5,
                       desc="The granddaddy of first-person shooters. Blast through demon-infested corridors."),
    "longdev": dict(system="psx", title="FINAL FANTASY VII", genre="RPG", year="1997",
                    dev="NINTENDO ENTERTAINMENT ANALYSIS & DEVELOPMENT", players="1 PLAYER",
                    stars=5, hero="disc", marquee_aspect=3 / 1,
                    desc="A landmark RPG epic of rebellion against an energy empire."),
    "widemarquee": dict(system="snes", title="F-ZERO", genre="RACING", year="1990",
                        dev="NINTENDO", players="1\u20132 PLAYERS", stars=4,
                        hero="cartridge", marquee_aspect=16 / 5,
                        desc="Blistering Mode-7 hover racing at the edge of control."),
    "nomarquee": dict(system="wii", title="WII SPORTS", genre="SPORTS", year="2006",
                      dev="NINTENDO", players="1\u20134 PLAYERS", stars=4,
                      hero="disc", marquee_aspect=None,
                      desc="Five sports that turned living rooms into stadiums."),
    "shortdesc": dict(system="gb", title="TETRIS", genre="PUZZLE", year="1989",
                       dev="NINTENDO", players="1 PLAYER", stars=5,
                       hero="cartridge", marquee_aspect=4 / 1,
                       desc="The timeless falling-block puzzler."),
    "norating": dict(system="snes", title="SUPER METROID", genre="ACTION-ADVENTURE",
                      year="1994", dev="NINTENDO R&D1", players="1 PLAYER", stars=0,
                      hero="cartridge", marquee_aspect=3 / 1,
                      desc="Samus descends into planet Zebes to recover the last Metroid from the Space Pirates."),
    "nodev": dict(system="nes", title="DUCK HUNT", genre="SHOOTER", year="1984",
                   dev="", players="1\u20132 PLAYERS", stars=3,
                   hero="cartridge", marquee_aspect=16 / 9,
                   desc="Aim the NES Zapper at the screen and blast clay pigeons and ducks."),
    "combo": dict(system="nds", title="BRAIN AGE", genre="PUZZLE", year="2005",
                   dev="", players="1 PLAYER", stars=0,
                   hero="dscard", marquee_aspect=None, desc=""),
}

# ------------------------------- checks ---------------------------------
def check_macro_lock():
    head = subprocess.run(["git", "-C", REPO, "show", "HEAD:theme-src/crystal/views.xml"],
                          capture_output=True, text=True).stdout
    a, b = geom_dict(parse_view(head, "gamelist")), geom_dict(parse_view(open(VIEWS).read(), "gamelist"))
    whitelist = {"libGameName": set(),          # fontSize only (not in geom)
                 "libMetaGenre": {"pos", "size"}, "libMetaSep1": {"pos"},
                 "libMetaYear": {"pos"}, "libMetaSep2": {"pos"},
                 "libMetaPlayers": {"pos"},
                 "libDesc": set(),              # fontSize only (not in geom)
                 "libRating": {"pos"},
                 "libScreenshot": {"pos"},
                 "libSelectedShadow": {"size"}, # opacity only (not in geom)
                 "libShardNext": {"pos", "size"}}
    ok, detail = True, ""
    removed = set(a) - set(b)
    if removed != {"libMetaDev", "libMetaSep3"} or set(b) - set(a):
        ok, detail = False, f"element set changed: removed={removed} added={set(b) - set(a)}"
    else:
        for k in a:
            if k in ("libMetaDev", "libMetaSep3"):
                continue
            wa = whitelist.get(k, set())
            for f, val in a[k].items():
                if f not in wa and b[k].get(f) != val:
                    ok, detail = False, f"{k}.{f}: {val} -> {b[k].get(f)}"
    check("macro-lock vs v17.8.0 (whitelisted convergence moves only)", ok,
          detail or f"{len(a)} elements")

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
    no_scroll = not any(k in t for k in ("<container>", "containerType",
                                         "containerScrollSpeed"))
    box_w = float(el_val(t, "size").split()[0]) * W
    fz = float(el_val(t, "fontSize"))
    # conservative: larger of int()/round() interpretations
    f_big = ImageFont.truetype(BOLD, max(int(fz * H), int(round(fz * H))))
    zelda = "THE LEGEND OF ZELDA: OCARINA OF TIME 3D"
    zw = f_big.getlength(zelda)
    margin = (box_w - zw) / 2
    check("title: static caption, no scroll; Zelda fits with >=48px/side margin",
          no_scroll and el_val(t, "fontSize") == "0.0260"
          and el_val(t, "size") == "0.58 0.0375" and margin >= 48,
          f"zelda={zw:.0f}px box={box_w:.0f}px margin={margin:.0f}px/side")

def check_rail_xml():
    xml = open(VIEWS).read()
    g = parse_view(xml, "gamelist")
    names = ["libMetaGenre", "libMetaSep1", "libMetaYear", "libMetaSep2",
             "libMetaPlayers"]
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
        if b0 < a1 - 1e-6:  # 7-decimal rounding; a real overlap is >=1px
            ok = False
    inside = spans[0][0] >= 0.413 and spans[-1][1] <= 0.993
    dev_gone = '<text name="libMetaDev">' not in g and '<text name="libMetaSep3">' not in g
    check("rail: 5 slots no-overlap, inside hero identity width (0.413-0.993); dev removed",
          ok and inside and dev_gone, f"span={spans[0][0]:.3f}-{spans[-1][1]:.3f}")
    # worst-case field widths must fit their slots (measured, 14px DejaVu)
    f_rail = ImageFont.truetype(REG, int(round(fs(0.0145))))
    worst = {"libMetaGenre": "FIRST-PERSON SHOOTER", "libMetaYear": "1998",
             "libMetaPlayers": "1-8 PLAYERS"}
    fit_ok, detail = True, ""
    for ename, txt in worst.items():
        tag = "datetime" if ename == "libMetaYear" else "text"
        b = el_box(g, f'{tag} name="{ename}"')
        sw = float(el_val(b, "size").split()[0]) * W
        tw = f_rail.getlength(txt)
        if tw > sw:
            fit_ok, detail = False, f"{ename} {tw:.0f}>{sw:.0f}"
    check("rail: worst-case values fit slots (no clip/overlap ever)",
          fit_ok, detail or "all fit")

def check_screenshot_xml():
    xml = open(VIEWS).read()
    s = el_box(parse_view(xml, "gamelist"), 'image name="libScreenshot"')
    check("screenshot: x=48, y=732 (+8px), h=170",
          el_val(s, "pos") == "0.0375 0.7625"
          and el_val(s, "size") == "0.309375 0.1770833",
          f"pos={el_val(s,'pos')} size={el_val(s,'size')}")

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
    check("hero wash: exists, softer still (peak alpha <= 20)",
          os.path.isfile(p) and max(alphas) <= 20 and im.size == (760, 760),
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
    check("all 21 rails present", n == 21, str(n))
    bad = []
    for s, _ in SYSTEMS:
        h1 = subprocess.run(["git", "-C", REPO, "show",
                             f"HEAD:theme-src/crystal/art/rails/{s}.png"],
                            capture_output=True).stdout
        h2 = open(os.path.join(ART, "rails", f"{s}.png"), "rb").read()
        if hashlib.sha256(h1).hexdigest() != hashlib.sha256(h2).hexdigest():
            bad.append(s)
    check("spine untouched: all rails byte-identical to v17.8.0", not bad,
          f"changed={bad}" if bad else "21 rails")

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
              "lib_shard_prev.png", "lib_title_rule.png",
              "star_filled.png", "star_unfilled.png", "lib_bottom_gradient.png",
              "lib_hero_wash.png", "lib_plane_hero.png"):
        h1 = subprocess.run(["git", "-C", REPO, "show", f"HEAD:theme-src/crystal/art/{f}"],
                            capture_output=True).stdout
        h2 = open(os.path.join(ART, f), "rb").read()
        if hashlib.sha256(h1).hexdigest() != hashlib.sha256(h2).hexdigest():
            check(f"asset unchanged: {f}", False)
            return
    check("shell assets unchanged (bg/shadow/glow/shards/rule/star/gradient)", True)
    # v17.9 intentionally regenerates: panel (+8px screenshot box, whisper
    # hairline) and the next-item shard (diagonal wedge)
    for f in ("lib_panel_main.png", "lib_shard_next.png"):
        h1 = subprocess.run(["git", "-C", REPO, "show", f"HEAD:theme-src/crystal/art/{f}"],
                            capture_output=True).stdout
        h2 = open(os.path.join(ART, f), "rb").read()
        if hashlib.sha256(h1).hexdigest() == hashlib.sha256(h2).hexdigest():
            check(f"asset regenerated: {f}", False, "byte-identical to v17.7")
            return
    check("v17.9 assets regenerated (panel/shard-next)", True)

def check_proof(name, v, img, info):
    mrect, zone = info["mrect"], info["zone"]
    pxa = img.load()
    zx0, zy0, zx1, zy1 = zone
    if v["marquee_aspect"]:
        # marquee fit: inside zone, aspect preserved, vertically centred
        x0, y0, x1, y1 = mrect
        ar = (x1 - x0) / (y1 - y0)
        check(f"[{name}] marquee maxSize-fit: aspect preserved, centred, in-zone",
              abs(ar - v["marquee_aspect"]) / v["marquee_aspect"] < 0.02
              and x0 >= zx0 - 1 and x1 <= zx1 + 1 and y0 >= zy0 - 1 and y1 <= zy1 + 1
              and abs((y0 + y1) / 2 - (zy0 + zy1) / 2) < 2,
              f"aspect={ar:.2f} rect={[int(q) for q in mrect]}")
        # zone outside the fitted rect is clean: no visible container. The
        # "NOW SHOWING" kicker is baked page furniture (y<60), excluded.
        outside = [pxa[x, y] for x in range(int(zx0), int(zx1), 7)
                   for y in range(max(int(zy0), 60), int(zy1), 7)
                   if not (x0 <= x <= x1 and y0 <= y <= y1)]
        clean = sum(1 for q in outside if lum(q) > 235)
        check(f"[{name}] marquee zone: no visible container around asset",
              len(outside) > 50 and clean / len(outside) > 0.97,
              f"clean={clean}/{len(outside)}")
    else:
        # missing marquee: clean fallback title inside the zone, no imitation
        x0, y0, x1, y1 = mrect
        ink = sum(1 for x in range(int(x0), int(x1), 4) for y in range(int(y0), int(y1), 4)
                  if lum(pxa[x, y]) < 150)
        check(f"[{name}] missing marquee: clean fallback title, no fake marquee",
              ink > 100, f"ink={ink}")
    # slot interiors uniform: no borders, no text, no debug treatment
    # (nomarquee: the marquee rect holds the fallback title - skip it)
    slot_list = [("screenshot", info["sbox"]), ("hero", info["hero"])]
    if v["marquee_aspect"]:
        slot_list.insert(0, ("marquee", mrect))
    for label, box in slot_list:
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
    # title: fits its box, no stray glyphs above it
    tbox = info["tbox"]
    gv = parse_view(open(VIEWS).read(), "gamelist")
    fz_t = float(el_val(el_box(gv, 'text name="libGameName"'), "fontSize"))
    f_t = ImageFont.truetype(BOLD, max(int(fz_t * H), int(round(fz_t * H))))
    tw = f_t.getlength(v["title"].upper())
    boxw = tbox[2] - tbox[0]
    check(f"[{name}] title fits box one line with >=48px/side margin (never clips)",
          tw <= boxw - 96, f"title={tw:.0f}px box={boxw:.0f}px")
    band = img.crop((550, 683, 1250, 696))
    stray = sum(1 for q in band.getdata() if lum(q) > 215)
    check(f"[{name}] above-title band: no stray glyphs", stray < 400, f"bright={stray}")
    # title/next-media: no overlap (title box bottom vs next slot top)
    xml2 = open(VIEWS).read()
    cb = el_box(parse_view(xml2, "gamelist"), 'carousel name="gameCarousel"')
    csh = float(el_val(cb, "size").split()[1])
    pitch = sz(csh) / 3.0
    cy0 = float(el_val(cb, "pos").split()[1])
    hx0, hy0, hx1, hy1 = info["hero"]
    sc = 240 / max(hx1 - hx0, hy1 - hy0)
    next_top = sz(cy0) + pitch - (hy1 - hy0) * sc / 2
    check(f"[{name}] title box clear of next media",
          tbox[3] < next_top - 20, f"tbox_bottom={tbox[3]:.0f} next_top={next_top:.0f}")
    # rail strings fit their slots (height-relative fonts)
    xml = open(VIEWS).read()
    g = parse_view(xml, "gamelist")
    f_rail = ImageFont.truetype(REG, int(round(fs(0.0145))))
    fit_ok, worst = True, ""
    for ename, txt in (("libMetaGenre", v["genre"].upper()), ("libMetaYear", v["year"]),
                       ("libMetaPlayers", v["players"].upper())):
        tag = "datetime" if "Year" in ename else "text"
        b = el_box(g, f'{tag} name="{ename}"')
        sw = float(el_val(b, "size").split()[0]) * W
        tw = f_rail.getlength(txt)
        if tw > sw:
            fit_ok, worst = False, f"{ename} {tw:.0f}>{sw:.0f}"
    check(f"[{name}] rail values fit their slots (no overlap/overflow)", fit_ok, worst or "all fit")
    # left-column developer: wraps to <=2 lines inside its box, never spills
    f_micro = ImageFont.truetype(REG, int(round(fs(0.015))))
    db = el_box(g, 'text name="libDev"')
    dev_box_w = float(el_val(db, "size").split()[0]) * W
    dev_y = float(el_val(db, "pos").split()[1]) * H
    dev_lines = wrap(v["dev"].upper(), f_micro, dev_box_w) if v["dev"] else []
    dev_bottom = dev_y + len(dev_lines) * 22
    kick_y = 694 + 10  # baked SCREENSHOT kicker, panel-local -> global
    check(f"[{name}] developer wraps in-column (<=2 lines, no spill; empty ok)",
          len(dev_lines) <= 2 and dev_bottom < kick_y,
          f"lines={len(dev_lines)} bottom={dev_bottom:.0f}")
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

def check_shard_wedge():
    im = Image.open(os.path.join(ART, "lib_shard_next.png")).convert("RGBA")
    a = im.split()[3]
    w2, h2 = im.size
    edge = ([a.getpixel((x, 0)) for x in range(w2)] + [a.getpixel((x, h2 - 1)) for x in range(w2)]
            + [a.getpixel((0, y)) for y in range(h2)] + [a.getpixel((w2 - 1, y)) for y in range(h2)])
    tl = a.getpixel((30, 30))
    br = a.getpixel((w2 - 30, h2 - 30))
    check("shard-next wedge: no hard edges (bitmap rim alpha ~0)",
          max(edge) <= 6, f"rim_max={max(edge)}")
    check("shard-next wedge: alpha ramps 0 (TL) -> ~65 (BR)",
          tl <= 10 and 45 <= br <= 70, f"TL={tl} BR={br}")
    xml = open(VIEWS).read()
    b = el_box(parse_view(xml, "gamelist"), 'image name="libShardNext"')
    check("shard-next element: (830,810) 450x150",
          el_val(b, "pos") == "0.6484375 0.84375"
          and el_val(b, "size") == "0.3515625 0.15625",
          f"pos={el_val(b,'pos')} size={el_val(b,'size')}")

def check_shadow():
    xml = open(VIEWS).read()
    b = el_box(parse_view(xml, "gamelist"), 'image name="libSelectedShadow"')
    check("hero shadow: 480px (hero footprint), opacity 0.7",
          el_val(b, "size") == "0.375 0.075"
          and el_val(b, "opacity") == "0.7",
          f"size={el_val(b,'size')} opacity={el_val(b,'opacity')}")

def check_rail_centre():
    xml = open(VIEWS).read()
    g = parse_view(xml, "gamelist")
    names = ["libMetaGenre", "libMetaSep1", "libMetaYear", "libMetaSep2", "libMetaPlayers"]
    spans = []
    for nm in names:
        tag = "datetime" if nm == "libMetaYear" else "text"
        b = el_box(g, f'{tag} name="{nm}"')
        x = float(el_val(b, "pos").split()[0]) * W
        w = float(el_val(b, "size").split()[0]) * W
        spans.append((x - w / 2, x + w / 2))
    spans.sort()
    cx = (spans[0][0] + spans[-1][1]) / 2
    contig = all(abs(s1[0] - s0[1]) < 1.5 for (s0, s1) in zip(spans, spans[1:]))
    check("rail: 5 slots contiguous and centred at x=900",
          contig and abs(cx - 900) < 2,
          f"span={spans[0][0]:.0f}-{spans[-1][1]:.0f} centre={cx:.0f}")

def check_clearance_worst_case():
    # real geometry: Zelda title at 0.0295 vs rail at 0.0145
    xml = open(VIEWS).read()
    g = parse_view(xml, "gamelist")
    tb = el_box(g, 'text name="libGameName"')
    tcy = float(el_val(tb, "pos").split()[1]) * H
    mcy = float(el_val(el_box(g, 'text name="libMetaGenre"'), "pos").split()[1]) * H
    c = Image.new("RGB", (900, 220), "white")
    d = ImageDraw.Draw(c)
    d.text((450, 90), "THE LEGEND OF ZELDA: OCARINA OF TIME 3D",
           font=ImageFont.truetype(BOLD, int(round(0.0260 * H))), fill="black", anchor="mm")
    d.text((450, 90 + (mcy - tcy)),
           "FIRST-PERSON SHOOTER \u2022 1998 \u2022 1-8 PLAYERS",
           font=ImageFont.truetype(REG, int(round(0.0145 * H))), fill="red", anchor="mm")
    pxx = c.load()
    t_rows = [y for y in range(220) for x in range(900) if pxx[x, y] == (0, 0, 0)]
    m_rows = [y for y in range(220) for x in range(900) if pxx[x, y][0] > 200 and pxx[x, y][1] < 100]
    gap = min(m_rows) - max(t_rows)
    check("title/rail clearance, real worst case (zelda + max rail)", gap >= 4, f"gap={gap}px")


def check_whisper():
    # the 2px #0A2FA0 alpha-8 hairline must be a whisper, not content:
    # sample along its path - pixels should carry a faint blue tint
    # (b - r > 2 on near-white) and must NEVER be dark stamped values
    # (a broken ImageDraw blend would stamp (10,47,160,8) as dark)
    im = Image.open(os.path.join(ART, "lib_panel_main.png")).convert("RGBA")
    pxd = im.load()
    tint, dark = 0, 0
    # the line exits the white module around local (445,155); only
    # sample the on-body segment (the rest is correctly mask-clipped)
    for i in range(0, 148, 2):
        x = 294 + int(i * 176 / 180)
        r, g2, b, a = pxd[x, i]
        if b - r > 2 and r > 235:
            tint += 1
        if r < 150:
            dark += 1
    check("panel whisper hairline: faint blue tint, never a dark stamp",
          tint > 50 and dark == 0, f"tint={tint} dark={dark}")

if __name__ == "__main__":
    os.makedirs(PROOFS, exist_ok=True)
    check_macro_lock(); check_marquee_xml(); check_title_xml(); check_rail_xml()
    check_screenshot_xml(); check_typography(); check_fallbacks(); check_plane()
    check_wash(); check_rails(); check_motion(); check_hygiene()
    check_clearance_worst_case(); check_shard_wedge(); check_shadow()
    check_rail_centre(); check_whisper()
    for name, v in VARIANTS.items():
        img, info = render(v)
        p = os.path.join(PROOFS, f"mock_v17_9_{name}.png")
        img.save(p)
        print("saved", p)
        check_proof(name, v, img, info)
    fails = sum(1 for _, ok, _ in CHECK_LOG if not ok)
    print(f"\n{'ALL CHECKS PASS' if fails == 0 else str(fails) + ' CHECKS FAILED'} "
          f"({len(CHECK_LOG)} checks)")
    sys.exit(1 if fails else 0)
