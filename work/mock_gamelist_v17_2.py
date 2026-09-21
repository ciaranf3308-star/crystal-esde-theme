#!/usr/bin/env python3
"""PIL mock of the Crystal v17.2.0 gamelist SHAPE-AWARENESS pass, parsed
from the real theme XML. Mock only - not an ES-DE screenshot.

Usage: mock_gamelist_v17_2.py [cartridge|gamecard|disc]
  cartridge -> n64 / SUPER MARIO 64 (tall cartridge silhouette)
  gamecard  -> n3ds / OCARINA OF TIME 3D (small game-card silhouette)
  disc      -> ps2 / SAN ANDREAS (printed disc silhouette)

The macro layout is LOCKED (left column 6,10 470x940; spine 486,24
60x912; hero 540px at 900,430; title rule Y716 / title Y736 / meta Y757;
screenshot 42,700 396x210; footer y915). This pass makes the hero
media-agnostic per the user's 10-point brief:

1. No disc assumption: the disc-specific yellow rim arc (libSelectedRim /
   lib_hero_rim.png) is retired and deleted. The hero keeps its native
   silhouette - cartridge, game card, UMD or disc.
2. Shadow/glow follow the silhouette in the mock (art-direction intent);
   the real theme uses the generic soft shadow + restrained blue
   atmosphere, which are shape-neutral by construction.
3. The selected media is large, crisp-edged, lifted (detached shadow),
   with only a thin restrained yellow highlight on part of the
   silhouette. No rings, no circular frame, no container.
4/5. Prev/next use the SAME shape as the selected system, ~44% hero
   scale, 45% opacity, pushed to the edges: prev 71% cropped off the top
   edge, next 29% cropped off the bottom edge, its visible mass pushed
   toward the lower-right corner by the redesigned foreground shard -
   clear of the title zone.
6. The title area is protected: the next item's box starts 23px below
   the meta line; nothing overlaps the identity zone.
7. The left panel uses the real reusable treatment: the mock marquee is
   a NEUTRAL stand-in (name lockup on open whitespace) - the v17
   game-specific burst artwork is gone, since the real theme binds the
   actual scraped marquee asset.
8. Left-panel direction kept: description/metadata x aligned to the
   baked kickers; no boxes back.
9. Spine: decorative noise reduced slightly; branding still dynamically
   bound to the actual current system for all 21 systems.
10. Three media types are rendered and checked: cartridge, game card,
    disc. None is forced into a disc treatment.

ES-DE 3.4.1 has no theme keyframes or idle animation, and none is
claimed. One honest mock-vs-reality note: ES-DE cannot draw a
per-silhouette yellow edge highlight, so the real theme carries the
selective yellow accent as the small compositional tick baked into the
hero plane behind the media; the mock draws the highlight along each
synthetic silhouette to illustrate the art-direction intent."""
import os, sys, re, glob, math, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

VARIANT = sys.argv[1] if len(sys.argv) > 1 else "cartridge"
assert VARIANT in ("cartridge", "gamecard", "disc"), VARIANT

W, H = 1280, 960
ROOT = os.path.expanduser("~/workspace/crystal-esde-theme/theme-src/crystal")
OUT = os.path.expanduser(
    "~/workspace/crystal-esde-theme/work/proofs/mock_v17_2_%s.png" %
    {"cartridge": "cartridge", "gamecard": "gamecard", "disc": "disc"}[VARIANT])

GAMES = {
    "cartridge": dict(system="n64", title="SUPER MARIO 64",
                      genre="PLATFORMER", year="1996", dev="NINTENDO",
                      players="1-2 PLAYERS",
                      desc=["A legendary platform adventure across",
                            "painted worlds. Bowser has other plans",
                            "this time - 120 Power Stars await the",
                            "brave. A landmark in 3D game design."]),
    "gamecard": dict(system="n3ds", title="THE LEGEND OF ZELDA: OCARINA OF TIME 3D",
                     genre="ACTION-ADVENTURE", year="2011", dev="NINTENDO",
                     players="1 PLAYER",
                     desc=["A timeless quest reborn in stereoscopic",
                           "3D. Guide Link through Hyrule's past and",
                           "future to stop Ganondorf. The landmark",
                           "adventure, refined for handheld."]),
    "disc": dict(system="ps2", title="GRAND THEFT AUTO: SAN ANDREAS",
                 genre="ACTION-ADVENTURE", year="2004", dev="ROCKSTAR GAMES",
                 players="1-2 PLAYERS",
                 desc=["Carl Johnson returns to San Andreas to save",
                       "his family and take control of the streets.",
                       "An open-world landmark of unprecedented",
                       "scale and attitude."]),
}
G = GAMES[VARIANT]

# ------------------------------------------------------------- xml parse ---
def px(pair):
    x, y = pair.strip().split()
    return float(x) * W, float(y) * H

def sz(pair):
    x, y = pair.strip().split()
    return float(x) * W, float(y) * H

tree = ET.parse(os.path.join(ROOT, "views.xml"))
gamelist = None
for v in tree.getroot().iter("view"):
    if v.get("name") == "gamelist":
        gamelist = v
        break
els = {}
for el in gamelist:
    if el.get("name"):
        els[(el.tag, el.get("name"))] = el

def get(tag, name):
    return els[(tag, name)]

def has(tag, name):
    return (tag, name) in els

def all_paths():
    return [el.findtext("path") or "" for el in gamelist.iter("image")]

def place(base, path, box, opacity=1.0):
    art = Image.open(os.path.join(ROOT, path.replace("./", ""))).convert("RGBA")
    x, y, w, h = box
    art = art.resize((int(w), int(h)), Image.LANCZOS)
    if opacity < 1.0:
        a = art.split()[3].point(lambda v: int(v * opacity))
        art.putalpha(a)
    base.alpha_composite(art, (int(x), int(y)))

def el_box(el):
    x, y = px(el.findtext("pos"))
    w, h = sz(el.findtext("size"))
    ox, oy = (float(v) for v in el.findtext("origin", "0 0").split())
    return x - ox * w, y - oy * h, w, h

def max_box(el):
    x, y = px(el.findtext("pos"))
    w, h = sz(el.findtext("maxSize"))
    return x, y, w, h

fb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fr = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
marker = os.path.join(ROOT, "fonts/PermanentMarker-Regular.ttf")
YELLOW = (255, 214, 10)

# ------------------------------------------------------- shape renderers ---
# Each returns an RGBA layer with TRUE transparent edges - the native
# silhouette of the physical media. Nothing is forced into a circle,
# square, card or common container.

def _label_art(d, x0, y0, w, h, seed=0):
    """Generic printed-label cover art (stand-in for the game's real
    label print): sky-to-ground gradient, sun, hill."""
    for yy in range(int(h)):
        t = yy / h
        col = (int(52 + 84 * t + seed), int(108 + 74 * t), int(198 + 40 * t))
        d.line([(x0, y0 + yy), (x0 + w, y0 + yy)], fill=col + (255,))
    d.ellipse([x0 + w * 0.62, y0 + h * 0.10, x0 + w * 0.86, y0 + h * 0.42],
              fill=(255, 236, 150, 255))
    d.polygon([(x0, y0 + h), (x0, y0 + h * 0.62), (x0 + w * 0.4, y0 + h * 0.5),
               (x0 + w, y0 + h * 0.72), (x0 + w, y0 + h)],
              fill=(36, 84, 60, 255))


def disc_shape(label_text, r=270):
    """A real game disc: printed label, clean circular silhouette,
    beveled hub. No concentric data-band rings."""
    S = r * 2 + 8
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c = S / 2
    dl = ImageDraw.Draw(layer)
    for i in range(48, 0, -1):
        t = i / 48
        rr = r * t
        col = (int(150 + 70 * (1 - t)), int(170 + 60 * (1 - t)),
               int(215 + 30 * (1 - t)))
        dl.ellipse([c - rr, c - rr, c + rr, c + rr], fill=col + (255,))
    lr = r * 0.94
    lab = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ll = ImageDraw.Draw(lab)
    _label_art(ll, c - lr, c - lr, lr * 2, lr * 2)
    fnt = ImageFont.truetype(marker, max(14, int(r * 0.11)))
    ll.text((c - lr * 0.30, c + lr * 0.42), label_text, font=fnt,
            fill=(255, 255, 255, 255), anchor="mm",
            stroke_width=max(1, int(r * 0.012)), stroke_fill=(10, 26, 92, 255))
    lmask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(lmask).ellipse([c - lr, c - lr, c + lr, c + lr], fill=255)
    lab.putalpha(ImageChops.multiply(lab.split()[3], lmask))
    layer = Image.alpha_composite(layer, lab)
    dl = ImageDraw.Draw(layer)
    dl.ellipse([c - r, c - r, c + r, c + r], outline=(8, 20, 70, 255),
               width=max(4, int(r * 0.045)))
    dl.ellipse([c - r * 0.20, c - r * 0.20, c + r * 0.20, c + r * 0.20],
               fill=(232, 238, 250, 255))
    dl.ellipse([c - r * 0.075, c - r * 0.075, c + r * 0.075, c + r * 0.075],
               fill=(34, 42, 66, 255))
    return layer


def cartridge_shape(label_text):
    """An N64-style cartridge: tall rounded body, top cap with notch,
    printed label, grip ridges. Reads as a cartridge, not a disc."""
    w, h = 360, 440
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    for yy in range(h):  # subtle vertical falloff on the shell
        t = yy / h
        col = (int(64 - 14 * t), int(68 - 14 * t), int(84 - 16 * t))
        d.line([(0, yy), (w, yy)], fill=col + (255,))
    body_mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(body_mask).rounded_rectangle([0, 0, w, h], radius=30, fill=255)
    img.putalpha(ImageChops.multiply(img.split()[3], body_mask))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([0, 0, w, 56], radius=30, fill=(38, 42, 56, 255))
    d.rectangle([0, 26, w, 56], fill=(38, 42, 56, 255))
    d.rectangle([w / 2 - 46, 0, w / 2 + 46, 18], fill=(0, 0, 0, 0))  # top notch
    d.line([(8, 60), (8, h - 8)], fill=(120, 128, 150, 160), width=3)  # edge light
    # printed label
    lx, ly, lw, lh = 30, 92, w - 60, 236
    lab = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ll = ImageDraw.Draw(lab)
    ll.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=10, fill=(0, 0, 0, 0))
    _label_art(ll, lx + 6, ly + 6, lw - 12, lh - 12)
    fnt = ImageFont.truetype(marker, 30)
    bb = fnt.getbbox(label_text)
    while bb[2] - bb[0] > lw - 24 and fnt.size > 12:
        fnt = ImageFont.truetype(marker, fnt.size - 2)
        bb = fnt.getbbox(label_text)
    ll.text((lx + lw / 2, ly + lh - 34), label_text, font=fnt,
            fill=(255, 255, 255, 255), anchor="mm",
            stroke_width=2, stroke_fill=(10, 26, 92, 255))
    lmask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(lmask).rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=10, fill=255)
    lab.putalpha(ImageChops.multiply(lab.split()[3], lmask))
    img = Image.alpha_composite(img, lab)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=10,
                        outline=(200, 206, 220, 200), width=2)
    for i in range(5):  # grip ridges
        y = 356 + i * 14
        d.line([(40, y), (w - 40, y)], fill=(30, 34, 48, 220), width=5)
    return img


def gamecard_shape(label_text):
    """A 3DS-style game card: small light card with a notched edge and a
    printed label. Reads as a game card, not a disc."""
    w, h = 320, 340
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([0, 0, w, h], radius=18, fill=(226, 229, 236, 255))
    d.rounded_rectangle([0, 0, w, h], radius=18, outline=(160, 166, 180, 255), width=3)
    # the card's signature notch, cut out of the top-right edge
    d.rectangle([w - 66, 0, w - 34, 24], fill=(0, 0, 0, 0))
    lx, ly, lw, lh = 22, 56, w - 44, 200
    lab = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ll = ImageDraw.Draw(lab)
    _label_art(ll, lx, ly, lw, lh, seed=20)
    fnt = ImageFont.truetype(marker, 24)
    bb = fnt.getbbox(label_text)
    while bb[2] - bb[0] > lw - 16 and fnt.size > 10:
        fnt = ImageFont.truetype(marker, fnt.size - 2)
        bb = fnt.getbbox(label_text)
    ll.text((lx + lw / 2, ly + lh - 28), label_text, font=fnt,
            fill=(255, 255, 255, 255), anchor="mm",
            stroke_width=2, stroke_fill=(10, 26, 92, 255))
    lmask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(lmask).rectangle([lx, ly, lx + lw, ly + lh], fill=255)
    lab.putalpha(ImageChops.multiply(lab.split()[3], lmask))
    img = Image.alpha_composite(img, lab)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([lx, ly, lx + lw, ly + lh], outline=(150, 156, 170, 220), width=2)
    ft = ImageFont.truetype(fb, 13)
    d.text((w / 2, h - 30), "NINTENDO 3DS", font=ft, fill=(90, 98, 115, 255), anchor="mm")
    # re-apply the notch over the composited label, then the body silhouette
    d.rectangle([w - 66, 0, w - 34, 24], fill=(0, 0, 0, 0))
    body_mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(body_mask).rounded_rectangle([0, 0, w, h], radius=18, fill=255)
    ImageDraw.Draw(body_mask).rectangle([w - 66, 0, w - 34, 24], fill=0)
    img.putalpha(ImageChops.multiply(img.split()[3], body_mask))
    return img


def umd_shape(label_text):
    """A PSP UMD: disc inside its signature shell with the offset hub
    window. Kept simple; the theme treats it generically like every
    other silhouette."""
    S = 440
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([10, 10, S - 10, S - 10], radius=60,
                        fill=(210, 216, 228, 235))
    disc = disc_shape(label_text, r=150)
    img.alpha_composite(disc, (int(S / 2 - disc.width / 2), int(S / 2 - disc.height / 2)))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([S / 2 - 46, S / 2 - 120, S / 2 + 46, S / 2 - 28],
                        radius=12, outline=(120, 128, 144, 255), width=4)
    body_mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(body_mask).rounded_rectangle([10, 10, S - 10, S - 10], radius=60, fill=255)
    img.putalpha(ImageChops.multiply(img.split()[3], body_mask))
    return img


SHAPE_FN = {"cartridge": cartridge_shape, "gamecard": gamecard_shape,
            "disc": disc_shape, "umd": umd_shape}[VARIANT]


def fit_shape(shape, box):
    s = min(box / shape.width, box / shape.height)
    return shape.resize((max(1, int(shape.width * s)), max(1, int(shape.height * s))),
                        Image.LANCZOS)


def silhouette_shadow(shape):
    """Soft contact shadow cast from the ACTUAL silhouette (mock
    art-direction intent; the real theme uses the generic soft shadow
    asset, which is shape-neutral)."""
    a = shape.split()[3]
    sh = Image.new("RGBA", shape.size, (6, 14, 44, 255))
    sh.putalpha(a.point(lambda v: int(v * 0.55)))
    return sh.filter(ImageFilter.GaussianBlur(16))


def yellow_highlight(shape):
    """ONE thin restrained yellow highlight on part of the silhouette
    (mock art-direction intent; the real theme carries the selective
    yellow accent on the hero plane, since ES-DE has no per-silhouette
    highlight mechanism)."""
    w, h = shape.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov, "RGBA")
    if VARIANT == "disc":
        r = w / 2 - 6
        a0, a1 = 200.0, 252.0
        a = a0
        while a < a1:
            t = (a - a0) / (a1 - a0)
            edge = min(1.0, t / 0.25, (1.0 - t) / 0.25)
            al = int(230 * max(0.0, min(1.0, edge)))
            if al > 2:
                d.arc([w / 2 - r, h / 2 - r, w / 2 + r, h / 2 + r],
                      start=a, end=a + 1.3, fill=YELLOW + (al,), width=4)
            a += 1.0
    else:
        # a short faded tick along the top edge of the silhouette
        x0, x1 = int(w * 0.18), int(w * 0.52)
        for x in range(x0, x1):
            t = (x - x0) / (x1 - x0)
            edge = min(1.0, t / 0.25, (1.0 - t) / 0.25)
            al = int(230 * max(0.0, min(1.0, edge)))
            d.line([(x, 7), (x, 11)], fill=YELLOW + (al,))
    # keep the highlight inside the silhouette
    ov.putalpha(ImageChops.multiply(ov.split()[3], shape.split()[3]))
    return ov

# ------------------------------------------------------------ base canvas ---
base = Image.open(os.path.join(ROOT, "art/gamelist_generic_bg.png")).convert("RGBA")
base = base.resize((W, H))
d = ImageDraw.Draw(base)
place(base, "./art/lib_bottom_gradient.png", el_box(get("image", "libBottomGradient")))
place(base, "./art/lib_panel_main.png", el_box(get("image", "libPanelMain")))
place(base, "./art/rails/%s.png" % G["system"], el_box(get("image", "libRail")))

# --------------------------------------- marquee: neutral stand-in ---
# The real theme binds the ACTUAL scraped marquee asset here
# (imageType=marquee). The mock shows a NEUTRAL stand-in: the game name
# in the Nova display face on open whitespace with the reusable framing
# (hairline rule + yellow tick). The v17 game-specific burst artwork is
# gone - the marquee's own artwork provides the personality on device.
mx, my, mw, mh = max_box(get("image", "libMarquee"))
mq = Image.new("RGBA", (int(mw), int(mh) + 14), (0, 0, 0, 0))
mqd = ImageDraw.Draw(mq, "RGBA")
_fm = ImageFont.truetype(marker, 64)
_bb = _fm.getbbox(G["title"])
while _bb[2] - _bb[0] > mw - 30 and _fm.size > 16:
    _fm = ImageFont.truetype(marker, _fm.size - 2)
    _bb = _fm.getbbox(G["title"])
mqd.text((mw / 2, mh * 0.42), G["title"], font=_fm, fill=(16, 52, 160, 255),
         anchor="mm")
_ft = ImageFont.truetype(fb, 15)
mqd.text((mw / 2, mh * 0.66), " ".join(G["system"].upper()), font=_ft,
         fill=(90, 110, 160, 230), anchor="mm")
mqd.line([(mw * 0.30, mh * 0.80), (mw * 0.70, mh * 0.80)],
         fill=YELLOW + (255,), width=3)
# soft lift off the page, shaped to the lockup
msh = Image.new("RGBA", mq.size, (0, 0, 0, 0))
_mmask = mq.split()[3].point(lambda v: 255 if v > 40 else 0)
_mbox = _mmask.getbbox()
if _mbox:
    ImageDraw.Draw(msh).rectangle(
        [_mbox[0] - 8, _mbox[1] - 4, _mbox[2] + 8, _mbox[3] + 10],
        fill=(6, 14, 44, 70))
    msh = msh.filter(ImageFilter.GaussianBlur(10))
    base.alpha_composite(msh, (int(mx), int(my)))
base.alpha_composite(mq, (int(mx), int(my)))
d = ImageDraw.Draw(base)

# ---------------------------------------------------------- metadata ---
def fake_text(el, lines, size, color, font=fr):
    x, y, w, h = el_box(el)
    fnt = ImageFont.truetype(font, size)
    yy = y
    for ln in lines:
        d.text((x, yy), ln, font=fnt, fill=color)
        yy += size + 7

desc = get("text", "libDesc")
fake_text(desc, G["desc"], 17, (58, 74, 115))
year = get("datetime", "libYear")
fake_text(year, [G["year"]], 57, (10, 47, 160), marker)
rx, ry, rw, rh = el_box(get("rating", "libRating"))
for i in range(4):
    star = Image.open(os.path.join(ROOT, "art/star_filled.png")).convert("RGBA").resize((26, 26))
    base.alpha_composite(star, (int(rx + i * 32), int(ry)))
fake_text(get("text", "libGenre"), [G["genre"]], 23, (10, 47, 160), fb)
fake_text(get("text", "libPlayers"), [G["players"]], 14, (58, 74, 115))
fake_text(get("text", "libDev"), [G["dev"]], 14, (58, 74, 115))

# ---------------------------------------------------------- screenshot ---
sx, sy, sw, sh = el_box(get("image", "libScreenshot"))
shot = Image.new("RGBA", (int(sw), int(sh)), (0, 0, 0, 0))
sd = ImageDraw.Draw(shot)
for yy in range(int(sh)):
    t = yy / sh
    col = (int(40 + 60 * t), int(90 + 70 * t), int(190 + 40 * t))
    sd.line([(0, yy), (sw, yy)], fill=col + (255,))
sd.ellipse([sw * 0.62, sh * 0.12, sw * 0.86, sh * 0.52], fill=(255, 236, 150, 255))
sd.polygon([(0, sh), (0, sh * 0.62), (sw * 0.4, sh * 0.5), (sw, sh * 0.72), (sw, sh)],
           fill=(36, 84, 60, 255))
base.alpha_composite(shot, (int(sx), int(sy)))

# ------------------------------------------------------------ hero column ---
# Shape-agnostic elevation: the hero plane behind, the restrained blue
# atmosphere, the strengthened generic contact shadow. No rim, no rings,
# no circular frame - the silhouette is the hero.
place(base, "./art/lib_plane_hero.png", el_box(get("image", "libPlaneHero")))
place(base, "./art/lib_glow_blue.png", el_box(get("image", "libSelectedGlowBlue")), 0.4)
# NOTE: the real theme draws the generic lib_shadow_soft ellipse here
# (opacity 0.9, shape-neutral). The mock renders the silhouette-cast
# shadow instead, per brief point 2 (shadow based on the actual visible
# silhouette) - see the module docstring.

car = get("carousel", "gameCarousel")
cx, cy = px(car.findtext("pos"))
cw, ch = sz(car.findtext("size"))
iw, ih = sz(car.findtext("itemSize"))
scale = float(car.findtext("itemScale"))
pitch = ch / float(car.findtext("maxItemCount"))
sel = iw * scale  # 540

SHAPE_FULL = SHAPE_FN(G["title"])

def dim(layer, op=0.45):
    a = layer.split()[3].point(lambda v: int(v * op))
    out = layer.copy()
    out.putalpha(a)
    # dim toward navy
    dark = Image.new("RGBA", layer.size, (10, 26, 92, 255))
    out = Image.alpha_composite(dark, out)
    out.putalpha(a)
    return out

# neighbours: the SAME shape as the selected system - smaller, dimmer,
# edge-cropped. Real navigation path, hero dominant.
nbr = fit_shape(SHAPE_FULL, iw)
for ncy in (cy - pitch, cy + pitch):
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    lay.alpha_composite(dim(nbr), (int(cx - nbr.width / 2), int(ncy - nbr.height / 2)))
    base = Image.alpha_composite(base, lay)

# selected hero: native silhouette at full scale, silhouette shadow for
# lift, generic blue atmosphere, ONE thin selective yellow highlight on
# part of the silhouette
hero = fit_shape(SHAPE_FULL, sel)
hl = yellow_highlight(hero)
hero = Image.alpha_composite(hero, hl)
sh_img = silhouette_shadow(hero)
shlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
shlay.alpha_composite(sh_img, (int(cx - sh_img.width / 2), int(cy - sh_img.height / 2 + 30)))
base = Image.alpha_composite(base, shlay)
hlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
hlay.alpha_composite(hero, (int(cx - hero.width / 2), int(cy - hero.height / 2)))
base = Image.alpha_composite(base, hlay)

# foreground shards crop the neighbours at the edges (above the carousel,
# exactly like the real z-order)
place(base, "./art/lib_shard_prev.png", el_box(get("image", "libShardPrev")))
place(base, "./art/lib_shard_next.png", el_box(get("image", "libShardNext")))
d = ImageDraw.Draw(base)

# title block: rule, display title, composite secondary line
place(base, "./art/lib_title_rule.png", el_box(get("image", "libTitleRule")))
te = get("text", "libGameName")
tx, ty, tw, th = el_box(te)
f5 = ImageFont.truetype(marker, 38)
_bb = f5.getbbox(G["title"])
while _bb[2] - _bb[0] > tw - 20 and f5.size > 16:
    f5 = ImageFont.truetype(marker, f5.size - 2)
    _bb = f5.getbbox(G["title"])
d.text((tx + tw / 2, ty + th / 2), G["title"], font=f5, fill="white", anchor="mm")
f7 = ImageFont.truetype(fb, 14)
parts = [("text", "libMetaGenre", G["genre"], 150),
         ("text", "libMetaSep1", "\u2022", 16),
         ("datetime", "libMetaYear", G["year"], 70),
         ("text", "libMetaSep2", "\u2022", 16),
         ("text", "libMetaDev", G["dev"], 120),
         ("text", "libMetaSep3", "\u2022", 16),
         ("text", "libMetaPlayers", G["players"], 90)]
for tag, name, label, _w in parts:
    ex, ey, ew, eh = el_box(get(tag, name))
    d.text((ex + ew / 2, ey + eh / 2), label, font=f7, fill=(255, 255, 255, 166), anchor="mm")
# footer
fe = get("text", "libFooter")
fx, fy, fw, fh = el_box(fe)
f6 = ImageFont.truetype(fr, 13)
d.text((fx + fw / 2, fy + fh / 2), "A PLAY \u2022 B BACK", font=f6, fill=(255, 255, 255, 128), anchor="mm")

base.convert("RGB").save(OUT)
print("mock ->", OUT)


# ------------------------------------------------------------- assertions ---
fails = []
def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)

# --- MACRO LAYOUT LOCK: the three major regions and the title zone ---
check(abs(sel - 540) < 2, f"selected hero {sel:.0f}px == 540 (scale preserved)")
check(abs(cx - 900) < 2 and abs(cy - 430) < 2, "selected centre (900,430)")
check(abs(float(get('carousel', 'gameCarousel').findtext("itemScale")) - 2.25) < 0.001, "itemScale 2.25")
check(abs(pitch - 480) < 1, f"carousel pitch {pitch:.0f}px == 480 (480*3=1440 element)")
prev_c = (cx, cy - pitch); next_c = (cx, cy + pitch)
check(abs(prev_c[0] - 900) < 2 and abs(prev_c[1] - (-50)) < 2, f"prev at ({prev_c[0]:.0f},{prev_c[1]:.0f})")
check(abs(next_c[0] - 900) < 2 and abs(next_c[1] - 910) < 2, f"next at ({next_c[0]:.0f},{next_c[1]:.0f})")
rbx, rby, rbw, rbh = el_box(get("image", "libRail"))
check(abs(rbx - 486) < 2 and abs(rbw - 60) < 2 and abs(rbh - 912) < 2, "spine 60x912 at x486 (unchanged)")
check(cx - sel / 2 > rbx + rbw + 40, "hero clear of spine (>=40px)")
pbx, pby, pbw, pbh = el_box(get("image", "libPanelMain"))
check(abs(pbx - 6) < 2 and abs(pby - 10) < 2 and abs(pbw - 470) < 2 and abs(pbh - 940) < 2,
      "panel box (6,10) 470x940 (unchanged)")
tbx, tby, tbw, tbh = el_box(get("image", "libTitleRule"))
check(abs(tby + tbh / 2 - 716) < 2, "title rule at Y716")
check(abs(ty + th / 2 - 736) < 2, "title at Y736")
mg0 = el_box(get("text", "libMetaGenre"))
check(abs(mg0[1] + mg0[3] / 2 - 757.5) < 3, "composite meta line at Y757")
check(abs(sx - 42) < 2 and abs(sy - 700) < 2 and abs(sw - 396) < 2 and abs(sh - 210) < 2,
      "screenshot window (42,700) 396x210 (unchanged)")
check(abs(fy + fh / 2 - 915) < 3, "footer at y915")

# --- brief point 1: no disc assumption anywhere in the hero ---
paths = " ".join(all_paths())
check(not has("image", "libSelectedRim"), "libSelectedRim element gone (no circular frame)")
check("lib_hero_rim" not in paths, "lib_hero_rim.png unreferenced")
check(not os.path.exists(os.path.join(ROOT, "art/lib_hero_rim.png")),
      "lib_hero_rim.png deleted from art/")
for dead in ["lib_hero_aura.png", "lib_hero_ring.png", "libSelectedAura",
             "libSelectedRing", "libSelectedGlow"]:
    check(dead not in paths and not has("image", dead),
          f"retired decoration stays retired: {dead}")
check(has("image", "libSelectedGlowBlue"), "generic blue atmosphere present (shape-neutral)")
check(has("image", "libSelectedShadow"), "generic contact shadow present (shape-neutral)")
check(abs(float(get("image", "libSelectedShadow").findtext("opacity")) - 0.9) < 0.01,
      "contact shadow strengthened (0.9)")

# --- brief point 2/3: the silhouette is the hero; highlight is selective ---
alpha = SHAPE_FULL.split()[3]
bbox = alpha.getbbox()
bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
cov = sum(1 for p in alpha.getdata() if p > 40) / (bw * bh)
if VARIANT == "cartridge":
    check(0.75 <= hero.width / hero.height <= 0.92,
          f"cartridge reads tall, not circular (aspect {hero.width/hero.height:.2f})")
    check(cov > 0.82, f"cartridge silhouette fills its box (coverage {cov:.2f}, not a disc)")
elif VARIANT == "gamecard":
    nx, ny = SHAPE_FULL.width - 50, 12  # inside the card's signature notch
    check(alpha.getpixel((nx, ny)) < 40,
          "game-card notch is truly cut out (transparent edge preserved)")
    check(cov > 0.82, f"game-card silhouette fills its box (coverage {cov:.2f})")
elif VARIANT == "disc":
    check(abs(bw - bh) <= 4, f"disc silhouette is circular (bbox {bw}x{bh})")
    check(0.75 <= cov <= 0.82, f"disc coverage {cov:.2f} (a circle, not a rounded box)")
# no full-circle yellow: the highlight must stay a selective accent
rgb = base.convert("RGB")
def _yellowish(p):
    return abs(p[0] - 255) < 30 and abs(p[1] - 214) < 45 and p[2] < 60
ann_in, ann_out, ann_y = sel / 2 - 34, sel / 2 + 34, 0
ann_n = 0
for yy in range(int(cy - ann_out), int(cy + ann_out)):
    for xx in range(int(cx - ann_out), int(cx + ann_out)):
        rr = math.hypot(xx - cx, yy - cy)
        if ann_in <= rr <= ann_out and 0 <= xx < W and 0 <= yy < H:
            ann_n += 1
            if _yellowish(rgb.getpixel((xx, yy))):
                ann_y += 1
check(ann_y / max(1, ann_n) < 0.12,
      f"no circular yellow frame: selective accent only ({ann_y/max(1,ann_n):.1%} of the annulus)")

# --- brief points 4/5: prev/next are shape-aware, edge-pushed, subordinate ---
nscale = iw / sel
check(0.40 <= nscale <= 0.60, f"neighbours ~44% hero scale ({nscale:.2f})")
check(abs(float(car.findtext("unfocusedItemOpacity")) - 0.45) < 0.01,
      "neighbours 45% opacity (40-55% band)")
prev_crop = (0 - (prev_c[1] - ih / 2)) / ih
next_crop = ((next_c[1] + ih / 2) - H) / ih
check(prev_crop >= 0.25, f"prev {prev_crop:.0%} cropped off the top edge (>=25%)")
check(next_crop >= 0.25, f"next {next_crop:.0%} cropped off the bottom edge (>=25%)")
# the shard veils the next item's upper-left while its lower-right stays
# exposed: the readable mass enters from the bottom-right corner.
# Measured directly on the shard alpha over the item's box.
shard_el = get("image", "libShardNext")
shx, shy, shw, shh = el_box(shard_el)
shard = Image.open(os.path.join(ROOT, "art/lib_shard_next.png")).convert("RGBA")
shard = shard.resize((int(shw), int(shh)), Image.LANCZOS)
sa = shard.split()[3]
sfull = Image.new("L", (W, H), 0)
sfull.paste(sa, (int(shx), int(shy)))
veil_ul = sfull.getpixel((850, 820))   # item's upper-left: should be veiled
veil_lr = sfull.getpixel((985, 945))   # item's lower-right: should stay readable
check(veil_ul > 50, f"shard veils the next item's upper-left (alpha {veil_ul})")
check(veil_lr < 50, f"next item's lower-right stays exposed (alpha {veil_lr})")
# and none of the next item's pixels intrude into the title band
nlay = Image.new("L", (W, H), 0)
nlay.paste(dim(nbr).split()[3],
           (int(next_c[0] - nbr.width / 2), int(next_c[1] - nbr.height / 2)))
in_title = [(x, y) for y in range(700, 771) for x in range(580, 1221)
            if nlay.getpixel((x, y)) > 40]
check(not in_title, f"title zone clear of next media ({len(in_title)} px intruding)")
check(next_c[1] - ih / 2 >= 770, "next item box starts below the title band (23px+ clear)")

# --- brief point 6: title area protected ---
check(next_c[1] - ih / 2 > mg0[1] + mg0[3] / 2 + 20,
      "clean air between the meta line and the next item")

# --- brief point 7: marquee is a neutral stand-in, no bespoke burst ---
def _burst_orange(p):
    return p[0] > 200 and 60 < p[1] < 170 and p[2] < 90
burst = sum(1 for yy in range(int(my), int(my + mh)) for xx in range(int(mx), int(mx + mw))
            if _burst_orange(rgb.getpixel((xx, yy))))
check(burst / (mw * mh) < 0.04,
      f"no game-specific burst artwork in the marquee zone ({burst/(mw*mh):.1%} orange)")

# --- brief point 8: left panel direction kept ---
check(not has("image", "libModMasthead") and not has("image", "libModMeta")
      and not has("image", "libModShot"), "no stacked cards: modules stay gone")
dx_, dy_, dw_, dh_ = el_box(get("text", "libDesc"))
check(abs(dx_ - 48) < 2, f"description aligned to the baked kickers (x={dx_:.0f})")

# --- brief point 9: spine, dynamic binding, calmer decoration ---
check("${system.name}" in get("image", "libRail").findtext("path"),
      "spine art bound to ${system.name} (actual current system)")
rails = glob.glob(os.path.join(ROOT, "art/rails/*.png"))
check(len(rails) == 21, f"21 spine PNGs ({len(rails)})")
rail = Image.open(os.path.join(ROOT, "art/rails/%s.png" % G["system"])).convert("RGB")
def _is_yellow(p):
    return abs(p[0] - 255) < 20 and abs(p[1] - 214) < 30 and abs(p[2] - 10) < 30
yell = sum(1 for y in range(48, 885, 8) if _is_yellow(rail.getpixel((4, y))))
check(yell > 90, f"ONE continuous thin yellow structural line ({yell} samples)")

# --- hygiene: no amateur signals, no debug, bg + system view untouched ---
check("lib_glow_yellow.png" not in paths, "no giant yellow glow asset")
check(abs(float(get("text", "libFooter").findtext("fontSize")) - 0.0135) < 0.001,
      "footer extremely quiet (0.0135)")
dbg = sum(1 for p in rgb.getdata()
          if (p[0] > 240 and p[1] < 20 and p[2] > 240) or (p[0] < 20 and p[1] > 240 and p[2] > 240))
check(dbg == 0, f"no debug magenta/cyan pixels ({dbg})")
import hashlib, subprocess
bg = hashlib.sha256(open(os.path.join(ROOT, "art/gamelist_generic_bg.png"), "rb").read()).hexdigest()
bg_head = subprocess.run(["git", "-C", os.path.expanduser("~/workspace/crystal-esde-theme"),
                          "show", "HEAD:theme-src/crystal/art/gamelist_generic_bg.png"],
                         capture_output=True).stdout
check(bg == hashlib.sha256(bg_head).hexdigest(), "gamelist_generic_bg.png unchanged")
rc = subprocess.run(["git", "-C", os.path.expanduser("~/workspace/crystal-esde-theme"),
                     "diff", "--quiet", "HEAD", "--",
                     "theme-src/crystal/cards", "theme-src/crystal/art/poster_on"]).returncode
check(rc == 0, "system-view cards/posters byte-identical to HEAD")
sysxml_head = subprocess.run(["git", "-C", os.path.expanduser("~/workspace/crystal-esde-theme"),
                              "show", "HEAD:theme-src/crystal/views.xml"],
                             capture_output=True, text=True).stdout
def _sysview(s):
    mm = re.search(r'<view name="system">.*?</view>', s, re.S)
    return mm.group(0) if mm else ""
check(_sysview(open(os.path.join(ROOT, "views.xml")).read()) == _sysview(sysxml_head),
      "system view section byte-identical to HEAD")

print("FAILURES:", len(fails))
sys.exit(1 if fails else 0)
