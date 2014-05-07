# Access the overall precision performance based on precision at different recall levels. It valuate the mean of the average precision over all users in the test set. AP for user u is computed at the point of each of the preferred items in the ranked list.
# mistakes made regarding highly relevant items more than for less relevant
# ones. AP correlation finds the precision between two orders at each index in the list
# and takes the average of these values
# τ aρ =
# C(i)
# 2
# · [
# ] − 1
# N − 1 i∈I index(i) − 1
# (7.14)
# N is the number of ranked items in the list, C(i) is the number of items at an index
# less than index(i) that are correctly ranked according to the ground truth. AP corre-
# lation ranges from +1 to -1. One problem with this metric is that it assumes that the
# ground truth list and the evaluated list give a total order, so when just partial orders
# are available, it is unusable.


import sys
import argparse
import helpers
import random
from bson import Binary, Code
from operator import itemgetter
import mmap
from multiprocessing import Pool
import meanap



parser = argparse.ArgumentParser(description='MAP for ratings. Input on the form <user, item, rating> in one file, as of now. Must have populated mongoDB with event-data, as of now.')
parser.add_argument('-sc', type=str, default="sessions")
parser.add_argument('-c', type=str, default="outMF.csv")
parser.add_argument('-k', type=int, default="20")
parser.add_argument('-f', type=str, default="testikus.txt")
args = parser.parse_args()

col = helpers.getCollection(args.sc)

print ("Collection used: ", args.sc)
print ("K size file:     ", args.k)
print ("Output file:     ", args.c)
print ("")

total = 0

def main():
    allRatings = makeRankListForUsers()
    userItemPurchaseGroups = group()
    items = col.distinct('product_id')
    items.remove('NULL')
    totalItems = len(items)
    count = 0
    users = col.distinct('user_id')
    total = len(users)
    k = args.k
    actual = []
    predicted = []
    for user in users:
        # userProd = col.find({'user_id':user}).distinct('product_id')
        if str(user) in allRatings:
            # get actual top items for user
            topItemsForUser = findTopItemsForUser(user)
            # add the top items to the list
            actual.append((topItemsForUser))
            # get the rank of the predicted items
            userRankedRatings = addRankToRatings((allRatings[str(user)]))
            # add the ranked list of the predicted items to the predicted list
            predicted.append(userRankedRatings[:k])

            tmp = meanap.apk(topItemsForUser,userRankedRatings,k)

            if tmp > 0.0:
                print (topItemsForUser)
                print (userRankedRatings)
                print (tmp)
                # sys.exit()

        count += 1
        helpers.printProgress(count,total)

    # def mapk(actual, predicted, k=10):
    print ()
    print ("Calculating score ")
    score = meanap.mapk(actual,predicted,k)

    print ("")
    print ("Score: %s" % score)
    print ("")

    sys.exit()

def findTopItemsForUser(user):
    gReducer = Code("""
        function (cur,result) {
            if (cur.event_id == 'product_purchase_intended'){
                result.value += 10;
            } else if (cur.event_id == 'product_wanted'){
                result.value += 5;
            } else if (cur.event_id == 'product_detail_clicked'){
                result.value += 1;
            }
        }
    """)

    eventGoups = col.group(
        key = {
            'user_id':1,
            'product_id':1
        },
        condition = {
            'user_id':user,
            'product_id':{'$ne' : "NULL"}
        },
        reduce = gReducer,
        initial = {
            'value':0
            # 'rating':0,
            # 'weight':0.6
        }
    )

    if len(eventGoups) > args.k:
        sortedGroups = sorted(eventGoups, key=lambda k: k['value'],reverse=True)
        productIds = getProductIdOnly(sortedGroups[:args.k])
        return productIds

    productIds = getProductIdOnly(eventGoups)
    return productIds

def getProductIdOnly(eventGoups):
    productIds = []
    for event in eventGoups:
        productIds.append(int(event.get('product_id')))

    return productIds

# [{'user_id': 874800601.0, 'product_id': 6318008.0, 'value': 10.0},
#  {'user_id': 874800601.0, 'product_id': 6368013.0, 'value': 5.0},
#   {'user_id': 874800601.0, 'product_id': 1998021.0, 'value': 5.0},
#   {'user_id': 874800601.0, 'product_id': 6398004.0, 'value': 5.0},
#    {'user_id': 874800601.0, 'product_id': 5188007.0, 'value': 5.0},
#     {'user_id': 874800601.0, 'product_id': 2008028.0, 'value': 5.0},
#      {'user_id': 874800601.0, 'product_id': 2018023.0, 'value': 5.0},
#       {'user_id': 874800601.0, 'product_id': 2038027.0, 'value': 5.0},
#       {'user_id': 874800601.0, 'product_id': 6368012.0, 'value': 5.0},
#        {'user_id': 874800601.0, 'product_id': 5168001.0, 'value': 1.0}]

def makeRankListForUsers():
    e = open(args.f,'r')

    print ("Read ratings from file")

    usersItemsRatings = {}
    total = sum(1 for line in open(args.f))
    count = 0
    print (total)

    for line in e.readlines():
        userItemRating = line.split(',')
        user = userItemRating[0]
        item = userItemRating[1]
        rating = float(userItemRating[2])

        if user in usersItemsRatings:
            usersItemsRatings[user][item] = rating
        else:
            usersItemsRatings[user] = {item:rating}
        count = count + 1
        helpers.printProgress(count,total)
    e.close()
    return usersItemsRatings


def addRankToRatings(ratings):
    count = 0
    total = len(ratings)
    sorterRatings = sorted(ratings.items(), key=lambda x:x[1],reverse=True)
    userRankedRatings = []

    for itemRating in sorterRatings:
        item = itemRating[0]
        rating = itemRating[1]
        rank = (count/total)*100
        userRankedRatings.append(int(item))
        count = count + 1
    return userRankedRatings

def getRankOfItemForUser(item,ratings):
    count = 0
    for rankedItem in ratings:
        if int(item) == int(rankedItem['_id']):
            return (count/len(ratings))*100
        count = count + 1

def purchsedItemsByUser(user):
    items = col.find({'user_id':user}).distinct('product_id')
    return items

def makeSimpleItemsRatings():
    """
    Make a simple item recommendation for testing purposes
    Using most popular approach
    Unnecessary user to rating mapping, but meant to be as close to the personalized recommendations

    change to:
        user, item, rating
    """

    users = col.distinct('user_id')
    ratings = {}
    userRatings = getRatingsForUser("")

    for user in users:
        ratings[user] = userRatings

    return ratings

def getRatingsForUser(user):
    userRatings = {}
    tmp = sorted(mostPopularMR().find(), key=itemgetter('value'),reverse=True)
    return tmp

def group():
    gReducer = Code("""
        function (cur,result) {
            result.count += 1
        }
   """)

    groups = col.group(
       key={'user_id':1,'product_id':1},
       condition={'event_id':'product_purchase_intended'},
       reduce=gReducer,
       initial={'count':0}
   )
    return groups

def mostPopularMR():
    mapper = Code(  """
        function () {
            key = this.product_id;
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
    return result

if __name__ == "__main__":
    main()

