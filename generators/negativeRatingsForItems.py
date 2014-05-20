import datetime
import sys
import argparse
import pymongo
# import helpers
from bson import Binary, Code

# col = helpers.getCollection("sessions")
client = pymongo.MongoClient()
db = client.mydb
col = db['sessions']

client = pymongo.MongoClient()
db = client.mydb
colWithNeg = db['negValues']

def main():
    findTimeFor("product_detail_clicked")

def findTimeFor(action):
    users = col.distinct('user_id')
    total = len(users)
    count = 0
    globalTot = 0
    zeroC = 0
    wtf = 0
    for user in users:
        userEvents = col.find({'user_id':user}).sort('ts',1)
        totalViewTimeOnIgnoredItem = 0
        viewTimeStart = -1
        viewedItem = ''
        viewedItemSession = -1
        prevEvent = ''
        c = 0

        for event in userEvents:
            # print ("%s - %s" % (event['event_id'],event['ts']))
            if event['event_id'] == action:
                viewTimeStart = event['ts']
                viewedItem = event['product_id']
                viewedItemSession = event['session']
                prevEvent = event
            if viewTimeStart != -1 and event['session'] == viewedItemSession and event['product_id'] != viewedItem:
                viewTime = event['ts'] - viewTimeStart
                totalViewTimeOnIgnoredItem += viewTime
                tmp = event
                if viewTime < 6000:
                    # consider event negative
                    tmp['event_id'] = 'Negative_event'
                colWithNeg.insert(tmp)
                viewTimeStart = -1
                viewedItemSession = -1
            else:
                colWithNeg.insert(event)

            c += 1

        # if totalViewTimeOnIgnoredItem == 0:
        #     sys.exit()
        # for sessionN in sessions:
        #     sessionEvents = col.find({'user_id':user,'session':sessionN})
        #     for event in sessionEvents:
        #         continue
                # print (event)
        if totalViewTimeOnIgnoredItem > 0:
            avgViewTimeOnIgnoredItem = totalViewTimeOnIgnoredItem/c
            globalTot += avgViewTimeOnIgnoredItem
            wtf += 1
            # print (wtf)
        else:
            zeroC += 1
        # print (avgViewTimeOnIgnoredItem)
        count += 1
        print ((count/total)*100)
        # helpers.printProgress(count,total)
    print ()
    print (globalTot/(count-zeroC))
    print (wtf)
    print (zeroC)
    print (count)
    print (globalTot)

    # 6062.000959310428
    # 623
    # 1656
    # 6262046.990967672

    # purchsedList = col.find({'event_id':'product_purchase_intended'})
    # wantedList = col.find({'event_id':'product_wanted'})
if __name__ == "__main__":
    main()
