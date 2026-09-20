#!/usr/bin/env python3
"""Crystal v3.6.0 'Showpiece' — visual polish flex pass.

Rebuilds the carousel-zone assets from scratch:

1. CARDS (theme-src/crystal/cards/*.png) — trading-card redesign:
   - white rounded border, deep-blue body with vertical gradient
   - bold white title plate with blue offset shadow (legible at a glance)
   - thin white rule under the title, subtle halftone texture
   - larger blue-duotone hardware render with a soft floor shadow
   - manufacturer small-caps tag at the bottom
2. STAGE (theme-src/crystal/art/carousel_vignette.png) — glossy deep-blue
   floor instead of the flat dark band:
   - royal-blue -> deep-navy vertical gradient
   - bright top-edge highlight + soft glow (the 'horizon' cards sit on)
   - halftone dots fading with depth, faint diagonal speed lines
   - baked horizontal edge falloff (outer cards recede = fake depth curve)
3. HALO (theme-src/crystal/art/selected_halo.png) — radial blue-white glow
   placed statically behind the carousel's center slot (the selected card is
   always centered, so this is a permanent spotlight on the hero card).
   Fades fully to transparent at the edges: no opaque rects, ever (v3.5 lesson).
"""
import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose_v3 import SYSTEMS, load_fg  # noqa: E402  (import-safe: main() guarded)

REPO = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal'
CARD_DIR = os.path.join(REPO, 'cards')
ART_DIR = os.path.join(REPO, 'art')
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

DEEP = (10, 47, 160)
WHITE = (255, 255, 255)


def rounded_mask(size, radius):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0], size[1]], radius, fill=255)
    return m


def tracked_text(draw, xy, text, font, fill, tracking=2):
    """Draw text with manual letter tracking."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += int(font.getlength(ch)) + tracking
    return x


def build_card(sys, meta):
    W, H = 400, 424
    card = Image.new('RGBA', (W, H), WHITE + (255,))

    # body: blue vertical gradient
    body = Image.new('RGBA', (W - 28, H - 28), (0, 0, 0, 0))
    bw, bh = body.size
    px = body.load()
    top = (58, 111, 245)
    bot = (11, 44, 143)
    for y in range(bh):
        t = y / max(bh - 1, 1)
        # slight ease for a richer top
        t = t * t * 0.35 + t * 0.65
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        for x in range(bw):
            px[x, y] = c + (255,)
    d = ImageDraw.Draw(body, 'RGBA')
    # halftone: subtle white dots, denser near top
    for yy in range(14, bh, 20):
        for xx in range(14, bw, 20):
            depth = 1 - yy / bh
            r = 1.5 + 2.0 * depth
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(255, 255, 255, int(26 * depth + 6)))
    # faint diagonal speed lines
    for i in range(5):
        x0 = 30 + i * 90
        d.line([x0, 40, x0 + 130, 200], fill=(255, 255, 255, 6), width=5)

    card.alpha_composite(body, (14, 14))
    d = ImageDraw.Draw(card, 'RGBA')

    # title with deep-blue offset shadow
    name = meta['card']
    size = 46
    f = ImageFont.truetype(FB, size)
    while f.getlength(name) > 336 and size > 20:
        size -= 2
        f = ImageFont.truetype(FB, size)
    tw = f.getlength(name)
    tx = (W - tw) / 2
    d.text((tx + 3, 17 + 3), name, font=f, fill=(6, 26, 110, 255))
    d.text((tx, 17), name, font=f, fill=WHITE + (255,))
    # thin rule under title
    d.line([52, 74, 348, 74], fill=(255, 255, 255, 120), width=2)

    # hardware with soft floor shadow
    fg = load_fg(meta['fg'])
    w, h = fg.size
    s = min(330 / w, 262 / h)
    fg = fg.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
    fw, fh = fg.size
    cx, cy = 200, 232  # optical center of body region
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.ellipse([cx - fw * 0.40, cy + fh * 0.32, cx + fw * 0.40, cy + fh * 0.52],
               fill=(4, 12, 60, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    card.alpha_composite(sh)
    card.alpha_composite(fg, (int(cx - fw / 2), int(cy - fh / 2)))

    # manufacturer tag
    mfr = meta['mfr']
    if mfr:
        fm = ImageFont.truetype(FB, 19)
        label = mfr.upper()
        total = sum(fm.getlength(c) for c in label) + 2 * (len(label) - 1)
        x = (W - total) / 2
        tracked_text(d, (x, 384), label, fm, (255, 255, 255, 235), tracking=2)

    card.putalpha(rounded_mask((W, H), 24))
    card.save(os.path.join(CARD_DIR, f'{sys}.png'))
    print(' card', sys)


def build_default_card():
    W, H = 400, 424
    card = Image.new('RGBA', (W, H), WHITE + (255,))
    body = Image.new('RGBA', (W - 28, H - 28), (0, 0, 0, 0))
    bw, bh = body.size
    px = body.load()
    for y in range(bh):
        t = y / max(bh - 1, 1)
        c = (int(58 + (11 - 58) * t), int(111 + (44 - 111) * t), int(245 + (143 - 245) * t))
        for x in range(bw):
            px[x, y] = c + (255,)
    card.alpha_composite(body, (14, 14))
    d = ImageDraw.Draw(card, 'RGBA')
    f = ImageFont.truetype(FB, 44)
    t = 'CRYSTAL'
    d.text(((W - f.getlength(t)) / 2 + 3, 20), t, font=f, fill=(6, 26, 110, 255))
    d.text(((W - f.getlength(t)) / 2, 17), t, font=f, fill=WHITE + (255,))
    d.line([52, 74, 348, 74], fill=(255, 255, 255, 120), width=2)
    # simple crown mark
    cx = 200
    pts = [(cx - 62, 250), (cx - 62, 195), (cx - 31, 222), (cx, 182),
           (cx + 31, 222), (cx + 62, 195), (cx + 62, 250)]
    d.polygon(pts, fill=WHITE + (255,))
    d.rectangle([cx - 62, 258, cx + 62, 274], fill=WHITE + (255,))
    fm = ImageFont.truetype(FB, 19)
    label = 'RETRO'
    total = sum(fm.getlength(c) for c in label) + 2 * (len(label) - 1)
    tracked_text(d, ((W - total) / 2, 384), label, fm, (255, 255, 255, 235), tracking=2)
    card.putalpha(rounded_mask((W, H), 24))
    card.save(os.path.join(CARD_DIR, '_default.png'))
    print(' card _default')


def build_stage():
    W, H = 1920, 360
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = img.load()
    stops = [(0.0, (34, 76, 196)), (0.45, (16, 48, 138)), (1.0, (5, 13, 48))]
    for y in range(H):
        t = y / (H - 1)
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                k = (t - t0) / max(t1 - t0, 1e-6)
                col = tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
                break
        for x in range(W):
            px[x, y] = col + (255,)
    # baked center spotlight: soft radial lift behind the selected card's
    # slot (carousel center y 0.8155 -> 0.508 of stage height). Wide smooth
    # falloff so there is no visible boundary — felt, not seen.
    gc_x, gc_y, gc_r = W / 2, H * 0.508, W * 0.28
    for y in range(H):
        for x in range(W):
            r = math.hypot(x - gc_x, y - gc_y) / gc_r
            if r < 1:
                k = (1 - r) ** 2.6
                lift = int(52 * k)
                pr, pg, pb, _ = px[x, y]
                px[x, y] = (min(255, pr + lift), min(255, pg + lift),
                            min(255, pb + int(lift * 1.25)), 255)
    d = ImageDraw.Draw(img, 'RGBA')
    # top-edge horizon highlight + soft glow
    d.rectangle([0, 0, W, 3], fill=(235, 244, 255, 160))
    for y in range(4, 40):
        a = int(60 * (1 - y / 40) ** 1.8)
        d.line([0, y, W, y], fill=(150, 190, 255, a))
    # halftone: lower two-thirds, staggered rows, fading with depth
    row = 0
    for yy in range(120, H, 24):
        off = 12 if row % 2 else 0
        for xx in range(12 + off, W, 24):
            depth = 1 - yy / H
            r = 2 + 2 * depth
            d.ellipse([xx - r, yy - r, xx + r, yy + r],
                      fill=(255, 255, 255, int(5 + 12 * depth)))
        row += 1
    # horizontal edge falloff: outer cards recede (fake depth curve)
    alpha = img.getchannel('A')
    rgb = img.convert('RGB')
    arr = bytearray(rgb.tobytes())
    for x in range(W):
        edge = abs(x / W - 0.5) * 2          # 0 center -> 1 edge
        k = 1.0 - 0.45 * max(0.0, (edge - 0.45) / 0.55) ** 1.6
        for y in range(H):
            o = (y * W + x) * 3
            arr[o] = int(arr[o] * k)
            arr[o + 1] = int(arr[o + 1] * k)
            arr[o + 2] = int(arr[o + 2] * k)
    img = Image.frombytes('RGB', (W, H), bytes(arr)).convert('RGBA')
    img.putalpha(alpha)
    img.save(os.path.join(ART_DIR, 'carousel_vignette.png'))
    print(' stage carousel_vignette.png', img.size)


def build_halo():
    S = 640
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    px = img.load()
    c = S / 2
    for y in range(S):
        for x in range(S):
            r = math.hypot(x - c, y - c) / c   # 0 center -> 1 edge
            if r >= 1:
                continue
            k = (1 - r) ** 1.7
            # white core -> crystal blue -> transparent
            if r < 0.45:
                col = (255, 255, 255, int(135 * k))
            else:
                col = (130, 175, 255, int(85 * k))
            px[x, y] = col
    img = img.filter(ImageFilter.GaussianBlur(6))
    img.save(os.path.join(ART_DIR, 'selected_halo.png'))
    print(' halo selected_halo.png', img.size)


if __name__ == '__main__':
    os.makedirs(CARD_DIR, exist_ok=True)
    os.makedirs(ART_DIR, exist_ok=True)
    for sys, meta in SYSTEMS.items():
        build_card(sys, meta)
    build_default_card()
    build_stage()
    # v3.6.0 final: the spotlight is baked into the stage (no separate halo
    # element — one asset, zero boundary risk). Remove any stale halo file.
    stale = os.path.join(ART_DIR, 'selected_halo.png')
    if os.path.exists(stale):
        os.remove(stale)
    print('DONE')
