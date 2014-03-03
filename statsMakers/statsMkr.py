import json
import pymongo
import csv
import argparse
import os

parser = argparse.ArgumentParser(description='Make csv files from mongoDB values.')
parser.add_argument('-v',dest='v', action='store_true')
parser.add_argument('-d',type=str, default="csv")
parser.add_argument('-c',type=str, default="prod")
parser.set_defaults(v=False)
args = parser.parse_args()

print ("Verbose: ", args.v)
print ("Store location: ", args.d)
print ("Collection used: ", args.c)

client = pymongo.MongoClient()
db = client.mydb
col = db[args.c]

skipVals = {
                "epoch_day",
                "event_data",
                "epoch_week",
                "dy",
                "event_json",
                "event_location",
                "hr",
                "price",
                "product_id",
                "product_name",
                "retailer_brand",
                "server_time_stamp",
                "tag_position",
                "storefront_position",
                "time_stamp",
                "storefront_id",
                "transaction_id",
                "ts",
                "user_agent",
                "user_id",
                "yr",
                "currency",
                "client_time_stamp"
            }


def handle_k(k):
    distincts = col.distinct(k)
    if args.v:
        print ("----------START----------", k)
    c = csv.writer(open(args.d + '/' + k + '.csv', "wb"))
    for dist in distincts:
        count = col.find({k:dist}).count()
        if args.v:
            print (dist, count)
        c.writerow([ unicode(dist).encode('utf-8'), count])
    if args.v:
        print ("----------END----------", k)


head = col.distinct("head")
if not os.path.exists(args.d):
        os.makedirs(args.d)
for k in head:
    if k not in skipVals:
        handle_k(k)
