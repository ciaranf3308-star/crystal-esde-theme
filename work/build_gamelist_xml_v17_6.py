#!/usr/bin/env python3
"""Build work/gamelist_view_v17_6.xml from the v17.5.0 section.

Edits are TYPOGRAPHY-ONLY: every pos/size/origin/zIndex value is
preserved byte-for-byte (macro geometry lock). Changes:
- PermanentMarker -> DejaVuSans-Bold on libMarqueeTitle, libYear,
  libGameName (the brush face is deleted from the theme).
- libMarqueeTitle fontSize 0.04 -> 0.034; libYear 0.06 -> 0.050;
  libGenre 0.024 -> 0.022 (DejaVu runs heavier than the marker face).
- Explicit fontPath on every remaining gamelist text element:
  DejaVuSans-Bold for display/anchors (libGenre), DejaVuSans (Regular)
  for body/micro (libDesc, libPlayers, libDev, the meta rail, footer).
- Comments rewritten for the v17.6 maturity pass.
"""
import os, re

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
src = open(os.path.join(REPO, "work/gamelist_view_v17_5.xml"), encoding="utf-8").read()

# ---- header comment swap (from the opening <!-- to the closing -->) ----
start = src.index("<!-- v17.5.0")
end = src.index("-->", start) + 3
header = """<!-- v17.6.0 (2026-09-21): VISUAL MATURITY PASS on the locked
             gamelist macro geometry. Every element pos/size/origin/
             zIndex is byte-identical to v17.5.0 (panel 6,10 470x940;
             spine 486,24 60x912; hero 540px at 900,430; rule Y716 /
             title Y736 / meta Y767.5; screenshot 42,700 396x210;
             footer y915). What changes is maturity only:
               - TYPOGRAPHY DISCIPLINE: PermanentMarker is REMOVED from
                 the theme (file deleted) and from game titles, the
                 marquee fallback, metadata values, secondary labels and
                 the year anchor. New system: Display = DejaVuSans-Bold
                 (title, marquee fallback, year anchor, genre);
                 Body = DejaVuSans Regular (description, players,
                 developer, meta rail, footer micro). No expressive
                 lettering survives in the gamelist shell - the marquee
                 slot carries the game's personality, shell type stays
                 quiet/premium/controlled.
               - YELLOW <=5%: audit of every gamelist yellow usage. Kept:
                 masthead registration square, screenshot registration
                 corner, spine's one thin 1px structural line, the
                 pedestal's one thin rule. Deleted/shrunk: the NOW
                 SHOWING yellow triangle, the rule-425 yellow square, the
                 blue intrusion + its yellow leading edges, both yellow
                 micro ticks, the spine tab, the title-rule end-ticks
                 (rule is now one thin 120px bar), and the yellow rating
                 stars (recolored royal blue).
               - LEFT PAGE: one editorial page - the blueprint fragment
                 and the blue geometric intrusion are deleted; one
                 whisper-quiet halftone at the angular right edge is the
                 single remaining halftone area; open whitespace, sparse
                 rules, baked kickers in DejaVuSans-Bold micro.
               - MARQUEE MASTHEAD: same zone, real ${game.marquee}
                 binding prominent, aspect preserved, no dark container,
                 no opacity wash, NOW SHOWING tiny microcopy, no system
                 abbreviation (the spine identifies the platform).
               - METADATA RESTRAINT: year = one strong display-sans
                 anchor; genre = secondary emphasis; players/developer =
                 quiet aligned two-column micro-grid; rating = small
                 royal supporting indicator; description = calm body.
               - SCREENSHOT: real ${game.screenshot} binding, no frame,
                 one bottom hairline, one tiny registration mark.
               - SPINE: deeper solid royal blue, dotgrid further reduced
                 (32px/alpha 4), ONE thin 1px yellow structural line,
                 supplied logo mounted with breathing room (plate without
                 outline), still dynamically bound to all 21 systems via
                 ${system.name}.
               - TITLE PEDESTAL: DejaVuSans-Bold display title (no brush),
                 GENRE - YEAR - DEVELOPER - PLAYERS rail, one subtle
                 yellow rule, generous spacing. Y positions preserved
                 (title 736, meta rail 767.5).
               - PREV/NEXT: pure bound physicalmedia, scale/position/
                 opacity treatment only.
               - MOTION (re-verified against the pinned
                 esde_theme_tables.json AND the official ES-DE theme
                 docs): carousel itemTransitions (animate) is the only
                 element-motion capability in 3.4.1 and stays engaged on
                 the carousel. <animation> is an animated-IMAGE component
                 (direction/speed/iterationCount = playback control), not
                 UI animation. No keyframes, crossfades, durations,
                 per-element animation, or idle float exist in the
                 schema: marquee/screenshot/title/metadata transitions
                 and explicit scale/position/opacity interpolation are
                 impossible in 3.4.1 and are not claimed.
             PHYSICAL MEDIA AND FALLBACK ART ARE OUT OF SCOPE: the hero,
             marquee and screenshot are immutable live asset slots; all
             media_fallbacks/* PNGs and hero-treatment assets remain
             byte-identical to the frozen v17.4 baseline. -->"""
src = src[:start] + header + src[end:]

# ---- brush face -> DejaVuSans-Bold (3 gamelist usages) ----
n = src.count("PermanentMarker-Regular.ttf")
assert n == 3, f"expected 3 PermanentMarker refs, found {n}"
src = src.replace("PermanentMarker-Regular.ttf", "DejaVuSans-Bold.ttf")

def block(name):
    """Return (start, end) of the element block with the given name."""
    i = src.index(f'name="{name}"')
    tag = src[src.rindex("<", 0, i) + 1:].split()[0]
    s = src.rindex("<" + tag + " ", 0, i)
    e = src.index(f"</{tag}>", i) + len(f"</{tag}>")
    return s, e

def edit_block(name, fn):
    global src
    s, e = block(name)
    src = src[:s] + fn(src[s:e]) + src[e:]

def set_font(b, font):
    if "<fontPath>" in b:
        b = re.sub(r"<fontPath>[^<]*</fontPath>",
                   f"<fontPath>{font}</fontPath>", b)
    else:
        b = b.replace("<fontSize>", f"<fontPath>{font}</fontPath>\n            <fontSize>", 1)
    return b

def set_size(b, old, new):
    assert f"<fontSize>{old}</fontSize>" in b, old
    return b.replace(f"<fontSize>{old}</fontSize>", f"<fontSize>{new}</fontSize>", 1)

BOLD = "./fonts/DejaVuSans-Bold.ttf"
REG = "./fonts/DejaVuSans.ttf"

edit_block("libMarqueeTitle", lambda b: set_size(set_font(b, BOLD), "0.04", "0.034"))
edit_block("libYear", lambda b: set_size(set_font(b, BOLD), "0.06", "0.050"))
edit_block("libDesc", lambda b: set_font(b, REG))
edit_block("libGenre", lambda b: set_size(set_font(b, BOLD), "0.024", "0.022"))
edit_block("libPlayers", lambda b: set_font(b, REG))
edit_block("libDev", lambda b: set_font(b, REG))
edit_block("libGameName", lambda b: set_font(b, BOLD))
for m in ("libMetaGenre", "libMetaYear", "libMetaDev", "libMetaPlayers"):
    edit_block(m, lambda b: set_font(b, REG))

def insert_font_after_origin(name, font):
    # elements whose block contains a nested <text> (truncates block
    # parsing): anchor on the name, then on the first <origin> after it
    global src
    i = src.index(f'name="{name}"')
    j = src.index("<origin>", i)
    k = src.index("</origin>", j) + len("</origin>")
    src = src[:k] + f"\n            <fontPath>{font}</fontPath>" + src[k:]

for m in ("libMetaSep1", "libMetaSep2", "libMetaSep3"):
    insert_font_after_origin(m, REG)
# footer: same nested-<text> problem; anchor on name, insert before <fontSize>
i = src.index('name="libFooter"')
j = src.index("<fontSize>", i)
src = src[:j] + f"<fontPath>{REG}</fontPath>\n            " + src[j:]

assert "PermanentMarker-Regular.ttf" not in src.replace(
    src[src.index("<!-- v17.6.0"):src.index("-->", src.index("<!-- v17.6.0"))], "")

# ---- section-12 comment rewrite (title pedestal) ----
old12 = """        <!-- 12. TITLE beneath the hero: generous clean air around the
             identity block. Redesigned rule at 716 (white hairline +
             SHORT yellow bar with a sweep head), bolder marker display
             title in white at 736, composite secondary line at 757:
             GENRE . YEAR . DEVELOPER . PLAYERS. Nothing competes with it:
             the next item enters from the bottom edge, cropped. -->"""
new12 = """        <!-- 12. TITLE beneath the hero: museum/display caption paired
             with the object above. One thin subtle yellow rule at 716,
             DejaVuSans-Bold display title in white at 736 (no brush),
             one quiet composite rail at 767.5:
             GENRE . YEAR . DEVELOPER . PLAYERS. Generous vertical
             spacing; nothing competes with it: the next item enters
             from the bottom edge, cropped. -->"""
assert old12 in src
src = src.replace(old12, new12)

out = os.path.join(REPO, "work/gamelist_view_v17_6.xml")
open(out, "w", encoding="utf-8").write(src)
print("wrote", out, len(src), "bytes")
