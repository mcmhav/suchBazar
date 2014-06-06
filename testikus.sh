#!/bin/bash

# Exit on error
set -e

# Trap ctrl+c and abort all if it is entered
trap 'echo -e "Interrupted, killing\n $(jobs)"; kill $(jobs -p); exit' INT

# Usage function, describing the parameters to the user.
usage() { 
cat <<EOL
Usage: $0 [options]

This program can do the following depending on the options provided:
  - Generate a set of implicit ratings based on an event log.
  - Recommend based on methods provided either by Mahout or MyMediaLite.
  - Evaluate the results yielding MAP@20, AUC and ROC.
  - Write the result to a latex-table, for easy exporting to a report.

OPTIONS:
  -i <input file>         The absolute path to the event log file.
  -f <product features>   The absolute path to file containing all product
                          features obtained from the product DB.
  -r <rank recommenders>  Which rank recommenders to user with MyMediaLite.
  -p <item recommenders>  Which item recommenders to use with MyMediaLite.
  -m <mahout algorithms>  Which recommender algorithms to use with mahout.
  -s <split type>         How to split test and training. Options: 'cold',
                          'time' or 'random'.
  -k <k values>           When using ItemKNN, control which k-values to use, as
                          a string of integers. E.g. '10 20 50'
  -b                      Convert all ratings to binary (all ratings to 1)
  -c                      Clean existing rating, prediction and scoring files
                          before running.
  -q                      Send stdout and stderr to /dev/null (except result)
  -h                      Display this help-information.

RANK RECOMMENDERS:
  The following algorithms are available to use with the rank recommender
  provided by MyMediaLite:
    BiPolarSlopeOne, GlobalAverage, ItemAttributeKNN, ItemAverage, ItemKNN
    MatrixFactorization, SlopeOne, UserAttributeKNN, UserAverage
    UserItemBaseline, UserKNN, TimeAwareBaseline
    TimeAwareBaselineWithFrequencies, CoClustering, Random, Constant
    LatentFeatureLogLinearModel, BiasedMatrixFactorization, SVDPlusPlus
    SigmoidSVDPlusPlus, SocialMF, SigmoidItemAsymmetricFactorModel
    SigmoidUserAsymmetricFactorModel, SigmoidCombinedAsymmetricFactorModel
    NaiveBayes, ExternalRatingPredictor, GSVDPlusPlus

ITEM RECOMMENDERS:
  The following algorithms are available to use with the item recommender
  provided by MyMediaLite:
    BPRMF, ItemAttributeKNN, ItemKNN, MostPopular, Random 
    UserAttributeKNN, UserKNN, WRMF, Zero, MultiCoreBPRMF 
    SoftMarginRankingMF, WeightedBPRMF, BPRLinear, MostPopularByAttributes 
    BPRSLIM, LeastSquareSLIM

MAHOUT RECOMMENDERS:
  The following methods are available when using Mahout:
    svd, itembased, userbased, itemuseraverage, svd, loglikelihood, itemaverage
    
Examples:
  Split randomly and calculate the itemaverage with mahout:
  $0 -i ../somefile.tab -s random -m 'itemaverage'

  Split on time and use itemKNN with various K-values to do recommendations:
  $0 -i ../somefile.tab -s time -p 'ItemKNN' -k '10 20 50'
EOL
exit 1; 
}

# Save the current path
ROOT=$( cd "$( dirname "$0" )" && pwd );
GENERATED="$ROOT/generated"

# Some parameters changable in the opts.
INFILE="../datasets/v3/sobazar_events_prod_cleaned_formatted.tab"
FEATURE_FILE="$GENERATED/itemFeatures.txt"
CLEAN=""
SPLIT=""
BINARY=0

# Available Item Recommenders:
# 'BPRMF' 'ItemAttributeKNN' 'ItemKNN' 'MostPopular' 'Random'
# 'UserAttributeKNN' 'UserKNN' 'WRMF' 'Zero' 'MultiCoreBPRMF'
# 'SoftMarginRankingMF' 'WeightedBPRMF' 'BPRLinear' 'MostPopularByAttributes'
# 'BPRSLIM' 'LeastSquareSLIM'
ITEMRECOMMENDERS=""

# Available Rank Recommenders:
# 'BiPolarSlopeOne' 'GlobalAverage' 'ItemAttributeKNN' 'ItemAverage' 'ItemKNN'
# 'MatrixFactorization' 'SlopeOne' 'UserAttributeKNN' 'UserAverage'
# 'UserItemBaseline' 'UserKNN' 'TimeAwareBaseline'
# 'TimeAwareBaselineWithFrequencies' 'CoClustering' 'Random' 'Constant'
# 'LatentFeatureLogLinearModel' 'BiasedMatrixFactorization' 'SVDPlusPlus'
# 'SigmoidSVDPlusPlus' 'SocialMF' 'SigmoidItemAsymmetricFactorModel'
# 'SigmoidUserAsymmetricFactorModel' 'SigmoidCombinedAsymmetricFactorModel'
# 'NaiveBayes' 'ExternalRatingPredictor' 'GSVDPlusPlus'
RANKRECOMMENDERS=""

#Available Mahout recommenders
# 'svd', 'itembased', 'userbased', itemuseraverage', 'svd', 'loglikelihood',
# 'itemaverage'
MAHOUTRECOMMENDERS=""

QUIET=""
KRANGE=""

while getopts "i:p:s:f:r:m:k:bcqh" o; do
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
    f)
      FEATUREFILE="${OPTARG}"
      ;;
    h)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

OPTS="-i $INFILE $CLEAN"

main() {
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

  # Splitting into training and test sets
  trainTestTuples=""
  for FILE in "$GENERATED"/ratings/*; do
    FILENAME=$(basename $FILE);
    FILENAME_NOEXT="${FILENAME%%.*}";
    if [ -n "$SPLIT" ]; then
        if [ "$SPLIT" == "random" ]; then
            split "$FILE" "$GENERATED/splits" "$FILENAME" "random";
            TESTFILE="${FILENAME_NOEXT}-1.txt";
            TRAINFILE="${FILENAME_NOEXT}-9.txt";
            trainTestTuples+="${TRAINFILE}:${TESTFILE} "
        elif [ "$SPLIT" == "time" ]; then
            python2.7 $ROOT/evaluation/simpleTimeSplit.py -i $FILE;
            TESTFILE="${FILENAME_NOEXT}_timetest.txt";
            TRAINFILE="${FILENAME_NOEXT}_timetrain.txt";
            trainTestTuples+="${TRAINFILE}:${TESTFILE} "
        elif [ "$SPLIT" == "cold" ]; then
          # Cold start split
          trainTestTuples="blend_itemtrain1.txt:blend_itemtest1.txt "
          trainTestTuples+="blend_itemtrain2.txt:blend_itemtest2.txt "
          trainTestTuples+="blend_itemtrain3.txt:blend_itemtest3.txt "
          trainTestTuples+="blend_systemtrain1.txt:blend_systemtest.txt "
          trainTestTuples+="blend_systemtrain2.txt:blend_systemtest.txt "
          trainTestTuples+="blend_systemtrain3.txt:blend_systemtest.txt "
          trainTestTuples+="blend_usertrain1.txt:blend_usertest1.txt "
          trainTestTuples+="blend_usertrain2.txt:blend_usertest2.txt "
          trainTestTuples+="blend_usertrain3.txt:blend_usertest3.txt "
          python2.7 $ROOT/evaluation/evaluation.py --coldstart-split $GENERATED/ratings/blend.txt --feature-file $ROOT/data/product_features.txt -t -fb '1,1,1,1,1';
        fi
    else
      echo "Getting tuples, no splitting"
      TESTFILE="${FILENAME_NOEXT}-1.txt";
      TRAINFILE="${FILENAME_NOEXT}-9.txt";
      trainTestTuples+="${TRAINFILE}:${TESTFILE} "
    fi
  done

  # Recommending with item_recommendation (MyMediaLite)
  if [ "$ITEMRECOMMENDERS" != "" ]; then
    for ir in $ITEMRECOMMENDERS; do
      medialitePredict "item_recommendation" $ir $KRANGE
      evaluate "item_recommendation" $ir
    done
  fi

  # Recommending with rating predictions (MyMediaLite)
  if [ "$RANKRECOMMENDERS" != "" ]; then
    for ir in $RANKRECOMMENDERS; do
      medialitePredict "rating_prediction" $ir $KRANGE
      evaluate "rating_prediction" "$ir"
    done
  fi

  # Recommending with Mahout
  if [ "$MAHOUTRECOMMENDERS" != "" ]; then
    for ir in $MAHOUTRECOMMENDERS; do
      # make predictions
      # /bin/bash $GENERATED/mahoutPredict.sh -t "$trainTestTuples" -h -p $ir $CLEAN $QUIET;
      mahoutPredict $ir

      # evaluate predicted values
      evaluate "mahout" $ir
    done
  fi

  # Generate Latex-lines based on scoring files.
  python $ROOT/evaluation/generateLatexLinesNormSplits.py
}

###
### Functions
###

evaluate() {
  # Possitional argument, indicating recommender system.
  RECOMMENDERSYS="${1}";
  RECOMMENDER="${2}";

  echo "Evaluating $RECOMMENDERSYS using $RECOMMENDER"

  # Do evaluation.
  for ttt in $trainTestTuples; do

    # Split 'train.txt:test.txt' on ':', and insert to Array.
    IFS=":" read -a Array <<< $ttt;
    TRAIN="${Array[0]}";
    TEST="${Array[1]}";
    TRAIN_FILE="$GENERATED/splits/${TRAIN}";
    TEST_FILE="$GENERATED/splits/${TEST}";
    OPT=(--training-file $TRAIN_FILE);
    OPT+=(--feature-file $FEATURE_FILE);
    OPT+=(--test-file $TEST_FILE);

    arr=("LeastSquareSLIM" "UserAttributeKNN" "UserKNN" "ItemKNN")
    if [[ " ${arr[@]} " =~ " ${RECOMMENDER} " ]] && [ "$KVAL" != "" ]; then
      for K in "$KVAL"; do
        PRED_FILE="$GENERATED/predictions/${TRAIN}-$KVAL-$SPLIT-$RECOMMENDERSYS-$RECOMMENDER.predictions";
        OPT+=(--prediction-file $PRED_FILE);
        execute_eval OPT[@] $RECOMMENDERSYS
      done
    else
      PRED_FILE="$GENERATED/predictions/${TRAIN}--$SPLIT-$RECOMMENDERSYS-$RECOMMENDER.predictions";
      OPT+=(--prediction-file $PRED_FILE);
      execute_eval OPT[@] $RECOMMENDERSYS
    fi
  done;
  wait;
}

execute_eval() {
  OPTS="${!1}"
  RECOMMENDERSYS="${2}"

  if [ $RECOMMENDERSYS == "item_recommendation" ]; then
    python2.7 $ROOT/evaluation/evaluation.py -b 2 -k 20 ${OPTS} -m &
  else
    python2.7 $ROOT/evaluation/evaluation.py -b 2 -k 20 ${OPTS} &
  fi
}

medialitePredict() {
  # Get arguments
  RECTYPE="${1}"
  RECOMMENDER="${2}";
  KVAL="${3}";

  echo "Recommending with $RECTYPE using $RECOMMENDER"

  for ttt in $trainTestTuples; do
    # Split 'train.txt:test.txt' on ':', and insert to Array.
    IFS=":" read -a Array <<< $ttt;
    TRAIN="${Array[0]}";
    TEST="${Array[1]}";
    OPT=(--training-file "$ROOT/generated/splits/${TRAIN}");
    OPT+=(--test-file "$ROOT/generated/splits/${TEST}");
    OPT+=(--recommender $RECOMMENDER);

    # Do item predictions
    arr=("LeastSquareSLIM" "UserAttributeKNN" "UserKNN" "ItemKNN")
    if [[ " ${arr[@]} " =~ " ${RECOMMENDER} " ]] && [ "$KVAL" != "" ]; then
      for K in "$KVAL"; do
        OPT+=("--recommender-options k=$K");
        OPT+=("--recommender-options correlation=Jaccard");
        execute_medialite OPT[@] "$PREDFILE" "$RECTYPE" "$K"
      done
    else
      execute_medialite OPT[@] "$PREDFILE" "$RECTYPE"
    fi
  done;
  wait;
}

execute_medialite() {
  OPTS="${!1}"
  PREDFILE="$2"
  RECTYPE="$3"
  K="$4"

  PREDFILE="$GENERATED/predictions/${TRAIN}-$K-$SPLIT-$RECTYPE-$RECOMMENDER.predictions"
  OPTS+=" --prediction-file $PREDFILE";

  if [ ! -f "$PREDFILE" ] || [ "$CLEAN" == "-c" ]; then
    if [ "$QUIET" == "-q" ]; then
      $RECTYPE ${OPTS} >/dev/null &
    else
      $RECTYPE ${OPTS} &
    fi
  fi
}

mahoutPredict() {
  # Get arguments
  RECOMMENDER=${1};

  echo "Recommending with Mahout using $RECOMMENDER"
  echo "$trainTestTuples"
  cd "$ROOT/mahout"
  javac TopKRecommendations.java
  for ttt in $trainTestTuples; do
    # Split 'train.txt:test.txt' on ':', and insert to Array.
    IFS=":" read -a Array <<< $ttt;
    TRAINFILE="${Array[0]}";
    TESTFILE="${Array[1]}";
    OUTFILE="$GENERATED/predictions/${Array[0]}--$SPLIT-mahout-$RECOMMENDER.predictions"
    if [ ! -f "$OUTFILE" ] || [ "$CLEAN" == "-c" ]; then
      if [ "$QUIET" == "-q" ]; then
        java TopKRecommendations "$GENERATED/splits" $TRAINFILE $RECOMMENDER $OUTFILE $TESTFILE >/dev/null 2>/dev/null &
      else
        java TopKRecommendations "$GENERATED/splits" $TRAINFILE $RECOMMENDER $OUTFILE $TESTFILE &
      fi
    else
      echo "Already had $OUTFILE and thus, I did not predict anything new...";
    fi
  done;
  cd -
  wait;
}

split() {
  # Argument #1: Input filename. File to split.
  # Argument #2: Output directory. Absolute path to directory.
  # Argument #3: Output filename.
  FILETOSPLIT="${1}"
  OUTDIR="${2}"
  OUTFILENAME="${3}"
  OUTPUT="${2}/${OUTFILENAME%%.*}";

  METHOD="${4}";
  TMPFILE="/tmp/test_tmp.txt";

  if [ "$METHOD" == "random" ]; then
    perl -MList::Util -e 'print List::Util::shuffle <>' "$FILETOSPLIT" > "$TMPFILE";
    FILETOSPLIT="$TMPFILE";
  fi

  awk '
    BEGIN { srand() }
    {f = rand() <= 0.9 ? "'"${OUTPUT}"'-9.txt" : "'"${OUTPUT}"'-1.txt"; print > f}
  ' "$FILETOSPLIT"

  rm -f "$TMPFILE";
}

# Run main function
main
