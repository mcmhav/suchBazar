import json
import pymongo
import csv
import argparse
import os
import sys
from bson import Binary, Code
from bson.json_util import dumps

parser = argparse.ArgumentParser(description='Find events with NULL value.')
parser.add_argument('-v',dest='v', action='store_true')
parser.add_argument('-c',type=str, default="prod")
parser.set_defaults(v=False)
args = parser.parse_args()

print ("Verbose:         %s" % (args.v))
print ("Collection used: %s" % (args.c))

client = pymongo.MongoClient()
db = client.mydb
col = db[args.c]

def main():
    handle_appStarted()

def handle_appStarted():
    val = "event_id"
    distincts = col.distinct(val)

    for dist in distincts:
        uIdAsNull = col.find({val:dist, 'user_id':'NULL'}).count()
        uIdNotNull = col.find({val:dist},{'$ne':{'user_id':'NULL'}}).count()
        print ("%s \t\t %s \t\t %s" % (dist,uIdAsNull,uIdNotNull))

if __name__ == "__main__":
    main()
