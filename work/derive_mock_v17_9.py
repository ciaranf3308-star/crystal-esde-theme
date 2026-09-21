#!/usr/bin/env python3
"""Derive work/mock_gamelist_v17_9.py from work/mock_gamelist_v17_8.py via
exact-match edits (asserted). v17.9 convergence QA:
  - title fontSize parsed from XML (0.0260), comfort-margin check
  - rail: 5 slots (dev dropped), worst-case content WITHOUT dev
  - desc fontSize parsed from XML (0.0145)
  - rating stars at parsed XML position (296,481)
  - screenshot y=732 check
  - shard-next wedge: no hard edges, feathered corners
  - shadow: 480px wide, opacity 0.7
  - rails: byte-identical to v17.8.0 (spine untouched)
  - new stress variants: shortdesc, norating, nodev, combo
"""
import os, shutil

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
SRC = os.path.join(REPO, "work/mock_gamelist_v17_8.py")
DST = os.path.join(REPO, "work/mock_gamelist_v17_9.py")

shutil.copyfile(SRC, DST)
s = open(DST, encoding="utf-8").read()
n = 0

def sub(old, new, expect=1):
    global s, n
    c = s.count(old)
    assert c == expect, f"expected {expect}, found {c}: {old[:90]!r}"
    s = s.replace(old, new)
    n += 1

# ---- header ------------------------------------------------------------
sub('"""Crystal v17.8.0 gamelist mock + verification (PIL renders, never ES-DE).',
    '"""Crystal v17.9.0 gamelist mock + verification (PIL renders, never ES-DE).')
sub('''ROBUSTNESS PASS mock. The VM carries NO scraped artwork, so hero /
marquee / screenshot / prev / next are rendered as CLEAN NEUTRAL SLOT
FILLS - no dashed borders, no labels, no debug treatment - because
on-device with real assets they have no visible treatment either. The
marquee slot draws ONLY the maxSize-fitted rect (the zone itself is
invisible open white). The proofs assess the UI SHELL around the slots.

10 variants cover the responsive extremes: ps2 (disc), n64
(cartridge), gba (long description), shorttitle (DOOM), longtitle
(THE LEGEND OF ZELDA: OCARINA OF TIME 3D - the reported clip case),
longdev (worst-case developer), widemarquee (16:5), tallmarquee
(1:1.5, DS-card hero, 1-8 players), nodesc (missing description),
nomarquee (missing marquee -> clean fallback title).''',
'''CONVERGENCE PASS mock. The VM carries NO scraped artwork, so hero /
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
(missing developer), combo (missing marquee+desc+rating+developer).''')

# ---- render(): parse dynamic values from XML ---------------------------
sub('''    f_desc = ImageFont.truetype(REG, int(round(fs(0.0175))))
    y = 312
    for line in wrap(v["desc"], f_desc, px(0.2984375))[:6]:
        d.text((48, y), line, font=f_desc, fill=INKDIM + (255,))
        y += 26''',
'''    fz_desc = float(el_val(el_box(view, 'text name="libDesc"'), "fontSize"))
    f_desc = ImageFont.truetype(REG, int(round(fs(fz_desc))))
    desc_step = int(round(fs(fz_desc) * 1.5))
    y = 312
    for line in wrap(v["desc"], f_desc, px(0.2984375))[:6]:
        d.text((48, y), line, font=f_desc, fill=INKDIM + (255,))
        y += desc_step''')

sub('''    # rating stars in the XML box (296,470 140x28)
    for i in range(5):
        cx, cy = 296 + 14 + i * 28, 470 + 14''',
'''    # rating stars in the XML box (parsed from the theme)
    rb = el_box(view, 'rating name="libRating"')
    rrx, rry = [float(q) for q in el_val(rb, "pos").split()]
    rrw = float(el_val(rb, "size").split()[0])
    for i in range(5):
        cx, cy = px(rrx) + 14 + i * 28, sz(rry) + 14''')

sub('''    f_title = ImageFont.truetype(BOLD, int(round(fs(0.0295))))
    title = v["title"].upper()
    if f_title.getlength(title) <= px(tw):
        d.text((px(tx), sz(ty)), title, font=f_title, fill=(255, 255, 255, 255),
               anchor="mm")
    else:
        # beyond the measured envelope: engine wraps; mock draws 2 lines
        for i, ln in enumerate(wrap(title, f_title, px(tw))[:2]):
            d.text((px(tx), sz(ty) + (i - 0.5) * int(round(fs(0.0295))) * 1.15),
                   ln, font=f_title, fill=(255, 255, 255, 255), anchor="mm")''',
'''    fz_title = float(el_val(t, "fontSize"))
    f_title = ImageFont.truetype(BOLD, int(round(fs(fz_title))))
    title = v["title"].upper()
    if f_title.getlength(title) <= px(tw):
        d.text((px(tx), sz(ty)), title, font=f_title, fill=(255, 255, 255, 255),
               anchor="mm")
    else:
        # beyond the measured envelope: engine word-wraps; mock draws 2 lines
        for i, ln in enumerate(wrap(title, f_title, px(tw))[:2]):
            d.text((px(tx), sz(ty) + (i - 0.5) * int(round(fs(fz_title))) * 1.15),
                   ln, font=f_title, fill=(255, 255, 255, 255), anchor="mm")''')

sub('''    rail = [("libMetaGenre", v["genre"].upper()), ("libMetaSep1", "\\u2022"),
            ("libMetaYear", v["year"]), ("libMetaSep2", "\\u2022"),
            ("libMetaDev", v["dev"].upper()), ("libMetaSep3", "\\u2022"),
            ("libMetaPlayers", v["players"].upper())]''',
'''    rail = [("libMetaGenre", v["genre"].upper()), ("libMetaSep1", "\\u2022"),
            ("libMetaYear", v["year"]), ("libMetaSep2", "\\u2022"),
            ("libMetaPlayers", v["players"].upper())]''')

sub('''    shadow = Image.open(os.path.join(ART, "lib_shadow_soft.png")).convert("RGBA") \\
        .resize((int(px(qw)), int(sz(qh))))
    shadow.putalpha(shadow.split()[3].point(lambda a: int(a * 0.9)))''',
'''    sh_op = float(el_val(sh2, "opacity"))
    shadow = Image.open(os.path.join(ART, "lib_shadow_soft.png")).convert("RGBA") \\
        .resize((int(px(qw)), int(sz(qh))))
    shadow.putalpha(shadow.split()[3].point(lambda a: int(a * sh_op)))''')

# ---- new stress variants ------------------------------------------------
sub('''    "nomarquee": dict(system="wii", title="WII SPORTS", genre="SPORTS", year="2006",
                      dev="NINTENDO", players="1\\u20134 PLAYERS", stars=4,
                      hero="disc", marquee_aspect=None,
                      desc="Five sports that turned living rooms into stadiums."),
}''',
'''    "nomarquee": dict(system="wii", title="WII SPORTS", genre="SPORTS", year="2006",
                      dev="NINTENDO", players="1\\u20134 PLAYERS", stars=4,
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
                   dev="", players="1\\u20132 PLAYERS", stars=3,
                   hero="cartridge", marquee_aspect=16 / 9,
                   desc="Aim the NES Zapper at the screen and blast clay pigeons and ducks."),
    "combo": dict(system="nds", title="BRAIN AGE", genre="PUZZLE", year="2005",
                   dev="", players="1 PLAYER", stars=0,
                   hero="dscard", marquee_aspect=None, desc=""),
}''')

# ---- macro lock: vs v17.8.0, dev/sep3 removal whitelisted --------------
sub('''def check_macro_lock():
    head = subprocess.run(["git", "-C", REPO, "show", "HEAD:theme-src/crystal/views.xml"],
                          capture_output=True, text=True).stdout
    a, b = geom_dict(parse_view(head, "gamelist")), geom_dict(parse_view(open(VIEWS).read(), "gamelist"))
    whitelist = {"libGameName": set(),          # fontSize only (not in geom)
                 "libMetaGenre": {"pos", "size"}, "libMetaSep1": {"pos", "size"},
                 "libMetaYear": {"pos", "size"}, "libMetaSep2": {"pos", "size"},
                 "libMetaDev": {"pos", "size"}, "libMetaSep3": {"pos", "size"},
                 "libMetaPlayers": {"pos", "size"},
                 "libGenre": {"pos"}, "libPlayers": {"pos"}, "libDev": {"pos", "size"},
                 "libScreenshot": {"pos", "size"},
                 "libSelectedGlowBlue": set(),    # opacity only (not in geom)
                 "gameCarousel": {"size"},       # pitch 480 -> 512
                 "libHeroWash": set(), "libPlaneHero": set(),
                 "libPanelMain": set(), "libRail": set()}
    ok, detail = True, ""
    if set(a) | {"libHeroWash"} != set(b):
        ok, detail = False, "element set changed"
    else:
        for k in a:
            wa = whitelist.get(k, set())
            for f, val in a[k].items():
                if f not in wa and b[k].get(f) != val:
                    ok, detail = False, f"{k}.{f}: {val} -> {b[k].get(f)}"
    check("macro-lock vs v17.7.0 (whitelisted robustness moves only)", ok,
          detail or f"{len(a)} elements")''',
'''def check_macro_lock():
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
          detail or f"{len(a)} elements")''')

# ---- title check: 0.0260, comfort margin >=48px/side --------------------
sub('''def check_title_xml():
    xml = open(VIEWS).read()
    t = el_box(parse_view(xml, "gamelist"), 'text name="libGameName"')
    no_scroll = not any(k in t for k in ("<container>", "containerType",
                                         "containerScrollSpeed"))
    box_w = float(el_val(t, "size").split()[0]) * W
    # conservative: larger of int()/round() interpretations of 0.0295
    f_big = ImageFont.truetype(BOLD, max(int(0.0295 * H), int(round(0.0295 * H))))
    zelda = "THE LEGEND OF ZELDA: OCARINA OF TIME 3D"
    zw = f_big.getlength(zelda)
    check("title: static caption 0.0295, no scroll; worst case fits one line",
          no_scroll and el_val(t, "fontSize") == "0.0295"
          and el_val(t, "size") == "0.58 0.0375" and zw <= box_w - 10,
          f"zelda={zw:.0f}px box={box_w:.0f}px")''',
'''def check_title_xml():
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
          f"zelda={zw:.0f}px box={box_w:.0f}px margin={margin:.0f}px/side")''')

# ---- rail check: 5 slots, dev gone, worst case without dev -------------
sub('''    names = ["libMetaGenre", "libMetaSep1", "libMetaYear", "libMetaSep2",
             "libMetaDev", "libMetaSep3", "libMetaPlayers"]''',
'''    names = ["libMetaGenre", "libMetaSep1", "libMetaYear", "libMetaSep2",
             "libMetaPlayers"]''')
sub('''    check("rail: 7 slots no-overlap, inside hero identity width (0.413-0.993)",
          ok and inside, f"span={spans[0][0]:.3f}-{spans[-1][1]:.3f}")''',
'''    dev_gone = '<text name="libMetaDev">' not in g and '<text name="libMetaSep3">' not in g
    check("rail: 5 slots no-overlap, inside hero identity width (0.413-0.993); dev removed",
          ok and inside and dev_gone, f"span={spans[0][0]:.3f}-{spans[-1][1]:.3f}")''')
sub('''    worst = {"libMetaGenre": "ACTION-ADVENTURE", "libMetaYear": "1998",
             "libMetaDev": "NINTENDO ENTERTAINMENT ANALYSIS & DEVELOPMENT",
             "libMetaPlayers": "1-8 PLAYERS"}''',
'''    worst = {"libMetaGenre": "FIRST-PERSON SHOOTER", "libMetaYear": "1998",
             "libMetaPlayers": "1-8 PLAYERS"}''')

# ---- screenshot y=732 ---------------------------------------------------
sub('''    check("screenshot rebalanced: x=48, y=724, h=170 (was 700/210)",
          el_val(s, "pos") == "0.0375 0.7541667"
          and el_val(s, "size") == "0.309375 0.1770833",
          f"pos={el_val(s,'pos')} size={el_val(s,'size')}")''',
'''    check("screenshot: x=48, y=732 (+8px), h=170",
          el_val(s, "pos") == "0.0375 0.7625"
          and el_val(s, "size") == "0.309375 0.1770833",
          f"pos={el_val(s,'pos')} size={el_val(s,'size')}")''')

# ---- rails: untouched in v17.9 ------------------------------------------
sub('''def check_rails():
    n = sum(1 for s, _ in SYSTEMS
            if os.path.exists(os.path.join(ART, "rails", f"{s}.png")))
    check("all 21 rails regenerated", n == 21, str(n))
    head = subprocess.run(["git", "-C", REPO,
                           "show", "HEAD:theme-src/crystal/art/rails/ps2.png"],
                          capture_output=True).stdout
    src8 = open(os.path.join(REPO, "work/gen_v17_8_assets.py")).read()
    src7 = open(os.path.join(REPO, "work/gen_v17_7_assets.py")).read()
    check("spine dotgrid quieter: 40px/alpha3 -> 48px/alpha2 in generator",
          "dotgrid(img, (6, 30, 54, 882), alpha=2, spacing=48)" in src8
          and "dotgrid(img, (6, 30, 54, 882), alpha=3, spacing=40)" in src7)
    # sanity: the regenerated rail really differs in the dot band
    import io
    old = Image.open(io.BytesIO(head)).convert("RGB")
    new = Image.open(os.path.join(ART, "rails/ps2.png")).convert("RGB")
    diff = sum(1 for x in range(6, 54, 3) for y in range(30, 882, 3)
               if abs(lum(old.getpixel((x, y))) - lum(new.getpixel((x, y)))) > 2)
    check("rails regenerated (pixel delta vs v17.6)", diff > 50, f"delta_px={diff}")
    prm = json.load(open(os.path.join(REPO, "work/rail_params_v17_8.json")))
    check("rails: optical lift + increased logo presence recorded",
          all(v.get("optical_lift") == 6 for v in prm.values()) and len(prm) == 21)''',
'''def check_rails():
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
          f"changed={bad}" if bad else "21 rails")''')

# ---- hygiene: v17.9 regenerates panel + shard-next only -----------------
sub('''    for f in ("gamelist_generic_bg.png", "lib_shadow_soft.png", "lib_glow_blue.png",
              "lib_shard_prev.png", "lib_shard_next.png", "lib_title_rule.png",
              "star_filled.png", "star_unfilled.png", "lib_bottom_gradient.png"):''',
'''    for f in ("gamelist_generic_bg.png", "lib_shadow_soft.png", "lib_glow_blue.png",
              "lib_shard_prev.png", "lib_title_rule.png",
              "star_filled.png", "star_unfilled.png", "lib_bottom_gradient.png",
              "lib_hero_wash.png", "lib_plane_hero.png"):''')
sub('''    # v17.8 intentionally regenerates: panel, rails, hero plane, hero wash
    for f in ("lib_panel_main.png", "lib_plane_hero.png", "lib_hero_wash.png",
              "rails/ps2.png"):''',
'''    # v17.9 intentionally regenerates: panel (+8px screenshot box, whisper
    # hairline) and the next-item shard (diagonal wedge)
    for f in ("lib_panel_main.png", "lib_shard_next.png"):''')
sub('''    check("v17.8 assets regenerated (panel/rails/plane/wash)", True)''',
'''    check("v17.9 assets regenerated (panel/shard-next)", True)''')

# ---- proof filename ------------------------------------------------------
sub('        p = os.path.join(PROOFS, f"mock_v17_8_{name}.png")',
    '        p = os.path.join(PROOFS, f"mock_v17_9_{name}.png")')

# ---- check_proof adaptations --------------------------------------------
sub('''    tbox = info["tbox"]
    f_t = ImageFont.truetype(BOLD, max(int(0.0295 * H), int(round(0.0295 * H))))
    tw = f_t.getlength(v["title"].upper())
    boxw = tbox[2] - tbox[0]
    check(f"[{name}] title fits box one line (never clips)",
          tw <= boxw, f"title={tw:.0f}px box={boxw:.0f}px")''',
'''    tbox = info["tbox"]
    gv = parse_view(open(VIEWS).read(), "gamelist")
    fz_t = float(el_val(el_box(gv, 'text name="libGameName"'), "fontSize"))
    f_t = ImageFont.truetype(BOLD, max(int(fz_t * H), int(round(fz_t * H))))
    tw = f_t.getlength(v["title"].upper())
    boxw = tbox[2] - tbox[0]
    check(f"[{name}] title fits box one line with >=48px/side margin (never clips)",
          tw <= boxw - 96, f"title={tw:.0f}px box={boxw:.0f}px")''')

sub('''    for ename, txt in (("libMetaGenre", v["genre"].upper()), ("libMetaYear", v["year"]),
                       ("libMetaDev", v["dev"].upper()), ("libMetaPlayers", v["players"].upper())):''',
'''    for ename, txt in (("libMetaGenre", v["genre"].upper()), ("libMetaYear", v["year"]),
                       ("libMetaPlayers", v["players"].upper())):''')

sub('''    dev_lines = wrap(v["dev"].upper(), f_micro, dev_box_w)
    dev_bottom = dev_y + len(dev_lines) * 26
    kick_y = 694 + 10  # baked SCREENSHOT kicker, panel-local -> global
    check(f"[{name}] developer wraps in-column (<=2 lines, no spill)",
          len(dev_lines) <= 2 and dev_bottom < kick_y,
          f"lines={len(dev_lines)} bottom={dev_bottom:.0f}")''',
'''    dev_lines = wrap(v["dev"].upper(), f_micro, dev_box_w) if v["dev"] else []
    dev_bottom = dev_y + len(dev_lines) * 22
    kick_y = 694 + 10  # baked SCREENSHOT kicker, panel-local -> global
    check(f"[{name}] developer wraps in-column (<=2 lines, no spill; empty ok)",
          len(dev_lines) <= 2 and dev_bottom < kick_y,
          f"lines={len(dev_lines)} bottom={dev_bottom:.0f}")''')

# ---- new checks: shard wedge, shadow, rail centring ---------------------
sub('''def check_clearance_worst_case():''',
'''def check_shard_wedge():
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

def check_clearance_worst_case():''')

sub('''    check("title/rail clearance, real worst case (zelda + max rail)", gap >= 4, f"gap={gap}px")''',
'''    check("title/rail clearance, real worst case (zelda + max rail)", gap >= 4, f"gap={gap}px")


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
          tint > 50 and dark == 0, f"tint={tint} dark={dark}")''')

sub('''    check_macro_lock(); check_marquee_xml(); check_title_xml(); check_rail_xml()
    check_screenshot_xml(); check_typography(); check_fallbacks(); check_plane()
    check_wash(); check_rails(); check_motion(); check_hygiene()
    check_clearance_worst_case()''',
'''    check_macro_lock(); check_marquee_xml(); check_title_xml(); check_rail_xml()
    check_screenshot_xml(); check_typography(); check_fallbacks(); check_plane()
    check_wash(); check_rails(); check_motion(); check_hygiene()
    check_clearance_worst_case(); check_shard_wedge(); check_shadow()
    check_rail_centre(); check_whisper()''')

# worst-case rail string for the clearance test: no developer anymore
sub('''           "ACTION-ADVENTURE \\u2022 1998 \\u2022 NINTENDO ENTERTAINMENT ANALYSIS & DEVELOPMENT \\u2022 1-8 PLAYERS",''',
'''           "FIRST-PERSON SHOOTER \\u2022 1998 \\u2022 1-8 PLAYERS",''')
sub('''    d.text((450, 90), "THE LEGEND OF ZELDA: OCARINA OF TIME 3D",
           font=ImageFont.truetype(BOLD, int(round(0.0295 * H))), fill="black", anchor="mm")''',
'''    d.text((450, 90), "THE LEGEND OF ZELDA: OCARINA OF TIME 3D",
           font=ImageFont.truetype(BOLD, int(round(0.0260 * H))), fill="black", anchor="mm")''')

open(DST, "w", encoding="utf-8").write(s)
print(f"mock derived ok: {n} edits")
