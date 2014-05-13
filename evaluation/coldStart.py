"""

A collection of functions for generating cold-start evaluation dataset splits

The GenerateColdStartSplits is similar to the approaches described in:

    Matchbox: Large Scale Bayesian Recommendations,
    Addressing cold-start problem in recommendation systems,
    Getting to Know You: Learning New User Preferences in Recommender Systems
    
The generateColdStartSystemSplits function is similar to the approach described in:

    Regression-based Latent Factor Models

"""

import random
import helpers


def generateColdStartSplits(ratings, type, test_ratio, rating_splits = 0):
    """
    Generates splits for cold-start user/item evaluation:
    
    path: filepath,
    type: split by "user" (0) or "item" (1),
    test_ratio: percentage of items used for testing,
    rating_splits: number test item ratings used for training for each split
    
    """
    
    #TODO - Make more robust & Add support for timestamps    
    if type == 'user':
        index = 0
        prefix = 'user'
    else:
        index = 1
        prefix = 'item'
    
    if not rating_splits:                                                               #If rating_splits are not defined
        rating_splits = [5, 10, 15]                                                     #Initialize as default
          
    X = helpers.buildDictByIndex(ratings, index)                                        #Build dictionary where item id is used as key
    min_limit = rating_splits[-1] + 5                                                   #Minimum number of ratings for test users
    X_train, y_test = generateSplitFromRatingLimit(X, test_ratio, min_limit)            #Split items into training and test items
    
    #TODO: How to make this shorter?
    train = []
    for user in X_train:
        for rating in X[user]:
            train.append(rating)

    for i in range(len(rating_splits)):
        test = []                                                                       #Add all ratings given by training users to training set       
        for y in y_test:                                                                #For each test item
            r = random.sample(range(len(X[y])), rating_splits[i])                       #Select a random subset of the ratings for the current user
            for j in range(len(X[y])):
                if j in r:
                    train.append(X[y][j])                                              #Add these ratings to the training set
                else:
                    test.append(X[y][j])                                             #Add the remaining ratings to the test set
        helpers.writeRatingsToFile('./%s_train%d.txt' %(prefix, i+1), train, '\t')
        helpers.writeRatingsToFile('./%s_test%d.txt' %(prefix, i+1), test, '\t')
                
  
def generateColdStartSystemSplits(ratings, test_ratio, ratios, time_stamps = False):
    """
    Generate splits for cold-start system evaluation
        
    path: filepath
    test_ratio: percentage of ratings set aside for testing
    train_ratios: Percentage of training data used for each split
    
    """   
        
    if not time_stamps:
        num_ratings = len(ratings)                                                                #Read ratings 
        r = random.sample(range(len(ratings)), int(test_ratio*len(ratings)))                      #Randomly select test ratings
        y_test = [ratings[i] for i in r]                                                          #Put ratings in testset
        X_pool = [i for j, i in enumerate(ratings) if j not in r]                                 #Put the remaining in the testset
        for i in range(len(ratios)):                                                              #For each training ratio supplied
            X_train = generateDatasetSplit(X_pool, ratios[i], num_ratings)                        #Generate a split of size ratios[i]
            helpers.writeRatingsToFile('./system_train%d.txt' %(i+1), X_train, delimiter='\t')
        helpers.writeRatingsToFile('./system_test.txt', y_test, delimiter='\t')
           
    else: ### TODO - Testing ###                                            
        ratings = sorted(ratings, key=lambda ratings: ratings[3], reverse=True)                   #Sort ratings based on timestamps, the freshest being 'on top'
        num_test_ratings = int(len(ratings)*test_ratio)                                           #Number of ratings to use for testing
        y_test = ratings[-num_test_ratings:]                                                      #Put freshest ratings in the testset
        X_pool = ratings[:-num_test_ratings]                                                      #Put the remainding in the training set pool
        for i in range(len(ratios)):                                                              #For each training ratio supplied
            X_train = generateDatasetSplit(X_pool, ratios[i])                                     #Generate a split of size ratios[i]
            helpers.writeRatingsToFile('./system_train%d.txt' %(i+1), X_train, '\t')
        helpers.writeRatingsToFile('./system_test.txt', y_test, delimiter='\t')
       
    
def generateDatasetSplit(trainingset, ratio, num_total_ratings, rand=True):
    '''
    Function for extracting a random subset of 
    size ratio*num_total_ratings from the training set.
    
    E.g. when the entire dataset has 1000 ratings and you do a 80:20 tranining-test split
    Given a ratio of 0.5 this function will extract 1000*0.5=500 ratings from the 800
    ratings of the training set
    
    '''
    
    if rand:
        r = random.sample(range(len(trainingset)), int(ratio*num_total_ratings))
        split = [trainingset[i] for i in r]
    else:
        split = trainingset[:int(ratio*num_total_ratings)]
            
    return split

 
def generateSplitFromRatingLimit(X, ratio, limit):
    '''
    Function for selecting test items or users where the
    limit specifies the minimum number of ratings required
    for an item or user to be used for testing
    '''
    
    train = []
    test = []
    
    for x in X:
        if len(X[x]) < limit:
            train.append(x)
        else:
            test.append(x)

    test_item_count = ratio*len(X)

    if test_item_count > len(test):
        print('Error: Not enough items/users with sufficient ratings')

    while len(test) > test_item_count :
        r = random.randint(0, len(test)-1)
        train.append(test[r])
        del test[r]
    
    return train, test
            
#generateColdStartSplits('./datasets/blend.txt', 'user', 0.1, [10, 15, 20])
#generateColdStartSplits('../../datasets/blend.txt', 'item', 0.02, [5, 10, 15])
#generateColdStartSystemSplits('../../datasets/bookcrossing.csv', 0.20, [0.4, 0.6, 0.8], False)  
    
    
        
        
           