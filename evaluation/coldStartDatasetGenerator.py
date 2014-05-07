"""

#############################################################################
A collection of functions for generating cold-start evaluation dataset splits
#############################################################################

"""

import csv
import random

def generateColdStartUserSplits(path, test_ratio, num_ratings = 0):
    """
    
    Generates splits for cold-start user evaluation similarly as described in:

    Matchbox: Large Scale Bayesian Recommendations
    Addressing cold-start problem in recommendation systems
    Getting to Know You: Learning New User Preferences in Recommender Systems
    
    Inputs:
    
        path:           Path of the original rating file
        test_ratio:     Percentage of users set aside for testing
        num_ratings:    [List] Number of ratings used for training for the test users for each split
    
    E.g. When setting the test_ratio = 0.1 we create two disjoint sets and set aside 10% of the users for testing and use the remaining 90% to train the model
    By using four splits with the default number of ratings we generate 4 training and test sets
    For training-test set one we train the model using 5 ratings for each test user and try to predict their remaining ratings, for set two we use 10...
    
    """
    
    #TODO - Add some checks, robustness
    #TODO - Add support for timestamps   
    
    #If number of ratings not specified use default: [5,10,15,20]
    if not num_ratings:
        for i in range(4):
            num_ratings.append(5*(i+1))
            
    ratings = []
    
    #Read ratings from file
    with open(path, 'r') as dat:
        reader =  csv.reader(dat, delimiter='\t')
        #reader.next()    #Skip Header
        for rating in reader:
            ratings.append(rating)  
    
    users = dict()
    
    #Build dictionary of users and ratings
    for rating in ratings:
        if rating[0] in users:
            users[rating[0]].append(rating)
        else:
            users[rating[0]] = list()
            users[rating[0]].append(rating)
            
    #Minumum number of ratings required for test users
    min_ratings = num_ratings[-1] + 5
    
    test_users = []
    train_users = []
    
    #Split users into training users and test users
    for user in users:
        if len(users[user]) >= min_ratings:
            test_users.append(user)
        else:
            train_users.append(user)
    
    #Number of users set aside for testing
    num_test_users = int(len(users)*test_ratio)
    
    if num_test_users > len(test_users):
        print('Warning: We do not have enough users with sufficient ratings')
        return
    
    #Until we have the desired number of test-users
    #Move the ones we have extra to the training set
    while len(test_users) > num_test_users:
        index = random.randint(0, len(test_users)-1)
        train_users.append(test_users[index])
        del test_users[index]
        
    #Generate the training and test sets
    for i in range(len(num_ratings)):
        
        train = []
        test = []        

        #Add all the ratings given by training users to training set
        for user in train_users:
            for rating in users[user]:
                train.append(rating)
                   
        for user in test_users:
            #Return a list of num_ratings[i] numbers selected from the ratings given by a user, without duplicates.
            random_ratings = random.sample(range(len(users[user])), num_ratings[i])
            #Iterate through the ratings given by the user
            for j in range(len(users[user])):
                #If the rating was selected by the random function, put it in the training set
                if j in random_ratings:
                    train.append(users[user][j])
                #If not, put it in the test set
                else:
                    test.append(users[user][j])
        
        #Write test and training sets to file
        with open('./Datasets/user_train%d.txt' %(i+1), 'wb') as trainfile:
            writer =  csv.writer(trainfile, delimiter='\t')
            writer.writerows(train)

        with open('./Datasets/user_test%d.txt' %(i+1), 'wb') as testfile:
            writer =  csv.writer(testfile, delimiter='\t')
            writer.writerows(test)
                

def generateColdStartItemSplits(path, test_ratio, num_ratings = 0):
    """
    
    Generates splits for cold-start item evaluation
    
    Inputs:
    
        path:           Path of the original rating file
        test_ratio:     Percentage of items set aside for testing
        num_ratings:    [List] Number of ratings used for training for the test items for each split
    
    E.g. When setting the test_ratio = 0.1 we create two disjoint sets and set aside 10% of the items for testing and use the remaining 90% to train the model
    By using four splits with the default number of ratings we generate 4 training and test sets
    For training-set 1 we train the model using 5 ratings for each test item and try to predict their remaining ratings, for set two we use 10 and so on.
    
    """
    
    #TODO - Add some checks, robustness
    #TODO - Add support for timestamps
    
    
    #If number of ratings not specified use default: [5, 10, 15, 20]
    #Starting at 5, increase by 5 for each successive split
    if not num_ratings:
        for i in range(4):
            num_ratings.append(5*(i+1))   
            
    ratings = []
    
    #Read ratings from file
    with open(path, 'r') as dat:
        reader =  csv.reader(dat, delimiter='\t')
        #reader.next()    #Skip Header
        for rating in reader:
            ratings.append(rating)  
    
    items = dict()
    
    #Build dictionary of users and ratings
    for rating in ratings:
        if rating[1] in items:
            items[rating[1]].append(rating)
        else:
            items[rating[1]] = list()
            items[rating[1]].append(rating)
            
    #Minumum number of ratings required for test users
    min_ratings = num_ratings[-1] + 5
    
    test_items = []
    train_items = []
    
    #Split users into training users and test users
    for item in items:
        if len(items[item]) >= min_ratings:
            test_items.append(item)
        else:
            train_items.append(item)
    
    #Number of users set aside for testing
    num_test_items = int(len(items)*test_ratio)
    
    if num_test_items > len(test_items):
        print('Error: We do not have enough items with sufficient ratings')
        return
    
    #Until we have the desired number of test-users
    #Move the ones we have extra to the training set
    while len(test_items) > num_test_items:
        index = random.randint(0, len(test_items)-1)
        train_items.append(test_items[index])
        del test_items[index]
        
    #Generate the training and test sets
    for i in range(len(num_ratings)):
        
        train = []
        test = []        

        #Add all the ratings given by training users to training set
        for user in train_items:
            for rating in items[user]:
                train.append(rating)
                   
        for user in test_items:
            #Return a list of num_ratings[i] numbers selected from the ratings given by a user, without duplicates.
            random_ratings = random.sample(range(len(items[user])), num_ratings[i])
            #Iterate through the ratings given by the user
            for j in range(len(items[user])):
                #If the rating was selected by the random function, put it in the training set
                if j in random_ratings:
                    train.append(items[user][j])
                #If not, put it in the test set
                else:
                    test.append(items[user][j])
        
        #Write test and training sets to file
        with open('./Datasets/item_train%d.txt' %(i+1), 'wb') as trainfile:
            writer =  csv.writer(trainfile, delimiter='\t')
            writer.writerows(train)

        with open('./Datasets/item_test%d.txt' %(i+1), 'wb') as testfile:
            writer =  csv.writer(testfile, delimiter='\t')
            writer.writerows(test)
    
def generateColdStartSystemSplits(path, test_ratio, train_ratios, time_stamps = False):
    """
    
    Generate splits for cold-start system evaluation similarly as described in:
    
    Regression-based Latent Factor Models
    
    Inputs:
        
        path:                Path of the original rating file
        test_ratio:          Percentage of ratings set aside for testing
        train_ratios:        Percentage of training examples for each split. E.g. [0.35, .60, .75, 1.0] if the test_ratio is set to 0.75 
    
    """
    
    ratings = []
    
    with open(path, 'r') as dat:
        reader =  csv.reader(dat, delimiter='\t')
        #reader.next()    #Skip Header
        for rating in reader:
            ratings.append(rating)
    
    test = []
    
    #If not time_stamps are supplied
    if not time_stamps:
        
        #Select test ratings at random
        random_ratings = random.sample(range(len(ratings)), int(test_ratio*len(ratings)))
        for rating in random_ratings:
            test.append(ratings[rating])
        
        #Remove the ratings used for the test-set
        ratings = [i for j, i in enumerate(ratings) if j not in random_ratings]
    
        #For each training ratio supplied
        for i in range(len(train_ratios)):
            
            train = []
            #Pick out the supplied ratio of ratings at random
            random_ratings = random.sample(range(len(ratings)), int(train_ratios[i]*len(ratings)))
            for rating in random_ratings:
                train.append(ratings[rating])
            
            with open('./Datasets/system_train%d.txt' %(i+1), 'wb') as trainfile:
                writer =  csv.writer(trainfile, delimiter='\t')
                writer.writerows(train)

        with open('./Datasets/system_test.txt', 'wb') as testfile:
                writer =  csv.writer(testfile, delimiter='\t')
                writer.writerows(test)
           
   
    ##### TODO - Testing of timestamps function #####
    if time_stamps:
        
        #Sort ratings based on timestamps, the newest being 'on top'
        ratings = sorted(ratings, key=lambda ratings: ratings[3], reverse=True)
        num_test_ratings = int(len(ratings)*test_ratio)
        #Extract the lastest ratings based on timestamps for testing
        test = ratings[-num_test_ratings:]
        ratings = ratings[:-num_test_ratings]
        
        for i in range(len(train_ratios)):
            
            train = []
            #Pick out the supplied ratio of ratings at random
            random_ratings = random.sample(range(len(ratings)), int(train_ratios[i]*len(ratings)))
            for rating in random_ratings:
                train.append(ratings[rating])
            
            with open('./Datasets/system_train%d.txt' %(i+1), 'wb') as trainfile:
                writer =  csv.writer(trainfile, delimiter='\t')
                writer.writerows(train)

        
        with open('./Datasets/system_test.txt', 'wb') as testfile:
                writer =  csv.writer(testfile, delimiter='\t')
                writer.writerows(test)
    
        
        
            
generateColdStartUserSplits('./Datasets/blend.txt', 0.1, [5, 10, 15, 20])
#generateColdStartItemSplits('./Datasets/blend.txt', 0.05, [5, 10, 15])
#generateColdStartSystemSplits('./Datasets/blend.txt', 0.25, [0.35, 0.6, 0.75, 1], False)  
    
    
        
        
           