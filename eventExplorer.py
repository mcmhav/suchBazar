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
col = db[args.c]

appStartedV = {
    # "app_first_started",
    "app_started",
    # "app_became_active",
    # "user_logged_in",
}

checked = []

def handle_appStarted():
    val = "event_id"
    distincts = col.distinct(val)

    for dist in distincts:
        if dist in appStartedV:
            for event in col.find({val:dist}):
                findSessionEvents(event['user_id'], event['dy'], event['mo'], event['yr'])
                if args.v:
                    print "%s" % (event['user_id'])
            # count = col.find({val:dist}).count()
            if args.v:
                print ""
                print "%s - %s" % (dist, count)

# def findSessionEvents(event):
def findSessionEvents(u_id, dy, mo, yr):
    if isHandled(u_id, dy, mo, yr):
        return
    tmp = db.prod.find({"user_id":u_id, "dy":dy, "mo":mo, "yr":yr})
    reducer = Code("""function(cur, result) { result.count++; }""")
    groups = db.prod.group(key={"event_id":1},
                            condition= {
                                "user_id":u_id,
                                "dy":dy,
                                "mo":mo,
                                "yr":yr
                                },
                                reduce=reducer,
                                initial= { "count": 0 })
    for ev in groups:
        print (ev)

    tmpC = tmp.count()
    print "Total amount:    %s" % (tmpC)
    print "User:            %s" % (u_id)
    # for sessEv in tmp:
    #     if "app_first_started" in sessEv['event_id']:
    #         print "app_first_started"
    #     elif "app_started" in sessEv['event_id']:
    #         print "app_started"
    #     elif "app_became_active" in sessEv['event_id']:
    #         print "app_became_active"
    #     elif "user_logged_in" in sessEv['event_id']:
    #         print "user_logged_in"

        # print "%s" % (sessEv)
        # if args.v:
        #     print "%s" % (sessEv['event_id'])
    # sys.exit("Error message")

def isHandled(u_id, dy, mo, yr):
    tm = str(u_id) + "," + str(dy) + "," + str(mo) + "," + str(yr)
    if tm in checked:
        return True
    else:
        checked.append(tm)
        return False

def handle_events():
    val = "event_id"
    distincts = col.distinct(val)

    for dist in distincts:
        if dist not in appStartedV:
            count = col.find({val:dist}).count()
            if args.v:
                print ""
                print "%s - %s" % (dist, count)

handle_appStarted()
# handle_events()
