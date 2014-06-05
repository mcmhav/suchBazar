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
        else
          # Cold start split
          trainTestTuples+="blend_itemtrain1.txt:blend_itemtest1.txt "
          trainTestTuples+="blend_itemtrain2.txt:blend_itemtest2.txt "
          trainTestTuples+="blend_itemtrain3.txt:blend_itemtest3.txt "
          trainTestTuples+="blend_systemtrain1.txt:blend_systemtest.txt "
          trainTestTuples+="blend_systemtrain2.txt:blend_systemtest.txt "
          trainTestTuples+="blend_systemtrain3.txt:blend_systemtest.txt "
          trainTestTuples+="blend_usertrain1.txt:blend_usertest1.txt "
          trainTestTuples+="blend_usertrain2.txt:blend_usertest2.txt "
          trainTestTuples+="blend_usertrain3.txt:blend_usertest3.txt"
          python2.7 $ROOT/evaluation/evaluation.py --coldstart-split $GENERATED/ratings/blend.txt --feature-file $ROOT/data/product_features.txt -t -fb '1,1,1,1,0';
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
      medialitepredict $ir $KRANGE
      evaluate "item_recommendation" $ir
    done
  fi

  # Recommending with rating predictions (MyMediaLite)
  if [ "$RANKRECOMMENDERS" != "" ]; then
    for ir in $RANKRECOMMENDERS; do
      medialitepredict $ir $KRANGE
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
  RECOMMENDERSYS="${0}";
  RECOMMENDER="${1}";

  # Check if we are evaluating something that comes from mymedialite.
  MYMEDIALITE_COND=""
  if [ $RECOMMENDERSYS != "mahout" ]; then
    MYMEDIALITE_COND="-m"
  fi

  # Do evaluation.
  for ttt in $trainTuples; do

    # Split 'train.txt:test.txt' on ':', and insert to Array.
    IFS=":" read -a Array <<< $ttt;
    TRAIN="${Array[0]}";
    TEST="${Array[1]}";
    TRAIN_FILE="$GENERATED/splits/${TRAIN}";
    TEST_FILE="$GENERATED/splits/${TEST}";

    PRED_FILE="$PREDFOLDER/${TRAIN}-$KVAL-$RECOMMENDERSYS-$RECOMMENDER.predictions";

    OPT=(--training-file $TRAIN_FILE);
    OPT+=(--test-file $TEST_FILE);
    OPT+=(--prediction-file $PRED_FILE);

    python2.7 $ROOT/evaluation/evaluation.py -b 2 -k 20 "${OPT[@]}" "$MYMEDIALITE_COND" &
  done;
  wait;
}

medialitePredict() {
  # Get arguments
  RECOMMENDER="${0}";
  KVAL="${1}";

  for ttt in $trainTuples; do
    # Split 'train.txt:test.txt' on ':', and insert to Array.
    IFS=":" read -a Array <<< $ttt;
    TRAIN="${Array[0]}";
    TEST="${Array[1]}";
    PREDFILE="$PREDICTIONS/${TRAIN}-$KVAL-$RECTYPE-$RECOMMENDER.predictions"

    OPT=(--training-file "$ROOT/generated/splits/${TRAIN}");
    OPT+=(--test-file "$ROOT/generated/splits/${TEST}");
    OPT+=(--recommender $RECOMMENDER);
    OPT+=(--recommender-options "k=$KVAL correlation=Jaccard");
    OPT+=(--prediction-file "$PREDFILE");

    # Do item predictions
    if [ ! -f "$PREDFILE" ] || [ $CLEAN -eq 1 ]; then
      if [ $QUIET -eq 1 ]; then
        $RECTYPE ${OPT[@]} >/dev/null &
      else
        $RECTYPE ${OPT[@]} &
      fi
    fi
  done;
  wait;
}

mahoutPredict() {
  # Get arguments
  RECOMMENDER=${0};

  for ttt in $trainTuples; do
    # Split 'train.txt:test.txt' on ':', and insert to Array.
    IFS=":" read -a Array <<< $ttt;
    TRAINFILE="${Array[0]}";
    TESTFILE="${Array[1]}";
    OUTFILE="$PREDICTIONS/${Array[0]}--mahout-$RECOMMENDER.predictions"
    if [ ! -f "$OUTFILE" ] || [ $CLEAN -eq 1 ]; then
      if [ $QUIET -eq 1 ]; then
        java TopKRecommendations "$GENERATED/splits" $TRAINFILE $RECOMMENDER $OUTFILE $TESTFILE >/dev/null 2>/dev/null &
      else
        java TopKRecommendations "$GENERATED/splits" $TRAINFILE $RECOMMENDER $OUTFILE $TESTFILE &
      fi
    else
      echo "Already had $OUTFILE and thus, I did not predict anything new...";
      exit 1;
    fi
  done;
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
