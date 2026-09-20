#!/usr/bin/env python3
"""Regenerate esde_theme_tables.json from a pinned ES-DE ThemeData.cpp.

The tables must come from the ES-DE version actually running on the Nova
(currently 3.4.1), NOT from master: ES-DE's parseElement() THROWS on any
property missing from its per-element table, so a property that only
exists in a newer build fails the whole theme load on the device
(the v3.1.0 itemLinearScale incident).

Usage:
    python3 gen_tables.py /path/to/ThemeData.cpp   # writes esde_theme_tables.json
The pinned source is kept at /tmp only during generation; re-run whenever
the Nova's ES-DE version changes.
"""
import json
import re
import sys

src = open(sys.argv[1]).read()
tables = {}
for m in re.finditer(r'\{"([a-zA-Z]+)",\s*\{\{(.*?)(?=\}\},)', src, re.S):
    elem = m.group(1)
    # The table opens with '{{', which consumes the first property's own '{'.
    block = "{" + m.group(2)
    props = re.findall(r'\{"([a-zA-Z]+)",\s*([A-Z_]+)\}', block)
    tables[elem] = {p: t for p, t in props}

with open("esde_theme_tables.json", "w") as f:
    json.dump(tables, f)

counts = {e: len(p) for e, p in tables.items()}
print(f"wrote esde_theme_tables.json: {len(tables)} elements")
print("carousel props:", len(tables["carousel"]),
      "| itemLinearScale present:", "itemLinearScale" in tables["carousel"])
