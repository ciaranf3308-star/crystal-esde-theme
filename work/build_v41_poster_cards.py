#!/usr/bin/env python3
"""v4.1.0: restore the user's supplied posters as the console-carousel cards.

v3.8.0 put the user's 7 on/off poster pairs into the carousel as animated
GIFs. v4.0.0 had to drop the GIFs (ES-DE 3.4.1's carousel hard-creates plain
ImageComponents, which have no GIF/animation path), and the static
trading-card PNGs came back -- so the user's posters vanished from the
carousel. This script puts them back as static cards: the vivid "on" poster
for each of the 7 systems, at the 240x320 card canvas.

The sources are exactly 1086x1448 (0.75), so the resize is distortion-free.
The carousel engine already handles the off-state via unfocusedItemSaturation
/ unfocusedItemDimming (selected card vivid, neighbours dimmed) -- the same
on/off language the user supplied, done per-frame by ES-DE.

Deterministic: fixed resize filter, no metadata, no randomness.
"""
import os
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = os.path.expanduser("~/workspace/user/media_library/image")
OUT_DIR = os.path.join(REPO, "theme-src", "crystal", "cards")

W, H = 240, 320  # card canvas (0.75 ratio, matches item box)

# system -> vivid "on" poster upload (same sources as build_anim_cards.py)
ON_POSTERS = {
    "genesis":   "c1/c18329cb33331d17f83524c2e0159deb6715785620c1b35d690ba8705f5b4ebf.jpg",
    "ps2":       "3c/3c6fad26c5000f7a772ebd237b9b1cd1ed33047b03443d0cb22d7b89ea0f548d.jpg",  # pair A per user pick
    "dreamcast": "ba/ba47b67003eeeb157b84fe6724a8a8610be6a9df2249c24d341c04fcd08b0085.jpg",
    "psx":       "3f/3f7f6abcda7ace2d45308d182681086f8259ebb8135f401d4820a6fa461d88c2.jpg",
    "megadrive": "08/0889d5014336cda7a77da8dd0b0ea0e27930de599692d02b17186115495d5d91.jpg",
    "n64":       "fd/fdc07520163140c843251c98235b5c3a3f6ae87b626ccbb29d1e42ae7132affa.jpg",
    "gc":        "82/82de8019fff5c3022f4ffbe5d67fc63b87585f7b1505b1422b3f2082d869ed07.jpg",
}

for system, rel in sorted(ON_POSTERS.items()):
    src = os.path.join(MEDIA, rel)
    im = Image.open(src).convert("RGB")
    assert abs(im.size[0] / im.size[1] - 0.75) < 0.01, f"{system}: aspect changed!"
    card = im.resize((W, H), Image.LANCZOS)
    out = os.path.join(OUT_DIR, f"{system}.png")
    card.save(out, "PNG")
    print(f"{system}: {src} -> {out} ({os.path.getsize(out)} bytes)")

print("done: 7 poster cards restored")
