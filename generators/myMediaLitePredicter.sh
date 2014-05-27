trap 'echo interrupted; exit' INT

usage() { echo "Usage: ./$0 mtodo"; exit 1; }

# Save the current path
ROOT=$( cd "$( dirname "$0" )" && pwd );

# Some parameters changable in the opts.
TTT=""
MYMEDIAITEM=0
MYMEDIAIRANK=0
RECOMMENDER=""

while getopts "t:irp:" o; do
  case "${o}" in
    t)
      TTT=("${OPTARG}")
      ;;
    i)
      MYMEDIAITEM=1
      ;;
    r)
      MYMEDIAIRANK=1
      ;;
    p)
      RECOMMENDER="${OPTARG}"
      ;;
    *)
      usage
      ;;
  esac
done

# OPTS="-t $TTT $MYMEDIAITEM $MYMEDIAIRANK"
# echo $OPTS

if [ $MYMEDIAITEM -eq 1 ]; then
    # declare -a RAItem=('BPRMF' 'ItemAttributeKNN' 'ItemKNN' 'MostPopular' 'Random' 'UserAttributeKNN' 'UserKNN' 'WRMF' 'Zero' 'MultiCoreBPRMF' 'SoftMarginRankingMF' 'WeightedBPRMF' 'BPRLinear' 'MostPopularByAttributes' 'BPRSLIM' 'LeastSquareSLIM')
    echo "Making MyMediaLite items predictions with $RECOMMENDER";
    for ttt in $TTT
    do
        set -- "$ttt"
        IFS=":"; declare -a Array=($*)
        item_recommendation --training-file="${Array[0]}" --test-file="${Array[1]}" --recommender="$RECOMMENDER" --prediction-file=../predictions/"${Array[0]}"-"${Array[1]}"--i-"$RECOMMENDER".predictions >/dev/null 2>/dev/null &
    done
    wait $!
    echo "Done making MyMediaLite items predictions with $RECOMMENDER";
fi

if [ $MYMEDIAIRANK -eq 1 ]; then
    # declare -a RARatingPrediction=('BiPolarSlopeOne' 'GlobalAverage' 'ItemAttributeKNN' 'ItemAverage' 'ItemKNN' 'MatrixFactorization' 'SlopeOne' 'UserAttributeKNN' 'UserAverage' 'UserItemBaseline' 'UserKNN' 'TimeAwareBaseline' 'TimeAwareBaselineWithFrequencies' 'CoClustering' 'Random' 'Constant' 'LatentFeatureLogLinearModel' 'BiasedMatrixFactorization' 'SVDPlusPlus' 'SigmoidSVDPlusPlus' 'SocialMF' 'SigmoidItemAsymmetricFactorModel' 'SigmoidUserAsymmetricFactorModel' 'SigmoidCombinedAsymmetricFactorModel' 'NaiveBayes' 'ExternalRatingPredictor' 'GSVDPlusPlus')
    echo "Making MyMediaLite rating predictions with $RECOMMENDER";
    for ttt in $TTT
    do
        set -- "$ttt"
        IFS=":"; declare -a Array=($*)
        rating_prediction --training-file="${Array[0]}" --test-file="${Array[1]}" --recommender="$RECOMMENDER" --prediction-file=../predictions/"${Array[0]}"-"${Array[1]}"--r-"$RECOMMENDER".predictions >/dev/null 2>/dev/null &
    done
    wait $!
    echo "Done making MyMediaLite rating predictions with $RECOMMENDER";
fi
