import datetime
import sys
import argparse
import helpers
from bson import Binary, Code

def main(sessDB='sessionsNew'):
    groups = makeGroups(sessDB)

    print (groups)
    timeSpans = [int(x['timespan']) for x in groups]
    counts = [int(x['count']) for x in groups]
    print (timeSpans)

def makeCSVFiles(groups):
    maxTimespan = 0
    maxItem = ''
    greaterThan1 = 0

    c = helpers.getCSVWriter("itemEventCount")
    c.writerow([ 'product_id', 'count' ])

    cts = helpers.getCSVWriter("timespanStats")
    cts.writerow([ 'product_id', 'timespan' ])

    cNts = helpers.getCSVWriter("timespanWithCountStats")
    cNts.writerow([ 'product_id', 'timespan', 'count' ])

    for item in groups:
        if item['timespan'] > maxTimespan:
            maxTimespan = item['timespan']
            maxItem = item['product_id']
        print (item)
        if (item['count'] > 1):
            greaterThan1 += 1

        c.writerow([ 'p' + str(int(item['product_id'])), int(item['count'])])
        cts.writerow([ 'p' + str(int(item['product_id'])), int(item['timespan']/(1000*60))])
        cNts.writerow([ 'p' + str(int(item['product_id'])), int(item['timespan']/(1000*60)), int(item['count'])])
    helpers.closeF()

def makeObjectForJson(groups):
    e = open("piss" + '.json','w')
    e.write("[\n")
    for item in groups:
        start = datetime.datetime.fromtimestamp(int(item['min'])/1000).strftime('%m/%d/%Y')
        end = datetime.datetime.fromtimestamp((int(item['max'])/1000)+(60*60*24)).strftime('%m/%d/%Y')
        e.write("['" + str(item['product_id']) + "', " + "new Date('" + start + "'), " + "new Date('" + end + "')],\n")
    e.write("]")
    e.close()

def makeGroups(sessDB):
    col = helpers.getCollection(sessDB)
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
        condition={'product_id':{'$ne':'NULL'}},
        reduce=reducer,
        initial={
            'count':0,
            'max':0,
            'min':13842573649850,
            'timespan':0,
            'avgTime':0
        }
    )
    return groups

if __name__ == "__main__":
    main()
