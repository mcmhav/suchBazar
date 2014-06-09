import pymongo
import csv
import os
import sys
from bson import Binary, Code
import helpers
import matplotlib.pyplot as plt
import numpy as np
import math

def main(sessDB='sessionsNew3',show=False,save=False):

    k = 'product_id'
    groups = helpers.getKGroups(k,sessDB)
    ks, counts = preprocessGroups(k,groups)
    ks,xss,xticks = groupProductsOnCounts(ks,counts,cap=50)
    yticks = helpers.makeTicks(yMax=max(ks),steps=10)
    yticksl = helpers.makeTicks(yMax=100,steps=10)
    helpers.makePlot(k + 'cum',
                     ks,
                     yaxis=xss,
                     # title='Cumulative distribution of events on products',
                     ylabel='Product count',
                     xlabel='Event count',
                     show=show,
                     xticks=[xticks,xticks],
                     yticks=[yticks,yticksl],
                     save=save
                     )

    k = 'product_id'
    maximum = 50
    groups = helpers.getKGroups(k,sessDB)
    ks, counts = preprocessGroups(k,groups)
    ks,counts = sortUsersOnEvenCount(ks,counts,maximum)
    xTicks = makeTicks(yMax=maximum)
    helpers.makePlot(k,
                     ks,
                     yaxis=ks,
                     # title='Cumulative distribution of events on products',
                     ylabel='Product count',
                     xlabel='Event count',
                     show=show,
                     xticks=[xTicks,xTicks],
                     save=save
                     )

    k = 'event_id'
    groups = helpers.getKGroups(k,sessDB)
    groups = removeLowVals(groups,k,200,addCapToOther=True)
    groups = sorted(groups, key=lambda k: k['count'],reverse=True)
    ks, counts = preprocessGroups(k,groups)
    helpers.makePlot(k,
                     counts,
                     yaxis=ks,
                     # title='Event id distribution',
                     ylabel='Event id count',
                     xlabel='Event id',
                     show=show,
                     steps=len(ks),
                     save=save
                     )

    k = 'storefront_name'
    groups = helpers.getKGroups(k,sessDB)
    ks,counts = preprocessGroups(k,groups)
    ks,counts = handleStoreFront(ks,counts)
    eventsOnStorDistr(k,ks,counts,sessDB,show=show,save=save)

    k = 'hr'
    groups = helpers.getKGroups(k,sessDB)
    ks, counts = preprocessGroups(k,groups)
    ks, counts = sortHours(k,ks,counts)
    xticks = helpers.makeTicks(yMax=len(counts),steps=len(counts))
    helpers.makePlot(k,
                     counts,
                     yaxis=ks,
                     # title='Distribution of events on hours',
                     ylabel='Event count',
                     xlabel='Time of day',
                     labels=ks,
                     show=show,
                     xticks=[],
                     steps=len(counts),
                     save=save
                     )

    k = 'user_id'
    maximum = 250
    groups = helpers.getKGroups(k,sessDB)
    ks, counts = preprocessGroups(k,groups)
    ks,counts = sortUsersOnEvenCount(ks,counts,maximum)
    xTicks = makeTicks(yMax=maximum)
    helpers.makePlot(
                        k,
                        ks,
                        yaxis=ks,
                        # title='Distribution of events for users',
                        ylabel='User count',
                        xlabel='Event count',
                        show=show,
                        grid=True,
                        xticks=[xTicks,xTicks],
                        save=save
                        # labels=[1,5,10],
                        # ticks=[[1,5,10],[1,5,10]]
                    )

    k = 'user_id'
    ks = []
    maximum = 250
    groups = helpers.getKGroups(k,sessDB)
    ks = [int(x[k]) for x in groups]
    ks, counts = preprocessGroups(k,groups)
    ks,yTicks,xTicks = sortUsersOnEvenCountCum(ks,counts,maximum)
    helpers.makePlot(
                        k + 'cum',
                        ks,
                        yaxis=ks,
                        # title='Cumulative distribution of events for users',
                        ylabel='Percentage of users',
                        xlabel='Event count',
                        show=show,
                        grid=True,
                        yticks=yTicks,
                        xticks=xTicks,
                        save=save
                        # labels=[1,5,10],
                        # ticks=[[1,5,10],[1,5,10]]
                    )

    k = 'session'
    maximum = 30
    # groups = helpers.getKGroups(k,sessDB)
    groups = getMaxSess(k,sessDB)
    ks, counts = preprocessGroups('user_id',groups,True)
    counts_sorted = sorted(counts,reverse=True)
    ks = getCountOfMaxSession(counts)
    ks = ks[:maximum]
    xTicks = makeTicks(yMax=maximum)
    yTicks = []
    yTicksSteps = makeTicks(yMax=max(ks),steps=10)
    yTicksLabes = yTicksSteps
    yTicks.append(yTicksSteps)
    yTicks.append(yTicksLabes)
    helpers.makePlot(
                        k,
                        ks,
                        yaxis=ks,
                        # title='Cumulative distribution of sessions for users',
                        ylabel='Amount of users',
                        xlabel='Session count',
                        show=show,
                        grid=True,
                        xticks=[xTicks,xTicks],
                        yticks=yTicks,
                        save=save
                        # labels=[1,5,10],
                        # ticks=[[1,5,10],[1,5,10]]
                    )

def getCountOfMaxSession(count):
    sd = [0] * (max(count) + 1)
    for c in count:
        sd[c] += 1

    return sd[1:]

def getMaxSess(k,sessDB):
    col = helpers.getCollection(sessDB)
    reducer = Code("""
                    function (cur,result) {
                        if(cur.session > result.count) {
                            result.count = cur.session;
                        }
                    }
                   """)
    groups = col.group(
                           key={'user_id':1},
                           condition={'$and':[
                                {k:{'$ne':'NULL'}},
                                {k:{'$ne':'N/A'}},
                                {k:{'$ne':''}},
                            ]},
                           reduce=reducer,
                           initial={
                                'count':0,
                                'count':0
                            }
                       )
    return groups

def removeLowVals(groups,k,cap,addCapToOther=False):
    tmp = []
    other = {k:'other', 'count':0}
    for g in groups:
        if g['count'] > cap:
            tmp.append(g)
        else:
            if addCapToOther:
                other['count'] += g['count']
    if addCapToOther:
        tmp.append(other)
    return tmp

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

def sortCountOnKSS(ks,counts,cap):
    ks = sorted(ks,reverse=False)
    counts = sorted(counts,reverse=False)
    print (ks)
    tmp = []
    cv = 0
    prev = 0
    for k in ks:
        if prev != k:
            tmp.append(k - prev)
            cv += (k)
        else:
            tmp.append(0)
        prev = k
    print (tmp)
    sys.exit()
    tmp_count = []
    for c in counts:
        if c > cap:
            continue
        tmp_count.append(c)
    ks = tmp[::-1]
    ks = ks[:len(tmp_count)]
    print (ks)
    print (sum(ks))
    return ks,tmp_count

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
    tot = 0

    tmp = []
    for c in counts:
        if c > cap:
            counts[i] = cap
        else:
            tot += 1
            tmp.append(counts[i])
        i += 1

    counts_sorted = sorted(tmp[:],reverse=reverse)
    i = 0
    ks = [0] * ((max(tmp))+1)
    for c in counts_sorted:
        ks[c] += 1
        i += 1

    return ks[1:len(ks)],tmp

def sortUsersOnEvenCountCum(ks,counts,cap):
    ks,lol = sortUsersOnEvenCount(ks,counts,cap)
    # print (list(ks))
    # print (ks[0])
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

def eventsOnStorDistr(k,ks,counts,sessDB,show=False,save=False):
    dicKs = convertListToDict(ks)
    # print (groups)
    groups = helpers.getKGroupsWithEventIdDistr(dicKs,k,sessDB)
    print (groups)

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
    if save:
        location = os.path.dirname(os.path.abspath(__file__)) + "/../../muchBazar/src/image/" + k + 'andEvent' + "distribution.png"
        plt.savefig(location)
        print ('Distribution written to: %s' % location)
    if show:
        plt.show()

def getTotalCount(counts):
    total = 0
    for c in counts:
        total += c
    return total
# "product_name",
# "user_id",

if __name__ == "__main__":
    main()
