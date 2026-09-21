#!/usr/bin/env python3
"""Transform mock_gamelist_v17_4.py part B: shapes, highlight, marquee, title font."""
import re

P = "/home/hatch/workspace/crystal-esde-theme/work/mock_gamelist_v17_4.py"
s = open(P).read()
W = "/home/hatch/workspace/crystal-esde-theme/work/"

def block(path):
    return open(W + path).read().rstrip() + "\n"

# 2. shape renderers -> real fallback assets
start = s.index("# ------------------------------------------------------- shape renderers ---")
end = s.index('SHAPE_FN = {"cartridge": cartridge_shape, "gamecard": gamecard_shape,')
s = s[:start] + block("shapes_v17_4.txt") + "\n" + s[end:]

# 3. SHAPE_FULL assignment
s = s.replace('SHAPE_FULL = SHAPE_FN(G["title"])', "SHAPE_FULL = _shape_from_fallback()")

# 4. yellow_highlight follows the alpha bbox
start = s.index("def yellow_highlight(shape):")
end = s.index("# ------------------------------------------------------------ base canvas ---")
s = s[:start] + block("highlight_v17_4.txt") + "\n" + s[end:]

# 5. marquee: mounted on the page
start = s.index("# --------------------------------------- marquee: bold neutral band ---")
end = s.index("# ---------------------------------------------------------- metadata ---")
s = s[:start] + block("marquee_v17_4.txt") + "\n" + s[end:]

# 6. title font 36 -> 38 (0.040) and the 0.0375 check -> 0.040
s = s.replace("f5 = ImageFont.truetype(marker, 36)",
              "f5 = ImageFont.truetype(marker, 38)  # 0.040: the pedestal title")
s = s.replace('abs(float(get("text", "libGameName").findtext("fontSize")) - 0.0375) < 0.0005,\n'
              '      "title 0.0375 (clean air inside its box, not squeezed)")',
              'abs(float(get("text", "libGameName").findtext("fontSize")) - 0.040) < 0.0005,\n'
              '      "title 0.040 (stands up to the enormous media, known-shipped v17.2 size)")')

open(P, "w").write(s)
import ast
ast.parse(s)
print("part B done, syntax OK")
