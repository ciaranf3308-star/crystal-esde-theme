#!/usr/bin/env python3
"""Crystal v18.4.0 SYSTEM-VIEW scheme proofs (VM-ONLY, NEVER SHIPS).

Renders the system view in light and dark using the real XML geometry,
now including the v18.4.0 sysHeroLogo element (parsed from views.xml:
pos/maxSize/origin), per-system text overrides, tinted background,
badge, carousel strip (real card art, XML dimming), help line.

Systems: nds (user's Nova case), psx, gb, snes, n64 (varied collage
styles), nes (no logo asset -> proves the clean paint-nothing case).
Side-by-side composites are the audit gate.
"""
import os, re, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
sys.path.insert(0, os.path.join(REPO, "work"))
from mock_gamelist_v18_3_proof import palette, HX, tint, px, sz, fs, el_box, el_val, parse_view

CRYS = os.path.join(REPO, "theme-src/crystal")
VIEWS = os.path.join(CRYS, "views.xml")
PROOFS = os.path.join(REPO, "work/proofs")
W, H = 1280, 960
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

SYSTEMS = ("nds", "psx", "gb", "snes", "n64", "nes")
NEIGHBORS = {
    "nds": ["gb", "gba", "gbc", "nds", "n3ds", "snes", "n64"],
    "psx": ["ps2", "n64", "snes", "psx", "gc", "gba", "wii"],
    "gb": ["gbc", "gba", "n64", "gb", "snes", "psx", "nes"],
    "snes": ["nes", "n64", "gc", "snes", "psx", "gba", "wii"],
    "n64": ["snes", "gc", "psx", "n64", "ps2", "gba", "nds"],
    "nes": ["snes", "gb", "gbc", "nes", "psx", "gba", "n64"],
}
COUNTS = {"nds": "13 GAMES", "psx": "128 GAMES", "gb": "96 GAMES",
          "snes": "42 GAMES", "n64": "35 GAMES", "nes": "58 GAMES"}

TEXT_ELEMS = ["mfrBadge", "sysName", "sysName1", "sysName2",
              "sysDesc", "countNum", "factsLine"]
COLOR_KEY = {"mfrBadge": "badgeInk", "sysName": "crystalText",
             "sysName1": "crystalText", "sysName2": "crystalText",
             "sysDesc": "crystalText", "countNum": "crystalText",
             "factsLine": "crystalAccent"}

def per_system_overrides(system):
    """Parse the per-system theme.xml system view into {elem: {prop: val}}."""
    xml = open(os.path.join(CRYS, system, "theme.xml"), encoding="utf-8").read()
    out = {}
    for elem in TEXT_ELEMS:
        m = re.search(r'<%s name="%s">(.*?)</%s>' % ("text", elem, "text"), xml, re.S)
        if not m:
            continue
        body = m.group(1)
        props = {}
        for p in ("pos", "size", "fontSize"):
            pm = re.search(r'<%s>(.*?)</%s>' % (p, p), body, re.S)
            if pm:
                props[p] = pm.group(1).strip()
        tm = re.search(r'(?<!\w)<text>(.*?)</text>', body, re.S)
        if tm:
            props["text"] = tm.group(1).strip()
        out[elem] = props
    return out

def render_sys(system, scheme):
    pal = palette(scheme)
    view = parse_view(open(VIEWS, encoding="utf-8").read(), "system")
    ov = per_system_overrides(system)
    bg = Image.open(os.path.join(CRYS, "backgrounds", f"{system}.webp")).convert("RGBA")
    bg = tint(bg, pal["sysBgTint"]).resize((W, H))

    # v18.4.0 hero logo, parsed from the real XML element
    lg = el_box(view, 'image name="sysHeroLogo"')
    lx, ly = [float(v) for v in el_val(lg, "pos").split()]
    lmw, lmh = [float(v) for v in el_val(lg, "maxSize").split()]
    logo_path = os.path.join(CRYS, "art/console_logos", f"{system}.png")
    if os.path.isfile(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        lw, lh = logo.size
        s = min(lmw * W / lw, lmh * H / lh)
        logo = logo.resize((max(1, int(lw * s)), max(1, int(lh * s))), Image.LANCZOS)
        bg.alpha_composite(logo, (int(lx * W - logo.size[0] / 2),
                                  int(ly * H - logo.size[1] / 2)))

    d = ImageDraw.Draw(bg, "RGBA")

    def props(elem):
        try:
            base = el_box(view, f'text name="{elem}"')
        except ValueError:
            # sysName1/2 exist only per-system; inherit sysName's base box
            base = el_box(view, 'text name="sysName"')
        p = {"pos": el_val(base, "pos"), "size": el_val(base, "size"),
             "fontSize": el_val(base, "fontSize")}
        p.update(ov.get(elem, {}))
        return p

    # mfrBadge pill
    bp = props("mfrBadge")
    bx, by = [float(v) for v in bp["pos"].split()]
    bx, by = px(bx), sz(by)
    fb = ImageFont.truetype(FB, int(round(fs(float(bp["fontSize"])))))
    btxt = ov.get("mfrBadge", {}).get("text", "")
    tw = int(fb.getlength(btxt)) + 26
    d.rounded_rectangle([bx - 13, by - 5, bx + tw - 13, by + fb.size + 12], 7,
                        fill=HX(pal["badgeBg"]) + (255,))
    d.text((bx, by), btxt, font=fb, fill=HX(pal["badgeInk"]) + (255,))

    for elem in ("sysName", "sysName1", "sysName2", "sysDesc", "countNum", "factsLine"):
        if elem not in ov and elem not in ("countNum",):
            continue
        p = props(elem)
        if elem == "countNum":
            txt = COUNTS[system]
        else:
            txt = ov.get(elem, {}).get("text", "")
            if not txt:
                continue
        ex, ey = [float(v) for v in p["pos"].split()]
        f = ImageFont.truetype(FB, int(round(fs(float(p["fontSize"])))))
        d.text((px(ex), sz(ey)), txt, font=f,
               fill=HX(pal[COLOR_KEY[elem]]) + (255,))

    # carousel strip (same math as v18.3 harness)
    c = el_box(view, 'carousel name="sysCarousel"')
    cy = float(el_val(c, "pos").split()[1])
    item_w, item_h = int(px(0.095)), int(sz(0.169))
    sel_w, sel_h = item_w * 2, item_h * 2
    cy_px = sz(cy) + sz(0.360) / 2
    order = NEIGHBORS[system]
    total_w = sel_w + 6 * (item_w + 24)
    x = (W - total_w) / 2
    for i, sname in enumerate(order):
        card = Image.open(os.path.join(CRYS, "cards", f"{sname}.png")).convert("RGBA")
        if i == 3:
            card = card.resize((sel_w, sel_h), Image.LANCZOS)
            bg.alpha_composite(card, (int(x), int(cy_px - sel_h / 2)))
            x += sel_w + 24
        else:
            card = card.resize((item_w, item_h), Image.LANCZOS)
            card = ImageEnhance.Color(card).enhance(0.50)
            card = ImageEnhance.Brightness(card).enhance(0.30)
            card.putalpha(card.split()[3].point(lambda a: int(a * 0.92)))
            bg.alpha_composite(card, (int(x), int(cy_px - item_h / 2)))
            x += item_w + 24

    fh = ImageFont.truetype(FB, int(round(fs(0.0145))))
    d.text((W / 2, sz(0.982)), "A SELECT   B BACK   Y OPTIONS", font=fh,
           fill=HX(pal["crystalDim"]) + (255,), anchor="mm")
    return bg.convert("RGB")

if __name__ == "__main__":
    os.makedirs(PROOFS, exist_ok=True)
    for system in SYSTEMS:
        li = render_sys(system, "light")
        dk = render_sys(system, "dark")
        pl = os.path.join(PROOFS, f"v18_4_sys_{system}_light.png")
        pd = os.path.join(PROOFS, f"v18_4_sys_{system}_dark.png")
        li.save(pl); dk.save(pd)
        sbs = Image.new("RGB", (W * 2, H), (0, 0, 0))
        sbs.paste(li, (0, 0)); sbs.paste(dk, (W, 0))
        ps = os.path.join(PROOFS, f"v18_4_sys_{system}_sbs.png")
        sbs.save(ps)
        print("saved", pl, pd, ps)
