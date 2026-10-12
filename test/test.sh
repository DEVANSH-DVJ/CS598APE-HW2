#!/bin/bash
# Run one benchmark on one built commit REPS times and print the times in seconds.
#   test/test.sh base diabetes
# Benchmarks: diabetes, cancer, housing, silk-wave, square-wave.
# The program is saved as test/results/<name>-<benchmark>.rkt.
# Every time is also added to test/results/times.csv.
# Environment: REPS (default 3), THREADS (default 1)
cd "$(dirname "$0")/.."
name=$1
bench=$2
mkdir -p test/results
out=$PWD/test/results/$name-$bench.rkt
csv=$PWD/test/results/times.csv
[ -f $csv ] || echo "commit,benchmark,threads,seconds" > $csv

cd test/build/$name
echo -n "$name $bench:"
for r in $(seq ${REPS:-3}); do
  OMP_NUM_THREADS=${THREADS:-1} ./genetic_benchmark $bench > $out 2> run.log
  if [ $? -ne 0 ]; then rm -f $out; echo " failed"; exit 1; fi
  t=$(grep -o '^;;Time.* = [0-9.]*' $out | awk '{print $NF}')
  echo -n " $t"
  echo "$name,$bench,${THREADS:-1},$t" >> $csv
done
echo
