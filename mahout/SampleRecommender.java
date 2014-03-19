import java.io.*;
import java.util.List;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.impl.recommender.GenericUserBasedRecommender;
import org.apache.mahout.cf.taste.impl.neighborhood.NearestNUserNeighborhood;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.UserSimilarity;
import org.apache.mahout.cf.taste.neighborhood.UserNeighborhood;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.eval.RecommenderEvaluator;
import org.apache.mahout.cf.taste.eval.RecommenderBuilder;
import org.apache.mahout.cf.taste.impl.eval.AverageAbsoluteDifferenceRecommenderEvaluator;
import org.apache.mahout.cf.taste.impl.eval.RMSRecommenderEvaluator;

class SampleRecommender {
  public static void main(String[] args) throws IOException, TasteException {
    long startTime = System.currentTimeMillis();

    DataModel model = new FileDataModel(new File("../generators/data/userItemRating.csv"));
    //DataModel model = new FileDataModel(new File("data.csv"));
    RecommenderBuilder builder = new RecommenderBuilder() {
      public Recommender buildRecommender(DataModel model) throws TasteException {
        UserSimilarity similarity = new PearsonCorrelationSimilarity(model);
        UserNeighborhood neighborhood = new NearestNUserNeighborhood(3, similarity, model);
        return new GenericUserBasedRecommender(model, neighborhood, similarity);
      }
    };
    //RecommenderEvaluator evaluator = new AverageAbsoluteDifferenceRecommenderEvaluator(); // Scores around 5.0.
    RecommenderEvaluator evaluator = new RMSRecommenderEvaluator(); // Scores around 10.5.

    // K-fold evaluation.
    double[] scores = new double[30];
    for (int i = 0; i < scores.length; i++) {
      System.out.print("\rRunning evaluation number " + i);
      scores[i] = evaluator.evaluate(builder, null, model, 0.9, 1.0);
    }

    // Get average score based on evaluations.
    double sum = 0;
    for (double d : scores) { sum += d; }
    long endTime = System.currentTimeMillis();
    System.out.print("\rAverage score after " + scores.length + " evaluations: " + sum/scores.length + " (Took : " + (endTime - startTime) + " ms)\n");
  }
}
