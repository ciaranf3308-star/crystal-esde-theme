#!/usr/bin/env python3
"""Crystal ES-DE v3.4.0: integrate the 7 new supplied 4:3 heroes.

Each source file was READ (not guessed from attachment order) and verified
to depict the system it is mapped to:
  gba       -> d9: GAME BOY ADVANCE (Pokemon Emerald)
  nds       -> 73: NINTENDO DS (Pokemon Diamond)
  psp       -> 0c: PLAYSTATION PORTABLE PSP (God of War: Chains of Olympus)
  ps2       -> 55: PlayStation 2 (DualShock 2)
  dreamcast -> c2: Dreamcast "GOOD GAMES LIVE ON" (blue spiral)
  genesis   -> da: SEGA GENESIS
  megadrive -> 4f: SEGA MEGA DRIVE
The unused Dreamcast alternate (95: "IT'S THINKING", orange spiral) also
passes the vet; it was skipped in favour of the blue-spiral variant which
sits better in Crystal's blue/white language.

All pass the design-language vet and the 4:3 contract: they render DIRECTLY
as fullscreen backgrounds, zero matte, zero bars, no crop, no stretch.
Re-sent files already integrated (snes, gc, n64, gbc, n3ds) are untouched.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import compose_v3 as C3

MEDIA = '/home/hatch/workspace/user/media_library/image'
OUT_BG = C3.OUT_BG

# system -> (filename, verified description)
HEROES = {
    'gba': ('d9/d92a4a1770b32cb0f735f9036f4d113a23263cc4e49515bec9ccbedf087ba763.jpg',
            'GAME BOY ADVANCE'),
    'nds': ('73/732a1a8500aa3499dcfa809e4510d157afc7aaf1cdc95530dea9cea353ed7e9d.jpg',
            'NINTENDO DS'),
    'psp': ('0c/0cb230445feb89e548ff14962a27ad877789c48acb2885aa4a93c22f0e0a162d.jpg',
            'PLAYSTATION PORTABLE PSP'),
    'ps2': ('55/5560d041caa0b2c5c330ff6fb294ca2e3f8844715f1a6b6f1ab1077e472c08f2.jpg',
            'PlayStation 2'),
    'dreamcast': ('c2/c2f82423acaa58ac5dc06209e0a410fa4796487202b6dce80baf58acd96debd6.jpg',
                  'Dreamcast GOOD GAMES LIVE ON'),
    'genesis': ('da/dabd249a36f0be9b9c0222cd82bb52bef9676498c65d2c2aa6511d9c602e3dd4.jpg',
                'SEGA GENESIS'),
    'megadrive': ('4f/4f5a479928fe899757b84520cd70191d91edbefb21c9483fee707847c1d5826a.jpg',
                  'SEGA MEGA DRIVE'),
}


def main():
    for sys, (rel, desc) in HEROES.items():
        src = os.path.join(MEDIA, rel)
        im = Image.open(src).convert('RGB')
        assert abs(im.size[0] / im.size[1] - 4 / 3) < 0.01, f'{sys} not 4:3: {im.size}'
        im.save(os.path.join(OUT_BG, f'{sys}.webp'), 'WEBP', quality=88, method=6)
        print('hero', sys, im.size, '-', desc)
    print('DONE')


if __name__ == '__main__':
    main()
