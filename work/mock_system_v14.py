#!/usr/bin/env python3
"""Crystal v14.0.0 system-view PIL mock + check suite.

Renders the REAL system-view carousel geometry parsed from
theme-src/crystal/views.xml (pos/size/itemSize/itemScale/maxItemCount,
selectedItemOffset, dimming/saturation/opacity) at 1280x960 with the real
card PNGs, then runs assertion checks:

  1. carousel composition matches the XML (7 items, selected 2x at center)
  2. selected item full-color and dominant (size + brightness delta)
  3. non-selected items heavily dimmed toward dark navy (sampled pixels:
     mean luminance below a strict threshold, blue-dominant hue)
  4. correct poster->system mapping for all 9 (cards match independent
     re-resize of the user-supplied posters; differ from v13 marquee cards)
  5. the 12 poster-less systems fall back to their marquee cards
     (byte-identical to HEAD, loadable, non-blank, no debug pixels)
  6. no debug circles / placeholder graphics in any card
  7. v13 gamelist work untouched (gamelist XML section, lib_*, rails,
     gamelist_generic_bg byte-identical to HEAD)

This is a PIL mock, never an "ES-DE screenshot". ES-DE 3.4.1 has no theme
keyframes/idle animation; none is claimed or simulated.
"""
import math
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
CRYSTAL = os.path.join(REPO, "theme-src/crystal")
VIEWS = os.path.join(CRYSTAL, "views.xml")
W, H = 1280, 960

POSTER_SYSTEMS = ["n3ds", "gba", "gb", "nds", "snes", "wii", "wiiu", "n64", "gc"]
ROSTER = ["dreamcast", "gb", "gba", "gbc", "gc", "genesis", "megadrive",
          "n3ds", "n64", "nds", "nes", "ps2", "psp", "psx", "snes", "steam",
          "wii", "wiiu", "windows", "xbox", "xbox360"]
MARQUEE_SYSTEMS = [s for s in ROSTER if s not in POSTER_SYSTEMS]

FAILURES = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" ({detail})" if detail else ""))
    if not cond:
        FAILURES.append(name)


def git(*args):
    return subprocess.run(["git", "-C", REPO, *args],
                          capture_output=True, text=True)


def parse_carousel():
    tree = ET.parse(VIEWS)
    car = tree.find(".//view[@name='system']/carousel[@name='sysCarousel']")
    assert car is not None, "sysCarousel not found in views.xml"

    def f(tag):
        return float(car.find(tag).text.strip().split()[0])

    def f2(tag):
        return [float(x) for x in car.find(tag).text.strip().split()]

    return {
        "pos": f2("pos"), "size": f2("size"),
        "itemSize": f2("itemSize"), "itemScale": f("itemScale"),
        "maxItemCount": int(car.find("maxItemCount").text.strip()),
        "selOffset": f2("selectedItemOffset"),
        "opacity": f("unfocusedItemOpacity"),
        "saturation": f("unfocusedItemSaturation"),
        "dimming": f("unfocusedItemDimming"),
        "cornerRadius": f("imageCornerRadius"),
    }


def dim_card(im, saturation, dimming):
    """Model of ES-DE's unfocused treatment: desaturate, then scale brightness."""
    gray = np.asarray(im.convert("L"), dtype=np.float32)[..., None]
    arr = np.asarray(im.convert("RGB"), dtype=np.float32)
    arr = gray + (arr - gray) * saturation
    arr = np.clip(arr * (1.0 - dimming), 0, 255)
    return Image.fromarray(arr.astype("uint8"))


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


def main():
    cfg = parse_carousel()
    print("carousel config from views.xml:", cfg)

    # ---- check 1: XML values are the v14 truth ----
    check("xml pos 0 0.640", cfg["pos"] == [0.0, 0.640])
    check("xml size 1 0.360", cfg["size"] == [1.0, 0.360])
    check("xml itemSize 0.095 0.169", cfg["itemSize"] == [0.095, 0.169])
    check("xml itemScale 2.0", cfg["itemScale"] == 2.0)
    check("xml maxItemCount 7", cfg["maxItemCount"] == 7)
    check("xml unfocusedItemDimming 0.70 (massive)", cfg["dimming"] == 0.70,
          f"got {cfg['dimming']}")
    check("xml unfocusedItemSaturation 0.50", cfg["saturation"] == 0.50,
          f"got {cfg['saturation']}")
    check("xml unfocusedItemOpacity 0.92", cfg["opacity"] == 0.92)

    # ---- geometry at 1280x960 ----
    cx, cy = W * cfg["pos"][0], H * cfg["pos"][1]
    cw, ch = W * cfg["size"][0], H * cfg["size"][1]
    iw, ih = W * cfg["itemSize"][0], H * cfg["itemSize"][1]
    sw, sh = iw * cfg["itemScale"], ih * cfg["itemScale"]
    offx, offy = W * cfg["selOffset"][0], H * cfg["selOffset"][1]
    sel_cx, sel_cy = W / 2 + offx, cy + ch / 2 + offy
    print(f"items {iw:.1f}x{ih:.1f} -> selected {sw:.1f}x{sh:.1f}, "
          f"selected center ({sel_cx:.1f},{sel_cy:.1f})")

    # ---- base: real system background + text panel ----
    canvas = Image.open(os.path.join(CRYSTAL, "backgrounds/snes.webp")).convert("RGB")
    canvas = canvas.resize((W, H)).convert("RGBA")
    dr = ImageDraw.Draw(canvas, "RGBA")
    fb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    fr = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    dr.text((0.030 * W, 0.195 * H), "NINTENDO", font=ImageFont.truetype(fb, 17), fill=(10, 47, 160))
    dr.text((0.030 * W, 0.230 * H), "Super Nintendo", font=ImageFont.truetype(fb, 38), fill=(20, 30, 60))
    dr.text((0.030 * W, 0.404 * H), "16-bit legend. Mode 7 forever.",
            font=ImageFont.truetype(fr, 18), fill=(20, 30, 60))
    dr.text((0.030 * W, 0.530 * H), "128", font=ImageFont.truetype(fb, 52), fill=(20, 30, 60))
    dr.text((0.030 * W, 0.613 * H), "16-BIT \u2022 1991",
            font=ImageFont.truetype(fr, 16), fill=(180, 90, 10))

    # ---- vignette (z39) + glow (z40), real art ----
    vig = Image.open(os.path.join(CRYSTAL, "art/sys_vignette.png")).convert("RGBA")
    vig = vig.resize((W, int(0.400 * H)))
    canvas.alpha_composite(vig, (0, int(0.600 * H)))
    glow = Image.open(os.path.join(CRYSTAL, "art/carousel_glow.png")).convert("RGBA")
    glow = glow.resize((int(0.484 * W), int(0.479 * H)))
    canvas.alpha_composite(glow, (int(0.5 * W - glow.width / 2), int(0.812 * H - glow.height / 2)))

    # ---- carousel strip: 7 items, snes selected ----
    # (order is illustrative; the mock asserts geometry, not ES-DE sort order)
    strip = ["nes", "n64", "wii", "snes", "nds", "ps2", "gbc"]
    check("strip has 7 items, snes selected", len(strip) == 7 and strip[3] == "snes")
    check("strip mixes 4 poster + 3 marquee systems",
          sum(s in POSTER_SYSTEMS for s in strip) == 4 and
          sum(s in MARQUEE_SYSTEMS for s in strip) == 3, str(strip))

    total_w = 6 * iw + sw
    x0 = W / 2 - total_w / 2
    radius = int(cfg["cornerRadius"] * H)
    item_rects = []
    x = x0
    for i, sname in enumerate(strip):
        wpx, hpx = (sw, sh) if i == 3 else (iw, ih)
        ccx = x + wpx / 2
        ccy = sel_cy if i == 3 else cy + ch / 2
        left, top = ccx - wpx / 2, ccy - hpx / 2
        item_rects.append((sname, left, top, wpx, hpx, i == 3))
        x += wpx

    # scissor: ES-DE clips carousel children to the carousel rect
    scissor_top, scissor_bottom = cy, cy + ch
    base = canvas.convert("RGBA")
    drawn = {}
    for sname, left, top, wpx, hpx, selected in item_rects:
        card = Image.open(os.path.join(CRYSTAL, f"cards/{sname}.png")).convert("RGBA")
        card = card.resize((int(round(wpx)), int(round(hpx))), Image.Resampling.LANCZOS)
        if not selected:
            dim = dim_card(card, cfg["saturation"], cfg["dimming"]).convert("RGBA")
            dim.putalpha(dim.getchannel("A").point(lambda v: int(v * cfg["opacity"])))
            card = dim
        mask = rounded_mask(card.size, radius)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.paste(card, (int(round(left)), int(round(top))), mask)
        # apply scissor
        px = np.array(layer)
        sc = np.zeros((H, W), dtype=bool)
        sc[int(scissor_top):int(scissor_bottom), :] = True
        px[~np.repeat(sc[:, :, None], 4, axis=2)] = 0
        base = Image.alpha_composite(base, Image.fromarray(px))
        drawn[sname] = (left, top, wpx, hpx)

    out = base.convert("RGB")
    out.save(os.path.join(REPO, "work/proofs/mock_v14_full.png"))
    print("wrote work/proofs/mock_v14_full.png")

    # ---- check 2: selected composition ----
    left, top, wpx, hpx = drawn["snes"]
    check("selected card 243x324 (2x)", abs(wpx - 243.2) < 1 and abs(hpx - 324.5) < 1,
          f"{wpx:.1f}x{hpx:.1f}")
    check("selected centered x=640", abs(left + wpx / 2 - 640) < 1,
          f"cx={left + wpx/2:.1f}")
    check("selected center y=0.812", abs((top + hpx / 2) / H - 0.812) < 0.002,
          f"cy={(top + hpx/2)/H:.4f}")
    check("no card pixels above scissor top (no clipping)",
          all(top >= scissor_top - 1 for _, top, *_ in
              [r[1:] for r in [("x",) + v for v in drawn.values()]]))

    # ---- check 3: selected full color vs neighbours dimmed ----
    arr = np.asarray(out).astype(np.float32)

    def region_lum(r):
        name, left, top, wpx, hpx = r
        x1, y1 = int(left + wpx * 0.3), int(top + hpx * 0.3)
        x2, y2 = int(left + wpx * 0.7), int(top + hpx * 0.7)
        reg = arr[y1:y2, x1:x2]
        lum = 0.2126 * reg[..., 0] + 0.7152 * reg[..., 1] + 0.0722 * reg[..., 2]
        return lum.mean(), reg[..., 0].mean(), reg[..., 1].mean(), reg[..., 2].mean()

    sel_lum, *_ = region_lum(("snes",) + drawn["snes"])
    # compare against the SAME interior region of the card art (the art's
    # bright border frame raises its full-image mean; the interior is what
    # the mock's sampled region sees)
    art = Image.open(os.path.join(CRYSTAL, "cards/snes.png")).convert("RGB")
    art = art.resize((int(round(243.2)), int(round(324.5))), Image.Resampling.LANCZOS)
    oarr = np.asarray(art).astype(np.float32)
    x1, y1 = int(243.2 * 0.3), int(324.5 * 0.3)
    x2, y2 = int(243.2 * 0.7), int(324.5 * 0.7)
    oreg = oarr[y1:y2, x1:x2]
    art_region_lum = (0.2126 * oreg[..., 0] + 0.7152 * oreg[..., 1] + 0.0722 * oreg[..., 2]).mean()
    check("selected full-color (matches card art interior)",
          abs(sel_lum - art_region_lum) < 12, f"rendered {sel_lum:.1f} vs art {art_region_lum:.1f}")
    neigh_lums = [region_lum(("x",) + drawn[s])[0] for s in strip if s != "snes"]
    check("selected dominant over neighbours",
          sel_lum > max(neigh_lums) * 1.8,
          f"selected {sel_lum:.1f} vs brightest neighbour {max(neigh_lums):.1f}")

    # ---- check 4: non-selected heavily dimmed toward dark navy ----
    STRICT_LUM = 55.0
    for s in strip:
        if s == "snes":
            continue
        lum, r, g, b = region_lum((s,) + drawn[s])
        check(f"dimmed {s}: lum < {STRICT_LUM} (near-dark-navy)",
              lum < STRICT_LUM, f"lum={lum:.1f}")
        check(f"dimmed {s}: navy hue (B>R)", b > r, f"B={b:.1f} R={r:.1f}")

    # ---- check 5: poster->system mapping for all 9 ----
    MEDIA = os.path.expanduser("~/workspace/user/media_library/image")
    sys.path.insert(0, os.path.join(REPO, "work"))
    from gen_v14_assets import POSTERS
    for s, rel in POSTERS.items():
        src = Image.open(os.path.join(MEDIA, rel)).convert("RGB")
        expect = np.asarray(src.resize((240, 320), Image.Resampling.LANCZOS)).astype(np.float32)
        got = np.asarray(Image.open(os.path.join(CRYSTAL, f"cards/{s}.png")).convert("RGB")).astype(np.float32)
        diff = np.abs(expect - got).mean()
        check(f"mapping {s}: card matches supplied poster", diff < 3.0, f"meandiff={diff:.2f}")
        old = subprocess.run(["git", "-C", REPO, "show", f"HEAD:theme-src/crystal/cards/{s}.png"],
                             capture_output=True).stdout
        check(f"mapping {s}: replaced v13 marquee card",
              len(old) > 0 and old != open(os.path.join(CRYSTAL, f"cards/{s}.png"), "rb").read())

    # ---- check 6: 12 marquee systems fall back cleanly ----
    for s in MARQUEE_SYSTEMS:
        p = os.path.join(CRYSTAL, f"cards/{s}.png")
        ok = os.path.isfile(p)
        check(f"marquee {s}: card exists", ok)
        if not ok:
            continue
        im = Image.open(p)
        check(f"marquee {s}: 240x320", im.size == (240, 320), str(im.size))
        head = subprocess.run(["git", "-C", REPO, "show", f"HEAD:theme-src/crystal/cards/{s}.png"],
                              capture_output=True).stdout
        check(f"marquee {s}: byte-identical to v13", head == open(p, "rb").read())
        a = np.asarray(im.convert("RGB")).astype(np.float32)
        check(f"marquee {s}: non-blank", a.std() > 5, f"std={a.std():.1f}")
        neon = ((a[..., 0] > 250) & (a[..., 1] < 5) & (a[..., 2] > 250)).sum()
        check(f"marquee {s}: no debug-magenta pixels", neon == 0, f"count={neon}")

    # ---- check 7: no debug/placeholder graphics in the 9 new cards ----
    for s in POSTER_SYSTEMS:
        a = np.asarray(Image.open(os.path.join(CRYSTAL, f"cards/{s}.png")).convert("RGB")).astype(np.float32)
        neon = ((a[..., 0] > 250) & (a[..., 1] < 5) & (a[..., 2] > 250)).sum()
        cyan = ((a[..., 0] < 5) & (a[..., 1] > 250) & (a[..., 2] > 250)).sum()
        check(f"poster {s}: no debug pixels", neon == 0 and cyan == 0,
              f"magenta={neon} cyan={cyan}")
        lum = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]).mean()
        check(f"poster {s}: real art, not blank/black", lum > 5, f"lum={lum:.1f}")

    # ---- check 8: v13 gamelist work untouched ----
    head_views = subprocess.run(["git", "-C", REPO, "show", "HEAD:theme-src/crystal/views.xml"],
                                capture_output=True, text=True).stdout
    new_views = open(VIEWS).read()

    def gamelist_section(t):
        m = re.search(r'<view name="gamelist">.*', t, re.S)
        return m.group(0) if m else ""

    check("gamelist XML section byte-identical to v13",
          gamelist_section(head_views) == gamelist_section(new_views))
    for pat in ["theme-src/crystal/art/lib_", "theme-src/crystal/art/rails/",
                "theme-src/crystal/art/gamelist_generic_bg.png"]:
        r = git("diff", "--name-only", "HEAD", "--", pat)
        check(f"no changes under {pat}", r.stdout.strip() == "", r.stdout.strip()[:120])

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURES: {FAILURES}")
        sys.exit(1)
    print("ALL CHECKS PASS")


if __name__ == "__main__":
    main()
