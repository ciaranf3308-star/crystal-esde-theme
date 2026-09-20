#!/usr/bin/env bash
# Deterministic build of crystal-theme-v1.zip for the Crystal ES-DE theme.
# Produces byte-identical output on every run:
#   - zip entries sorted by name
#   - fixed modification timestamps (SOURCE_DATE_EPOCH, default 2026-09-20)
#   - fixed unix permissions (0644)
#   - fixed compression (deflate level 9)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$REPO_DIR/theme-src"
OUT_DIR="$REPO_DIR/dist"
STAMP="${SOURCE_DATE_EPOCH:-1758326400}"   # 2026-09-20 00:00:00 UTC
ZIP_NAME="crystal-theme-v1.zip"

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR/$ZIP_NAME"

python3 - "$SRC_DIR" "$OUT_DIR/$ZIP_NAME" "$STAMP" <<'PYEOF'
import os, sys, time, zipfile

src, out, stamp = sys.argv[1], sys.argv[2], int(sys.argv[3])
dt = time.gmtime(stamp)[0:6]

entries = []
for root, dirs, files in os.walk(src):
    dirs.sort()
    for name in sorted(files):
        full = os.path.join(root, name)
        arc = os.path.relpath(full, src)
        entries.append((arc, full))

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for arc, full in entries:
        zi = zipfile.ZipInfo(arc, date_time=dt)
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.create_system = 3  # unix
        zi.external_attr = (0o644 << 16)
        with open(full, "rb") as fh:
            zf.writestr(zi, fh.read())

print(f"wrote {out} ({len(entries)} entries)")
PYEOF

sha256sum "$OUT_DIR/$ZIP_NAME"
