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

def main():
    purchsedList = col.find({'event_id':'product_purchase_intended'})
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

    wantedList = col.find({'event_id':'product_wanted'})


    iterateEventsAction(purchsedList)
    iterateEventsAction(wantedList)


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
                           key={'product_id':1},
                           condition={},
                           reduce=reducer,
                           initial={'count':0,'max':0,'min':13842573649850,'timespan':0,'avgTime':0}
                       )

    # total = len(groups)
    # maxTimespan = 0
    # maxItem = ''
    # greaterThan1 = 0

    # e = open("piss" + '.json','w')
    # e.write("[\n")

    # c = helpers.getCSVWriter("itemEventCount")
    # c.writerow([ 'product_id', 'count' ])

    # cts = helpers.getCSVWriter("timespanStats")
    # cts.writerow([ 'product_id', 'timespan' ])

    # cNts = helpers.getCSVWriter("timespanWithCountStats")
    # cNts.writerow([ 'product_id', 'timespan', 'count' ])

    # for item in groups:
    #     if item['timespan'] > maxTimespan:
    #         maxTimespan = item['timespan']
    #         maxItem = item['product_id']
    #     print (item)
    #     if (item['count'] > 1):
    #         greaterThan1 += 1
    #     start = datetime.datetime.fromtimestamp(int(item['min'])/1000).strftime('%m/%d/%Y')
    #     end = datetime.datetime.fromtimestamp((int(item['max'])/1000)+(60*60*24)).strftime('%m/%d/%Y')
    #     e.write("['" + str(item['product_id']) + "', " + "new Date('" + start + "'), " + "new Date('" + end + "')],\n")
    #     c.writerow([ 'p' + str(int(item['product_id'])), int(item['count'])])
    #     cts.writerow([ 'p' + str(int(item['product_id'])), int(item['timespan']/(1000*60))])
    #     cNts.writerow([ 'p' + str(int(item['product_id'])), int(item['timespan']/(1000*60)), int(item['count'])])

    # print (maxTimespan)
    # print (maxItem)
    # print (greaterThan1)
    # e.write("]")

    # e.close()
    # helpers.closeF()
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
