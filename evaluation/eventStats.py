'''
Functions for event_type specific evaluation metrics

'''

import csv
import os
import helpers
from datetime import datetime

import map

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)

def readEventTypeData(filePath='../generated/event_type.txt'):
    
    eventData = []
    
    with open(filePath, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            eventData.append(row)
    return eventData
    
def getEventType(itemId, eventData):
    '''
    Return the eventType of an item
    '''
    
    for event in eventData:
        if int(itemId) == int(event[0]):
            return int(event[1])
        
    print('Warning: event_type could not be determined')
    return 0
    
def getActualItems(actual, userId):
    '''
    Return the items in the testset for a given user
    '''
    
    items = []
    
    for rating in actual:
        if int(rating[0]) == userId:
            items.append(rating[1])
            
    return items
    
def getActualStats(actual, eventData):
    '''
    Count the number of:
    purchases, wants and purchases in the testset
    '''
    
    counts = [0,0,0]
    
    for rating in actual:
        eventType = getEventType(rating[1], eventData)
        if eventType == 1:
            counts[0] += 1
        elif eventType == 2:
            counts[1] += 1
        elif eventType == 3:
            counts[2] += 1
            
    return counts

def getPredictionStats(actual, predicted, eventData, topk=20):
    '''
    Count the number of:
    clicks, wants and purchases of the top-k list of all users
    '''
    
    #actual = [1,1,1]
    
    counts = [0,0,0]
    users = helpers.buildDictByIndex(predicted, 0)
    
    for user in users:
        actualList = getActualItems(actual, int(user))
        for i in range(topk):
            if users[user][i][1] in actualList:
                eventType = getEventType(users[user][i][1], eventData)
                if eventType == 1:
                    counts[0] += 1
                elif eventType == 2:
                    counts[1] += 1
                elif eventType == 3:
                    counts[2] += 1
                
    return counts
            
            
            
def filterNonTestUsersFromPredicted(actual, predicted):
    '''
    Remove non test users from the prediction list
    '''
    
    users = []
    for rating in actual:
        users.append(int(rating[0])) 
    uniqueTestUsers = set(users)
    new_list = []
    users = helpers.buildDictByIndex(predicted, 0)
    for user in users:
        if int(user) in uniqueTestUsers:
            for rating in users[user]:
                new_list.append(rating)

    print('Filtered out %d non test user ratings' %(len(predicted)-len(new_list)))
    return new_list

def extractRatingsByEventType(actual, event_type, eventData):
    
    new_list = []
    
    for rating in actual:
        eventType = getEventType(rating[1], eventData)
        if eventType == event_type:
            new_list.append(rating)
       
    return new_list

 
def compute(actual, predicted, k):
    
    startTime = datetime.now()
    
    eventData = readEventTypeData()
    predicted = filterNonTestUsersFromPredicted(actual, predicted)
    actualCounts = getActualStats(actual, eventData)
    predictedCounts = getPredictionStats(actual, predicted, eventData, k)
    
    recall = [x/float(y) for x, y in zip(predictedCounts, actualCounts)]
    
    MAP_click_test = extractRatingsByEventType(actual, 1, eventData) 
    MAP_want_test = extractRatingsByEventType(actual, 2, eventData) 
    MAP_purchase_test = extractRatingsByEventType(actual, 3, eventData) 
    
    t, p = helpers.preprocessMAP(MAP_click_test, predictions, k)
    map_click_k = map.mapk(t, p, k)
    t, p = helpers.preprocessMAP(MAP_want_test, predictions, k)
    map_want_k = map.mapk(t, p, k)
    t, p = helpers.preprocessMAP(MAP_purchase_test, predictions, k)
    map_purchase_k = map.mapk(t, p, k)
    
    print(datetime.now()-startTime)
    
    '''
    print('*** RESULTS ***')
    print('Predicted list recall (true-positives')
    print(predictedCounts)
    print('Test list event distribution')
    print(actualCounts)
    print('Recall at %d' %k)
    print(recall)
    print('MAP at %d clicked: %.2f' %(k, map_click_k))
    print('MAP at %d wanted: %.2f' %(k, map_want_k))
    print('MAP at %d purchased: %.2f' %(k, map_purchase_k))
    '''
    
    results = predictedCounts
    results.extend(actualCounts)
    results.extend(recall)
    results.append(map_click_k)
    results.append(map_want_k)
    results.append(map_purchase_k)
    print(results)
    
    return results
    
    
### TESTING ### 
        
#import itemAverage
        
#train = helpers.readRatingsFromFile('../data/count_linear.txt.1.txt')
#test = helpers.readRatingsFromFile('../data/count_linear.txt.1.txt')
#predictions = itemAverage.mostPopular(train, test)

#compute(test, predictions, 100)
