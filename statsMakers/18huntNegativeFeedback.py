import datetime
import sys
import argparse
import helpers
from bson import Binary, Code

parser = argparse.ArgumentParser(description='Time spent on item before action is taken, and what action.')
parser.add_argument('-sc', type=str, default="sessions")
args = parser.parse_args()

col = helpers.getCollection(args.sc)

print ("Collection used: ", args.sc)
print ("")

def main():
    findTimeFor("product_detail_clicked")

def findTimeFor(action):
    users = col.distinct('user_id')
    total = len(users)
    count = 0
    globalTot = 0
    zeroC = 0
    e = open("ignoreTime" + '.csv','w')
    wtf = 0
    for user in users:
        userEvents = col.find({'user_id':user}).sort('ts',1)
        avgViewTimeOnIgnoredItem = 0
        viewTimeStart = -1
        viewedItem = ''
        viewedItemSession = -1
        c = 0

        for event in userEvents:
            # print ("%s - %s" % (event['event_id'],event['ts']))
            if event['event_id'] == action:
                viewTimeStart = event['ts']
                viewedItem = event['product_id']
                viewedItemSession = event['session']
            if viewTimeStart != -1 and event['session'] == viewedItemSession and event['product_id'] != viewedItem:
                avgViewTimeOnIgnoredItem += (event['ts'] - viewTimeStart)
                viewTimeStart = -1
                viewedItemSession = -1
            c += 1

        # if avgViewTimeOnIgnoredItem == 0:
        #     sys.exit()
        # for sessionN in sessions:
        #     sessionEvents = col.find({'user_id':user,'session':sessionN})
        #     for event in sessionEvents:
        #         continue
                # print (event)
        if avgViewTimeOnIgnoredItem > 0:
            globalTot += avgViewTimeOnIgnoredItem/c
            e.write("uid" + str(user) + "," + str(avgViewTimeOnIgnoredItem/c) + "\n")
            wtf += 1
            # print (wtf)
        else:
            zeroC += 1
        # print (avgViewTimeOnIgnoredItem)
        count += 1
        helpers.printProgress(count,total)
    print ()
    print (globalTot/(count-zeroC))
    print (wtf)
    print (zeroC)
    print (count)
    print (globalTot)
    e.close()

    # 6062.000959310428
    # 623
    # 1656
    # 6262046.990967672

    # purchsedList = col.find({'event_id':'product_purchase_intended'})
    # wantedList = col.find({'event_id':'product_wanted'})
if __name__ == "__main__":
    main()
