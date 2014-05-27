#!/bin/bash

# make predictions
# With MyMediaLite - installed globally

trap 'echo interrupted; exit' INT

usage() { echo "Usage: ./$0 mtodo"; exit 1; }

# Some parameters changable in the opts.
TTT=""
MAHOUT=0
RECOMMENDER="svd"
RATINGSLOCATION="../generators/splits"
PREDICTIONSLOCATION="../generators/predictions"
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
      RATINGSLOCATION="${OPTARG}"
      ;;
    q)
      QUIET=1
      ;;
    *)
      usage
      ;;
  esac
done

cd ../mahout;
rm -f *.class;
javac TopKRecommendations.java >/dev/null 2>/dev/null;

echo "Making Mahout predictions with $RECOMMENDER";
for ttt in $TTT
do
    set -- "$ttt"
    IFS=":"; declare -a Array=($*)
    if [ $QUIET -eq 1 ]; then
      java TopKRecommendations $RATINGSLOCATION $RECOMMENDER "${Array[0]}" $PREDICTIONSLOCATION/"${Array[0]}"-"${Array[1]}"--h-"$RECOMMENDER".predictions >/dev/null 2>/dev/null &
      item_recommendation ${OPT[@]} >/dev/null 2>/dev/null &
    else
      java TopKRecommendations $RATINGSLOCATION $RECOMMENDER "${Array[0]}" $PREDICTIONSLOCATION/"${Array[0]}"-"${Array[1]}"--h-"$RECOMMENDER".predictions &
    fi
done
wait $!
echo "Done making Mahout items predictions with $RECOMMENDER";
