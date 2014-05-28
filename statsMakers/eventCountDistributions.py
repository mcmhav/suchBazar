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
import math

def main(sessDB='sessionsNew'):
    show = False

    k = 'event_id'
    groups = helpers.getKGroups(k,sessDB)
    ks, counts = preprocessGroups(k,groups)
    helpers.makePlot(k,
                     ks,
                     counts,
                     title='Event id distribution',
                     ylabel='Event id count',
                     xlabel='Event id',
                     show=show)

    k = 'storefront_name'
    groups = helpers.getKGroups(k,sessDB)
    ks,counts = preprocessGroups(k,groups)
    ks,counts = handleStoreFront(ks,counts)
    helpers.makePlot(k,
                     ks,
                     counts,
                     title='Distribution of events on stores',
                     ylabel='Event count',
                     xlabel='Store name',
                     show=show,
                     labels=ks,
                     xticks=[]
                     )

    k = 'retailer_brand'
    groups = helpers.getKGroups(k,sessDB)
    ks, counts = preprocessGroups(k,groups)
    labels = handleRetailerBrand(ks)
    helpers.makePlot(k,
                     ks,
                     counts,
                     title='Distribution of events on retailer brands',
                     ylabel='Event count',
                     xlabel='Brand name',
                     labels=labels,
                     show=show,
                     xticks=[]
                     )

    k = 'hr'
    groups = helpers.getKGroups(k,sessDB)
    ks, counts = preprocessGroups(k,groups)
    ks, counts = sortHours(k,ks,counts)
    helpers.makePlot(k,
                     ks,
                     counts,
                     title='Distribution of events on hours',
                     ylabel='Event count',
                     xlabel='Time of day',
                     labels=ks,
                     show=show,
                     xticks=[]
                     )

    k = 'user_id'
    maximum = 250
    groups = helpers.getKGroups(k,sessDB)
    ks, counts = preprocessGroups(k,groups)
    ks = sortUsersOnEvenCount(ks,counts,maximum)
    xTicks = makeTicks(yMax=maximum)
    helpers.makePlot(
                        k,
                        ks,
                        ks,
                        title='Cumulative distribution of events for users',
                        ylabel='Amount of users',
                        xlabel='Event count',
                        show=show,
                        grid=True,
                        xticks=[xTicks,xTicks]
                        # labels=[1,5,10],
                        # ticks=[[1,5,10],[1,5,10]]
                    )

    k = 'user_id'
    maximum = 250
    groups = helpers.getKGroups(k,sessDB)
    ks, counts = preprocessGroups(k,groups)
    ks,yTicks,xTicks = sortUsersOnEvenCountCum(ks,counts,maximum)
    helpers.makePlot(
                        k + 'cum',
                        ks,
                        ks,
                        title='Distribution of events for users',
                        ylabel='Percentage of users',
                        xlabel='Event count',
                        show=show,
                        grid=True,
                        yticks=yTicks,
                        xticks=xTicks,
                        # labels=[1,5,10],
                        # ticks=[[1,5,10],[1,5,10]]
                    )

def preprocessGroups(k,groups):
    '''
    '''
    ks = [str(x[k]) for x in groups]
    counts = [int(x['count']) for x in groups]

    return ks,counts

def handleStoreFront(ks,counts):
    '''
    '''
    i = 0
    tmpCounts = counts[:]
    for count in counts:
        if (count < 200):
            del tmpCounts[i]
            del ks[i]
            i -= 1
        i += 1
    counts = tmpCounts[:]
    return ks,counts

def handleRetailerBrand(ks):
    '''
    '''
    labels = getLabelFromItemDB(ks)

    return labels

def getLabelFromItemDB(bids):
    labels = []
    col = helpers.getCollection('brandstaging')

    for bid in bids:
        for dbId in col.find():
            if (bid) == str(float(dbId['id'])):
                labels.append(dbId['displayName'])
    return labels

def sortHours(k,ks,counts):
    ks = [int(float(x)) for x in ks]
    counts_sorted = [0] * len(counts)
    i = 0
    for k in ks:
        counts_sorted[int(float(k))] = counts[i]
        i += 1
    ks_sorted = sorted(ks)
    return ks_sorted,counts_sorted

def sortUsersOnEvenCount(ks,counts,cap):
    i = 0
    for c in counts:
        if c > cap:
            counts[i] = cap
        i += 1

    counts_sorted = sorted(counts)
    i = 0
    ks = [0] * ((max(counts))+1)
    for c in counts_sorted:
        ks[c] += 1
        i += 1
    return ks

def sortUsersOnEvenCountCum(ks,counts,cap):
    ks = sortUsersOnEvenCount(ks,counts,cap)
    total = getTotalCount(ks)
    cum_ks = [0] * (max(counts)+2)
    i = 0
    cum_ks[i] = total
    for k in ks:
        i += 1
        cum_ks[i] = cum_ks[i-1] - k

    yTicks = []
    yTicksSteps = makeTicks(yMax=total)
    yTicksLabes = makeTicks(yMax=100)
    yTicks.append(yTicksSteps)
    yTicks.append(yTicksLabes)

    xTicks = []
    xTicksSteps = makeTicks(yMax=len(cum_ks)-2)
    xTicks.append(xTicksSteps)
    xTicks.append(xTicksSteps)
    return cum_ks,yTicks,xTicks


def makeTickLabes(yStart=0,yEnd=101, steps=5):
    '''
    '''
    stepSize = math.ceil(yEnd/steps)
    labels = np.arange(yStart,yEnd, stepSize)
    return labels

def makeTicks(yMin=0,yMax=100,steps=5):
    '''
    '''
    stepSize = math.ceil(yMax/steps)
    index = np.arange(yMin,yMax+stepSize,stepSize)
    return index

def getTotalCount(counts):
    total = 0
    for c in counts:
        total += c
    return total
# "product_name",
# "user_id",

if __name__ == "__main__":
    main()
