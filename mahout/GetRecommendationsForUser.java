import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.eval.RecommenderBuilder;
import org.apache.mahout.cf.taste.impl.common.LongPrimitiveIterator;
import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;
import org.apache.mahout.cf.taste.impl.neighborhood.NearestNUserNeighborhood;
import org.apache.mahout.cf.taste.impl.recommender.GenericItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.recommender.GenericUserBasedRecommender;
import org.apache.mahout.cf.taste.impl.recommender.ItemAverageRecommender;
import org.apache.mahout.cf.taste.impl.recommender.ItemUserAverageRecommender;
import org.apache.mahout.cf.taste.impl.recommender.svd.ALSWRFactorizer;
import org.apache.mahout.cf.taste.impl.recommender.svd.SVDRecommender;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.neighborhood.UserNeighborhood;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;
import org.apache.mahout.cf.taste.similarity.UserSimilarity;

import java.io.*;
import java.util.*;

public class GetRecommendationsForUser {
    static String dataPath = "../generators/ratings";
    /* static String[] files = { "naive.txt", "sigmoid_count.txt", "sigmoid_recent.txt", "blend.txt" }; */c
    String[] files = { "blend.txt" };
  /* static String recommender = "itembased"; */

    public void recommendations(String filename, final String recommender, final long user) throws IOException, TasteException {
        System.out.println("Using recommender-engine: " + recommender);
        long startTime = System.currentTimeMillis();

        DataModel model = new FileDataModel(new File("../generators/ratings" + "/" + filename));
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
                    ALSWRFactorizer factorizer = new ALSWRFactorizer(model, 20, 0.01, 5);
                    return new SVDRecommender(model, factorizer);
                }
                // Not found, we default to item-average
                return new ItemAverageRecommender(model);
            }
        };

        Recommender r = builder.buildRecommender(model);

        LongPrimitiveIterator items = model.getItemIDs();
        LongPrimitiveIterator users = model.getUserIDs();

        HashMap<Long,List<RecommendedItem>> topKForUsers = new HashMap<Long, List<RecommendedItem>>();

        List<RecommendedItem> topK = r.recommend(user,10000);

        writeToFile(user, topK);
    }

    public void writeToFile(long user, List<RecommendedItem> topKForUser) throws IOException {
        //File file = new File("testikus");
        //BufferedReader reader = new BufferedReader(new FileReader(file));
        PrintWriter writer = new PrintWriter("../generators/ratings/tmp.predictions", "UTF-8");

        for (RecommendedItem ri :((List<RecommendedItem>)topKForUser)) {
            writer.println(user + ", " + ri.getItemID() + ", " + ri.getValue());
        }

        writer.close();
    }

    public List<String> parseConfig(String filename) throws IOException {
        List<String> ratingFiles = new ArrayList<String>();
        File file = new File(filename);
        BufferedReader reader = new BufferedReader(new FileReader(file));
        String text = null;
        while ((text = reader.readLine()) != null){
            ratingFiles.add(text);
        }
        return ratingFiles;
    }

    public void start(String[] args) throws IOException, TasteException {
        String[] vals = new String[3];
        if (args.length < 3) {
            System.out.print("Needs arguments: <ratignsFile> <method> <user>\n");
            System.out.print("Defaulting to: ../generators/ratings itembased\n");
            vals[0] = "recentness_sigmoid_fixed_sr-4.txt";
            vals[1] = "itembased";
            vals[2] = "1342189870";
        } else {
            vals = args;
        }

        recommendations(vals[0], vals[1], Long.parseLong(vals[2]));
    }

    public static void main(String[] args) throws IOException, TasteException{
        GetRecommendationsForUser tp = new GetRecommendationsForUser();
        tp.start(args);
    }

/*===================== testur========================
RMSE: 1.2692955172180542
AvgDiff: 0.9100378792394291
Precision: 0.034020521509931324
Recall: 0.003581286484268638
F1Measure: 0.006480392319969338
nDCG: 0.034084846430383786
Reach: 0.396240138756784
FallOut: 1.4278112033939378E-4
Took 9403990ms to calculate 1-fold cross-validation
===========================================================*/
}
