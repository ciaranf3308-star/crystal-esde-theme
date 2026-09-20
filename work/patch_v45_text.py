#!/usr/bin/env python3
"""Crystal v4.5.0 text pass — surgical patch of per-system theme.xml files.

Applies the v4.5.0 unified text grid WITHOUT regenerating files from scratch,
so the v4.4.0 selectedPoster overlays, comments, and formatting survive.

Changes:
  views.xml base: sysDesc pos 0.305->0.281, countNum 0.460->0.354,
                  factsLine 0.535->0.415 (the unified grid)
  Per-system:
    - sysName fontSize = measured v45 size (static short titles for
      gba/gbc/psp; gb box overrides removed)
    - sysDesc/countNum/factsLine pos overrides: KEPT only for forced-
      threading systems (dreamcast, gc, gbc, nds) and two-line nes;
      REMOVED for common-grid systems (they inherit the new base)
    - gb countNum unified to base 0.055 (drops the v4.0 0.042 exception)
    - nes grid tightened to (0.305, 0.375, 0.440); snes already correct
"""
import os
import re
import sys

REPO = '/home/hatch/workspace/crystal-esde-theme/theme-src/crystal'
BASE_SIZE = 0.040  # views.xml sysName base fontSize (fraction of H)

# sys -> (static_title or None, fontSize)
V45_TITLE = {
    'dreamcast': (None, 0.035),
    'gb':        (None, 0.029),
    'gba':       ('Game Boy Advance', 0.030),
    'gbc':       ('Game Boy Color', 0.036),
    'gc':        (None, 0.028),
    'genesis':   (None, 0.040),
    'megadrive': (None, 0.034),
    'n3ds':      (None, 0.040),
    'n64':       (None, 0.040),
    'nds':       (None, 0.040),
    'ps2':       (None, 0.030),
    'psp':       ('PSP', 0.040),
    'psx':       (None, 0.034),
    'steam':     (None, 0.040),
    'wii':       (None, 0.040),
    'wiiu':      (None, 0.038),
    'windows':   (None, 0.040),
    'xbox':      (None, 0.038),
    'xbox360':   (None, 0.030),
}
# sys -> (desc_y, count_y, facts_y); systems NOT listed inherit the base grid
V45_LAYOUT = {
    'dreamcast': (0.275, 0.350, 0.411),
    'gc':        (0.275, 0.350, 0.411),
    'gbc':       (0.302, 0.358, 0.431),
    'nds':       (0.273, 0.344, 0.405),
    'nes':       (0.305, 0.375, 0.440),
    'snes':      (0.341, 0.397, 0.458),
}


def patch_views():
    p = os.path.join(REPO, 'views.xml')
    s = open(p).read()
    orig = s
    # sysDesc block: pos 0.030 0.305 -> 0.030 0.281
    s = re.sub(
        r'(<text name="sysDesc">\s*<pos>)0\.030 0\.305(</pos>)',
        r'\g<1>0.030 0.281\g<2>', s)
    # countNum block: pos 0.030 0.460 -> 0.030 0.354
    s = re.sub(
        r'(<text name="countNum">\s*<pos>)0\.030 0\.460(</pos>)',
        r'\g<1>0.030 0.354\g<2>', s)
    # factsLine block: pos 0.030 0.535 -> 0.030 0.415
    s = re.sub(
        r'(<text name="factsLine">\s*<pos>)0\.030 0\.535(</pos>)',
        r'\g<1>0.030 0.415\g<2>', s)
    # idempotent: skip if already at the v4.5.0 grid
    if '0.030 0.281</pos>' in s and 'name="sysDesc"' in s:
        print('views.xml base grid already at v4.5.0')
        return
    assert s != orig, 'views.xml: no replacements made!'
    open(p, 'w').write(s)
    print('patched views.xml base grid')


def get_text_block(s, name):
    """Return (full_match, inner) for <text name="X">...</text>.
    Inner is normalized to end with a newline."""
    m = re.search(
        r'(<text name="%s">\n)(.*?)(\n        </text>)' % re.escape(name),
        s, re.DOTALL)
    if not m:
        return None, None
    inner = m.group(2)
    if not inner.endswith('\n'):
        inner += '\n'
    return m.group(0), inner


def set_or_remove_pos(inner, y):
    """Set <pos>0.030 Y</pos> if y given, else remove the <pos> line."""
    if y is None:
        inner = re.sub(r'            <pos>0\.030 [\d.]+</pos>\n', '', inner)
        # also remove a threading comment that only made sense with the pos
        inner = re.sub(
            r'            <!-- panel threading: sits between this background\'s ruled lines -->\n',
            '', inner)
    else:
        new_pos = f'            <pos>0.030 {y:.3f}</pos>\n'
        if '<pos>' in inner:
            inner = re.sub(r'            <pos>0\.030 [\d.]+</pos>\n', new_pos,
                           inner)
        else:
            # insert pos after the opening, before any comment/text
            inner = new_pos + inner
    return inner


def patch_system(sys):
    p = os.path.join(REPO, sys, 'theme.xml')
    s = open(p).read()
    orig = s
    is_two_line = sys in ('nes', 'snes')

    if not is_two_line:
        title, tsize = V45_TITLE[sys]
        # --- sysName ---
        full, inner = get_text_block(s, 'sysName')
        if full is None:
            # No override block: correct only if we want base size + systemdata.
            # (build_v40 omits the block when size == BASE_SIZE.)
            assert title is None and abs(tsize - BASE_SIZE) < 1e-9, \
                f'{sys}: missing sysName block but needs one'
        else:
            # set fontSize
            inner = re.sub(r'<fontSize>[\d.]+</fontSize>',
                           f'<fontSize>{tsize:.3f}</fontSize>', inner)
            # remove any <size> override (gb's narrow box)
            inner = re.sub(r'            <size>[\d.]+ [\d.]+</size>\n', '', inner)
            # static title for gba/gbc/psp; ensure no static text for others
            inner = re.sub(r'            <text>.*?</text>\n', '', inner)
            if title:
                inner += f'            <text>{title}</text>\n'
            s = s.replace(full, f'<text name="sysName">\n{inner}\n        </text>')

        # --- sysDesc / countNum / factsLine positions ---
        layout = V45_LAYOUT.get(sys)
        for name, idx in (('sysDesc', 0), ('countNum', 1), ('factsLine', 2)):
            full, inner = get_text_block(s, name)
            y = layout[idx] if layout else None
            if full is None:
                # No override block: inherits base. Correct for common-grid
                # systems; forced-layout systems must not be missing.
                assert y is None, f'{sys}: {name} block missing but layout needs pos'
                continue
            inner = set_or_remove_pos(inner, y)
            # gb: drop the narrow size / small count overrides (unified)
            if sys == 'gb':
                inner = re.sub(r'            <size>[\d.]+ [\d.]+</size>\n',
                               '', inner)
                if name == 'countNum':
                    inner = re.sub(r'            <fontSize>[\d.]+</fontSize>\n',
                                   '', inner)
            s = s.replace(full, f'<text name="{name}">\n{inner}\n        </text>')
    else:
        # two-line: only adjust desc/count/facts pos to the v45 layout
        layout = V45_LAYOUT[sys]
        for name, idx in (('sysDesc', 0), ('countNum', 1), ('factsLine', 2)):
            full, inner = get_text_block(s, name)
            assert full, f'{sys}: {name} block not found'
            inner = set_or_remove_pos(inner, layout[idx])
            s = s.replace(full, f'<text name="{name}">\n{inner}\n        </text>')

    if s != orig:
        open(p, 'w').write(s)
        print(f'patched {sys}')
    else:
        print(f'{sys}: no change')


if __name__ == '__main__':
    patch_views()
    systems = sorted(V45_TITLE.keys()) + ['nes', 'snes']
    for sys in systems:
        patch_system(sys)
    print('DONE')
