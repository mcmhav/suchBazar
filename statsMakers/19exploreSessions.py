import argparse
import sys
import helpers

parser = argparse.ArgumentParser(description='Explore events.')
parser.add_argument('-c',type=str, default="prod")
parser.add_argument('-sc',type=str, default="sessions")
parser.add_argument('-t',dest='t', action='store_true')
parser.set_defaults(v=False)
parser.set_defaults(t=False)
args = parser.parse_args()

print ("Collection used:             %s" % args.c)
print ("Sessions collection used:    %s" % args.sc)
print ("Test run, won't clear %s:    %s" % (args.sc,args.t))
print ("")

col = helpers.getCollection(args.c)
sessCol = helpers.getCollection(args.sc,True)

appStartedV = {
    # expected to be start of sessions
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

timeFrameHandled = []
globalTot = 0
sessions = 0
myGlobal = 0

def main():
    handle_appStarted()

def handle_appStarted():
    val = "event_id"
    distincts = col.distinct(val)

    users = col.distinct('user_id')
    total = len(users)
    count = 0.0
    for user in users:
        if user == 'NULL' or user == 'N/A':
            continue
        else:
            devideIntoSessions(user)
            count += 1
            helpers.printProgress(count,total)

def devideIntoSessions(user):
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
