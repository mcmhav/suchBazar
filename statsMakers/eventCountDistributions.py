import pymongo
import csv
import os
import sys
from bson import Binary, Code
import helpers
import matplotlib.pyplot as plt
import numpy as np
import math

def main(sessDB='sessionsNew'):
    show = False

    k = 'product_id'
    groups = helpers.getKGroups(k,sessDB)
    ks, counts = preprocessGroups(k,groups)
    ks,xss,xticks = groupProductsOnCounts(ks,counts,cap=50)
    helpers.makePlot(k + 'cum',
                     xss,
                     ks,
                     # title='Cumulative distribution of events on products',
                     ylabel='Product count',
                     xlabel='Event count',
                     show=show,
                     xticks=[xticks,xticks],
                     )
    k = 'event_id'
    groups = helpers.getKGroups(k,sessDB)
    ks, counts = preprocessGroups(k,groups)
    helpers.makePlot(k,
                     ks,
                     counts,
                     # title='Event id distribution',
                     ylabel='Event id count',
                     xlabel='Event id',
                     show=show,
                     )

    k = 'storefront_name'
    groups = helpers.getKGroups(k,sessDB)
    ks,counts = preprocessGroups(k,groups)
    ks,counts = handleStoreFront(ks,counts)
    helpers.makePlot(k,
                     ks,
                     counts,
                     # title='Distribution of events on stores',
                     ylabel='Event count',
                     xlabel='Store name',
                     show=show,
                     labels=ks,
                     xticks=[]
                     )

    eventsOnStorDistr(k,ks,counts,sessDB)

    k = 'retailer_brand'
    groups = helpers.getKGroups(k,sessDB)
    ks, counts = preprocessGroups(k,groups)
    labels = handleRetailerBrand(ks)
    helpers.makePlot(k,
                     ks,
                     counts,
                     # title='Distribution of events on retailer brands',
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
                     # title='Distribution of events on hours',
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
                        # title='Distribution of events for users',
                        ylabel='User count',
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
                        # title='Cumulative distribution of events for users',
                        ylabel='Percentage of users',
                        xlabel='Event count',
                        show=show,
                        grid=True,
                        yticks=yTicks,
                        xticks=xTicks,
                        # labels=[1,5,10],
                        # ticks=[[1,5,10],[1,5,10]]
                    )

    k = 'session'
    maximum = 100
    groups = helpers.getKGroups(k,sessDB)
    groups[:] = [d for d in groups if d.get('session') != 0.0]
    ks, counts = preprocessGroups(k,groups,True)
    ks,counts = sortCountOnKS(counts,ks,maximum)
    xTicks = makeTicks(yMax=maximum)
    yTicks = []
    yTicksSteps = makeTicks(yMax=max(ks),steps=10)
    yTicksLabes = makeTicks(yMax=100,steps=10)
    yTicks.append(yTicksSteps)
    yTicks.append(yTicksLabes)
    helpers.makePlot(
                        k + 'cum',
                        ks,
                        ks,
                        # title='Cumulative distribution of sessions for users',
                        ylabel='Percentage of users',
                        xlabel='Session count',
                        show=show,
                        grid=True,
                        xticks=[xTicks,xTicks],
                        yticks=yTicks
                        # labels=[1,5,10],
                        # ticks=[[1,5,10],[1,5,10]]
                    )

def groupProductsOnCounts(ks,counts,cap=80):
    '''
    '''
    values = max(counts)+1
    tmp = [0] * (values)

    for c in counts:
        tmp[c-1] += 1


    te = [0] * (len(tmp) +1)
    c = len(tmp) -1
    for t in reversed(tmp):
        te[c] = t + te[c+1]
        c -= 1
        # if (c > cap):
        #     tmp[cap-1] += 1
        # else:
    te = te[:cap]
    xss = helpers.makeTicks(1,len(te),len(te))
    xticks = helpers.makeTicks(0,min(te))
    return te,xss,xticks

def coloMapper(node):
    return {
        'storefront_clicked': 'blue',
        'product_detail_clicked': 'red',
        'featured_storefront_clicked': 'green',
        'product_wanted': 'yellow',
        'product_purchase_intended': 'purple',
        'collection_viewed': 'cyan',
        'A': 'blue',
        'B': 'red',
        'C': 'green',
        'D': 'black',
        'E': 'yellow',
        'F': 'brown',
        'G': 'purple',
        'H': 'pink',
        'I': 'orange',
        'J': 'gold',
        'K': 'cyan',
        'L': 'gray',
        'M': 'indigo',
        'N': 'violet',
        'S': 'orchid',
    }.get(node, 'gold')


def convertListToDict(listItems,val=0):
    tmpList = {}
    for l in listItems:
        tmpList[l] = val
    return tmpList

def preprocessGroups(k,groups,ksToString=False):
    '''
    '''
    if (ksToString):
        ks = [int(x[k]) for x in groups]
    else:
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

def sortCountOnKS(ks,counts,cap):
    ks = sorted(ks,reverse=True)
    counts = sorted(counts)
    tmp_count = []
    for c in counts:
        if c > cap:
            continue
        tmp_count.append(c)
    ks = ks[:len(tmp_count)]

    return ks,tmp_count

def sortUsersOnEvenCount(ks,counts,cap,reverse=False):
    i = 0
    for c in counts:
        if c > cap:
            counts[i] = cap
        i += 1

    counts_sorted = sorted(counts,reverse=reverse)
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

    # print (counts)
    # print (ks)
    # sys.exit()
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

def eventsOnStorDistr(k,ks,counts,sessDB):
    dicKs = convertListToDict(ks)
    groups = helpers.getKGroupsWithEventIdDistr(dicKs,k,sessDB)

    ks = []
    for g in groups[0]['storeCount']:
        ks.append(g)
    plots = []
    prev = ''
    index = np.arange(len(ks))
    width = 0.8
    fig, ax = plt.subplots()
    figsize=[14.0,8.0]
    fig.set_size_inches(figsize[0],figsize[1])

    events = []
    maximum = 0
    for g in groups:
        values = g['storeCount'].values()
        if prev:
            pt = plt.bar(index, values, width, color=coloMapper(g['event_id']),bottom=prev)
            tmp = []
            for v in values:
                tmp.append(v)
            c = 0
            for p in prev:
                tmp[c] += p
                c += 1
            prev = tmp
        else:
            pt = plt.bar(index, values, width, color=coloMapper(g['event_id']))
            prev = values
        plots.append(pt)
        events.append(g['event_id'])
    plt.legend(plots, events) #, loc=2, borderaxespad=0., bbox_to_anchor=(1.02, 1))
    plt.xticks(index+width/2., ks)
    fig.autofmt_xdate()
    plt.axis([0, len(ks), 0, max(counts) + (max(counts)/100)])
    plt.grid(True)
    location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/" + k + 'andEvent' + "distribution.png"
    plt.savefig(location)
    # plt.show()
    print ('Distribution written to: %s' % location)

def getTotalCount(counts):
    total = 0
    for c in counts:
        total += c
    return total
# "product_name",
# "user_id",

if __name__ == "__main__":
    main()
