#!/usr/bin/env python3
"""Crystal v3.7 proof: the 3 new supplied heroes at the Nova's 1280x960 with
the live text geometry from views.xml drawn over them. LOOK at the result."""
import os, re
from PIL import Image, ImageDraw, ImageFont

CRYSTAL = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal'
W, H = 1280, 960
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

V = dict(re.findall(r'<(\w+)>([0-9a-fA-F]{6,8})</\1>',
                    open(os.path.join(CRYSTAL, 'variables.xml')).read()))
def rgba(h):
    h = h + 'FF' if len(h) == 6 else h
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4, 6))

T_TEXT = rgba(V.get('crystalText', 'FFFFFFFF'))
T_DIM = rgba(V.get('crystalDim', 'B0C4DEFF'))
T_ACC = rgba(V.get('crystalAccent', 'FFD23FFF'))
BLUE = (10, 47, 160)

SYS = {
 'xbox': dict(name='Xbox', badge='MICROSOFT',
              desc="The green giant's first shot. Halo defined a generation.",
              facts='2001'),
 'wii': dict(name='Nintendo Wii', badge='NINTENDO',
             desc='Motion controls for everyone. Bowling in living rooms.',
             facts='2006'),
 'wiiu': dict(name='Nintendo Wii U', badge='NINTENDO',
              desc='The GamePad experiment. Hidden gems await.',
              facts='2012'),
}

def wrap(draw, s, px, max_w):
    f = ImageFont.truetype(FR, px)
    words, lines, cur = s.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if draw.textlength(t, font=f) <= max_w: cur = t
        else: lines.append(cur); cur = w_
    lines.append(cur)
    return lines

def render(sys):
    d = SYS[sys]
    bg = Image.open(f'{CRYSTAL}/backgrounds/{sys}.webp').convert('RGB').resize((W, H), Image.LANCZOS)
    dr = ImageDraw.Draw(bg)
    # mfrBadge pill: pos 0.028,0.200 fontSize 0.016, margins 0.010/0.005
    bx, by = 0.028*W, 0.200*H
    bf = ImageFont.truetype(FB, int(0.016*H))
    tw = dr.textlength(d['badge'], font=bf)
    mx, my = 0.010*W, 0.005*H
    dr.rounded_rectangle([bx-mx, by-my, bx+tw+mx, by+bf.size+my], radius=int(0.007*H), fill=(255,255,255))
    dr.text((bx, by), d['badge'], font=bf, fill=BLUE)
    # sysName: pos 0.028,0.232 size 0.22x0.05 fontSize 0.030
    nx, ny = 0.028*W, 0.232*H
    nf = ImageFont.truetype(FB, int(0.030*H))
    nw = dr.textlength(d['name'], font=nf)
    boxw = 0.22*W
    print(f"{sys}: sysName '{d['name']}' width={nw:.0f}px box={boxw:.0f}px fits={nw<=boxw}")
    dr.text((nx, ny), d['name'], font=nf, fill=T_TEXT)
    # sysDesc: pos 0.028,0.300 size 0.155 fontSize 0.0155
    dx, dy = 0.028*W, 0.300*H
    for i, ln in enumerate(wrap(dr, d['desc'], int(0.0155*H), 0.155*W)):
        dr.text((dx, dy + i*int(0.0155*H)*1.35), ln,
                font=ImageFont.truetype(FR, int(0.0155*H)), fill=T_DIM)
    # countNum + factsLine
    dr.text((0.028*W, 0.475*H), '128', font=ImageFont.truetype(FB, int(0.042*H)), fill=T_TEXT)
    dr.text((0.028*W, 0.545*H), d['facts'], font=ImageFont.truetype(FB, int(0.015*H)), fill=T_ACC)
    return bg

outs = [render(s) for s in ('xbox', 'wii', 'wiiu')]
sheet = Image.new('RGB', (W, H*3 // 2), (0, 0, 0))
for i, im in enumerate(outs):
    t = im.resize((W, H//2), Image.LANCZOS)
    sheet.paste(t, (0, i*H//2))
    ImageDraw.Draw(sheet).text((12, i*H//2 + 8), ('xbox', 'wii', 'wiiu')[i], fill=(255,255,0))
sheet.save('/home/hatch/workspace/your_files/crystal_v37_heroes.png')
print('proof -> ~/workspace/your_files/crystal_v37_heroes.png')
