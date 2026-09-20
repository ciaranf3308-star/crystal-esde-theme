#!/usr/bin/env python3
"""Erase the baked-in fake phone status bar (wifi / 15:24 / battery 87%) from
the top-right of user-supplied hero backgrounds.

Method per image:
  1. Locate the wifi icon (leftmost clock element, identical across all
     supplied images) by normalized cross-correlation of the bright-pixel
     mask against a wifi template extracted from gba.
  2. Box = [wifi_left-8, W-2] x [14, 54]  (covers wifi..87%, nothing else;
     comic linework sits left of the wifi and is untouched).
  3. Erase bright-ish pixels (min channel > 110, catches JPEG halos) inside
     the box; fill with the box's own non-bright median (pure strip navy),
     feathered 4px so no box edge shows.
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage, signal

BGDIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", "theme-src", "crystal", "backgrounds"))
# snes + gc have no clock (halftone-dot strips). The 6 generated bgs
# (nes, psx, steam, windows, xbox360, _default) DO have the clock at
# (1215, 20) - patched separately 2026-09-20 (wifi template differs from
# the supplied heroes, so they are not in this SYSTEMS list).
SYSTEMS = ["gb", "gbc", "gba", "nds", "n3ds", "n64", "psp", "ps2",
           "dreamcast", "genesis", "megadrive", "xbox", "wii", "wiiu"]

TEMPLATE_SRC = "gba"
# wifi icon crop in gba (x0, y0, x1, y1) - verified visually
TEMPLATE_BOX = (1218, 16, 1256, 42)


def bright_mask(a):
    return a.min(axis=2) > 140


def get_template():
    im = Image.open(os.path.join(BGDIR, TEMPLATE_SRC + ".webp")).convert("RGB")
    a = np.array(im).astype(np.float64)
    x0, y0, x1, y1 = TEMPLATE_BOX
    t = bright_mask(a[y0:y1, x0:x1]).astype(np.float64)
    t -= t.mean()
    return t


def find_wifi(a, tmpl):
    H, W, _ = a.shape
    sx0, sx1 = int(0.79 * W), int(0.88 * W)
    sy0, sy1 = 8, 58
    region = bright_mask(a[sy0:sy1, sx0:sx1]).astype(np.float64)
    th, tw = tmpl.shape
    N = th * tw
    ones = np.ones((th, tw))
    r_sum = signal.correlate(region, ones, mode="valid")
    r2_sum = signal.correlate(region ** 2, ones, mode="valid")
    corr = signal.correlate(region, tmpl, mode="valid")  # tmpl zero-mean
    t_ssd = float((tmpl ** 2).sum())
    denom = np.sqrt(np.maximum(r2_sum - r_sum ** 2 / N, 0) * t_ssd)
    ncc = np.divide(corr, denom, out=np.zeros_like(corr),
                    where=denom > 1e-9)
    j, i = np.unravel_index(np.argmax(ncc), ncc.shape)
    score = float(ncc[j, i])
    return sx0 + i, sy0 + j, score  # top-left of match in image coords


def process(path, proofdir, tmpl, dry_run=False):
    im = Image.open(path).convert("RGB")
    a = np.array(im)
    H, W, _ = a.shape
    wx, wy, score = find_wifi(a.astype(np.float64), tmpl)
    if score < 0.45:
        return (False, f"wifi NCC={score:.2f} too low -> SKIPPED")
    bx0, bx1 = wx - 8, W - 2
    by0, by1 = 14, 54
    box = a[by0:by1, bx0:bx1]
    erase = box.min(axis=2) > 110
    n_erase = int(erase.sum())
    if n_erase < 800:
        return (False, f"erase_px={n_erase} < 800 -> SKIPPED")
    win = box.reshape(-1, 3)
    bg = win[win.min(axis=1) <= 110]
    fill = tuple(int(v) for v in np.median(bg, axis=0)) if len(bg) else (1, 44, 167)
    if not dry_run:
        out = a.copy()
        core = ndimage.binary_dilation(erase, iterations=3)
        ring = ndimage.binary_dilation(erase, iterations=5) ^ core
        out[by0:by1, bx0:bx1][core] = fill
        # 50% blend ring softens any residual edge
        roi = out[by0:by1, bx0:bx1].astype(np.float64)
        roi[ring] = roi[ring] * 0.5 + np.array(fill) * 0.5
        out[by0:by1, bx0:bx1] = np.clip(roi, 0, 255).astype(np.uint8)
        Image.fromarray(out).save(path, "WEBP", quality=90, method=6)
        result = out
    else:
        result = a
    proof = Image.fromarray(result).crop(
        (max(0, bx0 - 60), 0, min(W, bx1 + 20), 90))
    if dry_run:
        from PIL import ImageDraw
        d = ImageDraw.Draw(proof)
        if bx0 - 60 >= 0:
            rx0, rx1 = 60, 60 + (bx1 - bx0)
        else:
            rx0, rx1 = bx0, bx1
        d.rectangle([rx0, 14, rx1, 54], outline=(255, 0, 0), width=2)
    proof = proof.resize((proof.width * 3, proof.height * 3), Image.NEAREST)
    proof.save(os.path.join(proofdir, os.path.basename(path) + ".zone.png"))
    # detection debug crop (template match location)
    return (True, f"wifi_x={wx} NCC={score:.2f} box=({bx0},{by0})-({bx1},{by1}) "
                  f"erase_px={n_erase} fill={fill}")


def main():
    proofdir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/clock_patch5"
    dry = "--dry" in sys.argv
    os.makedirs(proofdir, exist_ok=True)
    tmpl = get_template()
    print(f"template {tmpl.shape}, mean={tmpl.mean():.3f}")
    allok = True
    for s in SYSTEMS:
        ok, msg = process(os.path.join(BGDIR, s + ".webp"), proofdir, tmpl,
                          dry_run=dry)
        print(f"{s:10s} {msg}")
        allok = allok and ok
    print("ALL_OK" if allok else "SOME_SKIPPED")


if __name__ == "__main__":
    main()
