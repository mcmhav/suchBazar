#Remove old ratings files
# rm -f generators/ratings/*;
# Generate ratings


cd generators;
./test.sh -b -t -c -i mongo;

# blend.txt -

#Todo set blend split - should be possible to run the system on single files?

# Split ratings
# ./split.sh -i ratings/blend.txt;
# Cold start split
cd ../evaluation;
python2.7 evaluation.py --coldstart-split ../generators/ratings/blend.txt -t -fb '1,1,1,1,0';

# make predictions
cd ../generators;
./predict.sh
exit;

# declare -a RA=('BPRMF' 'ItemAttributeKNN' 'ItemKNN' 'MostPopular' 'Random' 'UserAttributeKNN' 'UserKNN' 'WRMF' 'Zero' 'MultiCoreBPRMF' 'SoftMarginRankingMF' 'WeightedBPRMF' 'BPRLinear' 'MostPopularByAttributes' 'BPRSLIM' 'LeastSquareSLIM')

# Get score for the predictions
cd ../evaluation;
declare -a RA=('MostPopular')
for a in "${RA[@]}"
do
    python2.7 evaluation.py -b 2 -k 20 --training-file ../generators/ratings/blend.txt.9.txt --test-file ../generators/ratings/blend.txt.1.txt --prediction-file ../generators/predictions/"$a".predictions -m
done

# Evaluate the top K recommendations
# javac SobazarRecommender.java && java SobazarRecommender;

