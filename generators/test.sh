#!/bin/bash

usage() { echo "Usage: $0 [-c (clean)] [-p (plot)] [-b (blend)] [-h (help)]"; exit 1; }

# Check for ctrl+c
trap 'echo interrupted; exit' INT

CLEAN=0
PLOT=0
BLEND=0

# Check options (basically if we want to clean and/or plot)
while getopts ":cpb" o; do
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
    *)
      usage
      ;;
  esac
done

# If cleaning, then we delete everything in ratings/ and dists/
if [ $CLEAN -eq 1 ]; then
  if [ -d ratings ]; then
    rm -f ratings/*.txt
  fi

  if [ -d dists ]; then
    rm -f dists/*.png
  fi
fi

# Test input file with some common schemes.
INFILE=../../datasets/v2/sobazar.tab.prod

##
# Our various methods to test
##
python ratings.py -i $INFILE -m naive

python ratings.py -i $INFILE -m recentness -fx sigmoid_fixed -sr 4.5
python ratings.py -i $INFILE -m recentness -fx sigmoid_constant -sc 30
python ratings.py -i $INFILE -m recentness -fx linear

python ratings.py -i $INFILE -m count -fx linear
python ratings.py -i $INFILE -m count -fx sigmoid_fixed -sr 4.5
python ratings.py -i $INFILE -m count -fx sigmoid_constant -sc 30

# If blend we do that as well.
if [ $BLEND -eq 1 ]; then
  ls ratings > files.conf
  python blend.py -c files.conf
fi

# If plot then we run the plotting tool
if [ $PLOT -eq 1 ]; then
  python plot_distribution.py
fi

