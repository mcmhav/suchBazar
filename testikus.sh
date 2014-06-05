#!/bin/bash

# Exit on error
set -e

# Trap ctrl+c and abort all if it is entered
trap 'echo interrupted; kill $(jobs -p); exit' INT

# Usage function, describing the parameters to the user.
usage() { echo "Usage: $0 -i sobazar_input.tab"; exit 1; }

# Save the current path
ROOT=$( cd "$( dirname "$0" )" && pwd );

# Some parameters changable in the opts.
INFILE="../datasets/v3/sobazar_events_prod_cleaned_formatted.tab"
CLEAN=""
SPLIT=""
BINARY=0

# Available Item Recommenders:
# 'BPRMF' 'ItemAttributeKNN' 'ItemKNN' 'MostPopular' 'Random' 'UserAttributeKNN' 'UserKNN' 'WRMF' 'Zero' 'MultiCoreBPRMF' 'SoftMarginRankingMF' 'WeightedBPRMF' 'BPRLinear' 'MostPopularByAttributes' 'BPRSLIM' 'LeastSquareSLIM'
#ITEMRECOMMENDERS="UserKNN ItemKNN MostPopular Random"
ITEMRECOMMENDERS=""

# Available Rank Recommenders:
# 'BiPolarSlopeOne' 'GlobalAverage' 'ItemAttributeKNN' 'ItemAverage' 'ItemKNN' 'MatrixFactorization' 'SlopeOne' 'UserAttributeKNN' 'UserAverage' 'UserItemBaseline' 'UserKNN' 'TimeAwareBaseline' 'TimeAwareBaselineWithFrequencies' 'CoClustering' 'Random' 'Constant' 'LatentFeatureLogLinearModel' 'BiasedMatrixFactorization' 'SVDPlusPlus' 'SigmoidSVDPlusPlus' 'SocialMF' 'SigmoidItemAsymmetricFactorModel' 'SigmoidUserAsymmetricFactorModel' 'SigmoidCombinedAsymmetricFactorModel' 'NaiveBayes' 'ExternalRatingPredictor' 'GSVDPlusPlus'
#RANKRECOMMENDERS="UserKNN ItemKNN"

#Available Mahout recommenders
# 'svd' ...

#MAHOUTRECOMMENDERS="itemuseraverage "
MAHOUTRECOMMENDERS=""

QUIET=""
GENERATED="$ROOT/generated"
KRANGE=""

while getopts "i:cp:s:r:m:qbk:" o; do
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
    b)
      BINARY=1
      ;;
    q)
      QUIET="-q"
      ;;
    k)
      KRANGE="${OPTARG}"
      ;;
    *)
      usage
      ;;
  esac
done

OPTS="-i $INFILE $CLEAN"

# Generate ratings (blending and timestamps enabled by default)
/bin/bash $ROOT/generators/generate_implicit.sh -t -b $OPTS;

# Check if we want binary ratings instead, making all ratings 1.
if [ $BINARY -eq 1 ]; then
  for FILE in "$GENERATED"/ratings/*; do
    FILENAME=$(basename "$FILE")
    cat "$FILE" | awk '{$3=1;print}' FS='\t' OFS='\t' > /tmp/"$FILENAME"
    mv /tmp/"$FILENAME" $FILE
  done
fi

trainTestTuples=""
if [ -n "$SPLIT" ]; then
  if [ "$SPLIT" == "random" ]; then
    for FILE in "$GENERATED"/ratings/*; do
      echo "Splitting based on $INFILE"
      /bin/bash $ROOT/generators/split.sh -r -i $FILE -o "$ROOT/generated/splits"

      FILENAME=$(basename $FILE);
      TESTFILE="${FILENAME%%.*}-1.txt";
      TRAINFILE="${FILENAME%%.*}-9.txt";

      trainTestTuples+="${TRAINFILE}:${TESTFILE} "
    done
  elif [ "$SPLIT" == "time" ]; then
    for FILE in "$GENERATED"/ratings/*; do
      echo "Splitting $INFILE based on TIME"
      python2.7 $ROOT/evaluation/simpleTimeSplit.py -i $FILE;

      FILENAME=$(basename $FILE);
      TESTFILE="${FILENAME%%.*}_timetest.txt";
      TRAINFILE="${FILENAME%%.*}_timetrain.txt";

      trainTestTuples+="${TRAINFILE}:${TESTFILE} "
    done
  else
    # Cold start split
    echo "Splitting data into colstart splits"
    trainTestTuples="blend_itemtrain1.txt:blend_itemtest1.txt blend_itemtrain2.txt:blend_itemtest2.txt blend_itemtrain3.txt:blend_itemtest3.txt blend_systemtrain1.txt:blend_systemtest.txt blend_systemtrain2.txt:blend_systemtest.txt blend_systemtrain3.txt:blend_systemtest.txt blend_usertrain1.txt:blend_usertest1.txt blend_usertrain2.txt:blend_usertest2.txt blend_usertrain3.txt:blend_usertest3.txt"

    python2.7 $ROOT/evaluation/evaluation.py --coldstart-split $ROOT/generated/ratings/blend.txt --feature-file $ROOT/data/product_features.txt -t -fb '1,1,1,1,0';
  fi
else
  echo "Getting tuples"
  for FILE in "$GENERATED"/ratings/*; do
    FILENAME=$(basename $FILE);
    TESTFILE="${FILENAME}.1.txt";
    TRAINFILE="${FILENAME}.9.txt";

    trainTestTuples+="${TRAINFILE}:${TESTFILE} "
  done
fi

echo $trainTestTuples


predictNevaluate() {
  echo "------------------------------"
  # make predictions
  ptmp=( "${!1}" )
  etmp=( "${!2}" )
  arr=("LeastSquareSLIM" "UserAttributeKNN" "UserKNN" "ItemKNN")
  if [[ " ${arr[@]} " =~ " ${3} " ]] && [ "$KRANGE" != "" ]; then
    for i in $KRANGE; do
      ptmp+=("-k" "$i")
      etmp+=("-k" "$i")
      ptmp+=("$CLEAN" "$QUIET")
    done
  else
    ptmp+=("$CLEAN" "$QUIET")
  fi
  /bin/bash $ROOT/generators/myMediaLitePredicter.sh "${ptmp[@]}";
  # evaluate predicted values
  /bin/bash $ROOT/evaluation/evaluate.sh "${etmp[@]}";
  echo "------------------------------"
}

if [ "$ITEMRECOMMENDERS" != "" ]; then
  for ir in $ITEMRECOMMENDERS
  do
    pOPT=("-t $trainTestTuples" "-r" "item_recommendation" "-p" "$ir")
    eOPT=("-t $trainTestTuples" "-r" "item_recommendation" "-p" "$ir" "-m")
    predictNevaluate pOPT[@] eOPT[@] "$ir"
  done
fi

if [ "$RANKRECOMMENDERS" != "" ]; then
  for ir in $RANKRECOMMENDERS
  do
    pOPT=("-t $trainTestTuples" "-r" "rating_prediction" "-p" "$ir")
    eOPT=("-t $trainTestTuples" "-r" "rating_prediction" "-p" "$ir")
    predictNevaluate pOPT[@] eOPT[@] "$ir"
  done
fi

if [ "$MAHOUTRECOMMENDERS" != "" ]; then
  for ir in $MAHOUTRECOMMENDERS
  do
    # make predictions
    echo "------------------------------"
    /bin/bash $ROOT/generators/mahoutPredict.sh -t "$trainTestTuples" -h -p $ir $CLEAN $QUIET;

    # evaluate predicted values
    /bin/bash $ROOT/evaluation/evaluate.sh -t "$trainTestTuples" -r "mahout" -p $ir;
    echo "------------------------------"
  done
fi

python $ROOT/evaluation/generateLatexLinesNormSplits.py

echo 'Done.'
