# Generate ratings
cd generators;

./test.sh -b;

exit;
# Split ratings
./split.sh -i ratings/blend.txt;

# Get top K recommendations
cd ../mahout && rm -f *.class && javac TopKRecommendations.java && java TopKRecommendations;

# Evaluate the top K recommendations
javac SobazarRecommender.java && java SobazarRecommender;
cd ../evaluation && python meanAveragePrecision.py;
python meanPercentageRanking.py;


