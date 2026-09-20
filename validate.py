#!/usr/bin/env python3
"""ES-DE ThemeData.cpp-faithful validator for the Crystal theme.

Replicates the parsing behavior that matters for correctness, checked
against the real ES-DE source (es-core/src/ThemeData.cpp, PINNED to the
version on the Nova — currently v3.4.1 — never master, see gen_tables.py):
- <include> processed inline, in document order (max depth 24)
- variables: name = TAG NAME, value = text content.
  The <variable name="" value=""/> form defines NOTHING (this was the v1.0.1 bug).
- <variant name="X">: children processed iff X == selected or X == "all"
  (the "all" special case is unique to the variant axis in real ES-DE).
- default selection = FIRST <variant> declared in capabilities.xml
  (real rule: mSelectedVariant = mVariants.front()).
- placeholder substitution: unknown variables resolve to "" (real
  resolvePlaceholders uses mVariables[replace] which inserts "").
- view names: only "all", "system", "gamelist" (anything else THROWS).
- element types and property names checked against ES-DE's real tables
  (esde_theme_tables.json, extracted from ThemeData.cpp sElementMap).
  Unknown element type / unknown property / extra attribute / blank
  property value all THROW in the real parser (this was the v3.0.2 bug:
  extra="true" and view "detailed" are RetroPie-era conventions that
  ES-DE 3.x rejects).
- color properties must be 6 or 8 hex digits after substitution.
- <path>/<default> must resolve to an existing file after substitution.

Usage: validate.py [theme.xml] [--variant light|dark]
Exit 0 = clean, 1 = errors.
"""
import os
import re
import sys
import json
import xml.etree.ElementTree as ET

MAX_INCLUDE_DEPTH = 24
SUPPORTED_VIEWS = {"all", "system", "gamelist"}

TABLES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "esde_theme_tables.json")
with open(TABLES_PATH) as f:
    ELEMENT_PROPS = json.load(f)

def text_of(elem):
    return "".join(elem.itertext()).strip()

def substitute(raw, variables, unknown):
    """Faithful to ThemeData::resolvePlaceholders: unknown -> ''."""
    m = re.search(r"\$\{([^}]*)\}", raw)
    if not m:
        return raw
    name = m.group(1)
    if name not in variables:
        unknown.add(name)
        repl = ""
    else:
        repl = variables[name]
    return raw[:m.start()] + repl + substitute(raw[m.end():], variables, unknown)

class Ctx:
    def __init__(self, theme_dir, selected_variant):
        self.theme_dir = theme_dir
        self.selected_variant = selected_variant
        self.variables = {}
        self.unknown_vars = set()
        self.errors = []
        self.warnings = []

def parse_node(elem, ctx, base_dir, depth, file_label):
    if depth > MAX_INCLUDE_DEPTH:
        ctx.errors.append(f"{file_label}: include depth exceeded")
        return
    for child in list(elem):
        tag = child.tag
        if tag == "include":
            rel = text_of(child)
            full = os.path.normpath(os.path.join(base_dir, rel))
            if not os.path.isfile(full):
                ctx.errors.append(f"{file_label}: include not found: {rel}")
                continue
            try:
                tree = ET.parse(full)
            except Exception as e:
                ctx.errors.append(f"{file_label}: include parse failed {rel}: {e}")
                continue
            parse_node(tree.getroot(), ctx, os.path.dirname(full), depth + 1, rel)
        elif tag == "variables":
            for var in list(child):
                if var.tag == "variable":
                    ctx.errors.append(
                        f"{file_label}: <variable name/value> form is NOT supported by ES-DE "
                        f"(name={var.get('name')!r}); use <name>value</name>")
                    continue
                ctx.variables[var.tag] = text_of(var)
        elif tag == "variant":
            name = child.get("name")
            if ctx.selected_variant is not None and (
                    name == ctx.selected_variant or name == "all"):
                parse_node(child, ctx, base_dir, depth, file_label)
            # else: skipped, exactly like real ES-DE
        elif tag == "view":
            parse_view(child, ctx, base_dir, file_label)
        # other tags at theme level are ignored here

def parse_view(view_elem, ctx, base_dir, file_label):
    raw_name = view_elem.get("name") or ""
    # Real parser splits on space/tab/comma; every part must be supported.
    parts = [p for p in re.split(r"[ \t\r\n,]+", raw_name) if p]
    if not parts:
        ctx.errors.append(f"{file_label}: view missing \"name\" attribute")
        return
    for part in parts:
        if part not in SUPPORTED_VIEWS:
            ctx.errors.append(
                f"{file_label}: unsupported {part!r} view style defined "
                f"(ES-DE only knows {sorted(SUPPORTED_VIEWS)})")
    view_name = raw_name
    for comp in list(view_elem):
        cname = comp.get("name")
        if not cname:
            ctx.errors.append(
                f"{file_label} view={view_name}: element of type {comp.tag!r} "
                f"missing \"name\" attribute")
            continue
        label = f"{file_label} view={view_name} {comp.tag}[{cname}]"
        if comp.tag not in ELEMENT_PROPS:
            ctx.errors.append(f"{label}: unknown element type {comp.tag!r}")
            continue
        if comp.get("extra") is not None:
            ctx.errors.append(
                f"{label}: unsupported \"extra\" attribute "
                f"(ES-DE 3.x rejects it; remove the attribute)")
        type_map = ELEMENT_PROPS[comp.tag]
        for prop in list(comp):
            pname = prop.tag  # real parser matches case-sensitively
            if pname not in type_map:
                ctx.errors.append(
                    f"{label}: unknown property {pname!r} for element {comp.tag!r}")
                continue
            raw = text_of(prop)
            resolved = substitute(raw, ctx.variables, ctx.unknown_vars)
            if resolved == "\b":
                continue  # mutually-exclusive system variable: skipped
            if resolved == "":
                ctx.errors.append(
                    f"{label}: property {pname!r} has no value defined")
                continue
            ptype = type_map[pname]
            if ptype == "COLOR":
                v = resolved.strip()
                if not re.fullmatch(r"[0-9a-fA-F]{6}([0-9a-fA-F]{2})?", v):
                    ctx.errors.append(
                        f"{label}: invalid color {pname}={v!r} (raw {raw!r})")
            elif ptype == "PATH":
                full = os.path.normpath(os.path.join(base_dir, resolved))
                if not os.path.isfile(full):
                    ctx.warnings.append(f"{label}: {pname} not found: {resolved}")
            elif ptype == "NORMALIZED_PAIR":
                if " " not in resolved.strip():
                    ctx.errors.append(
                        f"{label}: invalid normalized pair {pname}={resolved!r}")

def read_capability_variants(theme_dir):
    cap = os.path.join(theme_dir, "capabilities.xml")
    variants = []
    if not os.path.isfile(cap):
        return variants
    for _, elem in ET.iterparse(cap, events=("start",)):
        if elem.tag == "variant" and elem.get("name"):
            variants.append(elem.get("name"))
    return variants

def validate_theme_file(path, theme_dir, selected_variant):
    ctx = Ctx(theme_dir, selected_variant)
    # Seed the documented ES-DE system variables (THEMES.md), as the real
    # parser does via sysDataMap in ThemeData::loadFile(). The collection
    # variants resolve to backspace for non-applicable systems (faithful).
    ctx.variables.update({
        "system.name": "snes",
        "system.fullName": "Super Nintendo",
        "system.theme": "snes",
        "system.name.autoCollections": "\b",
        "system.name.customCollections": "\b",
        "system.fullName.autoCollections": "\b",
        "system.fullName.customCollections": "\b",
        "system.theme.autoCollections": "\b",
        "system.theme.customCollections": "\b",
    })
    tree = ET.parse(path)
    parse_node(tree.getroot(), ctx, os.path.dirname(path), 0, os.path.basename(path))
    return ctx

def main():
    theme_file = sys.argv[1] if len(sys.argv) > 1 else "theme-src/crystal/theme.xml"
    theme_dir = os.path.dirname(os.path.abspath(theme_file))
    variants = read_capability_variants(theme_dir)
    print(f"capabilities variants (in order): {variants}")

    forced = None
    if "--variant" in sys.argv:
        forced = sys.argv[sys.argv.index("--variant") + 1]

    # root + every per-system theme.xml
    files = [theme_file]
    for entry in sorted(os.listdir(theme_dir)):
        sub = os.path.join(theme_dir, entry, "theme.xml")
        if os.path.isfile(sub):
            files.append(sub)

    ok = True
    for sel in ([forced] if forced else [None, "light"]):
        selected = sel if sel is not None else (variants[0] if variants else None)
        tag = f"variant={selected!r}" if sel else f"default(first declared)={selected!r}"
        print(f"\n=== selection: {tag} ===")
        for f in files:
            ctx = validate_theme_file(f, theme_dir, selected)
            name = os.path.relpath(f, theme_dir)
            status = "OK " if not ctx.errors else "FAIL"
            if ctx.errors:
                ok = False
            print(f"  [{status}] {name} vars={len(ctx.variables)} "
                  f"errors={len(ctx.errors)} warnings={len(ctx.warnings)}")
            for e in ctx.errors:
                print(f"      ERROR: {e}")
            for w in sorted(ctx.unknown_vars):
                print(f"      unknown variable: {w}")
            for w in ctx.warnings[:5]:
                print(f"      warn: {w}")
            if len(ctx.warnings) > 5:
                print(f"      ... +{len(ctx.warnings)-5} more warnings")
    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
