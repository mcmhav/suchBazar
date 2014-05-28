#!/bin/bash

# make predictions
# With MyMediaLite - installed globally

trap 'echo interrupted; exit' INT

usage() { echo "Usage: ./$0 mtodo"; exit 1; }

# Some parameters changable in the opts.
TTT=""
MAHOUT=0
RECOMMENDER="svd"

CWD=$( cd "$( dirname "$0" )" && pwd );
ROOT=$( dirname "$CWD");

RATINGS="$ROOT/generated/splits"
PREDICTIONS="$ROOT/generated/predictions"

QUIET=0

while getopts "t:hp:l:" o; do
  case "${o}" in
    t)
      TTT=("${OPTARG}")
      ;;
    h)
      MAHOUT=1
      ;;
    p)
      RECOMMENDER="${OPTARG}"
      ;;
    l)
      RATINGS="${OPTARG}"
      ;;
    q)
      QUIET=1
      ;;
    *)
      usage
      ;;
  esac
done

OPTS=""
if [ $QUIET -eq 1 ]; then
  OPTS+=" >/dev/null 2>/dev/null"
fi

javac TopKRecommendations.java $OPTS;

echo "Making Mahout predictions with $RECOMMENDER";
for ttt in $TTT
do
    set -- "$ttt"
    IFS=":"; declare -a Array=($*)
    if [ $QUIET -eq 1 ]; then
      PREDFILE="$PREDICTIONS/"${Array[0]}"-"${Array[1]}"--h-"$RECOMMENDER".predictions"

      java TopKRecommendations $RATINGS $RECOMMENDER "${Array[0]}" $PREDFILE $OPTS &
      item_recommendation ${OPT[@]} $OPTS &
    else
      java TopKRecommendations $RATINGSLOCATION $RECOMMENDER "${Array[0]}" $PREDFILE $OPTS &
    fi
done
wait $!
echo "Done making Mahout items predictions with $RECOMMENDER";
