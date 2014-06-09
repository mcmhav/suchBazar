import argparse
import sys
import helpers
from bson import Binary, Code

appStartedV = { # expected to be start of sessions
    # "app_first_started",
    "app_started",
    # "app_became_active", all user_id's are NULL
    "user_logged_in",
}

productEvents = {
    'product_detail_clicked',
    'product_purchase_intended',
    'product_wanted'
}

def getKGroupsWithEventIdDistr(col):
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1;
                        tmp = result.storeCount;
                        currentEventId = cur.storefront_name;
                        hasProp = (tmp.hasOwnProperty(currentEventId));
                        if (hasProp) {
                            result.storeCount[cur.storefront_name] += 1;
                        }
                    }
                   """)
    groups = col.group(
        key={'user_id':1},
        condition={'$and':[
            {k:{'$ne':'NULL'}},
            {k:{'$ne':'N/A'}},
            {k:{'$ne':''}},
        ]},
        reduce=reducer,
        initial={
            'count':0,
            'storeCount':ks
        }
    )
    return groups

def testWithMapReduce(col):
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
    result = col.map_reduce(mapper, reducer, "myresults")
    return result.find()

def main(prodDB='prodR',sessionDB='sessionsNew3'):
    print ("Adding session numbers to the events")
    col = helpers.getCollection(prodDB)
    sessCol = helpers.getCollection(sessionDB,True)
    val = "event_id"
    distincts = col.distinct(val)

    # users = col.distinct('user_id',{'$or':[
    #                             {'event_id':'product_purchase_intended'},
    #                             {'event_id':'product_wanted'},
    #                             {'event_id':'product_detail_clicked'}
    #                         ]})
    # print (len(users))

    users = [x['_id'] for x in testWithMapReduce(col)]


    # c = 0
    # for u in users.find():
    #     print (u)
    #     c += 1
    # print (len(users))
    # sys.exit()
    total = len(users)
    count = 0.0
    ignUser = (535015706,100001385800886,100000140823565,509375838,100006950441307)
    for user in users:
        if user == 'NULL' or user == 'N/A' or int(user) in ignUser:
            continue
        else:
            devideIntoSessions(user,col,sessCol)
            count += 1
            helpers.printProgress(count,total)

    print ()
    print ("Done adding session numbers")

def devideIntoSessions(user,col,sessCol):
    events = col.find({'user_id':user}).sort('ts',1)
    sessions = {}
    sessions['user_id'] = user
    tmpSession = {}

    sessionsCounter = 0
    currentStoreName = ""
    currentStoreId = ""
    currentStorePos = ""
    for e in events:
        if e['event_id'] in appStartedV:
            sessionsCounter += 1
            currentStoreName = ""
            currentStoreId = ""
            currentStorePos = ""
        elif e['event_id'] == 'storefront_clicked':
            currentStoreName = e['storefront_name']
            currentStoreId = e['storefront_id']
            currentStorePos = e['storefront_position']
        elif e['event_id'] in productEvents:
            # if currentStoreName == "":
            #     sys.exit()
            e['storefront_name'] = currentStoreName
            e['storefront_id'] = currentStoreId
            e['storefront_position'] = currentStorePos
        e['session'] = sessionsCounter

        sessCol.insert(e)

if __name__ == "__main__":
    main()
