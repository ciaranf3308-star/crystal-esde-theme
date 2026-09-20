#!/usr/bin/env python3
"""Mock the CURRENT Crystal system view (gbc) at 1280x960 with real geometry.
Answers: does the panel text overlap by design?"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 960
bg = Image.open('theme-src/crystal/backgrounds/gbc.webp').convert('RGB').resize((W, H))
img = bg.copy()
d = ImageDraw.Draw(img)

def X(f): return int(f * W)
def Y(f): return int(f * H)
def FS(f): return int(f * H)

FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def text(x, y, s, fs, fill, font=FB, anchor='la'):
    d.text((X(x), Y(y)), s, font=ImageFont.truetype(font, FS(fs)), fill=fill, anchor=anchor)

# mfrBadge
d.rounded_rectangle([X(0.030)-13, Y(0.195)-5, X(0.030)+110, Y(0.195)+22], 7, fill='white')
text(0.030, 0.195, 'NINTENDO', 0.018, (10, 47, 160))
# sysName — systemdata=fullname wins over the static text (verified in SystemView.cpp)
text(0.030, 0.230, 'Nintendo Game Boy C...', 0.036, 'white')
# sysDesc (gbc pos override)
d.text((X(0.030), Y(0.302)), 'Color came to the brick. A pocket\nrainbow of classics.',
       font=ImageFont.truetype(FB, FS(0.019)), fill='white')
# countNum (gbc pos override)
text(0.030, 0.358, '0 GAMES', 0.055, 'white')
# factsLine (gbc pos override)
text(0.030, 0.431, '8-BIT \u2022 HANDHELD \u2022 1998', 0.017, (255, 210, 60))

# draw element boxes in red for diagnosis
for (x, y, w, h) in [(0.030,0.230,0.24,0.055),(0.030,0.302,0.20,0.140),
                     (0.030,0.358,0.20,0.07),(0.030,0.431,0.20,0.04)]:
    d.rectangle([X(x), Y(y), X(x+w), Y(y+h)], outline='red', width=2)

img.save('/tmp/mock_system_gbc.png')
print('saved /tmp/mock_system_gbc.png')
