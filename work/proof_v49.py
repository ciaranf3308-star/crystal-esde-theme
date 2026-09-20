#!/usr/bin/env python3
"""PIL proof of the Crystal v4.9.0 library hero view at 1280x960.

v4.9.0: carousel is physical media ONLY (disk/cart/3D box — never box
art). The selected game's scraped cover renders as a separate hero
overlay pixel-aligned to the 1.9x selected slot; with no scraped art the
overlay draws nothing and the selected disk shows through.

  proof_v49_hero.png  - n64: carts in carousel, scraped cover hero on selected
  proof_v49_noart.png - n64: no scraped art, selected disk stays visible
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from proof_v47 import (make_n64_cart, make_boxart, draw_footer, dejavu, marker,
                       W, H, ROOT, OUT, nx, ny)

TINT = Image.open(os.path.join(ROOT, "art", "lib_blue_tint.png")).convert("RGBA")

def compose(system, labels, scraped_cover, out_name):
    bg = Image.open(os.path.join(ROOT, "backgrounds", f"{system}.webp")
                    ).convert("RGBA").resize((W, H))
    bg = Image.alpha_composite(bg, TINT.resize((W, H)))
    d = ImageDraw.Draw(bg)

    c_cx, c_cy = nx(0.5), ny(0.465)
    iw, ih = nx(0.18), ny(0.185)
    sw, sh = int(iw * 1.9), int(ih * 1.9)
    gap = nx(0.18)

    # Carousel: physical media only — all three slots are carts.
    left = make_n64_cart(labels[0], iw, ih)
    right = make_n64_cart(labels[2], iw, ih)
    sel_disk = make_n64_cart(labels[1], sw, sh)
    for cart, cx in ((left, c_cx - gap), (right, c_cx + gap)):
        grey = Image.new("RGBA", cart.size, (90, 90, 110, 255))
        bg.alpha_composite(Image.blend(cart, grey, 0.22), (cx - iw // 2, c_cy - ih // 2))
    bg.alpha_composite(sel_disk, (c_cx - sw // 2, c_cy - sh // 2))

    # selectedArtwork overlay (z52): scraped cover, pixel-aligned to the
    # selected slot; draws nothing when there is no scraped art.
    if scraped_cover:
        hero = make_boxart(labels[1], sw, sh)
        bg.alpha_composite(hero, (c_cx - sw // 2, c_cy - sh // 2))

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

    bg.convert("RGB").save(os.path.join(OUT, out_name))
    print("wrote", out_name)

if __name__ == "__main__":
    labels = ["Castlevania", "Bomberman 64", "Battle for Naboo"]
    compose("n64", labels, True, "proof_v49_hero.png")
    compose("n64", labels, False, "proof_v49_noart.png")
