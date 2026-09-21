#!/usr/bin/env python3
"""Crystal v18.4.4 SCHEME-AWARE VISUAL PROOF HARNESS (VM-ONLY, NEVER SHIPS).

The v17.9 mock drew empty slots, so the screens all looked identical and
no real art-direction review was possible. This harness composites
temporary abstract proxy assets (work/proof_assets/) INTO the real XML
geometry — marquee, screenshot, hero, previous, next — so the screen
finally looks like a real product and the SHELL can be judged.

v18.4.4 changes: the libMarqueeTitle ghost-text fallback is GONE (no
white backing renders anywhere now); the screenshot is a true 4:3
maxSize stage (aspect preserved, never stretched); a libVideo layer
sits one z above it with <delay>5</delay> (screenshot first, video
after ~5s) - marked with a mock-only tag since PIL cannot play video.

Proof assets are abstract and deliberately unlabeled: they stand in for
scraped content only. They are NEVER referenced from theme-src/ and
never enter the production ZIP.

Output: work/proofs/v18_4_proof_{ps2,n64,3ds,psx_nomq}.png (1280x960
PIL renders, never ES-DE screenshots).
"""
import os, sys, math, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
sys.path.insert(0, os.path.join(REPO, "work"))
import mock_gamelist_v17_9 as M
from gen_v15_assets import ROYAL, DEEP, NAVY, INKDIM, WHITE

ART = os.path.join(REPO, "theme-src/crystal/art")
PA = os.path.join(REPO, "work/proof_assets")
VIEWS = os.path.join(REPO, "theme-src/crystal/views.xml")
PROOFS = os.path.join(REPO, "work/proofs")
W, H = 1280, 960
px, sz, fs = M.px, M.sz, M.fs
el_box, el_val, parse_view = M.el_box, M.el_val, M.parse_view
BOLD, REG = M.BOLD, M.REG
wrap = M.wrap
fit_rect = M.fit_rect

def _xml_font(name, view, default_path):
    b = el_box(view, name)
    rel = el_val(b, "fontPath").lstrip("./") if "<fontPath>" in b else default_path
    return os.path.join(REPO, "theme-src/crystal", rel)

def _inkdim():
    xml = open(os.path.join(REPO, "theme-src/crystal/variables.xml"),
               encoding="utf-8").read()
    m = re.search(r"<crystalInkDim>([0-9A-Fa-f]{6})</crystalInkDim>", xml)
    h = m.group(1)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

INKDIM = _inkdim()  # XML-driven: follows crystalInkDim (v18.2.1 darkened)

# --- v18.3.0: color-scheme support -------------------------------------
def palette(scheme):
    """Resolve the full palette the way the engine does: variables.xml
    base, then the selected <colorScheme> block's <variables> overrides."""
    pal = {}
    xml = open(os.path.join(REPO, "theme-src/crystal/variables.xml"),
               encoding="utf-8").read()
    for m in re.finditer(r"<([a-zA-Z]+)>([0-9A-Fa-f.]+)</\1>", xml):
        pal[m.group(1)] = m.group(2).strip()
    xml = open(os.path.join(REPO, "theme-src/crystal/colorschemes.xml"),
               encoding="utf-8").read()
    blk = re.search(r'<colorScheme name="%s">\s*<variables>(.*?)</variables>\s*</colorScheme>'
                    % scheme, xml, re.S).group(1)
    for m in re.finditer(r"<([a-zA-Z]+)>([0-9A-Fa-f.]+)</\1>", blk):
        pal[m.group(1)] = m.group(2).strip()
    return pal

def HX(h):
    h = h.strip()
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def HXA(h):
    h = h.strip()
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))

def tint(im, hex6):
    """ES-DE image <color> multiply tint (RGBA-safe)."""
    t = HX(hex6)
    if t == (255, 255, 255):
        return im.convert("RGBA")
    im = im.convert("RGBA")
    out = ImageChops.multiply(im, Image.new("RGBA", im.size, t + (255,)))
    out.putalpha(im.split()[3])
    return out

def cover_into(im, box):
    """Crop-to-fill `box` (x0,y0,x1,y1) with the image."""
    x0, y0, x1, y1 = [int(round(q)) for q in box]
    bw, bh = x1 - x0, y1 - y0
    sc = max(bw / im.width, bh / im.height)
    r = im.resize((int(im.width * sc + 0.5), int(im.height * sc + 0.5)),
                  Image.LANCZOS)
    ox, oy = (r.width - bw) // 2, (r.height - bh) // 2
    return r.crop((ox, oy, ox + bw, oy + bh))

def contain_into(im, box):
    """Fit `box` with the image (aspect preserved), return (layer, topleft)."""
    x0, y0, x1, y1 = [int(round(q)) for q in box]
    bw, bh = x1 - x0, y1 - y0
    sc = min(bw / im.width, bh / im.height)
    r = im.resize((int(im.width * sc + 0.5), int(im.height * sc + 0.5)),
                  Image.LANCZOS)
    return r, (x0 + (bw - r.width) // 2, y0 + (bh - r.height) // 2)

def hero_footprint(kind, cy=448):
    # engine truth: itemSize 240x240, selected itemScale 2.25 -> 540 box,
    # centred on the carousel's selected slot (XML-driven at call site)
    return (900 - 270, cy - 270, 900 + 270, cy + 270)

def render(v, scheme="light"):
    xml = open(VIEWS, encoding="utf-8").read()
    view = parse_view(xml, "gamelist")
    pal = palette(scheme)
    base = tint(Image.open(os.path.join(ART, "gamelist_generic_bg.png")), pal["libBgTint"]).resize((W, H))
    grad = Image.open(os.path.join(ART, "lib_bottom_gradient.png")).convert("RGBA")
    g = el_box(view, 'image name="libBottomGradient"')
    gx, gy = [float(x) for x in el_val(g, "pos").split()]
    gw, gh = [float(x) for x in el_val(g, "size").split()]
    base.alpha_composite(grad.resize((int(px(gw)), int(sz(gh)))),
                         (int(px(gx)), int(sz(gy))))
    base.alpha_composite(tint(Image.open(os.path.join(ART, "lib_panel_main.png")), pal["panelTint"]), (6, 10))
    base.alpha_composite(tint(Image.open(os.path.join(ART, "rails", f"{v['system']}.png")), pal["railTint"]), (486, 24))

    # v18.4.4: the libMarqueeTitle fallback is GONE (user directive -
    # no ghost text, no white backing). The marquee zone is clean empty
    # whitespace when art is missing; nothing renders here. (The old
    # z19 opaque-white block + Anton masthead were removed outright.)
    d = ImageDraw.Draw(base, "RGBA")

    # marquee: proxy asset fitted (contain) into the invisible region.
    # ENGINE TRUTH: maxSize-fit, left edge at the zone's left (origin
    # 0 0.5 puts the art's left edge at pos.x), vertically centred -
    # NOT horizontally centred.
    m = el_box(view, 'image name="libMarquee"')
    mx, my = [float(x) for x in el_val(m, "pos").split()]
    mw, mh = [float(x) for x in el_val(m, "maxSize").split()]
    zone = (px(mx), sz(my) - sz(mh) / 2, px(mx) + px(mw), sz(my) + sz(mh) / 2)
    if v.get("marquee"):
        mq = Image.open(os.path.join(PA, v["marquee"])).convert("RGBA")
        zw, zh = zone[2] - zone[0], zone[3] - zone[1]
        sc = min(zw / mq.width, zh / mq.height)
        rw, rh = int(mq.width * sc + 0.5), int(mq.height * sc + 0.5)
        mq_r = mq.resize((rw, rh), Image.LANCZOS)
        mq_xy = (int(zone[0]), int(zone[1] + (zh - rh) / 2))
        # v18.4.4: no fallback layer behind the art any more, so the
        # proxy composites straight onto the page (production marquee
        # art is opaque scraper media).
        base.alpha_composite(mq_r, mq_xy)

    # left-column text at real XML geometry
    dbox = el_box(view, 'text name="libDesc"')
    fz_desc = float(el_val(dbox, "fontSize"))
    ls = float(el_val(dbox, "lineSpacing")) if "<lineSpacing>" in dbox else 1.5
    f_desc = ImageFont.truetype(_xml_font('text name="libDesc"', view, REG),
                                int(round(fs(fz_desc))))
    desc_step = int(round(fs(fz_desc) * ls))
    dx, dy = [float(x) for x in el_val(dbox, "pos").split()]
    dw, dh = [float(x) for x in el_val(dbox, "size").split()]
    max_lines = max(1, int(sz(dh) // desc_step))
    y = int(sz(dy))
    for line in wrap(v["desc"], f_desc, px(dw))[:max_lines]:
        d.text((int(px(dx)), y), line, font=f_desc, fill=HX(pal["crystalInkDim"]) + (255,))
        y += desc_step
    yb = el_box(view, 'datetime name="libYear"')
    yx, yy = [float(x) for x in el_val(yb, "pos").split()]
    fz_year = float(el_val(yb, "fontSize"))
    d.text((px(yx), sz(yy)), v["year"], font=ImageFont.truetype(BOLD, int(round(fs(fz_year)))),
           fill=HX(pal["crystalDeep"]) + (255,))
    rb = el_box(view, 'rating name="libRating"')
    rrx, rry = [float(q) for q in el_val(rb, "pos").split()]
    for i in range(5):
        cx, cy = px(rrx) + 14 + i * 28, sz(rry) + 14
        pts = []
        for k in range(10):
            r = 11 if k % 2 == 0 else 4.6
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, fill=(18, 58, 178, 255) if i < v["stars"] else (10, 47, 160, 90),
                  outline=NAVY + (255,))
    b = el_box(view, 'text name="libGenre"')
    gx, gy = [float(q) for q in el_val(b, "pos").split()]
    d.text((px(gx), sz(gy)), v["genre"].upper(),
           font=ImageFont.truetype(BOLD, int(round(fs(0.022)))), fill=HX(pal["crystalDeep"]) + (255,))
    pb = el_box(view, 'text name="libPlayers"')
    fz_micro = float(el_val(pb, "fontSize"))
    f_micro = ImageFont.truetype(_xml_font('text name="libPlayers"', view, REG),
                                 int(round(fs(fz_micro))))
    px0, py0 = [float(q) for q in el_val(pb, "pos").split()]
    db = el_box(view, 'text name="libDev"')
    dx0, dy0 = [float(q) for q in el_val(db, "pos").split()]
    d.text((px(px0), sz(py0)), v["players"].upper(), font=f_micro, fill=HX(pal["crystalInkDim"]) + (255,))
    dev_w = float(el_val(db, "size").split()[0]) * W
    for i, ln in enumerate(wrap(v["dev"].upper(), f_micro, dev_w)[:2]):
        d.text((px(dx0), sz(dy0) + i * 26), ln, font=f_micro, fill=HX(pal["crystalInkDim"]) + (255,))

    # screenshot: v18.4.4 true-4:3 stage. ENGINE TRUTH: maxSize-fit
    # (aspect preserved, never stretched), origin 0 0.5 about the region
    # centre, so the proxy is contain-fitted and centred - NOT
    # cover-cropped like the old strip.
    s = el_box(view, 'image name="libScreenshot"')
    sx, sy = [float(x) for x in el_val(s, "pos").split()]
    sw, sh = [float(x) for x in el_val(s, "maxSize").split()]
    sbox = (px(sx), sz(sy) - sz(sh) / 2, px(sx) + px(sw), sz(sy) + sz(sh) / 2)
    shot = Image.open(os.path.join(PA, v["shot"])).convert("RGBA")
    cov, cxy = contain_into(shot, sbox)
    base.alpha_composite(cov, cxy)

    # video layer (libVideo, z21): the engine holds the screenshot for
    # <delay>5</delay> then fades the game video in over this same stage.
    # A static PIL proof cannot play video, so this tiny mock-only tag
    # marks the stage - it is NOT part of the theme.
    vd = el_box(view, 'video name="libVideo"')
    vx, vy = [float(x) for x in el_val(vd, "pos").split()]
    vw, vh = [float(x) for x in el_val(vd, "maxSize").split()]
    vtag = "\u25b6 VIDEO \u00b7 5s"
    f_tag = ImageFont.truetype(REG, 20)
    twd = f_tag.getlength(vtag)
    tx0 = int(px(vx) + px(vw) - twd - 28)
    ty0 = int(sz(vy) + sz(vh) / 2 - 22)
    d.rounded_rectangle([tx0, ty0, tx0 + int(twd) + 20, ty0 + 30], radius=8,
                       fill=(10, 47, 160, 210))
    d.text((tx0 + 10, ty0 + 4), vtag, font=f_tag, fill=(255, 255, 255, 255))

    # hero stage: plane (resized to its XML size), wash, glow, shadow
    pl = el_box(view, 'image name="libPlaneHero"')
    px0, py0 = [float(x) for x in el_val(pl, "pos").split()]
    pw, ph = [float(x) for x in el_val(pl, "size").split()]
    porg = el_val(pl, "origin").split()
    plane = tint(Image.open(os.path.join(ART, "lib_plane_hero.png")), pal["planeTint"]) \
        .resize((int(px(pw)), int(sz(ph))), Image.LANCZOS)
    base.alpha_composite(plane,
                         (int(px(px0) - (px(pw) / 2 if porg[0] == "0.5" else 0)),
                          int(sz(py0) - (sz(ph) / 2 if porg[1] == "0.5" else 0))))
    hw = el_box(view, 'image name="libHeroWash"')
    hx, hy = [float(x) for x in el_val(hw, "pos").split()]
    hww, hwh = [float(x) for x in el_val(hw, "size").split()]
    base.alpha_composite(tint(Image.open(os.path.join(ART, "lib_hero_wash.png")), pal["heroWashTint"])
                         .resize((int(px(hww)), int(sz(hwh)))),
                         (int(px(hx) - px(hww) / 2), int(sz(hy) - sz(hwh) / 2)))
    gl = el_box(view, 'image name="libSelectedGlowBlue"')
    gx2, gy2 = [float(x) for x in el_val(gl, "pos").split()]
    gw2, gh2 = [float(x) for x in el_val(gl, "size").split()]
    glow = Image.open(os.path.join(ART, "lib_glow_blue.png")).convert("RGBA") \
        .resize((int(px(gw2)), int(sz(gh2))))
    glow.putalpha(glow.split()[3].point(lambda a: int(a * float(pal["glowOpacity"]))))
    base.alpha_composite(glow, (int(px(gx2) - px(gw2) / 2), int(sz(gy2) - sz(gh2) / 2)))
    sh2 = el_box(view, 'image name="libSelectedShadow"')
    qx, qy = [float(x) for x in el_val(sh2, "pos").split()]
    qw, qh = [float(x) for x in el_val(sh2, "size").split()]
    sh_op = float(el_val(sh2, "opacity"))
    shadow = Image.open(os.path.join(ART, "lib_shadow_soft.png")).convert("RGBA") \
        .resize((int(px(qw)), int(sz(qh))))
    shadow.putalpha(shadow.split()[3].point(lambda a: int(a * sh_op)))
    base.alpha_composite(shadow, (int(px(qx) - px(qw) / 2), int(sz(qy) - sz(qh) / 2)))

    # hero proxy: contained in the hero footprint, centred on the
    # carousel's real selected slot (XML-driven)
    cb0 = el_box(view, 'carousel name="gameCarousel"')
    sel_cy = sz(float(el_val(cb0, "pos").split()[1]))
    hb = hero_footprint(v["hero"], sel_cy)
    hero_im = Image.open(os.path.join(PA, v["media"])).convert("RGBA")
    hr, hxy = contain_into(hero_im, hb)
    base.alpha_composite(hr, hxy)

    # prev/next: engine truth - itemSize 240 box, unfocusedItemOpacity
    # 0.45, unfocusedItemSaturation 0.5, unfocusedItemDimming ~0.6.
    # Positions from the real carousel element (pitch = size.y / 3).
    from PIL import ImageEnhance
    cb = el_box(view, 'carousel name="gameCarousel"')
    ccx = float(el_val(cb, "pos").split()[0])
    cy0 = float(el_val(cb, "pos").split()[1])
    csh = float(el_val(cb, "size").split()[1])
    pitch = sz(csh) / 3.0
    dim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for key, cy in (("prev", sz(cy0) - pitch), ("next", sz(cy0) + pitch)):
        pm = Image.open(os.path.join(PA, v["media"])).convert("RGBA")
        pr, pxy = contain_into(pm, (px(ccx) - 120, cy - 120, px(ccx) + 120, cy + 120))
        pr = ImageEnhance.Color(pr).enhance(0.5)
        pr = ImageEnhance.Brightness(pr).enhance(0.62)
        pr.putalpha(pr.split()[3].point(lambda a: int(a * 0.45)))
        dim.alpha_composite(pr, pxy)
    base.alpha_composite(dim)

    # foreground shards at real XML geometry
    for ename in ('image name="libShardPrev"', 'image name="libShardNext"'):
        b = el_box(view, ename)
        bx, by = [float(x) for x in el_val(b, "pos").split()]
        bw2, bh2 = [float(x) for x in el_val(b, "size").split()]
        aname = "lib_shard_prev.png" if "Prev" in ename else "lib_shard_next.png"
        sh = Image.open(os.path.join(ART, aname)).convert("RGBA").resize((int(px(bw2)), int(sz(bh2))))
        base.alpha_composite(sh, (int(px(bx)), int(sz(by))))

    # title block: rule asset, title, rail
    rule = Image.open(os.path.join(ART, "lib_title_rule.png")).convert("RGBA")
    base.alpha_composite(rule, (int(900 - rule.width / 2), 711))
    t = el_box(view, 'text name="libGameName"')
    tx, ty = [float(x) for x in el_val(t, "pos").split()]
    tw, th = [float(x) for x in el_val(t, "size").split()]
    fz_title = float(el_val(t, "fontSize"))
    f_title = ImageFont.truetype(BOLD, int(round(fs(fz_title))))
    title = v["title"].upper()
    if f_title.getlength(title) <= px(tw):
        d.text((px(tx), sz(ty)), title, font=f_title, fill=HX(pal["titleInk"]) + (255,),
               anchor="mm")
    else:
        for i, ln in enumerate(wrap(title, f_title, px(tw))[:2]):
            d.text((px(tx), sz(ty) + (i - 0.5) * int(round(fs(fz_title))) * 1.15),
                   ln, font=f_title, fill=HX(pal["titleInk"]) + (255,), anchor="mm")
    f_rail = ImageFont.truetype(REG, int(round(fs(0.0145))))
    rail = [("libMetaGenre", v["genre"].upper()), ("libMetaSep1", "\u2022"),
            ("libMetaYear", v["year"]), ("libMetaSep2", "\u2022"),
            ("libMetaPlayers", v["players"].upper())]
    for ename, txt in rail:
        tag = "datetime" if "Year" in ename else "text"
        b = el_box(view, f'{tag} name="{ename}"')
        bx, by = [float(x) for x in el_val(b, "pos").split()]
        d.text((px(bx), sz(by)), txt, font=f_rail, fill=HXA(pal["railInk"]), anchor="mm")
    f_foot = ImageFont.truetype(REG, int(round(fs(0.0135))))
    d.text((640, 915), "A PLAY \u2022 B BACK", font=f_foot, fill=HXA(pal["footerInk"]), anchor="mm")
    return base.convert("RGB")

VARIANTS = {
    "ps2": dict(system="ps2", title="GRAN TURISMO 4", genre="RACING", year="2004",
                dev="POLYPHONY DIGITAL", players="1\u20132 PLAYERS", stars=5,
                hero="disc", marquee="marquee_wide.png", shot="screenshot_a.png",
                media="disc_hero.png", prev="disc_prev.png", next="disc_next.png",
                desc="The definitive driving simulator: over 700 cars and 50 tracks. Polyphony Digital's obsessive attention to vehicle dynamics, now sharper than ever."),
    "n64": dict(system="n64", title="SUPER MARIO 64", genre="PLATFORMER", year="1996",
                dev="NINTENDO", players="1 PLAYER", stars=5,
                hero="cartridge", marquee="marquee_square.png", shot="screenshot_b.png",
                media="cart_hero.png", prev="cart_prev.png", next="cart_next.png",
                desc="Mario's groundbreaking leap into 3D. Explore 15 courses inside Princess Peach's castle, collecting 120 Power Stars to confront Bowser."),
    "3ds": dict(system="n3ds", title="THE LEGEND OF ZELDA: OCARINA OF TIME 3D",
                genre="ACTION-ADVENTURE", year="2011", dev="NINTENDO EAD",
                players="1 PLAYER", stars=5,
                hero="dscard", marquee="marquee_tall.png", shot="screenshot_c.png",
                media="card_hero.png", prev="card_prev.png", next="card_next.png",
                desc="The landmark adventure reborn in stereoscopic 3D. Travel through time as young and adult Link to stop Ganondorf's dark reign over Hyrule."),
    # v18.4.4: NO-marquee case (Driver 2 on the user's Nova) -> the zone
    # stays clean empty whitespace now; the ghost-text fallback is gone.
    # marquee=None paints nothing (as before).
    "psx_nomq": dict(system="psx", title="DRIVER 2: BACK ON THE STREETS",
                genre="RACING, DRIVING", year="2000",
                dev="REFLECTIONS INTERACTIVE", players="1\u20132 PLAYERS", stars=4,
                hero="disc", marquee=None, shot="screenshot_a.png",
                media="disc_hero.png", prev="disc_prev.png", next="disc_next.png",
                desc="gangs. The action takes you to Chicago, Las Vegas, Rio and Havana, all of which are depicted in detail, with curved roads added from the first game. As before, you have full control over the car as it"),
}

if __name__ == "__main__":
    os.makedirs(PROOFS, exist_ok=True)
    for name, v in VARIANTS.items():
        li = render(v, "light")
        dk = render(v, "dark")
        pl = os.path.join(PROOFS, f"v18_4_proof_{name}_light.png")
        pd = os.path.join(PROOFS, f"v18_4_proof_{name}_dark.png")
        li.save(pl); dk.save(pd)
        sbs = Image.new("RGB", (W * 2, H), (0, 0, 0))
        sbs.paste(li, (0, 0)); sbs.paste(dk, (W, 0))
        ps = os.path.join(PROOFS, f"v18_4_proof_{name}_sbs.png")
        sbs.save(ps)
        print("saved", pl, pd, ps)
