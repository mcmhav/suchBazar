# make predictions

# With MyMediaLite - installed globally
# FROM=20
# TO=40
# declare -a RAItem=('BPRMF' 'ItemAttributeKNN' 'ItemKNN' 'MostPopular' 'Random' 'UserAttributeKNN' 'UserKNN' 'WRMF' 'Zero' 'MultiCoreBPRMF' 'SoftMarginRankingMF' 'WeightedBPRMF' 'BPRLinear' 'MostPopularByAttributes' 'BPRSLIM' 'LeastSquareSLIM')
# declare -a RARatingPrediction=('BiPolarSlopeOne' 'GlobalAverage' 'ItemAttributeKNN' 'ItemAverage' 'ItemKNN' 'MatrixFactorization' 'SlopeOne' 'UserAttributeKNN' 'UserAverage' 'UserItemBaseline' 'UserKNN' 'TimeAwareBaseline' 'TimeAwareBaselineWithFrequencies' 'CoClustering' 'Random' 'Constant' 'LatentFeatureLogLinearModel' 'BiasedMatrixFactorization' 'SVDPlusPlus' 'SigmoidSVDPlusPlus' 'SocialMF' 'SigmoidItemAsymmetricFactorModel' 'SigmoidUserAsymmetricFactorModel' 'SigmoidCombinedAsymmetricFactorModel' 'NaiveBayes' 'ExternalRatingPredictor' 'GSVDPlusPlus')

# In splits folder
cd splits;
declare -a trainTestTuples=('blend_itemtrain1.txt:blend_itemtest1.txt' 'blend_itemtrain2.txt:blend_itemtest2.txt' 'blend_itemtrain3.txt:blend_itemtest3.txt' 'blend_systemtrain1.txt:blend_systemtest.txt' 'blend_systemtrain2.txt:blend_systemtest.txt' 'blend_systemtrain3.txt:blend_systemtest.txt' 'blend_usertrain1.txt:blend_usertest1.txt' 'blend_usertrain2.txt:blend_usertest2.txt' 'blend_usertrain3.txt:blend_usertest3.txt')

declare -a RA=('MatrixFactorization')
for a in "${RA[@]}"
do
    for ttt in "${trainTestTuples[@]}"
    do
        set -- "$ttt"
        IFS=":"; declare -a Array=($*)
        # echo "${Array[0]}"
        # echo "${Array[1]}"
        rating_prediction --training-file="${Array[0]}" --test-file="${Array[1]}" --recommender="$a" --prediction-file=../predictions/"$a".predictions
    done
done





# Please provide either --test-file=FILE, --test-ratio=NUM, --cross-validation=K, --chronological-split=NUM|DATETIME, or --save-model=FILE.

#    - MatrixFactorization num_factors=10 regularization=0.015 learn_rate=0.01 learn_rate_decay=1 num_iter=30
#        supports --find-iter=N, --online-evaluation

# With Mahout in root of soBazar:
# Get top K recommendations
# cd ../mahout && rm -f *.class && javac TopKRecommendations.java && java TopKRecommendations;


