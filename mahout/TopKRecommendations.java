import org.apache.mahout.cf.taste.common.NoSuchUserException;
import org.apache.mahout.cf.taste.common.TasteException;
import org.apache.mahout.cf.taste.eval.IRStatistics;
import org.apache.mahout.cf.taste.eval.RecommenderBuilder;
import org.apache.mahout.cf.taste.eval.RecommenderEvaluator;
import org.apache.mahout.cf.taste.eval.RecommenderIRStatsEvaluator;
import org.apache.mahout.cf.taste.impl.common.FastIDSet;
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
import org.apache.mahout.cf.taste.model.PreferenceArray;
import org.apache.mahout.cf.taste.neighborhood.UserNeighborhood;
import org.apache.mahout.cf.taste.recommender.RecommendedItem;
import org.apache.mahout.cf.taste.recommender.Recommender;
import org.apache.mahout.cf.taste.similarity.ItemSimilarity;
import org.apache.mahout.cf.taste.similarity.UserSimilarity;

import java.io.*;
import java.util.*;

public class TopKRecommendations {
    /* static String[] files = { "naive.txt", "sigmoid_count.txt", "sigmoid_recent.txt", "blend.txt" }; */
    String[] files = { "blend.txt" };
  /* static String recommender = "itembased"; */

    public void recommendations(String dataPath, String filename, final String recommender, String predictionFile, String testFile) throws IOException, TasteException {
        System.out.println("Using dataPath: " + dataPath);
        System.out.println("Train file: " + filename);
        System.out.println("Using recommender-engine: " + recommender);
        System.out.println("Storing to: " + predictionFile);
        long startTime = System.currentTimeMillis();

        DataModel model = new FileDataModel(new File(dataPath + "/" + filename));

        //PreferenceArray user_test = model.getPreferencesFromUser(userId);
        //System.out.print(user_test);

        RecommenderBuilder builder = new RecommenderBuilder() {
            public Recommender buildRecommender(DataModel model) throws TasteException {
                if (recommender.equals("itembased")) {
                    ItemSimilarity similarity = new LogLikelihoodSimilarity(model);
                    //ItemSimilarity similarity = new PearsonCorrelationSimilarity(model);
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
        DataModel test = new FileDataModel(new File(dataPath + "/" + testFile));
        LongPrimitiveIterator test_users = test.getUserIDs();

        PrintWriter w = new PrintWriter(predictionFile);
        w.print("");
        w.close();

        PrintWriter writer = new PrintWriter(new BufferedWriter(new FileWriter(predictionFile, true)));

        Long i = (long) 0;
        Long ui = (long) 0;

        //System.out.print("\n");
        while (test_users.hasNext()) {
        	//System.out.print("\rUser " + i);
        	i++;
            long user = test_users.next();
            //System.out.println("USER:" +user);

            LongPrimitiveIterator items = model.getItemIDs();


            while (items.hasNext()){
            	long item = items.next();

            	//System.out.println("Switched to next item: " + item);
            	boolean found = false;
            	//System.out.println("ITEM:" +item);
            	try{
            		LongPrimitiveIterator items_user = model.getItemIDsFromUser(user).iterator();
            		while (items_user.hasNext()){
                		ui = items_user.next();
                		//System.out.print(user + " " + item + " vs. " + ui + " equals " + (ui == item) + "\n");
                		if (ui == item){
                			found = true;
                		}
                	}
            		
            	} catch(NoSuchUserException e){
            		found = true;
            		//System.out.println(e);
            	}

            	if(found == false){
            		//System.out.println(user + " " + item + " " + ui);
            		Float rating = (float) r.estimatePreference(user, item);
            		if (rating.isNaN())
            			rating = (float) 0.0;
            		appendToRatingFile(user, item, rating, writer);
            	}
            }
        }
        writer.close();
    }

    public void appendToRatingFile(Long userID, Long itemID, Float rating, PrintWriter writer){
        String f = userID.toString() + '\t' + itemID.toString() + '\t' + rating.toString();
        writer.println(f);
    }

    public void writeToFile(HashMap<Long,List<RecommendedItem>> topKForUsers, String predictionFile) throws IOException {
        //File file = new File("testikus");
        //BufferedReader reader = new BufferedReader(new FileReader(file));

        String saveLocation = getSaveLocation(predictionFile);
        File dir = new File(saveLocation);
        dir.mkdir();

        PrintWriter writer = new PrintWriter(predictionFile, "UTF-8");

        Iterator it = topKForUsers.entrySet().iterator();
        int max = 0;
        Object maxUser = 0;
        while (it.hasNext()) {
            Map.Entry pairs = (Map.Entry)it.next();
            int i = 0;
            for (RecommendedItem ri :((List<RecommendedItem>)pairs.getValue())) {
                writer.println(pairs.getKey() + ", " + ri.getItemID() + ", " + ri.getValue());
                i ++;
            }
            if (i > max) {
                max = i;
                maxUser = pairs.getKey();
            }
            it.remove();
        }
        System.out.println(max);
        System.out.println(maxUser);
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
        String[] vals = new String[5];
        if (args.length < 3) {
            System.out.print("Needs arguments: <ratings-folder> <method> <rating-file> <predictionfile>\n");
            System.out.print("Defaulting to: ../generators/ratings itembased\n");
            vals[0] = "../generated/splits";
            vals[1] = "blend-9.txt";
            vals[2] = "itembased";
            vals[3] = "../generated/predictions/tmp.predictions";
            vals[4] = "blend-1.txt";
        } else {
            vals = args;
        }

        /*List<String> files = parseConfig(vals[2]);

        this.dataPath = vals[0];
        for (int i = 0; i < files.size(); i++) {
        }*/
        recommendations(vals[0], vals[1], vals[2], vals[3], vals[4]);
    }

    public static void main(String[] args) throws IOException, TasteException{
        TopKRecommendations tp = new TopKRecommendations();
        tp.start(args);
    }
}
