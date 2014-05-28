import json
import pymongo
import csv
import argparse
import os
import sys
from bson import Binary, Code
import helpers
import matplotlib.pyplot as plt
import numpy as np

def main(sessDB='sessionsNew'):
    for val in useVals:
        handle_k(val,sessDB)

def handle_k(k,sessDB):
    col = helpers.getCollection(sessDB)
    reducer = Code("""
                    function (cur,result) {
                        result.count += 1
                    }
                   """)

    groups = col.group(
                           key={k:1},
                           condition={'$and':[
                                {k:{'$ne':'NULL'}},
                                {k:{'$ne':'N/A'}},
                                {k:{'$ne':''}}
                            ]},
                           reduce=reducer,
                           initial={'count':0}
                       )
    # print (groups)

    makePlot(groups,k)
    # for group in groups:
    #     if group[k] == None:
    #         continue
    #     else:
    #         makePlot(group,k)

def makePlot(groups,k):
    '''
    '''
    ks = [str(x[k]) for x in groups]
    counts = [int(x['count']) for x in groups]
    print (counts)
    print (len(ks))
    if (k == 'storefront_name'):
        i = 0
        tmpCounts = counts[:]
        counts = []
        tmpks = []
        for count in tmpCounts:
            if (count < 1000):
                counts.append()
                del ks[i]
            i += 1
    print (len(ks))


    index = np.arange(len(counts))
    width = 0.8

    fig, ax = plt.subplots()
    fig.set_size_inches(14.0,8.0)
    plt.bar(index, counts, width)
    plt.title(k)
    # lwidth = 0.35 abels = []
    # for l in range(0,6):
    #     tmp = math.floor(l * (maxPrice/5))
    #     labels.append(tmp)
    if (k == "retailer_brand"):
        labels = getLabelFromItemDB(ks)
        plt.xticks(index+width/2., labels)
    else:
        plt.xticks(index+width/2., ks)
    plt.ylabel('Amount ' + k)
    plt.xlabel(k)
    # ax.set_xticks(range(0,len(counts)+2))

    fig.autofmt_xdate()
    # ax.set_xticklabels(ks)

    plt.axis([0, len(ks), 0, max(counts) + (max(counts)/100)])
    plt.grid(True)
    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/" + k + "distribution.png"
    plt.savefig(location)
    plt.show()
    print ('Price distribution written to: %s' % location)

def getLabelFromItemDB(bids):
    labels = []
    col = helpers.getCollection('brandstaging')

    for bid in bids:
        for dbId in col.find():
            if (bid) == str(float(dbId['id'])):
                labels.append(dbId['displayName'])
    return labels



useVals = {
    # "service_id",
    # "event_id",
    # # "event_data",
    # "price",
    # "product_id",
    # # "product_name",
    "retailer_brand",
    # # "user_agent",
    # "gender_target",
    # # "storefront_position",
    "storefront_name",
    # "storefront_id",
    # "country_id",
    # "user_id",
    # "product_type",
    # "origin_ui",
    # "tag_position",
    # "country_name",
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
