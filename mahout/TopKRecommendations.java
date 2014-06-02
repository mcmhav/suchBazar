import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.eval.IRStatistics;
import org.apache.mahout.cf.taste.eval.RecommenderBuilder;
import org.apache.mahout.cf.taste.eval.RecommenderEvaluator;
import org.apache.mahout.cf.taste.eval.RecommenderIRStatsEvaluator;
import org.apache.mahout.cf.taste.impl.common.LongPrimitiveIterator;
import org.apache.mahout.cf.taste.impl.eval.AverageAbsoluteDifferenceRecommenderEvaluator;
import org.apache.mahout.cf.taste.impl.eval.GenericRecommenderIRStatsEvaluator;
import org.apache.mahout.cf.taste.impl.eval.RMSRecommenderEvaluator;
import org.apache.mahout.cf.taste.impl.model.file.FileDataModel;
import org.apache.mahout.cf.taste.impl.neighborhood.NearestNUserNeighborhood;
import org.apache.mahout.cf.taste.impl.recommender.GenericItemBasedRecommender;
import org.apache.mahout.cf.taste.impl.recommender.GenericUserBasedRecommender;
import org.apache.mahout.cf.taste.impl.recommender.ItemAverageRecommender;
import org.apache.mahout.cf.taste.impl.recommender.ItemUserAverageRecommender;
import org.apache.mahout.cf.taste.impl.recommender.svd.ALSWRFactorizer;
import org.apache.mahout.cf.taste.impl.recommender.svd.SVDRecommender;
import org.apache.mahout.cf.taste.impl.similarity.LogLikelihoodSimilarity;
import org.apache.mahout.cf.taste.impl.similarity.PearsonCorrelationSimilarity;
import org.apache.mahout.cf.taste.model.DataModel;
import org.apache.mahout.cf.taste.neighborhood.UserNeighborhood;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;
import org.apache.mahout.cf.taste.similarity.UserSimilarity;

import java.io.*;
import java.util.*;

public class TopKRecommendations {
    static String dataPath = "../generated/splits";
    /* static String[] files = { "naive.txt", "sigmoid_count.txt", "sigmoid_recent.txt", "blend.txt" }; */
    String[] files = { "blend.txt" };
  /* static String recommender = "itembased"; */

    public void recommendations(String dataPath, String filename, final String recommender, String predictionFile) throws IOException, TasteException {
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
                    ALSWRFactorizer factorizer = new ALSWRFactorizer(model, 20, 100, 5, true, 20);
                    return new SVDRecommender(model, factorizer);
                } else if (recommender.equals("loglikelihood")) {
                    ItemSimilarity similarity = new LogLikelihoodSimilarity(model);
                    return new GenericItemBasedRecommender(model, similarity);
                }
                // Not found, we default to item-average
                return new ItemAverageRecommender(model);
            }
        };

        Recommender r = builder.buildRecommender(model);

        LongPrimitiveIterator items = model.getItemIDs();
        LongPrimitiveIterator users = model.getUserIDs();

        HashMap<Long,List<RecommendedItem>> topKForUsers = new HashMap<Long, List<RecommendedItem>>();

        while (users.hasNext()) {
            long user = users.next();
            List<RecommendedItem> topK = r.recommend(user,16000);

            topKForUsers.put(user,topK);
        }

        writeToFile(topKForUsers, predictionFile);
    }

    public void writeToFile(HashMap<Long,List<RecommendedItem>> topKForUsers, String predictionFile) throws IOException {
        //File file = new File("testikus");
        //BufferedReader reader = new BufferedReader(new FileReader(file));

        String saveLocation = getSaveLocation(predictionFile);
        File dir = new File(saveLocation);
        dir.mkdir();

        PrintWriter writer = new PrintWriter(predictionFile, "UTF-8");

        Iterator it = topKForUsers.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry pairs = (Map.Entry)it.next();
            for (RecommendedItem ri :((List<RecommendedItem>)pairs.getValue())) {
                writer.println(pairs.getKey() + ", " + ri.getItemID() + ", " + ri.getValue());
            }
            it.remove();
        }
        writer.close();
    }

    private String getSaveLocation(String predictionFile){
        String[] folders = predictionFile.split("/");
        String saveLocation = "";
        for (int i = 0; i < folders.length-1; i++) {
            saveLocation += folders[i] + "/";
        }
        return saveLocation;
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
        String[] vals = new String[4];
        if (args.length < 3) {
            System.out.print("Needs arguments: <ratings-folder> <method> <rating-file> <predictionfile>\n");
            System.out.print("Defaulting to: ../generators/ratings itembased\n");
            vals[0] = "../generated/splits";
            vals[1] = "blend_itemtrain1.txt";
            vals[2] = "svd";
            vals[3] = "../generated/predictions/tmp.predictions";
        } else {
            vals = args;
        }

        /*List<String> files = parseConfig(vals[2]);

        this.dataPath = vals[0];
        for (int i = 0; i < files.size(); i++) {
        }*/
        recommendations(vals[0], vals[1], vals[2], vals[3]);
    }

    public static void main(String[] args) throws IOException, TasteException{
        TopKRecommendations tp = new TopKRecommendations();
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
