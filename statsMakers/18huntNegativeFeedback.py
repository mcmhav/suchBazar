import datetime
import sys
import argparse
import helpers
from bson import Binary, Code

parser = argparse.ArgumentParser(description='Time spent on item before action is taken, and what action.')
parser.add_argument('-sc', type=str, default="sessions")
parser.add_argument('-c', type=str, default="outMF.csv")
args = parser.parse_args()

col = helpers.getCollection(args.sc)

print ("Collection used: ", args.sc)
print ("Output file:     ", args.c)
print ("")

total = 0

showInterest = {
    'product_purchase_intended',
    'product_wanted'
}

def main():
    users = col.distinct('user_id')
    total = len(users)
    count = 0
    globalTot = 0
    zeroC = 0
    for user in users:
        userEvents = col.find({'user_id':user}).sort('ts',1)
        avgViewTimeOnIgnoredItem = 0
        viewTimeStart = -1
        viewedItem = ''
        viewedItemSession = -1
        c = 0
        for event in userEvents:
            # print ("%s - %s" % (event['event_id'],event['ts']))
            if event['event_id'] == "product_detail_clicked":
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
        else:
            zeroC += 1
        # print (avgViewTimeOnIgnoredItem)
        count += 1
        helpers.printProgress(count,total)
    print ()
    print (globalTot/(count-zeroC))
    print (zeroC)
    print (count)
    print (globalTot)

    # 6062.000959310428
    # 623
    # 1656
    # 6262046.990967672

    # purchsedList = col.find({'event_id':'product_purchase_intended'})
    # wantedList = col.find({'event_id':'product_wanted'})

    # iterateEventsAction(purchsedList)
    # iterateEventsAction(wantedList)


    reducer = Code("""
                    function (cur,result) {
                        if (cur.ts > result.max) {
                            result.max = cur.ts;
                        }
                        if (cur.ts < result.min) {
                            result.min = cur.ts;
                        }
                        result.count += 1;
                        result.timespan = result.max - result.min;
                        result.avgTime = result.timespan/result.count;
                    }
                   """)

    groups = col.group(
                           key={'user_id':1,'session':1},
                           condition={},
                           reduce=reducer,
                           initial={'count':0,'max':0,'min':13842573649850,'timespan':0,'avgTime':0}
                       )

def mr():
    mapper = Code(  """
        function () {
            values = {this.session, this.user_id, this.ts}
            emit(this, values)
        }
    """)

    reducer = Code( """
                    function (key, values) {
                        var total = 0;
                        for (var i = 0; i < values.length; i++) {
                            total += values[i];
                        }
                        return total;
                    }
                    """)
    result = col.map_reduce(mapper, reducer, "myresults")
    return result

def iterateEventsAction(eventList):
    totalTime = 0
    count = 0
    eventType = {}
    for purchase in eventList:
        preEvent = getEventBeforeAction(purchase)
        if preEvent == -1 or preEvent == {}:
            continue
        else:
            timeSpent = purchase['ts'] - preEvent['ts']
            totalTime = totalTime + timeSpent
            count += 1
            if not preEvent['event_id'] in eventType:
                eventType[preEvent['event_id']] = 0
            else:
                eventType[preEvent['event_id']] += 1
            # print(timeSpent)

    print (totalTime/count)
    print (eventType)

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
