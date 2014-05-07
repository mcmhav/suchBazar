"""

#############################################################################
A collection of functions for generating cold-start evaluation dataset splits
#############################################################################

"""

import random
import numpy as np

def generateColdStartSplits(path, type, test_ratio, rating_splits = 0):
    """
    
    Generates splits for cold-start user/item evaluation, as described in:
   
    Matchbox: Large Scale Bayesian Recommendations,
    Addressing cold-start problem in recommendation systems,
    Getting to Know You: Learning New User Preferences in Recommender Systems
    
    path: filepath,
    type: split by "user" (0) or "item" (1),
    test_ratio: percentage of items used for testing,
    rating_splits: number test item ratings used for training for each split
    
    """
    
    #TODO - Make more robust & Add support for timestamps    
    index = False if type == 'user' else True
    
    if not rating_splits:                                                               #If rating_splits are not defined
        rating_splits = [5, 10, 15]                                                     #Initialize as default
          
    ratings = np.genfromtxt(open(path, 'r'), delimiter='\t', dtype='int, int, float')   #Read ratings from file  
    X = buildDictByIndex(ratings, index)                                                #Build dictionary where item id is used as key
    min_limit = rating_splits[-1] + 5                                                   #Minimum number of ratings for test users
    X_train, y_test = generateSplitFromRatingLimit(X, test_ratio, min_limit)            #Split items into training and test items
    for i in range(len(rating_splits)):
        train = X_train                                                            #Add all ratings given by training users to training set       
        for y in y_test:                                                           #For each test item
            r = random.sample(range(len(X[y])), rating_splits[i])                  #Select a random subset of rating_splits[i] ratings
            train = np.array([ratings[i] for i in r])                              #Add these ratings to the training set
            test = np.array([i for j, i in enumerate(ratings) if j not in r])      #Add the remaining ratings to the test set
        
        np.savetxt('./train%d.txt' %(i+1), train,fmt='%d %d %.3f', delimiter='\t') #Write the resulting test and training
        np.savetxt('./test%d.txt' %(i+1), test, fmt='%d %d %.3f', delimiter='\t')  #sets to file
                
  
def generateColdStartSystemSplits(path, test_ratio, ratios, time_stamps = False):
    """
    
    Generate splits for cold-start system evaluation similarly as described in:
    
    Regression-based Latent Factor Models
        
    path: filepath
    test_ratio: percentage of ratings set aside for testing
    train_ratios: Percentage of training data used for each split
    
    """   
        
    if not time_stamps:
        ratings = np.genfromtxt(open(path, 'r'), delimiter='\t', dtype='int, int, float')         #Read ratings 
        r = random.sample(range(len(ratings)), int(test_ratio*len(ratings)))                      #Randomly select test ratings
        y_test = np.array([ratings[i] for i in r])                                                #Put ratings in testset
        X_pool = np.array([i for j, i in enumerate(ratings) if j not in r])                       #Put the remaining in the testset
        for i in range(len(ratios)):                                                              #For each training ratio supplied
            X_train = generateDatasetSplit(X_pool, ratios[i])                                     #Generate a split of size ratios[i]
            np.savetxt('./system_train%d.txt' %(i+1), X_train,  fmt='%d %d %.3f', delimiter='\t') #Write training split to file
        np.savetxt('./system_test.txt', y_test, fmt='%d %d %.3f', delimiter='\t')                 #Write testset to file
           
    else: ### TODO - Testing ###
        ratings = np.genfromtxt(open(path, 'r'), delimiter='\t', dtype='int, int, float')         #TODO add string/timestamp as fourth column
        ratings = sorted(ratings, key=lambda ratings: ratings[3], reverse=True)                   #Sort ratings based on timestamps, the freshest being 'on top'
        num_test_ratings = int(len(ratings)*test_ratio)                                           #Number of ratings to use for testing
        y_test = ratings[-num_test_ratings:]                                                      #Put freshest ratings in the testset
        X_pool = ratings[:-num_test_ratings]                                                      #Put the remainding in the training set pool
        for i in range(len(ratios)):                                                              #For each training ratio supplied
            X_train = generateDatasetSplit(X_pool, ratios[i])                                     #Generate a split of size ratios[i]
            np.savetxt('./system_train%d.txt' %(i+1), X_train,  fmt='%d %d %.3f', delimiter='\t') #Write training split to file
        np.savetxt('./system_test.txt', y_test, fmt='%d %d %.3f', delimiter='\t')                 #Write testset to file
    
def generateDatasetSplit(ratings, ratio, rand=True):
    
    if rand:
        r = random.sample(range(len(ratings)), int(ratio*len(ratings)))
        split = [ratings[i] for i in r]
    else:
        split = ratings[:int(ratio*len(ratings))]
            
    return split

 
def generateSplitFromRatingLimit(X, ratio, limit):
    
    train = []
    test = []
    test_item_count = ratio*len(X)
    
    for x in X:
        if x.size < limit:
            train.append(x)
        else:
            test.append(x)
    
    if test_item_count < len(test):
        print('Error: Not enough items/users with sufficient ratings')
            
    while len(test) > test_item_count :
        r = random.randint(0, len(test)-1)
        train.append(test[r])
        del test[r]
    
    return train, test

def buildDictByIndex(X, index=0):
    
    d = dict()
    
    for x in X:
        if x[index] in d:
            d[x[index]].append(x)
        else:
            d[x[index]] = list()
            d[x[index]].append(x)
            
    return d            
            
generateColdStartSplits('../../datasets/blend.txt', 'user', 0.1, [5, 10, 15, 20])
#generateColdStartSplits('./Datasets/blend.txt', 'item', 0.1, [5, 10, 15, 20])
#generateColdStartSystemSplits('../../datasets/blend.txt', 0.25, [0.35, 0.6, 0.75, 1], False)  
    
    
        
        
           