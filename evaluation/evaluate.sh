#!/bin/bash

# Stop on error
set -e

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
PREDFOLDER="$ROOT/generated/predictions"
KVAL=""

while getopts "t:p:r:mk:" o; do
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
    k)
      KVAL="${OPTARG}"
      ;;
    *)
      usage
      ;;
  esac
done

# Ensure predictions folder exists
if [ ! -d "$PREDFOLDER" ]; then
  mkdir -p "$PREDFOLDER";
fi

# Get score for the predictions
echo "Evaluating $RECOMMENDER"
for ttt in $TTT
do
    set -- "$ttt"
    IFS=":"; declare -a Array=($*)

    TRAIN_FILE="$ROOT/generated/splits/${Array[0]}";
    TEST_FILE="$ROOT/generated/splits/${Array[1]}";
    PRED_FILE="$PREDFOLDER/${Array[0]}-${Array[1]}-$KVAL-$RECOMMENDERSYS-$RECOMMENDER.predictions";
    F_FILE="$FEATUREFILE";

    echo "Evaluating $PRED_FILE";

    OPT=(--training-file $TRAIN_FILE);
    OPT+=(--test-file $TEST_FILE);
    OPT+=(--prediction-file $PRED_FILE);
    python2.7 $CMD/evaluation.py -b 2 -k 20 "${OPT[@]}" $MMLITEMRATINGSTYLE &
done
wait;
echo "Done evaluating $RECOMMENDER";
