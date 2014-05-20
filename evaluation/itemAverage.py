from collections import Counter
from collections import OrderedDict
from operator import itemgetter
import time
import helpers


def itemAverage(train, test):
    
    
    
    start = time.time()
    print('Generating item-average predictions...')
    
    ratingCounter = Counter()
    itemRatings = Counter()
    
    i = 0
    
    for rating in train:
        itemRatings[rating[1]] += rating[2]
        ratingCounter[rating[1]] += 1    
        
    
    itemRatings = {k: float(itemRatings[k])/ratingCounter[k] for k in itemRatings}   
    itemRatings = sorted(itemRatings.iteritems(), key=itemgetter(1), reverse=True)       
   
    predictions = []
    testUsers = helpers.buildDictByIndex(test, 0)
    print(itemRatings)
    
    for user in testUsers:
        for item in itemRatings:
            if not item[0] in testUsers[user]:
                predictions.append([user, item[0], item[1]])
                
    print('itemAverage used %d seconds to generate %d ratings' %(time.time()-start, len(predictions)))
    
    return predictions


def mostPopular(train, test):
    
    start = time.time()
    print('Generating item-average predictions...')
    
    ratingCounter = Counter()
    
    i = 0
    
    for rating in train:
        ratingCounter[rating[1]] += 1    
        
    ratingCounter = sorted(ratingCounter.iteritems(), key=itemgetter(1), reverse=True)       
   
    predictions = []
    testUsers = helpers.buildDictByIndex(test, 0)
    
    for user in testUsers:
        for item in ratingCounter:
            if not item[0] in testUsers[user]:
                predictions.append([user, item[0], 1.0])
                
    print('mostPopular used %d seconds to generate %d ratings' %(time.time()-start, len(predictions)))
    
    return predictions



