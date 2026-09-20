#!/usr/bin/env python3
"""Crystal v4.3.0 — system-view carousel dressing.

1. art/carousel_glow.png — a soft radial spotlight that sits BEHIND the
   carousel at its horizontal center. The selected item is always centered,
   so this reads as a glow around the selected card. Cool white-blue,
   whisper-subtle: it must lift the card, not wash the background.

2. art/sys_vignette.png — a soft bottom-up dark vignette that gives the
   carousel zone a visual bed WITHOUT being a bar. Neutral black (NOT blue),
   max ~30% at the very bottom, feathered to transparent well above the
   carousel. The background stays fully visible through it.
"""
import os
from PIL import Image

ART = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal/art'


def radial_glow(w, h, inner=0.0, outer=1.0, peak=64, color=(190, 205, 255)):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = img.load()
    cx, cy = w / 2, h / 2
    for y in range(h):
        for x in range(w):
            dx = (x - cx) / (w / 2)
            dy = (y - cy) / (h / 2)
            r = min(1.0, (dx * dx + dy * dy) ** 0.5)
            if r >= outer:
                continue
            t = max(0.0, (outer - r) / (outer - inner))
            a = int(peak * t * t * (3 - 2 * t))  # smoothstep falloff
            px[x, y] = color + (a,)
    return img


def main():
    os.makedirs(ART, exist_ok=True)

    # a cool halo that reads on the bright Nova backgrounds: bluer and
    # stronger than a plain white glow, still feathered to nothing
    glow = radial_glow(620, 460, peak=115, color=(120, 155, 255))
    glow.save(os.path.join(ART, 'carousel_glow.png'))
    print('wrote carousel_glow.png', glow.size)

    # bottom vignette: 1280x400, transparent at top -> black ~40% at bottom
    w, h = 1280, 400
    vig = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = vig.load()
    for y in range(h):
        t = y / (h - 1)                      # 0 top -> 1 bottom
        a = int(102 * t ** 2.0)              # ease in, max ~40%
        for x in range(w):
            px[x, y] = (4, 6, 14, a)
    vig.save(os.path.join(ART, 'sys_vignette.png'))
    print('wrote sys_vignette.png', vig.size)


if __name__ == '__main__':
    main()
