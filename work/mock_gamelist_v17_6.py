#!/usr/bin/env python3
"""Crystal v17.6.0 gamelist mock + verification (PIL renders, never ES-DE).

The VM carries NO scraped artwork, so hero / marquee / screenshot /
previous / next are rendered as honest neutral LIVE-SLOT indicators
(dashed royal border, binding label, tiny yellow registration ticks) -
never invented game art. The proofs assess the UI SHELL only.

Variants: ps2 (Gran Turismo 4), n64 (Super Mario 64), gba (Mario Golf:
Advance Tour) - the user's named Nova QA contexts.

v17.6.0 maturity assertions: typography discipline (DejaVuSans-Bold
display / DejaVuSans body - zero PermanentMarker), yellow <=5%,
macro-lock (all 29 elements' geometry byte-identical to v17.5.0),
fallbacks byte-identical to the frozen v17.4 baseline, spine texture
reduced further, itemTransitions=animate only.
"""
import os, sys, json, hashlib, subprocess, math
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
SLATE = (126, 138, 166)
CHECK_LOG = []

def check(name, ok, detail=""):
    CHECK_LOG.append((name, ok, detail))
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""))

def px(v): return v * W
def sz(v): return v * H

def lum(p): return 0.299*p[0] + 0.587*p[1] + 0.114*p[2]
def is_yellow(p): return p[0] > 200 and p[1] > 160 and p[2] < 110
def is_yellowish(p):
    return p[0] > 220 and p[1] > 190 and p[2] < 205 and (p[0] - p[2]) > 50

def parse_view(xml, name):
    start = xml.index(f'<view name="{name}">')
    end = xml.index("</view>", start)
    return xml[start:end]

def el_box(view, ename):
    tag = ename.split()[0]
    start = view.index("<" + ename)
    end = view.index("</" + tag + ">", start)
    return view[start:end]

def el_val(line, tag):
    return line.split(f"<{tag}>")[1].split(f"</{tag}>")[0]

# ---------------- slot indicators: honest live-asset markers ------------
def dashed(d, box, color, width=2, dash=9, gap=6):
    x0, y0, x1, y1 = box
    for horiz, fixed, start, end in ((True, y0, x0, x1), (True, y1, x0, x1),
                                    (False, x0, y0, y1), (False, x1, y0, y1)):
        p = start
        while p < end:
            q = min(p + dash, end)
            if horiz:
                d.line([(p, fixed), (q, fixed)], fill=color, width=width)
            else:
                d.line([(fixed, p), (fixed, q)], fill=color, width=width)
            p += dash + gap

def tracked_text_img(text, size, color, tracking, alpha=255):
    font = ImageFont.truetype(BOLD, size)
    tw = 0
    for ch in text:
        tw += font.getlength(ch) + tracking
    img = Image.new("RGBA", (int(tw) + 8, size + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    x = 4
    for ch in text:
        d.text((x, 4), ch, font=font, fill=color + (alpha,))
        x += font.getlength(ch) + tracking
    return img

def draw_slot(layer, box, label, font_sz=13, label_alpha=200):
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    d = ImageDraw.Draw(layer, "RGBA")
    d.rectangle([(x0, y0), (x1, y1)], fill=(255, 255, 255, 90))
    dashed(d, (x0, y0, x1, y1), ROYAL + (170,), width=2)
    yc = YELLOW + (220,)
    for cx, cy, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1),
                           (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(cx, cy), (cx + sx * 14, cy)], fill=yc, width=2)
        d.line([(cx, cy), (cx, cy + sy * 14)], fill=yc, width=2)
    lab = tracked_text_img(label, font_sz, SLATE, 3, alpha=label_alpha)
    layer.alpha_composite(lab, ((x0 + x1 - lab.width) // 2,
                               (y0 + y1 - lab.height) // 2))

# --------------------------- metadata (real data) -----------------------
def draw_desc(base, desc, xy):
    f = ImageFont.truetype(REG, 17)
    d = ImageDraw.Draw(base, "RGBA")
    y = xy[1]
    for line in desc:
        d.text((xy[0], y), line, font=f, fill=INKDIM + (255,))
        y += 26

def draw_date(base, year, xy):
    f = ImageFont.truetype(BOLD, 48)
    d = ImageDraw.Draw(base, "RGBA")
    d.text((xy[0], xy[1]), year, font=f, fill=NAVY + (255,))

def draw_rating(base, fill, xy):
    x0, y0 = xy
    for i in range(5):
        c = (x0 + i * 42 + 15, y0 + 16)
        pts = []
        for k in range(10):
            r = 15 if k % 2 == 0 else 6.2
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
        # v17.6: filled star is ROYAL (recolored asset), not yellow
        ImageDraw.Draw(base, "RGBA").polygon(
            pts, fill=ROYAL + (255,) if i < fill else (255, 255, 255, 120),
            outline=NAVY + (255,))

def draw_genre(base, genre, xy):
    d = ImageDraw.Draw(base, "RGBA")
    d.text(xy, genre, font=ImageFont.truetype(BOLD, 21), fill=NAVY + (255,))

def draw_facts(base, text, xy):
    d = ImageDraw.Draw(base, "RGBA")
    d.text(xy, text, font=ImageFont.truetype(REG, 14), fill=INKDIM + (255,))

def draw_title_block(base, title, meta):
    rule = Image.open(os.path.join(ART, "lib_title_rule.png")).convert("RGBA")
    base.alpha_composite(rule, (int(900 - rule.width / 2), 714))
    d = ImageDraw.Draw(base, "RGBA")
    # engine: title DejaVuSans-Bold 38px centered at (900,736);
    # meta rail DejaVuSans 14px centered at y767.5
    d.text((900, 736), title, font=ImageFont.truetype(BOLD, 38),
           fill=(255, 255, 255, 255), anchor="mm")
    d.text((900, 767), meta, font=ImageFont.truetype(REG, 14),
           fill=(255, 255, 255, 150), anchor="mm")

def draw_footer(base, title, sysname):
    d = ImageDraw.Draw(base, "RGBA")
    f = ImageFont.truetype(REG, 13)
    t1 = "A PLAY \u2022 B BACK"
    d.text((640 - f.getlength(t1) / 2, 912), t1, font=f,
           fill=(255, 255, 255, 200))

# ------------------------------- render ---------------------------------
def render(system, game, prev_next=True):
    base = Image.open(os.path.join(ART, "gamelist_generic_bg.png")).convert("RGBA").resize((W, H))
    panel = Image.open(os.path.join(ART, "lib_panel_main.png")).convert("RGBA")
    base.alpha_composite(panel, (6, 10))
    base.alpha_composite(Image.open(os.path.join(ART, "rails", f"{system}.png")).convert("RGBA"), (486, 24))
    xml = open(VIEWS, encoding="utf-8").read()
    view = parse_view(xml, "gamelist")

    mline = el_box(view, 'image name="libMarquee"')
    mx, my = [float(x) for x in el_val(mline, "pos").split()]
    mw_, mh_ = [float(x) for x in el_val(mline, "maxSize").split()]
    mbox = (px(mx), sz(my), px(mx) + px(mw_), sz(my) + sz(mh_))
    sline = el_box(view, 'image name="libScreenshot"')
    sx, sy = [float(x) for x in el_val(sline, "pos").split()]
    sw_, sh_ = [float(x) for x in el_val(sline, "size").split()]
    sbox = (px(sx), sz(sy), px(sx) + px(sw_), sz(sy) + sz(sh_))

    slots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_slot(slots, mbox, "${game.marquee}")
    draw_slot(slots, sbox, "${game.screenshot}")
    draw_slot(slots, (900 - 270, 430 - 270, 900 + 270, 430 + 270),
              "${game.physicalmedia}", font_sz=15)
    base.alpha_composite(slots)

    if prev_next:
        dim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for cy in (-50, 910):
            b = (900 - 120, cy - 120, 900 + 120, cy + 120)
            cx0, cy0, cx1, cy1 = [int(round(v)) for v in b]
            ImageDraw.Draw(dim, "RGBA").rectangle(
                [(max(cx0, 0), max(cy0, 0)), (min(cx1, W), min(cy1, H))],
                fill=(255, 255, 255, 90))
            draw_slot(dim, (cx0, cy0, cx1, cy1), "${game.physicalmedia}",
                      font_sz=11, label_alpha=170)
        dim.putalpha(dim.split()[3].point(lambda a: int(a * 0.45)))
        base.alpha_composite(dim)

    draw_desc(base, game["desc"], (48, 312))
    draw_date(base, game["year"], (48, 468))
    draw_rating(base, 4, (392, 478))
    draw_genre(base, game["genre"], (48, 578))
    draw_facts(base, game["players"], (48, 640))
    draw_facts(base, game["dev"], (300, 640))

    shard_p = Image.open(os.path.join(ART, "lib_shard_prev.png")).convert("RGBA")
    base.alpha_composite(shard_p.resize((132, 132)), (894, -16))
    shard_n = Image.open(os.path.join(ART, "lib_shard_next.png")).convert("RGBA")
    base.alpha_composite(shard_n.resize((144, 144)), (828, 868))

    draw_title_block(base, game["title"], game["meta"])
    draw_footer(base, game["title"], game["sysname"])
    return base.convert("RGB")

# ------------------------------- checks ---------------------------------
def check_macro_lock():
    import re
    def geom_lines(text):
        d = {}
        cur = None
        for line in text.splitlines():
            m = re.search(r'<(image|text|datetime|rating|carousel) name="([^"]+)"', line)
            if m: cur = m.group(2); d[cur] = {}
            g = re.search(r'<(pos|size|origin|zIndex|maxSize)>([^<]*)</\1>', line)
            if g and cur: d[cur][g.group(1)] = g.group(2)
        return d
    xml_head = subprocess.run(["git", "-C", REPO, "show", "HEAD:theme-src/crystal/views.xml"],
                              capture_output=True, text=True).stdout
    xml_now = open(VIEWS, encoding="utf-8").read()
    a, b = geom_lines(parse_view(xml_head, "gamelist")), geom_lines(parse_view(xml_now, "gamelist"))
    same = sorted(a) == sorted(b) and all(a[k] == b[k] for k in a)
    check("macro-lock: ALL gamelist geometry byte-identical to v17.5.0 (no exceptions)",
          same, f"elements={len(a)}")

def check_typography_discipline():
    import re as _re
    xml = open(VIEWS, encoding="utf-8").read()
    g = _re.sub(r"<!--.*?-->", "", parse_view(xml, "gamelist"), flags=_re.S)
    check("no PermanentMarker reference anywhere in the gamelist XML",
          "PermanentMarker" not in g)
    check("brush font deleted from the theme",
          not os.path.exists(os.path.join(FONTS, "PermanentMarker-Regular.ttf")))
    check("DejaVuSans-Bold.ttf + DejaVuSans.ttf shipped in theme fonts",
          os.path.isfile(os.path.join(FONTS, "DejaVuSans-Bold.ttf")) and
          os.path.isfile(os.path.join(FONTS, "DejaVuSans.ttf")))
    import re
    expect = {"libMarqueeTitle": ("./fonts/DejaVuSans-Bold.ttf", "0.034"),
              "libYear": ("./fonts/DejaVuSans-Bold.ttf", "0.050"),
              "libDesc": ("./fonts/DejaVuSans.ttf", "0.0175"),
              "libGenre": ("./fonts/DejaVuSans-Bold.ttf", "0.022"),
              "libPlayers": ("./fonts/DejaVuSans.ttf", "0.015"),
              "libDev": ("./fonts/DejaVuSans.ttf", "0.015"),
              "libGameName": ("./fonts/DejaVuSans-Bold.ttf", "0.040"),
              "libMetaGenre": ("./fonts/DejaVuSans.ttf", "0.0145"),
              "libMetaDev": ("./fonts/DejaVuSans.ttf", "0.0145"),
              "libFooter": ("./fonts/DejaVuSans.ttf", "0.0135")}
    ok, detail = True, ""
    for name, (path, size) in expect.items():
        i = g.index(f'name="{name}"')
        seg = g[i:i + 700]
        if path not in seg or f"<fontSize>{size}</fontSize>" not in seg:
            ok = False
            detail += f" {name}"
    check("typography system: display/body/micro fonts+sizes match spec", ok,
          "mismatch:" + detail if detail else f"{len(expect)} elements")
    # every gamelist text/datetime element has an explicit fontPath now
    names = re.findall(r'<(text|datetime) name="([^"]+)"', g)
    missing = [n for t, n in names
               if "<fontPath>" not in g[g.index(f'name="{n}"'):g.index(f'name="{n}"') + 700]]
    check("explicit fontPath on every gamelist text/datetime element", not missing,
          f"missing={missing}" if missing else f"{len(names)} elements")

def check_bindings():
    xml = open(VIEWS, encoding="utf-8").read()
    g = parse_view(xml, "gamelist")
    ok = True
    for binding in ("<imageType>marquee</imageType>",
                    "<imageType>physicalmedia 3dbox</imageType>",
                    "<imageType>image</imageType>",
                    "./art/rails/${system.name}.png",
                    "./media_fallbacks/${system.name}.png",
                    "itemTransitions", "animate"):
        if binding not in g:
            ok = False
            print("  missing:", binding)
    for bad in ("<storyboard", "<animation ", "itemRotation", "<video "):
        if bad in g:
            ok = False
            print("  banned present:", bad)
    check("dynamic bindings + carousel transitions intact, no banned props", ok)

def check_panel_art():
    p = Image.open(os.path.join(ART, "lib_panel_main.png")).convert("RGBA")
    bad = 0
    for lx in range(34, 440, 8):
        for ly in range(40, 280, 8):
            q = p.getpixel((lx, ly))
            if q[3] > 200 and lum(q[:3]) < 110:
                bad += 1
    check("marquee zone open white (no dark box)", bad == 0, f"dark={bad}")
    royal = 0
    for x in range(40, 430, 6):
        r, gg, b = p.getpixel((x, 294))[:3]
        if b > r + 25 and b > gg + 10:
            royal += 1
    check("masthead baseline hairline present", royal > 40, f"royal_px={royal}")
    reg = sum(1 for x in range(36, 43) for y in range(292, 297) if is_yellow(p.getpixel((x, y))))
    check("masthead yellow registration square (the one kept)", reg > 0, f"yellow_px={reg}")
    # the v17.5 yellow triangle at NOW SHOWING is DELETED
    tri = sum(1 for x in range(26, 40) for y in range(8, 20) if is_yellow(p.getpixel((x, y))))
    check("NOW SHOWING yellow triangle deleted", tri == 0, f"yellow_px={tri}")
    # the rule-425 yellow square is DELETED (plain rule)
    sq = sum(1 for x in range(34, 46) for y in range(421, 429) if is_yellow(p.getpixel((x, y))))
    check("rule-425 yellow square deleted", sq == 0, f"yellow_px={sq}")
    # the blue intrusion is DELETED: its old zone must be white/clean
    intr = sum(1 for x in range(420, 448, 2) for y in range(340, 600, 4)
               if lum(p.getpixel((x, y))[:3]) < 225)
    check("blue geometric intrusion deleted", intr < 40, f"nonwhite_px={intr}")
    # the blueprint fragment is DELETED
    bp = sum(1 for x in range(340, 460, 4) for y in range(560, 690, 4)
             if lum(p.getpixel((x, y))[:3]) < 225)
    check("blueprint fragment deleted", bp < 60, f"nonwhite_px={bp}")
    # screenshot registration corner still crosses the top-right
    corner = sum(1 for x in range(424, 440) for y in range(682, 698) if is_yellow(p.getpixel((x, y))))
    check("screenshot registration corner (the one kept)", corner > 8, f"yellow_px={corner}")
    bottom = sum(1 for x in range(40, 430, 6) if lum(p.getpixel((x, 900))) < 190)
    check("screenshot bottom-edge hairline", bottom > 30, f"dark_px={bottom}")

def check_title_rule():
    r = Image.open(os.path.join(ART, "lib_title_rule.png")).convert("RGB")
    pix = list(r.getdata())
    yel = sum(1 for q in pix if is_yellow(q))
    white = sum(1 for q in pix if lum(q) > 235)
    check("title rule: one thin subtle yellow rule, no end-ticks, no white",
          150 < yel < 400 and white == 0, f"yellow={yel} white={white} size={r.size}")

def check_star():
    s = Image.open(os.path.join(ART, "star_filled.png")).convert("RGBA")
    pix = [q for q in s.getdata() if q[3] > 128]
    yel = sum(1 for q in pix if is_yellow(q[:3]))
    royal = sum(1 for q in pix if q[2] > q[0] + 40 and q[2] > q[1] + 20)
    check("rating star recolored yellow -> royal blue", yel == 0 and royal > 300,
          f"yellow={yel} royal={royal}")

def check_rails():
    ok_count = 0
    for system, _ in SYSTEMS:
        if os.path.exists(os.path.join(ART, "rails", f"{system}.png")):
            ok_count += 1
    check("all 21 rails regenerated", ok_count == 21, str(ok_count))
    head_rails = subprocess.run(["git", "-C", REPO, "show", "HEAD:theme-src/crystal/art/rails/ps2.png"],
                                capture_output=True).stdout
    import io
    old = Image.open(io.BytesIO(head_rails)).convert("RGB")
    new = Image.open(os.path.join(ART, "rails/ps2.png")).convert("RGB")
    def bright(im):
        return sum(1 for x in range(20, 50, 2) for y in range(100, 250, 2)
                   if lum(im.getpixel((x, y))) > 170)
    b_old, b_new = bright(old), bright(new)
    check("spine texture reduced further vs v17.5", b_new <= 0.6 * b_old,
          f"old={b_old} new={b_new}")
    line = sum(1 for y in range(50, 880) if is_yellow(new.getpixel((4, y))))
    side = sum(1 for y in range(50, 880)
               if is_yellow(new.getpixel((3, y))) or is_yellow(new.getpixel((5, y))))
    check("spine: ONE thin 1px yellow line, no tab", line > 700 and side == 0,
          f"line_px={line} side_px={side}")
    tab = sum(1 for x in range(1, 8) for y in range(20, 40) if is_yellow(new.getpixel((x, y))))
    check("spine tab deleted", tab == 0, f"yellow_px={tab}")
    params = json.load(open(os.path.join(REPO, "work/rail_params_v17_6.json")))
    pad_ok = all(v["pad"] >= 20 for v in params.values())
    check("logo plate breathing room >= 20px (21 systems)", pad_ok and len(params) == 21)
    xml = open(VIEWS, encoding="utf-8").read()
    check("spine keeps dynamic ${system.name} binding", "${system.name}" in parse_view(xml, "gamelist"))

def check_title_meta_geometry():
    xml = open(VIEWS, encoding="utf-8").read()
    g = parse_view(xml, "gamelist")
    tb = el_box(g, 'text name="libGameName"')
    tsize = float(el_val(tb, "fontSize")) * W
    tcy = float(el_val(tb, "pos").split()[1]) * H
    mb = el_box(g, 'text name="libMetaGenre"')
    msize = float(el_val(mb, "fontSize")) * W
    mcy = float(el_val(mb, "pos").split()[1]) * H
    dv_b = ImageFont.truetype(BOLD, int(tsize))
    dv_r = ImageFont.truetype(REG, int(msize))
    c = Image.new("RGB", (900, 200), "white")
    d = ImageDraw.Draw(c)
    d.text((450, 80), "GRAN TURISMO 4", font=dv_b, fill="black", anchor="mm")
    d.text((450, 80 + (mcy - tcy)), "RACING \u2022 2004 \u2022 TEST \u2022 1-2 PLAYERS",
           font=dv_r, fill="red", anchor="mm")
    px = c.load()
    t_rows = [y for y in range(200) for x in range(900) if px[x, y] == (0, 0, 0)]
    m_rows = [y for y in range(200) for x in range(900)
              if px[x, y][0] > 200 and px[x, y][1] < 100]
    overlap = max(0, min(max(t_rows), max(m_rows)) - max(min(t_rows), min(m_rows)))
    check("title/meta glyph clearance (real fonts, XML positions)",
          overlap == 0 and abs(tcy - 736) < 1 and abs(mcy - 767.5) < 1,
          f"title_y={tcy:.1f} meta_y={mcy:.1f} overlap={overlap}px")

def check_fallbacks():
    base = {l.split()[1]: l.split()[0] for l in open(BASELINE) if l.strip()}
    ok, bad = True, []
    for name, h in base.items():
        p = os.path.join(REPO, name)
        real = hashlib.sha256(open(p, "rb").read()).hexdigest()
        if real != h:
            ok = False
            bad.append(name)
    check("all 22 media_fallbacks byte-identical to frozen baseline", ok,
          f"changed={bad}" if bad else f"{len(base)} files")
    untouched = []
    for f in ("lib_shadow_soft.png", "lib_glow_blue.png", "lib_plane_hero.png",
              "lib_shard_prev.png", "lib_shard_next.png",
              "gamelist_generic_bg.png"):
        head = subprocess.run(["git", "-C", REPO, "show", f"HEAD:theme-src/crystal/art/{f}"],
                              capture_output=True).stdout
        now = open(os.path.join(ART, f), "rb").read()
        untouched.append(hashlib.sha256(head).hexdigest() == hashlib.sha256(now).hexdigest())
    check("hero-treatment + generic-bg assets byte-identical to v17.5.0", all(untouched))

def check_hygiene():
    xml = open(VIEWS, encoding="utf-8").read()
    check("no debug pixels", "DEBUG" not in xml.upper() or "debug pixels" in xml.lower())
    sv_head = subprocess.run(["git", "-C", REPO, "show", "HEAD:theme-src/crystal/views.xml"],
                             capture_output=True, text=True).stdout
    check("system view section byte-identical",
          parse_view(sv_head, "system") == parse_view(xml, "system"))
    st = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "theme-src/crystal/art/cards",
                         "theme-src/crystal/art/poster_on"], capture_output=True, text=True).stdout
    check("system-view cards untouched", st.strip() == "", st.strip()[:80])

def check_transitions():
    t = json.load(open(os.path.join(REPO, "esde_theme_tables.json")))
    txt = json.dumps(t)
    check("pinned 3.4.1 tables: itemTransitions exists only on carousel+grid",
          "itemTransitions" in txt and "storyboard" not in txt.lower()
          and "keyframes" not in txt.lower() and "crossfade" not in txt.lower())
    check("pinned 3.4.1 tables: no durations/easing/tween anywhere",
          "duration" not in txt.lower() and "easing" not in txt.lower()
          and "tween" not in txt.lower())
    import re as _re
    xml = open(VIEWS, encoding="utf-8").read()
    g = _re.sub(r"<!--.*?-->", "", parse_view(xml, "gamelist"), flags=_re.S)
    i = g.index('<carousel name="gameCarousel"')
    block = g[i:i + 1200]
    check("gameCarousel itemTransitions=animate engaged",
          "itemTransitions" in block and "animate" in block)
    motionish = sum(1 for bad in ("<storyboard", "<animation ", "itemRotation",
                                  "crossfade", "fadeInTime", "duration")
                    if bad in g)
    check("no other motion constructs in the gamelist view", motionish == 0)

def check_yellow_budget(path):
    img = Image.open(path).convert("RGB")
    pix = list(img.getdata())
    yel = sum(1 for q in pix if is_yellow(q) or is_yellowish(q))
    share = yel / len(pix) * 100
    return share, yel

def check_proof(system, path, title):
    img = Image.open(path).convert("RGB")
    slot = img.crop((630, 160, 1080, 700))
    spx = list(slot.getdata())
    royal_h = sum(1 for q in spx if q[2] > q[0] + 40 and q[2] > q[1] + 20 and lum(q) < 150)
    inset = img.crop((654, 184, 1056, 676))
    pix = list(inset.getdata())
    mean = sum(lum(q) for q in pix) / len(pix)
    yel = sum(1 for q in pix if is_yellow(q))
    check(f"[{system}] hero slot indicator present, neutral, no yellow",
          royal_h > 300 and mean > 190 and yel == 0,
          f"royal={royal_h} mean={mean:.0f} yellow={yel}")
    zone = img.crop((24, 44, 448, 296))
    zpx = list(zone.getdata())
    royal = sum(1 for q in zpx if q[2] > q[0] + 40 and q[2] > q[1] + 20 and lum(q) < 150)
    dark = sum(1 for q in zpx if lum(q) < 60)
    check(f"[{system}] marquee slot indicator present, no bespoke art",
          royal > 200 and dark < 800, f"royal={royal} dark={dark}")
    shot = img.crop((42, 700, 438, 910))
    spx = list(shot.getdata())
    royal2 = sum(1 for q in spx if q[2] > q[0] + 40 and q[2] > q[1] + 20 and lum(q) < 150)
    inner = img.crop((52, 710, 428, 900))
    imean = sum(lum(q) for q in inner.getdata()) / (376 * 190)
    check(f"[{system}] screenshot slot indicator present",
          royal2 > 150 and imean > 180, f"royal={royal2} imean={imean:.0f}")
    band = img.crop((550, 708, 1250, 764))
    bpx = list(band.getdata())
    white_txt = sum(1 for q in bpx if lum(q) > 210)
    clean = render(system, GAMES[system], prev_next=False).convert("RGB")
    clean_band = clean.crop((550, 708, 1250, 764))
    diff = sum(1 for a, b in zip(band.getdata(), clean_band.getdata()) if a != b)
    check(f"[{system}] title present + next item clear of title zone",
          white_txt > 1500 and diff == 0,
          f"white={white_txt} intruding_px={diff}")
    rule = img.crop((840, 716, 960, 723))
    yel2 = sum(1 for q in rule.getdata() if is_yellow(q))
    check(f"[{system}] one thin yellow rule under title", yel2 > 60, f"yellow={yel2}")
    share, yel3 = check_yellow_budget(path)
    check(f"[{system}] yellow pixel-share <= 5%", share <= 5.0,
          f"{share:.2f}% ({yel3}px)")
    # rating: no yellow stars in the rating zone
    rz = img.crop((392, 470, 610, 510))
    rzpx = rz.load()
    prm = json.load(open(os.path.join(REPO, "work/rail_params_v17_6.json")))[system]
    lw, lh = prm["logo"]; pad = prm["pad"]
    ox, oy = (60 - lw) // 2 + 2, (912 - lh) // 2
    # global plate box (supplied logo art is allowed its own colors)
    pb = (486 + ox - pad, 24 + oy - pad, 486 + ox + lw + pad, 24 + oy + lh + pad)
    def in_plate(gx, gy):
        return pb[0] <= gx <= pb[2] and pb[1] <= gy <= pb[3]
    ryel = sum(1 for x in range(rz.width) for y in range(rz.height)
               if not (488 <= 392 + x <= 493) and not in_plate(392 + x, 470 + y)
               and is_yellow(rzpx[x, y][:3]))
    check(f"[{system}] rating zone: no yellow stars", ryel == 0, f"yellow={ryel}")

GAMES = {
    "ps2": dict(title="GRAN TURISMO 4", sysname="Sony PlayStation 2", genre="RACING",
                year="2004", dev="POLYPHONY DIGITAL", players="1-2 PLAYERS",
                meta="RACING \u2022 2004 \u2022 POLYPHONY DIGITAL \u2022 1-2 PLAYERS",
                desc=["The definitive driving simulator: 700+ cars,",
                      "51 circuits and a career of unmatched depth.",
                      "Polyphony's obsession, rendered at 1080i.",
                      "Precision handling, endless tuning."]),
    "n64": dict(title="SUPER MARIO 64", sysname="Nintendo 64", genre="PLATFORMER",
                year="1996", dev="NINTENDO", players="1 PLAYER",
                meta="PLATFORMER \u2022 1996 \u2022 NINTENDO \u2022 1 PLAYER",
                desc=["A landmark in 3D design: 120 Power Stars",
                      "hidden across painted worlds. Bowser's",
                      "ambitions end at the castle gates.",
                      "The blueprint for every 3D platformer since."]),
    "gba": dict(title="MARIO GOLF: ADVANCE TOUR", sysname="Game Boy Advance", genre="SPORTS",
                year="2004", dev="CAMELOT", players="1-4 PLAYERS",
                meta="SPORTS \u2022 2004 \u2022 CAMELOT \u2022 1-4 PLAYERS",
                desc=["Camelot's handheld golf RPG: build a rookie",
                      "from the clubhouse to the Mushroom Kingdom",
                      "tour. Deep swing mechanics, charming story.",
                      "Link-cable multiplayer for four."]),
}

if __name__ == "__main__":
    os.makedirs(PROOFS, exist_ok=True)
    check_macro_lock(); check_typography_discipline(); check_bindings()
    check_panel_art(); check_title_rule(); check_star()
    check_title_meta_geometry()
    check_rails(); check_fallbacks(); check_hygiene(); check_transitions()
    for system, game in GAMES.items():
        p = os.path.join(PROOFS, f"mock_v17_6_{system}.png")
        render(system, game).save(p)
        print("saved", p)
        check_proof(system, p, game["title"])
    fails = sum(1 for _, ok, _ in CHECK_LOG if not ok)
    print(f"\n{'ALL CHECKS PASS' if fails == 0 else str(fails) + ' CHECKS FAILED'} "
          f"({len(CHECK_LOG)} checks)")
    sys.exit(1 if fails else 0)
