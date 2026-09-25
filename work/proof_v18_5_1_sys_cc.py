#!/usr/bin/env python3
"""Crystal v18.5.1 SYSTEM-VIEW proofs for custom-collections (VM-ONLY, NEVER SHIPS).

Two states, light + dark, via the real XML geometry in proof_v18_4_sys:
  (a) SELECTED: the "Mario" collection is the selected system - its card
      (cards/custom-collections.png, the fixed <staticImage> override)
      renders 2x in the glow; background = collections scene.
  (b) IN-STRIP: psx selected, the collection's card visible dimmed in the
      strip (unfocused dimming/saturation per the real XML).
The proof harness resolves cards/{neighbor}.png per strip entry, which
mirrors the real engine: the fixed staticImage path means every custom
collection's entry loads cards/custom-collections.png.
"""
import os
import sys

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
sys.path.insert(0, os.path.join(REPO, "work"))
import proof_v18_4_sys as P
import proof_v18_5_sys_cc as V18_5

SYSTEM = "custom-collections"

P.per_system_overrides = V18_5.patched_ov
P.COUNTS[SYSTEM] = "12 GAMES"

# (a) collection selected: the collection's card is the 2x center item.
P.NEIGHBORS[SYSTEM] = ["psx", "n64", "snes", SYSTEM, "gc", "gba", "wii"]
# (b) psx selected, collection dimmed in the strip.
P.NEIGHBORS["psx"] = ["n64", "snes", SYSTEM, "psx", "gc", "gba", "wii"]

if __name__ == "__main__":
    from PIL import Image
    os.makedirs(P.PROOFS, exist_ok=True)
    W, H = 1280, 960
    for scheme in ("light", "dark"):
        sel = P.render_sys(SYSTEM, scheme)
        ps = os.path.join(P.PROOFS, f"v18_5_1_cc_selected_{scheme}.png")
        sel.save(ps)
        print("wrote", ps)
        strip = P.render_sys("psx", scheme)
        pi = os.path.join(P.PROOFS, f"v18_5_1_cc_instrip_{scheme}.png")
        strip.save(pi)
        print("wrote", pi)
        sbs = Image.new("RGB", (W * 2, H), (0, 0, 0))
        sbs.paste(sel, (0, 0)); sbs.paste(strip, (W, 0))
        pc = os.path.join(P.PROOFS, f"v18_5_1_cc_sbs_{scheme}.png")
        sbs.save(pc)
        print("wrote", pc)
