'''
Functions for event_type specific evaluation metrics

'''

import csv
import os
import helpers
import sys

import map

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)

def readEventTypeData(filePath=ROOT_FOLDER + '/generated/event_type.txt'):

    eventData = []
    if not os.path.isfile(filePath):
      sys.stderr.write("File %s does not exist" % filePath)
      sys.exit(1)
    with open(filePath, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            eventData.append([int(row[0]), int(row[1]), int(row[2])])
    return eventData

def getEventType(userId, itemId, eventTypes):
    '''
    Return the eventType of an item
    Only return something if the item and user
    combination is in the log files
    '''

    if userId in eventTypes:
        for event in eventTypes[userId]:
            if int(itemId) == int(event[1]):
                return int(event[2])

    return 0

def getActualItems(actual, userId):
    '''
    Return the items in the testset for a given user
    '''

    items = []

    for rating in actual:
        if int(rating[0]) == int(userId):
            items.append(rating[1])

    return items

def getActualStats(actual, eventData):
    '''
    Count the number of:
    purchases, wants and purchases in the testset
    '''

    counts = [0,0,0]

    for user in actual:
        for rating in actual[user]:
            eventType = getEventType(user, rating[1], eventData)
            if eventType == 1:
                counts[0] += 1
            elif eventType == 2:
                counts[1] += 1
            elif eventType == 3:
                counts[2] += 1


    return counts

def itemInList(item, list):

    for i in list:
        if int(i[1]) == int(item[1]):
            return True
    return False

def getPredictionStats(actual, predicted, eventData, topk=20):

    counts = [0,0,0]

    for key, p_user_ratings in predicted.iteritems():
        for a_user_ratings in actual.get(key, []):
            for p_rating in p_user_ratings[:min(len(p_user_ratings), topk)]:
                if a_user_ratings[1] == p_rating[1]:
                    eventType = getEventType(key, p_rating[1], eventData)
                    if eventType > 0 and eventType < 4:
                        counts[eventType-1] += 1

    return counts



def filterNonTestUsersFromPredicted(actual, predicted):
    '''
    Remove non test users from the prediction list
    '''

    for user in actual:
        if not user in predicted:
            predicted.pop(user, None)

    return predicted


def extractRatingsByEventType(actual, eventData):

    events = {}

    for user in actual:
        for rating in actual[user]:
            eventType = getEventType(user, rating[1], eventData)
            if not eventType in events:
                events[eventType] = list()
            events[eventType].append(rating)

    return events

def compute_recall(actual, predicted):

    recall = []
    for x,y in zip(predicted, actual):
        if x != 0 and y != 0:
            recall.append(x/float(y))
        else:
            recall.append(0)
    return recall

def generateResultList(aCounts, pCounts, recall, map_c, map_w, map_p):

    if aCounts[0] == 0:
        map_c = 0
    if aCounts[1] == 0:
        map_w = 0
    if aCounts[2] == 0:
        map_p = 0

    result = aCounts
    result.extend(pCounts)
    result.extend(recall)
    result.append(map_c)
    result.append(map_w)
    result.append(map_p)
    return result

def preprocessMeanAvgPrecision(events, predicted, k):

    test = []
    predictions = []

    for user, user_pred_ratings in predicted.iteritems():
        #predictions.append(user_ratings)
        user_test_items = []
        user_pred_items = []

        for rating in events:
            if rating[0] == user:
                user_test_items.append(rating[1])

        #If the user is in the test set
        if len(user_test_items) > 0:

            for rating in user_pred_ratings[:min(len(user_pred_ratings), k)]:
                user_pred_items.append(rating[1])

            test.append(user_test_items)
            predictions.append(user_pred_items)

    return test, predictions

def compute(actual, predicted, k):

    eventData = readEventTypeData()
    eventData = helpers.buildDictByIndex(eventData, 0)

#     print (actual)
#     sys.exit()
#     actual = helpers.buildDictByIndex(actual, 0)
#     predicted = helpers.buildDictByIndex(predicted, 0)

    aCounts = getActualStats(actual, eventData)
    pCounts = getPredictionStats(actual, predicted, eventData, k)
    recall = compute_recall(aCounts, pCounts)

    events = extractRatingsByEventType(actual, eventData)

    t, p = preprocessMeanAvgPrecision(events[1], predicted, k)
    map_c = map.mapk(t, p, k)

    t, p = preprocessMeanAvgPrecision(events[2], predicted, k)
    map_w = map.mapk(t, p, k)

    t, p = preprocessMeanAvgPrecision(events[3], predicted, k)
    map_p = map.mapk(t, p, k)



    return generateResultList(aCounts, pCounts, recall, map_c, map_w, map_p)

### TESTING ###
#import itemAverage
#test = helpers.readRatingsFromFile('../generated/Data/test.txt')
#train = helpers.readRatingsFromFile('../generated/Data/t.txt')
#predictions = itemAverage.mostPopular(train ,test)


#compute(test, predictions,50)

