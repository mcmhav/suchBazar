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
                        result.timespan = result.max - result.min
                    }
                   """)

    groups = col.group(
                           key={'product_id':1},
                           condition={},
                           reduce=reducer,
                           initial={'count':0,'max':0,'min':13842573649850,'timespan':0}
                       )

    total = len(groups)

    for item in groups:
        print (item)

if __name__ == "__main__":
    main()
