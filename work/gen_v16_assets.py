#!/usr/bin/env python3
"""Crystal v16.0.0: second batch of system-view console carousel posters.

Reads the portrait posters from ~/workspace/user/media_library/image/,
resizes each to 240x320 with high-quality Lanczos (direct resize, no crop —
the 1086x1448 sources are exactly 3:4, so the resize is distortion-free)
and writes theme-src/crystal/cards/<system>.png.

- New: genesis, ps2, dreamcast, psx, megadrive, xbox
- Replacements (old-style v14 cards retired in favour of matching art):
  n64, gc, n3ds
- PS2: variant B used (f2/...): fuller right-column composition
  (memory card + disc fill the column), signature "PLAY NEXT LEVEL"
  tagline, and the longer 7-bullet spec list. Variant A (3c/...) retired
  from this release (file not baked; kept out of theme-src).

System view ONLY — gamelist/rails/lib assets untouched.
"""
import os
import sys
from PIL import Image

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
MEDIA = os.path.expanduser("~/workspace/user/media_library/image")
CARDS = os.path.join(REPO, "theme-src/crystal/cards")

# system -> media_library relative path (user-supplied, standing approved)
POSTERS = {
    "genesis":   "c1/c18329cb33331d17f83524c2e0159deb6715785620c1b35d690ba8705f5b4ebf.jpg",  # Genesis (new)
    "ps2":       "f2/f2e1ad7e5012dfdffdace5e3ec13cd3ba9c20dd23e4451ca542c02a9d30c27f5.jpg",  # PS2 variant B (new)
    "dreamcast": "ba/ba47b67003eeeb157b84fe6724a8a8610be6a9df2249c24d341c04fcd08b0085.jpg",  # Dreamcast (new)
    "psx":       "3f/3f7f6abcda7ace2d45308d182681086f8259ebb8135f401d4820a6fa461d88c2.jpg",   # PlayStation (new)
    "megadrive": "08/0889d5014336cda7a77da8dd0b0ea0e27930de599692d02b17186115495d5d91.jpg",  # Mega Drive (new)
    "n64":       "fd/fdc07520163140c843251c98235b5c3a3f6ae87b626ccbb29d1e42ae7132affa.jpg",  # N64 (replacement)
    "gc":        "82/82de8019fff5c3022f4ffbe5d67fc63b87585f7b1505b1422b3f2082d869ed07.jpg",  # GameCube (replacement)
    "xbox":      "62/62fe0f6dce696b62ed88566d6940e220e517a5c2631a2409bf2c8ff23575423f.jpg",  # Xbox (new)
    "n3ds":      "5d/5d9a583dfc0e82efe7de5299bd087d16311c7c2728c98caa584bf10bb68d8ee3.jpg",  # 3DS (replacement)
}

CARD_W, CARD_H = 240, 320


def main() -> None:
    for system, rel in POSTERS.items():
        src = os.path.join(MEDIA, rel)
        dst = os.path.join(CARDS, f"{system}.png")
        if not os.path.isfile(src):
            print(f"MISSING source for {system}: {src}", file=sys.stderr)
            sys.exit(1)
        with Image.open(src) as im:
            print(f"{system:9s} <- {rel[:40]}... {im.size}")
            assert im.size == (1086, 1448), f"{system} unexpected size {im.size}"
            card = im.convert("RGB").resize((CARD_W, CARD_H), Image.Resampling.LANCZOS)
            card.save(dst, "PNG")
        with Image.open(dst) as check:
            assert check.size == (CARD_W, CARD_H), f"{system} wrong size {check.size}"
    print(f"wrote 9 cards to {CARDS}")


if __name__ == "__main__":
    main()
