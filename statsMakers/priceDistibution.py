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

    buckets=51
    maxPrice=4000

    # priceBuckets = makeBuckets(priceCounts,buckets,maxPrice)
    # makePlot(priceBuckets,buckets,maxPrice)

    priceBuckets = makeCumBuckets(priceCounts,buckets,maxPrice)
    xticks = helpers.makeTicks(yMax=len(priceBuckets))
    xticksl = helpers.makeTicks(yMax=max(priceBuckets))
    # makePlot(priceBuckets,buckets,maxPrice)

    helpers.makePlot(
                    "cumpriceDistribution",
                    priceBuckets,
                    # yaxis=priceBuckets,
                    # title='Cumulative distribution of sessions for users',
                    ylabel='Amount of users',
                    xlabel='Session count',
                    show=True,
                    grid=True,
                    xticks=[xticks,xticksl],
                    # yticks=yTicks
                    # labels=[1,5,10],
                    # ticks=[[1,5,10],[1,5,10]]
                )

def makePlot(priceBuckets,buckets,maxCount):
    yaxis,maxPrice = makeYaxis(priceBuckets)
    plotIt(priceBuckets,yaxis,buckets,maxCount,maxPrice)

def makeCumBuckets(priceCounts,buckets,maxPrice):
    priceBuckets = [0] * buckets
    bucketSize = 100
    for p in priceCounts:
        for x in range(0,len(priceBuckets)):
            if p > bucketSize*x:
                priceBuckets[x] += priceCounts[p]

    return priceBuckets

def makeYaxis(priceBuckets):
    yaxis = []
    maxCount = max(priceBuckets)
    print (maxCount)
    c = 0
    yaxis = []
    for price in priceBuckets:
        yaxis.append(c)
        c += 1
    print (yaxis)
    return yaxis,maxCount

def makeBuckets(priceCounts,buckets=51,maxPrice=4000):
    priceBuckets = [0] * buckets

    overMax = 0
    for price in priceCounts:
        if int(price) >= maxPrice:
            overMax += 1
            continue
        else:
            bucket = math.floor((price/(maxPrice/buckets)))
            priceBuckets[bucket] += priceCounts[price]

    return priceBuckets

def plotIt(priceBuckets,yaxis,buckets,maxCount,maxPrice):
    fig, ax = plt.subplots()
    fig.set_size_inches(14.0,8.0)
    plt.bar(yaxis, priceBuckets)
    # plt.title('Price Distribution')
    labels = []
    for l in range(0,6):
        tmp = math.floor(l * (maxPrice/5))
        labels.append(tmp)
    ax.set_xticklabels(labels)
    plt.ylabel('Amount Of Items')
    plt.xlabel('Price')
    plt.axis([0, len(priceBuckets), 0, max(priceBuckets) + max(priceBuckets)/80])
    plt.grid(True)
    plt.show()
    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/priceDistribution.png"
    plt.savefig(location)
    print ('Price distribution written to: %s' % location)

def findPriceForItems(sessDB):
    col = helpers.getCollection(sessDB)
    gReducer = Code("""
        function (cur,result) {
            result.count += 1;
            if (result.maxPrice < cur.price){
                result.maxPrice = cur.price;
            }
        }
    """)
    eventGoups = col.group(
        key={
            'product_id':1,
        },
        condition={'$and':[
            {'price':{'$ne':'NULL'}},
            {'price':{'$ne':'N/A'}}
        ]},
        reduce=gReducer,
        initial={
            'count':0,
            'maxPrice':0
        }
    )

    priceCounts = {}
    for g in eventGoups:
        price = g['maxPrice']
        if price not in priceCounts:
            priceCounts[price] = 0
        priceCounts[price] += 1

    return priceCounts

if __name__ == "__main__":
    main()
