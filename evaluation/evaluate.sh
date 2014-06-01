#!/bin/bash

# Trap ctrl+c and abort all if it is entered
trap 'echo interrupted; exit' INT

# Usage function, describing the parameters to the user.
usage() { echo "Usage: ./$0 -i sobazar_input.tab"; exit 1; }

# Save the current path
CMD=$( cd "$( dirname "$0" )" && pwd );
ROOT=`pwd`

# Some parameters changable in the opts.
TTT=""
MMLITEMRATINGSTYLE=""
RECOMMENDERSYS=""
RECOMMENDER=""
FEATUREFILE="$ROOT/generated/itemFeatures.txt"

while getopts "t:p:r:m" o; do
  case "${o}" in
    m)
      MMLITEMRATINGSTYLE="-m"
      ;;
    t)
      TTT=("${OPTARG}")
      ;;
    r)
      RECOMMENDERSYS="${OPTARG}"
      ;;
    p)
      RECOMMENDER="${OPTARG}"
      ;;
    *)
      usage
      ;;
  esac
done

# Get score for the predictions
echo "Evaluating $RECOMMENDER"
for ttt in $TTT
do
    set -- "$ttt"
    IFS=":"; declare -a Array=($*)

    TRAIN_FILE="$ROOT/generated/ratings/${Array[0]}";
    TEST_FILE="$ROOT/generated/ratings/${Array[1]}";
    PRED_FILE="$ROOT/generated/predictions/${Array[0]}-${Array[1]}-$RECOMMENDERSYS-$RECOMMENDER.predictions";
    F_FILE="$FEATUREFILE";

    OPT=(--training-file $TRAIN_FILE);
    OPT+=(--test-file $TEST_FILE);
    OPT+=(--prediction-file $PRED_FILE);

    python2.7 $CMD/evaluation.py -b 2 -k 20 "${OPT[@]}" $MMLITEMRATINGSTYLE >/dev/null &
done
wait $!
echo "Done evaluating $RECOMMENDER"
