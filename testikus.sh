# Generate ratings
cd generators;
python2.7 ratings.py -m recentness -fx sigmoid_constant -i mongo;
# Split ratings
./split.sh -i ratings/recentness_sigmoid_constant_sc-30.txt;
# Get top K recommendations
cd ../mahout && rm -f *.class && javac TopKRecommendations.java && java TopKRecommendations;
# Evaluate the top K recommendations
javac SobazarRecommender.java && java SobazarRecommender;
cd ../evaluation && python meanAveragePrecision.py;
python meanPercentageRanking.py;
