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
import numpy as np

def main(sessDB='sessionsNew3',show=False,save=False, writeLocation='data/stats/priceDistribution'):
    priceCounts = findPriceForItems(sessDB)

    # tot = 0
    # c = 0
    # prices = []
    # for p in priceCounts:
    #     tot += p*priceCounts[p]
    #     c += priceCounts[p]
    #     for x in range(0,priceCounts[p]):
    #         prices.append(p)

    # avg = tot/c
    # print (avg)
    # median = np.median(prices)
    # print (median)
    # sys.exit()

    buckets=25
    bucketSize=100
    maxPrice=bucketSize*buckets

    priceBuckets = makeBuckets(priceCounts,buckets,maxPrice)
    yTicksl = helpers.makeTicks(yMax=maxPrice,steps=10)
    makePlot(priceBuckets,maxPrice,yTicksl,"priceDistribution",show=show,save=save)

    priceBuckets = makeCumBuckets(priceCounts,buckets,bucketSize)
    yTicksl = helpers.makeTicks(yMax=100,steps=10)
    makePlot(priceBuckets,maxPrice,yTicksl,"cumpriceDistribution",show=show,save=save)

def makePlot(priceBuckets,maxPrice,yTicksl,name,show=False,save=False):
    xticks = helpers.makeTicks(yMax=len(priceBuckets))
    xticksl = helpers.makeTicks(yMax=maxPrice)
    yTicks = helpers.makeTicks(yMax=max(priceBuckets),steps=10)

    helpers.makePlot(
                    name,
                    priceBuckets,
                    # yaxis=priceBuckets,
                    # title='Cumulative distribution of sessions for users',
                    ylabel='Percentage of products',
                    xlabel='Price',
                    # show=True,
                    grid=True,
                    xticks=[xticks,xticksl],
                    yticks=[yTicks,yTicksl],
                    show=show,
                    save=save
                    # labels=[1,5,10],
                    # ticks=[[1,5,10],[1,5,10]]
                )

def makeCumBuckets(priceCounts,buckets,bucketSize):
    priceBuckets = [0] * buckets
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
