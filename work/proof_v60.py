#!/usr/bin/env python3
"""v6.0 gamelist proof mocks — faithful to the implemented XML geometry.
Renders: psx (disc), gba (cart), nds (card) + edge-case sheet.
NOT ES-DE renders — layout proofs only."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H = 1280, 960
SRC = os.path.expanduser('~/workspace/crystal-esde-theme/theme-src/crystal')
OUT = '/tmp'

def font(sz):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def draw_disc(d, cx, cy, r, dim=1.0):
    # silver-blue disc with hub
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(200, 210, 230))
    for rr, col in [(r*0.82, (175, 190, 215)), (r*0.62, (195, 205, 228)),
                    (r*0.42, (170, 185, 212))]:
        d.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], outline=col, width=3)
    hr = r*0.18
    d.ellipse([cx-hr, cy-hr, cx+hr, cy+hr], fill=(120, 135, 165))
    d.ellipse([cx-hr*0.45, cy-hr*0.45, cx+hr*0.45, cy+hr*0.45], fill=(240, 242, 250))
    # label text arc-ish
    d.text((cx-r*0.55, cy-r*0.28), 'PLAYSTATION', font=font(int(r*0.16)), fill=(40, 60, 120))

def draw_cart(d, cx, cy, w, h, dim=1.0, label='GAME BOY ADVANCE'):
    x0, y0 = cx-w/2, cy-h/2
    d.rounded_rectangle([x0, y0, x0+w, y0+h], radius=14, fill=(88, 96, 120))
    d.rounded_rectangle([x0+10, y0+10, x0+w-10, y0+h*0.62], radius=8, fill=(215, 220, 235))
    d.text((x0+22, y0+26), label, font=font(16), fill=(30, 50, 110))
    d.rectangle([x0+w*0.3, y0+h-26, x0+w*0.7, y0+h-12], fill=(60, 66, 84))

def draw_card(d, cx, cy, w, h, label='NINTENDO DS'):
    x0, y0 = cx-w/2, cy-h/2
    d.rounded_rectangle([x0, y0, x0+w, y0+h], radius=8, fill=(150, 158, 180))
    d.rounded_rectangle([x0+8, y0+8, x0+w-8, y0+h*0.55], radius=5, fill=(225, 230, 242))
    d.text((x0+16, y0+16), label, font=font(13), fill=(30, 50, 110))

def dim_layer(img, opacity):
    a = img.split()[3].point(lambda v: int(v*opacity))
    img.putalpha(a)
    return img

def render(system, media_kind, title, sub, marquee=True, media_missing=False,
           tall_art=False, out_name='proof.png'):
    bg = Image.open(f'{SRC}/art/gamelist_generic_bg.png').convert('RGBA')
    img = bg.copy()
    d = ImageDraw.Draw(img)

    # --- marquee ghost upper-left ---
    if marquee:
        mq = Image.new('RGBA', (512, 250), (0, 0, 0, 0))
        md = ImageDraw.Draw(mq)
        md.rounded_rectangle([10, 60, 502, 190], radius=18, fill=(150, 170, 230))
        md.text((40, 100), 'M A R Q U E E', font=font(44), fill=(255, 255, 255))
        mq = mq.rotate(-12, expand=True, resample=Image.BICUBIC)
        # blue/white filter: desaturate-ish + tint
        tint = Image.new('RGBA', mq.size, (185, 201, 255, 0))
        mq = Image.blend(mq, tint, 0.25)
        a = mq.split()[3].point(lambda v: int(v*0.38))
        mq.putalpha(a)
        img.alpha_composite(mq, (40, 30))
    else:
        d.text((77, 96), title, font=font(38), fill=(10, 47, 160, 140))

    # --- metadata upper-right (no panel) ---
    ink, deep = (58, 74, 115), (10, 47, 160)
    d.text((845, 67), 'A brave hero sets out across a vast kingdom to rescue the princess and defeat evil.', font=font(19), fill=ink)
    d.text((845, 110), 'Epic adventure spanning dungeons, oceans and skies.', font=font(19), fill=ink)
    d.text((845, 204), 'Action-Adventure', font=font(21), fill=deep)
    d.text((1242, 204), '2001', font=font(21), fill=deep, anchor='ra')
    d.text((845, 238), 'Nintendo', font=font(21), fill=deep)
    d.text((1242, 238), '1-4', font=font(21), fill=deep, anchor='ra')
    for i in range(5):
        c = (255, 214, 10) if i < 4 else (190, 200, 220)
        d.polygon([(845+i*34, 292), (853+i*34, 278), (861+i*34, 292), (857+i*34, 300), (849+i*34, 300)], fill=c)
    d.text((845, 317), '20 Sep 2026', font=font(16), fill=ink)

    # --- glow + shadow behind selected ---
    glow = Image.new('RGBA', (397, 397), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([20, 20, 377, 377], fill=(255, 214, 10, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img.alpha_composite(glow, (640-198, 512-198))
    sh = Image.open(f'{SRC}/art/lib_shadow_soft.png').convert('RGBA')
    sh = sh.resize((346, 53))
    a = sh.split()[3].point(lambda v: int(v*0.55))
    sh.putalpha(a)
    img.alpha_composite(sh, (640-173, 684-26))

    # --- carousel: neighbours 213px @ y-bottom 691, selected 319px lifted to 672 ---
    def item(cx, size, selected, kind):
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        bottom = 672 if selected else 691
        cy = bottom - size/2
        if media_missing and not selected:
            fb = Image.open(f'{SRC}/media_fallbacks/{system}.png').convert('RGBA').resize((size, size))
            layer.alpha_composite(fb, (int(cx-size/2), int(cy-size/2)))
        elif kind == 'disc':
            draw_disc(ld, cx, cy, size/2)
        elif kind == 'cart':
            hh = size*1.12 if tall_art and selected else size*0.95
            draw_cart(ld, cx, cy, size, hh)
        else:
            draw_card(ld, cx, cy, size*0.95, size*0.8)
        if not selected:
            # unfocused: dim + desaturate-ish + lower opacity
            px = layer.load()
            a = layer.split()[3].point(lambda v: int(v*0.75))
            layer.putalpha(a)
        return layer

    for cx in (0, 320):            # prev-2 (peeks at left edge), prev
        img.alpha_composite(item(cx, 213, False, media_kind))
    for cx in (960, 1280):          # next, next+2 (peeks at right edge)
        img.alpha_composite(item(cx, 213, False, media_kind))
    img.alpha_composite(item(640, 319, True, media_kind))

    # --- game identity under media ---
    d.text((640, 741), title, font=font(35), fill=(255, 255, 255), anchor='ma')
    g, y, pl = sub
    d.text((610, 789), g, font=font(18), fill=(191, 212, 255), anchor='ra')
    d.text((640, 789), y, font=font(18), fill=(191, 212, 255), anchor='ma')
    d.text((670, 789), pl, font=font(18), fill=(191, 212, 255), anchor='la')

    # --- system logo (real asset) ---
    logo = Image.open(f'{SRC}/art/console_logos/{system}.png').convert('RGBA')
    lw, lh = logo.size
    s = min(461/lw, 60/lh)
    logo = logo.resize((int(lw*s), int(lh*s)))
    img.alpha_composite(logo, (640-logo.width//2, 843-logo.height//2))

    # --- footer: single centred helpsystem row ---
    d.text((640, 917), 'A  SELECT    B  BACK    X  VIEW MEDIA    Y  FAVORITES', font=font(18),
           fill=(255, 255, 255), anchor='ma')

    img.convert('RGB').save(f'{OUT}/{out_name}')
    print('saved', out_name)

render('ps2', 'disc', 'Gran Turismo 3: A-Spec', ('Racing', '2001', '1-2'), out_name='proof_v60_psx.png')
render('gba', 'cart', 'The Legend of Zelda: The Minish Cap', ('Action-Adventure', '2004', '1'), out_name='proof_v60_gba.png')
render('nds', 'card', 'New Super Mario Bros.', ('Platform', '2006', '1-4'), out_name='proof_v60_nds.png')
# edge cases
render('ps2', 'disc', 'The Legend of Zelda: The Wind Waker HD — A Very Long Game Name Indeed', ('Action-Adventure', '2003', '1'),
       marquee=False, out_name='proof_v60_edge_longname.png')
render('snes', 'cart', 'Unscraped Game', ('RPG', '1994', '1'), media_missing=True, tall_art=True, out_name='proof_v60_edge_fallback.png')
