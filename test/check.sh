#!/bin/bash
# After test/run.sh: check that every commit printed the same program as the one before it.
# The ;;Time line is ignored; a difference shows the changed ;; lines.
cd "$(dirname "$0")/results"
names=$(grep -v '^#' ../commits.txt | cut -d' ' -f1)

prev=
for name in $names; do
  for bench in diabetes cancer housing silk-wave square-wave; do
    if [ -n "$prev" ]; then
      if [ ! -f $prev-$bench.rkt ] || [ ! -f $name-$bench.rkt ]; then
        echo "$name $bench: no results"
      elif diff -q <(grep -v '^;;Time' $prev-$bench.rkt) <(grep -v '^;;Time' $name-$bench.rkt) > /dev/null; then
        echo "$name $bench: same as $prev"
      else
        echo "$name $bench: DIFFERENT from $prev"
        diff <(grep '^;;' $prev-$bench.rkt | grep -v '^;;Time') <(grep '^;;' $name-$bench.rkt | grep -v '^;;Time')
      fi
    fi
  done
  prev=$name
done
