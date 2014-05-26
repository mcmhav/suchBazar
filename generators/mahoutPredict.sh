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
    java TopKRecommendations $RATINGSLOCATION $RECOMMENDER "${Array[0]}" $PREDICTIONSLOCATION/"${Array[0]}"-"${Array[1]}"--h-"$RECOMMENDER".predictions >/dev/null 2>/dev/null &
    # item_recommendation --training-file="${Array[0]}" --test-file="${Array[1]}" --recommender="$RECOMMENDER" --prediction-file=../predictions/"${Array[0]}"-"${Array[1]}"--i-"$RECOMMENDER".predictions >/dev/null 2>/dev/null &
done
wait $!
echo "Done making Mahout items predictions with $RECOMMENDER";
