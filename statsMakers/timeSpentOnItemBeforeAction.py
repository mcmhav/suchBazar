import datetime
import sys
import argparse
import helpers
import math
from bson import Binary, Code
import numpy as np
import os.path

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.dirname(SCRIPT_FOLDER)
DATA_FOLDER = 'data'
folder = SCRIPT_FOLDER + '/' + DATA_FOLDER

if not os.path.exists(folder):
        os.makedirs(folder)

def main(sessDB='sessionsNew3',makeNew=False,show=False,save=False):
    col = helpers.getCollection(sessDB)
    capVal=12
    actionTime('product_purchase_intended',col,"before purchase",capVal=capVal,makeNew=makeNew,show=show,save=save)
    actionTime('product_wanted',col,"before want",capVal=capVal,makeNew=makeNew,show=show,save=save)

def actionTime(action,col,name,makeNew=False,capVal=0,save=False,show=True):
    cap = 2000
    maxBucket = 50

    if os.path.isfile(folder + '/' + action + '.csv') and not makeNew:
        userAverages = getActionFile(action)
    else:
        userAverages,buckets = makeUserAverage(action,cap,maxBucket,col)
        writeUserAverages(userAverages,action)
        # writeToFile(buckets,action)

    # print (buckets)
    # print (action)
    # plotFromUserAverages(userAverages)

    helpers.plotAverageSomething(
        userAverages,
        action,
        # title='Time looked at item ' + name,
        ylabel='Amount of Users',
        xlabel='View time ',
        show=show,
        capAtEnd=True,
        capVal=capVal,
        save=save
    )

# [70, 94, 78, 48, 43, 20, 28, 15, 12, 6, 12, 3, 6, 4, 2, 3, 4, 4, 0, 1]
# [array([ 0,  2,  4,  6,  8, 10, 12, 14, 16, 18, 20]), array([ 0,  6, 12, 18, 24, 30, 36, 42, 48, 54])]
# Distribution written to: /home/m/repos/suchBazar/../muchBazar/src/image/product_purchase_intendeddistribution.png
# lol
# [96, 112, 118, 104, 69, 59, 39, 24, 20, 12, 10, 4, 9, 3, 3, 3, 1, 4, 0, 1, 2, 1, 1]
# [array([ 0,  3,  6,  9, 12, 15, 18, 21, 24]), array([ 0,  9, 18, 27, 36, 45, 54, 63, 72, 81, 90])]

def makeUserAverage(action,cap,maxBucket,col):
    buckets = [0] * maxBucket
    count = 0
    users = col.distinct('user_id')
    total = len(users)
    userAverages = []
    for user in users:
        userAverage = 0
        actionList = col.find({'event_id':action,'user_id':user}).sort('ts',1)
        buckets,userAverage = iterateEventsAction(actionList,buckets,col,cap,maxBucket)
        count += 1
        if userAverage != 0:
            # print ('lol')
            userAverages.append(userAverage)
            # e.write("uid" + str(user) + "," + str(userAverage) + "\n")

        helpers.printProgress(count,total)
    return userAverages,buckets

def writeUserAverages(userAverages,action):
    e = open(folder + '/' + action + '.csv','w')
    for av in userAverages:
        e.write(str(av) + ", ")
    e.close()

def findCountOverAndUnderAVG(userAverages):
    avg = sum(userAverages)/len(userAverages)
    underC = 0
    overC = 0
    for ua in userAverages:
        if ua < avg:
            underC += 1
        else:
            overC += 1
    return underC,overC

def iterateEventsAction(eventList,buckets,col,cap,maxBucket):
    totalTime = 0
    count = 0
    eventType = {}
    total = eventList.count()

    for purchase in eventList:
        preEvent = getEventBeforeAction(purchase,col)
        if preEvent == -1 or preEvent == {}:
            continue
        else:
            timeSpent = purchase['ts'] - preEvent['ts']
            totalTime = totalTime + timeSpent
            count += 1

            # bucetLocation = math.floor(timeSpent/cap)
            # if bucetLocation > maxBucket:
            #     buckets[maxBucket-1] += 1
            # else:
            #     buckets[bucetLocation] += 1

            if not preEvent['event_id'] in eventType:
                eventType[preEvent['event_id']] = 1
            else:
                eventType[preEvent['event_id']] += 1
            # print(timeSpent)
    # print (totalTime/count)
    # print (eventType)
    buckets = []
    if count == 0:
        return (buckets,0)
    else:
        return (buckets,(totalTime/count))

def writeToFile(buckets,action):
    e = open(action + 'asodi.csv','w')
    for key, bucket in enumerate(buckets):
        e.write(str(key) + "," + str(bucket) + "\n")
    e.close()

def getEventBeforeAction(e,col):
    # 2892302.2136465325
    # {'product_wanted': 107, 'product_detail_clicked': 785}

    eventSession = col.find({
                            'session':e['session'],
                            'user_id':e['user_id'],
                            'ts':{'$lt':e['ts']}
                            }).sort('ts',-1).limit(1)
    # prev = {}
    for event in eventSession:
        # if e['event_id'] == event['event_id']:
        #     return -1
        return event
    #     print (event['ts'])
    #     if event == e:
    #         return prev
    #     prev = event
    # sys.exit()
    return -1

def getActionFile(action):
    e = open(folder + "/" + action + '.csv','r')
    line = e.readlines()
    e.close()
    userAverages = []
    for ua in line[0].split(','):
        try:
            userAverages.append(float(ua))
        except:
            print ('lol')
    return userAverages

if __name__ == "__main__":
    main()
