#!/usr/bin/env python3
"""Crystal v17.4.0: physical-media fallback silhouettes, deliberately PLAIN.

Used as <default> (hero image) and defaultImage (carousel) when a game has
no physicalmedia / 3dbox art. One flat muted blue-grey silhouette per media
class - no label art, no rings, no ridges, no screws, no contacts, no sheen.
The UI is designed around REAL scraped artwork; these exist only to keep the
layout competent for the ~2% of games without it.
"""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "theme-src", "crystal", "media_fallbacks")
os.makedirs(OUT, exist_ok=True)

W = H = 400
MAIN = (107, 127, 160, 255)    # muted blue-grey
DARK = (78, 96, 130, 255)
LIGHT = (140, 158, 190, 255)
CLEAR = (0, 0, 0, 0)

def canvas():
    return Image.new("RGBA", (W, H), CLEAR)

def save(im, name):
    im.save(os.path.join(OUT, name + ".png"))

def cart():
    """Cartridge: plain rounded body, top notch cut out."""
    im = canvas(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([60, 40, 340, 360], radius=28, fill=MAIN)
    d.rectangle([175, 40, 225, 78], fill=CLEAR)  # top notch
    return im

def disc(r=150, hole=34):
    """Disc: flat circle, hub hole, thin hub ring."""
    im = canvas(); d = ImageDraw.Draw(im)
    d.ellipse([200 - r, 200 - r, 200 + r, 200 + r], fill=MAIN)
    d.ellipse([200 - hole, 200 - hole, 200 + hole, 200 + hole], fill=CLEAR)
    d.ellipse([200 - hole - 8, 200 - hole - 8, 200 + hole + 8, 200 + hole + 8],
              outline=DARK, width=6)
    return im

def umd():
    """UMD: flat shell, darker disc window, hub hole."""
    im = canvas(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([50, 110, 350, 290], radius=24, fill=LIGHT)
    d.ellipse([140, 140, 260, 260], fill=MAIN)
    d.ellipse([185, 185, 215, 215], fill=CLEAR)
    return im

def card():
    """Game card: plain rounded card, signature notch cut out."""
    im = canvas(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([110, 70, 290, 330], radius=18, fill=MAIN)
    d.rectangle([258, 70, 290, 104], fill=CLEAR)  # notch
    return im

def digital():
    """Digital-only systems (steam, windows): plain rounded square."""
    im = canvas(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([110, 110, 290, 290], radius=24, fill=MAIN)
    return im

CART = ["gb", "gbc", "gba", "nes", "snes", "n64", "genesis", "megadrive", "_default"]
DISC = ["psx", "ps2", "dreamcast", "xbox", "xbox360", "wii", "wiiu"]
for name in CART:
    save(cart(), name)
for name in DISC:
    save(disc(), name)
save(disc(r=112, hole=30), "gc")
save(umd(), "psp")
for name in ["nds", "n3ds"]:
    save(card(), name)
for name in ["steam", "windows"]:
    save(digital(), name)

print("wrote", len(os.listdir(OUT)), "fallbacks to", OUT)
