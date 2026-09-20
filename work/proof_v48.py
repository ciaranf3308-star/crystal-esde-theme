#!/usr/bin/env python3
"""PIL proof of the Crystal v4.8.0 gamelist blue wash at 1280x960.

v4.8.0 adds libBlueTint (art/lib_blue_tint.png, z2) over the per-system
background (z1); carousel/title/metadata stay above it, untinted.
Renders n64, gb, psx plus an n64 before/after strip.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from proof_v47 import compose as compose47, make_n64_cart, make_gb_cart, W, H, ROOT, OUT, nx, ny

TINT = Image.open(os.path.join(ROOT, "art", "lib_blue_tint.png")).convert("RGBA")

def tinted_bg(system):
    bg = Image.open(os.path.join(ROOT, "backgrounds", f"{system}.webp")
                    ).convert("RGBA").resize((W, H))
    wash = TINT.resize((W, H))
    return Image.alpha_composite(bg, wash)

# Monkey-patch compose's background step by pre-tinting: simplest is to
# replicate compose here with the tinted background.
from PIL import ImageDraw, ImageFont
from proof_v47 import make_boxart, draw_footer, dejavu, marker

def compose(system, cart_fn, labels, boxart_hero=False, live_footer=False,
            out_name="proof_v48.png", tint=True):
    bg = Image.open(os.path.join(ROOT, "backgrounds", f"{system}.webp")
                    ).convert("RGBA").resize((W, H))
    if tint:
        bg = Image.alpha_composite(bg, TINT.resize((W, H)))
    d = ImageDraw.Draw(bg)

    c_cx, c_cy = nx(0.5), ny(0.465)
    iw, ih = nx(0.18), ny(0.185)
    sw, sh = int(iw * 1.9), int(ih * 1.9)
    gap = nx(0.18)

    left = cart_fn(labels[0], iw, ih)
    right = cart_fn(labels[2], iw, ih)
    sel = make_boxart(labels[1], sw, sh) if boxart_hero else cart_fn(labels[1], sw, sh)

    for cart, cx in ((left, c_cx - gap), (right, c_cx + gap)):
        grey = Image.new("RGBA", cart.size, (90, 90, 110, 255))
        dim = Image.blend(cart, grey, 0.22)
        bg.alpha_composite(dim, (cx - iw // 2, c_cy - ih // 2))
    bg.alpha_composite(sel, (c_cx - sw // 2, c_cy - sh // 2))

    cf = dejavu(58, bold=False)
    d.text((nx(0.030), c_cy), "<", font=cf, anchor="mm", fill=(255, 255, 255, 255))
    d.text((nx(0.970), c_cy), ">", font=cf, anchor="mm", fill=(255, 255, 255, 255))

    scrim = Image.open(os.path.join(ROOT, "art", "lib_scrim.png")).convert("RGBA")
    scrim = scrim.resize((nx(0.66), ny(0.31)))
    bg.alpha_composite(scrim, (nx(0.5 - 0.33), ny(0.752 - 0.155)))

    tf = marker(int(0.068 * H))
    d.text((W // 2, ny(0.735)), labels[1], font=tf, anchor="mm", fill=(10, 47, 160, 255))

    mf = dejavu(int(0.0165 * H), bold=False)
    ink = (58, 74, 115, 255)
    for text, x, w_ in [("Action", 0.28, 0.10), ("•", 0.38, 0.02), ("1997", 0.40, 0.065),
                        ("•", 0.465, 0.02), ("Hudson Soft", 0.485, 0.12),
                        ("•", 0.605, 0.02), ("1-4 Players", 0.625, 0.095)]:
        d.text((nx(x + w_ / 2), ny(0.808)), text, font=mf, anchor="mm", fill=ink)

    if live_footer:
        draw_footer(d)

    bg.convert("RGB").save(os.path.join(OUT, out_name))
    print("wrote", out_name)
    return bg

if __name__ == "__main__":
    compose("n64", make_n64_cart, ["Castlevania", "Bomberman 64", "Battle for Naboo"],
            False, False, "proof_v48_n64.png")
    compose("gb", make_gb_cart, ["Tetris", "Super Mario Land", "Kirby's Dream Land"],
            False, True, "proof_v48_gb.png")
    compose("psx", make_n64_cart, ["Crash", "Metal Gear Solid", "Spyro"],
            False, True, "proof_v48_psx.png")
    # before/after strip for n64
    before = compose("n64", make_n64_cart, ["Castlevania", "Bomberman 64", "Battle for Naboo"],
                     False, False, "proof_v48_before.png", tint=False)
    after = Image.open(os.path.join(OUT, "proof_v48_n64.png"))
    strip = Image.new("RGB", (W, H))
    strip.paste(before.convert("RGB").resize((W // 2, H)), (0, 0))
    strip.paste(after.resize((W // 2, H)), (W // 2, 0))
    d = ImageDraw.Draw(strip)
    lab = dejavu(28)
    d.text((W // 4, 30), "BEFORE", font=lab, anchor="mm", fill=(255, 255, 255, 255))
    d.text((3 * W // 4, 30), "AFTER (blue wash)", font=lab, anchor="mm", fill=(255, 255, 255, 255))
    strip.save(os.path.join(OUT, "proof_v48_compare.png"))
    print("wrote proof_v48_compare.png")
