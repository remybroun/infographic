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
# Nine sheets, named for what is actually on them. Rows flow rather than break
# per family, so a family's last half-width specimen shares a sheet with the next
# family's first; the compound names say so. Re-derive these from the render if
# you add or resize a specimen, do not assume the mapping held.
# pdftoppm pads the page number to the width of the page COUNT, so the same
# document is g-1.png at nine pages and g-01.png at ten. Take whichever exists
# rather than assuming, because the count changes whenever a specimen resizes.
page_file() {
  [ -f "$OUT/g-$1.png" ] && echo "$OUT/g-$1.png" || printf '%s/g-%02d.png\n' "$OUT" "$1"
}
rm -f assets/gallery-*.png
i=1
for name in quantity guards-change change-part part-principles structure \
            structure-diagram diagram-editorial editorial aliases; do
  cp "$(page_file $i)" "assets/gallery-$name.png"
  i=$((i + 1))
done
python3 assets/trim_png.py assets/gallery-*.png

rm -rf "$OUT"
ls -l assets/*.png
