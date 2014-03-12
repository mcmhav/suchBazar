import json
import pymongo
import csv
import argparse
import os
import sys
from bson import Binary, Code
from bson.json_util import dumps

parser = argparse.ArgumentParser(description='Explore events.')
parser.add_argument('-v',dest='v', action='store_true')
parser.add_argument('-c',type=str, default="prod")
parser.set_defaults(v=False)
args = parser.parse_args()

print "Verbose:         %s" % (args.v)
print "Collection used: %s" % (args.c)

client = pymongo.MongoClient()
db = client.mydb
db.sessions.remove()
col = db[args.c]

appStartedV = {
    "app_first_started",
    "app_started",
    # "app_became_active",
    "user_logged_in",
}

checked = []
globalTot = 0
sessions = 0
myGlobal = 0

def main():
    handle_appStarted()

def handle_appStarted():
    val = "event_id"
    distincts = col.distinct(val)

    for dist in distincts:
        if dist in appStartedV:
            for event in col.find({val:dist}):
                findSessionEvents(event['user_id'], event['dy'], event['mo'], event['yr'])

def findSessionEvents(u_id, dy, mo, yr):
    if isHandled(u_id, dy, mo, yr):
        return
    conditions = {'user_id':u_id,'dy':dy,'mo':mo,'yr':yr}
    reducer = Code("""function(cur, result) { result.count++; }""")
    groups = db.prod.group(key={"event_id":1},
                            condition=conditions,
                            reduce=reducer,
                            initial= { "count": 0 })

    tmpC = combieNinsert(u_id,{'dy':dy,'mo':mo,'yr':yr},groups)

    global sessions
    sessions += 1

    if args.v:
        global globalTot
        globalTot += tmpC
        for ev in groups:
            print (ev)
        print "Total amount:    %s" % (tmpC)
        print "User:            %s" % (u_id)
        print "Total Sessions:  %s" % (sessions)
        print "Total Events:    %s" % (globalTot)
        print "Date:            %s - %s - %s" % (dy, mo, yr)

    percentDone = (sessions/124507.0)*100
    sys.stdout.write("Percent Done :   %s %% \r" % (percentDone))
    sys.stdout.flush()

def combieNinsert(u_id,date,groups):
    jsonobj = {}
    tmpC = 0
    for val in groups:
        c = val['count']
        jsonobj[val['event_id']] = c
        tmpC += c
    jsonobj['totCount'] = tmpC
    jsonobj['u_id'] = u_id
    jsonobj['date'] = date
    db.sessions.insert(jsonobj)
    return tmpC

def isHandled(u_id, dy, mo, yr):
    tm = str(u_id) + "," + str(dy) + "," + str(mo) + "," + str(yr)
    if tm in checked:
        return True
    else:
        checked.append(tm)
        return False

if __name__ == "__main__":
    main()
