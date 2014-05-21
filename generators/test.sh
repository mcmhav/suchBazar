#!/bin/bash

usage() { echo "Usage: $0 [-c (clean)] [-p (plot)] [-b (blend)] [-i (infile)] [-h (help)]"; exit 1; }

# Check for ctrl+c
trap 'echo interrupted; exit' INT

CLEAN=0
PLOT=0
BLEND=0
TIMESTAMP=""
MIN_DATE=""
MAX_DATE=""
INFILE="-i ../../datasets/v3/sobazar_events_prod_cleaned.tab"

# Check options (basically if we want to clean and/or plot)
while getopts "imx:cpbt" o; do
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
OPTS="$INFILE $TIMESTAMP $MIN_DATE $MAX_DATE"

# If cleaning, then we delete everything in ratings/ and dists/
if [ $CLEAN -eq 1 ]; then
  if [ -d ratings ]; then
    rm -f ratings/*.txt
  fi

  if [ -d dists ]; then
    rm -f dists/*.png
  fi
fi

##
# Our various methods to test
##
python ratings.py $OPTS -m naive

python ratings.py $OPTS -m recentness -fx sigmoid_fixed -sr 4.5
python ratings.py $OPTS -m recentness -fx sigmoid_constant -sc 30
python ratings.py $OPTS -m recentness -fx linear

python ratings.py $OPTS -m count -fx linear
python ratings.py $OPTS -m count -fx sigmoid_fixed -sr 4.5
python ratings.py $OPTS -m count -fx sigmoid_constant -sc 30

# If blend we do that as well.
if [ $BLEND -eq 1 ]; then
  ls ratings > files.conf
  python blend.py -c files.conf
fi

# If plot then we run the plotting tool
if [ $PLOT -eq 1 ]; then
  python plot_distribution.py
fi

