#!/usr/bin/env python3
"""Transform mock_gamelist_v17_3.py -> mock_gamelist_v17_4.py (run once)."""
import sys

SRC = "/home/hatch/workspace/crystal-esde-theme/work/mock_gamelist_v17_3.py"
DST = "/home/hatch/workspace/crystal-esde-theme/work/mock_gamelist_v17_4.py"
s = open(SRC).read()

# 0. rename
s = s.replace("mock_gamelist_v17_3.py", "mock_gamelist_v17_4.py")
s = s.replace("Crystal v17.3.0 gamelist PREMIUM POLISH pass",
              "Crystal v17.4.0 gamelist EDITORIAL SHELL pass")
s = s.replace("work/proofs/mock_v17_3_%s.png", "work/proofs/mock_v17_4_%s.png")

# 1. docstring
start = s.index('"""PIL mock')
end = s.index("import os, sys, re, glob, math, xml.etree.ElementTree as ET")
new_doc = open("/home/hatch/workspace/crystal-esde-theme/work/doc_v17_4.txt").read()
s = s[:start] + new_doc + "\n" + s[end:]

open(DST, "w").write(s)
print("wrote", DST, len(s), "chars")
