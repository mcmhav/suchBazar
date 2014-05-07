import datetime
import sys
import argparse
import helpers
import math
from bson import Binary, Code

parser = argparse.ArgumentParser(description='Time spent on item before action is taken, and what action.')
parser.add_argument('-sc', type=str, default="sessions")
args = parser.parse_args()

col = helpers.getCollection(args.sc)

print ("Collection used: ", args.sc)
print ("")


def main():
    actionTime('product_purchase_intended')
    actionTime('product_wanted')

    # 15074.550855991944
    # {
    #     'product_wanted': 103,
    #     'product_detail_clicked': 767,
    #     'product_purchase_intended': 120
    # }
    # 19939.903638814016
    # {
    #     'activity_clicked': 11,
    #     'storefront_clicked': 16,
    #     'around_me_clicked': 4,
    #     'user_logged_in': 5,
    #     'featured_storefront_clicked': 0,
    #     'stores_map_clicked': 45,
    #     'product_detail_clicked': 1058,
    #     'product_purchase_intended': 184,
    #     'app_started': 33,
    #     'product_wanted': 117,
    #     'store_clicked': 0
    # }

    # 19833.43308309604
    # {
    #     'around_me_clicked': 13,
    #     'featured_storefront_clicked': 47,
    #     'app_started': 277,
    #     'featured_collection_clicked': 67,
    #     'stores_map_clicked': 40,
    #     'product_purchase_intended': 39,
    #     'activity_clicked': 4,
    #     'friend_invited': 0,
    #     'product_detail_clicked': 1847,
    #     'user_logged_in': 9,
    #     'storefront_clicked': 1095,
    #     'store_clicked': 1,
    #     'product_wanted': 4274
    # }

def actionTime(action):
    users = col.distinct('user_id')
    buckets = [0] * 102

    count = 0
    total = len(users)
    e = open(action + 'average.csv','w')
    for user in users:
        userAverage = 0
        actionList = col.find({'event_id':action,'user_id':user}).sort()
        buckets,userAverage = iterateEventsAction(actionList,buckets)
        count += 1
        if userAverage != 0:
            e.write("uid" + str(user) + "," + str(userAverage) + "\n")
        helpers.printProgress(count,total)

    e.close()
    writeToFile(buckets,action)

def iterateEventsAction(eventList,buckets):
    totalTime = 0
    count = 0
    eventType = {}
    total = eventList.count()

    for purchase in eventList:
        preEvent = getEventBeforeAction(purchase)
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

def getEventBeforeAction(e):
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
