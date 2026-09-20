#!/usr/bin/env python3
"""PIL proof of the Crystal v4.7.0 library hero view at 1280x960.

Matches theme-src/crystal/views.xml gamelist geometry per the user mockup:
  proof_v47_hero.png    - n64 (baked footer in bg): carousel, white scrim,
                          navy marker title, dark metadata line
  proof_v47_boxart.png  - same, selected slot shows scraped boxart
  proof_v47_gb.png      - gb (no baked footer): live per-system footer hints
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 960
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "theme-src", "crystal")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proofs")
os.makedirs(OUT, exist_ok=True)

def nx(x): return int(x * W)
def ny(y): return int(y * H)

def dejavu(sz, bold=True):
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), sz)

def marker(sz):
    return ImageFont.truetype(os.path.join(ROOT, "fonts", "PermanentMarker-Regular.ttf"), sz)

def make_n64_cart(label, w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = (148, 152, 158)
    dark = (110, 114, 120)
    d.rounded_rectangle([0, 0, w, h], radius=int(h * 0.09), fill=body + (255,))
    d.rounded_rectangle([int(w*0.08), int(h*0.80), int(w*0.92), h], radius=int(h*0.04),
                        fill=dark + (255,))
    for x in range(int(w*0.12), int(w*0.88), max(8, int(w*0.055))):
        d.rectangle([x, int(h*0.84), x + int(w*0.028), int(h*0.94)], fill=(210, 170, 90, 255))
    lx0, ly0, lx1, ly1 = int(w*0.16), int(h*0.14), int(w*0.84), int(h*0.74)
    d.rounded_rectangle([lx0, ly0, lx1, ly1], radius=int(h*0.05), fill=(245, 245, 245, 255))
    d.rounded_rectangle([lx0, ly0, lx1, ly0 + int(h*0.16)], radius=int(h*0.05),
                        fill=(10, 47, 160, 255))
    d.rectangle([lx0, ly0 + int(h*0.10), lx1, ly0 + int(h*0.16)], fill=(10, 47, 160, 255))
    fs = max(10, int(h * 0.075))
    d.text(((lx0+lx1)//2, (ly0+ly1)//2 + int(h*0.06)), label, font=dejavu(fs),
           anchor="mm", fill=(10, 47, 160, 255))
    d.rounded_rectangle([int(w*0.06), int(h*0.03), int(w*0.94), int(h*0.10)],
                        radius=int(h*0.03), fill=(255, 255, 255, 60))
    return im

def make_gb_cart(label, w, h):
    """Stand-in Game Boy cart: tall grey cart with label."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], radius=int(w*0.06), fill=(150, 150, 155, 255))
    d.rounded_rectangle([int(w*0.12), int(h*0.06), int(w*0.88), int(h*0.62)],
                        radius=int(w*0.04), fill=(240, 240, 240, 255))
    fs = max(9, int(w * 0.10))
    d.text((w//2, int(h*0.30)), label, font=dejavu(fs), anchor="mm", fill=(30, 30, 40, 255))
    d.rectangle([int(w*0.2), int(h*0.80), int(w*0.8), int(h*0.92)], fill=(105, 105, 110, 255))
    return im

def make_boxart(label, w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], radius=10, fill=(18, 52, 140, 255))
    d.rounded_rectangle([8, 8, w-8, int(h*0.72)], radius=6, fill=(90, 140, 230, 255))
    d.ellipse([w*0.30, h*0.12, w*0.70, h*0.42], fill=(255, 214, 10, 255))
    fs = max(12, int(w * 0.09))
    d.text((w//2, int(h*0.84)), label, font=marker(fs), anchor="mm", fill=(255, 255, 255, 255))
    return im

def draw_footer(d, navy=(10, 47, 160, 255)):
    bf, wf = dejavu(int(0.020 * H)), dejavu(int(0.016 * H), bold=False)
    for badge, word, bx, wx in (("A", "SELECT", 0.047, 0.072),
                                ("B", "BACK", 0.129, 0.154),
                                ("Y", "OPTIONS", 0.211, 0.236)):
        bw, bh = nx(0.030), ny(0.040)
        cx, cy = nx(bx), ny(0.955)
        d.ellipse([cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2],
                  fill=(255, 255, 255, 255))
        d.text((cx, cy), badge, font=bf, anchor="mm", fill=navy)
        d.text((nx(wx), cy), word, font=wf, anchor="lm", fill=(255, 255, 255, 255))

def compose(system, cart_fn, labels, boxart_hero=False, live_footer=False,
            out_name="proof_v47_hero.png"):
    bg = Image.open(os.path.join(ROOT, "backgrounds", f"{system}.webp")
                    ).convert("RGBA").resize((W, H))
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

    # white scrim behind the title block (libScrim, z5)
    scrim = Image.open(os.path.join(ROOT, "art", "lib_scrim.png")).convert("RGBA")
    scrim = scrim.resize((nx(0.66), ny(0.31)))
    bg.alpha_composite(scrim, (nx(0.5 - 0.33), ny(0.752 - 0.155)))

    # navy marker title
    tf = marker(int(0.068 * H))
    title = labels[1]
    d.text((W // 2, ny(0.735)), title, font=tf, anchor="mm", fill=(10, 47, 160, 255))

    # dark metadata line
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

if __name__ == "__main__":
    compose("n64", make_n64_cart, ["Castlevania", "Bomberman 64", "Battle for Naboo"],
            False, False, "proof_v47_hero.png")
    compose("n64", make_n64_cart, ["Castlevania", "Bomberman 64", "Battle for Naboo"],
            True, False, "proof_v47_boxart.png")
    compose("gb", make_gb_cart, ["Tetris", "Super Mario Land", "Kirby's Dream Land"],
            False, True, "proof_v47_gb.png")
