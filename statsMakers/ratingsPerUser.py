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
    cap = 150
    counts = getCounts(sessDB)

    print (max(counts))
    # print (len(counts))

    # print (np.mean(counts))
    # print (np.median(counts))

    avgCount = helpers.getAvgOfCount(counts)

    xaxis = groupEventCountsOnCount(counts,cap)
    xaxis = xaxis[1:]
    plotRatingCounts(xaxis,'ratingsPerUser',ylabel='Amount of Users',xlabel='Amount of item interactions',show=show,save=save)

    xaxis = groupEventCountsOnCountCum(counts,len(xaxis))
    xaxis = xaxis[1:]
    yticks = [helpers.makeTicks(yMax=max(xaxis),steps=10),helpers.makeTicks(yMax=100,steps=10)]
    plotRatingCounts(xaxis,'ratingsPerUsercum',ylabel='Percentage of Users',xlabel='Amount of item interactions',yticks=yticks,show=show,save=save)

def getCounts(sessDB):
    ueic = helpers.getUserEventOnItemCounts(sessDB)

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
        yticks=[],
        save=False
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
        xticks=[helpers.makeTicks(yMax=len(xaxis)),helpers.makeTicks(yMax=len(xaxis))],
        save=save
    )


if __name__ == "__main__":
    main()
