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

RECOMMENDER_LOCATION="$ROOT/mahout"

QUIET=0
DIR=""
CLEAN=0

while getopts "cdt:hp:l:q" o; do
  case "${o}" in
    c)
      CLEAN=1
      ;;
    d)
      DIR="${OPTARG}"
      ;;
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
cd $RECOMMENDER_LOCATION;

rm *.class

if [ $QUIET -eq 1 ]; then
  javac TopKRecommendations.java >/dev/null 2>/dev/null;
else
  javac TopKRecommendations.java;
fi

echo "Making Mahout predictions with $RECOMMENDER";
for ttt in $TTT
do
    set -- "$ttt"
    IFS=":"; declare -a Array=($*)
    PREDFILE="$PREDICTIONS/${Array[0]}-${Array[1]}--h-$RECOMMENDER.predictions"
    if [ ! -f "$PREDFILE" ] || [ $CLEAN -eq 1 ]; then
      if [ $QUIET -eq 1 ]; then
        cat "$RATINGS/${Array[1]}" >> "$RATINGS/${Array[0]}"
        java TopKRecommendations $RATINGS "${Array[0]}" $RECOMMENDER  $PREDFILE >/dev/null 2>/dev/null &
      else
        java TopKRecommendations $RATINGS "${Array[0]}" $RECOMMENDER  $PREDFILE &
      fi
    fi
done
wait;
echo "Done making Mahout items predictions with $RECOMMENDER";
