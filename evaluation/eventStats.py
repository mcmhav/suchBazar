'''
Functions for event_type specific evaluation metrics

'''

import csv
import os
import helpers
import sys
from datetime import datetime

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
            eventData.append(row)
    return eventData

def getEventType(userId, itemId, eventData):
    '''
    Return the eventType of an item
    Only return something if the item and user
    combination is in the log files
    '''

    for event in eventData:
        if int(itemId) == int(event[1]) and int(userId) == int(event[0]):
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

    for rating in actual:
        eventType = getEventType(rating[0], rating[1], eventData)
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

    counts = [0,0,0]
    users = helpers.buildDictByIndex(predicted, 0)

    for user in users:
        actualList = getActualItems(actual, int(user))
        m = len(users[user])
        if m > topk:
            m = topk
        for i in range(m):
            if users[user][i][1] in actualList:
                eventType = getEventType(user, users[user][i][1], eventData)
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
        eventType = getEventType(rating[0], rating[1], eventData)
        if eventType == event_type:
            new_list.append(rating)

    print('Extracted %d ratings with eventType %d' %(len(new_list), event_type))
    return new_list

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


def compute(actual, predicted, k):

    startTime = datetime.now()

    eventData = readEventTypeData()
    predictions = filterNonTestUsersFromPredicted(actual, predicted)

    aCounts = getActualStats(actual, eventData)
    pCounts = getPredictionStats(actual, predicted, eventData, k)
    recall = compute_recall(aCounts, pCounts)

    MAP = extractRatingsByEventType(actual, 1, eventData)
    t, p = helpers.preprocessMAP(MAP, predictions, k)
    map_c = map.mapk(t, p, k)

    MAP = extractRatingsByEventType(actual, 2, eventData)
    t, p = helpers.preprocessMAP(MAP, predictions, k)
    map_w = map.mapk(t, p, k)

    MAP = extractRatingsByEventType(actual, 3, eventData)
    t, p = helpers.preprocessMAP(MAP, predictions, k)
    map_p = map.mapk(t, p, k)

    print(datetime.now()-startTime)

    print('*** RESULTS ***')
    print('Predicted list recall (true-positives)')
    print(pCounts)
    print('Test list event distribution')
    print(aCounts)
    print('Recall at %d' %k)
    print(recall)
    print('MAP at %d clicked: %.6f' %(k, map_c))
    print('MAP at %d wanted: %.6f' %(k, map_w))
    print('MAP at %d purchased: %.6f' %(k, map_p))

    return generateResultList(aCounts, pCounts, recall, map_c, map_w, map_p)


### TESTING ###

#import itemAverage
#train = helpers.readRatingsFromFile('../data/count_linear.txt.9.txt')
#test = helpers.readRatingsFromFile('../data/count_linear.txt.1.txt')
#predictions = itemAverage.mostPopular(train, test)
#compute(test, predictions, 20)

