#!/bin/bash

# Exit on error
set -e

# Trap ctrl+c and abort all if it is entered
trap 'echo interrupted; exit' INT

# Usage function, describing the parameters to the user.
usage() { echo "Usage: $0 -i sobazar_input.tab"; exit 1; }

# Save the current path
ROOT=$( cd "$( dirname "$0" )" && pwd );

# Some parameters changable in the opts.
INFILE="../datasets/v3/sobazar_events_prod_cleaned_formatted.tab"
CLEAN=""
SPLIT=0

# Available Item Recommenders:
# 'BPRMF' 'ItemAttributeKNN' 'ItemKNN' 'MostPopular' 'Random' 'UserAttributeKNN' 'UserKNN' 'WRMF' 'Zero' 'MultiCoreBPRMF' 'SoftMarginRankingMF' 'WeightedBPRMF' 'BPRLinear' 'MostPopularByAttributes' 'BPRSLIM' 'LeastSquareSLIM'
ITEMRECOMMENDERS="MostPopular"

# Available Rank Recommenders:
# 'BiPolarSlopeOne' 'GlobalAverage' 'ItemAttributeKNN' 'ItemAverage' 'ItemKNN' 'MatrixFactorization' 'SlopeOne' 'UserAttributeKNN' 'UserAverage' 'UserItemBaseline' 'UserKNN' 'TimeAwareBaseline' 'TimeAwareBaselineWithFrequencies' 'CoClustering' 'Random' 'Constant' 'LatentFeatureLogLinearModel' 'BiasedMatrixFactorization' 'SVDPlusPlus' 'SigmoidSVDPlusPlus' 'SocialMF' 'SigmoidItemAsymmetricFactorModel' 'SigmoidUserAsymmetricFactorModel' 'SigmoidCombinedAsymmetricFactorModel' 'NaiveBayes' 'ExternalRatingPredictor' 'GSVDPlusPlus'
RANKRECOMMENDERS="MatrixFactorization"

#Available Mahout recommenders
# 'svd' ...
MAHOUTRECOMMENDERS="svd"

QUIET=''
GENERATED="$ROOT/generated"

while getopts "i:cp:s:r:m:q" o; do
  case "${o}" in
    i)
      INFILE="${OPTARG}"
      ;;
    c)
      CLEAN="-c"
      ;;
    p)
      ITEMRECOMMENDERS="${OPTARG}"
      ;;
    r)
      RANKRECOMMENDERS="${OPTARG}"
      ;;
    m)
      MAHOUTRECOMMENDERS="${OPTARG}"
      ;;
    s)
      SPLIT="${OPTARG}"
      ;;
    q)
      QUIET="-q"
      ;;
    *)
      usage
      ;;
  esac
done

OPTS="-i $INFILE $CLEAN"

TESTFILE=""
TRAINFILE=""

# Todo: can we avoid having such a long string which, to be honest, no one will change in near future anyways?
trainTestTuples="blend_itemtrain1.txt:blend_itemtest1.txt blend_itemtrain2.txt:blend_itemtest2.txt blend_itemtrain3.txt:blend_itemtest3.txt blend_systemtrain1.txt:blend_systemtest.txt blend_systemtrain2.txt:blend_systemtest.txt blend_systemtrain3.txt:blend_systemtest.txt blend_usertrain1.txt:blend_usertest1.txt blend_usertrain2.txt:blend_usertest2.txt blend_usertrain3.txt:blend_usertest3.txt"

# Generate ratings (blending and timestamps enabled by default)
/bin/bash $ROOT/generators/generate_implicit.sh -b -t $OPTS;

trainTestTuples=""
if [ -n "$SPLIT" ]; then

  if [ "$SPLIT" == "random" ]; then
    for FILE in "$GENERATED"/ratings/*; do
      echo "Splitting based on $INFILE"
      /bin/bash $ROOT/generators/split.sh -r -i $FILE -o "$ROOT/generated/splits"

      FILENAME=$(basename $FILE);
      TESTFILE="${FILENAME}.1.txt";
      TRAINFILE="${FILENAME}.9.txt";

      trainTestTuples+="${TRAINFILE}:${TESTFILE} "
    done
  else
    # Cold start split
    echo "Splitting data into colstart splits"
    python2.7 $ROOT/evaluation/evaluation.py --coldstart-split $ROOT/generated/ratings/blend.txt --feature-file $ROOT/data/product_features.txt -t -fb '1,1,1,1,0';
  fi

fi

if [ "$ITEMRECOMMENDERS" != "" ]; then
  for ir in $ITEMRECOMMENDERS
  do
    # make predictions
    echo "------------------------------"
    /bin/bash $ROOT/generators/myMediaLitePredicter.sh -t "$trainTestTuples" -i -p $ir $QUIET;

    # evaluate predicted values
    /bin/bash $ROOT/evaluation/evaluate.sh -t "$trainTestTuples" -r -i -p $ir -m;
  done
fi

if [ "$RANKRECOMMENDERS" != "" ]; then
  for ir in $RANKRECOMMENDERS
  do
    # make predictions
    /bin/bash $ROOT/generators/myMediaLitePredicter.sh -t "$trainTestTuples" -r -p $ir $QUIET;

    # evaluate predicted values
    /bin/bash $ROOT/generators/evaluate.sh -t "$trainTestTuples" -r -p $ir;
  done
fi

if [ "$MAHOUTRECOMMENDERS" != "" ]; then
  for ir in $MAHOUTRECOMMENDERS
  do
    # make predictions
    /bin/bash $ROOT/generators/mahoutPredict.sh -t "$trainTestTuples" -h -p $ir $QUIET;

    # evaluate predicted values
    /bin/bash $ROOT/evaluation/evaluate.sh -t "$trainTestTuples" -r -h -p $ir;
  done
fi

python $ROOT/evaluation/generateLatexLines.py

echo 'Done.'
