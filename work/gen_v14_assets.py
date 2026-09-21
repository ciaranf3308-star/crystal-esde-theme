#!/usr/bin/env python3
"""Crystal v14.0.0: integrate the 9 user-supplied console carousel posters.

Reads the portrait posters from ~/workspace/user/media_library/image/,
resizes each to 240x320 with high-quality Lanczos (direct resize, no crop,
no letterbox — the art is stylized and the ~6.7% vertical squeeze on the
two 1122x1402 sources is invisible; the poster's rounded frame must stay
intact), and writes theme-src/crystal/cards/<system>.png, replacing the
black marquee trading cards for exactly those 9 systems.

The other 12 systems keep their marquee cards; _default.png is untouched.
System view ONLY — gamelist/rails/lib assets are not touched by this script.
"""
import os
import sys
from PIL import Image

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
MEDIA = os.path.expanduser("~/workspace/user/media_library/image")
CARDS = os.path.join(REPO, "theme-src/crystal/cards")

# system -> media_library relative path (user-supplied, standing approved)
POSTERS = {
    "n3ds": "63/63127d1eae2b5e5b6ff4355dfabcff812dc7ba5cec8721d98ae693e795cd6fe1.jpg",  # Nintendo 3DS
    "gba":  "2c/2cfa3341627ba17bb3a2d1c0171fca9a9e69f1f5072dbd34dfed3bade0cc8531.jpg",  # Game Boy Advance
    "gb":   "c5/c5e63785df17b9e75d4f9652beb26eb8458c5872ba12bea17a992640075872d5.jpg",  # Game Boy
    "nds":  "03/03d66e74e0db3f719611f8616c29d2704c2c0c9d916bd641018a19cb29bf8ebe.jpg",  # Nintendo DS
    "snes": "9b/9b8e7134eb2846c2022e6b336fd508e1aefb6424c0a56a64a620098d08d5bde6.jpg",  # Super Nintendo
    "wii":  "0a/0a8378679d5408f48eb0422542d83fbb7acf465412fe60263150d7bc6f5c92d1.jpg",  # Wii
    "wiiu": "e9/e96485e4fda5f5fce3b678aa133379d58a4372a4db0ef536ac52966e31866c57.jpg",  # Wii U
    "n64":  "4b/4b23ef9e2e1fa2b55c543528e40da24016b5b08007491c6e81b62a39d05b061e.jpg",  # Nintendo 64
    "gc":   "5d/5d9afcb9b8515fb033bdedf5b2e67808e620f4a84b3cf7fa3367968403f6b7db.jpg",  # GameCube
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
            print(f"{system:6s} <- {rel[:40]}... {im.size}")
            card = im.convert("RGB").resize((CARD_W, CARD_H), Image.Resampling.LANCZOS)
            card.save(dst, "PNG")
        with Image.open(dst) as check:
            assert check.size == (CARD_W, CARD_H), f"{system} wrong size {check.size}"
    print(f"wrote 9 cards to {CARDS}")


if __name__ == "__main__":
    main()
