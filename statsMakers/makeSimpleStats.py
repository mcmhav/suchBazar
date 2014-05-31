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

def main(sessDB='prodR'):
    '''
    '''
    col = helpers.getCollection(sessDB)

    vals = {}
    vals['Total number of events'] = col.find().count()
    vals['Unique users ids'] = len(col.distinct('user_id'))
    vals['Unique item ids'] = len(col.distinct('product_id'))
    vals['Unique storefronts'] = len(col.distinct('storefront_name'))
    vals['Unique brands'] = len(col.distinct('retailer_brand'))
    vals['Item clicks'] = col.find({'event_id':'product_detail_clicked'}).count()
    vals['Item wants'] = col.find({'event_id':'product_wanted'}).count()
    vals['Item purchases'] = col.find({'event_id':'product_purchase_intended'}).count()
    vals['Average rating per item'] = longTailSomething.findAverageRatingCount(helpers.getKGroups('product_id',sessDB))
    vals['Average rating per user'] = ratingsPerUser.getRatingAmountAverage(sessDB)

    countP,countW,countD = getasdfsadf(sessDB)
    vals['Average purchase count per user'] = countP/vals['Unique users ids']
    vals['Average purchase count per user'] = countW/vals['Unique users ids']
    vals['Average item click count per user'] = countD/vals['Unique users ids']

    for v in vals:
        print ("%s \t&\t %s \\\\" % (v,vals[v]))


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
