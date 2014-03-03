import json
import pymongo
import csv
import argparse
import os
import sys
from bson import Binary, Code
from bson.json_util import dumps

parser = argparse.ArgumentParser(description='Constructs overview of how many sessions users have.')
parser.add_argument('-v',dest='v', action='store_true')
parser.add_argument('-c',type=str, default="sessions")
parser.add_argument('-d',type=str, default="stats")
parser.set_defaults(v=False)
args = parser.parse_args()

print ("Verbose:         %s" % args.v)
print ("Collection used: %s" % args.c)

client = pymongo.MongoClient()
db = client.mydb
col = db[args.c]

def main():
    handle_appStarted()


def handle_appStarted():

    userCount = -1
    sessionCount = 0
    if sys.version_info >= (3,0,0):
        f = open(args.d + '/' + 'sessionsCounts' + '.csv', "w", newline='')
    else:
        f = open(args.d + '/' + 'sessionsCounts' + '.csv', "wb")
    c = csv.writer(f)
    prevSessionCount = 'SessionCount'
    preUserCount = 'UserCount'
    while userCount != 0:
        tmp = userCount
        userCount = len(col.find({'session':{'$gt':sessionCount}}).distinct('user_id'))
        if userCount != preUserCount:
            c.writerow([prevSessionCount, preUserCount])
        preUserCount = userCount
        prevSessionCount = sessionCount
        if args.v:
            print ("%s - %s" % (sessionCount, userCount), end='\r')
        sessionCount += 1

    f.close()


if __name__ == "__main__":
    main()
