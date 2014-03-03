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
parser.add_argument('-sc',type=str, default="sessions")
parser.add_argument('-t',dest='t', action='store_true')
parser.set_defaults(v=False)
parser.set_defaults(t=False)
args = parser.parse_args()

print ("Verbose:                     %d" % args.v)
print ("Collection used:             %s" % args.c)
print ("Sessions collection used:    %s" % args.sc)
print ("Test run, won't clear %s:    %s" % (args.sc,args.t))
print ("")

client = pymongo.MongoClient()
db = client.mydb
col = db[args.c]
sessCol = db[args.sc]

if (not args.t):
    print ("%s cleared" % args.sc)
    sessCol.remove()

appStartedV = { # expected to be start of sessions
    # "app_first_started",
    "app_started",
    # "app_became_active", all user_id's are NULL
    "user_logged_in",
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
            percentDone = (count/total)*100
            sys.stdout.write("Percent Done :   %s %% \r" % (percentDone))
            sys.stdout.flush()

        # sys.exit()

def devideIntoSessions(user):
    events = col.find({'user_id':user}).sort('ts',1)
    sessions = {}
    sessions['user_id'] = user
    tmpSession = {}

    sessionsCounter = 0
    for e in events:
        if e['event_id'] in appStartedV:
            sessionsCounter += 1
            if args.v:
                print ("")
                print ("----------New Session, s %s-----------" % sessionsCounter)
        e['session'] = sessionsCounter
        if not args.t:
            sessCol.insert(e)
        if args.v:
            print ("%s \t %s" % (e['event_id'],e['time_stamp']))


    if args.v:
        print ("User: %s \t Events: %s \t Sessions: %s" % (user, events.count(), sessionsCounter))
        print ("")
        print ("")
    # print sessions
    # sys.exit()


if __name__ == "__main__":
    main()
