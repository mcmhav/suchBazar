import csv
import argparse
import sys
import helpers
from bson import Binary, Code
from bson.son import SON

parser = argparse.ArgumentParser(description='')
parser.add_argument('-c',type=str, default="prod")
parser.add_argument('-d',type=str, default="stats")
parser.set_defaults(v=False)
args = parser.parse_args()

print ("Collection used: %s" % args.c)

col = helpers.getCollection(args.c)

def main():
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

    groups = col.group(
                           key={'yr':1,'mo':1,'dy':1},
                           condition={},
                           reduce=reducer,
                           initial={'count':0}
                       )
    c = helpers.getCSVWriter(args.d + '/' + 'eventsPerDay')

    c.writerow(["Date","Events"])

    for g in groups:
        print (g)
        if (g['yr'] != None):
            s = str(int(g['yr'])) + str(int(g['mo'])+10) + str(int(g['dy'])+10)
            s2 = "date: " + str(int(s) - 1010)
            # s = str(int(g['yr'])) + "." + str(g['mo']) + "." + str(g['dy'])
            c.writerow([s2,g['count']])

    helpers.closeF()
    # test = col.aggregate([
    #      {"$group": {"_id": {'dy':"$dy",'mo':"$mo",'yr':"$yr"}, "count": {"$sum": 1}}},
    #      {"$sort": SON([("dy", -1)])},
    #      {'$project': {'ts':1}},
    #  ])

    # test = col.aggregate(
    #                         # Lets find our records
    #                         {"$match":{}},

    #                         # Now lets group on the name counting how many grouped documents we have
    #                         {"$group":{"_id":"$dy"}}
    #                     )
    # for f in groups:
    #     print(f)
    # print (len(groups))

    # print (len(test['result']))
    # for t in test['result']:
    #     print (t)
    # c = helpers.getCSVWriter(args.d + '/' + 'sessionsCounts')
    # helpers.closeF()


if __name__ == "__main__":
    main()
