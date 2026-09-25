#!/usr/bin/env python3
"""Crystal v18.5.0 SYSTEM-VIEW proof for custom-collections (VM-ONLY, NEVER SHIPS).

Renders the custom-collections system view in light and dark using the
real XML geometry via proof_v18_4_sys.render_sys. The collection name
is user-chosen; the proof substitutes a realistic example ("Mario") for
the ${system.name} binding. Neighbours are a plausible carousel slice.
"""
import os
import sys

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
sys.path.insert(0, os.path.join(REPO, "work"))
import proof_v18_4_sys as P
import xml.etree.ElementTree as ET

SYSTEM = "custom-collections"

# Realistic example collection name for the ${system.name} binding.
# (Parsed with ElementTree: the shared harness regex stops at the first
# inner </text> and misses content placed after <fontSize>, as in every
# per-system module.)


def patched_ov(system):
    xml = open(os.path.join(P.CRYS, system, "theme.xml"), encoding="utf-8").read()
    root = ET.fromstring(xml)
    out = {}
    for elem in root.iter("view"):
        if elem.get("name") != "system":
            continue
        for t in elem.iter("text"):
            name = t.get("name")
            if not name:
                continue
            props = {}
            for child in t:
                if child.tag in ("pos", "size", "fontSize"):
                    props[child.tag] = (child.text or "").strip()
                elif child.tag == "text":
                    props["text"] = (child.text or "").strip()
            out[name] = props
    if out.get("sysName", {}).get("text") == "${system.name}":
        out["sysName"]["text"] = "Mario"
    return out


P.per_system_overrides = patched_ov
P.NEIGHBORS[SYSTEM] = ["psx", "n64", "snes", "psx", "gc", "gba", "wii"]
P.COUNTS[SYSTEM] = "12 GAMES"

if __name__ == "__main__":
    os.makedirs(P.PROOFS, exist_ok=True)
    for scheme in ("light", "dark"):
        img = P.render_sys(SYSTEM, scheme)
        out = os.path.join(P.PROOFS, f"v18_5_custom_collections_{scheme}.png")
        img.save(out)
        print("wrote", out)
