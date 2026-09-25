#!/usr/bin/env python3
"""Crystal v18.5.2 SYSTEM-VIEW proofs for custom-collections (VM-ONLY, NEVER SHIPS).

The user rejected v18.5.0's "baked title is the hero" call: the supplied
lockup PNG is now the big main hero logo at PS1-spec geometry
(pos 0.64 0.39, maxSize 0.58 0.29, rotation -28, z30), and the
background's baked title was painted out (navy halftone stage).

Renders, light + dark, via the real XML geometry in proof_v18_4_sys:
  (a) SELECTED: the "Mario" collection selected - hero lockup over the
      new background, its carousel card 2x in the glow.
  (b) VS PSX: side-by-side of the collection view and the PS1 view -
      the hero-pattern match the user asked for ("look at ps1 for
      example").
The proof substitutes "Mario" for the ${system.name} binding.
"""
import os
import sys

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
sys.path.insert(0, os.path.join(REPO, "work"))
import proof_v18_4_sys as P
import proof_v18_5_sys_cc as V18_5

SYSTEM = "custom-collections"

P.per_system_overrides = V18_5.patched_ov
P.HERO_PATH_OVERRIDE = {SYSTEM: "art/console_logos/custom-collections.png"}
P.COUNTS[SYSTEM] = "12 GAMES"

P.NEIGHBORS[SYSTEM] = ["psx", "n64", "snes", SYSTEM, "gc", "gba", "wii"]

if __name__ == "__main__":
    from PIL import Image
    os.makedirs(P.PROOFS, exist_ok=True)
    W, H = 1280, 960
    for scheme in ("light", "dark"):
        sel = P.render_sys(SYSTEM, scheme)
        ps = os.path.join(P.PROOFS, f"v18_5_2_cc_selected_{scheme}.png")
        sel.save(ps)
        print("wrote", ps)
        ref = P.render_sys("psx", scheme)
        sbs = Image.new("RGB", (W * 2, H), (0, 0, 0))
        sbs.paste(sel, (0, 0)); sbs.paste(ref, (W, 0))
        pc = os.path.join(P.PROOFS, f"v18_5_2_cc_vs_psx_{scheme}.png")
        sbs.save(pc)
        print("wrote", pc)
