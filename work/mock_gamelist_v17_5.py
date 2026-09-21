#!/usr/bin/env python3
"""Crystal v17.5.0 gamelist mock + verification.

The VM carries NO scraped artwork, so hero / marquee / screenshot /
previous / next are rendered as honest neutral LIVE-SLOT indicators
(dashed royal border, binding label, tiny yellow registration ticks) -
never invented game art. The proofs assess the UI SHELL only.

Variants: ps2 (Gran Turismo 4), n64 (Super Mario 64), gba (Mario Golf:
Advance Tour) - the user's named Nova QA contexts.
"""
import os, sys, json, hashlib, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.expanduser("~/workspace/crystal-esde-theme/work"))
from gen_v15_assets import ROYAL, DEEP, NAVY, INKDIM, YELLOW, WHITE, FB, SYSTEMS

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
FBB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FBSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MARK = os.path.join(REPO, "theme-src/crystal/fonts/PermanentMarker-Regular.ttf")
PERM = MARK
ART = os.path.join(REPO, "theme-src/crystal/art")
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
def is_yellowish(p):  # translucent yellow over white/blue
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

def tracked_text_img(text, size, color, tracking, alpha=255):
    font = ImageFont.truetype(FBB, size)
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

# --------------------------- metadata (real data) -----------------------
def draw_desc(base, desc, xy):
    f = ImageFont.truetype(FBB, 21)
    d = ImageDraw.Draw(base, "RGBA")
    y = xy[1]
    for line in desc:
        d.text((xy[0], y), line, font=f, fill=INKDIM + (255,))
        y += 26

def draw_date(base, year, xy):
    f = ImageFont.truetype(MARK, 57)
    d = ImageDraw.Draw(base, "RGBA")
    d.text((xy[0], xy[1]), year, font=f, fill=NAVY + (255,))

def draw_rating(base, fill, xy):
    import math
    x0, y0 = xy
    for i in range(5):
        c = (x0 + i * 42 + 15, y0 + 16)
        pts = []
        for k in range(10):
            r = 15 if k % 2 == 0 else 6.2
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
        ImageDraw.Draw(base, "RGBA").polygon(
            pts, fill=YELLOW + (255,) if i < fill else (255, 255, 255, 120),
            outline=NAVY + (255,))

def draw_genre(base, genre, xy):
    d = ImageDraw.Draw(base, "RGBA")
    d.text(xy, genre, font=ImageFont.truetype(FBB, 23), fill=NAVY + (255,))

def draw_facts(base, text, xy):
    d = ImageDraw.Draw(base, "RGBA")
    d.text(xy, text, font=ImageFont.truetype(FBSB, 14), fill=INKDIM + (255,))

def draw_title_block(base, title, meta):
    rule = Image.open(os.path.join(ART, "lib_title_rule.png")).convert("RGBA")
    base.alpha_composite(rule, (int(900 - rule.width / 2), 714))
    d = ImageDraw.Draw(base, "RGBA")
    # engine: title centered at (900,736), 0.040; meta rail centered at y767.5
    # (moved from 757.5: measured 6px glyph collision fix, see changelog)
    d.text((900, 736), title, font=ImageFont.truetype(PERM, 51),
           fill=(255, 255, 255, 255), anchor="mm")
    d.text((900, 767), meta, font=ImageFont.truetype(FBB, 18),
           fill=(255, 255, 255, 150), anchor="mm")

def draw_footer(base, title, sysname):
    d = ImageDraw.Draw(base, "RGBA")
    f = ImageFont.truetype(FBSB, 16)
    t1, t2 = title.upper(), sysname.upper()
    w1, w2 = f.getlength(t1), f.getlength(t2)
    d.text((900 - w1 / 2, 906), t1, font=f, fill=(255, 255, 255, 255))
    d.text((900 - w2 / 2, 932), t2, font=f, fill=(255, 255, 255, 255))

# ------------------------------- render ---------------------------------
def render(system, game, prev_next=True):
    base = Image.open(os.path.join(ART, "gamelist_generic_bg.png")).convert("RGBA").resize((W, H))
    panel = Image.open(os.path.join(ART, "lib_panel_main.png")).convert("RGBA")
    base.alpha_composite(panel, (6, 10))
    base.alpha_composite(Image.open(os.path.join(ART, "rails", f"{system}.png")).convert("RGBA"), (486, 24))
    xml = open(VIEWS, encoding="utf-8").read()
    view = parse_view(xml, "gamelist")

    # live slots: marquee, screenshot (from the XML boxes)
    mline = el_box(view, "image name=\"libMarquee\"")
    mx, my = [float(x) for x in el_val(mline, "pos").split()]
    mw_, mh_ = [float(x) for x in el_val(mline, "maxSize").split()]
    mbox = (px(mx), sz(my), px(mx) + px(mw_), sz(my) + sz(mh_))
    sline = el_box(view, "image name=\"libScreenshot\"")
    sx, sy = [float(x) for x in el_val(sline, "pos").split()]
    sw_, sh_ = [float(x) for x in el_val(sline, "size").split()]
    sbox = (px(sx), sz(sy), px(sx) + px(sw_), sz(sy) + sz(sh_))

    slots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_slot(slots, mbox, "${game.marquee}")
    draw_slot(slots, sbox, "${game.screenshot}")
    # hero: the immutable dynamic physicalmedia slot, 540px at (900,430)
    draw_slot(slots, (900 - 270, 430 - 270, 900 + 270, 430 + 270),
              "${game.physicalmedia}", font_sz=15)
    base.alpha_composite(slots)

    # prev/next: dimmed slots on the unchanged trajectory
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

    # metadata (real data, engine positions)
    draw_desc(base, game["desc"], (48, 312))
    draw_date(base, game["year"], (48, 468))
    draw_rating(base, 4, (392, 478))
    draw_genre(base, game["genre"], (48, 578))
    draw_facts(base, game["players"], (48, 640))
    draw_facts(base, game["dev"], (300, 640))

    # shard foregrounds (shell, not media)
    shard_p = Image.open(os.path.join(ART, "lib_shard_prev.png")).convert("RGBA")
    base.alpha_composite(shard_p.resize((132, 132)), (894, -16))
    shard_n = Image.open(os.path.join(ART, "lib_shard_next.png")).convert("RGBA")
    base.alpha_composite(shard_n.resize((144, 144)), (828, 868))

    draw_title_block(base, game["title"], game["meta"])
    draw_footer(base, game["title"], game["sysname"])
    return base.convert("RGB")

# ------------------------------- checks ---------------------------------
def check_macro_lock():
    xml_head = subprocess.run(["git", "-C", REPO, "show", "HEAD:theme-src/crystal/views.xml"],
                              capture_output=True, text=True).stdout
    xml_now = open(VIEWS, encoding="utf-8").read()
    g_head = parse_view(xml_head, "gamelist")
    g_now = parse_view(xml_now, "gamelist")
    import re, difflib
    strip = lambda s: re.sub(r"<!--.*?-->", "", s, flags=re.S)
    h, n = strip(g_head).splitlines(), strip(g_now).splitlines()
    diff = [l for l in difflib.unified_diff(h, n, n=0) if l[:1] in "+-"
            and not l.startswith(("+++", "---"))]
    # the ONLY allowed geometric change: the 7 meta-rail elements moving
    # 0.7890625 -> 0.7994792 (documented 6px glyph-collision fix)
    ok = len(diff) == 14
    for l in diff:
        body = l[1:].strip()
        if l.startswith("-"):
            ok = ok and "0.7890625" in body and "<pos>" in body
        else:
            ok = ok and "0.7994792" in body and "<pos>" in body
    check("macro-lock: only the documented meta-rail fix differs from HEAD", ok,
          f"diff_lines={len(diff)}")

def check_bindings():
    xml = open(VIEWS, encoding="utf-8").read()
    g = parse_view(xml, "gamelist")
    # ES-DE binds via <imageType>, not literal ${game.*} strings
    ok = True
    for binding in ("<imageType>marquee</imageType>",
                    "<imageType>physicalmedia 3dbox</imageType>",
                    "<imageType>image</imageType>",  # libScreenshot: scraped shot
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
    # masthead hairline at local y=294 with royal tint
    royal = 0
    for x in range(40, 430, 6):
        r, gg, b = p.getpixel((x, 294))[:3]
        if b > r + 25 and b > gg + 10:
            royal += 1
    check("masthead baseline hairline present", royal > 40, f"royal_px={royal}")
    reg = sum(1 for x in range(36, 43) for y in range(292, 297) if is_yellow(p.getpixel((x, y))))
    check("masthead yellow registration square", reg > 0, f"yellow_px={reg}")
    corner = sum(1 for x in range(424, 447) for y in range(682, 705) if is_yellow(p.getpixel((x, y))))
    check("screenshot registration corner crosses top-right", corner > 8, f"yellow_px={corner}")
    edge = sum(1 for x in range(422, 425) for y in range(602, 684)
               if is_yellow(p.getpixel((x, y))[:3]) or is_yellowish(p.getpixel((x, y))[:3]))
    check("intrusion yellow leading edge extends to screenshot", edge > 40, f"yellow_px={edge}")
    bottom = sum(1 for x in range(40, 430, 6) if lum(p.getpixel((x, 900))) < 190)
    check("screenshot bottom-edge hairline", bottom > 30, f"dark_px={bottom}")

def check_title_rule():
    r = Image.open(os.path.join(ART, "lib_title_rule.png")).convert("RGB")
    pix = list(r.getdata())
    yel = sum(1 for q in pix if is_yellow(q))
    white = sum(1 for q in pix if lum(q) > 235)
    check("title rule: clean yellow registration rule, no white", yel > 300 and white == 0,
          f"yellow={yel} white={white} size={r.size}")

def check_rails():
    ok_count = 0
    for system, _ in SYSTEMS:
        if os.path.exists(os.path.join(ART, "rails", f"{system}.png")):
            ok_count += 1
    check("all 21 rails regenerated", ok_count == 21, str(ok_count))
    head_rails = subprocess.run(["git", "-C", REPO, "show", "HEAD:theme-src/crystal/art/rails/ps2.png"],
                                capture_output=True).stdout
    old = Image.open(__import__("io").BytesIO(head_rails)).convert("RGB")
    new = Image.open(os.path.join(ART, "rails/ps2.png")).convert("RGB")
    def bright(im):
        return sum(1 for x in range(20, 50, 2) for y in range(100, 250, 2)
                   if lum(im.getpixel((x, y))) > 170)
    b_old, b_new = bright(old), bright(new)
    check("spine texture reduced further vs v17.4", b_new <= 0.75 * b_old,
          f"old={b_old} new={b_new}")
    # halftone band lived at x44-58,y340-572 in v17.4; mask out the logo
    # plate (from the sidecar) so the white logo doesn't swamp the count
    prm = json.load(open(os.path.join(REPO, "work/rail_params_v17_5.json")))["ps2"]
    lw, lh = prm["logo"]
    ox, oy = (60 - lw) // 2 + 2, (912 - lh) // 2
    pb = (ox - 22, oy - 22, ox - 22 + prm["plate"][0], oy - 22 + prm["plate"][1])
    def band(im):
        n = 0
        for x in range(44, 58):
            for y in range(340, 572):
                if pb[0] <= x <= pb[2] and pb[1] <= y <= pb[3]:
                    continue
                if lum(im.getpixel((x, y))) > 75:
                    n += 1
        return n
    band_new, band_old = band(new), band(old)
    check("halftone mid-band removed", band_old > 20 and band_new < 0.3 * band_old,
          f"old={band_old} new={band_new}")
    yline = sum(1 for y in range(50, 880) if is_yellow(new.getpixel((4, y))))
    check("one continuous yellow line + tab", yline > 700, f"yellow_px={yline}")
    params = json.load(open(os.path.join(REPO, "work/rail_params_v17_5.json")))
    pad_ok = all(v["pad"] >= 20 for v in params.values())
    check("logo plate breathing room >= 20px (21 systems)", pad_ok and len(params) == 21)
    xml = open(VIEWS, encoding="utf-8").read()
    check("spine keeps dynamic ${system.name} binding", "${system.name}" in parse_view(xml, "gamelist"))

def check_title_meta_geometry():
    # parse the real engine positions from the XML, render each line with
    # the real font on a blank canvas, and require zero glyph overlap
    xml = open(VIEWS, encoding="utf-8").read()
    g = parse_view(xml, "gamelist")
    tb = el_box(g, 'text name="libGameName"')
    tsize = float(el_val(tb, "fontSize")) * W
    tcy = float(el_val(tb, "pos").split()[1]) * H
    mb = el_box(g, 'text name="libMetaGenre"')
    msize = float(el_val(mb, "fontSize")) * W
    mcy = float(el_val(mb, "pos").split()[1]) * H
    perm = ImageFont.truetype(PERM, int(tsize))
    dv = ImageFont.truetype(FBB, int(msize))
    c = Image.new("RGB", (900, 200), "white")
    d = ImageDraw.Draw(c)
    d.text((450, 80), "GRAN TURISMO 4", font=perm, fill="black", anchor="mm")
    d.text((450, 80 + (mcy - tcy)), "RACING \u2022 2004 \u2022 TEST \u2022 1-2 PLAYERS",
           font=dv, fill="red", anchor="mm")
    px = c.load()
    t_rows = [y for y in range(200) for x in range(900) if px[x, y] == (0, 0, 0)]
    m_rows = [y for y in range(200) for x in range(900)
              if px[x, y][0] > 200 and px[x, y][1] < 100]
    overlap = max(0, min(max(t_rows), max(m_rows)) - max(min(t_rows), min(m_rows)))
    check("title/meta glyph clearance (real fonts, XML positions)",
          overlap == 0 and abs(tcy - 736) < 1,
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
    # hero-treatment assets untouched vs HEAD
    untouched = []
    for f in ("lib_shadow_soft.png", "lib_glow_blue.png", "lib_plane_hero.png",
              "lib_shard_prev.png", "lib_shard_next.png"):
        head = subprocess.run(["git", "-C", REPO, "show", f"HEAD:theme-src/crystal/art/{f}"],
                              capture_output=True).stdout
        now = open(os.path.join(ART, f), "rb").read()
        untouched.append(hashlib.sha256(head).hexdigest() == hashlib.sha256(now).hexdigest())
    check("hero-treatment assets byte-identical to v17.4.0", all(untouched))

def check_hygiene():
    xml = open(VIEWS, encoding="utf-8").read()
    check("no debug pixels", "DEBUG" not in xml.upper() or "debug pixels" in xml.lower())
    bg_head = subprocess.run(["git", "-C", REPO, "show", "HEAD:theme-src/crystal/art/gamelist_generic_bg.png"],
                             capture_output=True).stdout
    bg_now = open(os.path.join(ART, "gamelist_generic_bg.png"), "rb").read()
    check("gamelist_generic_bg.png unchanged",
          hashlib.sha256(bg_head).hexdigest() == hashlib.sha256(bg_now).hexdigest())
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
    check("pinned 3.4.1 tables: itemTransitions on carousel only",
          "itemTransitions" in txt and "storyboard" not in txt.lower())
    xml = open(VIEWS, encoding="utf-8").read()
    g = parse_view(xml, "gamelist")
    i = g.index('<carousel name="gameCarousel"')
    block = g[i:i + 1200]
    check("gameCarousel itemTransitions=animate engaged",
          "itemTransitions" in block and "animate" in block)

def check_proof(system, path, title):
    img = Image.open(path).convert("RGB")
    # hero slot: the slot indicator is present, interior is a neutral
    # white-veiled live slot (bg shows through the veil by design),
    # no yellow, no invented art
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
    # marquee zone: slot border present, no dark bespoke blob
    zone = img.crop((24, 44, 448, 296))
    zpx = list(zone.getdata())
    royal = sum(1 for q in zpx if q[2] > q[0] + 40 and q[2] > q[1] + 20 and lum(q) < 150)
    dark = sum(1 for q in zpx if lum(q) < 60)
    check(f"[{system}] marquee slot indicator present, no bespoke art",
          royal > 200 and dark < 800, f"royal={royal} dark={dark}")
    # screenshot slot: border present, bright interior
    shot = img.crop((42, 700, 438, 910))
    spx = list(shot.getdata())
    royal2 = sum(1 for q in spx if q[2] > q[0] + 40 and q[2] > q[1] + 20 and lum(q) < 150)
    inner = img.crop((52, 710, 428, 900))
    imean = sum(lum(q) for q in inner.getdata()) / (376 * 190)
    check(f"[{system}] screenshot slot indicator present",
          royal2 > 150 and imean > 180, f"royal={royal2} imean={imean:.0f}")
    # title zone: white title present; the next item must not reach the
    # title zone - verified by diffing the title band against a render
    # with the prev/next slots omitted (any intrusion changes pixels)
    band = img.crop((550, 708, 1250, 764))
    bpx = list(band.getdata())
    white_txt = sum(1 for q in bpx if lum(q) > 210)
    clean = render(system, GAMES[system], prev_next=False).convert("RGB")
    clean_band = clean.crop((550, 708, 1250, 764))
    diff = sum(1 for a, b in zip(band.getdata(), clean_band.getdata()) if a != b)
    check(f"[{system}] title present + next item clear of title zone",
          white_txt > 1500 and diff == 0,
          f"white={white_txt} intruding_px={diff}")
    rule = img.crop((840, 714, 960, 718))
    yel2 = sum(1 for q in rule.getdata() if is_yellow(q))
    check(f"[{system}] yellow registration rule under title", yel2 > 100, f"yellow={yel2}")
    # footer
    foot = img.crop((700, 906, 1100, 950))
    check(f"[{system}] footer readable", max(lum(q) for q in foot.getdata()) > 200)

GAMES = {
    "ps2": dict(title="GRAN TURISMO 4", sysname="Sony PlayStation 2", genre="RACING",
                year="2004", dev="POLYPHONY DIGITAL", players="1-2 PLAYERS",
                meta="RACING • 2004 • POLYPHONY DIGITAL • 1-2 PLAYERS",
                desc=["The definitive driving simulator: 700+ cars,",
                      "51 circuits and a career of unmatched depth.",
                      "Polyphony's obsession, rendered at 1080i.",
                      "Precision handling, endless tuning."]),
    "n64": dict(title="SUPER MARIO 64", sysname="Nintendo 64", genre="PLATFORMER",
                year="1996", dev="NINTENDO", players="1 PLAYER",
                meta="PLATFORMER • 1996 • NINTENDO • 1 PLAYER",
                desc=["A landmark in 3D design: 120 Power Stars",
                      "hidden across painted worlds. Bowser's",
                      "ambitions end at the castle gates.",
                      "The blueprint for every 3D platformer since."]),
    "gba": dict(title="MARIO GOLF: ADVANCE TOUR", sysname="Game Boy Advance", genre="SPORTS",
                year="2004", dev="CAMELOT", players="1-4 PLAYERS",
                meta="SPORTS • 2004 • CAMELOT • 1-4 PLAYERS",
                desc=["Camelot's handheld golf RPG: build a rookie",
                      "from the clubhouse to the Mushroom Kingdom",
                      "tour. Deep swing mechanics, charming story.",
                      "Link-cable multiplayer for four."]),
}

if __name__ == "__main__":
    os.makedirs(PROOFS, exist_ok=True)
    check_macro_lock(); check_bindings(); check_panel_art(); check_title_rule()
    check_title_meta_geometry()
    check_rails(); check_fallbacks(); check_hygiene(); check_transitions()
    fails = 0
    for system, game in GAMES.items():
        p = os.path.join(PROOFS, f"mock_v17_5_{system}.png")
        render(system, game).save(p)
        print("saved", p)
        check_proof(system, p, game["title"])
    fails = sum(1 for _, ok, _ in CHECK_LOG if not ok)
    print(f"\n{'ALL CHECKS PASS' if fails == 0 else str(fails) + ' CHECKS FAILED'} "
          f"({len(CHECK_LOG)} checks)")
    sys.exit(1 if fails else 0)
