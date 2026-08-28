#!/bin/sh
# Export the three paper figures to PNG on macOS with no third-party tools.
# Quick Look (qlmanage) renders SVG to a square thumbnail and CLIPS a wide
# figure, so each SVG is first wrapped in a white square canvas of side
# max(width,height), rendered at 2400 px, then cropped back to the figure's
# aspect ratio with sips.  Run from the repository root:
#   sh docs/paper/figures/png/export_png.sh
set -eu
FIG=docs/paper/figures; OUT=$FIG/png; TMP=$(mktemp -d)
for pair in "1 fig1_boundary_attribution" "2 fig2_window_timeline" "3 fig3_decision_gates"; do
  n=${pair%% *}; f=${pair#* }
  python3 - "$FIG/$f.svg" "$TMP/fig$n.svg" <<'PY'
import re, sys, pathlib
src, dst = sys.argv[1], sys.argv[2]
s = pathlib.Path(src).read_text()
w, h = map(int, re.search(r'viewBox="0 0 (\d+) (\d+)"', s).groups())
side = max(w, h); inner = re.sub(r'<\?xml[^>]*\?>', '', s, count=1)
pathlib.Path(dst).write_text(
  f'<svg xmlns="http://www.w3.org/2000/svg" width="{side}" height="{side}" viewBox="0 0 {side} {side}">'
  f'<rect width="100%" height="100%" fill="white"/><svg x="{(side-w)//2}" y="{(side-h)//2}" width="{w}" height="{h}">{inner}</svg></svg>')
print(f"{w} {h}")
PY
done
qlmanage -t -s 2400 -o "$TMP" "$TMP"/fig1.svg "$TMP"/fig2.svg "$TMP"/fig3.svg >/dev/null 2>&1
for pair in "1 fig1_boundary_attribution" "2 fig2_window_timeline" "3 fig3_decision_gates"; do
  n=${pair%% *}; f=${pair#* }
  read w h <<EOT
$(python3 -c "import re,sys;print(*re.search(r'viewBox=\"0 0 (\d+) (\d+)\"',open('$FIG/$f.svg').read()).groups())")
EOT
  side=$(( w > h ? w : h )); scale=$(( 2400 / side ))
  cw=$(( w * 2400 / side )); ch=$(( h * 2400 / side ))
  ox=$(( (2400 - cw) / 2 )); oy=$(( (2400 - ch) / 2 ))
  cp "$TMP/fig$n.svg.png" "$OUT/fig$n.png"
  sips -c "$ch" "$cw" --cropOffset "$oy" "$ox" "$OUT/fig$n.png" >/dev/null
  echo "fig$n.png ${cw}x${ch}"
done
rm -rf "$TMP"
