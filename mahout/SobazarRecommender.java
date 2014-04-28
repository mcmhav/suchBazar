import java.io.*;
import java.util.List;

import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.impl.recommender.GenericUserBasedRecommender;
import org.apache.mahout.cf.taste.impl.recommender.GenericItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.recommender.ItemAverageRecommender;
import org.apache.mahout.cf.taste.impl.recommender.ItemUserAverageRecommender;
import org.apache.mahout.cf.taste.impl.recommender.svd.SVDRecommender;
import org.apache.mahout.cf.taste.impl.recommender.svd.ALSWRFactorizer;
import org.apache.mahout.cf.taste.impl.neighborhood.NearestNUserNeighborhood;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.UserSimilarity;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;
import org.apache.mahout.cf.taste.neighborhood.UserNeighborhood;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.eval.RecommenderEvaluator;
import org.apache.mahout.cf.taste.eval.RecommenderBuilder;
import org.apache.mahout.cf.taste.impl.eval.AverageAbsoluteDifferenceRecommenderEvaluator;
import org.apache.mahout.cf.taste.impl.eval.RMSRecommenderEvaluator;

class SobazarRecommender {
  static String dataPath = "../generators/ratings";
  /* static String[] files = { "naive.txt", "sigmoid_count.txt", "sigmoid_recent.txt", "blend.txt" }; */
  static String[] files = { "blend.txt" };
  /* static String recommender = "itembased"; */

  public static void evaluate(String filename, final String recommender) throws IOException, TasteException {
    System.out.println("Using recommender-engine: " + recommender);
    long startTime = System.currentTimeMillis();

    DataModel model = new FileDataModel(new File(dataPath + "/" + filename));
    RecommenderBuilder builder = new RecommenderBuilder() {
      public Recommender buildRecommender(DataModel model) throws TasteException {
        if (recommender.equals("itembased")) {
          ItemSimilarity similarity = new PearsonCorrelationSimilarity(model);
          return new GenericItemBasedRecommender(model, similarity);
        } else if(recommender.equals("userbased")) {
          UserSimilarity similarity = new PearsonCorrelationSimilarity(model);
          UserNeighborhood neighborhood = new NearestNUserNeighborhood(3, similarity, model);
          return new GenericUserBasedRecommender(model, neighborhood, similarity);
        } else if (recommender.equals("itemuseraverage")) {
          return new ItemUserAverageRecommender(model);
        } else if (recommender.equals("svd")) {
          // ALSWRFactorizer(DataModel dataModel, int numFeatures, double lambda, int numIterations)
          // ALSWRFactorizer(DataModel dataModel, int numFeatures, double lambda, int numIterations, boolean usesImplicitFeedback, double alpha)
          //ALSWRFactorizer factorizer = new ALSWRFactorizer(model, 20, 0.01, 5, true, 0.01);
          ALSWRFactorizer factorizer = new ALSWRFactorizer(model, 20, 0.01, 5);
          return new SVDRecommender(model, factorizer);
        }

        // Not found, we default to item-average
        return new ItemAverageRecommender(model);
      }
    };

    RecommenderEvaluator avgdiffEvaluator = new AverageAbsoluteDifferenceRecommenderEvaluator();
    RecommenderEvaluator rmseEvaluator= new RMSRecommenderEvaluator();

    // K-fold evaluation.
    double[][] scores = new double[5][2];
    for (int i = 0; i < scores.length; i++) {
      System.out.print("\rRunning evaluation number " + i + " on " + filename);
      scores[i][0] = avgdiffEvaluator.evaluate(builder, null, model, 0.9, 1.0);
      scores[i][1] = rmseEvaluator.evaluate(builder, null, model, 0.9, 1.0);
    }

    // Get average score based on evaluations.
    double rmse = 0;
    double avgdiff = 0;
    for (int i = 0; i < scores.length; i++) {
      avgdiff += scores[i][0];
      rmse += scores[i][1];
    }

    long endTime = System.currentTimeMillis();
    System.out.print("\r===================== " + filename + "========================\n");
    System.out.print("RMSE: " + rmse/scores.length + "\n");
    System.out.print("AvgDiff: " + avgdiff/scores.length + "\n");
    System.out.print("Took " + (endTime - startTime) + "ms\n");
    System.out.print("===========================================================\n\n");
  }

  public static void main(String[] args) throws IOException, TasteException {
    for (int i = 0; i < files.length; i++) {
      evaluate(files[i], args[0]);
    }
  }
}
