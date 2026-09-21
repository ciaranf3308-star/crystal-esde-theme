#!/usr/bin/env python3
"""Merge the v17.9.0 CONVERGENCE PASS into theme-src/crystal/views.xml
(gamelist section ONLY). Every replacement is an exact-match with an
assertion on occurrence count - the script fails loudly rather than
silently missing an edit. Macro geometry is otherwise untouched.

Whitelisted v17.9 moves (from the three parallel reviews):
  TYPOGRAPHY:
    * libGameName fontSize 0.0295 -> 0.0260 (Zelda 640.8px / 50.8px
      margins/side in the 742px box; DOOM 88px, GT4 245px stay
      confident). Two-line wrap is natively possible but the pedestal
      has no room (37px available, 75 needed) - one-line fixed stays.
    * Meta rail: DEVELOPER DROPPED PERMANENTLY. The 7-slot rail
      already failed on real inputs (FIRST-PERSON SHOOTER overflows
      the 151px genre slot; the AND-variant dev name overflows the
      398px dev slot) and ES-DE 3.4.1 cannot conditionally omit
      fields. New 5-slot layout: GENRE . YEAR . PLAYERS, contiguous,
      centred at x=900, genre slot widened 151->180px. Worst-case
      content group 314.1px in the 347px slot span.
    * libRating y +11px (470->481): centres the stars on the year
      digit caps instead of floating above them.
    * libDesc fontSize 0.0175 -> 0.0145: GT4 description wraps to
      54/50/40 chars (avg 48, inside the 45-70 target).
  COMPOSITION:
    * libShardNext regenerated (450x150 diagonal wedge, alpha 0 at
      TL corner -> peak ~65 at BR, all edges feathered) and moved
      (780,790)->(830,810): the next item reads as entering from the
      lower-right corner shadow, not sitting inside a pale panel.
    * libSelectedShadow narrowed 640->480px (hero footprint) and
      softened 0.9->0.7: grounding shadow, not a caption backing bar.
    * libScreenshot +8px y (724->732): the tightest joint in the
      column gains the air; baked frame follows in lib_panel_main.
    * One whisper: 2px #0A2FA0 hairline at alpha 8 baked into the
      panel (diagonal echo of the background geometry).
"""
import os, re, sys

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
VIEWS = os.path.join(REPO, "theme-src/crystal/views.xml")

xml = open(VIEWS, encoding="utf-8").read()
orig = xml
n_repl = 0

def sub_once(old, new, expect=1):
    global xml, n_repl
    c = xml.count(old)
    assert c == expect, f"expected {expect} occurrence(s), found {c}: {old[:80]!r}"
    xml = xml.replace(old, new)
    n_repl += 1

# ---------- 1. header comment: replace the whole v17.8.0 block ---------
start_m = "<!-- v17.8.0 (2026-09-21): RESPONSIVE ROBUSTNESS + FINAL COMPOSITION"
end_m = "asset slots. -->"
i, j = xml.index(start_m), xml.index(end_m) + len(end_m)
new_header = """<!-- v17.9.0 (2026-09-21): FULL CONVERGENCE PASS on the locked
             gamelist macro geometry. No style redesign, no fallback
             changes, no new components. Three parallel reviews
             (typography/responsive, composition/spacing,
             ES-DE-constraints) were merged into ONE implementation.
             Every fix below is measured against real DejaVuSans
             metrics at the 1280x960 4:3 target:
               - TITLE: fontSize 0.0295 -> 0.0260. The named failure
                 case "THE LEGEND OF ZELDA: OCARINA OF TIME 3D" is
                 640.8px inside the 742px (0.58) hero identity box -
                 50.8px margins/side, one line, never clips, never
                 exceeds the box, never touches prev/next media.
                 DOOM (88.1px) and GRAN TURISMO 4 (244.8px) stay
                 centred and confident. ES-DE 3.4.1 has no auto-shrink
                 and no dynamic sizing; two-line wrap IS native but
                 the pedestal has no room (37px available, 75 needed
                 for 2 lines at this size) and a second line would
                 paint the next-media region - the fixed one-line size
                 is the production answer. Legibility beats maximum
                 size.
               - META RAIL: DEVELOPER DROPPED PERMANENTLY. The 7-slot
                 rail already failed on real inputs: "FIRST-PERSON
                 SHOOTER" (173.5px) overflows the 151px genre slot and
                 "NINTENDO ENTERTAINMENT ANALYSIS AND DEVELOPMENT"
                 (411.1px) overflows the 398px dev slot. ES-DE 3.4.1
                 cannot conditionally omit fields (no conditional
                 visibility/layout - verified against the pinned 3.4.1
                 tables), so the requested "drop DEVELOPER when too
                 wide" is impossible. The fixed 5-slot rail
                 GENRE . YEAR . PLAYERS is the robust substitute:
                 contiguous, centred at x=900, genre slot widened
                 151 -> 180px, worst-case content group 314.1px inside
                 the 347px slot span. Developer already lives in the
                 left-column micro-grid (two-line wrap) - no
                 information is lost.
               - LEFT COLUMN: libRating y 470 -> 481 (+11px) centres
                 the stars on the year digit caps; libDesc 0.0175 ->
                 0.0145 gives 54/50/40-char lines (avg 48, inside the
                 45-70 target). Kickers are baked art - value positions
                 stay glued to them.
               - SCREENSHOT: y 724 -> 732 (+8px); the baked frame,
                 shadow, hairline and registration corner follow in
                 lib_panel_main.png. Height stays 170px.
               - NEXT SHARD: REGENERATED as a 450x150 diagonal wedge
                 (alpha 0 at top-left corner -> peak ~65 at
                 bottom-right, all four edges feathered - no panel, no
                 hard edges) and moved (780,790) -> (830,810). The next
                 item's visible mass sits outside the wedge's diagonal
                 cut, entering from the lower-right corner shadow. 42px
                 of air between the meta rail and the shard top.
               - HERO SHADOW: narrowed 640 -> 480px (the hero's own
                 footprint) and softened 0.9 -> 0.7 - a grounding
                 shadow, not a caption backing bar. The pedestal zone
                 now contains exactly: rule + title + rail.
               - PANEL: one whisper added - a 2px #0A2FA0 diagonal
                 hairline at alpha 8, local (294,0)->(470,180),
                 echoing the background's diagonal geometry.
               - MARQUEE: binding unchanged (native maxSize fit is
                 already the efficient mechanism: 4:1 fills 100% of
                 the width, 1:1.5 uses the full height, never
                 cropped). SPINE: unchanged (44x680 logo reads
                 authoritative; 48px/a2 dotgrid does not compete).
               - MOTION: carousel itemTransitions=animate stays
                 engaged (the accepted engine ceiling for 3.4.1). No
                 fake motion.
             PHYSICAL MEDIA AND FALLBACK ART ARE OUT OF SCOPE: all
             media_fallbacks/* PNGs remain byte-identical to the frozen
             v17.4 baseline; hero/marquee/screenshot are immutable live
             asset slots. -->"""
xml = xml[:i] + new_header + xml[j:]
n_repl += 1

# ---------- 2. title fontSize ------------------------------------------
sub_once('            <fontSize>0.0295</fontSize>\n',
         '            <fontSize>0.0260</fontSize>\n')

# ---------- 3. description fontSize ------------------------------------
sub_once('            <fontSize>0.0175</fontSize>\n',
         '            <fontSize>0.0145</fontSize>\n')

# ---------- 4. rating stars: centre on the year digit caps -------------
sub_once('            <pos>0.23125 0.4895833</pos>\n',
         '            <pos>0.23125 0.5011</pos>\n')

# ---------- 5. screenshot +8px y ---------------------------------------
sub_once('            <pos>0.0375 0.7541667</pos>\n',
         '            <pos>0.0375 0.7625</pos>\n')

# ---------- 6. hero shadow: narrower, softer ---------------------------
sub_once('            <size>0.5 0.075</size>\n',
         '            <size>0.375 0.075</size>\n')
sub_once('            <opacity>0.9</opacity>\n',
         '            <opacity>0.7</opacity>\n')

# ---------- 7. next shard: move to (830,810), size 450x150 -------------
sub_once('            <pos>0.609375 0.8229167</pos>\n',
         '            <pos>0.6484375 0.84375</pos>\n')
sub_once('            <size>0.390625 0.1770833</size>\n',
         '            <size>0.3515625 0.15625</size>\n')

# ---------- 8. delete libMetaDev + libMetaSep3 --------------------------
for ename in ("libMetaDev", "libMetaSep3"):
    tag = "text"
    blk_start = xml.index(f'<{tag} name="{ename}">')
    # NOTE: separator elements contain a nested <text>&#8226;</text> whose
    # closing tag would match a naive index("</text>") search first.
    # Find the element's own closing tag: the first </text> at the
    # element's indentation level (8 spaces).
    probe = blk_start
    while True:
        cand = xml.index(f"</{tag}>", probe)
        line_s = xml.rindex("\n", 0, cand) + 1
        if xml[line_s:cand] == " " * 8:
            blk_end = cand + len(f"</{tag}>")
            break
        probe = cand + 1
    # include the leading newline + indentation of the element line
    line_start = xml.rindex("\n", 0, blk_start) + 1
    # also swallow the single trailing newline after the closing tag
    line_end = blk_end + 1 if xml[blk_end:blk_end + 1] == "\n" else blk_end
    xml = xml[:line_start] + xml[line_end:]
    n_repl += 1

# ---------- 9. re-lay the 5 surviving rail slots ------------------------
sub_once('            <pos>0.4765625 0.7994792</pos>\n',
         '            <pos>0.6378906 0.7994792</pos>\n')
sub_once('            <size>0.1179688 0.02</size>\n',
         '            <size>0.140625 0.02</size>\n')
sub_once('            <pos>0.5414063 0.7994792</pos>\n',
         '            <pos>0.7140625 0.7994792</pos>\n')
sub_once('            <pos>0.5636719 0.7994792</pos>\n',
         '            <pos>0.7363281 0.7994792</pos>\n')
sub_once('            <pos>0.5859375 0.7994792</pos>\n',
         '            <pos>0.7585937 0.7994792</pos>\n')
sub_once('            <pos>0.9515625 0.7994792</pos>\n',
         '            <pos>0.8015625 0.7994792</pos>\n')

# ---------- 10. stale comment updates ----------------------------------
sub_once("""        <!-- 7. SCREENSHOT, an editorial image on the page (48,700
             396x210): aligned exactly with the text column.""",
         """        <!-- 7. SCREENSHOT, an editorial image on the page (48,732
             396x170): aligned exactly with the text column (moved +8px
             down in v17.9 so the column above breathes).""")

sub_once("""             The next-item shard was redesigned for the re-pitched
             carousel: (780,790 500x170), occluding the next item's
             upper-left along a diagonal, so its visible mass enters
             from the bottom-right corner, partially cropped - a
             distinct visual space from the selected game's title, which
             keeps clean air. -->""",
         """             The next-item shard was REGENERATED for v17.9
             (830,810 450x150): a diagonal wedge whose alpha ramps 0 at
             the top-left corner to peak ~65 at the bottom-right, all
             edges feathered - no panel, no hard edges. The next item's
             visible mass sits outside the wedge's diagonal cut,
             entering from the lower-right corner shadow - a distinct
             visual space from the selected game's title, which keeps
             clean air (42px between rail and shard top). -->""")

sub_once("""             beneath the media, detached soft contact shadow (slight
             elevation, strengthened). No rim, no rings, no circular""",
         """             beneath the media, detached soft contact shadow (slight
             elevation). v17.9: narrowed 640 -> 480px to the hero's own
             footprint and softened 0.9 -> 0.7 - a grounding shadow, not
             a caption backing bar. No rim, no rings, no circular""")

sub_once("""             one quiet composite rail at 767.5:
             GENRE . YEAR . DEVELOPER . PLAYERS. Generous vertical
             spacing; nothing competes with it: the next item enters
             from the bottom edge, cropped. The title is a STATIC
             single-line caption at a measured safe size (0.0295):
             ES-DE 3.4.1 has no auto-shrink and no dynamic sizing, and
             the scroll container proved unsatisfactory on-device, so
             the production rule is legibility beats maximum size. The
             worst-case title fits one line with margin; anything
             longer is beyond the measured envelope. -->""",
         """             one quiet composite rail at 767.5:
             GENRE . YEAR . PLAYERS (developer removed permanently in
             v17.9 - it duplicated the left-column micro-grid and the
             7-slot rail failed on real inputs; ES-DE 3.4.1 cannot
             conditionally omit fields). Generous vertical spacing;
             nothing competes with it: the next item enters from the
             lower-right corner shadow, cropped. The title is a STATIC
             single-line caption at a measured safe size (0.0260):
             ES-DE 3.4.1 has no auto-shrink and no dynamic sizing, and
             the scroll container proved unsatisfactory on-device, so
             the production rule is legibility beats maximum size. The
             worst-case title fits one line with 50.8px margins/side;
             anything longer is beyond the measured envelope. -->""")

assert xml != orig
open(VIEWS, "w", encoding="utf-8").write(xml)
print(f"merge ok: {n_repl} replacements")
