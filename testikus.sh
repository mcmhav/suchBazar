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
  -a <filterbot settings> A string defining which filterbots to enable.
                          Defaults to '0,0,0,0,0'.
  -c                      Clean existing rating, prediction and scoring files
                          before running.
  -i <input file>         The absolute path to the event log file.
  -f <product features>   The absolute path to file containing all product
                          features obtained from the product DB.
  -d <product file>       Where to find product file with JSON-data, used with
                          cold-start splits. Defaults to 'generated/products.txt'
  -r <rank recommenders>  Which rank recommenders to user with MyMediaLite.
  -p <item recommenders>  Which item recommenders to use with MyMediaLite.
  -m <mahout algorithms>  Which recommender algorithms to use with mahout.
  -s <split type>         How to split test and training. Options: 'cold',
                          'time' or 'random'.
  -k <k values>           When using ItemKNN, control which k-values to use, as
                          a string of integers. E.g. '10 20 50'
  -b                      Convert all ratings to binary (all ratings to 1)
  -q                      Send stdout and stderr to /dev/null (except result)
  -t                      Split coldstart on time
  -l                      Run recommender on blend file only.
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
    svd, itembased, userbased, itemuseraverage, loglikelihood, itemaverage

Examples:
  Split randomly and calculate the itemaverage with mahout:
  $0 -i ../somefile.tab -s random -m 'itemaverage'

  Split on time and use itemKNN with various K-values to do recommendations:
  $0 -i ../somefile.tab -s time -p 'ItemKNN' -k '10 20 50'

  Split with cold start and use some filterbots:
  $0 -i ../somefile.tab -s cold -m 'userbased' -a '1,1,1,0,0'
EOL
exit 1;
}

# Save the current path
ROOT=$( cd "$( dirname "$0" )" && pwd );
GENERATED="$ROOT/generated"

# Some parameters changable in the opts.
INFILE="../datasets/v3/sobazar_events_prod_cleaned_formatted.tab"
FEATURE_FILE="$GENERATED/itemFeatures.txt"
PRODUCT_FILE="$GENERATED/products.txt"
CLEAN=0
SPLIT=""
BINARY=0
QUIET=0
KRANGE=""
ITEMRECOMMENDERS=""
RANKRECOMMENDERS=""
MAHOUTRECOMMENDERS=""
COLDTIME="";
BOTSETTINGS="0,0,0,0,0";
BLENDONLY=0;

while getopts "i:p:s:f:r:m:k:t:a:d:bcqhl" o; do
  case "${o}" in
    a)
      BOTSETTINGS="${OPTARG}"
      ;;
    c)
      CLEAN=1
      ;;
    i)
      INFILE="${OPTARG}"
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
    d)
      PRODUCT_FILE="${OPTARG}"
      ;;
    s)
      SPLIT="${OPTARG}"
      ;;
    b)
      BINARY=1
      ;;
    q)
      QUIET=1
      ;;
    k)
      KRANGE="${OPTARG}"
      ;;
    f)
      FEATURE_FILE="${OPTARG}"
      ;;
    t)
      COLDTIME="-t"
      ;;
    l)
      BLENDONLY=1
      ;;
    h)
      usage
      ;;
    *)
      usage
      ;;
  esac
done


main() {
  # Check that the infile exists.
  if [ ! -f $INFILE ] && [ "$INFILE" != "mongo" ]; then
    echo "Did not find $INFILE. Please specify event log with '-i eventlog.tab'. Aborting.";
    exit 1;
  fi

  # Generate ratings (blending and timestamps enabled by default)
  C="";
  if [ $CLEAN -eq 1 ]; then C="-c"; fi
  /bin/bash $ROOT/generators/generate_implicit.sh -t -b -i $INFILE $C;

  # Check if we want binary ratings instead, making all ratings 1.
  if [ $BINARY -eq 1 ]; then
    for FILE in "$GENERATED"/ratings/*; do
      FILENAME=$(basename "$FILE");
      cat "$FILE" | awk '{$3=1;print}' FS='\t' OFS='\t' > /tmp/"$FILENAME";
      mv /tmp/"$FILENAME" $FILE;
    done
  fi

  # make predictions folder
  PREDICTIONSFOLDER="$GENERATED"/predictions
  if [ ! -d "$PREDICTIONSFOLDER" ]; then
    mkdir "$PREDICTIONSFOLDER";
  fi

  # Splitting into training and test sets
  trainTestTuples=""
  if [ -z "$SPLIT" ]; then
    echo "You need to specify split with -s <type of split>. Available splits are: 'cold', 'time' and 'random'. Aborting.";
    exit 1;
  elif [ "$SPLIT" == "cold" ]; then
    # Where to find blend file.
    BLEND_FILE="$GENERATED/ratings/blend.txt";
    if [ ! -f "$BLEND_FILE" ]; then
      echo "Need blend file ($BLEND_FILE) in order to do cold start splits. Aborting."; exit 1;
    fi

    # Check that necessary files are OK.
    if [ ! -f "$FEATURE_FILE" ]; then

      # We need to have a product file containing all our data. Ask if user wants to download it.
      if [ ! -f "$PRODUCT_FILE" ]; then
        echo "No featurefile defined. Trying to create it, but you do not have a product DB downloaded."
        read -p "Do you wish to download product data from the SoBazaar API? " yn
        case $yn in
          [Yy]*) create_productfile "$PRODUCT_FILE";;
          [Nn]*) echo "Ok. Then I have to abort, as I can not do cold-start splits."; exit;;
          *) echo "Please answer yes or no [y/n]"; exit 1;;
        esac
      fi

      # At this point we are guaranteed a product file. So we can create the featurefile as well.
      echo "No featurefile found! Creating from ${BLEND_FILE} and ${PRODUCT_FILE}, as: '$FEATURE_FILE'";
      create_featurefile "$FEATURE_FILE" "$PRODUCT_FILE" "$BLEND_FILE";
    fi

    # Cold start split
    trainTestTuples="blend_itemtrain1.txt:blend_itemtest1.txt ";
    trainTestTuples+="blend_itemtrain2.txt:blend_itemtest2.txt ";
    trainTestTuples+="blend_itemtrain3.txt:blend_itemtest3.txt ";
    trainTestTuples+="blend_systemtrain1.txt:blend_systemtest.txt ";
    trainTestTuples+="blend_systemtrain2.txt:blend_systemtest.txt ";
    trainTestTuples+="blend_systemtrain3.txt:blend_systemtest.txt ";
    trainTestTuples+="blend_usertrain1.txt:blend_usertest1.txt ";
    trainTestTuples+="blend_usertrain2.txt:blend_usertest2.txt ";
    trainTestTuples+="blend_usertrain3.txt:blend_usertest3.txt ";
    OPT=(--coldstart-split $BLEND_FILE);
    OPT+=(--feature-file $FEATURE_FILE);
    python2.7 $ROOT/evaluation/evaluation.py "${OPT[@]}" -fb "$BOTSETTINGS" $COLDTIME;
  else
    for FILE in "$GENERATED"/ratings/*; do
      FILENAME=$(basename $FILE);
      FILENAME_NOEXT="${FILENAME%%.*}";
      if [ "$SPLIT" == "random" ]; then
          split "$FILE" "$GENERATED/splits" "$FILENAME" "random";
          TESTFILE="${FILENAME_NOEXT}-1.txt";
          TRAINFILE="${FILENAME_NOEXT}-9.txt";
          if [ $BLENDONLY -eq 1 ]; then
            if [ "$FILENAME" == "blend.txt" ]; then
              trainTestTuples+="${TRAINFILE}:${TESTFILE} ";
            fi
          else
            trainTestTuples+="${TRAINFILE}:${TESTFILE} ";
          fi
      elif [ "$SPLIT" == "time" ]; then
          python2.7 $ROOT/evaluation/simpleTimeSplit.py -i $FILE -s "0.2";
          TESTFILE="${FILENAME_NOEXT}_timetest.txt";
          TRAINFILE="${FILENAME_NOEXT}_timetrain.txt";
          if [ $BLENDONLY -eq 1 ]; then
            if [ "$FILENAME" == "blend.txt" ]; then
              trainTestTuples+="${TRAINFILE}:${TESTFILE} ";
            fi
          else
            trainTestTuples+="${TRAINFILE}:${TESTFILE} ";
          fi
      fi
    done
  fi

  # Recommending with item_recommendation (MyMediaLite)
  if [ "$ITEMRECOMMENDERS" != "" ]; then
    for rectype in $ITEMRECOMMENDERS; do
      medialitePredict "item_recommendation" $rectype "$KRANGE";
      evaluate "item_recommendation" $rectype "$KRANGE";
    done
  fi

  # Recommending with rating predictions (MyMediaLite)
  if [ "$RANKRECOMMENDERS" != "" ]; then
    for rectype in $RANKRECOMMENDERS; do
      medialitePredict "rating_prediction" $rectype "$KRANGE";
      evaluate "rating_prediction" "$rectype" "$KRANGE";
    done
  fi

  # Recommending with Mahout
  if [ "$MAHOUTRECOMMENDERS" != "" ]; then
    for ir in $MAHOUTRECOMMENDERS; do
      # make predictions
      mahoutPredict $ir;

      # evaluate predicted values
      evaluate "mahout" $ir;
    done
  fi

  # Generate Latex-lines based on scoring files.
  python $ROOT/evaluation/generateLatexLines.py;
}

###
### Functions
###

evaluate() {
  # Possitional argument, indicating recommender system.
  RECOMMENDERSYS="${1}";
  RECOMMENDER="${2}";
  KRANGE="${3}";

  echo "Evaluating $RECOMMENDERSYS using $RECOMMENDER"

  # Do evaluation.
  for ttt in $trainTestTuples; do

    # Split 'train.txt:test.txt' on ':', and insert to Array.
    IFS=":" Array=($ttt); unset IFS;
    TRAIN="${Array[0]}";
    TEST="${Array[1]}";
    TRAIN_FILE="$GENERATED/splits/${TRAIN}";
    TEST_FILE="$GENERATED/splits/${TEST}";
    if [ ! -f "$TRAIN_FILE" ]; then
      echo "Did not find training file: $TRAIN_FILE. Please try again. Aborting.";
      exit 1;
    fi
    if [ ! -f "$TEST_FILE" ]; then
      echo "Did not find test file: $TEST_FILE. Please try again. Aborting.";
      exit 1;
    fi
    OPT=(--training-file $TRAIN_FILE);
    OPT+=(--feature-file $FEATURE_FILE);
    OPT+=(--test-file $TEST_FILE);

    arr=("LeastSquareSLIM" "UserAttributeKNN" "UserKNN" "ItemKNN")
    if [[ " ${arr[@]} " =~ " ${RECOMMENDER} " ]] && [ "$KRANGE" != "" ]; then
      for K in $KRANGE; do
        PRED_FILE="$GENERATED/predictions/${TRAIN}-$K-$SPLIT-$RECOMMENDERSYS-$RECOMMENDER.predictions";
        tmp="${OPT[@]}";
        tmp+=" --prediction-file $PRED_FILE";
        execute_eval "${tmp[@]}" $RECOMMENDERSYS;
      done
    else
      PRED_FILE="$GENERATED/predictions/${TRAIN}--$SPLIT-$RECOMMENDERSYS-$RECOMMENDER.predictions";
      tmp="${OPT[@]}";
      tmp+=" --prediction-file $PRED_FILE";
      execute_eval "${tmp[@]}" $RECOMMENDERSYS;
    fi
  done;
  wait;
}

execute_eval() {
  OPTS="${1}"
  RECOMMENDERSYS="${2}"


  if [ -e "$file_name" ]; then
    echo "File exists"
  fi

  if [ $RECOMMENDERSYS == "item_recommendation" ]; then
    python2.7 $ROOT/evaluation/evaluation.py -b 2 -k 20 ${OPTS} -m &
  else
    python2.7 $ROOT/evaluation/evaluation.py -b 2 -k 20 ${OPTS} &
  fi
}

medialitePredict() {
  # Get arguments
  RECTYPE="${1}";
  RECOMMENDER="${2}";
  KRANGE="${3}";

  echo "Recommending with $RECTYPE using $RECOMMENDER";
  for ttt in $trainTestTuples; do
    # Split 'train.txt:test.txt' on ':', and insert to Array.
    IFS=":" Array=($ttt); unset IFS;
    TRAIN="$GENERATED/splits/${Array[0]}";
    TEST="$GENERATED/splits/${Array[1]}";
    if [ ! -f "$TRAIN" ]; then
      echo "Did not find training file: $TRAIN. Please try again. Aborting.";
      exit 1;
    fi
    if [ ! -f "$TEST" ]; then
      echo "Did not find test file: $TEST. Please try again. Aborting.";
      exit 1;
    fi

    # Arguments to recommender program.
    OPT=(--training-file "${TRAIN}");
    OPT+=(--test-file "${TEST}");
    OPT+=(--recommender $RECOMMENDER);

    # Do item predictions
    arr=("LeastSquareSLIM" "UserAttributeKNN" "UserKNN" "ItemKNN");
    if [[ " ${arr[@]} " =~ " ${RECOMMENDER} " ]] && [ "$KRANGE" != "" ]; then
      for K in $KRANGE; do
        tmp="${OPT[@]}"
        tmp+=" --recommender-options k=$K";
        tmp+=" --recommender-options correlation=Jaccard";
        execute_medialite "${tmp[@]}" "$PREDFILE" "$RECTYPE" "$K";
      done
    else
      tmp="${OPT[@]}"
      execute_medialite "${tmp[@]}" "$PREDFILE" "$RECTYPE";
    fi
  done;
  wait;
}

execute_medialite() {
  OPTS="${1}";
  PREDFILE="$2";
  RECTYPE="$3";
  K="$4";

  PREDFILE="$GENERATED/predictions/${Array[0]}-$K-$SPLIT-$RECTYPE-$RECOMMENDER.predictions";
  OPTS+=" --prediction-file $PREDFILE";

  # Check that the binary exists (is installed)
  hash $RECTYPE 2>/dev/null || { echo >&2 "You need medialite installed to run ${RECTYPE}. Aborting."; exit 1; }

  if [ ! -f "$PREDFILE" ] || [ $CLEAN -eq 1 ]; then
    if [ $QUIET -eq 1 ]; then
      $RECTYPE ${OPTS} >/dev/null &
    else
      $RECTYPE ${OPTS} &
    fi
  fi
}

mahoutPredict() {
  # Get arguments
  RECOMMENDER=${1};

  echo "Recommending with Mahout using $RECOMMENDER";
  cd "$ROOT/mahout";
  javac TopKRecommendations.java
  for ttt in $trainTestTuples; do
    # Split 'train.txt:test.txt' on ':', and insert to Array.
    IFS=":" Array=($ttt); unset IFS;
    TRAINFILE="${Array[0]}";
    TESTFILE="${Array[1]}";
    OUTFILE="$GENERATED/predictions/${Array[0]}--$SPLIT-mahout-$RECOMMENDER.predictions"
    if [ ! -f "$OUTFILE" ] || [ $CLEAN -eq 1 ]; then
      if [ $QUIET -eq 1 ]; then
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

create_featurefile() {
  # Argument 1: The featurefile to create.
  FEATURE_FILE="$1";
  PRODUCT_FILE="$2";
  python2.7 $ROOT/contentBased/main.py -o $FEATURE_FILE -i $PRODUCT_FILE;
}

create_productfile() {
  echo "Creating product file, saving it as: '$PRODUCT_FILE'"
  python2.7 $ROOT/rest/fetch_items.py -o "$PRODUCT_FILE"
}

split() {
  # Argument #1: Input filename. File to split.
  # Argument #2: Output directory. Absolute path to directory.
  # Argument #3: Output filename.
  FILETOSPLIT="${1}";
  OUTDIR="${2}";
  OUTFILENAME="${3}";
  OUTPUT="${2}/${OUTFILENAME%%.*}";

  METHOD="${4}";
  TMPFILE="/tmp/test_tmp.txt";

  if [ ! -d "$OUTDIR" ]; then
    mkdir "$OUTDIR";
  fi

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
main;
