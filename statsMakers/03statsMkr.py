import json
import pymongo
import csv
import argparse
import os
import sys
from bson import Binary, Code
import helpers

parser = argparse.ArgumentParser(description='Make csv files from mongoDB values.')
parser.add_argument('-d',type=str, default="csv")
parser.add_argument('-c',type=str, default="sessions")
parser.set_defaults(v=False)
args = parser.parse_args()

print ("Store location: ", args.d)
print ("Collection used: ", args.c)

col = helpers.getCollection(args.c)

def main():
    head = col.distinct("head")
    if not os.path.exists(args.d):
            os.makedirs(args.d)
    else:
        for the_file in os.listdir(args.d):
            file_path = os.path.join(args.d, the_file)
            try:
                os.unlink(file_path)
            except (Exception, e):
                print (e)

    total = len(useVals)
    count = 0
    for k in head:
        if k in useVals:
            handle_k(k)
            count += 1
            helpers.printProgress(count,total)

def handle_k(k):
    distincts = col.distinct(k)
    print (k)
    if sys.version_info >= (3,0,0):
        f = open(args.d + '/' + k + '.csv', "w", newline='')
    else:
        f = open(args.d + '/' + k + '.csv', "wb")
    c = csv.writer(f)

    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

    groups = col.group(
                           key={k:1},
                           condition={k:{'$ne':'None'},k:{'$ne':''}},
                           reduce=reducer,
                           initial={'count':0}
                       )

    c.writerow([k,'count'])
    for group in groups:
        if group[k] == None:
            continue
        else:
            c.writerow([ group[k], group['count']])

    f.close()

useVals = {
    # "service_id",
    "event_id",
    # "event_data",
    "price",
    "product_id",
    "product_name",
    "retailer_brand",
    # "user_agent",
    "gender_target",
    # "storefront_position",
    "storefront_name",
    "storefront_id",
    # "country_id",
    "user_id",
    # "product_type",
    "origin_ui",
    # "tag_position",
    "country_name",
    # "time_stamp",
    # "tag_name",
    # "login_type",
    # "event_location",
    # "tag_id",
    # "server_time_stamp",
    # "client_time_stamp",
    # "server_environment",
    # "currency",
    # "age_target",
    # "platform",
    # "app_version",
    # "transaction_id",
    # "event_json",
    # "hr",
    # "ts",
    # "epoch_day",
    # "epoch_week",
    # "yr",
    # "mo",
    # "dy",
}

if __name__ == "__main__":
    main()
