# Generate ratings
cd generators && python ratings.py;
# Split ratings
./split.sh ratings/ratings.txt;
# Get top K recommendations
cd ../mahout && rm -f *.class && javac TopKRecommendations.java && java TopKRecommendations;
# Evaluate the top K recommendations
javac SobazarRecommender.java && java SobazarRecommender;
cd ../evaluation && python meanAveragePrecision.py;
python meanPercentageRanking.py;
