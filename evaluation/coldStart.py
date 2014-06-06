"""
A collection of functions for generating cold-start evaluation dataset splits

The GenerateColdStartSplits is similar to the approaches described in:
    -    Matchbox: Large Scale Bayesian Recommendations,
    -    Addressing cold-start problem in recommendation systems,
    -    Getting to Know You: Learning New User Preferences in Recommender Systems

The generateColdStartSystemSplits function is similar to the approach described in:
    -    Regression-based Latent Factor Models

"""

import random
import helpers
import os
import filterbots as fb
from operator import itemgetter

#Ratings are written to the following folder
SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)
SPLITS_FOLDER = 'splits'
GENERATED_LOCATION = 'generated'
folder = ROOT_FOLDER + '/' + GENERATED_LOCATION + '/' + SPLITS_FOLDER

if not os.path.exists(folder):
        os.makedirs(folder)

def generateColdStartSplits(filename, ratings, type, test_ratio, rating_limit, featurefile='/', rating_splits = [0.10, 0.40, 0.75], time_stamps=False, fbots=False):
    """
    Generates splits for cold-start user/item evaluation:
    ratings: list of ratings,
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

    if time_stamps == True:
        if(len(ratings[0]) < 4):
            print('Warning: No timestamps found')
    
    X = helpers.buildDictByIndex(ratings, index)                                        #Build dictionary where item id is used as key                                                  #Minimum number of ratings for test users
    X_train, y_test = generateSplitFromRatingLimit(X, test_ratio, rating_limit)         #Split items into training and test items
    #TODO: How to make this shorter?
    X_pool = []
    for user in X_train:
        for rating in X[user]:
            X_pool.append(rating)

    for i in range(len(rating_splits)):
        train = X_pool
        test = []                                                                       #Add all ratings given by training users to training set
        for y in y_test:                                                                #For each test item
            if time_stamps:
                r = selectRatingsByTimeStamp(X[y], rating_splits[i])
            else:
                r = random.sample(range(len(X[y])), int(rating_splits[i]*len(X[y])))                  #Select a random subset of the ratings for the current user
                #r = selectTopRatings(X[y], rating_splits[i])
            for j in range(len(X[y])):
                if j in r:
                    train.append(X[y][j])                                              #Add these ratings to the training set
                else:
                    test.append(X[y][j])                                             #Add the remaining ratings to the test set
        
        num_ratings = len(train)                       
        if fbots:
            train = fb.addFilterBotRatings(train, featurefile, fbots)
        print('Added', len(train)-num_ratings, 'filterbot ratings', type, fbots, time_stamps)
        helpers.writeRatingsToFile('%s/%s_%strain%d.txt' % (folder, filename,  prefix, i+1), train, '\t')
        helpers.writeRatingsToFile('%s/%s_%stest%d.txt' % (folder,filename, prefix, i+1), test, '\t')


def generateColdStartSystemSplits(filename, ratings, test_ratio, featurefile, ratios, time_stamps = False, fbots=False):
    """
    Generate splits for cold-start system evaluation

    path: filepath
    test_ratio: percentage of ratings set aside for testing
    train_ratios: Percentage of training data used for each split

    """
    if time_stamps == True:
        if(len(ratings[0]) < 4):
            print('Warning: No timestamps found')

    num_ratings = len(ratings)
    if not time_stamps:                                                                           #Read ratings
        r = random.sample(range(len(ratings)), int(test_ratio*len(ratings)))                      #Randomly select test ratings
        y_test = [ratings[i] for i in r]                                                          #Put ratings in testset
        X_pool = [i for j, i in enumerate(ratings) if j not in r]                                 #Put the remaining in the testset
        for i in range(len(ratios)):                                                              #For each training ratio supplied
            X_train = generateDatasetSplit(X_pool, ratios[i], num_ratings)                        #Generate a split of size ratios[i]
            num_ratings = len(X_train) 
            if fbots:
                X_train = fb.addFilterBotRatings(X_train, featurefile, fbots)
            print('Added', len(X_train)-num_ratings, 'filterbot ratings', 'system', fbots, time_stamps)
            helpers.writeRatingsToFile('%s/%s_systemtrain%d.txt' %(folder, filename, i+1), X_train, delimiter='\t')
        helpers.writeRatingsToFile('%s/%s_systemtest.txt' %(folder, filename), y_test, delimiter='\t')

    else:
        ratings = sorted(ratings, key=itemgetter(3), reverse=True)                                #Sort ratings based on timestamps, the freshest being 'on top'
        num_test_ratings = int(len(ratings)*test_ratio)                                           #Number of ratings to use for testing
        y_test = ratings[-num_test_ratings:]                                                      #Put freshest ratings in the testset
        X_pool = ratings[:-num_test_ratings]                                                      #Put the remainding in the training set pool
        for i in range(len(ratios)):                                                              #For each training ratio supplied
            X_train = generateDatasetSplit(X_pool, ratios[i], num_ratings)                               #Generate a split of size ratios[i]
            num_ratings = len(X_train) 
            if fbots:
                X_train = fb.addFilterBotRatings(X_train, featurefile, fbots)
            print('Added', len(X_train)-num_ratings, 'filterbot ratings', 'system', fbots, time_stamps)
            helpers.writeRatingsToFile('%s/%s_systemtrain%d.txt' %(folder, filename, i+1), X_train, delimiter='\t')
        helpers.writeRatingsToFile('%s/%s_systemtest.txt' %(folder, filename), y_test, delimiter='\t')


def generateDatasetSplit(trainingset, ratio, num_total_ratings, rand=True):
    '''
    Function for extracting a random subset of
    size ratio*num_total_ratings from the training set.

    E.g. when the entire dataset has 1000 ratings and you do a 80:20 tranining-test split
    Given a ratio of 0.5 this function will extract 1000*0.5=500 ratings from the 800
    ratings of the training set

    '''
 
    if rand:
        #Alt 1:
        random.shuffle(trainingset)
        split = trainingset[:int(ratio*num_total_ratings)]
        #Alt 2 (Slow):
        #r = random.sample(range(len(trainingset)), int(ratio*num_total_ratings))
        #split = [trainingset[i] for i in r]
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

def selectRatingsByTimeStamp(ratings, num_ratings):
    '''
    Select the num_ratings oldest ratings
    Returns the index(s) in the users rating list
    '''

    selected = []
    r = []

    for i in range(len(ratings)):
        selected.append([i, ratings[i][3]])

    selected = sorted(selected, key=itemgetter(1), reverse=False)

    #If percentage of ratings used
    if num_ratings < 1.0:
        num_ratings = int(num_ratings*len(ratings))
        for i in range(num_ratings):
            r.append(selected[i][0])
    #If hard limits are used
    else:
        for i in range(num_ratings):
            r.append(selected[i][0])

    return r

def selectTopRatings(ratings, num_ratings):
    '''
    Select the num_ratings highest ratings
    Returns the index(s) in the users rating list
    '''

    selected = []
    r = []

    for i in range(len(ratings)):
        selected.append([i, ratings[i][2]])

    selected = sorted(selected, key=itemgetter(1), reverse=True)

    if num_ratings < 1:
        num_ratings = int(len(ratings)*num_ratings)

    for i in range(num_ratings):
        r.append(selected[i][0])

    return r





#generateColdStartSplits('./datasets/blend.txt', 'user', 0.1, [10, 15, 20])
#generateColdStartSplits('../../datasets/blend.txt', 'item', 0.02, [5, 10, 15])
#generateColdStartSystemSplits('../../datasets/bookcrossing.csv', 0.20, [0.4, 0.6, 0.8], False)





