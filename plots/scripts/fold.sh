#!/bin/bash
# Fold the output of perf script into the call stacks that flame.sh draws.
#   perf script | ./dockerrun.sh plots/scripts/fold.sh > plots/data/flame-cancer.txt
# Run on the host after perf record -g ./genetic_benchmark cancer; perf is not in the container.

# Name every frame at a kernel address [kernel] and every frame of libm [libm]
sed -E -e 's/^(\s*ffffffff[0-9a-f]+) .*/\1 [kernel] ([kernel])/' \
       -e 's/^(\s*[0-9a-f]+) .*libm\.so\.6\)$/\1 [libm] ([libm])/' |
  /opt/FlameGraph/stackcollapse-perf.pl |
  perl -ne '
    # Keep the frames from main down, skip stacks outside main
    s/^.*?;(main[; ])/$1/ or next;
    # Shorten [libc.so.6] to [libc] and sinf@plt to sinf
    s/\.so\.6|\@plt//g;
    # Drop template arguments, innermost first
    1 while s/<[^<>]*>//;
    # Drop return types, keeping operator new and the sample count
    s/;(?!operator)[^; ]+ (?=\D)/;/g;
    # Drop the genetic:: and __cxx11:: namespaces and the [abi:cxx11] tag
    s/genetic::|__cxx11::|\[abi:cxx11\]//g;
    print;
  ' |
  # Merge adjacent equal frames and sum equal stacks
  /opt/FlameGraph/stackcollapse-recursive.pl
