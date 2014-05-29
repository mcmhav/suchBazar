import datetime
import sys
import argparse
import helpers
import math
from bson import Binary, Code



def main(sessDB='sessionsNew'):
    col = helpers.getCollection(sessDB)
    actionTime('product_purchase_intended',col)
    actionTime('product_wanted',col)

def actionTime(action,col):
    users = col.distinct('user_id')
    buckets = [0] * 102

    count = 0
    total = len(users)
    for user in users:
        userAverage = 0
        actionList = col.find({'event_id':action,'user_id':user}).sort('ts',1)
        buckets,userAverage = iterateEventsAction(actionList,buckets,col)
        count += 1
        if userAverage != 0:
            print ('lol')
        helpers.printProgress(count,total)

    print (buckets)
    print (action)

    writeToFile(buckets,action)

def iterateEventsAction(eventList,buckets,col):
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

            bucetLocation = math.floor(timeSpent/1000)
            if bucetLocation > 100:
                buckets[101] += 1
            else:
                buckets[bucetLocation] += 1

            if not preEvent['event_id'] in eventType:
                eventType[preEvent['event_id']] = 1
            else:
                eventType[preEvent['event_id']] += 1
            # print(timeSpent)
    # print (totalTime/count)
    # print (eventType)
    if count == 0:
        return (buckets,0)
    else:
        return (buckets,(totalTime/count))

def writeToFile(buckets,action):
    e = open(action + '.csv','w')
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

if __name__ == "__main__":
    main()
