#!/bin/bash

# Trap ctrl+c and abort all if it is entered
trap 'echo interrupted; exit' INT

# Usage function, describing the parameters to the user.
usage() { echo "Usage: $0 -i sobazar_input.tab"; exit 1; }

# Save the current path
ROOT=$( cd "$( dirname "$0" )" && pwd );

# Some parameters changable in the opts.
INFILE="-i ../datasets/v3/sobazar_events_prod_cleaned_formatted.tab"
CLEAN=""
MYMEDIAITEM=""
MYMEDIAIRANK=""
MAHOUT=""
SPLIT=0

# Available Item Recommenders:
# 'BPRMF' 'ItemAttributeKNN' 'ItemKNN' 'MostPopular' 'Random' 'UserAttributeKNN' 'UserKNN' 'WRMF' 'Zero' 'MultiCoreBPRMF' 'SoftMarginRankingMF' 'WeightedBPRMF' 'BPRLinear' 'MostPopularByAttributes' 'BPRSLIM' 'LeastSquareSLIM'
ITEMRECOMMENDERS="MostPopular WRMF BPRMF"

# Available Rank Recommenders:
# 'BiPolarSlopeOne' 'GlobalAverage' 'ItemAttributeKNN' 'ItemAverage' 'ItemKNN' 'MatrixFactorization' 'SlopeOne' 'UserAttributeKNN' 'UserAverage' 'UserItemBaseline' 'UserKNN' 'TimeAwareBaseline' 'TimeAwareBaselineWithFrequencies' 'CoClustering' 'Random' 'Constant' 'LatentFeatureLogLinearModel' 'BiasedMatrixFactorization' 'SVDPlusPlus' 'SigmoidSVDPlusPlus' 'SocialMF' 'SigmoidItemAsymmetricFactorModel' 'SigmoidUserAsymmetricFactorModel' 'SigmoidCombinedAsymmetricFactorModel' 'NaiveBayes' 'ExternalRatingPredictor' 'GSVDPlusPlus'
RANKRECOMMENDERS="MatrixFactorization NaiveBayes"

#Available Mahout recommenders
# 'svd' ...
MAHOUTRECOMMENDERS="svd"

while getopts "i:cp:sr:h:tm" o; do
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
      MAHOUT="-h"
      MAHOUTRECOMMENDERS="svd"
      ;;
    s)
      SPLIT=1
      ;;
    *)
      usage
      ;;
  esac
done

OPTS="$INFILE $CLEAN"
RECOMMENDERSYS="$MYMEDIAITEM $MYMEDIAIRANK $MAHOUT"

# Generate ratings
/bin/bash $ROOT/generators/test.sh -b -t $OPTS;

if [ $SPLIT -eq 1 ]; then
  # Cold start split
  echo "Splitting data into colstart splits"
  python2.7 $ROOT/evaluation/evaluation.py --coldstart-split $ROOT/generators/ratings/blend.txt --feature-file $ROOT/data/product_features.txt -t -fb '1,1,1,1,0';
fi
exit;
# Todo: can we avoid having such a long string which, to be honest, no one will change in near future anyways?
trainTestTuples="blend_itemtrain1.txt:blend_itemtest1.txt blend_itemtrain2.txt:blend_itemtest2.txt blend_itemtrain3.txt:blend_itemtest3.txt blend_systemtrain1.txt:blend_systemtest.txt blend_systemtrain2.txt:blend_systemtest.txt blend_systemtrain3.txt:blend_systemtest.txt blend_usertrain1.txt:blend_usertest1.txt blend_usertrain2.txt:blend_usertest2.txt blend_usertrain3.txt:blend_usertest3.txt"

if [[ $MYMEDIAITEM ]]; then
  for ir in $ITEMRECOMMENDERS
  do
    # make predictions
    echo "------------------------------"
    echo "Running $ROOT/generators/myMediaLitePredicter.sh -t '$trainTestTuples' $MYMEDIAITEM -p $ir";
    /bin/bash $ROOT/generators/myMediaLitePredicter.sh -t "$trainTestTuples" $MYMEDIAITEM -p $ir;

    echo "------------------------------"

    # evaluate predicted values
    echo "Running $ROOT/evaluation/evaluate.sh -t '$trainTestTuples' -r $MYMEDIAITEM -p $ir -m";
    /bin/bash $ROOT/evaluation/evaluate.sh -t "$trainTestTuples" -r $MYMEDIAITEM -p $ir -m;
  done
fi

if [[ $MYMEDIAIRANK ]]; then
  for ir in $RANKRECOMMENDERS
  do
    # make predictions
    /bin/bash $ROOT/generators/myMediaLitePredicter.sh -t "$trainTestTuples" $MYMEDIAIRANK -p $ir;

    # evaluate predicted values
    /bin/bash $ROOT/generators/evaluate.sh -t "$trainTestTuples" -r $MYMEDIAIRANK -p $ir;
  done
fi

if [[ $MAHOUT ]]; then
  for ir in $MAHOUTRECOMMENDERS
  do
    # make predictions
    /bin/bash $ROOT/generators/mahoutPredict.sh -t "$trainTestTuples" $MAHOUT -p $ir;

    # evaluate predicted values
    /bin/bash $ROOT/evaluation/evaluate.sh -t "$trainTestTuples" -r $MAHOUT -p $ir;
  done
fi

python $ROOT/evaluation/generateLatexLines.py

echo 'Done.'
