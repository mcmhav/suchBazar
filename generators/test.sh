#!/bin/bash

usage() { echo "Usage: $0 [-c (clean)] [-p (plot)] [-b (blend)] [-i (infile)] [-h (help)]"; exit 1; }

# Check for ctrl+c
trap 'echo interrupted; exit' INT

# Save the current path
CWD=$( cd "$( dirname "$0" )" && pwd );

CLEAN=0
PLOT=0
BLEND=0
FORCE=""
TIMESTAMP=""
MIN_DATE=""
MAX_DATE=""
INFILE="-i ../../datasets/v3/sobazar_events_prod_cleaned_formatted.tab"

# Check options (basically if we want to clean and/or plot)
while getopts "i:m:x:cpbtf" o; do
  case "${o}" in
    c)
      CLEAN=1
      ;;
    p)
      PLOT=1
      ;;
    b)
      BLEND=1
      ;;
    f)
      FORCE="-f"
      ;;
    t)
      TIMESTAMP="-t"
      ;;
    i)
      INFILE="-i ${OPTARG}"
      ;;
    m)
      MIN_DATE="--min-date=${OPTARG}"
      ;;
    x)
      MAX_DATE="--max-date=${OPTARG}"
      ;;
    *)
      usage
      ;;
  esac
done
OPTS="$INFILE $TIMESTAMP $MIN_DATE $MAX_DATE $FORCE"

# If cleaning, then we delete everything in ratings/ and dists/
if [ $CLEAN -eq 1 ]; then
  if [ -d $CWD/ratings ]; then
    rm -f $CWD/ratings/*.txt
  fi

  if [ -d $CWD/dists ]; then
    rm -f $CWD/dists/*.png
  fi
fi

##
# Our various methods to test
##
SCRIPT="$CWD/ratings.py"

#python $SCRIPT $OPTS -m naive

#python $SCRIPT $OPTS -m recentness -fx sigmoid_constant -sc 30
#python $SCRIPT $OPTS -m recentness -fx linear

#python $SCRIPT $OPTS -m count -fx linear
#python $SCRIPT $OPTS -m count -fx sigmoid_fixed -sr 4.5
#python $SCRIPT $OPTS -m count -fx sigmoid_constant -sc 30

## A nice, example blend
python $SCRIPT $OPTS -m count -fx linear
python $SCRIPT $OPTS -m count -fx sigmoid_fixed -sr 3.5
python $SCRIPT $OPTS -m count -fx sigmoid_fixed -sr 4.5
python $SCRIPT $OPTS -m recentness -fx sigmoid_constant -sc 15
python $SCRIPT $OPTS -m recentness -fx sigmoid_fixed -sr 1.5

# If blend we do that as well.
if [ $BLEND -eq 1 ]; then
  ls "$CWD/ratings" > "$CWD/files.conf"
  python $CWD/blend.py -c "$CWD/files.conf"
fi

# If plot then we run the plotting tool
if [ $PLOT -eq 1 ]; then
  python $CWD/plot_distribution.py
fi

