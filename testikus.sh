#!/bin/bash

# Trap ctrl+c and abort all if it is entered
trap 'echo interrupted; exit' INT

# Usage function, describing the parameters to the user.
usage() { echo "Usage: ./$0 -i sobazar_input.tab"; exit 1; }

# Some parameters changable in the opts.
INFILE="-i ../datasets/v3/sobazar_events_prod_cleaned_formatted.tab"
CLEAN=""
MYMEDIAITEM=""
MYMEDIAIRANK=""
MAHOUT=""

# declare -a RAItem=('BPRMF' 'ItemAttributeKNN' 'ItemKNN' 'MostPopular' 'Random' 'UserAttributeKNN' 'UserKNN' 'WRMF' 'Zero' 'MultiCoreBPRMF' 'SoftMarginRankingMF' 'WeightedBPRMF' 'BPRLinear' 'MostPopularByAttributes' 'BPRSLIM' 'LeastSquareSLIM')
ITEMRECOMMENDERS="MostPopular WRMF BPRMF"

# declare -a RARatingPrediction=('BiPolarSlopeOne' 'GlobalAverage' 'ItemAttributeKNN' 'ItemAverage' 'ItemKNN' 'MatrixFactorization' 'SlopeOne' 'UserAttributeKNN' 'UserAverage' 'UserItemBaseline' 'UserKNN' 'TimeAwareBaseline' 'TimeAwareBaselineWithFrequencies' 'CoClustering' 'Random' 'Constant' 'LatentFeatureLogLinearModel' 'BiasedMatrixFactorization' 'SVDPlusPlus' 'SigmoidSVDPlusPlus' 'SocialMF' 'SigmoidItemAsymmetricFactorModel' 'SigmoidUserAsymmetricFactorModel' 'SigmoidCombinedAsymmetricFactorModel' 'NaiveBayes' 'ExternalRatingPredictor' 'GSVDPlusPlus')
RANKRECOMMENDERS="MatrixFactorization NaiveBayes"
MAHOUTRECOMMENDERS="svd"

while getopts "i:cp:r:h:tm" o; do
  case "${o}" in
    i)
      INFILE="-i ${OPTARG}"
      ;;
    c)
      CLEAN="-c"
      ;;
    p)
      MYMEDIAITEM="-i"
      ITEMRECOMMENDERS="${OPTARG}"
      ;;
    r)
      MYMEDIAIRANK="-r"
      RANKRECOMMENDERS="${OPTARG}"
      ;;
    h)
      MAHOUT="-h"
      MAHOUTRECOMMENDERS="${OPTARG}"
      ;;
    t)
      MYMEDIAITEM="-i"
      ITEMRECOMMENDERS="BPRMF ItemKNN MostPopular Random UserKNN WRMF"
      # ITEMRECOMMENDERS="BPRMF ItemAttributeKNN ItemKNN MostPopular Random UserAttributeKNN UserKNN WRMF Zero MultiCoreBPRMF SoftMarginRankingMF WeightedBPRMF BPRLinear MostPopularByAttributes BPRSLIM LeastSquareSLIM"
      # MYMEDIAIRANK="-r"
      # RANKRECOMMENDERS="GlobalAverage ItemAverage ItemKNN MatrixFactorization SlopeOne UserAverage UserKNN TimeAwareBaseline Random NaiveBayes"
      # RANKRECOMMENDERS="BiPolarSlopeOne GlobalAverage ItemAttributeKNN ItemAverage ItemKNN MatrixFactorization SlopeOne UserAttributeKNN UserAverage UserItemBaseline UserKNN TimeAwareBaseline TimeAwareBaselineWithFrequencies CoClustering Random Constant LatentFeatureLogLinearModel BiasedMatrixFactorization SVDPlusPlus SigmoidSVDPlusPlus SocialMF SigmoidItemAsymmetricFactorModel SigmoidUserAsymmetricFactorModel SigmoidCombinedAsymmetricFactorModel NaiveBayes ExternalRatingPredictor GSVDPlusPlus"
      MAHOUT="-h"
      MAHOUTRECOMMENDERS="svd"
      ;;
    *)
      usage
      ;;
  esac
done

OPTS="$INFILE $CLEAN"
RECOMMENDERSYS="$MYMEDIAITEM $MYMEDIAIRANK $MAHOUT"

# Generate ratings
cd generators;
./test.sh -b -t $OPTS >/dev/null;

# Split ratings
# ./split.sh -i ratings/blend.txt;
# Cold start split
cd ../evaluation;
if [[ $CLEAN ]]; then
  echo "Splitting data into colstart splits"
  python2.7 evaluation.py --coldstart-split ../generators/ratings/blend.txt -t -fb '1,1,1,1,0' >/dev/null;
fi

cd ../generators;
# declare -a trainTestTuples=('blend_itemtrain1.txt:blend_itemtest1.txt' 'blend_itemtrain2.txt:blend_itemtest2.txt' 'blend_itemtrain3.txt:blend_itemtest3.txt' 'blend_systemtrain1.txt:blend_systemtest.txt' 'blend_systemtrain2.txt:blend_systemtest.txt' 'blend_systemtrain3.txt:blend_systemtest.txt' 'blend_usertrain1.txt:blend_usertest1.txt' 'blend_usertrain2.txt:blend_usertest2.txt' 'blend_usertrain3.txt:blend_usertest3.txt')

trainTestTuples="blend_itemtrain1.txt:blend_itemtest1.txt blend_itemtrain2.txt:blend_itemtest2.txt blend_itemtrain3.txt:blend_itemtest3.txt blend_systemtrain1.txt:blend_systemtest.txt blend_systemtrain2.txt:blend_systemtest.txt blend_systemtrain3.txt:blend_systemtest.txt blend_usertrain1.txt:blend_usertest1.txt blend_usertrain2.txt:blend_usertest2.txt blend_usertrain3.txt:blend_usertest3.txt"

if [[ $MYMEDIAITEM ]]; then
  for ir in $ITEMRECOMMENDERS
  do
    # make predictions
    cd ../generators;
    ./myMediaLitePredicter.sh -t "$trainTestTuples" $MYMEDIAITEM -p $ir;
    # evaluate predicted values
    cd ../evaluation;
    ./evaluate.sh -t "$trainTestTuples" -r $MYMEDIAITEM -p $ir -m;
  done
fi

if [[ $MYMEDIAIRANK ]]; then
  for ir in $RANKRECOMMENDERS
  do
    # make predictions
    cd ../generators;
    ./myMediaLitePredicter.sh -t "$trainTestTuples" $MYMEDIAIRANK -p $ir;
    # evaluate predicted values
    cd ../evaluation;
    ./evaluate.sh -t "$trainTestTuples" -r $MYMEDIAIRANK -p $ir;
  done
fi

if [[ $MAHOUT ]]; then
  for ir in $MAHOUTRECOMMENDERS
  do
    # make predictions
    cd ../generators;
    ./mahoutPredict.sh -t "$trainTestTuples" $MAHOUT -p $ir;
    # evaluate predicted values
    cd ../evaluation;
    ./evaluate.sh -t "$trainTestTuples" -r $MAHOUT -p $ir;
  done
fi
# declare -a RA=('BPRMF' 'ItemAttributeKNN' 'ItemKNN' 'MostPopular' 'Random' 'UserAttributeKNN' 'UserKNN' 'WRMF' 'Zero' 'MultiCoreBPRMF' 'SoftMarginRankingMF' 'WeightedBPRMF' 'BPRLinear' 'MostPopularByAttributes' 'BPRSLIM' 'LeastSquareSLIM')



python generateLatexLines.py

echo 'lol, done'
# Evaluate the top K recommendations
# javac SobazarRecommender.java && java SobazarRecommender;
