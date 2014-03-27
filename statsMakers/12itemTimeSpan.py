import datetime
import sys
import argparse
import helpers
from bson import Binary, Code

parser = argparse.ArgumentParser(description='Timespan of each item.')
parser.add_argument('-sc', type=str, default="cleanedItems")
parser.add_argument('-c', type=str, default="outMF.csv")
args = parser.parse_args()

col = helpers.getCollection(args.sc)

print ("Collection used: ", args.sc)
print ("Output file:     ", args.c)
print ("")

total = 0

def main():
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

    total = len(groups)
    maxTimespan = 0
    maxItem = ''
    greaterThan1 = 0

    e = open("piss" + '.json','w')
    e.write("[\n")

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
        start = datetime.datetime.fromtimestamp(int(item['min'])/1000).strftime('%Y, %m, %d')
        end = datetime.datetime.fromtimestamp((int(item['max'])/1000)+(60*60*24)).strftime('%Y, %m, %d')
        e.write("['" + str(item['product_id']) + "', " + "new Date(" + start + "), " + "new Date(" + end + ")],\n")
        c.writerow([ 'p' + str(int(item['product_id'])), int(item['count'])])
        cts.writerow([ 'p' + str(int(item['product_id'])), int(item['timespan']/(1000*60))])
        cNts.writerow([ 'p' + str(int(item['product_id'])), int(item['timespan']/(1000*60)), int(item['count'])])

    print (maxTimespan)
    print (maxItem)
    print (greaterThan1)
    e.write("]")

    e.close()
    helpers.closeF()

if __name__ == "__main__":
    main()

# javascript/google fucks up jan - feb transition
# ['29778002.0', new Date(2014, 01, 31), new Date(2014, 02, 01)],
# ['24788050.0', new Date(2014, 01, 30), new Date(2014, 02, 01)],
# ['29648001.0', new Date(2014, 01, 31), new Date(2014, 02, 02)],
# ['28138054.0', new Date(2014, 01, 31), new Date(2014, 02, 01)],
# ['21738002.0', new Date(2014, 01, 31), new Date(2014, 02, 01)],
# ['30018032.0', new Date(2014, 01, 31), new Date(2014, 02, 01)],
# ['28448045.0', new Date(2014, 01, 31), new Date(2014, 02, 01)],
# ['10088007.0', new Date(2014, 01, 31), new Date(2014, 02, 01)],
# ['29218008.0', new Date(2014, 01, 31), new Date(2014, 02, 01)],
# ['25258012.0', new Date(2014, 01, 31), new Date(2014, 02, 01)],
