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

    print (maxTimespan)
    print (maxItem)
    print (greaterThan1)
    e.write("]")
    e.close()

if __name__ == "__main__":
    main()
