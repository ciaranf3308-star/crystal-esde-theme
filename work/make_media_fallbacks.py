#!/usr/bin/env python3
"""Generate per-system physical-media fallback silhouettes.

Used as <default> (hero image) and defaultImage (carousel) when a game has no
physicalmedia / 3dbox / cover art. White-on-transparent duotone shapes in the
Nova language: cartridge, disc, mini-disc, UMD-ish shell, game card.
"""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "theme-src", "crystal", "media_fallbacks")
os.makedirs(OUT, exist_ok=True)

W = H = 400
WHITE = (255, 255, 255, 255)
BLUE = (10, 47, 160, 255)
LBLUE = (191, 212, 255, 255)

def canvas():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def save(im, name):
    im.save(os.path.join(OUT, name + ".png"))

def cart():
    im = canvas(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([60, 40, 340, 360], radius=28, fill=WHITE)          # body
    d.rounded_rectangle([60, 40, 340, 110], radius=28, fill=WHITE)          # top (ridge zone)
    for x in range(95, 320, 28):                                          # grip ridges
        d.rectangle([x, 58, x + 12, 92], fill=BLUE)
    d.rounded_rectangle([92, 140, 308, 300], radius=14, fill=LBLUE)        # label
    d.rounded_rectangle([92, 140, 308, 185], radius=14, fill=BLUE)         # label header
    d.rectangle([92, 171, 308, 185], fill=BLUE)
    d.ellipse([80, 322, 96, 338], fill=BLUE)                               # screws
    d.ellipse([304, 322, 320, 338], fill=BLUE)
    return im

def disc(r=150, hole=34):
    im = canvas(); d = ImageDraw.Draw(im)
    d.ellipse([200 - r, 200 - r, 200 + r, 200 + r], fill=WHITE)            # disc
    d.ellipse([200 - r + 26, 200 - r + 26, 200 + r - 26, 200 + r - 26],
              outline=LBLUE, width=10)                                    # data ring
    d.ellipse([200 - 62, 200 - 62, 200 + 62, 200 + 62], outline=BLUE, width=8)
    d.ellipse([200 - hole, 200 - hole, 200 + hole, 200 + hole],
              fill=(0, 0, 0, 0))                                          # hub hole
    d.ellipse([200 - hole, 200 - hole, 200 + hole, 200 + hole],
              outline=BLUE, width=6)
    return im

def umd():
    im = canvas(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([50, 110, 350, 290], radius=24, fill=WHITE)        # shell
    d.ellipse([140, 140, 260, 260], fill=LBLUE)                            # window disc
    d.ellipse([185, 185, 215, 215], outline=BLUE, width=6)
    d.rounded_rectangle([50, 110, 350, 150], radius=24, fill=BLUE)         # shell header
    d.rectangle([50, 134, 350, 150], fill=BLUE)
    return im

def card():
    im = canvas(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([110, 70, 290, 330], radius=18, fill=WHITE)        # card
    d.polygon([(250, 70), (290, 70), (290, 110)], fill=WHITE)             # notch cut
    d.polygon([(252, 72), (288, 72), (288, 108)], fill=(0, 0, 0, 0))
    d.rounded_rectangle([128, 96, 272, 200], radius=10, fill=LBLUE)       # label
    d.rounded_rectangle([128, 96, 272, 128], radius=10, fill=BLUE)
    d.rectangle([128, 118, 272, 128], fill=BLUE)
    for x in range(140, 260, 22):                                         # contacts
        d.rectangle([x, 240, x + 12, 300], fill=BLUE)
    return im

CART = ["gb", "gbc", "gba", "nes", "snes", "n64", "genesis", "megadrive", "_default"]
DISC = ["psx", "ps2", "dreamcast", "xbox", "xbox360", "wii", "wiiu", "steam", "windows"]
for name in CART:
    save(cart(), name)
for name in DISC:
    save(disc(), name)
save(disc(r=112, hole=30), "gc")      # GameCube mini-disc
save(umd(), "psp")                    # UMD-ish shell
for name in ["nds", "n3ds"]:
    save(card(), name)

print("wrote", len(os.listdir(OUT)), "fallbacks to", OUT)
