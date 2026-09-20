#!/usr/bin/env python3
"""Crystal ES-DE v3.3.0: 4:3 backgrounds for the Nova (1280x960).

The Nova is 4:3, so backgrounds are 4:3:
- The 5 supplied heroes are used DIRECTLY (native 4:3, zero canvas/matte).
- The 16 generated comic backgrounds are recomposed at 1440x1080 with the
  same fractional design: blue panel x 0.013..0.267 (from the template),
  graffiti title right of the panel, hardware hero center-right.
Cards are untouched.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import compose_v3 as C3

W, H = 1440, 1080
OUT_BG = C3.OUT_BG

HEROES = {
    'snes': '/home/hatch/workspace/user/media_library/image/a3/a3aaf0c4142b86a219ff8c8daea2563361cfeb2478e955386d968f1afbd19d00.jpg',
    'gc': '/home/hatch/workspace/user/media_library/image/e5/e529c8f83492b92a4dfe5a56b7a064431e4b1fe7edd756a94c57231deaa39444.jpg',
    'n64': '/home/hatch/workspace/user/media_library/image/8f/8f9ff001bb555685faaef05a3e3aeeef22875959d87d5d4f6854b901d22b62a8.jpg',
    'gbc': '/home/hatch/workspace/user/media_library/image/03/03fb186269bf3569ccea110bfe1f2e8d83d4e28f27fd3b75fb0f2e815e5d3ee4.jpg',
    'n3ds': '/home/hatch/workspace/user/media_library/image/49/49fd48102f3afc1eb78714df470ee014d7b1e2870fdbc81e2548eb05b531ec08.png',
}


def main():
    # 1. Supplied heroes: rendered on their own, nothing added, nothing cut.
    for sys, src in HEROES.items():
        im = Image.open(src).convert('RGB')
        assert abs(im.size[0] / im.size[1] - 4 / 3) < 0.01, f'{sys} not 4:3: {im.size}'
        im.save(os.path.join(OUT_BG, f'{sys}.webp'), 'WEBP', quality=88, method=6)
        print('hero', sys, im.size)

    # 2. Generated comic backgrounds recomposed at 4:3.
    tpl = Image.open(os.path.join(
        C3.WORK, 'media-generation-blue-template-clean-0-4bfe272b-0cae-4202-a08b-c2d3308d5678.png')).convert('RGB')
    tw, th = tpl.size
    sc = H / th
    nw = int(tw * sc)  # 1432 at 1080 high: the template is natively ~4:3
    scaled = tpl.resize((nw, H), Image.LANCZOS)
    base = Image.new('RGB', (W, H), (255, 255, 255))
    base.paste(scaled, (0, 0))
    if nw < W:
        need = W - nw
        fill = C3.comic_fill(need, H)
        base.paste(fill.convert('RGB'), (nw, 0))
    base_rgba = base.convert('RGBA')
    base_rgba.save(os.path.join(C3.WORK, 'base_1440.png'))

    for sys, meta in C3.SYSTEMS.items():
        if sys in HEROES:
            continue
        cv = base_rgba.copy()
        # Title right of the blue panel (panel ends x=384 on this canvas).
        C3.draw_title(cv, meta['title'], 472, 130, 938, size=150)
        fg = C3.load_fg(meta['fg'])
        C3.paste_hero(cv, fg, 923, 545, 765, 600)
        cv.convert('RGB').save(os.path.join(OUT_BG, f'{sys}.webp'), 'WEBP', quality=82, method=6)
        print(' bg', sys)

    base_rgba.convert('RGB').save(os.path.join(OUT_BG, '_default.webp'), 'WEBP', quality=82, method=6)
    print(' bg _default')
    print('DONE')


if __name__ == '__main__':
    main()
