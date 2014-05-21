import argparse
import sys
import helpers

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

def main(prodDB='prodR',sessionDB='sessionsNew'):
    print ("Adding session numbers to the events")
    col = helpers.getCollection(prodDB)
    sessCol = helpers.getCollection(sessionDB,True)
    val = "event_id"
    distincts = col.distinct(val)

    users = col.distinct('user_id')
    total = len(users)
    count = 0.0
    for user in users:
        if user == 'NULL' or user == 'N/A':
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
