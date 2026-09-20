#!/usr/bin/env python3
"""v3.8.0: build animated carousel cards.

For the 7 systems with user-supplied on/off poster pairs: a 10-frame GIF that
slowly crossfades between the vivid "on" poster and the dim blueprint "off"
poster (frame 0 = ON, so a non-animating renderer shows the vivid poster).

For the other 14 systems: an 8-frame GIF of the existing trading card with a
very subtle "breathing" zoom (1.00 -> 1.05 -> 1.00), so the whole carousel
feels alive while the 7 poster systems get the full design dissolve.

Hold durations are jittered per system so cards drift out of sync instead of
pulsing in unison. Output: theme-src/crystal/cards_anim/<system>.gif

Deterministic: no timestamps, no randomness.
"""
import os
from PIL import Image, ImageChops

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = os.path.expanduser("~/workspace/user/media_library/image")
SRC_CARDS = os.path.join(REPO, "theme-src", "crystal", "cards")
OUT = os.path.join(REPO, "theme-src", "crystal", "cards_anim")

W, H = 240, 320  # card canvas (0.75 ratio, matches item box)

UPLOADS = [
    "c1/c18329cb33331d17f83524c2e0159deb6715785620c1b35d690ba8705f5b4ebf.jpg",  # 0 genesis on
    "af/af39b5263a5c750ee07f103f1a29d6c1f6e26c8fdffe8f278c612e14cafdb601.jpg",  # 1 genesis off
    "3c/3c6fad26c5000f7a772ebd237b9b1cd1ed33047b03443d0cb22d7b89ea0f548d.jpg",  # 2 ps2 on (pair A)
    "ab/abf440b360ca8507d7e0c03c8a634474712217cecf5dbeaea0980f0c295c3cad.jpg",  # 3 ps2 off (pair A)
    "ba/ba47b67003eeeb157b84fe6724a8a8610be6a9df2249c24d341c04fcd08b0085.jpg",  # 4 dreamcast on
    "45/45d9a69fb9c66adc836c73860f3d0392166e8d72083039bd4785ec252b7d980a.jpg",  # 5 dreamcast off
    "3f/3f7f6abcda7ace2d45308d182681086f8259ebb8135f401d4820a6fa461d88c2.jpg",  # 6 psx on
    "c3/c3073c4d81cd9d3167d6861a6c65bd813065194b5ed1530db7ad6c031c100a4a.jpg",  # 7 psx off
    "08/0889d5014336cda7a77da8dd0b0ea0e27930de599692d02b17186115495d5d91.jpg",  # 8 megadrive on
    "73/73fbddd3dc0fc0a91181b86ac2c677797b770f9c848803d5b2e1a5aae3c6d5d9.jpg",  # 9 megadrive off
    # (ps2 pair B was parked by user choice - not included)
    "fd/fdc07520163140c843251c98235b5c3a3f6ae87b626ccbb29d1e42ae7132affa.jpg",  # n64 on
    "51/516781ceae52dbccd733b7d23565e557134536d6aa4cad1448f09d3b58e8fb5d.jpg",  # n64 off
    "82/82de8019fff5c3022f4ffbe5d67fc63b87585f7b1505b1422b3f2082d869ed07.jpg",  # gc on
    "e3/e3f751ec81d3fcda61ab9484311ff200d4d6065f5a21a8e2f2b189f299eafbad.jpg",  # gc off
]

# system -> (on_upload_idx, off_upload_idx); ps2 uses pair A, pair B parked
POSTER_PAIRS = {
    "genesis": (0, 1),
    "ps2": (2, 3),
    "dreamcast": (4, 5),
    "psx": (6, 7),
    "megadrive": (8, 9),
    "n64": (10, 11),
    "gc": (12, 13),
}

TRADING_SYSTEMS = ["gb", "gbc", "gba", "nds", "n3ds", "snes", "nes", "psp",
                   "xbox", "xbox360", "wii", "wiiu", "steam", "windows"]


def pal_image(colors_img, ncolors):
    q = colors_img.quantize(colors=ncolors, method=Image.MEDIANCUT,
                            dither=Image.Dither.NONE)
    pal = Image.new("P", (1, 1))
    p = q.getpalette()[:ncolors * 3]
    p += [0] * (768 - len(p))
    pal.putpalette(p)
    return pal


def quantize_rgb(img, pal):
    return img.quantize(palette=pal, dither=Image.Dither.NONE)


def build_poster(system, on_idx, off_idx, jitter):
    on = Image.open(os.path.join(MEDIA, UPLOADS[on_idx])).convert("RGB")
    off = Image.open(os.path.join(MEDIA, UPLOADS[off_idx])).convert("RGB")
    on_s = on.resize((W, H), Image.LANCZOS)
    off_s = off.resize((W, H), Image.LANCZOS)

    # shared palette from both endpoints
    combo = Image.new("RGB", (W, H * 2))
    combo.paste(on_s, (0, 0))
    combo.paste(off_s, (0, H))
    pal = pal_image(combo, 256)

    blends = [Image.blend(on_s, off_s, t) for t in (0.2, 0.4, 0.6, 0.8)]
    seq = [on_s] + blends + [off_s] + blends[::-1]
    durs = [1500, 120, 120, 120, 120, 1500 + jitter, 120, 120, 120, 120]
    frames = [quantize_rgb(f, pal) for f in seq]
    return frames, durs


def build_trading(system, jitter):
    art = Image.open(os.path.join(SRC_CARDS, system + ".png")).convert("RGBA")
    # fit by width into canvas, keep transparent padding like the live theme
    fw, fh = W, round(W * art.height / art.width)
    fitted = art.resize((fw, fh), Image.LANCZOS)

    # 255-color palette from the card flattened on white; index 255 = transparent
    alpha = fitted.split()[3]
    white = Image.new("RGB", fitted.size, (255, 255, 255))
    white.paste(fitted, mask=alpha)
    pal = pal_image(white, 255)

    zooms = [1.00, 1.018, 1.032, 1.045, 1.05, 1.045, 1.032, 1.018]
    durs = [1500, 450, 450, 450, 1500 + jitter, 450, 450, 450]
    frames = []
    for z in zooms:
        zw, zh = round(fw * z), round(fh * z)
        zart = art.resize((zw, zh), Image.LANCZOS)
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        canvas.paste(zart, ((W - zw) // 2, (H - zh) // 2), zart)
        rgb = canvas.convert("RGB")
        p = quantize_rgb(rgb, pal)
        # restore 1-bit transparency for padding (palette index 255)
        tmask = canvas.split()[3].point(lambda v: 255 if v < 128 else 0)
        p.paste(255, tmask)
        frames.append(p)
    return frames, durs


def save_gif(frames, durs, path, transparent=None):
    kw = dict(save_all=True, append_images=frames[1:], duration=durs,
              loop=0, disposal=2)
    if transparent is not None:
        kw["transparency"] = transparent
    frames[0].save(path, **kw)


def main():
    os.makedirs(OUT, exist_ok=True)
    order = list(POSTER_PAIRS) + TRADING_SYSTEMS
    for i, system in enumerate(order):
        path = os.path.join(OUT, system + ".gif")
        if system in POSTER_PAIRS:
            on_i, off_i = POSTER_PAIRS[system]
            frames, durs = build_poster(system, on_i, off_i, (i * 29) % 90 * 10)
            save_gif(frames, durs, path)
            kind = "poster-xfade"
        else:
            frames, durs = build_trading(system, (i * 23) % 60 * 10)
            save_gif(frames, durs, path, transparent=255)
            kind = "trading-breathe"
        size = os.path.getsize(path)
        print(f"{system:10s} {kind:15s} {len(frames)} frames  {size//1024}KB")


if __name__ == "__main__":
    main()
