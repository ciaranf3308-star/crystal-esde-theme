#!/usr/bin/env python3
"""Crystal ES-DE v3 asset composer: blue/white hero backgrounds + carousel cards."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from collections import deque
import os

WORK = '/home/hatch/workspace/crystal-esde-theme/work'
FG = '/tmp/fg/hardware'
OUT_BG = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal/backgrounds'
OUT_CARD = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal/cards'
os.makedirs(OUT_BG, exist_ok=True)
os.makedirs(OUT_CARD, exist_ok=True)

FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
BLUE = (10, 47, 160)

SYSTEMS = {
    'dreamcast': dict(mfr='SEGA', title=['DREAMCAST'], card='DREAMCAST',
                      desc="Sega's 128-bit swan song. Arcade soul with VMU dreams.",
                      facts='128-BIT \u2022 1999', fg='dreamcast/dreamcast.png'),
    'gb': dict(mfr='NINTENDO', title=['GAME BOY'], card='GAME BOY',
               desc='The brick that built handheld gaming. Tetris forever.',
               facts='8-BIT \u2022 HANDHELD \u2022 1989', fg='gb/gb.png'),
    'gba': dict(mfr='NINTENDO', title=['GAME BOY', 'ADVANCE'], card='GAME BOY ADVANCE',
                desc="Nintendo's 32-bit handheld brought iconic franchises and a massive 2D library to a new generation.",
                facts='32-BIT \u2022 HANDHELD \u2022 2001', fg='gba/gba.png'),
    'gbc': dict(mfr='NINTENDO', title=['GAME BOY', 'COLOR'], card='GAME BOY COLOR',
                desc='Color came to the brick. A pocket rainbow of classics.',
                facts='8-BIT \u2022 HANDHELD \u2022 1998', fg='gbc/gbc.png'),
    'gc': dict(mfr='NINTENDO', title=['GAMECUBE'], card='GAMECUBE',
               desc="Nintendo's cube of joy. Smash, Sunshine and Wind Waker.",
               facts='128-BIT \u2022 2001', fg='gc/gc.png'),
    'genesis': dict(mfr='SEGA', title=['GENESIS'], card='GENESIS',
                    desc="Blast-processing attitude. Sonic's 16-bit battleground.",
                    facts='16-BIT \u2022 1989', fg='genesis/genesis.png'),
    'megadrive': dict(mfr='SEGA', title=['MEGA', 'DRIVE'], card='MEGA DRIVE',
                      desc="Europe's name for Sega's 16-bit speed machine.",
                      facts='16-BIT \u2022 1990', fg='megadrive/megadrive.png'),
    'n3ds': dict(mfr='NINTENDO', title=['NINTENDO', '3DS'], card='NINTENDO 3DS',
                 desc='Glasses-free 3D in your pocket. StreetPass adventures.',
                 facts='HANDHELD \u2022 2011', fg='n3ds/n3ds.png'),
    'n64': dict(mfr='NINTENDO', title=['NINTENDO 64'], card='N64',
                desc='Three-pronged pioneer of 3D. Mario 64 changed everything.',
                facts='64-BIT \u2022 1996', fg='n64/n64.png'),
    'nds': dict(mfr='NINTENDO', title=['NINTENDO DS'], card='NINTENDO DS',
                desc='Two screens, one stylus, endless touch-screen experiments.',
                facts='HANDHELD \u2022 2004', fg='nds/nds.png'),
    'nes': dict(mfr='NINTENDO', title=['NINTENDO', 'NES'], card='NES',
                desc='The gray box that saved gaming. 8-bit legends live here.',
                facts='8-BIT \u2022 1985', fg='GEN:nes'),
    'ps2': dict(mfr='SONY', title=['PLAYSTATION 2'], card='PLAYSTATION 2',
                 desc='The best-selling console ever. An endless library.',
                 facts='128-BIT \u2022 2000', fg='ps2/ps2.png'),
    'psp': dict(mfr='SONY', title=['PLAYSTATION', 'PORTABLE'], card='PSP',
                desc='Console power in your pocket. UMD adventures.',
                facts='HANDHELD \u2022 2005', fg='psp/psp.png'),
    'psx': dict(mfr='SONY', title=['PLAYSTATION'], card='PLAYSTATION',
                 desc='Where 3D grew up. Crash, Spyro, Final Fantasy VII.',
                 facts='32-BIT \u2022 1995', fg='psx/psx.png'),
    'snes': dict(mfr='NINTENDO', title=['SUPER', 'NINTENDO'], card='SUPER NINTENDO',
                  desc='The 16-bit golden age. Mode 7 magic and timeless RPGs.',
                  facts='16-BIT \u2022 1991', fg='snes/snes.png'),
    'steam': dict(mfr='VALVE', title=['STEAM'], card='STEAM',
                  desc="PC gaming's front door. Thousands of worlds await.",
                  facts='PC \u2022 2003', fg='steam/steam.png'),
    'wii': dict(mfr='NINTENDO', title=['WII'], card='WII',
                desc='Motion controls for everyone. Bowling in living rooms.',
                facts='2006', fg='wii/wii.png'),
    'wiiu': dict(mfr='NINTENDO', title=['WII U'], card='WII U',
                 desc='The GamePad experiment. Hidden gems await.',
                 facts='2012', fg='wiiu/wiiu.png'),
    'windows': dict(mfr='', title=['WINDOWS'], card='WINDOWS',
                    desc='PC classics, indie gems and emulation everything.',
                    facts='PC', fg='GEN:windows'),
    'xbox': dict(mfr='MICROSOFT', title=['XBOX'], card='XBOX',
                  desc="The green giant's first shot. Halo defined a generation.",
                  facts='2001', fg='xbox/xbox.png'),
    'xbox360': dict(mfr='MICROSOFT', title=['XBOX 360'], card='XBOX 360',
                     desc='HD-era pioneer. A legendary library.',
                     facts='2005', fg='xbox360/xbox360.png'),
}


def remove_white_bg(im, tol=20):
    im = im.convert('RGBA')
    a = np.array(im)
    h, w = a.shape[:2]
    white = (a[:, :, 0] > 255 - tol) & (a[:, :, 1] > 255 - tol) & (a[:, :, 2] > 255 - tol)
    bg = np.zeros((h, w), bool)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if white[y, x] and not bg[y, x]:
                bg[y, x] = True
                dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if white[y, x] and not bg[y, x]:
                bg[y, x] = True
                dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        if y > 0 and white[y-1, x] and not bg[y-1, x]:
            bg[y-1, x] = True; dq.append((y-1, x))
        if y < h-1 and white[y+1, x] and not bg[y+1, x]:
            bg[y+1, x] = True; dq.append((y+1, x))
        if x > 0 and white[y, x-1] and not bg[y, x-1]:
            bg[y, x-1] = True; dq.append((y, x-1))
        if x < w-1 and white[y, x+1] and not bg[y, x+1]:
            bg[y, x+1] = True; dq.append((y, x+1))
    a[bg, 3] = 0
    # 1px defringe: erode opaque mask slightly
    opaque = a[:, :, 3] > 128
    eroded = opaque.copy()
    eroded[1:, :] &= opaque[:-1, :]
    eroded[:-1, :] &= opaque[1:, :]
    eroded[:, 1:] &= opaque[:, :-1]
    eroded[:, :-1] &= opaque[:, 1:]
    a[opaque & ~eroded, 3] = 0
    return Image.fromarray(a)


def duotone_blue(im):
    """Map render to blue duotone so hardware matches the theme scheme."""
    im = im.convert('RGBA')
    a = np.array(im).astype(np.float32)
    lum = (0.299*a[:, :, 0] + 0.587*a[:, :, 1] + 0.114*a[:, :, 2]) / 255.0
    dark = np.array([8, 30, 120], np.float32)
    light = np.array([205, 228, 255], np.float32)
    rgb = dark[None, None, :] * (1 - lum[:, :, None]) + light[None, None, :] * lum[:, :, None]
    a[:, :, :3] = np.clip(rgb, 0, 255)
    return Image.fromarray(a.astype(np.uint8))


def load_fg(spec):
    if spec.startswith('GEN:'):
        name = spec[4:]
        p = os.path.join(WORK, f'media-generation-{"nes-console" if name=="nes" else "windows-controller"}-0-*.png')
        import glob
        p = sorted(glob.glob(p))[0]
        im = Image.open(p).convert('RGB')
        return duotone_blue(remove_white_bg(im))
    return duotone_blue(Image.open(os.path.join(FG, spec)).convert('RGBA'))


def shear_text_layer(layer):
    # italic-ish energy: horizontal shear
    w, h = layer.size
    return layer.transform((w + int(h * 0.18), h), Image.AFFINE, (1, -0.18, 0, 0, 1, 0),
                           resample=Image.BICUBIC)


def draw_title(base, lines, x, y, max_w, size=150):
    """White bold-italic title with blue offset shadow."""
    while size > 40:
        f = ImageFont.truetype(FONT_BOLD, size)
        widths = [f.getlength(t) for t in lines]
        if max(widths) * 1.1 <= max_w:
            break
        size -= 8
    f = ImageFont.truetype(FONT_BOLD, size)
    lh = int(size * 1.02)
    total_h = lh * len(lines)
    maxw = int(max(f.getlength(t) for t in lines) * 1.15) + 40
    layer = Image.new('RGBA', (maxw, total_h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, t in enumerate(lines):
        yy = 10 + i * lh
        d.text((16, yy + 9), t, font=f, fill=BLUE + (255,))
        d.text((10, yy), t, font=f, fill=(255, 255, 255, 255))
    layer = shear_text_layer(layer)
    base.alpha_composite(layer, (x, y))


def paste_hero(base, fg, cx, cy, max_w, max_h, angle=-8):
    w, h = fg.size
    s = min(max_w / w, max_h / h)
    fg = fg.resize((int(w * s), int(h * s)), Image.LANCZOS)
    fg = fg.rotate(angle, expand=True, resample=Image.BICUBIC)
    # soft shadow
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    fw, fh = fg.size
    ds.ellipse([cx - fw*0.42, cy + fh*0.30, cx + fw*0.42, cy + fh*0.52], fill=(10, 20, 80, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    base.alpha_composite(sh)
    base.alpha_composite(fg, (int(cx - fw/2), int(cy - fh/2)))


print('building base canvas...')
tpl = Image.open(os.path.join(
    WORK, 'media-generation-blue-template-clean-0-4bfe272b-0cae-4202-a08b-c2d3308d5678.png')).convert('RGB')
tw, th = tpl.size
sc = 1080 / th
nw = int(tw * sc)
scaled = tpl.resize((nw, 1080), Image.LANCZOS)
def comic_fill(w, h):
    """Procedural blue/white comic fill for the canvas extension (no mirrored text)."""
    import random
    random.seed(7)
    img = Image.new('RGBA', (w, h), (232, 240, 255, 255))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(8):
        x0 = random.randint(0, w); y0 = random.randint(0, h)
        pts = [(x0, y0), (x0 + random.randint(80, 280), y0 + random.randint(-50, 50)),
               (x0 + random.randint(20, 140), y0 + random.randint(90, 260))]
        d.polygon(pts, fill=(20, 60, 180, random.randint(35, 95)))
    for yy in range(12, h, 26):
        for xx in range(12, w, 26):
            r = 3 + 7 * (xx / w)
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(25, 70, 190, 120))
    for _ in range(12):
        x0 = random.randint(0, w); y0 = random.randint(0, h)
        d.line([x0, y0, x0 + random.randint(60, 220), y0 + random.randint(-30, 30)],
               fill=(25, 70, 190, 80), width=3)
    return img


base = Image.new('RGB', (1920, 1080), (255, 255, 255))
base.paste(scaled, (0, 0))
if nw < 1920:
    # procedural comic extension with soft seam blend (no mirrored artifacts)
    need = 1920 - nw
    fill = comic_fill(need, 1080)
    bw = min(90, need)
    mask = Image.new('L', (need, 1080), 255)
    mp = mask.load()
    for x in range(bw):
        v = int(255 * x / bw)
        for y in range(1080):
            mp[x, y] = v
    base.paste(fill.convert('RGB'), (nw, 0), mask)
base_rgba = base.convert('RGBA')
base_rgba.save(os.path.join(WORK, 'base_1920.png'))
print('base saved', base_rgba.size)

print('compositing backgrounds...')
for sys, meta in SYSTEMS.items():
    cv = base_rgba.copy()
    draw_title(cv, meta['title'], 470, 130, 780, size=150)
    fg = load_fg(meta['fg'])
    paste_hero(cv, fg, 1230, 545, 1020, 600)
    cv.convert('RGB').save(os.path.join(OUT_BG, f'{sys}.webp'), 'WEBP', quality=82, method=6)
    print(' bg', sys)

# _default: clean base, no title/console
base_rgba.convert('RGB').save(os.path.join(OUT_BG, '_default.webp'), 'WEBP', quality=82, method=6)
print(' bg _default')

print('compositing cards...')
# card backdrop: comic crop from base
cardbg_src = base_rgba.crop((700, 150, 1150, 700)).resize((400, 424), Image.LANCZOS)
for sys, meta in SYSTEMS.items():
    card = cardbg_src.copy()
    d = ImageDraw.Draw(card, 'RGBA')
    d.rectangle([0, 0, 399, 423], outline=(255, 255, 255, 255), width=10)
    # name plate
    f = ImageFont.truetype(FONT_BOLD, 40)
    name = meta['card']
    while f.getlength(name) > 330 and f.size > 18:
        f = ImageFont.truetype(FONT_BOLD, f.size - 2)
    twd = f.getlength(name)
    d.text((200 - twd/2 + 3, 18 + 3), name, font=f, fill=BLUE + (255,))
    d.text((200 - twd/2, 18), name, font=f, fill=(255, 255, 255, 255))
    # hardware
    fg = load_fg(meta['fg'])
    w, h = fg.size
    s = min(320 / w, 250 / h)
    fg = fg.resize((int(w*s), int(h*s)), Image.LANCZOS)
    card.alpha_composite(fg, (int(200 - fg.size[0]/2), int(300 - fg.size[1]/2)))
    # selected-glow edge (subtle inner)
    card.save(os.path.join(OUT_CARD, f'{sys}.png'))
    print(' card', sys)

cardbg_src.save(os.path.join(OUT_CARD, '_default.png'))
print('DONE')
