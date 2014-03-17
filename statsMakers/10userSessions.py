import sys
import argparse
import helpers
from bson import Binary, Code

parser = argparse.ArgumentParser(description='Users sessions.')
parser.add_argument('-sc', type=str, default="sessions")
args = parser.parse_args()

sessCol = helpers.getCollection(args.sc)

print ("Collection used: ", args.sc)
print ("")

totalRatings = {
    'product_wanted':0,
    'product_detail_clicked':0,
    'product_purchase_intended':0
}
total = 0
usersOver19 =0

def main():
    handle_appStarted()

def handle_appStarted():
    users = sessCol.distinct('user_id')


    global total
    total = len(users)
    count = 0.0

    for user in users:
        count += 1
        if user == 'NULL' or user == '':
            continue
        else:
            hadndleUser(user)
            helpers.printProgress(count,total)
    testWithMapReduce(user)
    findTotalAverageOfRatingEvents()

def hadndleUser(user):
    print (user)

    # findStoreCount(user)
    # findTop10Items(user)
    # userEvents = sessCol.find({'user_id':user})
    # avgEventsSess = avgEventPerSession(userEvents)
    # print (avgEventsSess)
    # userStart = findMin(userEvents,'ts')
    # print (userStart)
    # userLast = findMax(userEvents,'ts')
    # print (userLast)
    # avgSession = avgSessionsTime(user)
    # print (avgSession)

    # userRatings = findRatingAmountForUser(user)


def findStoreCount(user):
    print ("Finding access count for the different stores")
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

    groups = sessCol.group(
                           key={'storefront_name':1},
                           condition={'user_id':user,'storefront_name':{'$ne':'NULL'},'storefront_name':{'$ne':''}},
                           reduce=reducer,
                           initial={'count':0}
                       )
    for s in groups:
        print (s)
    return groups
def findMin(userEvents,field):
    print ("Finding Min Value for %s" % field)
    return findMinMax(userEvents,1,field)
def findMax(userEvents,field):
    print ("Finding Max Value for %s" % field)
    return findMinMax(userEvents,-1,field)
def findMinMax(userEvents,val,field):
    return userEvents.sort(field,val)[0][field]

def avgSessionsTime(user):
    print ("Finding average sessions time")
    sessions = sessCol.find({'user_id':user}).distinct('session')
    total = 0
    for session in sessions:
        sessionEvents = sessCol.find({'user_id':user,'session':session}).sort('ts',-1)
        total += sessionEvents[0]['ts'] - sessionEvents[sessionEvents.count()-1]['ts']
    return total/len(sessions)

def avgEventPerSession(userEvents):
    print("Finding average amount of events per session")
    sessions = userEvents.distinct('session')
    return userEvents.count()/len(sessions)

def findTop10Items(user):
    print ("Finding top 10 items for user")
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

    groups = sessCol.group(
                           key={'product_id':1},
                           condition={'user_id':user,'product_id':{'$ne':'NULL'}},
                           reduce=reducer,
                           initial={'count':0}
                       )
    for s in groups:
        print (s)

    return groups

def findRatingAmountForUser(user):
    # print ("Counting rating events for user")
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

    groups = sessCol.group(
                           key={'event_id':1},
                           condition={'user_id':user,'$or':[{'event_id':'product_purchase_intended'}, {'event_id':'product_wanted'},{'event_id':'product_detail_clicked'}]},
                           reduce=reducer,
                           initial={'count':0}
                       )
    totalRatings = 0
    for s in groups:
        totalRatings += s['count']
        # print (s)


    global usersOver19
    if (totalRatings > 19):
        addToRatingTotal(groups)
        usersOver19 += 1
    # sys.exit()

    return groups

def testWithMapReduce(user):
    mapper = Code(  """
                    function () {
                        if (this.event_id == 'product_purchase_intended' || this.event_id == 'product_wanted' || this.event_id == 'product_detail_clicked')
                            emit(this.user_id, 1);
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
    result = sessCol.map_reduce(mapper, reducer, "myresults")

    for r in result.find():
        print (r)

def addToRatingTotal(userRatings):
    global totalRatings
    for rating in userRatings:
        totalRatings[rating['event_id']] += int(rating['count'])

def findTotalAverageOfRatingEvents():
    print (totalRatings)
    print (usersOver19)
    # for rating in totalRatings:
    #     print (str(rating[rating]))

if __name__ == "__main__":
    main()


# 0.8961352657
# 4.6654589372
# 8.47584541063
