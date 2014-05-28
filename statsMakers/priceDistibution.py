from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import helpers
import argparse
from bson import Binary, Code
import matplotlib.pyplot as plt
import os
import sys
import math
import operator

def main(sessDB='sessionsNew', writeLocation='data/stats/priceDistribution'):
    priceCounts = findPriceForItems(sessDB)
    buckets = 51
    maxPrice = 3000
    priceBuckets = [0] * buckets

    for price in priceCounts:
        if int(price['price']) >= maxPrice:
            price['price'] = maxPrice
            priceBuckets[buckets - 1] += int(price['count'])
        else:
            priceBuckets[math.floor((price['price']/(maxPrice/buckets)))] += price['count']
            # priceBuckets[int(price['price'])] = int(price['count'])

    test = [x['price'] for x in priceCounts]
    maxCount = max(priceBuckets)
    w = helpers.getCSVWriter(writeLocation)
    c = 0
    yaxis = []
    for price in priceBuckets:
        w.writerow([c,price])
        yaxis.append(c)
        c += 1
    helpers.closeF()
    print (yaxis)
    plotIt(priceBuckets,yaxis,buckets,maxCount,maxPrice)

def plotIt(priceBuckets,yaxis,buckets,maxCount,maxPrice):
    fig, ax = plt.subplots()
    fig.set_size_inches(14.0,8.0)
    plt.bar(yaxis, priceBuckets)
    plt.title('Price Distribution')
    labels = []
    for l in range(0,6):
        tmp = math.floor(l * (maxPrice/5))
        labels.append(tmp)
    ax.set_xticklabels(labels)
    plt.ylabel('Amount Of Items')
    plt.xlabel('Price')
    plt.axis([0, buckets, 0, maxCount + 100])
    plt.grid(True)
    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/priceDistribution.png"
    plt.savefig(location)
    print ('Price distribution written to: %s' % location)

def findPriceForItems(sessDB):
    col = helpers.getCollection(sessDB)
    gReducer = Code("""
        function (cur,result) {
            result.count += 1
        }
    """)
    eventGoups = col.group(
        key={'price':1},
        condition={'$and':[
            {'price':{'$ne':'NULL'}},
            {'price':{'$ne':'N/A'}}
        ]},
        reduce=gReducer,
        initial={'count':0}
    )

    return eventGoups

if __name__ == "__main__":
    main()
