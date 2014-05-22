# make predictions

# With MyMediaLite - installed globally
FROM=20
TO=40
# declare -a RA=('BPRMF' 'ItemAttributeKNN' 'ItemKNN' 'MostPopular' 'Random' 'UserAttributeKNN' 'UserKNN' 'WRMF' 'Zero' 'MultiCoreBPRMF' 'SoftMarginRankingMF' 'WeightedBPRMF' 'BPRLinear' 'MostPopularByAttributes' 'BPRSLIM' 'LeastSquareSLIM')
declare -a RA=('MostPopular')
for a in "${RA[@]}"
do
    item_recommendation --training-file=ratings/blend.txt.9.txt --recommender="$a" --prediction-file=predictions/"$a".predictions
done

# With Mahout in root of soBazar:
# Get top K recommendations
# cd ../mahout && rm -f *.class && javac TopKRecommendations.java && java TopKRecommendations;


