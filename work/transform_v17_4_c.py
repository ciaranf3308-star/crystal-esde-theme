#!/usr/bin/env python3
"""Transform mock_gamelist_v17_4.py part C: assertion replacements."""
import ast

P = "/home/hatch/workspace/crystal-esde-theme/work/mock_gamelist_v17_4.py"
W = "/home/hatch/workspace/crystal-esde-theme/work/"
s = open(P).read()


def block(path):
    return open(W + path).read().rstrip() + "\n"


def replace(start_marker, end_marker, path):
    """Replace text from start_marker through the end of the line
    containing end_marker with the block file."""
    global s
    start = s.index(start_marker)
    em = s.index(end_marker)
    end = s.index("\n", em) + 1
    s = s[:start] + block(path) + "\n" + s[end:]


def insert_after(anchor, path):
    """Insert the block file right after the line containing anchor."""
    global s
    i = s.index("\n", s.index(anchor)) + 1
    s = s[:i] + block(path) + "\n" + s[i:]


# 1. per-variant shape checks -> v17.4 fallback checks
replace(
    'if VARIANT == "cartridge":\n    check(0.75 <= hero.width / hero.height <= 0.92,',
    'check(0.75 <= cov <= 0.82, f"disc coverage {cov:.2f} (a circle, not a rounded box)")',
    "assert_shapes_v17_4.txt",
)

# 2. disc arc selectivity, inserted after the "no circular yellow frame" check
insert_after(
    'f"no circular yellow frame: selective accent only ({ann_y/max(1,ann_n):.1%} of the annulus)")',
    "assert_arc_v17_4.txt",
)

# 3. marquee block -> v17.4 open-white checks (keep the title comment line)
replace(
    "# --- v17.3 brief point 2: the marquee header is a SOLID feature banner ---",
    'f"no game-specific burst artwork in the marquee zone ({burst/(mw*mh):.1%} orange)")',
    "assert_marquee_v17_4.txt",
)

# 4. spine block -> v17.4 spine checks (keep the hygiene comment line)
replace(
    "# --- brief point 9: spine, dynamic binding, calmer decoration ---",
    'check(yell > 90, f"ONE continuous thin yellow structural line ({yell} samples)")',
    "assert_spine_v17_4.txt",
)

# 5. transition audit before hygiene
insert_before = "# --- hygiene: no amateur signals, no debug, bg + system view untouched ---"
_s = s
i = _s.index(insert_before)
s = _s[:i] + block("assert_transitions_v17_4.txt") + "\n" + _s[i:]

open(P, "w").write(s)
ast.parse(s)
print("part C done, syntax OK")
