import datetime
import sys
import helpers
from bson import Binary, Code
import math
import numpy as np
import matplotlib.pyplot as plt
import os
import ratingsPerUser
import longTailSomething
from collections import OrderedDict

def main(sessDB='sessionsNew3'):
    '''
    '''
    col = helpers.getCollection(sessDB)

    users = len(col.distinct('user_id'))
    products = len(col.distinct('product_id'))
    storefronts = len(col.distinct('storefront_name'))
    retailers = len(col.distinct('retailer_brand'))

    clicks = col.find({'event_id':'product_detail_clicked'}).count()
    wants = col.find({'event_id':'product_wanted'}).count()
    purchases = col.find({'event_id':'product_purchase_intended'}).count()

    userIntCount = [int(x['count']) for x in helpers.getUserEventOnItemCounts(sessDB)]

    median = np.median(userIntCount)

    totNumberOfItemInts = clicks + wants + purchases

    avgCPU = clicks/users
    avgWPU = wants/users
    avgPPU = purchases/users

    avgIntsPU = totNumberOfItemInts/users
    avgUIPI = totNumberOfItemInts/products

    vals = {}

    names = []
    values = []

    # vals['Total number of product events'] = totNumberOfItemInts
    names.append('Total number of product events')
    values.append(totNumberOfItemInts)
    # vals['Unique users ids'] = users
    names.append('Unique users ids')
    values.append(users)
    # vals['Unique item ids'] = products
    names.append('Unique item ids')
    values.append(products)
    # vals['Unique storefronts'] = str(storefronts) + "~\\tablefootnote{A storefront is a access point, with different clusterings of items. Stores can have multiple storefronts}"
    names.append('Unique storefronts')
    values.append(str(storefronts) + "~\\tablefootnote{A storefront is a access point, with different clusterings of items. Stores can have multiple storefronts}")
    # vals['Unique brands'] = retailers
    names.append('Unique retailer brands')
    values.append(retailers)

    # vals['Item clicks'] = clicks
    names.append('Item clicks')
    values.append(clicks)
    # vals['Item wants'] = wants
    names.append('Item wants')
    values.append(wants)
    # vals['Item purchases'] = purchases
    names.append('Item purchases')
    values.append(purchases)


    # vals['Average item click count per user'] = avgCPU
    names.append('Average item click count per user')
    values.append(avgCPU)
    # vals['Average item want count per user'] = avgWPU
    names.append('Average item want count per user')
    values.append(avgWPU)
    # vals['Average item purchase count per user'] = avgPPU
    names.append('Average item purchase count per user')
    values.append(avgPPU)


    # vals['Average user interaction count per item'] = avgUIPI
    names.append('Average user interaction count per item')
    values.append(avgUIPI)
    # vals['Average item interaction count per user'] = avgIntsPU
    names.append('Average item interaction count per user')
    values.append(avgIntsPU)
    # vals['Median item interaction count per user'] = median
    names.append('Median item interaction count per user')
    values.append(median)

    for x in range(0,len(names)):
        print ("%s \t&\t %s \\\\" % (names[x],values[x]))





    # OrderedDict(FUTURE=[123,123,123], TODAY=["asf","asdfas","asdfsa"])


    # print (d_sorted_by_value)

    # for v in vals:
    #     print ("%s \t&\t %s \\\\" % (v,vals[v]))


def getasdfsadf(sessDB):
    groups = helpers.getKGroups('event_id',sessDB)

    countP = 0
    countW = 0
    countD = 0
    for g in groups:
        if g['event_id'] == 'product_purchase_intended':
            countP = g['count']
            continue
        elif g['event_id'] == 'product_wanted':
            countW = g['count']
            continue
        elif g['event_id'] == 'product_detail_clicked':
            countD = g['count']
            continue

    return countP,countW,countD

if __name__ == "__main__":
    main()
