import datetime
import sys
import helpers
from bson import Binary, Code
import math
import numpy as np
import matplotlib.pyplot as plt
import os

def main(sessDB='sessionsNew3',show=False,save=False):
    '''
    '''
    bucketSize = 100
    cap = 30
    counts = getCounts(sessDB)

    priceAvgBuckets = makePriceAVGBuckets(counts,bucketSize=bucketSize,cap=cap)
    print (priceAvgBuckets)
    xticks = helpers.makeTicks(yMax=(cap),steps=15)
    xticksl = helpers.makeTicks(yMin=100,yMax=(bucketSize*cap),steps=15)

    helpers.makePlot(
        k='avgUserPrices',
        counts=priceAvgBuckets,
        show=show,
        xticks=[xticks,xticksl],
        ylabel='Count of Users',
        xlabel='Average Prize Buckets',
        save=True
    )

def makePriceAVGBuckets(avgPrices,bucketSize=100,cap=30):
    print (avgPrices)
    buckets = [0] * cap
    maxBucket = bucketSize * cap

    for ap in avgPrices:
        if ap < maxBucket:
            bucket = math.floor(ap/bucketSize)
            buckets[bucket] += 1
    return buckets

def getCounts(sessDB):
    userPrices = helpers.getUserAVGPrice(sessDB)

    avgPrices = []
    for up in userPrices:
        avgPrices.append(up['value'])

    avgPrices_sorted = sorted(avgPrices)

    return avgPrices_sorted


if __name__ == "__main__":
    main()
