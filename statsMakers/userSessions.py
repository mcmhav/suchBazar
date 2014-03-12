import json
import pymongo
import sys
import argparse
from bson import Binary, Code

parser = argparse.ArgumentParser(description='Users sessions.')
parser.add_argument('-sc', type=str, default="sessions")
args = parser.parse_args()

client = pymongo.MongoClient()
db = client.mydb
sessCol = db[args.sc]

print ("Collection used: ", args.sc)
print ("")

def main():
    handle_appStarted()

def handle_appStarted():
    users = sessCol.distinct('user_id')

    total = len(users)
    count = 0.0
    sJson = {}
    sJson['name'] = 'flare'
    sJson['children'] = []

    for user in users:
        if user == 'NULL' or user == '':
            continue
        else:
            hadndleUser(user)
            sys.exit()

def hadndleUser(user):
    print (user)

    findStoreCount(user)
    findTop10Items(user)
    userEvents = sessCol.find({'user_id':user})
    avgEventsSess = avgEventPerSession(userEvents)
    print (avgEventsSess)
    userStart = findMin(userEvents,'ts')
    print (userStart)
    userLast = findMax(userEvents,'ts')
    print (userLast)
    avgSession = avgSessionsTime(user)
    print (avgSession)


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

if __name__ == "__main__":
    main()
