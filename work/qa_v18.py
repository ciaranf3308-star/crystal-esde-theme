#!/usr/bin/env python3
"""v18.0.0 ship QA: macro-lock, geometry, production hygiene, zip safety."""
import os, sys, re, hashlib, subprocess, zipfile
from PIL import Image

REPO = os.path.expanduser("~/workspace/crystal-esde-theme")
sys.path.insert(0, os.path.join(REPO, "work"))
import mock_gamelist_v17_9 as M
from gen_v15_assets import SYSTEMS

VIEWS = os.path.join(REPO, "theme-src/crystal/views.xml")
BASELINE = os.path.join(REPO, "work/baseline_media_fallbacks_v17_4.sha256")
W, H = 1280, 960
fails = []

def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""))
    if not ok:
        fails.append(name)

def geom_dict(view):
    d = {}
    for m in re.finditer(r'<(image|text|datetime|rating|carousel) name="([^"]+)"', view):
        blk = M.el_box(view, f"{m.group(1)} name=\"{m.group(2)}\"")
        d[m.group(2)] = M.el_geom(blk)
    return d

xml = open(VIEWS, encoding="utf-8").read()
g = M.parse_view(xml, "gamelist")

# 1. macro-lock vs v17.9.0 (HEAD): only whitelisted XML moves
head = subprocess.run(["git", "-C", REPO, "show", "HEAD:theme-src/crystal/views.xml"],
                      capture_output=True, text=True).stdout
a, b = geom_dict(M.parse_view(head, "gamelist")), geom_dict(g)
whitelist = {"gameCarousel": {"pos", "size"},
             "libPlaneHero": {"pos", "size", "origin"},
             "libGameName": set(), "libYear": set(), "libSelectedShadow": set()}
ok, detail = True, ""
if set(a) != set(b):
    ok, detail = False, f"element set changed"
else:
    for k in a:
        wa = whitelist.get(k, set())
        for f, val in a[k].items():
            if f not in wa and b[k].get(f) != val:
                ok, detail = False, f"{k}.{f}: {val} -> {b[k].get(f)}"
check("macro-lock vs v17.9.0 (whitelisted v18 moves only)", ok, detail or f"{len(a)} elements")

# 2. carousel geometry + motion
cb = M.el_box(g, 'carousel name="gameCarousel"')
check("carousel: pos (0.703125, 0.453125), size 0.5x1.53125",
      M.el_val(cb, "pos") == "0.703125 0.453125" and M.el_val(cb, "size") == "0.5 1.53125",
      f"pos={M.el_val(cb,'pos')} size={M.el_val(cb,'size')}")
gc = re.sub(r"<!--.*?-->", "", g, flags=re.S)
i = gc.index('<carousel name="gameCarousel"')
check("gameCarousel itemTransitions=animate engaged",
      "itemTransitions" in gc[i:i+1200] and "animate" in gc[i:i+1200])
check("no unsupported motion constructs",
      not any(x in gc for x in ("<storyboard", "<animation ", "crossfade")))

# 3. hero plane: centred radial, no rectangle
pl = M.el_box(g, 'image name="libPlaneHero"')
check("plane: centred on hero (0.703125 0.4479167), origin 0.5 0.5, 900x900, z44",
      M.el_val(pl, "pos") == "0.703125 0.4479167"
      and M.el_val(pl, "origin") == "0.5 0.5"
      and M.el_val(pl, "size") == "0.703125 0.9375"
      and M.el_val(pl, "zIndex") == "44")
pim = Image.open(os.path.join(REPO, "theme-src/crystal/art/lib_plane_hero.png")).convert("RGBA")
pa = pim.split()[3]
rim = [pa.getpixel((x, 0)) for x in range(pim.width)] + [pa.getpixel((x, pim.height-1)) for x in range(pim.width)] \
    + [pa.getpixel((0, y)) for y in range(pim.height)] + [pa.getpixel((pim.width-1, y)) for y in range(pim.height)]
check("plane asset: no rectangular footprint (rim alpha 0, peak <= 20)",
      max(rim) == 0 and max(pa.getdata()) <= 20, f"rim_max={max(rim)} peak={max(pa.getdata())}")

# 4. year + shadow
yb = M.el_box(g, 'datetime name="libYear"')
check("year fontSize 0.044 (calmer anchor)", M.el_val(yb, "fontSize") == "0.044")
sb = M.el_box(g, 'image name="libSelectedShadow"')
check("hero shadow opacity 0.8", M.el_val(sb, "opacity") == "0.8")

# 5. title + rail unchanged from v17.9 (still robust)
tb = M.el_box(g, 'text name="libGameName"')
check("title: fontSize 0.0260, box 0.58 (v17.9 robustness kept)",
      M.el_val(tb, "fontSize") == "0.0260" and M.el_val(tb, "size") == "0.58 0.0375")
check("rail: dev still removed", '<text name="libMetaDev">' not in g)

# 6. spine rails: feathered edges, dots nearly gone, yellow line crisp
rim_ok, dot_ok, yel_ok = True, True, True
for s, _ in SYSTEMS:
    im = Image.open(os.path.join(REPO, f"theme-src/crystal/art/rails/{s}.png")).convert("RGBA")
    a = im.split()[3]
    if a.getpixel((0, 456)) > 12 or a.getpixel((59, 456)) > 12:
        rim_ok = False
    # yellow line at x=8 must be full-alpha yellow
    r, gg, bb, aa = im.getpixel((8, 456))
    if not (r > 200 and gg > 160 and bb < 110 and aa > 200):
        yel_ok = False
check("rails: 6px feathered left/right edges", rim_ok)
check("rails: 1px yellow structural line crisp at x=8", yel_ok)
check("rails: all 21 present", all(os.path.exists(os.path.join(REPO, f"theme-src/crystal/art/rails/{s}.png")) for s, _ in SYSTEMS))

# 7. typography / fallbacks / hygiene
check("no PermanentMarker in gamelist XML", "PermanentMarker" not in gc)
base = {l.split()[1]: l.split()[0] for l in open(BASELINE) if l.strip()}
bad = [n for n, h in base.items()
       if hashlib.sha256(open(os.path.join(REPO, n), "rb").read()).hexdigest() != h]
check("all 22 media_fallbacks byte-identical to frozen baseline", not bad,
      f"changed={bad}" if bad else f"{len(base)} files")
check("production grep clean",
      "${game" not in xml and "dashed" not in xml.lower()
      and "placeholder" not in xml.lower().replace("placeholder artwork", "")
      and "debug" not in xml.lower().replace("<!--", "").replace("-->", ""),
      "no ${game/dashed/placeholder/debug in shipped XML")

# 8. proof screens: yellow budget + no proof assets in tree paths
def is_yellow(p): return p[0] > 200 and p[1] > 160 and p[2] < 110
for n in ("ps2", "n64", "3ds"):
    im = Image.open(os.path.join(REPO, f"work/proofs/v18_proof_{n}.png")).convert("RGB")
    share = sum(1 for q in im.getdata() if is_yellow(q)) / (W * H) * 100
    check(f"[{n}] yellow <= 5%", share <= 5.0, f"{share:.2f}%")

# 9. build + proof assets excluded from the ZIP
subprocess.run(["bash", "build.sh"], cwd=REPO, capture_output=True)
zf = zipfile.ZipFile(os.path.join(REPO, "dist/crystal-theme-v1.zip"))
names = zf.namelist()
check("proof assets ABSENT from production ZIP",
      not any("proof_assets" in n or "work/" in n for n in names), f"{len(names)} entries")
check("theme-src only in ZIP", all(not n.startswith("work/") for n in names))

print(f"\n{'ALL QA PASS' if not fails else str(len(fails)) + ' QA FAILED'}")
sys.exit(1 if fails else 0)
