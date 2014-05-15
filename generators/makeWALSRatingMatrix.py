import argparse
import sys
import pymongo
from functools import partial
from bson import Binary, Code

parser = argparse.ArgumentParser(description='Make wALS rating matrix.')
parser.add_argument('-sc',type=str, default="sessions")
args = parser.parse_args()

print ("Collection used:             %s" % args.sc)
print ("")

client = pymongo.MongoClient()
db = client.mydb
col = db[args.sc]

def main():
    useScheme(partial(schemeNo1),"schemeNo1")

# Scheme #1:
#     Rating is binary
#         For wants and purchases 1
#         Else 0

#     Weight is double between 1 and 0
#         For purchase:   1
#         For want:       0.85
#         For click:      0.3
#         Else:           0.6

def useScheme(scheme,No):
    # user, item, rating, weight
    ratings = scheme()
    # count = 0
    # total = len(ratings)
    e = open("ratings/No" + '.csv','w')
    for s in ratings:
        if (s['product_id'] != 'NULL'):
            ratingColumn = str(int(s['user_id']))+' '+str(int(s['product_id']))+' '+str(int(s['rating']))+' '+str(s['weight'])+'\n'
            e.write(ratingColumn)
        # sys.exit()
        # count += 1
        # print (str((count/total)*100) + '%')

    # for user in users:
    #     userStats = scheme(user)
    #     for s in userStats:
    #         if (s['product_id'] != 'NULL'):
    #             ratingColumn = str(int(s['user_id']))+' '+str(int(s['product_id']))+' '+str(int(s['rating']))+' '+str(s['weight'])+'\n'
    #             e.write(ratingColumn)
    #     # sys.exit()
    #     count += 1
    #     print (str((count/total)*100) + '%')
    e.close()

def useSchemeOld(scheme,No):
    # user, item, rating, weight
    users = col.distinct('user_id')
    count = 0
    total = len(users)
    e = open("No" + '.csv','w')
    for user in users:
        userStats = scheme(user)
        for s in userStats:
            if (s['product_id'] != 'NULL'):
                ratingColumn = str(int(s['user_id']))+' '+str(int(s['product_id']))+' '+str(int(s['rating']))+' '+str(s['weight'])+'\n'
                e.write(ratingColumn)
        # sys.exit()
        count += 1
        print (str((count/total)*100) + '%')
    e.close()


def schemeNo1():
    gReducer = Code("""
        function (cur,result) {
            if (cur.event_id == 'product_purchase_intended'){
                result.rating = 1;
                result.weight = 1;
            } else if (cur.event_id == 'product_wanted'){
                result.rating = 1;
                result.weight = 0.8;
            } else if (cur.event_id == 'product_detail_clicked'){
                result.rating = 0;
                result.weight = 0.3;
            }
        }
    """)

    eventGoups = col.group(
        key = {
            'user_id':1,
            'product_id':1
        },
        condition = {
            # 'user_id':user,
        },
        reduce = gReducer,
        initial = {
            'rating':0,
            'weight':0.6
        }
    )
    return eventGoups

def handleWithGroups(user):
    gReducer = Code("""
        function (cur,result) {
            if (cur.event_id == 'product_purchase_intended'){
                result.purchaseCount += 1;
            } else if (cur.event_id == 'product_wanted'){
                result.wantCount += 1;
            } else if (cur.event_id == 'product_detail_clicked'){
                result.clickCount += 1;
            }
            result.count += 1
        }
    """)

    eventGoups = col.group(
        key = {
            'user_id':1
        },
        condition = {
            'user_id':user,
        },
        reduce = gReducer,
        initial = {
            'count':0,
            'purchaseCount':0,
            'wantCount':0,
            'clickCount':0
        }
    )
    return eventGoups

def handleWithMR():
    mapper = Code(  """
        function () {
            key = this.user_id + "\t" + this.product_id;
            if (this.event_id == 'product_purchase_intended'){
                emit(key, 10);
            } else if (this.event_id == 'product_wanted'){
                emit(key, 5);
            } else if (this.event_id == 'product_detail_clicked'){
                emit(key, 1);
            }
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


if __name__ == "__main__":
    main()


