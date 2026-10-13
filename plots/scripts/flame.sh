#!/bin/bash
# Draw one flame graph per plots/data/flame-*.txt as SVG and PDF in plots/figures.
#   plots/scripts/flame.sh      (inside the container)
# The data files are folded stacks made with plots/scripts/fold.sh.
cd "$(dirname "$0")/../.."
mkdir -p plots/figures

for data in plots/data/flame-*.txt; do
  name=$(basename $data .txt)
  name=${name/-/_}
  svg=plots/figures/$name.svg
  # 12 px text on 800 px prints at 7.6 pt on 7 in
  /opt/FlameGraph/flamegraph.pl --title ' ' --width 800 --height 16 --fontsize 12 \
    --bgcolors '#ffffff' --hash --minwidth 3 $data > $svg
  # Drop the title, details, buttons and match count (interactive leftovers)
  sed -i '/<text id="\(title\|details\|unzoom\|search\|ignorecase\|matched\)"/d' $svg
  rsvg-convert -f pdf -o ${svg%.svg}.pdf $svg
done
