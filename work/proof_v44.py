#!/usr/bin/env python3
"""Crystal v4.4.0 proof mock — "Select" system carousel.

v4.3.0 geometry plus the per-system selectedPoster overlay (z55, above the
z45 carousel): the selected slot shows the vivid supplied poster for the 7
poster systems; every unselected entry keeps the generic black marquee card.

Overlay geometry mirrors the engine math exactly:
  selected center = (0.5*W, 0.640*H + 0.360*H/2 - 0.008*H) = (640, 779.5)
  overlay size   = 0.19*W x 0.338*H = 243.2 x 324.5 (the 2x selected card)
The overlay is a system-view image element, so (like the real engine) it is
NOT clipped to the carousel rect — only the carousel layer is.

Usage: proof_v44.py <system> -> work/proofs/carousel_select_v44_<sys>.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proof_v43 as p43  # noqa: E402
from PIL import Image, ImageDraw, ImageChops  # noqa: E402

W, H = p43.W, p43.H
CRYSTAL = p43.CRYSTAL
POSTER_SYSTEMS = {'genesis', 'ps2', 'dreamcast', 'psx', 'megadrive', 'n64', 'gc'}


def render(sys, out):
    # Base: full v4.3.0 render (background, text, vignette, glow, carousel).
    # Reuse its layering by calling its internals via a temp file is awkward,
    # so replicate: call p43.render to a temp PNG, then add the overlay.
    tmp = '/tmp/proof_v44_base.png'
    p43.render(sys, tmp)
    bg = Image.open(tmp).convert('RGBA')

    if sys in POSTER_SYSTEMS:
        poster = Image.open(
            os.path.join(CRYSTAL, 'art', 'poster_on', f'{sys}.png')).convert('RGBA')
        ow, oh = int(0.19 * W), int(0.338 * H)          # 243 x 324
        poster = poster.resize((ow, oh), Image.LANCZOS)
        poster = p43.p40.rounded(poster, int(0.008 * W))  # cornerRadius 0.008
        # Engine-exact selected-slot center (matches carouselGlow at 0.5 0.812).
        cx, cy = int(0.5 * W - ow / 2), int(0.812 * H - oh / 2)
        bg.alpha_composite(poster, (cx, cy))

    bg.convert('RGB').save(out, 'PNG')
    print(f'saved {out}')


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'n64'
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proofs')
    os.makedirs(outdir, exist_ok=True)
    render(target, os.path.join(outdir, f'carousel_select_v44_{target}.png'))
