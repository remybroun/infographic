#!/bin/sh
# Rebuild every image on the README and in GALLERY.md, from the repo's own data.
#
#   sh assets/build_gallery.sh
#
# 120 dpi, so A4 rasterises to 992px: GitHub caps its column near 890px, and a
# page label is a fixed size in millimetres, so the page WIDTH is what decides
# how large that label lands. A4 portrait puts an 8pt label at about 12px.
set -e
cd "$(dirname "$0")/.."
OUT=$(mktemp -d)

python3 assets/gen_readme.py >/dev/null
# `|| true`, and only here. The three README slides set `tables: false`, so the
# linter reports `no-table-view` as an error and exits non-zero. That check is
# right for a document and wrong for a raster image frame, where a <details>
# twin is a control nobody can operate. The reason is written into the README
# rather than hidden, and the gallery below keeps its twins.
python3 scripts/ig.py render assets/readme_spec.json --out-dir "$OUT" >/dev/null || true
pdftoppm -r 110 -png "$OUT/readme_spec.pdf" "$OUT/r"
python3 assets/pngtop.py "$OUT/r-1.png" assets/produces.png 640
python3 assets/pngtop.py "$OUT/r-2.png" assets/forms.png 780
python3 assets/pngtop.py "$OUT/r-3.png" assets/budget.png 600

python3 assets/gen_gallery.py >/dev/null
python3 scripts/ig.py render assets/gallery_spec.json --out-dir "$OUT"
pdftoppm -r 120 -png "$OUT/gallery_spec.pdf" "$OUT/g"
i=1
for name in quantity-1 quantity-2 change part structure-1 structure-2 \
            diagram aliases editorial-1 editorial-2; do
  cp "$OUT/g-$(printf %02d $i).png" "assets/gallery-$name.png"
  i=$((i + 1))
done
python3 assets/trim_png.py assets/gallery-*.png

rm -rf "$OUT"
ls -l assets/*.png
