#!/bin/bash
#
# A shell script utilizing various script created under our Master Thesis 2014.
# Input is a event log with implicit data.
# Output is the implicit ratings, based on various schemes (defined below).
#
# If flags are provided the script also removes old files, blends the ratings
# and plots its distributions.
####

# Exit on error
set -e

usage() { echo "Usage: $0 [-c (clean)] [-p (plot)] [-b (blend)] [-i (infile)] [-h (help)]"; exit 1; }

# Check for ctrl+c
trap 'echo interrupted; exit' INT

# Save the current path
CWD=$( cd "$( dirname "$0" )" && pwd );
ROOT=$( dirname "$CWD");
GENERATED="$ROOT/generated"

CLEAN=0
PLOT=0
BLEND=0
FORCE=""
TIMESTAMP=""
MIN_DATE=""
MAX_DATE=""
INFILE="-i ../../datasets/v3/sobazar_events_prod_cleaned_formatted.tab"

RATINGS="$GENERATED/ratings"
RATING_DISTS="$GENERATED/rating_distributions"

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
OPTS="$INFILE $TIMESTAMP $MIN_DATE $MAX_DATE $FORCE -d $RATINGS"

# If cleaning, then we delete everything in ratings/ and dists/
if [ $CLEAN -eq 1 ]; then
  if [ -d $RATINGS ]; then
    rm -f $RATINGS/*.txt
  fi

  if [ -d $RATING_DISTS ]; then
    rm -f $RATING_DISTS/*.png
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
python $SCRIPT $OPTS -m count -fx linear &
python $SCRIPT $OPTS -m count -fx sigmoid_fixed -sr 3.5 &
python $SCRIPT $OPTS -m count -fx sigmoid_fixed -sr 4.5 &
python $SCRIPT $OPTS -m recentness -fx sigmoid_constant -sc 15 &
python $SCRIPT $OPTS -m recentness -fx sigmoid_fixed -sr 1.5 &

# Wait till the last backgorund process has completed.
wait

# If blend we do that as well.
if [ $BLEND -eq 1 ]; then
  # Delete old blend file, if exists.
  rm -f $RATINGS/blend.txt

  # Create config-file for blending.
  ls "$RATINGS" > "$GENERATED/files.conf"

  # Do the blend.
  python $CWD/blend.py -c "$GENERATED/files.conf" -d "$RATINGS" -o "blend.txt"
fi

# If plot then we run the plotting tool
if [ $PLOT -eq 1 ]; then
  python $CWD/plot_distribution.py -i "$RATINGS" -d "$RATING_DISTS"
fi
