#!/usr/bin/env python3
"""Merge the v18.0.0 ART-DIRECTION PASS into theme-src/crystal/views.xml
(gamelist section ONLY). Every replacement is an exact-match with an
assertion on occurrence count - the script fails loudly rather than
silently missing an edit.

Whitelisted v18.0 moves (judged against full-looking VM proof screens
with proxy assets - the first time the shell could actually be SEEN):
  1. HERO STAGE: libPlaneHero was a 420x360 asset reading as a pale
     RECTANGLE behind the hero ("asset box"). Replaced with a 900x900
     fully-feathered radial wash (no edges); element re-centred on the
     hero (0.703125 0.4479167, origin 0.5 0.5, size 0.703125 0.9375).
     The hero now reads suspended over the Nova environment.
  2. CAROUSEL PATH: size 1.6 -> 1.53125, pos y 0.4479167 -> 0.453125.
     Previous now peeks ~65px in from the top edge (upper-right,
     partially off-screen) instead of hiding entirely; next sits at
     y=925 (30px clear of the metadata rail, cropped ~85px by the
     screen edge) - entering from the lower-right corner shadow.
     itemTransitions=animate untouched.
  3. YEAR: libYear fontSize 0.050 -> 0.044. The giant display year
     competed with the screenshot; the anchor row is calmer now.
  4. HERO GROUNDING: libSelectedShadow opacity 0.7 -> 0.8 - the
     selected object sits IN the space with more presence.
  5. SPINE (assets, see gen_v18_assets.py): rails regenerated with
     6px feathered left/right edges (the bar melts into panel and
     stage - it binds the page instead of splitting it), dotgrid
     48px/a2 -> 64px/a1, logo caps 44x680 -> 48x720 (optical lift
     kept), yellow line x=4 -> x=8 (crisp outside the feather).

Macro geometry otherwise locked. Fallback media untouched.
"""
import os

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
VIEWS = os.path.join(REPO, "theme-src/crystal/views.xml")

xml = open(VIEWS, encoding="utf-8").read()
n_repl = 0

def sub_once(old, new, expect=1):
    global xml, n_repl
    c = xml.count(old)
    assert c == expect, f"expected {expect} occurrence(s), found {c}: {old[:80]!r}"
    xml = xml.replace(old, new)
    n_repl += 1

# ---------- 1. header comment: replace the whole v17.9.0 block ---------
start_m = "<!-- v17.9.0 (2026-09-21): FULL CONVERGENCE PASS"
end_m = "asset slots. -->"
i, j = xml.index(start_m), xml.index(end_m) + len(end_m)
new_header = """<!-- v18.0.0 (2026-09-21): ART-DIRECTION PASS on the locked gamelist
             macro geometry. v17.9's review screens rendered EMPTY asset
             slots, so no real visual review was possible; this pass was
             judged against a VM-ONLY proof harness (work/proof_assets/,
             never shipped) compositing abstract proxies for marquee /
             screenshot / disc / cartridge / DS-card into the real XML
             geometry. Visible changes, not micro-numbers:
               - HERO STAGE: lib_plane_hero.png regenerated as a 900x900
                 fully-feathered radial wash (centre alpha 26 -> 0, no
                 edges). The old 420x360 asset read as a pale rectangle
                 behind the hero; the hero now reads suspended over the
                 Nova environment with subtle local contrast. Element
                 re-centred: pos 0.703125 0.4479167, origin 0.5 0.5,
                 size 0.703125 0.9375, z44.
               - CAROUSEL PATH: size 0.5 1.6 -> 0.5 1.53125, pos y
                 0.4479167 -> 0.453125. Previous peeks ~65px in from the
                 top edge (upper-right, partially off-screen) instead of
                 hiding entirely; next sits at y=925 - 30px clear of the
                 metadata rail, ~85px cropped by the screen edge -
                 entering from the lower-right corner shadow.
                 itemTransitions=animate stays engaged (engine ceiling).
               - YEAR: libYear fontSize 0.050 -> 0.044 - the display year
                 no longer competes with the screenshot.
               - GROUNDING: libSelectedShadow opacity 0.7 -> 0.8.
               - SPINE: rails regenerated - 6px feathered left/right
                 edges (the bar melts into panel and stage, binding the
                 page instead of splitting it), dotgrid 48px/a2 ->
                 64px/a1, logo caps 44x680 -> 48x720 (6px optical lift
                 kept), the 1px yellow structural line x=4 -> x=8 so it
                 stays crisp outside the feather zone.
             ES-DE 3.4.1 limits still stand (no dynamic sizing, no
             conditional visibility/layout) - the worst-case fixed
             geometry from v17.8/v17.9 is unchanged.
             PHYSICAL MEDIA AND FALLBACK ART ARE OUT OF SCOPE: all
             media_fallbacks/* PNGs remain byte-identical to the frozen
             v17.4 baseline; hero/marquee/screenshot are immutable live
             asset slots. -->"""
xml = xml[:i] + new_header + xml[j:]
n_repl += 1

# ---------- 2. carousel: tighter track, neighbours read as a path -----
sub_once("<type>vertical</type>\n            <color>00000000</color>\n"
         "            <pos>0.703125 0.4479167</pos>",
         "<type>vertical</type>\n            <color>00000000</color>\n"
         "            <pos>0.703125 0.453125</pos>")
sub_once("<size>0.5 1.6</size>", "<size>0.5 1.53125</size>")

# ---------- 3. hero plane: centred radial wash, no rectangle -----------
old_plane = ('<image name="libPlaneHero">\n'
             '            <pos>0.6875 0.5625</pos>\n'
             '            <size>0.328125 0.375</size>\n'
             '            <origin>0 0</origin>\n'
             '            <path>./art/lib_plane_hero.png</path>\n'
             '            <zIndex>44</zIndex>\n'
             '        </image>')
new_plane = ('<image name="libPlaneHero">\n'
             '            <pos>0.703125 0.4479167</pos>\n'
             '            <size>0.703125 0.9375</size>\n'
             '            <origin>0.5 0.5</origin>\n'
             '            <path>./art/lib_plane_hero.png</path>\n'
             '            <zIndex>44</zIndex>\n'
             '        </image>')
sub_once(old_plane, new_plane)

# ---------- 4. year: calmer anchor -------------------------------------
sub_once("<fontSize>0.050</fontSize>", "<fontSize>0.044</fontSize>")

# ---------- 5. hero grounding ------------------------------------------
sub_once("<opacity>0.7</opacity>", "<opacity>0.8</opacity>")

open(VIEWS, "w", encoding="utf-8").write(xml)
print(f"merge_v18: {n_repl} replacements applied")
