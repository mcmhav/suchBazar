import datetime
import sys
import helpers
from bson import Binary, Code
import math
import numpy as np
import matplotlib.pyplot as plt
import os

def main(sessDB='sessionsNew'):
    '''
    '''
    cap = 150
    counts = getCounts(sessDB)
    avgCount = helpers.getAvgOfCount(counts)

    xaxis = groupEventCountsOnCount(counts,cap)

    plotRatingCounts(xaxis,'ratingsPerUser',ylabel='Amount of Users',xlabel='Amount of item interactions')

    xaxis = groupEventCountsOnCountCum(counts,len(xaxis))
    yticks = [helpers.makeTicks(yMax=max(xaxis),steps=10),helpers.makeTicks(yMax=100,steps=10)]
    plotRatingCounts(xaxis,'ratingsPerUsercum',ylabel='Percentage of Users',xlabel='Amount of item interactions',yticks=yticks)

def getCounts(sessDB):
    ueic = getUserEventOnItemCounts(sessDB)

    ueic_sorted = sorted(ueic, key=lambda k: k['count'],reverse=True)
    counts = [int(x['count']) for x in ueic_sorted]

    return counts

def getRatingAmountAverage(sessDB='sessionsNew'):
    counts = getCounts(sessDB)
    avg = helpers.getAvgOfCount(counts)
    return avg

def groupEventCountsOnCountCum(counts,cap):
    '''
    '''
    ratingCounts = groupEventCountsOnCount(counts,0)

    tmp = [0] * (len(ratingCounts) + 1)
    i = 1
    for c in reversed(ratingCounts):
        tmp[i] = c + tmp[i-1]
        i += 1
    test = tmp[::-1][:cap]
    return test

def groupEventCountsOnCount(counts,cap):
    counts = counts[cap:]
    ratingCounts = [0] * (max(counts) + 1)

    for c in reversed(counts):
        ratingCounts[c] += 1
    return ratingCounts

def plotRatingCounts(
        xaxis,
        name,
        show=False,
        ylabel='',
        xlabel='',
        yticks=[]
    ):
    '''
    '''
    helpers.makePlot(
        name,
        xaxis,
        # yaxis,
        # title='Global Sessions Count',
        ylabel=ylabel,
        xlabel=xlabel,
        show=show,
        grid=True,
        yticks=yticks,
        xticks=[helpers.makeTicks(yMax=len(xaxis)),helpers.makeTicks(yMax=len(xaxis))]
    )

def getUserEventOnItemCounts(sessDB):
    col = helpers.getCollection(sessDB)
    reducer = Code("""
                    function (cur,result) {
                        tmp = [
                            'product_purchase_intended',
                            'product_wanted',
                            'product_detail_clicked'
                        ];
                        hasProp = (tmp.indexOf(cur.event_id) > -1);
                        if (hasProp) {
                            result.count += 1
                        }
                    }
                   """)
    k = 'user_id'
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
    return groups

if __name__ == "__main__":
    main()
