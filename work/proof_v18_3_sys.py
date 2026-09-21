#!/usr/bin/env python3
"""Crystal v18.3.0 SYSTEM-VIEW scheme proofs (VM-ONLY, NEVER SHIPS).

Renders the system view for psx + gb in light and dark using the real
XML geometry: tinted background, badge, texts, carousel strip (real card
art, XML dimming for unfocused items), help line. Side-by-side
composites are the contrast audit gate.
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

def sys_text(system, elem_name):
    xml = open(os.path.join(CRYS, system, "theme.xml"), encoding="utf-8").read()
    m = re.search(r'<%s name="%s">.*?<text>(.*?)</text>' % ("text", elem_name), xml, re.S)
    return m.group(1) if m else ""

NEIGHBORS = {  # systems flanking the selected one in the strip
    "psx": ["ps2", "n64", "snes", "psx", "gc", "gba", "wii"],
    "gb": ["gbc", "gba", "n64", "gb", "snes", "psx", "nes"],
}
NAMES = {"psx": ("SONY", "PlayStation", "Where 3D grew up. Crash, Spyro, Final Fantasy VII.",
                 "128 GAMES", "32-BIT \u2022 1995"),
         "gb": ("NINTENDO", "Nintendo Game Boy", "A pocket rainbow of classics. Tetris sold millions.",
                "96 GAMES", "8-BIT \u2022 HANDHELD \u2022 1989")}

def render_sys(system, scheme):
    pal = palette(scheme)
    view = parse_view(open(VIEWS, encoding="utf-8").read(), "system")
    bg = Image.open(os.path.join(CRYS, "backgrounds", f"{system}.webp")).convert("RGBA")
    bg = tint(bg, pal["sysBgTint"]).resize((W, H))
    d = ImageDraw.Draw(bg, "RGBA")
    badge_txt, name_txt, desc_txt, count_txt, facts_txt = NAMES[system]

    # mfrBadge: pill + text
    b = el_box(view, 'text name="mfrBadge"')
    bx, by = px(float(el_val(b, "pos").split()[0])), sz(float(el_val(b, "pos").split()[1]))
    fz = int(round(fs(float(el_val(b, "fontSize")))))
    fb = ImageFont.truetype(FB, fz)
    tw = int(fb.getlength(badge_txt)) + 26
    d.rounded_rectangle([bx - 13, by - 5, bx + tw - 13, by + fz + 12], 7,
                        fill=HX(pal["badgeBg"]) + (255,))
    d.text((bx, by), badge_txt, font=fb, fill=HX(pal["badgeInk"]) + (255,))

    def put(elem, txt, font_path, color_key):
        e = el_box(view, f'text name="{elem}"')
        ex, ey = [float(x) for x in el_val(e, "pos").split()]
        fz2 = float(el_val(e, "fontSize"))
        f = ImageFont.truetype(font_path, int(round(fs(fz2))))
        d.text((px(ex), sz(ey)), txt, font=f, fill=HX(pal[color_key]) + (255,))

    put("sysName", name_txt, FB, "crystalText")
    put("sysDesc", desc_txt, FB, "crystalText")
    # countNum is a datetime-less text in XML? it's <text systemdata=gamecountGames>
    e = el_box(view, 'text name="countNum"')
    ex, ey = [float(x) for x in el_val(e, "pos").split()]
    fz2 = float(el_val(e, "fontSize"))
    d.text((px(ex), sz(ey)), count_txt,
           font=ImageFont.truetype(FB, int(round(fs(fz2)))),
           fill=HX(pal["crystalText"]) + (255,))
    put("factsLine", facts_txt, FB, "crystalAccent")

    # carousel strip: selected 2x centered, neighbors dimmed per XML
    c = el_box(view, 'carousel name="sysCarousel"')
    cx, cy = float(el_val(c, "pos").split()[0]), float(el_val(c, "pos").split()[1])
    item_w, item_h = int(px(0.095)), int(sz(0.169))
    sel_w, sel_h = item_w * 2, item_h * 2
    cy_px = sz(cy) + sz(0.360) / 2
    order = NEIGHBORS[system]
    total_w = sel_w + 6 * (item_w + 24)
    x = (W - total_w) / 2  # engine centers items in the full-width strip
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

    # help line
    fh = ImageFont.truetype(FB, int(round(fs(0.0145))))
    d.text((W / 2, sz(0.982)), "A SELECT   B BACK   Y OPTIONS", font=fh,
           fill=HX(pal["crystalDim"]) + (255,), anchor="mm")
    return bg.convert("RGB")

if __name__ == "__main__":
    os.makedirs(PROOFS, exist_ok=True)
    for system in ("psx", "gb"):
        li = render_sys(system, "light")
        dk = render_sys(system, "dark")
        pl = os.path.join(PROOFS, f"v18_3_sys_{system}_light.png")
        pd = os.path.join(PROOFS, f"v18_3_sys_{system}_dark.png")
        li.save(pl); dk.save(pd)
        sbs = Image.new("RGB", (W * 2, H), (0, 0, 0))
        sbs.paste(li, (0, 0)); sbs.paste(dk, (W, 0))
        ps = os.path.join(PROOFS, f"v18_3_sys_{system}_sbs.png")
        sbs.save(ps)
        print("saved", pl, pd, ps)
