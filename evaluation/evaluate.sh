#!/bin/bash

# Trap ctrl+c and abort all if it is entered
trap 'echo interrupted; exit' INT

# Usage function, describing the parameters to the user.
usage() { echo "Usage: ./$0 -i sobazar_input.tab"; exit 1; }

# Some parameters changable in the opts.
TTT=""
MMLITEMRATINGSTYLE=""
RECOMMENDERSYS=""
RECOMMENDER=""

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
    python2.7 evaluation.py -b 2 -k 20 --training-file ../generators/splits/"${Array[0]}" --test-file ../generators/splits/"${Array[1]}" --prediction-file ../generators/predictions/"${Array[0]}"-"${Array[1]}"-"$RECOMMENDERSYS"-"$RECOMMENDER".predictions $MMLITEMRATINGSTYLE >/dev/null &
done
wait $!
echo "Done evaluating $RECOMMENDER"
