# Used to measure the user satisfaction in an ordered list.
# rank_ui is the precentile-ranking of item i within the ordered list of all
# items for user u.
# Rank_ui = 0% means that item i is most preffered by user u.
# Higher ranking indicates that i is predicted to be less desirale for user u.

# The way of calcualting the MPR:
# For each actual pair of a user and the purchased item, we randomly select
# 1000 other items, and predict ratings for these 1000 items and produce an ordered
# list with these 1001 items based on their ranking.
# Then, we keep track of where the actual purchased item is ranked, and calculate the
# expected percentage ranking for all users and items.

import sys
import argparse
import helpers
import random
from bson import Binary, Code
from operator import itemgetter
import mmap
from multiprocessing import Pool
from py4j.java_gateway import JavaGateway
import subprocess
import os
import operator

dataPath = '../generators/ratings/'
trainFile = 'tmp.train'
predictionFile = 'tmp.predictions'

def main():
    # train = helpers.readRatingsFromFile('../generators/training.txt')
    # test = helpers.readRatingsFromFile('../generators/validation.txt')
    # predictions = helpers.readRatingsFromFile('../generators/testikus.txt')

    # mpr = compute(train, test, predictions)
    # print (mpr)
    compute('mymedialite')


def compute(recommenderSystem):
    purchases = getPurchases('mongo')
    ratingFile = "recentness_sigmoid_fixed_sr-4.txt"


    totalRank = 0
    count = 0
    for event in purchases:
        user = event['user_id']
        product = event['product_id']
        print ("User: {} Product: {}".format(str(user), str(product)))
        makeRatingsFile(user,product)

        if recommenderSystem == 'mymedialite':
            # Use MyMediaLite
            generatePredictionsMyMediaLite(ratingFile,user)
            percentileRank = findRankOfProductMyMediLite(int(user),int(product))
        elif recommenderSystem == 'mahout':
            # use mahout
            generatePredictionsMahout(ratingFile,user)
            percentileRank = findRankOfProductMahout(product)

        if percentileRank >= 0:
            totalRank += percentileRank
            count += 1
        # print (totalRank)
        # sys.exit()
    mpr = totalRank/count
    print (mpr)
    return mpr

def generatePredictionsMahout(ratingFile,user):
    subprocess.call(['java', 'GetRecommendationsForUser', ratingFile, 'itembased', str(user)])

def generatePredictionsMyMediaLite(ratingFile,user):
    subprocess.call([
        'item_recommendation',
        '--training-file=' + dataPath + trainFile,
        '--recommender=MostPopular',
        '--prediction-file=' + dataPath + predictionFile
    ])

def findRankOfProductMyMediLite(user,product):
    predLocation = dataPath + predictionFile
    predictions = helpers.readMyMediaLitePredictionsForMPR(predLocation)

    userPredictions = predictions[user]
    userPredictions_sorted = sorted(userPredictions.items(), key=operator.itemgetter(1), reverse=True)
    total = len(userPredictions_sorted)

    if total == 0:
        return -1
    count = 0
    rank = -1
    for prediction in userPredictions_sorted:
        if product == prediction[0]:
            rank = count
        count += 1
    percentileRank = (rank/total)*100
    # print (rank)
    # print (total)
    # print (percentileRank)
    # sys.exit()
    return percentileRank

def findRankOfProductMahout(user,product):
    predLocation = dataPath + predictionFile
    predictions = helpers.readMyMediaLitePredictions(predLocation)
    total = len(predictions)
    sys.exit()

    if total == 0:
        return -1
    count = 0
    rank = -1
    for prediction in predictions:
        # print (prediction[1])
        if str(product) == str(prediction[1]):
            rank = count
            sys.exit()
        count += 1
    # print (product)
    # sys.exit()
    percentileRank = (rank/total)*100
    return percentileRank

def makeRatingsFile(user,product):
    # clone = helpers.getCollection('tmp',True)
    # col = helpers.getCollection('sessions')
    train = helpers.readRatingsFromFile('../generators/ratings/recentness_sigmoid_fixed_sr-4.txt')
    e = open(dataPath + trainFile,'w')
    for item in train:
        if item[0] == user and item[1] == product:
            continue
        e.write(str(item[0]) + "\t" + str(item[1]) + "\t" + str(item[2]) + "\n")
    e.close()
    # for item in train:
    #     print (train)
    # print (user)
    # print (product)
    # sys.exit()

def getPurchases(collection):
    if collection == 'mongo':
        col = helpers.getCollection('sessions')
        purchases = col.find({'event_id':'product_purchase_intended'})
    return purchases

def computeOld(train, test, predictions):
    train_users = helpers.buildDictByIndex(train, 0)
    test_users = helpers.buildDictByIndex(test, 0)
    predictions = helpers.buildDictByIndex(predictions, 0)
    #sortDictByRatings(predictions)                                #The ratings usually comes pre sorted

    # candidateItems = helpers.getUniqueItemList(train)

    # numCandidateItems = len(candidateItems)                       #Number of unique items in training set

    MPR = 0
    num_users = 0
    for user in test_users:
        print (user)
        sys.exit()
        #Number of items that are recommendable to the user (all items - those already rated)
        numCandidateItemsThisUser = numCandidateItems - len(train_users[user])

        if user in predictions:                                   #Check if user is in the prediction set
            predictionCount = len(predictions[user])              #Length of the users prediction set
            if predictionCount < numCandidateItemsThisUser:
                #TODO - Consider adding a function for randomly appending the missing items
                print('Warning: Not all items have been ranked!')
            numDroppedItems = numCandidateItemsThisUser - predictionCount
            AUC += auc(predictions[user], test_users[user], numDroppedItems)
            num_users += 1
    return MPR

def mpr(train, test, predicted):
    MPR = 0

    return MPR

def getRankListForUser(user):
    return user

def oldMPR():
    col = helpers.getCollection('sessions')
    allRatings = makeRankListForUsers()
    userItemPurchaseGroups = group()
    items = col.distinct('product_id')
    items.remove('NULL')
    totalItems = len(items)
    count = 0

    MPR = -1
    tmpTop = 0.0
    tmpBottom = 0.0

    print ("")
    print ("Rank items")
    users = col.distinct('user_id')
    total = len(users)
    totalList = []
    for user in users:
        if str(user) in allRatings:
            # Add ranks to the ratings
            userRankedRatings = addRankToRatings(allRatings[str(user)])
            # Fetch items purchased by the user
            userPurchasedItems = purchsedItemsByUser(user)
            # userItemRankList = getRankOfItemForUser(user)
            # randomItems = random.sample(items, 1000)
            # userRankedRatings = getRankInRandomListOfItem(randomItems,allRatings[user],pair['product_id'])
            # rank = getRankInRandomListOfItem(rankedItems,userRatings,pair['product_id'])

            for ratedItems in userRankedRatings:
                # print (userRankedRatings)
                # print (ratedItems)
                # print (userRankedRatings[ratedItems])
                # sys.exit()
                if int(userRankedRatings[ratedItems]['item']) in userPurchasedItems:
                    rank = userRankedRatings[str(int(ratedItems))]['rank']
                    tmpTop += rank
                    tmpBottom += 1
        count = count + 1
        helpers.printProgress(count,total)
    if tmpBottom > 0:
        MPR = tmpTop/tmpBottom
    else:
        MPR = "BLÆ"
    print ("")
    print ("MPR: %s%%" % MPR)
    print ("")

def getRankInRandomListOfItem(randomItems,userRatings,pitem):
    if pitem not in randomItems:
        randomItems.append(int(pitem))
    count = 0
    total = len(userRatings)
    sorterRatings = sorted(userRatings.items(), key=lambda x:x[1],reverse=True)
    userRankedRatings = {}


    # print (sorterRatings)
    for itemRating in sorterRatings:
        item = itemRating[0]
        if int(item) in randomItems:
            rating = itemRating[1]
            rank = (count/total)*100
            count = count + 1
            userRankedRatings[item] = {'rank':rank,'rating':rating}
    return userRankedRatings

def makeRankListForUsers():
    e = open(args.f,'r')

    print ("Read ratings from file")

    usersItemsRatings = {}
    total = sum(1 for line in open(args.f))
    count = 0

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

def addRankToRatingsMongo(ratings):
    count = 0
    total = len(ratings)
    sorterRatings = sorted(ratings.items(), key=lambda x:x[1],reverse=True)
    userRankedRatings = {}

    for itemRating in sorterRatings:
        item = itemRating[0]
        rating = itemRating[1]
        rank = (count/total)*100
        userRankedRatings[item] = {'rank':rank,'rating':rating}
        count = count + 1
    return userRankedRatings

def addRankToRatings(ratings):
    count = 0
    total = len(ratings)
    sorterRatings = sorted(ratings.items(), key=lambda x:x[1],reverse=True)
    userRankedRatings = {}

    for itemRating in sorterRatings:
        item = itemRating[0]
        rating = itemRating[1]
        rank = (count/total)*100
        userRankedRatings[str(count)] = {'rank':rank,'rating':rating,'item':int(item)}
        count = count + 1
    return userRankedRatings

def getRankOfItemForUser(item,ratings):
    count = 0
    for rankedItem in ratings:
        if int(item) == int(rankedItem['_id']):
            return (count/len(ratings))*100
        count = count + 1

def purchsedItemsByUser(user):
    items = col.find({'user_id':user,'event_id':{'$in':['product_purchase_intended','product_wanted']}}).distinct('product_id')
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
